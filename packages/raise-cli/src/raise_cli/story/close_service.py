"""Composite story-close service — S7884.3 (E7884 K1, ADR-093/ADR-024).

Ports the deterministic close sequence of the rai-story-close skill
(retro gate, hygiene, merge-target resolution, --no-ff merge, branch
cleanup, worktree restoration, Done transition) into tested code.

Judgment stays with the LLM: AR checklist (P1-P3), epic-scope checkbox
edits and retro content are NOT absorbed here (design D3). Jidoka:
merge conflicts abort + block, a missing retro blocks, ambiguity in the
Done transition blocks with candidates.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from raise_cli.release_preflight import ReleasePreflightResult, run_release_preflight
from raise_cli.session.open_service import (
    STATUS_RANK,
    CheckResult,
    check_hygiene,
    run_git,
)
from raise_cli.story.open_service import transition_backlog
from raise_cli.telemetry.trailer import resolve_session_id, with_session_trailer


class StoryCloseReport(BaseModel):
    """Composite result of a story close: every deterministic step."""

    status: str
    release_preflight: ReleasePreflightResult
    retro: CheckResult
    hygiene: CheckResult
    merge: CheckResult
    cleanup: CheckResult
    restore: CheckResult
    backlog: CheckResult


def _skipped(name: str) -> CheckResult:
    return CheckResult(name=name, status="ok", data={"skipped": True})


def _strict_release_preflight(
    project: Path, development_branch: str, jira_key: str
) -> ReleasePreflightResult:
    """Resolve optional Jira capability and run the pre-mutation release check."""
    from raise_cli.adapters.backlog_config import get_configured_adapters
    from raise_cli.adapters.protocols import ProjectVersionManagementAdapter
    from raise_cli.adapters.resolve import resolve_pm_adapter

    project_key = ""
    adapter = None
    adapter_error = ""
    if jira_key and get_configured_adapters(project) - {"filesystem"}:
        project_key = jira_key.split("-", 1)[0]
        try:
            candidate = resolve_pm_adapter(None, project_root=project)
            if isinstance(candidate, ProjectVersionManagementAdapter):
                adapter = candidate
            else:
                adapter_error = "configured adapter cannot list project versions"
        except Exception as exc:  # noqa: BLE001 — converted to strict diagnostic
            adapter_error = str(exc)
    return run_release_preflight(
        project,
        development_branch,
        project_key=project_key,
        adapter=adapter,
        adapter_error=adapter_error,
        strict=True,
    )


def check_retro(project: Path, epic_dir: str, story_id: str) -> CheckResult:
    """Retrospective must exist before close — no exceptions."""
    sid = story_id.lower()
    retro = (
        project / "work" / "epics" / epic_dir / "stories" / f"{sid}-retrospective.md"
    )
    if retro.is_file():
        return CheckResult(
            name="retro",
            status="ok",
            data={"path": str(retro.relative_to(project))},
        )
    return CheckResult(
        name="retro",
        status="blocked",
        data={
            "missing": str(retro.relative_to(project)),
            "action": "run /rai-story-review first",
        },
    )


def resolve_merge_target(
    project: Path,
    cwd: Path,
    story_id: str,
    *,
    dev_branch: str,
) -> tuple[str, str]:
    """Three-tier merge-target resolution, mirroring the legacy skill.

    Returns ``(target, tier)`` where tier is worktree|epic-branch|dev.
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        worktree = SqliteWorktreeStore(project).get_by_path(str(cwd))
        # Stories merge to the worktree's OWN branch — merge_target is what
        # the worktree itself merges to at /rai-worktree-close (QR S7884.3:
        # evidence = S7884.1/.2 merges landed on worktree-e7884-lean-muda).
        if worktree.branch:
            return worktree.branch, "worktree"
    except WorktreeNotFoundError:
        pass

    epic_n = ""
    sid = story_id.lower().lstrip("s")
    if "." in sid:
        epic_n = sid.split(".", 1)[0]
    if epic_n:
        for pattern in (f"worktree-e{epic_n}*", f"epic/*{epic_n}*"):
            proc = run_git(cwd, "branch", "--list", pattern)
            if proc is not None and proc.returncode == 0:
                branches = [b.strip().lstrip("* ") for b in proc.stdout.splitlines()]
                branches = [b for b in branches if b]
                if branches:
                    return branches[0], "epic-branch"

    return dev_branch, "dev"


