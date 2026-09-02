"""Declarative merge-conflict auto-resolution (RAISE-16772).

Story/epic close rewrites governance artifacts (``items.json``, ``scope.md``)
directly on the target branch, so every open story branch hits the same
predictable conflicts at MR time. The resolution is always identical — take the
target — but it was done by hand. This module turns that tribal knowledge into
a reviewable policy file, ``.raise/conflict-resolution.yaml``.

Side semantics (design D3)
--------------------------
Strategies are defined relative to ``git merge origin/{target}`` executed **on
the source branch**::

    theirs = the target branch version
    ours   = the source branch version

They invert under ``git rebase``. Consumers of this module MUST merge, not
rebase. Both seeded patterns are ``theirs``: the target is authoritative
because the artifact is regenerated at the next close anyway.

Consumers: ``rai scm resolve-conflicts`` (used by ``rai-mr-create`` Step 2)
and, from S4 (RAISE-16774), ``rai-mr-merge``. Nothing here touches the
raise-server SCM proxy, so it survives S6's (RAISE-16777) removal of
``RaiseServerScmAdapter``.
"""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

CONFIG_RELATIVE_PATH = Path(".raise") / "conflict-resolution.yaml"

_GIT_TIMEOUT_S = 30

Strategy = Literal["theirs", "ours", "union"]

UnresolvedReason = Literal[
    "no_matching_rule",
    "union_not_implemented",
    "checkout_failed",
]


class ConflictResolutionError(Exception):
    """Base for every failure this module raises."""


class ConflictConfigError(ConflictResolutionError):
    """The policy file exists but cannot be trusted.

    Deliberately not silent: ignoring a malformed governance policy would
    quietly downgrade "resolve these conflicts automatically" to "resolve
    nothing", which looks like success (design D6).
    """


class GitStateError(ConflictResolutionError):
    """Git could not be queried at all — not a git repo, missing binary, timeout.

    Distinct from "no conflicts found", which is a legitimate empty report.
    Collapsing the two would make a broken environment read as success.
    """


class ConflictRule(BaseModel):
    """One glob → strategy mapping.

    ``reason`` is optional in the schema but expected in practice — it is what
    a reviewer reads to decide whether the automatic resolution is still
    correct a year from now.
    """

    model_config = ConfigDict(extra="forbid")

    pattern: str = Field(min_length=1)
    strategy: Strategy
    reason: str | None = None


class ConflictResolutionConfig(BaseModel):
    """Ordered ruleset. The first matching rule wins."""

    model_config = ConfigDict(extra="forbid")

    auto_resolve: list[ConflictRule] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Glob matching (design D5)
# ---------------------------------------------------------------------------


def _glob_to_regex(pattern: str) -> str:
    """Translate a gitignore-style glob into an anchored regex.

    Semantics::

        **/   zero or more directories
        **    anything, including separators
        *     anything except '/'
        ?     one character except '/'

    Why hand-rolled: ``fnmatch`` lets ``*`` cross ``/``, so
    ``work/epics/*/scope.md`` would silently match nested directories — far too
    loose for a file that authorises unattended conflict resolution.
    ``glob.translate`` and ``PurePath.full_match`` have the right semantics but
    are Python 3.13+, and this package's floor is 3.12.

    Bracket expressions (``[abc]``) are NOT supported; ``[`` is literal. No
    seeded pattern needs them, and a half-implemented character class in a
    governance policy is worse than an honestly literal one.
    """
    out: list[str] = []
    index = 0
    length = len(pattern)

    while index < length:
        char = pattern[index]
        if char == "*":
            star_end = index
            while star_end < length and pattern[star_end] == "*":
                star_end += 1
            if star_end - index >= 2:
                if star_end < length and pattern[star_end] == "/":
                    # 'a/**/b' must also match 'a/b' — '**' may span zero dirs.
                    out.append("(?:.*/)?")
                    star_end += 1
                else:
                    out.append(".*")
            else:
                out.append("[^/]*")
            index = star_end
        elif char == "?":
            out.append("[^/]")
            index += 1
        else:
            out.append(re.escape(char))
            index += 1

    return "".join(out)


@lru_cache(maxsize=256)
def _compiled(pattern: str) -> re.Pattern[str]:
    return re.compile(_glob_to_regex(pattern))


def matches(pattern: str, path: str) -> bool:
    """Return whether *path* (repo-relative, POSIX separators) matches *pattern*."""
    normalised = path.replace("\\", "/").removeprefix("./")
    return _compiled(pattern).fullmatch(normalised) is not None


def match_rule(path: str, config: ConflictResolutionConfig) -> ConflictRule | None:
    """Return the first rule matching *path*, or ``None``.

    First-match-wins so a narrow rule placed above a broad one overrides it,
    which is the only ordering users can reason about without reading code.
    """
    for rule in config.auto_resolve:
        if matches(rule.pattern, path):
            return rule
    return None


# ---------------------------------------------------------------------------
# Loading (design D6)
# ---------------------------------------------------------------------------


def _format_validation_error(path: Path, error: ValidationError) -> str:
    lines = [f"{path}: invalid conflict-resolution config"]
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"]) or "<root>"
        lines.append(f"  {location}: {detail['msg']} (got {detail.get('input')!r})")
    return "\n".join(lines)


