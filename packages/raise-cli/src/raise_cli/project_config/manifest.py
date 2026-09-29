"""Project manifest schema and persistence (core tier).

The manifest file (.raise/manifest.yaml) stores project metadata detected
during initialization, including project type and code file count.

Moved from onboarding/manifest.py in RAISE-16419 S4 — core-tier models
importable from any layer without an upward-violation waiver.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal, Self, cast

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    model_validator,
)
from ruamel.yaml import YAML

from raise_cli.config.ide import IdeType
from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
from raise_cli.project_config.types import ProjectType

logger = logging.getLogger(__name__)

# ruamel.yaml instance for round-trip parsing that preserves YAML comments.
# Not thread-safe for concurrent writes, but safe for a single-process CLI.
_ryaml = YAML()
_ryaml.preserve_quotes = True


def _deep_update_commented(target: Any, source: dict[str, Any]) -> None:
    """Recursively merge *source* into *target* preserving ruamel CommentedMaps.

    A plain dict.update() replaces nested CommentedMaps with plain dicts,
    stripping the comments attached to nested keys. This function recurses into
    nested mappings so that only scalar leaf values are replaced, not the
    CommentedMap containers that carry YAML comments (RAISE-17308).
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in target and hasattr(target[key], "update"):
            _deep_update_commented(target[key], value)
        else:
            target[key] = value


