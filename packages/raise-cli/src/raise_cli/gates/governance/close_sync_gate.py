"""CloseSyncVerificationGate — code backstop for RAISE-10966 Jira-sync enforcement.

RAISE-10966 requires bugfix/story close to leave Jira in sync with git: the
issue must reach a Done-category status with the active release's fixVersion
assigned. For bugfix close that guarantee was, until RAISE-11770, enforced
only as prose in ``rai-bugfix-close/SKILL.md`` Step 2b — an LLM instruction
(run on ``model: haiku``) with no code backstop, and no read-back after the
transition/update write to confirm the mutation actually landed. RAISE-10936
closed with Jira left on 'Ready' (indeterminate, no fixVersion) because the
prose enforcement was never carried through to completion and nothing in
code caught it (RAISE-11770 RCA).

``verify_close_sync`` is the reusable, adapter-agnostic core — it re-reads
the issue and fails loudly on any mismatch, rather than trusting a prior
write call's return value. ``CloseSyncVerificationGate`` is a thin wrapper
resolving issue_key (from the bug branch) and expected fixVersion (from the
active release, same derivation as
``raise_cli.story.open_service._active_release_version``) so the check can
run as ``rai gate check gate-close-jira-sync``.

The pipeline enforces this gate at ``after:bug:close``: architecture-review
attestation remains at ``before:bug:close``, Jira transitions to Done, and only
then can this read-back postcondition be meaningful (RAISE-15567).

Architecture: RAISE-11770 (code backstop), RAISE-15567 (transition ordering).
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol

from raise_cli.adapters.id_utils import load_id_pattern, work_id_re
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.release_preflight import ReleasePreflightResult, run_release_preflight

if TYPE_CHECKING:
    from raise_cli.adapters.models.pm import IssueDetail

logger = logging.getLogger(__name__)

_SKIP_ENV = "RAISE_CLOSE_SYNC_SKIP"
_ISSUE_RE = re.compile(r"(?:bug|story)/(RAISE-\d+)/")
# _JIRA_KEY_RE is now compiled per-evaluate from id_pattern (RAISE-18508)


class AmbiguousMergeTargetError(Exception):
    """Raised when worktrees bound to the same issue disagree on merge_target.

    RAISE-18300: the registry may hold more than one worktree for an issue
    (e.g. a stale entry plus the real one) — silently picking either would
    reintroduce the cwd-dependent drift this resolution order exists to
    remove, so disagreement fails loud instead.
    """


class SupportsGetIssue(Protocol):
    """Minimal adapter surface ``verify_close_sync`` needs.

    Any object with a ``get_issue(key) -> IssueDetail`` method satisfies
    this — production callers pass a resolved PM adapter; tests pass a
    lightweight fake (see RAISE-11770 regression tests).
    """

    def get_issue(self, key: str) -> IssueDetail:
        """Return full issue detail for ``key``, re-read live from the adapter."""
        ...


def _remote_read_adapter(adapter: SupportsGetIssue) -> SupportsGetIssue:
    """Prefer the remote read surface when a composite adapter is configured.

    Close-sync verifies a Jira postcondition, so a composite adapter's local
    mirror is insufficient: it can be stale or contain only the fields written
    during a transition.  GraphRefreshAdapter is the normal outer wrapper and
    exposes its composite through ``delegate``; CompositeBacklogAdapter exposes
    remote adapters through ``remotes``.  Keep this structural so the gate
    stays independent of adapter implementation classes.
    """
    inner = getattr(adapter, "delegate", adapter)
    remotes = getattr(inner, "remotes", ())
    return remotes[0] if remotes else adapter


@dataclass(frozen=True)
class CloseSyncResult:
    """Outcome of a single ``verify_close_sync`` re-read check."""

    passed: bool
    issue_key: str
    status_category: str
    fix_versions: tuple[str, ...]
    expected_fix_version: str | None
    message: str


def verify_close_sync(
    *,
    issue_key: str,
    expected_fix_version: str | None,
    adapter: SupportsGetIssue,
) -> CloseSyncResult:
    """Re-read ``issue_key`` and assert it actually landed Done + fixVersion.

    This closes the gap RAISE-11770 identified: ``transition_issue`` and
    ``update_issue`` return success purely because the POST did not raise —
    neither the MCP tool, the adapter, nor the prose enforcement in
    ``rai-bugfix-close`` ever re-read Jira to confirm the mutation landed. A
    2xx-but-no-op POST (workflow condition/post-function silently rejects,
    or a fixVersion name Jira drops) would otherwise report success.

    Args:
        issue_key: The issue to verify (e.g. ``RAISE-10936``).
        expected_fix_version: Required fixVersion name, or ``None`` when the
            dev branch has no associated release (no fixVersion contract).
        adapter: Anything with ``get_issue(key) -> IssueDetail``.

    Returns:
        A ``CloseSyncResult`` — ``passed=True`` only when the re-read shows
        ``status_category == "done"`` AND (no fixVersion expected, or the
        expected fixVersion is present).
    """
    detail = adapter.get_issue(issue_key)
    status_category = detail.status_category or ""
    fix_versions = tuple(detail.fix_versions or ())

    done = status_category == "done"
    version_ok = expected_fix_version is None or expected_fix_version in fix_versions

    if done and version_ok:
        return CloseSyncResult(
            passed=True,
            issue_key=issue_key,
            status_category=status_category,
            fix_versions=fix_versions,
            expected_fix_version=expected_fix_version,
            message=f"{issue_key} confirmed Done (fixVersions={list(fix_versions)})",
        )

    problems: list[str] = []
    if not done:
        problems.append(f"status_category={status_category!r} (expected 'done')")
    if not version_ok:
        problems.append(
            f"fixVersion {expected_fix_version!r} not in {list(fix_versions)}"
        )
    return CloseSyncResult(
        passed=False,
        issue_key=issue_key,
        status_category=status_category,
        fix_versions=fix_versions,
        expected_fix_version=expected_fix_version,
        message=(
            f"{issue_key} Jira sync verification FAILED after close — "
            + "; ".join(problems)
        ),
    )


def _git_branch(working_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001
        return ""


def _jira_configured(working_dir: Path) -> bool:
    """True when a non-filesystem PM adapter (e.g. jira) is configured."""
    from raise_cli.adapters.backlog_config import get_configured_adapters

    configured = get_configured_adapters(working_dir)
    return bool(configured - {"filesystem"})


def _branch_target(working_dir: Path) -> str | None:
    """Return the release branch this worktree's branch tracks, if any."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "@{upstream}"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        if result.returncode == 0:
            upstream = result.stdout.strip()
            return upstream.removeprefix("origin/") if upstream else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("git rev-parse @{upstream} failed in %s: %s", working_dir, exc)
        return None
    return None


