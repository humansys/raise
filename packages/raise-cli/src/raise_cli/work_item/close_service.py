"""Composite story-close service — S7884.3 (E7884 K1, ADR-093/ADR-024).

Ports the deterministic close sequence of the rai-story-close skill
(retro gate, hygiene, merge-target resolution, configurable merge strategy,
branch cleanup, worktree restoration, Done transition) into tested code.

Judgment stays with the LLM: AR checklist (P1-P3), epic-scope checkbox
edits and retro content are NOT absorbed here (design D3). Jidoka:
merge conflicts abort + block, a missing retro blocks, ambiguity in the
Done transition blocks with candidates.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel

from raise_cli.release_preflight import ReleasePreflightResult, run_release_preflight
from raise_cli.session.open_service import (
    STATUS_RANK,
    CheckResult,
    check_hygiene,
    run_git,
)
from raise_cli.telemetry.trailer import resolve_session_id, with_session_trailer
from raise_cli.work_item.open_service import normalize_story_id, transition_backlog

_MERGE_FLAGS: dict[str, str] = {
    "no-ff": "--no-ff",
    "ff-only": "--ff-only",
    "squash": "--squash",
}


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
    sid = normalize_story_id(story_id)
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


def _run_merge_strategy(
    repo: Path, story_branch: str, message: str, strategy_flag: str
) -> tuple[subprocess.CompletedProcess[str] | None, bool]:
    """Run the git merge command for *strategy_flag*.

    Returns ``(proc, squash_staged)`` — ``squash_staged`` is True once
    ``merge --squash`` lands rc=0 and the follow-up ``commit`` is attempted
    (needed by ``_merge_failure_reason`` to tell ``nothing-to-merge`` from a
    real ``merge-conflict``). It does *not* pick the cleanup strategy on
    failure — ``is_squash``, derived from *strategy_flag*, does (RAISE-17692).
    """
    if strategy_flag == "--ff-only":
        return run_git(repo, "merge", story_branch, "--ff-only"), False
    if strategy_flag == "--squash":
        proc = run_git(repo, "merge", story_branch, "--squash")
        if proc is not None and proc.returncode == 0:
            return run_git(repo, "commit", "-m", message), True
        return proc, False
    return run_git(repo, "merge", story_branch, "--no-ff", "-m", message), False


def _merge_failure_reason(repo: Path, squash_staged: bool) -> str:
    """RAISE-17641: an already-merged squash retry is not a real conflict.

    ``git diff --cached --quiet`` must run before any reset — rc=0 (nothing
    staged) proves the commit failed because there was nothing to land, not
    because content collided.
    """
    if not squash_staged:
        return "merge-conflict"
    diff_proc = run_git(repo, "diff", "--cached", "--quiet")
    if diff_proc is not None and diff_proc.returncode == 0:
        return "nothing-to-merge"
    return "merge-conflict"


def _merge_blocked_result(
    repo: Path,
    proc: subprocess.CompletedProcess[str] | None,
    squash_staged: bool,
    original: str,
    target: str,
    *,
    is_squash: bool = False,
) -> CheckResult:
    """Build the blocked CheckResult for a failed merge attempt, then clean up.

    ``squash_staged`` (only true when the initial ``merge --squash`` landed
    rc=0 and the follow-up ``commit`` then failed) drives the reason label
    via ``_merge_failure_reason``. ``is_squash`` drives the *cleanup*
    strategy below and is a distinct signal: the far more common squash
    failure is a conflict in the initial ``merge --squash`` step itself,
    which leaves ``squash_staged=False`` — so cleanup cannot key off
    ``squash_staged`` without missing that case (RAISE-17692).
    """
    reason = _merge_failure_reason(repo, squash_staged)
    if is_squash:
        # RAISE-17692: `git merge --squash` never writes MERGE_HEAD — not
        # when the merge step itself conflicts (squash_staged=False, the
        # common case) nor when it staged cleanly and only the follow-up
        # `commit` failed (squash_staged=True, nothing-to-merge). Either
        # way, `git merge --abort` has nothing to track and fails with
        # "there is no merge to abort" — it is skipped here rather than
        # called as a documented no-op. A plain `reset HEAD` only unstages
        # the index — it leaves conflict markers in the working tree,
        # which then makes the `checkout(original)` below fail on a dirty
        # tree and strands the developer on `target` mid-conflict.
        # `reset --merge HEAD` clears exactly the unmerged/conflicted
        # paths back to HEAD (unblocking the checkout) while leaving any
        # *unrelated* dirty file untouched — the same preservation
        # `merge --abort` gives the non-squash branch below. `reset --hard`
        # would also clear the conflict, but it wipes the entire working
        # tree, silently destroying unrelated uncommitted edits that were
        # never part of the merge — squash has no MERGE_HEAD, not no
        # working-tree state worth preserving.
        run_git(repo, "reset", "--merge", "HEAD")
    else:
        run_git(repo, "merge", "--abort")
    if original:
        run_git(repo, "checkout", original)
    return CheckResult(
        name="merge",
        status="blocked",
        data={
            "reason": reason,
            "target": target,
            "error": (proc.stderr.strip() or proc.stdout.strip()) if proc else "",
            "action": (
                "already landed; nothing further to merge"
                if reason == "nothing-to-merge"
                else "resolve on story branch, then retry"
            ),
        },
    )


def merge_story(
    repo: Path,
    story_branch: str,
    target: str,
    *,
    message: str,
    merge_strategy: str = "no-ff",
) -> CheckResult:
    """Merge the story branch into *target* using the configured merge strategy.

    ``merge_strategy`` controls the git flag: "no-ff" (default, backward-
    compatible), "ff-only", or "squash". Unknown values fall back to "--no-ff".
    Conflicts abort the merge and restore the original branch (jidoka):
    the repo is never left mid-merge.
    """
    if story_branch == target:
        # RAISE-17641: defense in depth alongside the RAISE-17504 report-level
        # guard in build_story_close_report — `git merge X` while already on
        # `X` returns rc=0 ("Already up to date") and trivially satisfies
        # ancestry, so this is the only check that catches a self-merge here.
        return CheckResult(
            name="merge",
            status="blocked",
            data={"reason": "target-equals-source", "target": target},
        )

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
    strategy_flag = _MERGE_FLAGS.get(merge_strategy, "--no-ff")

    pre_merge_proc = run_git(repo, "rev-parse", "--short", "HEAD")
    pre_merge_sha = pre_merge_proc.stdout.strip() if pre_merge_proc else ""

    proc, squash_staged = _run_merge_strategy(
        repo, story_branch, message, strategy_flag
    )

    if proc is None or proc.returncode != 0:
        return _merge_blocked_result(
            repo,
            proc,
            squash_staged,
            original,
            target,
            is_squash=strategy_flag == "--squash",
        )

    # RAISE-17641: rc=0 alone is not proof the source landed in target's
    # history — for no-ff/ff-only, assert ancestry (motion-agnostic: an
    # already-merged branch has HEAD not moving, which is a true positive,
    # not a failure). Squash has no merge parent, so ancestry is
    # structurally unavailable and HEAD-advanced remains its postcondition.
    if strategy_flag != "--squash":
        ancestry_proc = run_git(
            repo, "merge-base", "--is-ancestor", story_branch, target
        )
        if ancestry_proc is None or ancestry_proc.returncode != 0:
            if original:
                run_git(repo, "checkout", original)
            return CheckResult(
                name="merge",
                status="blocked",
                data={
                    "reason": "merge-not-landed",
                    "target": target,
                    "error": (
                        ancestry_proc.stderr.strip()
                        if ancestry_proc
                        else "git unavailable"
                    ),
                },
            )

    sha_proc = run_git(repo, "rev-parse", "--short", "HEAD")
    sha = sha_proc.stdout.strip() if sha_proc else ""
    noop = strategy_flag != "--squash" and sha == pre_merge_sha
    return CheckResult(
        name="merge",
        status="ok",
        data={"target": target, "sha": sha, **({"noop": True} if noop else {})},
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
    from raise_cli.project_config import resolve_dev_branch
    from raise_cli.project_config.branches import resolve_merge_strategy

    dev_branch = dev_branch or resolve_dev_branch(project_path)
    effective_merge_strategy = resolve_merge_strategy(project_path) or "no-ff"
    sid = normalize_story_id(story_id)
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

    # RAISE-17504: target must never equal the story branch — a self-merge is a
    # silent no-op that git reports as success but moves no work to the target.
    if not blocked and target == story_branch:
        blocked_merge = CheckResult(
            name="merge",
            status="blocked",
            data={
                "reason": "target-equals-source",
                "target": target,
                "tier": tier,
                "action": (
                    "The resolved merge target equals the story branch itself. "
                    "Re-register the worktree with its own dedicated branch "
                    "(not the story branch) via `rai worktree register`, or "
                    "create an epic branch so the resolver picks a real target."
                ),
            },
        )
        return StoryCloseReport(
            status="blocked",
            release_preflight=release_preflight,
            retro=retro,
            hygiene=hygiene,
            merge=blocked_merge,
            cleanup=_skipped("cleanup"),
            restore=_skipped("restore"),
            backlog=_skipped("backlog"),
        )

    # RAISE-16268: dev-branch fallback must never silently merge to main.
    # When the resolver falls to tier=dev and returns a branch equal to
    # branches.main, refuse immediately — the worktree is unregistered and
    # merging to main directly would bypass all PR/MR governance.
    if not blocked and tier == "dev":
        try:
            from raise_cli.project_config.manifest import load_manifest

            manifest = load_manifest(project_path)
            main_branch = manifest.branches.main if manifest is not None else "main"
        except Exception:  # noqa: BLE001 — defensive; prefer safe block over crash
            main_branch = "main"
        if target == main_branch:
            blocked_merge = CheckResult(
                name="merge",
                status="blocked",
                data={
                    "reason": "dev-fallback-resolves-to-main",
                    "target": target,
                    "main": main_branch,
                    "tier": tier,
                    "action": (
                        "Register the worktree via story-open (/rai-story-start)"
                        " or create an epic branch so the dev-branch fallback"
                        f" resolves to a branch other than {main_branch!r}."
                    ),
                },
            )
            return StoryCloseReport(
                status="blocked",
                release_preflight=release_preflight,
                retro=retro,
                hygiene=hygiene,
                merge=blocked_merge,
                cleanup=_skipped("cleanup"),
                restore=_skipped("restore"),
                backlog=_skipped("backlog"),
            )

    merge = (
        _skipped("merge")
        if blocked
        else merge_story(
            cwd,
            story_branch,
            target,
            message=(f"Merge branch '{story_branch}' into {target}\n\n{merge_summary}"),
            merge_strategy=effective_merge_strategy,
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
