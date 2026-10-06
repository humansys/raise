"""Branch resolution utilities — project_config tier (RAISE-16462).

Extracted from ``raise_cli.story.open_service`` so that both T2 service modules
and T3 domain modules can import without creating upward edges.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from raise_cli.project_config.manifest import ReleaseLine

_RELEASE_BRANCH_RE = re.compile(r"^release/(?P<base>\d+\.\d+\.\d+)$")


def _release_version_key(branch: str) -> tuple[int, int, int] | None:
    """Parse a ``release/X.Y.Z`` branch into a sortable version tuple.

    Deliberately not imported from ``raise_cli.release_version``: that module
    is T2, this package is T5 (foundation) per the RAISE-16340 layer contract
    — T5 cannot depend upward on T2. The two implementations are trivial and
    independently pure; the layer boundary, not style, is why this exists.
    """
    match = _RELEASE_BRANCH_RE.fullmatch(branch)
    if match is None:
        return None
    major, minor, patch = match.group("base").split(".")
    return (int(major), int(minor), int(patch))


def _validate_branch_exists(project: Path, branch: str) -> None:
    """Verifica que origin/{branch} exista en los refs ya fetcheados (RAISE-17563).

    Fail-open cuando git no está disponible o el directorio no es un repo git.
    Solo lanza ``ManifestInvalidError`` cuando git confirma que el branch
    definitivamente no existe en origin.
    """
    from raise_cli.exceptions import ManifestInvalidError

    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=project,
            capture_output=True,
        )
    except OSError:
        logger.warning(
            "No se pudo verificar existencia de origin/%s — git no disponible",
            branch,
        )
        return

    if git_check.returncode != 0:
        logger.warning(
            "No se pudo verificar existencia de origin/%s — %s no es un repositorio git",
            branch,
            project,
        )
        return

    origin_check = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=project,
        capture_output=True,
    )
    if origin_check.returncode != 0:
        logger.warning(
            "No se pudo verificar existencia de origin/%s — remote 'origin' no configurado",
            branch,
        )
        return

    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"origin/{branch}"],
        cwd=project,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ManifestInvalidError(
            f"Branch de desarrollo 'origin/{branch}' no existe en refs remotos. "
            "Ejecuta git fetch o actualiza branches.development en .raise/manifest.yaml"
        )


def resolve_dev_branch(project: Path) -> str:
    """Development branch from explicit environment or manifest configuration.

    ``RAISE_DEVELOPMENT_BRANCH`` lets CI delta gates compare against the actual
    merge-request target. Normal CLI usage remains manifest-driven.

    Manifest classification (RAISE-18074): a missing manifest (``not_found``)
    is not an error — nothing to read falls back to ``"main"`` with a warning.
    An empty or schema-invalid manifest (``empty``/``invalid``) raises
    ``ManifestInvalidError`` — same behaviour as ``resolve_target()``
    (RAISE-17092/17093). The resolved branch name is validated against
    already-fetched remote refs (RAISE-17563).
    """
    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override

    from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
    from raise_cli.exceptions import ManifestInvalidError
    from raise_cli.project_config.manifest import load_manifest_result

    load_result = load_manifest_result(project)

    if load_result.status == "not_found":
        logger.warning(
            "Manifest no encontrado en %s — usando 'main' como branch de desarrollo",
            project,
        )
        return "main"

    if load_result.status in ("invalid", "empty"):
        manifest_path = get_raise_dir(project) / MANIFEST_FILE
        raise ManifestInvalidError(f"{manifest_path}: {load_result.error}")

    manifest = load_result.manifest
    if manifest is None:
        raise AssertionError("load_manifest_result() status='ok' must carry a manifest")

    branch = manifest.branches.development
    _validate_branch_exists(project, branch)
    return branch


def _resolve_registry_merge_target(repo_root: Path) -> str | None:
    """Return the worktree registry's ``merge_target`` for ``repo_root``, or None.

    Mirrors the primitive ``gate-revert-scope`` already uses
    (``SqliteWorktreeStore(...).get_by_path(...)``, RAISE-17599). Any lookup
    failure — no registered worktree, a corrupt/locked local DB, or any
    other storage error — degrades to ``None`` (the caller falls back to
    ``resolve_dev_branch``'s manifest default) rather than raising: a local
    gate's base-branch resolution must never crash on registry trouble
    (MUST-CRAFT-002 — every ``except Exception`` here logs before degrading).
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        worktree = SqliteWorktreeStore(repo_root).get_by_path(str(repo_root))
    except WorktreeNotFoundError:
        logger.debug(
            "No worktree registered at %s — falling back to manifest development branch",
            repo_root,
        )
        return None
    except Exception:  # noqa: BLE001 — registry lookup degrades, never crashes a gate
        logger.warning(
            "Worktree registry lookup failed for %s — falling back to manifest "
            "development branch",
            repo_root,
            exc_info=True,
        )
        return None
    return worktree.merge_target or None


def _prefer_remote_tracking_ref(repo_root: Path, branch: str) -> str:
    """Return ``origin/<branch>`` when that remote-tracking ref resolves, else ``branch``.

    Only called for non-CI-env-supplied bases (RAISE-18299): CI already
    fetches its MR target ref explicitly and passes the exact name via
    ``RAISE_DEVELOPMENT_BRANCH``, so that path is left verbatim. Outside CI,
    a local branch ref can be stale relative to what was last fetched (a
    worktree that ran ``git fetch`` without fast-forwarding its own local
    branch) — preferring the remote-tracking ref, when it exists, avoids
    computing a merge-base against that stale position.
    """
    if branch.startswith("origin/"):
        return branch
    remote_ref = f"origin/{branch}"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", remote_ref],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError:
        return branch
    return remote_ref if result.returncode == 0 else branch


def _ref_resolves(repo_root: Path, ref: str) -> bool:
    """True when git can resolve ``ref``; also True when git can't be run.

    An ``OSError`` means existence is unknowable, not disproven — keep the
    ref rather than discard a possibly-valid registry target.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError:
        return True
    return result.returncode == 0


def resolve_gate_base_branch(repo_root: Path) -> str:
    """Base branch for local git-range gates (RAISE-18299).

    Precedence: CI-supplied MR target (``RAISE_DEVELOPMENT_BRANCH``, verbatim
    — CI already fetches exactly that ref) -> the registered worktree's
    ``merge_target`` for ``repo_root`` (only when git can resolve it) ->
    ``resolve_dev_branch``'s manifest
    default (unchanged legacy behaviour, including its own env check — a
    plain positional read here would be redundant, not a second source).

    Outside the CI-env path, the resolved branch is preferred as
    ``origin/<branch>`` when that remote-tracking ref exists locally,
    trading a possibly-stale local branch ref for the last-fetched remote
    state. The registry and remote-ref steps never raise; the manifest
    fallback keeps ``resolve_dev_branch``'s contract and may raise
    ``ManifestInvalidError`` (empty/invalid manifest, or ``origin/<dev>``
    missing — RAISE-17563). A gate calling this degrades an unresolvable
    *name* the same way it already did for ``resolve_dev_branch``'s output;
    a raised manifest error surfaces as a failed gate via the runner's
    exception isolation, never as a pass.

    An unresolvable registry ``merge_target`` (deleted or never fetched) is
    treated as no registration: range gates then run against the manifest
    line instead of skipping. On a cross-line worktree that can be the newer
    line — a real check against the wrong base beats a silent ``main``
    fallback (false PASS); fetch the target to get the right one.
    """
    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override

    target = _resolve_registry_merge_target(repo_root)
    if target is not None:
        ref = _prefer_remote_tracking_ref(repo_root, target)
        if _ref_resolves(repo_root, ref):
            return ref
        # A stale merge_target (ref deleted/never fetched) must not become the
        # base: callers' fallbacks (e.g. schema-lock's ``main``) would then
        # compare against the wrong line — a false PASS (RAISE-18328 panel).
        logger.warning(
            "Registered merge_target %r for %s does not resolve — falling back "
            "to manifest development branch",
            target,
            repo_root,
        )

    return _prefer_remote_tracking_ref(repo_root, resolve_dev_branch(repo_root))


def resolve_scm(project: Path) -> str | None:
    """SCM provider from explicit environment or manifest configuration.

    Same override chain as ``resolve_dev_branch``: env → manifest → default.
    Unlike the dev branch, the default is ``None`` — absence of a detected
    or configured SCM is not a guess (RAISE-16561).
    """
    override = os.environ.get("RAISE_SCM", "").strip()
    if override:
        return override
    with suppress(Exception):
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.scm
    return None


def resolve_source_branch() -> str | None:
    """MR source branch from CI-supplied pipeline config.

    ``CI_MERGE_REQUEST_SOURCE_BRANCH_NAME`` is set by GitLab CI in MR
    pipelines. It is CI-supplied infrastructure config — the same trust
    category as ``RAISE_DEVELOPMENT_BRANCH`` — not an agent-controlled
    escape hatch (RAISE-16748).
    """
    value = os.environ.get("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", "").strip()
    return value or None


def resolve_merge_strategy(project: Path) -> str | None:
    """Merge strategy from explicit environment or manifest configuration.

    Same override chain as ``resolve_dev_branch``: env → manifest → default.
    Unlike the dev branch, the default is ``None`` — absence of a detected
    or configured merge strategy is not a guess (RAISE-16561).
    """
    override = os.environ.get("RAISE_MERGE_STRATEGY", "").strip()
    if override:
        return override
    with suppress(Exception):
        from raise_cli.project_config.manifest import load_manifest

        manifest = load_manifest(project)
        if manifest is not None:
            return manifest.branches.merge_strategy
    return None


# ---------------------------------------------------------------------------
# Multi-release-line resolution (RAISE-17066)
# ---------------------------------------------------------------------------

_FEATURE_WORK_TYPES = frozenset({"story", "feature", "epic"})


def _resolve_from_lines(
    release_lines: list[ReleaseLine],
    work_type: str,
    fix_version: str | None,
) -> str:
    from raise_cli.exceptions import AmbiguousTargetError

    non_sunset = [ln for ln in release_lines if ln.status != "sunset"]

    if fix_version:
        for ln in non_sunset:
            if fix_version in ln.fix_versions:
                return ln.branch
        raise AmbiguousTargetError(
            f"fix_version '{fix_version}' not found in any active release line",
        )

    if len(non_sunset) == 1:
        return non_sunset[0].branch

    if work_type == "bugfix":
        bugfix_only = [ln for ln in non_sunset if ln.status == "bugfix-only"]
        if len(bugfix_only) == 1:
            return bugfix_only[0].branch

    # Step 5: all other work -> active line (includes bugfix when >1 bugfix-only lines)
    active = [ln for ln in release_lines if ln.status == "active"]
    if active:
        return active[0].branch

    raise AmbiguousTargetError(
        "Cannot determine target branch — no active release line found",
    )


def resolve_target(
    project: Path,
    work_type: str,
    fix_version: str | None = None,
    explicit_base: str | None = None,
) -> str:
    """Deterministic target-branch resolution chain (RAISE-17066).

    Chain: explicit_base > env > fix_version mapping > work-type default > FAIL.
    Empty ``release_lines`` triggers legacy mode (``resolve_dev_branch``).

    Manifest classification (RAISE-17532): a missing manifest (``not_found``)
    is not an error — nothing to read falls back to ``"main"``, unchanged
    behaviour. An empty or schema-invalid manifest (``empty``/``invalid``),
    however, raises ``ManifestInvalidError`` instead of silently returning
    ``"main"`` — a corrupt/empty manifest must never silently route work to
    the wrong branch (RAISE-17092/17093).
    """
    from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
    from raise_cli.exceptions import ManifestInvalidError
    from raise_cli.project_config.manifest import load_manifest_result

    if explicit_base:
        return explicit_base

    override = os.environ.get("RAISE_DEVELOPMENT_BRANCH", "").strip()
    if override:
        return override

    load_result = load_manifest_result(project)

    if load_result.status == "not_found":
        return "main"

    if load_result.status in ("invalid", "empty"):
        manifest_path = get_raise_dir(project) / MANIFEST_FILE
        raise ManifestInvalidError(f"{manifest_path}: {load_result.error}")

    manifest = load_result.manifest
    if manifest is None:
        # Unreachable: status == "ok" always carries a manifest — narrows
        # the type for the checker without an `assert` statement (S101).
        raise AssertionError("load_manifest_result() status='ok' must carry a manifest")

    lines = manifest.branches.release_lines
    if not lines:
        return manifest.branches.development

    return _resolve_from_lines(lines, work_type, fix_version)


def check_admission(
    target_branch: str,
    work_type: str,
    release_lines: list[ReleaseLine],
) -> None:
    """Reject work that violates release-line lifecycle policy."""
    from raise_cli.exceptions import AdmissionError

    for ln in release_lines:
        if ln.branch != target_branch:
            continue
        if ln.status == "sunset":
            raise AdmissionError(
                f"Branch {target_branch} is sunset — no work accepted",
            )
        if ln.status == "bugfix-only" and work_type in _FEATURE_WORK_TYPES:
            raise AdmissionError(
                f"Branch {target_branch} is bugfix-only — feature/story work rejected",
            )
        return
    # Branch not in release_lines — pass defensively (may be manually specified)


# ---------------------------------------------------------------------------
# Forward-merge propagation chain (RAISE-17076 / S17066.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hop:
    """One forward-merge from a release line to the next non-sunset line."""

    index: int
    source: str
    target: str
    target_status: str


@dataclass(frozen=True)
class SkippedLine:
    """A release line excluded from a computed propagation chain."""

    branch: str
    reason: str


def propagation_chain(
    release_lines: list[ReleaseLine], source_branch: str
) -> tuple[list[Hop], list[SkippedLine]]:
    """Ordered hops from ``source_branch`` to every newer non-sunset line.

    ``main`` is never a target — ``release_lines`` only ever contains release
    lines by construction (ADR-033). Sunset lines newer than the source are
    skipped and reported rather than silently dropped, so
    ``3.1.0 -> [3.2.0 sunset] -> 3.3.0`` yields a single 3.1.0 -> 3.3.0 hop.

    Raises AmbiguousTargetError if ``source_branch`` is not a declared
    release line, is itself sunset, or any declared line is not a
    well-formed ``release/X.Y.Z`` branch.
    """
    from raise_cli.exceptions import AmbiguousTargetError

    keyed: list[tuple[tuple[int, int, int], ReleaseLine]] = []
    for line in release_lines:
        key = _release_version_key(line.branch)
        if key is None:
            raise AmbiguousTargetError(
                f"release line '{line.branch}' is not a release/X.Y.Z branch",
            )
        keyed.append((key, line))
    keyed.sort(key=lambda item: item[0])

    source_key = _release_version_key(source_branch)
    source_line = next((ln for ln in release_lines if ln.branch == source_branch), None)
    if source_key is None or source_line is None:
        raise AmbiguousTargetError(
            f"source '{source_branch}' is not a declared release line "
            "(branches.release_lines)",
        )
    if source_line.status == "sunset":
        raise AmbiguousTargetError(f"source '{source_branch}' is sunset")

    hops: list[Hop] = []
    skipped: list[SkippedLine] = []
    current_source = source_branch
    for key, line in keyed:
        if key <= source_key:
            continue
        if line.status == "sunset":
            skipped.append(SkippedLine(branch=line.branch, reason="sunset"))
            continue
        hops.append(
            Hop(
                index=len(hops) + 1,
                source=current_source,
                target=line.branch,
                target_status=line.status,
            )
        )
        current_source = line.branch

    return hops, skipped


def propagation_branch(work_id: str, source: str, target: str) -> str:
    """``forward-merge/{work_id}/{src_ver}-to-{tgt_ver}`` (D4)."""
    src_ver = source.removeprefix("release/")
    tgt_ver = target.removeprefix("release/")
    return f"forward-merge/{work_id}/{src_ver}-to-{tgt_ver}"