class ManifestModel(BaseModel):
    """Base model that keeps forward-compatible manifest extensions."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class AppInfo(ManifestModel):
    """Per-app configuration for monorepo projects.

    Each entry describes one app/package within a monorepo, with optional
    command overrides that take precedence over root-level commands.

    Attributes:
        name: App name (e.g. 'raise-cli').
        path: Relative path from project root (e.g. 'packages/raise-cli').
        test_command: Per-app test command override.
        lint_command: Per-app lint command override.
        type_check_command: Per-app type check command override.
        format_command: Per-app format command override.
    """

    name: str
    path: str
    test_command: str | None = None
    lint_command: str | None = None
    type_check_command: str | None = None
    format_command: str | None = None


# ---------------------------------------------------------------------------
# ADR-071 project.* convention sub-models (defined before ProjectInfo so they
# can be used as concrete types rather than forward references)
# ---------------------------------------------------------------------------


class ProjectCodeConfig(ManifestModel):
    """Tier-2 code layout configuration (fallback-on-missing)."""

    root_glob: str | None = None


class ProjectSchemaConfig(ManifestModel):
    """Tier-2 schema file configuration (fallback-on-missing)."""

    file: str | None = None


class ProjectDocsProductConfig(ManifestModel):
    """Tier-3 product docs paths (skip-on-absence)."""

    primary_dir: str | None = None
    translations_dir: str | None = None
    parity_check: str | None = None


class ProjectDocsDeveloperConfig(ManifestModel):
    """Tier-3 developer docs paths (skip-on-absence)."""

    modules_dir: str | None = None


class ProjectDocsConfig(ManifestModel):
    """Tier-3 documentation paths (skip-on-absence)."""

    product: ProjectDocsProductConfig = Field(default_factory=ProjectDocsProductConfig)
    developer: ProjectDocsDeveloperConfig = Field(
        default_factory=ProjectDocsDeveloperConfig
    )


class ProjectGovernanceConfig(ManifestModel):
    """Tier-3 governance file paths (skip-on-absence)."""

    drift_catalog: str | None = None
    drift_hotspots: str | None = None
    adrs_dir: str | None = None


class ProjectPortfolioConfig(ManifestModel):
    """Portfolio component map (skip-on-absence).

    Maps component identifiers to path prefix lists used by the graph
    builder to tag SymbolNodes with ``portfolio_component`` (RAISE-15251).

    Attributes:
        component_paths: Mapping of component name → list of path prefixes
            (relative to the package root after src-root stripping).
            Example: ``{"storage": ["raise_cli/storage"], "graph": ["raise_cli/graph"]}``
    """

    component_paths: dict[str, list[str]] = Field(default_factory=dict)


class ProjectInfo(ManifestModel):
    """Information about the project detected during init.

    Attributes:
        name: Project name (usually directory name).
        project_type: Whether greenfield or brownfield.
        language: Dominant programming language (auto-detected or user-specified).
        test_command: Command to run tests (configuration over convention).
        lint_command: Command to run linter (configuration over convention).
        type_check_command: Command to run type checker (configuration over convention).
        format_command: Command to run formatter check (configuration over convention).
        code_file_count: Number of code files detected.
        detected_at: When the project was initialized.
        apps: Optional list of per-app configs for monorepo projects.
        server_slug: Authoritative slug confirmed by the server at init/connect
            time (RAISE-11083); falls back to `name` when absent.
    """

    name: str
    project_type: ProjectType
    language: str | None = None
    test_command: str | None = None
    lint_command: str | None = None
    type_check_command: str | None = None
    format_command: str | None = None
    code_file_count: int = 0
    server_slug: str | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    apps: list[AppInfo] | None = None
    # ADR-071 tier-2 and tier-3 project convention keys
    code: ProjectCodeConfig | None = None
    schema_cfg: ProjectSchemaConfig | None = Field(default=None, alias="schema")
    learnings_dir: str | None = None
    docs: ProjectDocsConfig | None = None
    governance: ProjectGovernanceConfig | None = None
    portfolio: ProjectPortfolioConfig | None = None


class ReleaseLine(ManifestModel):
    """One entry in the ``release_lines`` table (RAISE-17066)."""

    branch: str
    status: Literal["active", "bugfix-only", "sunset"]
    fix_versions: list[str] = []
    sunset: date | None = None


class BranchConfig(ManifestModel):
    """Branch naming configuration for the project.

    Attributes:
        development: The development/integration branch name.
        main: The stable/production branch name.
        scm: Detected/configured SCM provider (RAISE-16561). None means no
            signal was observed or configured — never a guess. Widened to
            include ``azuredevops`` and ``bitbucket`` in RAISE-16771: both are
            reachable through ``resolve_scm()`` and have adapter stubs, and an
            unlisted value makes ``load_manifest`` discard the entire manifest
            rather than just that field.
        merge_strategy: Detected/configured merge strategy (RAISE-16561).
            None means no signal was observed or configured — never a guess.
        release_lines: Concurrent release line definitions (RAISE-17066).
            Empty list means legacy single-line mode.
    """

    development: str = "main"
    main: str = "main"
    scm: Literal["github", "gitlab", "azuredevops", "bitbucket"] | None = None
    merge_strategy: Literal["no-ff", "ff-only", "squash"] | None = None
    release_lines: list[ReleaseLine] = []

    @model_validator(mode="after")
    def _validate_topology(self) -> Self:
        if not self.release_lines:
            return self
        active = [ln for ln in self.release_lines if ln.status == "active"]
        if len(active) != 1:
            raise ValueError("exactly 1 active release line required")
        if self.development != active[0].branch:
            raise ValueError(
                f"development ({self.development}) must match active line ({active[0].branch})"
            )
        non_sunset = [ln for ln in self.release_lines if ln.status != "sunset"]
        if len(non_sunset) > 3:
            raise ValueError("max 3 concurrent non-sunset release lines")
        for ln in self.release_lines:
            if ln.status == "bugfix-only" and not ln.sunset:
                raise ValueError(f"{ln.branch}: bugfix-only requires a sunset date")
        return self


class OrgBinding(ManifestModel):
    """Organization this project is bound to (RAISE-9823).

    Persisted on create/link so server writes can refuse to land in a
    different org after server.json switches between operations. ``id`` is the
    canonical match key (UUID); ``name`` is the human slug for messages.
    """

    name: str = ""
    id: str = ""


class IdeManifest(ManifestModel):
    """IDE configuration persisted in manifest (legacy single-IDE format).

    Attributes:
        type: Which IDE this project uses.
    """

    type: IdeType = "claude"


class AgentsManifest(ManifestModel):
    """Multi-agent configuration persisted in manifest.

    Replaces IdeManifest with a list to support multiple simultaneous agents.

    Attributes:
        types: List of active agent types (e.g. ["claude", "cursor", "windsurf"]).
    """

    types: list[str] = Field(default_factory=lambda: ["claude"])


class BacklogStalenessConfig(ManifestModel):
    """Backlog mirror freshness thresholds (optional, nested under ``backlog``).

    Attributes:
        stale_days: Age in days at/above which the backlog mirror is considered
            stale. Defaults to 3 days — a sync older than this is advisory-warned
            in session open and doctor (RAISE-16998).
    """

    stale_days: int = Field(default=3, gt=0)


class BacklogConfig(ManifestModel):
    """Backlog configuration from manifest (optional section).

    Attributes:
        staleness: Backlog mirror freshness thresholds. Absent section or missing
            keys fall back to the defaults on ``BacklogStalenessConfig``.
    """

    staleness: BacklogStalenessConfig = Field(default_factory=BacklogStalenessConfig)


class GraphStalenessConfig(ManifestModel):
    """Graph freshness thresholds (optional, nested under ``graph``).

    Single source of default threshold values — reused directly as the
    ``context.freshness`` core's thresholds type (RAISE-16049 SD1, no
    parallel model). Defaults match the pre-existing hardcoded constants
    (``_STALE_AGE_DAYS = 7``, ``_STALE_COMMIT_THRESHOLD = 50``) for
    backward-compat.

    Attributes:
        warn_days: Age in days at/above which the graph is "warn" stale.
        warn_commits: Commits behind at/above which the graph is "warn" stale.
        critical_days: Age in days at/above which staleness escalates to
            the "critical" tier (still status ``warn`` in session open).
        critical_commits: Commits behind at/above which staleness escalates
            to the "critical" tier.
    """

    warn_days: int = 7
    warn_commits: int = 50
    critical_days: int = 14
    critical_commits: int = 100


class GraphConfig(ManifestModel):
    """Graph build configuration from manifest (optional section).

    Attributes:
        document_sources: Glob patterns (relative to project root) for the
            documents loader — freeform docs like SOPs, RFCs, research.
            Example: ``["dev/sops/*.md", "work/research/**/report.md"]``.
            Empty list or absent section = no documents loaded.
        staleness: Graph freshness thresholds. Absent section or missing
            keys fall back to the defaults on ``GraphStalenessConfig``.
    """

    document_sources: list[str] = Field(default_factory=list)
    staleness: GraphStalenessConfig = Field(default_factory=GraphStalenessConfig)


class TierConfig(ManifestModel):
    """Tier configuration from manifest (optional section).

    Attributes:
        level: Tier level string (community, pro, enterprise).
        backend_url: Backend URL for PRO/Enterprise tiers.
        capabilities: List of capability strings enabled for this tier.
    """

    level: str = "community"
    backend_url: str | None = None
    capabilities: list[str] = Field(default_factory=list)


class ProtocolComplianceEntry(ManifestModel):
    """Maps a source file pattern to compliance test scopes (RAISE-8109).

    When a task modifies a file matching ``pattern``, the gate runner also
    executes ``_run_scoped_gates`` for each scope in ``scopes`` — ensuring
    protocol contract drift is detected at task-gate time, not 24h later
    in the full MR gate.

    Attributes:
        pattern: Substring matched against each file path in the task's
            ``files`` argument (e.g. ``"adapters/protocols.py"``).
        scopes: Test directory paths to run when the pattern matches
            (e.g. ``["packages/raise-cli/tests/adapters/"]``).
    """

    pattern: str
    scopes: list[str] = Field(default_factory=list)


class ProjectManifest(ManifestModel):
    """Project manifest stored in .raise/manifest.yaml.

    Attributes:
        version: Manifest schema version.
        project: Project information.
        branches: Branch naming configuration.
        ide: Legacy single-IDE configuration (backward compat — read/write).
        agents: Multi-agent configuration (new format).
        tier: Optional tier configuration (S211.5).
        protocol_compliance: File-pattern → compliance test scope mappings
            (RAISE-8109). Empty list disables the feature.
    """

    version: str = "1.0"
    project: ProjectInfo
    org: OrgBinding | None = None
    branches: BranchConfig = Field(default_factory=BranchConfig)
    ide: IdeManifest = Field(default_factory=IdeManifest)
    agents: AgentsManifest = Field(default_factory=AgentsManifest)
    tier: TierConfig | None = None
    backlog: BacklogConfig | None = None
    graph: GraphConfig | None = None
    protocol_compliance: list[ProtocolComplianceEntry] = Field(default_factory=list)
    _loaded_from_file: bool = PrivateAttr(default=False)

    def to_persisted_data(self) -> dict[str, Any]:
        """Serialize without adding defaults absent from a loaded manifest."""
        return self.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=not self._loaded_from_file,
            exclude_unset=self._loaded_from_file,
        )

    def mark_loaded_from_file(self) -> None:
        """Preserve the source document's explicit shape on later saves."""
        self._loaded_from_file = True

    @model_validator(mode="before")
    @classmethod
    def _migrate_ide_to_agents(cls, data: Any) -> dict[str, Any]:
        """Migrate old ide.type format to agents.types on load.

        If 'agents' key is absent but 'ide' key is present, derive
        agents.types from ide.type for backward compat.
        """
        if not isinstance(data, dict):
            return cast("dict[str, Any]", data)
        typed: dict[str, Any] = cast("dict[str, Any]", data)
        if "agents" not in typed and "ide" in typed:
            raw_ide: object = typed["ide"]
            if isinstance(raw_ide, dict):
                raw_type: object = cast("dict[str, object]", raw_ide).get(
                    "type", "claude"
                )
                ide_type: str = str(raw_type) if raw_type is not None else "claude"
            else:
                ide_type = "claude"
            typed["agents"] = {"types": [ide_type]}
        return typed


