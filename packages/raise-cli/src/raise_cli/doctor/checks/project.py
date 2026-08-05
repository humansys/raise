"""Built-in ProjectCheck — validates .raise/ structure and project coherence.

Checks .raise/ directory, manifest.yaml, graph staleness, graph age,
commits since last build, adapter config, skill deployment, and .gitignore entries.

Architecture: ADR-045, S352.3, S6173.4 (staleness detection)
"""

from __future__ import annotations

import logging
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar, cast

import yaml

from raise_cli.config.paths import checkout_scope_id
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_core.graph.backends.protocol import GraphBackendMetadata

logger = logging.getLogger(__name__)

_RAISE_DIR_NAME = ".raise"
_FIX_HINT_INIT = "run: rai init"
_FIX_HINT_GRAPH_BUILD = "run: rai graph build"
_PERSONAL_GIT_PROBES = (
    ".raise/rai/personal/.rai-doctor-probe",
    ".raise/rai/personal/memory/.rai-doctor-probe",
)

_STALE_AGE_DAYS = 7
_STALE_COMMIT_THRESHOLD = 50


class ProjectCheck(DoctorCheck):
    """Diagnostic check for .raise/ project structure and coherence.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "project"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = ".raise/ structure, manifest, graph staleness, config"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run all project coherence checks."""
        root = context.working_dir
        results: list[CheckResult] = []

        results.append(self._check_raise_dir(root))
        results.append(self._check_manifest(root))
        results.append(self._check_graph_staleness(root))
        built_at = _read_built_at(root)
        results.append(self._check_graph_age(built_at))
        results.append(self._check_graph_commits_behind(root, built_at))
        results.append(self._check_adapter_config(root))
        results.append(self._check_skills_deployed(root))
        results.append(self._check_gitignore(root))
        results.append(self._check_mcp_json(root))
        results.append(self._check_mcp_json_tracked(root))
        results.append(self._check_config_toml(root))

        return results

    def _check_raise_dir(self, root: Path) -> CheckResult:
        """Check that .raise/ directory exists."""
        raise_dir = root / _RAISE_DIR_NAME
        if raise_dir.is_dir():
            return CheckResult(
                check_id="project-raise-dir",
                category=self.category,
                status=CheckStatus.PASS,
                message=".raise/ directory exists",
            )
        return CheckResult(
            check_id="project-raise-dir",
            category=self.category,
            status=CheckStatus.ERROR,
            message=".raise/ directory missing",
            fix_hint=_FIX_HINT_INIT,
        )

    def _check_manifest(self, root: Path) -> CheckResult:
        """Check that manifest.yaml exists and is valid YAML."""
        manifest = root / _RAISE_DIR_NAME / "manifest.yaml"
        if not manifest.is_file():
            return CheckResult(
                check_id="project-manifest",
                category=self.category,
                status=CheckStatus.ERROR,
                message="manifest.yaml missing",
                fix_hint=_FIX_HINT_INIT,
            )
        try:
            content = manifest.read_text(encoding="utf-8")
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                return CheckResult(
                    check_id="project-manifest",
                    category=self.category,
                    status=CheckStatus.ERROR,
                    message="manifest.yaml is not a valid YAML mapping",
                )
        except yaml.YAMLError as exc:
            return CheckResult(
                check_id="project-manifest",
                category=self.category,
                status=CheckStatus.ERROR,
                message=f"manifest.yaml has invalid YAML: {exc}",
            )
        return CheckResult(
            check_id="project-manifest",
            category=self.category,
            status=CheckStatus.PASS,
            message="manifest.yaml is valid",
        )

    def _check_graph_staleness(self, root: Path) -> CheckResult:
        """Check if graph index has been built.

        Reads graph_builds SQLite table (written by 'rai graph build') first.
        Falls back to active backend storage, then legacy index.json for
        backward compatibility.
        """
        from raise_cli.config.paths import get_memory_dir
        from raise_cli.graph.backends import get_active_backend

        build_check = self._check_last_build_graph(root)
        if build_check is not None:
            return build_check

        index_path = get_memory_dir(root) / "index.json"
        backend = get_active_backend(index_path, project_root=root)
        backend_name, details = self._backend_details(backend, index_path)

        try:
            graph = backend.load()
        except FileNotFoundError:
            graph = None
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            return self._graph_warn(
                f"graph backend {backend_name} unavailable: {exc}",
                details=details,
            )
        if graph is not None:
            node_count = graph.node_count
            if node_count > 0:
                return CheckResult(
                    check_id="project-graph",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message=f"graph backend {backend_name} built ({node_count} nodes)",
                    details=details,
                )
            if not index_path.is_file():
                return self._graph_warn(
                    f"graph backend {backend_name} empty "
                    "(run rai graph build to populate)",
                    details=details,
                )

        return self._check_legacy_graph_json(index_path, details)

    def _check_last_build_graph(self, root: Path) -> CheckResult | None:
        """Read THIS checkout's most recent graph_builds record as a CheckResult.

        Returns None when no record exists (fallback to backend/legacy path).
        Scoped by checkout_id (RAISE-15607): another worktree's build says
        nothing about whether this one has an index.
        """
        import sqlite3

        from raise_cli.storage.connection import get_project_db_path, get_project_id

        try:
            project_id = get_project_id(root)
            db_path = get_project_db_path(root)
            if not db_path.is_file():
                return None
            conn = sqlite3.connect(str(db_path))
            try:
                row = conn.execute(
                    "SELECT node_count, symbol_depth FROM graph_builds"
                    " WHERE project_id = ? AND checkout_id = ?"
                    " ORDER BY built_at DESC LIMIT 1",
                    (project_id, checkout_scope_id(root)),
                ).fetchone()
            finally:
                conn.close()
        except Exception:  # noqa: BLE001 — doctor checks must not crash
            return None

        if row is None:
            return None

        node_count, symbol_depth = int(row[0] or 0), str(row[1] or "")
        if node_count == 0:
            return self._graph_warn(
                "graph index empty (run rai graph build to populate)"
            )
        depth_suffix = f", depth: {symbol_depth}" if symbol_depth else ""
        return CheckResult(
            check_id="project-graph",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"graph built ({node_count} nodes{depth_suffix})",
        )

    def _backend_details(
        self, backend: object, fallback_path: Path
    ) -> tuple[str, tuple[str, ...]]:
        backend_name = "unknown"
        storage_location = str(fallback_path)
        if isinstance(backend, GraphBackendMetadata):
            backend_name = backend.backend_name()
            storage_location = backend.storage_location()
        return backend_name, (f"backend={backend_name}", f"storage={storage_location}")

    def _graph_warn(
        self, message: str, *, details: tuple[str, ...] = ()
    ) -> CheckResult:
        return CheckResult(
            check_id="project-graph",
            category=self.category,
            status=CheckStatus.WARN,
            message=message,
            fix_hint=_FIX_HINT_GRAPH_BUILD,
            fix_id="rebuild-graph",
            details=details,
        )

    def _check_legacy_graph_json(
        self, index_path: Path, details: tuple[str, ...]
    ) -> CheckResult:
        import json

        if not index_path.is_file():
            return self._graph_warn(
                "graph not built (run rai graph build to populate)", details=details
            )
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            node_count = len(data.get("nodes", []))
        except (json.JSONDecodeError, OSError):
            node_count = 0
        if node_count == 0:
            return self._graph_warn(
                "graph index empty (run rai graph build to populate)"
            )
        return CheckResult(
            check_id="project-graph",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"graph built ({node_count} nodes)",
        )

    def _check_adapter_config(self, root: Path) -> CheckResult:
        """Check if adapter config files are present (only if manifest references Jira)."""
        manifest_path = root / _RAISE_DIR_NAME / "manifest.yaml"
        uses_jira = False
        if manifest_path.is_file():
            try:
                manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                if isinstance(manifest, dict):
                    typed_manifest = cast("dict[str, Any]", manifest)
                    raw_backlog = typed_manifest.get("backlog")
                    typed_backlog = (
                        cast("dict[str, Any]", raw_backlog)
                        if isinstance(raw_backlog, dict)
                        else {}
                    )
                    uses_jira = typed_backlog.get("adapter") == "jira"
            except yaml.YAMLError:
                pass
        jira_config = root / _RAISE_DIR_NAME / "backlog.yaml"
        if jira_config.is_file():
            return CheckResult(
                check_id="project-adapter-config",
                category=self.category,
                status=CheckStatus.PASS,
                message="backlog.yaml adapter config found",
            )
        if not uses_jira:
            return CheckResult(
                check_id="project-adapter-config",
                category=self.category,
                status=CheckStatus.PASS,
                message="no Jira adapter configured — backlog.yaml not required",
            )
        return CheckResult(
            check_id="project-adapter-config",
            category=self.category,
            status=CheckStatus.WARN,
            message="backlog.yaml not found (needed for configured Jira adapter)",
            fix_hint="Run `rai adapter setup jira` to generate .raise/backlog.yaml",
        )

    def _check_skills_deployed(self, root: Path) -> CheckResult:
        """Check if skills are deployed to .claude/skills/."""
        skills_dir = root / ".claude" / "skills"
        if not skills_dir.is_dir():
            return CheckResult(
                check_id="project-skills",
                category=self.category,
                status=CheckStatus.WARN,
                message=".claude/skills/ directory missing",
                fix_hint="run: rai skill sync",
            )
        skill_files = list(skills_dir.rglob("SKILL.md"))
        if not skill_files:
            return CheckResult(
                check_id="project-skills",
                category=self.category,
                status=CheckStatus.WARN,
                message="no skills deployed in .claude/skills/",
                fix_hint="run: rai skill sync",
            )
        return CheckResult(
            check_id="project-skills",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"{len(skill_files)} skills deployed",
        )

    def _check_mcp_json(self, root: Path) -> CheckResult:
        """Check that `.mcp.json` exists at project root (RAISE-1664).

        Required for Claude Code to auto-discover the rai-workspace MCP
        server and expose pipeline tools. Missing → WARN with upgrade hint.
        """
        mcp_json = root / ".mcp.json"
        if mcp_json.is_file():
            return CheckResult(
                check_id="project-mcp-json",
                category=self.category,
                status=CheckStatus.PASS,
                message=".mcp.json is present",
            )
        return CheckResult(
            check_id="project-mcp-json",
            category=self.category,
            status=CheckStatus.WARN,
            message=".mcp.json missing — CC cannot auto-discover rai-workspace MCP tools",
            fix_hint="run: rai upgrade",
        )

    def _check_mcp_json_tracked(self, root: Path) -> CheckResult:
        """Check whether `.mcp.json` is git-tracked (RAISE-10767).

        A tracked `.mcp.json` is a footgun signal: any local per-worktree
        override that a provisioning generator (McpJsonGenerator) writes gets
        silently clobbered by the committed copy on the next checkout/pull.
        This check is diagnostic only — it never runs `git rm` or otherwise
        modifies tracking state; untracking is a deliberate change pending
        separate confirmation.
        """
        tracked = _is_mcp_json_tracked(root)
        if tracked is True:
            return CheckResult(
                check_id="project-mcp-json-tracked",
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    ".mcp.json is tracked in git — a committed copy overwrites "
                    "any local per-worktree override on checkout/pull"
                ),
                fix_hint=(
                    "untracking .mcp.json is a deliberate change pending "
                    "separate confirmation — do not `git rm` automatically"
                ),
            )
        if tracked is False:
            return CheckResult(
                check_id="project-mcp-json-tracked",
                category=self.category,
                status=CheckStatus.PASS,
                message=".mcp.json is not tracked in git",
            )
        return CheckResult(
            check_id="project-mcp-json-tracked",
            category=self.category,
            status=CheckStatus.PASS,
            message="git tracking status of .mcp.json is unknown/unavailable",
        )

    def _check_config_toml(self, root: Path) -> CheckResult:
        """Check that `.raise/config.toml` exists and is valid TOML.

        The file is optional — its absence is a soft warning with an upgrade
        hint. If present, validate that it is parseable TOML.
        """
        import sys

        config_toml = root / ".raise" / "config.toml"
        if not config_toml.is_file():
            return CheckResult(
                check_id="project-config-toml",
                category=self.category,
                status=CheckStatus.WARN,
                message=".raise/config.toml missing — project-level config not available",
                fix_hint="run: rai upgrade",
            )

        if sys.version_info >= (3, 11):  # noqa: UP036
            import tomllib
        else:
            import tomli as tomllib  # type: ignore[no-redef]

        try:
            config_toml.read_bytes()
            tomllib.loads(config_toml.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return CheckResult(
                check_id="project-config-toml",
                category=self.category,
                status=CheckStatus.WARN,
                message=".raise/config.toml exists but is not valid TOML",
                fix_hint="fix TOML syntax in .raise/config.toml",
            )

        return CheckResult(
            check_id="project-config-toml",
            category=self.category,
            status=CheckStatus.PASS,
            message=".raise/config.toml is present and valid",
        )

    def _check_graph_age(self, built_at: datetime | None) -> CheckResult:
        """Check if graph was built within the staleness threshold."""
        if built_at is None:
            return CheckResult(
                check_id="project-graph-age",
                category=self.category,
                status=CheckStatus.WARN,
                message="graph never built — age unknown",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
            )
        age = datetime.now(tz=UTC) - built_at
        age_days = age.days
        if age_days >= _STALE_AGE_DAYS:
            built_str = built_at.strftime("%Y-%m-%d")
            return CheckResult(
                check_id="project-graph-age",
                category=self.category,
                status=CheckStatus.WARN,
                message=f"graph is {age_days} days old (built {built_str})",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
            )
        return CheckResult(
            check_id="project-graph-age",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"graph is {age_days} days old",
        )

    def _check_graph_commits_behind(
        self, root: Path, built_at: datetime | None
    ) -> CheckResult:
        """Check if many commits have landed since the last graph build."""
        if built_at is None:
            return CheckResult(
                check_id="project-graph-commits",
                category=self.category,
                status=CheckStatus.WARN,
                message="graph never built — commit count unknown",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
            )
        count = _count_commits_since(root, built_at)
        if count is None:
            return CheckResult(
                check_id="project-graph-commits",
                category=self.category,
                status=CheckStatus.PASS,
                message="commit count unavailable (git not accessible)",
            )
        if count >= _STALE_COMMIT_THRESHOLD:
            return CheckResult(
                check_id="project-graph-commits",
                category=self.category,
                status=CheckStatus.WARN,
                message=f"{count} commits since last graph build",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
            )
        return CheckResult(
            check_id="project-graph-commits",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"{count} commits since last graph build",
        )

    def _check_gitignore(self, root: Path) -> CheckResult:
        """Check that .raise/rai/ is tracked (v3 policy: personal data is committed)."""
        gitignore = root / ".gitignore"
        if not gitignore.is_file():
            return CheckResult(
                check_id="project-gitignore",
                category=self.category,
                status=CheckStatus.PASS,
                message=".gitignore absent — .raise/rai/ is tracked by default",
            )
        content = gitignore.read_text(encoding="utf-8")
        ignored = _personal_state_is_gitignored(root)
        if ignored is None:
            ignored = _has_obvious_personal_ignore(content)
        if ignored:
            return CheckResult(
                check_id="project-gitignore",
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    ".raise/rai/personal/ or its portable memory is gitignored "
                    "— v3 policy requires it to be tracked"
                ),
                fix_hint=(
                    "Remove broad personal ignore rules from .gitignore "
                    "(specific volatile subpaths may remain ignored)"
                ),
            )
        return CheckResult(
            check_id="project-gitignore",
            category=self.category,
            status=CheckStatus.PASS,
            message=".raise/rai/ is tracked (v3 policy)",
        )