def _registered_merge_target(working_dir: Path) -> str | None:
    """Merge target for the worktree registered at this exact checkout, if any.

    RAISE-18300 priority 1 — the gate's own cwd is checked first, ahead of
    git upstream and the dev-branch fallback, so a bug worktree with no
    upstream configured (case B) still resolves correctly.
    """
    from raise_cli.session.open_service import get_worktree_merge_target

    try:
        return get_worktree_merge_target(working_dir, working_dir)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "worktree registry lookup by path failed for %s: %s", working_dir, exc
        )
        return None


def _issue_bound_merge_target(working_dir: Path, issue_key: str) -> str | None:
    """Merge target from worktree(s) bound to ``issue_key`` via ``stories``.

    RAISE-18300 priority 2 — includes closed worktrees, since the bug's own
    close may have already completed the worktree by the time this gate
    runs (case D: gate evaluated from a checkout other than the bug's own,
    e.g. the primary checkout). Raises ``AmbiguousMergeTargetError`` when
    bound worktrees disagree, rather than picking one silently.
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore

    try:
        worktrees = SqliteWorktreeStore(working_dir).list_worktrees(include_closed=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "worktree registry lookup by issue failed for %s: %s", issue_key, exc
        )
        return None

    targets = {wt.merge_target for wt in worktrees if issue_key in wt.stories}
    if not targets:
        return None
    if len(targets) > 1:
        raise AmbiguousMergeTargetError(
            f"{issue_key} is bound to worktrees with conflicting merge_target "
            f"values: {sorted(targets)} — resolve the registry before closing"
        )
    return next(iter(targets))


def _declared_release_branches(working_dir: Path) -> set[str]:
    """Every branch name the manifest declares as a release line.

    RAISE-18300: an upstream is only trustworthy as the resolution target
    when it names one of these — an ``origin/<bug-branch>`` upstream (case
    C) must never qualify (MUST-ARCH-003: resolved from the manifest, never
    from ``release/*`` name patterns or ``origin/``-specific assumptions).
    """
    from raise_cli.project_config.manifest import load_manifest

    try:
        manifest = load_manifest(working_dir)
    except Exception as exc:  # noqa: BLE001
        logger.warning("manifest load failed for %s: %s", working_dir, exc)
        return set()
    if manifest is None:
        return set()
    declared = {line.branch for line in manifest.branches.release_lines}
    declared.add(manifest.branches.development)
    return declared


def _resolve_target_branch(working_dir: Path, issue_key: str | None) -> str:
    """Resolve the release line a close should be verified against (RAISE-18300).

    Registry-first, cwd/upstream-independent resolution order:

    1. Worktree registered at this exact checkout -> its ``merge_target``.
    2. Worktree(s) (incl. closed) bound to ``issue_key`` -> their
       ``merge_target``, provided they agree; disagreement fails loud
       (``AmbiguousMergeTargetError``).
    3. git ``@{upstream}``, only when it names a manifest-declared release
       line — an ``origin/<bug-branch>`` upstream is ignored.
    4. ``resolve_dev_branch()`` — last-resort fallback (pre-existing
       behaviour, RAISE-17226).
    """
    from raise_cli.project_config import resolve_dev_branch

    target = _registered_merge_target(working_dir)
    if target:
        return target

    if issue_key is not None:
        target = _issue_bound_merge_target(working_dir, issue_key)
        if target:
            return target

    upstream = _branch_target(working_dir)
    if upstream is not None and upstream in _declared_release_branches(working_dir):
        return upstream

    return resolve_dev_branch(working_dir)


def _manifest_fix_version(working_dir: Path, target_branch: str) -> str | None:
    """Return the first declared fix_version for a release line, if any."""
    from raise_cli.project_config.manifest import load_manifest

    try:
        manifest = load_manifest(working_dir)
    except Exception:  # noqa: BLE001
        return None
    if manifest is None:
        return None
    for line in manifest.branches.release_lines:
        if line.branch == target_branch and line.fix_versions:
            return line.fix_versions[0]
    return None


def _expected_fix_version(
    working_dir: Path, issue_key: str | None = None
) -> str | None:
    """Resolve fixVersion from the branch's actual target, not the active line.

    Bugfix branches targeting a bugfix-only release line (e.g. release/3.1.0)
    must resolve against that line's fixVersion, not the active line (RAISE-17226).
    Manifest-declared fix_versions take precedence over pyproject.toml derivation
    since the manifest names the exact Jira version strings.

    ``issue_key`` enables the registry-first target resolution (RAISE-18300)
    — pass ``None`` only where no issue context exists yet (e.g. before the
    branch/context issue_key is resolved).
    """
    from raise_cli.release_version import resolve_fix_version

    target = _resolve_target_branch(working_dir, issue_key)
    return _manifest_fix_version(working_dir, target) or resolve_fix_version(
        working_dir, target
    )


def _is_version_stale(working_dir: Path) -> bool:
    """Return True when the worktree version differs from the release target version.

    Calls ``run_release_preflight`` to compare the locally resolved version
    against the release-branch HEAD. A divergence means the worktree has not
    yet merged the target branch, so the resolved fixVersion may be stale.
    """
    from raise_cli.project_config import resolve_dev_branch

    try:
        dev_branch = resolve_dev_branch(working_dir)
        preflight: ReleasePreflightResult = run_release_preflight(
            working_dir, dev_branch
        )
        return bool(
            preflight.local_version is not None
            and preflight.resolved_version is not None
            and preflight.local_version != preflight.resolved_version
        )
    except Exception:  # noqa: BLE001
        return False


class CloseSyncVerificationGate:
    """Code-level backstop confirming Jira landed Done + fixVersion after bug close.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Escape hatch: set ``RAISE_CLOSE_SYNC_SKIP=<reason>`` to bypass with a
    logged warning.
    """

    gate_id: ClassVar[str] = "gate-close-jira-sync"
    description: ClassVar[str] = (
        "Jira issue confirmed Done + fixVersion after bug/story close (RAISE-10966 backstop)"
    )
    workflow_point: ClassVar[str] = "after:bug:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Re-read the bug's Jira issue and fail loudly on any drift."""
        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            return GateResult(
                passed=True,
                skipped=True,
                gate_id=self.gate_id,
                message=f"Close-sync check skipped: {skip_reason}",
            )

        _key_re = work_id_re(load_id_pattern(context.working_dir))
        issue_key = context.issue_id
        if issue_key is not None and _key_re.fullmatch(issue_key) is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Invalid explicit issue id: {issue_key!r}",
            )
        if issue_key is None:
            branch = _git_branch(context.working_dir)
            issue_m = _ISSUE_RE.search(branch)
            issue_key = issue_m.group(1) if issue_m else None
        if issue_key is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No bug branch context detected — close-sync check not applicable",
            )
        if not _jira_configured(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No Jira adapter configured — close-sync check not applicable",
            )

        try:
            expected_fix_version = _expected_fix_version(context.working_dir, issue_key)
        except AmbiguousMergeTargetError as exc:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=str(exc),
            )

        from raise_cli.adapters.resolve import resolve_pm_adapter

        try:
            adapter = resolve_pm_adapter(None, context.working_dir)
            result = verify_close_sync(
                issue_key=issue_key,
                expected_fix_version=expected_fix_version,
                adapter=_remote_read_adapter(adapter),
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Could not re-read {issue_key} to verify close sync: {exc}",
                details=(
                    f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
                ),
            )

        if result.passed:
            return GateResult(passed=True, gate_id=self.gate_id, message=result.message)

        details: list[str] = [f"rai backlog get {issue_key}"]
        if expected_fix_version and _is_version_stale(context.working_dir):
            details.append(
                "resolved fixVersion may be stale — run rai release version-open"
            )
        details.append(f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}")

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=result.message,
            details=tuple(details),
        )