def save_manifest(manifest: ProjectManifest, project_root: Path) -> None:
    """Save project manifest to .raise/manifest.yaml.

    Creates .raise/ directory if it doesn't exist.

    Args:
        manifest: The manifest to save.
        project_root: Root directory of the project.
    """
    raise_dir = get_raise_dir(project_root)
    raise_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = raise_dir / MANIFEST_FILE

    # by_alias=True: serializes schema_cfg -> "schema" (alias) so the YAML key
    # matches what the canonical prelude and rai manifest validate expect.
    # New manifests omit optional null defaults. Loaded manifests instead omit
    # only fields absent from the source, preserving explicit nulls and extras.
    data = manifest.to_persisted_data()

    if manifest_path.exists():
        try:
            existing_raw = manifest_path.read_text(encoding="utf-8")
            # RAISE-15663: skip write when content is logically unchanged. Compare
            # dict representations (not yaml.dump() strings) to avoid false triggers
            # from quote-style or ordering differences.
            if yaml.safe_load(existing_raw) == data:
                logger.debug("Manifest unchanged, skipping write: %s", manifest_path)
                return
            # RAISE-17308: load with ruamel to retain the CommentedMap so that
            # developer annotations survive even when real fields change.
            existing_commented = _ryaml.load(existing_raw)
            if existing_commented is not None and hasattr(existing_commented, "keys"):
                # Remove top-level keys absent from the new data (stale / unknown
                # schema fields) so the file reflects the current manifest shape.
                for stale in [k for k in existing_commented if k not in data]:
                    del existing_commented[stale]
                _deep_update_commented(existing_commented, data)
                out = io.StringIO()
                _ryaml.dump(existing_commented, out)
                manifest_path.write_text(out.getvalue(), encoding="utf-8")
                logger.debug("Saved manifest (comments preserved): %s", manifest_path)
                return
        except Exception as exc:  # noqa: BLE001 — corrupt/unreadable: fall through to plain write
            logger.debug(
                "ruamel round-trip failed, falling back to plain write: %s", exc
            )

    # New file or unreadable existing file: write without comment preservation.
    out = io.StringIO()
    _ryaml.dump(data, out)
    manifest_path.write_text(out.getvalue(), encoding="utf-8")
    logger.debug("Saved manifest: %s", manifest_path)


