"""Forward-merge hop preparation via ``git merge-tree`` (RAISE-17076 / S17066.4).

``prepare_hop`` computes one propagation hop's merge without ever checking
out the target: it writes exactly one local ref
(``refs/heads/forward-merge/{work_id}/{src_ver}-to-{tgt_ver}``) whose commit
has exactly two parents — the hop's base ref and the target line's tip — or,
on conflict, writes nothing and reports the conflicting paths (D2/D7). Re-
running after a conflict is resolved by hand reuses the existing branch
(D8/idempotent).
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

    # C1 fix: when the branch exists but target advanced (base is ancestor,
    # target is NOT), use the existing tip as merge base so the new commit
    # fast-forwards the pushed ref and preserves prior resolutions.
    actual_base, old_ref_sha = _resolve_merge_base(
        git, repo, branch, effective_base_ref, target_ref
    )

    return _write_hop(
        git,
        repo,
        branch=branch,
        actual_base=actual_base,
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
    effective_base_ref: str,
    target_ref: str,
    old_ref_sha: str | None,
    work_id: str,
    source: str,
    target: str,
) -> HopResult:
    merge_tree = git(
        repo,
        "merge-tree",
        "--write-tree",
        "--name-only",
        actual_base,
        target_ref,
    )
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
        )

    if merge_tree.returncode != 0:
        raise ScmCommandError(
            f"git merge-tree exited {merge_tree.returncode}: {merge_tree.stderr}"
        )

    tree_sha = merge_tree.stdout.strip().splitlines()[0]
    base_sha = _rev_parse(git, repo, actual_base)
    target_sha = _rev_parse(git, repo, target_ref)
    if base_sha is None or target_sha is None:
        raise ScmCommandError(f"could not resolve {actual_base!r} or {target_ref!r}")

    commit = git(
        repo,
        "commit-tree",
        tree_sha,
        "-p",
        base_sha,
        "-p",
        target_sha,
        "-m",
        f"forward-merge({work_id}): {source} -> {target}",
    )
    if commit is None or commit.returncode != 0:
        raise ScmCommandError("git commit-tree failed")
    merge_sha = commit.stdout.strip()

    update_ref_args = ["update-ref", f"refs/heads/{branch}", merge_sha]
    if old_ref_sha is not None:
        update_ref_args.append(old_ref_sha)
    update_ref = git(repo, *update_ref_args)
    if update_ref is None or update_ref.returncode != 0:
        raise ScmCommandError(f"git update-ref refs/heads/{branch} failed")

    return HopResult(
        status="prepared",
        branch=branch,
        base_ref=effective_base_ref,
        merge_sha=merge_sha,
        parents=[base_sha, target_sha],
        commits_ahead=_commits_ahead(git, repo, target_ref, effective_base_ref),
        conflicts=[],
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
    )


def _resolve_merge_base(
    git: GitRunner,
    repo: Path,
    branch: str,
    base_ref: str,
    target_ref: str,
) -> tuple[str, str | None]:
    """Return (actual_base_for_merge_tree, old_ref_sha_or_None).

    When the branch already exists and base_ref is an ancestor but
    target_ref is NOT, use the existing tip as merge base so the new
    commit fast-forwards the pushed ref (C1 fix).

    ``_hop_ref`` only ever returns the local ref (``prepare_hop`` fetches
    the branch via refspec into ``refs/heads/{branch}`` before this runs,
    RAISE-18004), so the returned old-ref sha is always safe to use as an
    ``update-ref`` compare-and-swap value.
    """
    ref = _hop_ref(git, repo, branch)
    if ref is None:
        return base_ref, None

    old_sha = _rev_parse(git, repo, ref)
    if old_sha is None:
        return base_ref, None

    base_anc = git(repo, "merge-base", "--is-ancestor", base_ref, ref)
    if base_anc is None or base_anc.returncode != 0:
        return base_ref, None

    target_anc = git(repo, "merge-base", "--is-ancestor", target_ref, ref)
    if target_anc is not None and target_anc.returncode == 0:
        return base_ref, old_sha

    return ref, old_sha


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
