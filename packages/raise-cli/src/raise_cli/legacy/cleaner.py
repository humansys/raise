"""Plan and execute legacy residue cleanup.

``plan_clean`` translates a ``ScanReport`` into a list of ``CleanAction``
objects.  ``execute_clean`` runs the actions.  Dry-run means the CLI never
calls ``execute_clean`` -- no ``dry_run`` parameter exists here (S2-D4,
purge pattern).

Architecture: Epic RAISE-16227 design S2, I1.
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, model_validator

from raise_cli.legacy.models import Residue, ResidueKind, ScanReport
from raise_cli.legacy.scanner import DEP_RE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verb taxonomy
# ---------------------------------------------------------------------------

CleanVerb = Literal[
    "consolidate", "fix-config", "delete", "remove-line", "remove-entry",
    "move-aside",
]

# The ONLY kinds a CleanAction can be built from.  Everything else
# (cartridges, uvlock-entry, path-shadowing, symlinks, user configs,
# venv-console-script, venv-prerename-pkg, the 3 global kinds) is
# unconstructible -- epic D3 enforced by the model validator.
VERB_BY_KIND: dict[ResidueKind, CleanVerb] = {
    # owned -- processed without --force
    "orphan-project-db": "consolidate",
    "orphan-global-partition": "consolidate",
    "stale-mcp-command": "fix-config",
    "stale-runtime-config": "fix-config",
    # advisory, force-actionable -- processed only with --force
    "venv-raise-cli": "delete",
    "venv-renamed": "delete",
    "requirements-dep": "remove-line",
    "pyproject-dep": "remove-entry",
    "repo-cartridge-self-ingest": "move-aside",
}

FORCE_ONLY_KINDS: frozenset[ResidueKind] = frozenset({
    "venv-raise-cli", "venv-renamed", "requirements-dep", "pyproject-dep",
    "repo-cartridge-self-ingest",
})

_VERB_ORDER: dict[CleanVerb, int] = {
    "consolidate": 0,
    "fix-config": 1,
    "move-aside": 2,
    "delete": 3,
    "remove-line": 4,
    "remove-entry": 5,
}

# Regex for quoted list items in pyproject.toml dependencies.
_PYPROJECT_DEP_RE = re.compile(
    r"""^\s*["'](raise-cli|raise-core|rai-cli|rai-core)([^"']*)["'],?\s*$""",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# CleanAction
# ---------------------------------------------------------------------------


class CleanAction(BaseModel):
    """A single planned cleanup action.

    Only constructible for kinds in ``VERB_BY_KIND`` with the correct verb.
    Never-actionable kinds raise ``ValidationError`` -- epic D3.
    """

    residue: Residue
    verb: CleanVerb

    @model_validator(mode="after")
    def _validate_kind_verb(self) -> CleanAction:
        expected_verb = VERB_BY_KIND.get(self.residue.kind)
        if expected_verb is None:
            msg = (
                f"Residue kind {self.residue.kind!r} is not actionable -- "
                f"it cannot be converted to a CleanAction"
            )
            raise ValueError(msg)
        if self.verb != expected_verb:
            msg = (
                f"Residue kind {self.residue.kind!r} requires verb "
                f"{expected_verb!r}, got {self.verb!r}"
            )
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# ActionOutcome / CleanResult
# ---------------------------------------------------------------------------


class ActionOutcome(BaseModel):
    """Result of executing a single CleanAction."""

    action: CleanAction
    status: Literal["done", "skipped", "failed"]
    detail: str = ""
    backup_path: Path | None = None


class CleanResult(BaseModel):
    """Aggregated result of execute_clean."""

    outcomes: list[ActionOutcome] = []
    consolidated_sources: int = 0
    notes: list[str] = []
    errors: list[str] = []

    @property
    def ok(self) -> bool:
        """True when there are no errors and no failed outcomes."""
        if self.errors:
            return False
        return not any(o.status == "failed" for o in self.outcomes)


# ---------------------------------------------------------------------------
# plan_clean
# ---------------------------------------------------------------------------


def plan_clean(
    report: ScanReport, *, force: bool = False,
) -> list[CleanAction]:
    """Translate residues into executable actions.

    Without *force*, only owned residues are planned.  With *force*,
    ``FORCE_ONLY_KINDS`` advisory residues are included.
    Deduplicates by ``(verb, resolved_path)`` and orders by verb priority.
    """
    seen: set[tuple[CleanVerb, Path]] = set()
    actions: list[CleanAction] = []

    for residue in report.residues:
        verb = VERB_BY_KIND.get(residue.kind)
        if verb is None:
            continue  # not actionable at all
        if residue.kind in FORCE_ONLY_KINDS and not force:
            continue  # advisory, skip without --force

        try:
            resolved = residue.path.resolve()
        except OSError:
            resolved = residue.path

        key = (verb, resolved)
        if key in seen:
            continue
        seen.add(key)

        actions.append(CleanAction(residue=residue, verb=verb))

    # Sort by verb priority
    actions.sort(key=lambda a: _VERB_ORDER[a.verb])
    return actions


# ---------------------------------------------------------------------------
# execute_clean
# ---------------------------------------------------------------------------


def execute_clean(
    actions: list[CleanAction],
    *,
    project_root: Path,
    ignore_tracked: bool = False,
) -> CleanResult:
    """Execute planned cleanup actions.

    No ``dry_run`` parameter -- dry-run means the CLI never calls this.

    Args:
        actions: Planned cleanup actions.
        project_root: Project root path.
        ignore_tracked: When True, ``fix-config`` actions write even if the
            target is git-tracked (``--fix-config`` explicit consent).
    """
    result = CleanResult()

    # Batch consolidation: one call for all consolidate actions
    consolidate_actions = [a for a in actions if a.verb == "consolidate"]
    if consolidate_actions:
        _execute_consolidation(consolidate_actions, project_root=project_root, result=result)

    # Process remaining verbs
    for action in actions:
        if action.verb == "consolidate":
            continue  # already handled
        if action.verb == "fix-config":
            _execute_fix_config(
                action,
                project_root=project_root,
                result=result,
                ignore_tracked=ignore_tracked,
            )
        elif action.verb == "delete":
            _execute_delete(action, project_root=project_root, result=result)
        elif action.verb == "remove-line":
            _execute_remove_line(action, result=result)
        elif action.verb == "remove-entry":
            _execute_remove_entry(action, result=result)
        elif action.verb == "move-aside":
            _execute_move_aside(action, project_root=project_root, result=result)

    # NOTE: the "run uv lock" note is added by the CLI layer (_do_execute
    # in clean.py) which has access to the full ScanReport.  uvlock-entry
    # is never actionable, so it can never appear in ``actions`` here.

    return result


# ---------------------------------------------------------------------------
# Verb executors
# ---------------------------------------------------------------------------


def _execute_consolidation(
    actions: list[CleanAction],
    *,
    project_root: Path,
    result: CleanResult,
) -> None:
    """Run consolidate_all once for all DB residues."""
    try:
        from raise_cli.storage.consolidate import consolidate_all

        cr = consolidate_all(project_root=project_root)
        result.consolidated_sources = cr.sources_found
        if cr.errors:
            result.errors.extend(cr.errors)
        for action in actions:
            status: Literal["done", "skipped", "failed"] = (
                "failed" if cr.errors else "done"
            )
            result.outcomes.append(
                ActionOutcome(action=action, status=status, detail="consolidated")
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("consolidation failed", exc_info=True)
        result.errors.append(f"consolidation: {exc}")
        for action in actions:
            result.outcomes.append(
                ActionOutcome(action=action, status="failed", detail=str(exc))
            )


_SKIP_DETAILS: dict[str, str] = {
    "unchanged": "already up to date",
    "git-tracked": "git-tracked -- rai clean --fix-config will handle this",
    "not-main-checkout": "linked worktree -- run rai worktree register",
}


def _resolve_config_rel(action: CleanAction, project_root: Path) -> str | None:
    """Resolve the relative config path for a fix-config action.

    Returns None when the residue path is outside *project_root*.
    """
    if action.residue.kind == "stale-mcp-command":
        return ".mcp.json"
    try:
        return str(action.residue.path.relative_to(project_root))
    except ValueError:
        return None


def _execute_fix_config(
    action: CleanAction,
    *,
    project_root: Path,
    result: CleanResult,
    ignore_tracked: bool = False,
) -> None:
    """Fix stale MCP or runtime config commands via ``apply_runtime_config``.

    Backup only when content actually changed (idempotency: epic contract 5).
    """
    config_path = action.residue.path
    try:
        original = config_path.read_bytes() if config_path.is_file() else b""
    except OSError:
        original = b""

    rel = _resolve_config_rel(action, project_root)
    if rel is None:
        result.outcomes.append(
            ActionOutcome(
                action=action,
                status="failed",
                detail=f"config path {config_path} outside project root",
            )
        )
        return

    try:
        from raise_cli.worktree.provision import apply_runtime_config

        apply_result = apply_runtime_config(
            project_root, rel, ignore_tracked=ignore_tracked,
        )
    except Exception as exc:  # noqa: BLE001
        result.outcomes.append(
            ActionOutcome(action=action, status="failed", detail=str(exc))
        )
        return

    # Map ConfigApplyResult to ActionOutcome (D-S3.4)
    skip_detail = _SKIP_DETAILS.get(apply_result.status)
    if skip_detail is not None:
        result.outcomes.append(
            ActionOutcome(action=action, status="skipped", detail=skip_detail)
        )
        return

    # status == "written"
    backup_path: Path | None = None
    if original:
        backup = config_path.with_suffix(config_path.suffix + ".bak")
        backup.write_bytes(original)
        backup_path = backup

    detail = "config updated"
    if apply_result.was_tracked:
        detail = "config updated (git-tracked -- review the diff in your working tree)"

    result.outcomes.append(
        ActionOutcome(
            action=action, status="done", detail=detail,
            backup_path=backup_path,
        )
    )


def _execute_delete(
    action: CleanAction, *, project_root: Path, result: CleanResult,
) -> None:
    """Delete a venv directory with safety guards."""
    target = action.residue.path

    # Guard: must be under project_root
    try:
        target_resolved = target.resolve()
        root_resolved = project_root.resolve()
        target_resolved.relative_to(root_resolved)
    except (OSError, ValueError):
        result.outcomes.append(
            ActionOutcome(
                action=action, status="failed",
                detail=f"target {target} is outside project root",
            )
        )
        return

    # Guard: must have pyvenv.cfg (confirms it's a venv)
    if not (target / "pyvenv.cfg").is_file():
        result.outcomes.append(
            ActionOutcome(
                action=action, status="failed",
                detail=f"no pyvenv.cfg in {target} -- refusing to delete",
            )
        )
        return

    try:
        shutil.rmtree(target)
        result.outcomes.append(
            ActionOutcome(action=action, status="done", detail="deleted")
        )
    except OSError as exc:
        result.outcomes.append(
            ActionOutcome(action=action, status="failed", detail=str(exc))
        )


def _execute_remove_line(action: CleanAction, *, result: CleanResult) -> None:
    """Remove matching dep lines from requirements*.txt with backup."""
    req_path = action.residue.path
    try:
        original = req_path.read_text()
    except OSError as exc:
        result.outcomes.append(
            ActionOutcome(action=action, status="failed", detail=str(exc))
        )
        return

    lines = original.splitlines(keepends=True)
    filtered = [line for line in lines if not DEP_RE.search(line)]

    if filtered == lines:
        result.outcomes.append(
            ActionOutcome(action=action, status="skipped", detail="no matching lines")
        )
        return

    backup = req_path.with_suffix(req_path.suffix + ".bak")
    backup.write_text(original)
    req_path.write_text("".join(filtered))
    result.outcomes.append(
        ActionOutcome(
            action=action, status="done", detail="lines removed",
            backup_path=backup,
        )
    )


def _execute_remove_entry(action: CleanAction, *, result: CleanResult) -> None:
    """Remove matching dep entries from pyproject.toml with backup.

    Known limitation: only removes quoted list-item style deps.
    Table-style deps (``raise-cli = "..."`` under ``[tool.*.dependencies]``)
    are left for manual action.
    """
    pyproject_path = action.residue.path
    try:
        original = pyproject_path.read_text()
    except OSError as exc:
        result.outcomes.append(
            ActionOutcome(action=action, status="failed", detail=str(exc))
        )
        return

    lines = original.splitlines(keepends=True)
    filtered = [line for line in lines if not _PYPROJECT_DEP_RE.match(line)]

    if filtered == lines:
        result.outcomes.append(
            ActionOutcome(
                action=action, status="skipped",
                detail="no quoted list-item deps found; table-style deps need manual removal",
            )
        )
        return

    backup = pyproject_path.with_suffix(pyproject_path.suffix + ".bak")
    backup.write_text(original)
    pyproject_path.write_text("".join(filtered))
    result.outcomes.append(
        ActionOutcome(
            action=action, status="done", detail="entries removed",
            backup_path=backup,
        )
    )


def _execute_move_aside(
    action: CleanAction, *, project_root: Path, result: CleanResult,
) -> None:
    """Move a directory aside (rename with .bak suffix) within the project."""
    target = action.residue.path
    if target.is_file():
        target = target.parent

    try:
        target_resolved = target.resolve()
        root_resolved = project_root.resolve()
        target_resolved.relative_to(root_resolved)
    except (OSError, ValueError):
        result.outcomes.append(
            ActionOutcome(
                action=action, status="failed",
                detail=f"target {target} is outside project root",
            )
        )
        return

    if not target.is_dir():
        result.outcomes.append(
            ActionOutcome(action=action, status="skipped", detail="directory not found")
        )
        return

    backup = target.with_name(target.name + ".bak")
    if backup.exists():
        result.outcomes.append(
            ActionOutcome(
                action=action, status="skipped",
                detail=f"backup {backup.name} already exists",
            )
        )
        return

    try:
        target.rename(backup)
        result.outcomes.append(
            ActionOutcome(
                action=action, status="done",
                detail=f"moved to {backup.name}",
                backup_path=backup,
            )
        )
    except OSError as exc:
        result.outcomes.append(
            ActionOutcome(action=action, status="failed", detail=str(exc))
        )
