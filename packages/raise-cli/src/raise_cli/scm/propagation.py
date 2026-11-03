"""Forward-merge hop preparation via ``git merge-tree`` (RAISE-17076 / S17066.4).

``prepare_hop`` computes one propagation hop's merge without ever checking
out the target: it writes exactly one local ref
(``refs/heads/forward-merge/{work_id}/{src_ver}-to-{tgt_ver}``) whose commit
has exactly two parents — the hop's base ref and the target line's tip (or,
when resuming a human-resolved branch whose lines advanced, the existing tip
and the tip(s) it lacks) — or, on conflict, writes nothing and reports the conflicting paths (D2/D7). Re-
running after a conflict is resolved by hand reuses the existing branch
(D8/idempotent). If the source and/or target line advanced after that
resolution, only the missing tip(s) are merged into the existing branch tip
(sequentially when both advanced), so the human resolution is kept and the
ref fast-forwards; a conflict arises only if the new delta itself conflicts.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel

from raise_cli.exceptions import ConfigurationError
from raise_cli.project_config.branches import propagation_branch
from raise_cli.scm.adapter import ScmCommandError
from raise_cli.session.open_service import run_git

_ZERO_OID = "0" * 40
_FETCH_TIMEOUT_S = 90
_MIN_GIT_VERSION = (2, 38)
_GIT_VERSION_RE = re.compile(r"(\d+)\.(\d+)")


class GitRunner(Protocol):
    """Matches ``raise_cli.session.open_service.run_git``'s call shape.

    Injectable so tests can simulate a below-minimum git version or a
    failing/timed-out git invocation without depending on the host's
    actual git binary for those two cases.
    """

    def __call__(
        self, repo: Path, *args: str, timeout: float = ...
    ) -> subprocess.CompletedProcess[str] | None:
        """Run git in *repo*; ``None`` on OS error/timeout."""
        ...


class HopResult(BaseModel):
    """Outcome of preparing one forward-merge hop."""

    status: Literal["prepared", "existing", "conflict"]
    branch: str
    base_ref: str
    merge_sha: str | None
    parents: list[str]
    commits_ahead: int
    conflicts: list[str]
    resumed: bool = False  # built on an existing hop ref (D8 resume)


def prepare_hop(
    repo: Path,
    *,
    source: str,
    target: str,
    work_id: str,
    base_ref: str | None = None,
    git: GitRunner = run_git,
) -> HopResult:
    """Prepare (or reuse) the local ref for one ``source`` -> ``target`` hop.

    Never checks out or mutates the caller's working tree or index. Fetches
    ``source``/``target`` from ``origin``, then either reuses an existing
    ``forward-merge/...`` branch (D8) or computes the merge via
    ``git merge-tree --write-tree`` (D2): a clean result is committed and
    written to a new ref (``status="prepared"``); a conflicting result
    writes no ref (``status="conflict"``, D7).

    Raises:
        ConfigurationError: git is older than 2.38 (``merge-tree
            --write-tree`` requires it).
        ScmCommandError: any git invocation fails, times out, or returns
            unparseable output.
    """
    version = _git_version(git, repo)
    if version is None or version < _MIN_GIT_VERSION:
        detected = "unknown" if version is None else ".".join(str(p) for p in version)
        raise ConfigurationError(
            "forward-merge requires git >= 2.38 (git merge-tree --write-tree); "
            f"detected {detected}",
        )

    branch = propagation_branch(work_id, source, target)
    effective_base_ref = base_ref or f"origin/{source}"

    fetch = git(repo, "fetch", "origin", source, target, timeout=_FETCH_TIMEOUT_S)
    if fetch is None or fetch.returncode != 0:
        raise ScmCommandError(f"git fetch origin {source} {target} failed")

    # Best-effort: fetch the propagation branch itself via an explicit
    # refspec so a fresh clone (CI) discovers AND materializes as a real
    # local ref a branch already prepared/resolved and pushed by a prior
    # run (D8) — not just as a remote-tracking ref (RAISE-18004: the
    # downstream forward-merge contract hard-requires refs/heads/{branch}).
    # No `+` force-prefix: a diverged local human resolution is preserved
    # (the fetch simply fails, non-fatal), and a branch checked out in
    # another worktree is safely refused (also non-fatal). On a hop's
    # first run the branch does not exist on origin yet — that failure is
    # the expected common case.
    git(
        repo,
        "fetch",
        "origin",
        f"refs/heads/{branch}:refs/heads/{branch}",
        timeout=_FETCH_TIMEOUT_S,
    )

    target_ref = f"origin/{target}"

    existing = _existing_hop(git, repo, branch, effective_base_ref, target_ref)
    if existing is not None:
        return existing

    # D8 resume: when the branch exists, merge only the tip(s) it lacks INTO
    # the existing tip so prior (human) resolutions survive and the pushed
    # ref fast-forwards (C1 = target advanced; RAISE-19360 = source advanced).
    actual_base, old_ref_sha, merge_refs, resumed = _resolve_merge_base(
        git, repo, branch, effective_base_ref, target_ref
    )

    return _write_hop(
        git,
        repo,
        branch=branch,
        actual_base=actual_base,
        merge_refs=merge_refs,
        resumed=resumed,
        effective_base_ref=effective_base_ref,
        target_ref=target_ref,
        old_ref_sha=old_ref_sha,
        work_id=work_id,
        source=source,
        target=target,
    )


def _write_hop(
    git: GitRunner,
    repo: Path,
    *,
    branch: str,
    actual_base: str,
    merge_refs: list[str],
    resumed: bool,
    effective_base_ref: str,
    target_ref: str,
    old_ref_sha: str | None,
    work_id: str,
    source: str,
    target: str,
) -> HopResult:
    """Merge each of *merge_refs* into *actual_base* in order; update the ref last.

    Intermediate merge commits are computed in memory (unreferenced objects);
    a conflict at any step writes no ref.
    """
    message = f"forward-merge({work_id}): {source} -> {target}"
    left = actual_base
    parents: list[str] = []
    merge_sha = ""
    for right in merge_refs:
        merge_tree = git(repo, "merge-tree", "--write-tree", "--name-only", left, right)
        if merge_tree is None:
            raise ScmCommandError("git merge-tree did not run")

        if merge_tree.returncode == 1:
            return HopResult(
                status="conflict",
                branch=branch,
                base_ref=effective_base_ref,
                merge_sha=None,
                parents=[],
                commits_ahead=_commits_ahead(git, repo, target_ref, effective_base_ref),
                conflicts=_parse_conflicts(merge_tree.stdout),
                resumed=resumed,
            )

        if merge_tree.returncode != 0:
            raise ScmCommandError(
                f"git merge-tree exited {merge_tree.returncode}: {merge_tree.stderr}"
            )

        tree_sha = merge_tree.stdout.strip().splitlines()[0]
        left_sha = _rev_parse(git, repo, left)
        right_sha = _rev_parse(git, repo, right)
        if left_sha is None or right_sha is None:
            raise ScmCommandError(f"could not resolve {left!r} or {right!r}")

        commit = git(
            repo,
            "commit-tree",
            tree_sha,
            "-p",
            left_sha,
            "-p",
            right_sha,
            "-m",
            message,
        )
        if commit is None or commit.returncode != 0:
            raise ScmCommandError("git commit-tree failed")
        merge_sha = commit.stdout.strip()
        parents = [left_sha, right_sha]
        left = merge_sha

    _assert_not_checked_out(git, repo, branch)
    # CAS: the zero OID means "ref must not exist yet" (no clobbering a ref
    # created concurrently).
    update_ref = git(
        repo,
        "update-ref",
        f"refs/heads/{branch}",
        merge_sha,
        old_ref_sha or _ZERO_OID,
    )
    if update_ref is None or update_ref.returncode != 0:
        raise ScmCommandError(f"git update-ref refs/heads/{branch} failed")

    return HopResult(
        status="prepared",
        branch=branch,
        base_ref=effective_base_ref,
        merge_sha=merge_sha,
        parents=parents,
        commits_ahead=_commits_ahead(git, repo, target_ref, effective_base_ref),
        conflicts=[],
        resumed=resumed,
    )


def _assert_not_checked_out(git: GitRunner, repo: Path, branch: str) -> None:
    """Refuse to move a branch that is checked out in any worktree."""
    proc = git(repo, "worktree", "list", "--porcelain")
    if proc is None or proc.returncode != 0:
        return
    path = ""
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree ") :]
        elif line == f"branch refs/heads/{branch}":
            raise ScmCommandError(
                f"forward-merge branch {branch} is checked out in worktree "
                f"{path}; update it there (git merge origin/<line>) or remove "
                "the worktree"
            )


def _git_version(git: GitRunner, repo: Path) -> tuple[int, int] | None:
    proc = git(repo, "--version")
    if proc is None or proc.returncode != 0:
        return None
    match = _GIT_VERSION_RE.search(proc.stdout)
    if match is None:
        return None
    return (int(match.group(1)), int(match.group(2)))


def _hop_ref(git: GitRunner, repo: Path, branch: str) -> str | None:
    """Return `refs/heads/{branch}` if it exists locally, else None.

    ``prepare_hop`` fetches the propagation branch via an explicit refspec
    (`refs/heads/{branch}:refs/heads/{branch}`) before this is called, so a
    branch already pushed by a prior run (CI or manual) is materialized as
    a real local ref before discovery runs (RAISE-18004) — no
    remote-tracking-ref fallback is needed here. On a hop's first run, or
    when origin has no such branch yet, no local ref exists and this
    returns None.
    """
    ref = f"refs/heads/{branch}"
    show_ref = git(repo, "show-ref", "--verify", "--quiet", ref)
    if show_ref is not None and show_ref.returncode == 0:
        return ref
    return None


def _existing_hop(
    git: GitRunner, repo: Path, branch: str, base_ref: str, target_ref: str
) -> HopResult | None:
    ref = _hop_ref(git, repo, branch)
    if ref is None:
        return None
    base_ancestor = git(repo, "merge-base", "--is-ancestor", base_ref, ref)
    if base_ancestor is None or base_ancestor.returncode != 0:
        return None
    target_ancestor = git(repo, "merge-base", "--is-ancestor", target_ref, ref)
    if target_ancestor is None or target_ancestor.returncode != 0:
        return None

    merge_sha = _rev_parse(git, repo, ref)
    parents = _commit_parents(git, repo, merge_sha) if merge_sha else []
    return HopResult(
        status="existing",
        branch=branch,
        base_ref=base_ref,
        merge_sha=merge_sha,
        parents=parents,
        commits_ahead=_commits_ahead(git, repo, target_ref, base_ref),
        conflicts=[],
        resumed=True,
    )


def _resolve_merge_base(
    git: GitRunner,
    repo: Path,
    branch: str,
    base_ref: str,
    target_ref: str,
) -> tuple[str, str | None, list[str], bool]:
    """Return (merge_left, old_ref_sha_or_None, refs_to_merge, resumed).

    D8 resume. With an existing branch that carries a resolution (at least
    one merge commit not already in the base or target line) the existing
    tip is the left side and only the tips it lacks are merged into it, so
    the resolution is preserved and the ref fast-forwards:

    - target missing (target advanced, C1): ``[target]``.
    - base missing (source advanced, RAISE-19360): ``[base]``.
    - both missing: ``[base, target]``, merged sequentially.

    Otherwise (no branch, or a stale branch already contained in the base
    or target line) fall back to a from-scratch merge of target into base;
    an existing ref's sha is still the ``update-ref`` compare-and-swap value.

    MR !2086: an existing ref is never replaced by a non-descendant. A
    branch with own commits but no resolution merge (F1), or whose first
    own merge does not join base and target (F2), raises; so does any
    failed provenance inspection.
    """
    ref = _hop_ref(git, repo, branch)
    if ref is None:
        return base_ref, None, [target_ref], False

    old_sha = _rev_parse(git, repo, ref)
    if old_sha is None:
        return base_ref, None, [target_ref], False

    own_merges = git(
        repo, "rev-list", "--merges", "--reverse", ref, "--not", base_ref, target_ref
    )
    if own_merges is None or own_merges.returncode != 0:
        raise ScmCommandError(f"could not inspect provenance of {branch!r}")
    merge_shas = own_merges.stdout.split()
    if not merge_shas:
        # No resolution: a from-scratch rebuild is only safe when it keeps
        # the existing tip (MR !2086 F1, never drop descendant commits).
        if _is_ancestor(git, repo, old_sha, base_ref) or _is_ancestor(
            git, repo, old_sha, target_ref
        ):
            return base_ref, old_sha, [target_ref], False
        raise ScmCommandError(
            f"refusing to replace {branch!r}: it has commits outside "
            f"{base_ref} and {target_ref} and no resolution merge"
        )
    # The root resolution must join the base and target lines (MR !2086 F2).
    parents = _commit_parents(git, repo, merge_shas[0])
    if len(parents) != 2 or not (
        (
            _is_ancestor(git, repo, parents[0], base_ref)
            and _is_ancestor(git, repo, parents[1], target_ref)
        )
        or (
            _is_ancestor(git, repo, parents[0], target_ref)
            and _is_ancestor(git, repo, parents[1], base_ref)
        )
    ):
        raise ScmCommandError(
            f"refusing to resume {branch!r}: its first own merge does not join "
            f"{base_ref} and {target_ref}"
        )

    has_base = _is_ancestor(git, repo, base_ref, ref)
    has_target = _is_ancestor(git, repo, target_ref, ref)

    if has_base and has_target:
        # Already handled by _existing_hop; never rebuild over a resolution.
        raise ScmCommandError(f"refusing to rebuild up-to-date {branch!r}")
    if has_base:
        return ref, old_sha, [target_ref], True
    if has_target:
        return ref, old_sha, [base_ref], True
    return ref, old_sha, [base_ref, target_ref], True


def _is_ancestor(git: GitRunner, repo: Path, ancestor: str, ref: str) -> bool:
    """True if *ancestor* is in *ref*'s history; git errors raise."""
    proc = git(repo, "merge-base", "--is-ancestor", ancestor, ref)
    if proc is None or proc.returncode not in (0, 1):
        raise ScmCommandError(f"git merge-base --is-ancestor {ancestor} {ref} failed")
    return proc.returncode == 0


def _rev_parse(git: GitRunner, repo: Path, ref: str) -> str | None:
    proc = git(repo, "rev-parse", ref)
    if proc is None or proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _commit_parents(git: GitRunner, repo: Path, sha: str) -> list[str]:
    proc = git(repo, "log", "-1", "--format=%P", sha)
    if proc is None or proc.returncode != 0:
        return []
    return proc.stdout.split()


def _commits_ahead(git: GitRunner, repo: Path, base_ref: str, target_ref: str) -> int:
    proc = git(repo, "rev-list", "--count", f"{base_ref}..{target_ref}")
    if proc is None or proc.returncode != 0:
        return 0
    try:
        return int(proc.stdout.strip())
    except ValueError:
        return 0


def _parse_conflicts(stdout: str) -> list[str]:
    first_block = stdout.split("\n\n", 1)[0]
    lines = [line.strip() for line in first_block.splitlines() if line.strip()]
    return lines[1:]  # first line is the (unusable) conflicted tree OID