@dataclass(frozen=True)
class ManifestLoadResult:
    """Typed outcome of a manifest load — never raises (RAISE-17532).

    ``load_manifest()`` (the pre-existing function) collapses *no manifest*,
    *empty manifest*, *invalid YAML*, and *schema-invalid* into a single
    ``None`` — a caller cannot tell "nothing to read" (not a failure) apart
    from "something is there and it's broken" (a failure that must not be
    silently swallowed). ``load_manifest_result()`` classifies every case
    instead; ``load_manifest()`` stays as a compat wrapper for its existing
    call sites that only need manifest-or-None.

    Attributes:
        manifest: The loaded, validated manifest. ``None`` unless
            ``status == "ok"``.
        status: ``"ok"`` (loaded and valid), ``"not_found"`` (no manifest
            file — not an error), ``"invalid"`` (unreadable, malformed YAML,
            or schema-validation failure), or ``"empty"`` (the file exists
            but parses to an empty document).
        error: Human-readable reason, populated iff ``status`` is
            ``"invalid"`` or ``"empty"``.
    """

    manifest: ProjectManifest | None
    status: Literal["ok", "not_found", "invalid", "empty"]
    error: str | None = None


def load_manifest_result(project_root: Path) -> ManifestLoadResult:
    """Load project manifest, classifying every outcome (RAISE-17532).

    Never raises: unreadable files (OSError/PermissionError), invalid YAML,
    an empty document, and Pydantic schema-validation failures are all
    reported as a ``status`` rather than an exception or a bare ``None``.

    Args:
        project_root: Root directory of the project.

    Returns:
        A ``ManifestLoadResult`` describing exactly what happened.
    """
    manifest_path = get_raise_dir(project_root) / MANIFEST_FILE

    if not manifest_path.exists():
        logger.debug("Manifest not found: %s", manifest_path)
        return ManifestLoadResult(manifest=None, status="not_found")

    try:
        content = manifest_path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("Could not read manifest: %s", e)
        return ManifestLoadResult(manifest=None, status="invalid", error=str(e))

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in manifest: %s", e)
        return ManifestLoadResult(manifest=None, status="invalid", error=str(e))

    if data is None:
        logger.warning("Empty manifest: %s", manifest_path)
        return ManifestLoadResult(
            manifest=None, status="empty", error="manifest is empty"
        )

    try:
        manifest = ProjectManifest.model_validate(data)
    except ValidationError as e:
        logger.warning("Invalid manifest schema: %s", e)
        return ManifestLoadResult(manifest=None, status="invalid", error=str(e))

    manifest.mark_loaded_from_file()
    return ManifestLoadResult(manifest=manifest, status="ok")


def load_manifest(project_root: Path) -> ProjectManifest | None:
    """Load project manifest from .raise/manifest.yaml (compat wrapper).

    Args:
        project_root: Root directory of the project.

    Returns:
        ProjectManifest if file exists and is valid, None otherwise. Use
        ``load_manifest_result()`` where the failure mode needs to be
        distinguished (RAISE-17532) — e.g. to fail loud on an empty/invalid
        manifest instead of silently defaulting.
    """
    return load_manifest_result(project_root).manifest


def persist_server_slug(project_path: Path, slug: str | None) -> None:
    """Persist the server-confirmed project slug into the manifest (RAISE-11083).

    No-op when ``slug`` is None/empty, when no manifest exists yet, or when
    the manifest already has this slug recorded — avoids unnecessary writes.

    Args:
        project_path: Root directory of the project.
        slug: The slug confirmed against the server (e.g. from a successful
            `GET /api/v2/projects/{slug}/config`).
    """
    if not slug:
        return

    manifest = load_manifest(project_path)
    if manifest is None:
        return

    if manifest.project.server_slug == slug:
        return

    manifest.project.server_slug = slug
    save_manifest(manifest, project_path)