def _personal_state_is_gitignored(root: Path) -> bool | None:
    """Use Git semantics to determine whether v3 personal state is ignored."""
    for probe in _PERSONAL_GIT_PROBES:
        try:
            result = subprocess.run(
                ["git", "check-ignore", "--quiet", "--no-index", "--", probe],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, OSError):
            logger.debug("Failed to check Git visibility for %s", probe)
            return None
        if result.returncode == 0:
            return True
        if result.returncode != 1:
            logger.debug(
                "git check-ignore failed for %s: %s",
                probe,
                result.stderr.strip(),
            )
            return None
    return False


def _has_obvious_personal_ignore(content: str) -> bool:
    """Conservative fallback when Git ignore semantics are unavailable."""
    broad_patterns = {
        ".raise/",
        ".raise/rai/",
        ".raise/rai/personal/",
    }
    ignored = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        pattern = line.removeprefix("!").removeprefix("/")
        if pattern in broad_patterns:
            ignored = not negated
    return ignored


def _read_built_at(root: Path) -> datetime | None:
    """Read last graph build timestamp FOR THIS CHECKOUT.

    Primary: SQLite MAX(updated_at) from graph_nodes.
    Fallback: graph_builds table MAX(built_at) — explicit build record.

    Both are scoped to ``checkout_id`` (RAISE-15607). Reading them repo-wide
    made doctor report a fresh graph off another worktree's build while the
    local partition was empty — a "fresh" verdict over no evidence at all.
    """
    ts = _read_built_at_sqlite(root)
    if ts is not None:
        return ts
    return _read_built_at_graph_builds(root)


