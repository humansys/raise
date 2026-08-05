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

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol

from raise_cli.gates.models import GateContext, GateResult

if TYPE_CHECKING:
    from raise_cli.adapters.models.pm import IssueDetail

_SKIP_ENV = "RAISE_CLOSE_SYNC_SKIP"
_BUG_RE = re.compile(r"bug/(RAISE-\d+)/")
_JIRA_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class SupportsGetIssue(Protocol):
    """Minimal adapter surface ``verify_close_sync`` needs.

    Any object with a ``get_issue(key) -> IssueDetail`` method satisfies
    this — production callers pass a resolved PM adapter; tests pass a
    lightweight fake (see RAISE-11770 regression tests).
    """

    def get_issue(self, key: str) -> IssueDetail:
        """Return full issue detail for ``key``, re-read live from the adapter."""
        ...


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


def _expected_fix_version(working_dir: Path) -> str | None:
    """Resolve the shared active-release fixVersion policy."""
    from raise_cli.release_version import resolve_fix_version
    from raise_cli.story.open_service import resolve_dev_branch

    return resolve_fix_version(working_dir, resolve_dev_branch(working_dir))


class CloseSyncVerificationGate:
    """Code-level backstop confirming Jira landed Done + fixVersion after bug close.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Escape hatch: set ``RAISE_CLOSE_SYNC_SKIP=<reason>`` to bypass with a
    logged warning.
    """

    gate_id: ClassVar[str] = "gate-close-jira-sync"
    description: ClassVar[str] = (
        "Jira issue confirmed Done + fixVersion after bug close (RAISE-10966 backstop)"
    )
    workflow_point: ClassVar[str] = "after:bug:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Re-read the bug's Jira issue and fail loudly on any drift."""
        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Close-sync check skipped: {skip_reason}",
            )

        issue_key = context.issue_id
        if issue_key is not None and _JIRA_KEY_RE.fullmatch(issue_key) is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Invalid explicit issue id: {issue_key!r}",
            )
        if issue_key is None:
            branch = _git_branch(context.working_dir)
            bug_m = _BUG_RE.search(branch)
            issue_key = bug_m.group(1) if bug_m else None
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

        expected_fix_version = _expected_fix_version(context.working_dir)

        from raise_cli.adapters.resolve import resolve_pm_adapter

        try:
            adapter = resolve_pm_adapter(None, context.working_dir)
            result = verify_close_sync(
                issue_key=issue_key,
                expected_fix_version=expected_fix_version,
                adapter=adapter,
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

        details = [f"rai backlog get {issue_key}"]
        if expected_fix_version:
            details.append(
                f'rai backlog update {issue_key} -F \'fixVersions=[{{"name": '
                f'"{expected_fix_version}"}}]\''
            )
        details.append(f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}")

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=result.message,
            details=tuple(details),
        )
