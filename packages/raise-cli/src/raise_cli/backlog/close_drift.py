"""Close-sync drift detection by git ancestry (RAISE-15879, S15853.4).

`gate-close-jira-sync` verifies Jira-side state only — status and
fixVersion. It never asks git whether the code actually shipped, so an
issue can be closed Done with the active release fixVersion while its
work never landed (RAISE-14589). This module answers that question,
read-only: for every Done issue in the release, resolve landing evidence
from git commit messages, then classify with a single
``git merge-base --is-ancestor`` test against the development ref.

Three verdicts (D2), not a drift boolean:
  - LANDED — evidence commit is an ancestor of the development ref.
  - UNLANDED — evidence commit exists but is not an ancestor (high
    confidence — the drifted-close case this module exists to find).
  - NO_EVIDENCE — no commit anywhere cites the key (weaker signal; may be
    a spike, docs-only close, or work committed under a sibling key).

Landing evidence comes from commit messages, not branch ancestry (D1):
branches are deleted after merge (project rule), so branch resolution
would fail precisely in the healthy case.
"""

from __future__ import annotations

import re
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Sequence

    from raise_cli.adapters.models import IssueSummary


class DriftVerdict(StrEnum):
    """Landing status of a Done issue against the development ref."""

    LANDED = "landed"
    UNLANDED = "unlanded"
    NO_EVIDENCE = "no-evidence"


class DriftCandidate(BaseModel, frozen=True):
    """One Jira issue classified against git ancestry."""

    key: str
    summary: str
    verdict: DriftVerdict
    evidence_sha: str | None = Field(
        default=None,
        description="Commit that produced the verdict. Set for LANDED and "
        "UNLANDED, None for NO_EVIDENCE.",
    )


class CloseDriftReport(BaseModel, frozen=True):
    """Result of classifying a set of Done issues against a development ref."""

    fix_version: str
    fix_version_source: str | None
    dev_ref: str
    dev_ref_sha: str | None
    candidates: tuple[DriftCandidate, ...] = ()
    warnings: tuple[str, ...] = Field(
        default=(),
        description="Non-empty when the run could not fully verify — e.g. the "
        "development ref didn't resolve, or the git-grep evidence search "
        "itself failed. Every consumer of the report (either --format) must "
        "treat a non-empty warnings tuple as 'couldn't verify', never as a "
        "confident clean result (F1/F2, RAISE-15879 round 2).",
    )

    @property
    def degraded(self) -> bool:
        """True when the run couldn't fully verify — see ``warnings``."""
        return bool(self.warnings)

    @property
    def drifted(self) -> tuple[DriftCandidate, ...]:
        """Candidates that did not land, unlanded first."""
        order = {DriftVerdict.UNLANDED: 0, DriftVerdict.NO_EVIDENCE: 1}
        return tuple(
            sorted(
                (c for c in self.candidates if c.verdict is not DriftVerdict.LANDED),
                key=lambda c: (order[c.verdict], c.key),
            )
        )