def merge_story(
    repo: Path,
    story_branch: str,
    target: str,
    *,
    message: str,
) -> CheckResult:
    """Merge the story branch into *target* with --no-ff.

    Conflicts abort the merge and restore the original branch (jidoka):
    the repo is never left mid-merge.
    """
    original_proc = run_git(repo, "branch", "--show-current")
    original = original_proc.stdout.strip() if original_proc else ""

    proc = run_git(repo, "checkout", target)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="merge",
            status="blocked",
            data={
                "reason": "target-checkout-failed",
                "target": target,
                "error": (proc.stderr.strip() if proc else "git unavailable"),
            },
        )
    current_proc = run_git(repo, "branch", "--show-current")
    if (current_proc.stdout.strip() if current_proc else "") != target:
        return CheckResult(
            name="merge",
            status="blocked",
            data={"reason": "branch-assertion-failed", "target": target},
        )

    session_id = resolve_session_id()
    message = with_session_trailer(message, session_id)
    proc = run_git(repo, "merge", story_branch, "--no-ff", "-m", message)
    if proc is None or proc.returncode != 0:
        run_git(repo, "merge", "--abort")
        if original:
            run_git(repo, "checkout", original)
        return CheckResult(
            name="merge",
            status="blocked",
            data={
                "reason": "merge-conflict",
                "target": target,
                "error": (proc.stderr.strip() or proc.stdout.strip()) if proc else "",
                "action": "resolve on story branch, then retry",
            },
        )
    sha_proc = run_git(repo, "rev-parse", "--short", "HEAD")
    return CheckResult(
        name="merge",
        status="ok",
        data={
            "target": target,
            "sha": sha_proc.stdout.strip() if sha_proc else "",
        },
    )


def cleanup_branch(repo: Path, story_branch: str) -> CheckResult:
    """Delete the merged story branch (-d only — unmerged warns)."""
    proc = run_git(repo, "branch", "-d", story_branch)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="cleanup",
            status="warn",
            data={
                "branch": story_branch,
                "error": proc.stderr.strip() if proc else "git unavailable",
            },
        )
    return CheckResult(name="cleanup", status="ok", data={"deleted": story_branch})


def restore_worktree_branch(repo: Path, worktree_branch: str) -> CheckResult:
    """Checkout the worktree's dedicated branch after merging.

    Leaving the worktree on the dev branch blocks every other session
    from merging to it — restoration is non-optional when registered.
    """
    if not worktree_branch:
        return CheckResult(name="restore", status="ok", data={"skipped": True})
    proc = run_git(repo, "checkout", worktree_branch)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="restore",
            status="warn",
            data={
                "branch": worktree_branch,
                "error": proc.stderr.strip() if proc else "git unavailable",
            },
        )
    return CheckResult(name="restore", status="ok", data={"branch": worktree_branch})


def build_story_close_report(
    *,
    project_path: Path,
    cwd: Path,
    story_id: str,
    slug: str,
    jira_key: str,
    epic_dir: str,
    merge_summary: str,
    dev_branch: str = "",
    restore_branch: str = "",
) -> StoryCloseReport:
    """Run the full story-close sequence; skip everything after a block.

    ``restore_branch`` overrides the branch restored after the merge;
    by default the registered worktree branch (if any) is used. When the
    story merges to the worktree's own branch nothing is restored.
    """
    from raise_cli.story.open_service import resolve_dev_branch

    dev_branch = dev_branch or resolve_dev_branch(project_path)
    sid = story_id.lower()
    story_branch = f"story/{sid}/{slug}"

    release_preflight = _strict_release_preflight(project_path, dev_branch, jira_key)
    retro = check_retro(project_path, epic_dir, story_id)
    hygiene = check_hygiene(cwd)

    blocked = (
        release_preflight.status == "blocked"
        or retro.status == "blocked"
        or hygiene.status == "blocked"
    )

    target, tier = resolve_merge_target(
        project_path, cwd, story_id, dev_branch=dev_branch
    )

    merge = (
        _skipped("merge")
        if blocked
        else merge_story(
            cwd,
            story_branch,
            target,
            message=(f"Merge branch '{story_branch}' into {target}\n\n{merge_summary}"),
        )
    )
    if merge.status == "ok":
        merge.data["tier"] = tier
    blocked = blocked or merge.status == "blocked"

    cleanup = _skipped("cleanup") if blocked else cleanup_branch(cwd, story_branch)

    if not restore_branch and tier == "worktree":
        from raise_cli.storage.worktrees import (
            SqliteWorktreeStore,
            WorktreeNotFoundError,
        )

        try:
            wt = SqliteWorktreeStore(project_path).get_by_path(str(cwd))
            restore_branch = wt.branch if wt.branch != target else ""
        except WorktreeNotFoundError:
            restore_branch = ""
    restore = (
        _skipped("restore") if blocked else restore_worktree_branch(cwd, restore_branch)
    )

    backlog = (
        _skipped("backlog")
        if blocked
        else transition_backlog(project_path, jira_key, kind="done")
    )

    checks = (retro, hygiene, merge, cleanup, restore, backlog)
    worst = (
        "blocked"
        if release_preflight.status == "blocked"
        else max(checks, key=lambda c: STATUS_RANK[c.status]).status
    )
    return StoryCloseReport(
        status=worst,
        release_preflight=release_preflight,
        retro=retro,
        hygiene=hygiene,
        merge=merge,
        cleanup=cleanup,
        restore=restore,
        backlog=backlog,
    )
