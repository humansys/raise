"""GovernanceTrailCiGate — CI backstop for the governance trail (RAISE-15132).

``GovernanceArtifactsGate`` (``gates/governance/artifacts_gate.py``) is the
agent-side gate: it derives context from the git *branch name* at
``before:story:implement`` and honors an escape-hatch environment variable —
a bypass the agent it is meant to constrain can set itself. That gate also
cannot run meaningfully in CI: GitLab MR pipelines check out a detached
HEAD, so ``git rev-parse --abbrev-ref HEAD`` returns the literal string
``HEAD`` and the branch-name regexes never match (story design D1).

This gate is the layer the agent does not control. It derives its own commit
range from git alone — no branch name, no Jira key — and classifies every
path in that range into **trail** / **exempt** / **substantive** (D3).
Whenever the range contains a substantive path, at least one trail artifact
(a ``scope.md``, story- or epic-shaped) must also be in the range, or the
gate fails loudly.

``context.changed_files`` is deliberately NOT read (D4): the range is
derived internally via ``resolve_dev_branch`` + ``resolve_merge_base`` so the
verdict is identical whether the gate is invoked by id, by ``--point``, or by
``--all`` — ``run_gate``/``run_all_gates`` populate ``changed_files``
differently, and a backstop whose answer depends on how it was invoked is
not a backstop.

No suppression mechanism exists (D2/AC4/AC12) — the only "escape" is the
path-derived exempt bucket, itself visible in the MR diff. There is no
bypass beyond the CI-supplied base ref: ``resolve_dev_branch`` honors
``RAISE_DEVELOPMENT_BRANCH`` (R5, quality-review, RAISE-15878), which does
change which ref the range is computed against — but that variable is
deliberately CI-supplied pipeline config (the GitLab MR target branch), not
something the agent this gate constrains sets on itself, unlike the
escape-hatch env var on ``GovernanceArtifactsGate`` above. An unresolvable
base ref degrades to an honest, loudly-labeled skip (D7) rather than a false
block or a silent pass.

Architecture: work/epics/e15853-rc2-governance-modeling/stories/s15853.3-design.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import ClassVar

from raise_cli.core.tools import git_root
from raise_cli.exceptions import DependencyError
from raise_cli.gates.drift._delta import read_at_ref, resolve_merge_base
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.impact.git_diff import GitDiffError, collect_changed_files
from raise_cli.project_config import resolve_dev_branch

# D3 — trail bucket: anything under work/ whose filename is scope.md or ends
# -scope.md. Covers epic (work/epics/e*/scope.md), story
# (work/epics/**/sN.M-scope.md) and bug (work/bugs/<KEY>/scope.md) shapes
# with one rule.
_TRAIL_DIR_PREFIX = "work/"

# D3 — exempt bucket: docs/config surfaces that never carry behavior. Order
# matters relative to the trail check only — trail is checked first so a
# work/**/scope.md is never misclassified as merely "under work/".
_EXEMPT_EXACT: frozenset[str] = frozenset(
    {
        "CLAUDE.md",
        "AGENTS.md",
        "README.md",
        ".gitlab-ci.yml",
        ".gitignore",
        ".pre-commit-config.yaml",
        "uv.lock",
    }
)
_EXEMPT_PREFIXES: tuple[str, ...] = (
    ".github/",
    "dev/",
    "docs/",
    "work/",
    "governance/",
    # R1 (quality-review, RAISE-15878): NOT a blanket ".raise/" — that
    # swallowed skill bodies (.raise/skills/**/SKILL.md) and gate
    # definitions (.raise/gates/*.md), which are behavior, not docs (D3,
    # same rule already applied to .claude/skills/**). Cartridges are
    # declarative extraction config end to end (CARTRIDGE.yaml + schemas),
    # so the whole subtree is exempt.
    ".raise/cartridges/",
)


def _is_trail(path: str) -> bool:
    if not path.startswith(_TRAIL_DIR_PREFIX):
        return False
    name = PurePosixPath(path).name
    return name == "scope.md" or name.endswith("-scope.md")


def _is_raise_top_level_config(path: str) -> bool:
    """``.raise/*.yaml`` only — declarative instance config.

    Covers ``cockpit.yaml``, ``jira.yaml``, ``docs.yaml``. Deliberately
    not recursive: nested dirs like ``.raise/skills/`` or ``.raise/gates/``
    carry behavior (R1).
    """
    parent, _, name = path.rpartition("/")
    return parent == ".raise" and name.endswith(".yaml")


def _is_exempt(path: str) -> bool:
    if path in _EXEMPT_EXACT:
        return True
    if path.startswith(_EXEMPT_PREFIXES):
        return True
    return _is_raise_top_level_config(path)


@dataclass(frozen=True)
class TrailClassification:
    """Partition of a commit range's paths — total over the input (D8)."""

    trail: tuple[str, ...]
    substantive: tuple[str, ...]
    exempt: tuple[str, ...]

    @property
    def requires_trail(self) -> bool:
        """True when any substantive path is present — a trail is required."""
        return bool(self.substantive)


def classify_paths(paths: tuple[str, ...]) -> TrailClassification:
    """Pure: repo-relative POSIX paths -> three-bucket partition (D3/D8).

    Trail is checked before exempt so a ``work/**/scope.md`` is classified
    as trail, not merely as "under work/" (which is otherwise exempt).
    """
    trail: list[str] = []
    substantive: list[str] = []
    exempt: list[str] = []
    for path in paths:
        if _is_trail(path):
            trail.append(path)
        elif _is_exempt(path):
            exempt.append(path)
        else:
            substantive.append(path)
    return TrailClassification(
        trail=tuple(trail), substantive=tuple(substantive), exempt=tuple(exempt)
    )


_EXPECTED_HINT = (
    "work/epics/**/*-scope.md, work/epics/*/scope.md, or work/bugs/<KEY>/scope.md"
)


class GovernanceTrailCiGate:
    """Fail-closed CI backstop: substantive changes require a committed trail.

    Registered via the ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "governance-trail-ci"
    description: ClassVar[str] = (
        "Commit range carries a governance scope artifact (RAISE-15132)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Derive the MR range, classify its paths, require a trail (D4).

        ``context.changed_files`` is deliberately NOT read — the verdict must
        be identical whether invoked by id, by ``--point``, or by ``--all``.

        C3 (quality-review, RAISE-15878): every git-touching call in this
        method must receive the *resolved repo root*, never
        ``context.working_dir`` directly. ``context.working_dir`` is a raw
        ``Path.cwd()`` (never resolved — ``gates/models.py``,
        ``cli/commands/gate.py``); C2 already fixed one cwd-dependent call
        (``read_at_ref``) but ``resolve_dev_branch`` — which locates
        ``.raise/manifest.yaml`` directly under the path it is given, with
        no upward search — silently fell back to ``"main"`` when invoked
        from a subdirectory, producing a false PASS on a fail-closed
        backstop (worse than C2's false-fail). Resolving the root once here
        and threading it through every call closes the whole defect class
        instead of patching call sites one at a time.
        """
        try:
            repo_root = git_root(context.working_dir)
        except DependencyError:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="⚠ SKIPPED (cannot evaluate): not inside a git checkout",
            )

        dev_branch = resolve_dev_branch(repo_root)
        merge_base = resolve_merge_base(dev_branch, repo_root)
        if merge_base is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"⚠ SKIPPED (cannot evaluate): base ref '{dev_branch}' "
                    "unresolvable in this checkout"
                ),
            )

        try:
            changed = collect_changed_files(merge_base, "HEAD", repo_root)
        except GitDiffError:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"⚠ SKIPPED (cannot evaluate): could not diff base ref "
                    f"'{dev_branch}' against HEAD"
                ),
            )

        classification = classify_paths(tuple(path.as_posix() for path in changed))
        range_line = f"range: {merge_base[:8]}..HEAD (base: {dev_branch})"

        # C1 (quality-review, RAISE-15878): `collect_changed_files` runs a
        # plain `git diff --name-only` with no `--diff-filter`, so a deleted
        # scope.md is still in `classification.trail` — the path pattern
        # matched, but the file no longer exists. Without this check a
        # `git rm work/**/scope.md` on an unrelated stale trail would
        # satisfy "trail present" for substantive changes riding along in
        # the same range, defeating the backstop (AC2, AC12). Only a trail
        # path that still exists at HEAD counts as an actual trail. The
        # substantive bucket is untouched — deletions there must keep
        # failing closed.
        #
        # C2 (quality-review, RAISE-15878): the first cut of this check used
        # `(context.working_dir / path).is_file()` — but `path` is always
        # repo-root-relative (that's what `git diff --name-only` emits,
        # regardless of cwd — see `collect_changed_files`), while
        # `context.working_dir` is a raw `Path.cwd()` never resolved to the
        # repo root (`gates/models.py`, `cli/commands/gate.py`). Invoked from
        # any subdirectory, every trail path resolved against the wrong
        # base and `is_file()` always came back False — a real trail read as
        # missing, purely because of *where* the gate ran (D4: "a backstop
        # whose answer depends on how it was invoked is not a backstop").
        # `git cat-file`-via-`read_at_ref` is cwd-independent (git always
        # resolves `ref:path` against the repo root) and, as a side effect,
        # only ever looks at the committed tree at HEAD — never the working
        # tree's dirty/untracked state (closes R3 too, same reviewer pass).
        live_trail = tuple(
            path
            for path in classification.trail
            if read_at_ref("HEAD", path, repo_root) is not None
        )

        if not classification.requires_trail:
            # R2 (quality-review): a trail-only range (e.g. the first commit
            # of a story, which is only scope.md) must not be reported as
            # "empty" — it did carry a governance artifact, just no
            # substantive code yet. Checked ahead of the exempt branch so a
            # trail file alongside exempt files is still reported honestly.
            if live_trail:
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message="trail present, no substantive changes yet",
                    details=(range_line, f"trail: {live_trail[0]}"),
                )
            if classification.trail:
                # O1 (quality-review, RAISE-15878): a range that only
                # *deletes* trail file(s) (no other changes) has a non-empty
                # `classification.trail` but an empty `live_trail` — reusing
                # the generic "empty range" message below would be
                # misleading, since something WAS in the range. Narrower
                # instance of R2's honesty fix, checked before the exempt
                # branch for the same reason.
                deleted_list = ", ".join(classification.trail)
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message="trail path(s) removed — no substantive changes",
                    details=(
                        range_line,
                        f"{len(classification.trail)} trail path(s) removed: "
                        f"{deleted_list}",
                    ),
                )
            if classification.exempt:
                exempt_list = ", ".join(classification.exempt)
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message="infra-only range — trail not required",
                    details=(
                        range_line,
                        f"{len(classification.exempt)} exempt path(s): {exempt_list}",
                    ),
                )
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="empty range — trail not required",
                details=(range_line,),
            )

        if live_trail:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="governance trail present",
                details=(range_line, f"trail: {live_trail[0]}"),
            )

        substantive = classification.substantive
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="no governance trail artifact in commit range",
            details=(
                range_line,
                f"{len(substantive)} substantive path(s) require a trail artifact:",
                *(f"  {path}" for path in substantive),
                "expected: a scope artifact added or modified in this range —",
                _EXPECTED_HINT,
            ),
        )