def issue_key_pattern(key: str) -> str:
    """Perl-regexp matching the issue number in any form the repo uses.

    Matches RAISE-15753, E15753, e15753, S15753, s15753.4 and slugs such as
    e14988-worktree-lifecycle-management. Digit-bounded on both sides so
    RAISE-1304 never matches a RAISE-13048 commit. Requires lookaround
    (Python ``re`` here; ``--perl-regexp`` when passed to ``git log``) —
    POSIX ERE has no lookaround.
    """
    number = key.rsplit("-", 1)[-1]
    return rf"(?i)(?<![0-9])(RAISE-|[ES])0*{re.escape(number)}(?![0-9])"


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Run git and return the completed process, or None if git failed to spawn."""
    try:
        return subprocess.run(  # noqa: S603 — fixed git executable, controlled args
            ["git", *args],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None


def _git_text(project_root: Path, *args: str) -> str | None:
    """Run git and return trimmed stdout, or None on any failure.

    Collapses "command failed" and "succeeded with no output" to the same
    None — correct for callers like ``rev-parse`` where a non-zero exit is
    itself the meaningful, expected-to-happen result (an unresolved ref).
    Callers that need to tell "no match" apart from "the command itself
    broke" (e.g. the evidence-search grep, F2) must not use this helper —
    see ``resolve_evidence_commit``.
    """
    result = _run_git(project_root, *args)
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _git_status(project_root: Path, *args: str) -> int:
    """Run git and return its exit code, or 1 if git itself failed to run."""
    result = _run_git(project_root, *args)
    return 1 if result is None else result.returncode


def resolve_evidence_commit(
    project_root: Path, pattern: str, ref: str | None
) -> tuple[str | None, bool]:
    """Newest commit whose message cites the key. ``ref=None`` searches all refs.

    Returns ``(sha_or_none, grep_failed)``. ``grep_failed=True`` means
    ``git log --grep`` itself exited non-zero — e.g. ``--perl-regexp``
    unsupported by this git build, or git failed to spawn at all — as
    opposed to running fine and simply finding no match (F2, RAISE-15879
    round 2). Collapsing those two cases to the same ``None`` is exactly
    what let a broken evidence search render as a confident "no evidence"
    instead of "couldn't verify".
    """
    scope = [ref] if ref else ["--all"]
    result = _run_git(
        project_root,
        "log",
        *scope,
        "--perl-regexp",
        f"--grep={pattern}",
        "--format=%H",
        "-1",
    )
    if result is None or result.returncode != 0:
        return None, True
    return result.stdout.strip() or None, False


def is_ancestor(project_root: Path, sha: str, ref: str) -> bool:
    """True when sha is reachable from ref. Same primitive as guard:tag-ancestry."""
    return _git_status(project_root, "merge-base", "--is-ancestor", sha, ref) == 0


def resolve_mr_branch(project_root: Path, evidence_sha: str) -> str | None:
    """Remote branch (if any) that still contains ``evidence_sha`` (S15853.5).

    There is no persisted MR reference anywhere in Jira for an UNLANDED
    candidate to resolve its MR from (verified live — see s15853.5-story.md's
    premise correction; ``rai-mr-create`` writes its metadata block into the
    MR *description*, never into Jira). Git is the only real source: if the
    branch that produced the evidence commit hasn't been deleted (project
    rule: branches are deleted after merge — the healthy case — so an
    UNLANDED candidate's branch may well still be alive), its name is
    resolvable directly from the commit.

    Returns ``None`` when no remote branch contains the commit — either the
    branch was deleted, or it was never fetched locally. Both degrade to
    "drift sin clasificar" in the caller, a legitimate terminal state
    already established by S15853.4.
    """
    result = _run_git(
        project_root,
        "for-each-ref",
        "--contains",
        evidence_sha,
        "--format=%(refname:short)",
        "refs/remotes/origin",
    )
    if result is None or result.returncode != 0:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    return lines[0].removeprefix("origin/")


def resolve_dev_ref(project_root: Path, dev_branch: str) -> str:
    """Prefer ``origin/<dev_branch>``, fall back to the local branch name (D4).

    Mirrors ``resolve_target_fix_version``'s own two-step fallback. If
    neither ref actually exists, the local branch name is still returned —
    ancestry then naturally degrades per D4/AC7 rather than raising.
    """
    remote_ref = f"origin/{dev_branch}"
    resolved = _git_text(
        project_root, "rev-parse", "--verify", "--quiet", f"{remote_ref}^{{commit}}"
    )
    return remote_ref if resolved is not None else dev_branch


def fetch_dev_ref(project_root: Path, dev_branch: str) -> str | None:
    """Fetch ``origin/<dev_branch>`` so ancestry checks see current state.

    Opt-in (D6, AC9): returns ``None`` on success, or an error message on
    failure. A fetch failure is a warning the caller may surface — it must
    never become a hard stop, so this never raises.
    """
    try:
        result = subprocess.run(  # noqa: S603 — fixed git executable, controlled args
            ["git", "fetch", "origin", dev_branch],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return str(exc)
    if result.returncode != 0:
        return result.stderr.strip() or "git fetch failed"
    return None


def _classify(
    project_root: Path, key: str, dev_ref: str, *, dev_ref_resolved: bool
) -> tuple[DriftVerdict, str | None, bool]:
    """Classify one issue key per D4: dev-ref evidence first, then all-refs.

    ``dev_ref_resolved=False`` means ``dev_ref`` didn't resolve to a commit
    at all (AC7) — ancestry can never be confirmed in that state, so
    classification degrades straight to NO_EVIDENCE rather than trusting the
    ``--all`` fallback, which would report UNLANDED for any issue with a
    commit anywhere and turn "can't verify" into "widespread drift" (R2).

    Returns ``(verdict, evidence_sha, grep_failed)``. ``grep_failed=True``
    means the evidence search itself broke (F2) — the caller surfaces this
    as a run-level warning so a systematically-broken grep can't render as a
    clean "no drift found" either.
    """
    if not dev_ref_resolved:
        return DriftVerdict.NO_EVIDENCE, None, False

    pattern = issue_key_pattern(key)

    dev_sha, dev_failed = resolve_evidence_commit(project_root, pattern, dev_ref)
    if dev_sha and is_ancestor(project_root, dev_sha, dev_ref):
        return DriftVerdict.LANDED, dev_sha, dev_failed

    any_sha, any_failed = resolve_evidence_commit(project_root, pattern, None)
    grep_failed = dev_failed or any_failed
    if any_sha:
        return DriftVerdict.UNLANDED, any_sha, grep_failed

    return DriftVerdict.NO_EVIDENCE, None, grep_failed


def detect_close_drift(
    *,
    project_root: Path,
    issues: Sequence[IssueSummary],
    dev_ref: str,
    fix_version: str,
    fix_version_source: str | None = None,
) -> CloseDriftReport:
    """Classify each Done issue as landed, unlanded, or without evidence.

    Pure with respect to the backlog: issues are already fetched and
    filtered by the caller (server-side JQL — D7), so this is
    unit-testable with a plain list. Only git is subprocessed.
    """
    dev_ref_sha = _git_text(project_root, "rev-parse", dev_ref)
    dev_ref_resolved = dev_ref_sha is not None

    warnings: list[str] = []
    if not dev_ref_resolved:
        warnings.append(
            f"development ref '{dev_ref}' could not be resolved locally - "
            "every verdict is a degraded NO_EVIDENCE, not a confirmed "
            "absence of drift. Run with --fetch or verify the ref exists."
        )

    candidates: list[DriftCandidate] = []
    grep_failed = False
    for issue in issues:
        candidate, failed = _candidate_for(
            project_root, issue, dev_ref, dev_ref_resolved=dev_ref_resolved
        )
        candidates.append(candidate)
        grep_failed = grep_failed or failed

    if grep_failed:
        warnings.append(
            "the git evidence search (git log --grep) failed for one or more "
            "issues - this git build or environment may not support the "
            "options used; affected verdicts may read as no-evidence when "
            "the search itself could not run."
        )

    return CloseDriftReport(
        fix_version=fix_version,
        fix_version_source=fix_version_source,
        dev_ref=dev_ref,
        dev_ref_sha=dev_ref_sha,
        candidates=tuple(candidates),
        warnings=tuple(warnings),
    )


def _candidate_for(
    project_root: Path, issue: IssueSummary, dev_ref: str, *, dev_ref_resolved: bool
) -> tuple[DriftCandidate, bool]:
    verdict, sha, grep_failed = _classify(
        project_root, issue.key, dev_ref, dev_ref_resolved=dev_ref_resolved
    )
    return (
        DriftCandidate(
            key=issue.key,
            summary=issue.summary,
            verdict=verdict,
            evidence_sha=sha,
        ),
        grep_failed,
    )