def _read_built_at_sqlite(root: Path) -> datetime | None:
    """Read MAX(updated_at) from THIS checkout's graph_nodes partition."""
    import sqlite3

    from raise_cli.storage.connection import get_project_db_path, get_project_id

    try:
        db_path = get_project_db_path(root)
        if not db_path.is_file():
            return None
        project_id = get_project_id(root)
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT MAX(updated_at) FROM graph_nodes"
                " WHERE project_id = ? AND checkout_id = ?",
                (project_id, checkout_scope_id(root)),
            ).fetchone()
        finally:
            conn.close()
        if row is None or row[0] is None:
            return None
        return datetime.fromisoformat(row[0])
    except Exception:  # noqa: BLE001 — doctor checks must not crash
        return None


def _read_built_at_graph_builds(root: Path) -> datetime | None:
    """Fallback: MAX(built_at) from THIS checkout's graph_builds records."""
    import sqlite3

    from raise_cli.storage.connection import get_project_db_path, get_project_id

    try:
        project_id = get_project_id(root)
        db_path = get_project_db_path(root)
        if not db_path.is_file():
            return None
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT MAX(built_at) FROM graph_builds"
                " WHERE project_id = ? AND checkout_id = ?",
                (project_id, checkout_scope_id(root)),
            ).fetchone()
        finally:
            conn.close()
        if row is None or row[0] is None:
            return None
        return datetime.fromisoformat(row[0])
    except Exception:  # noqa: BLE001 — doctor checks must not crash
        return None


def _is_mcp_json_tracked(root: Path) -> bool | None:
    """Check whether `.mcp.json` is tracked by git.

    Returns True (tracked), False (not tracked), or None when tracking status
    is unknown/unavailable (not a git repo, git not installed, timeout, etc.).
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".mcp.json"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        logger.debug("Failed to determine git tracking status of .mcp.json")
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def _count_commits_since(root: Path, since: datetime) -> int | None:
    """Count commits since a given datetime. Returns None on git failure."""
    since_str = since.isoformat()
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"--since={since_str}", "HEAD"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError, ValueError):
        logger.debug("Failed to count commits since %s", since_str)
        return None
