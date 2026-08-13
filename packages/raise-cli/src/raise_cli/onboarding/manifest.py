"""Project manifest schema and persistence.

The manifest file (.raise/manifest.yaml) stores project metadata detected
during initialization, including project type and code file count.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    model_validator,
)

from raise_cli.config.ide import IdeType
from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
from raise_cli.onboarding.detection import ProjectType

logger = logging.getLogger(__name__)


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


class BranchConfig(ManifestModel):
    """Branch naming configuration for the project.

    Attributes:
        development: The development/integration branch name.
        main: The stable/production branch name.
    """

    development: str = "main"
    main: str = "main"


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


class BacklogConfig(ManifestModel):
    """Backlog configuration from manifest (optional section).

    Attributes:
        adapter_default: Default PM adapter name (e.g., 'jira', 'filesystem').
    """

    adapter_default: str | None = None


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

    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    # RAISE-15663: Skip write when content is logically unchanged — preserves YAML
    # comments that PyYAML's round-trip would otherwise destroy.  We normalize the
    # on-disk content through the same serialisation path and compare; any difference
    # means a real field mutation that warrants a write.
    if manifest_path.exists():
        try:
            existing_raw = manifest_path.read_text(encoding="utf-8")
            existing_normalized = yaml.dump(
                yaml.safe_load(existing_raw),
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
            if existing_normalized == content:
                logger.debug(
                    "Skipped manifest write — content unchanged: %s", manifest_path
                )
                return
        except Exception as exc:  # noqa: BLE001 — corrupt/unreadable file: fall through to write
            logger.debug("Manifest noop-check failed, proceeding with write: %s", exc)

    manifest_path.write_text(content, encoding="utf-8")
    logger.debug("Saved manifest: %s", manifest_path)


def load_manifest(project_root: Path) -> ProjectManifest | None:
    """Load project manifest from .raise/manifest.yaml.

    Args:
        project_root: Root directory of the project.

    Returns:
        ProjectManifest if file exists and is valid, None otherwise.
    """
    manifest_path = get_raise_dir(project_root) / MANIFEST_FILE

    if not manifest_path.exists():
        logger.debug("Manifest not found: %s", manifest_path)
        return None

    try:
        content = manifest_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            logger.warning("Empty manifest: %s", manifest_path)
            return None
        manifest = ProjectManifest.model_validate(data)
        manifest.mark_loaded_from_file()
        return manifest
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in manifest: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid manifest schema: %s", e)
        return None


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