def load_config(
    project_root: Path, *, config_path: Path | None = None
) -> ConflictResolutionConfig:
    """Load the policy file for *project_root*.

    A missing file is not an error — it yields an empty ruleset, so a project
    that has never needed auto-resolution runs the same code path as one that
    has (design D6). A file that exists but is malformed IS an error.

    Args:
        project_root: repository root; the file is read from
            ``{project_root}/.raise/conflict-resolution.yaml``.
        config_path: explicit override, for callers that do not have a
            conventional project root.

    Raises:
        ConflictConfigError: the file is unreadable, is not a YAML mapping, or
            violates the schema. The message names the offending entry.
    """
    path = (
        config_path if config_path is not None else project_root / CONFIG_RELATIVE_PATH
    )
    if not path.is_file():
        return ConflictResolutionConfig()

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConflictConfigError(f"{path}: malformed YAML — {exc}") from exc
    except OSError as exc:
        raise ConflictConfigError(f"{path}: cannot be read — {exc}") from exc

    if raw is None:
        return ConflictResolutionConfig()
    if not isinstance(raw, dict):
        raise ConflictConfigError(
            f"{path}: expected a mapping with an 'auto_resolve' key, "
            f"got {type(raw).__name__}"
        )

    try:
        return ConflictResolutionConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConflictConfigError(_format_validation_error(path, exc)) from exc


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


class ResolvedFile(BaseModel):
    """A conflict this module closed, and the rule that authorised it."""

    model_config = ConfigDict(frozen=True)

    path: str
    rule: ConflictRule


class UnresolvedFile(BaseModel):
    """A conflict left for the developer, and why it was left.

    The reason is not decoration: "no rule matched" is routine, while
    "checkout failed" means git refused an operation the policy expected to
    work, and the two warrant different reactions.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    reason: UnresolvedReason
    detail: str | None = None


class ResolutionReport(BaseModel):
    """Outcome of one resolution pass."""

    model_config = ConfigDict(frozen=True)

    resolved: list[ResolvedFile] = Field(default_factory=list)
    unresolved: list[UnresolvedFile] = Field(default_factory=list)
    dry_run: bool = False

    @property
    def all_resolved(self) -> bool:
        """True when nothing is left for a human — including the no-conflict case."""
        return not self.unresolved


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitStateError(
            f"git {' '.join(args)} failed in {repo_root}: {exc}"
        ) from exc


def conflicted_files(repo_root: Path) -> list[str]:
    """Repo-relative paths git currently considers unmerged.

    ``--diff-filter=U`` is the precise question. ``git status --short`` also
    reports untracked and staged files, which would have to be re-filtered by
    parsing two-letter status codes — more surface, same answer.
    """
    result = _git(repo_root, "diff", "--name-only", "--diff-filter=U")
    if result.returncode != 0:
        raise GitStateError(
            f"git diff --diff-filter=U failed in {repo_root} "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )
    return [line for line in result.stdout.splitlines() if line]


def resolve_conflicts(
    *,
    repo_root: Path,
    config: ConflictResolutionConfig,
    dry_run: bool = False,
) -> ResolutionReport:
    """Auto-resolve the conflicted files that a rule authorises.

    Assumes an in-progress ``git merge origin/{target}`` started on the source
    branch, which is what fixes the meaning of ``theirs``/``ours`` (design D3).
    Under a rebase the sides are swapped and every resolution would be exactly
    wrong, so callers must not rebase.

    Files with no matching rule are never touched — that is the whole point of
    a policy file rather than a blanket ``-X theirs``.

    Args:
        repo_root: working tree with the in-progress merge.
        config: the ruleset; an empty one resolves nothing.
        dry_run: report what would happen without touching the index.

    Returns:
        A report whose ``all_resolved`` is True only when nothing remains.

    Raises:
        GitStateError: git is unusable or *repo_root* is not a work tree.
    """
    resolved: list[ResolvedFile] = []
    unresolved: list[UnresolvedFile] = []

    for path in conflicted_files(repo_root):
        rule = match_rule(path, config)
        if rule is None:
            unresolved.append(UnresolvedFile(path=path, reason="no_matching_rule"))
            continue

        if rule.strategy == "union":
            # D4: schema-valid, deliberately unimplemented. Falling back to
            # another strategy here would corrupt the file while reporting
            # success, so it is reported as work left for a human.
            unresolved.append(
                UnresolvedFile(
                    path=path,
                    reason="union_not_implemented",
                    detail=(
                        f"strategy 'union' is not implemented — {path} is left "
                        "for manual resolution"
                    ),
                )
            )
            continue

        if dry_run:
            resolved.append(ResolvedFile(path=path, rule=rule))
            continue

        checkout = _git(repo_root, "checkout", f"--{rule.strategy}", "--", path)
        if checkout.returncode != 0:
            # Typically a modify/delete conflict: one side has no version of
            # the path to check out. Not exceptional — just not automatable.
            unresolved.append(
                UnresolvedFile(
                    path=path,
                    reason="checkout_failed",
                    detail=checkout.stderr.strip() or checkout.stdout.strip(),
                )
            )
            continue

        add = _git(repo_root, "add", "--", path)
        if add.returncode != 0:
            # An unstaged resolution still blocks the merge commit, so this
            # counts as unresolved rather than a silent partial success.
            unresolved.append(
                UnresolvedFile(
                    path=path,
                    reason="checkout_failed",
                    detail=add.stderr.strip() or add.stdout.strip(),
                )
            )
            continue

        resolved.append(ResolvedFile(path=path, rule=rule))

    return ResolutionReport(resolved=resolved, unresolved=unresolved, dry_run=dry_run)
