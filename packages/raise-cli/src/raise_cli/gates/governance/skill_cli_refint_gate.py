"""SkillCliReferentialIntegrityGate — CI gate for RAISE-15763.

Skills instruct agents to run ``rai <...>`` commands. Nothing verified those
commands still exist, which is exactly how ``rai-story-close`` kept citing
``rai mission list`` / ``rai mission accomplish {index}`` (removed by
ADR-130) for an entire release cycle (RAISE-15762).

This gate derives the real command tree by in-process introspection of the
Typer/Click app (D1), extracts ``rai ...`` citations from skill *authoring
sources* (D2), and reports any citation whose command prefix does not
resolve (D5). Deterministic set membership — no inference, no LLM, no
subprocess (AC8).

Architecture: work/epics/e15763-refint-gate/stories/s15763.1-design.md
(D1-D11). Direct clone of the ``gate-workflow-transition-ownership`` mold —
opposite polarity: that gate asserts a forbidden string is absent, this one
asserts a referenced command exists.
"""

from __future__ import annotations

import itertools
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

# D4 — a segment starting with any of these is a placeholder.
# "..." is the universal prose ellipsis (e.g. `rai backlog ...`).
_PLACEHOLDER_PREFIXES: tuple[str, ...] = ("{", "<", "$", "...")

# D3 — fenced code block info strings that are scanned. Empty string (bare
# ```) counts too.
_FENCED_INFO_STRINGS: frozenset[str] = frozenset({"bash", "sh", "shell", "console", ""})

# D3 tokenizer: a command starts at a boundary (string start, or one of
# | ; & ( — the last also covers `$(` since it ends in `(`), optionally
# preceded by VAR=value assignments and an optional `uv run [--flags]`
# wrapper, then requires the literal `rai` followed by whitespace or end of
# string. The trailing lookahead is load-bearing (D3): without it,
# `RAI_META="<!-- rai:"` would false-positive.
_INVOCATION_RE = re.compile(
    r"""
    (?:\A|[|;&(])
    [ \t]*
    (?:[A-Za-z_][A-Za-z0-9_]*=\S+[ \t]+)*
    (?:uv[ \t]+run(?:[ \t]+-{1,2}\S+)*[ \t]+)?
    rai(?=[ \t]|\Z)
    """,
    re.VERBOSE,
)

_FENCE_RE = re.compile(r"^\s*```(\S*)\s*$")
_INLINE_SPAN_RE = re.compile(r"`([^`]+)`")

# A path token stops the current path collection when it contains one of
# these chars — they mark the start of a new command (`;`, `&`, `|`) or the
# close of a subshell (`)`) glued onto the previous word with no whitespace
# (e.g. "start;", 'build)').
_TOKEN_TERMINATORS: frozenset[str] = frozenset("|;&)")


def _is_placeholder(segment: str) -> bool:
    """D4 — a segment starting with ``{``, ``<``, or ``$`` is a placeholder."""
    return segment.startswith(_PLACEHOLDER_PREFIXES)


def _extract_citations(line: str) -> list[tuple[str, ...]]:
    """Extract ``rai`` command-path citations from a single line of text.

    Returns one tuple per invocation found: the ordered command-path
    segments up to (but not including) the first flag (``-...``) or the
    first placeholder segment. A citation whose *first* segment is a
    placeholder is unresolvable by construction and is skipped entirely
    (D4), not reported.
    """
    citations: list[tuple[str, ...]] = []
    for match in _INVOCATION_RE.finditer(line):
        rest = line[match.end() :]
        tokens = rest.split()
        path: list[str] = []
        for raw_token in tokens:
            if raw_token.startswith("#"):
                # Shell comment — nothing after this is part of the command.
                break
            term_idx = next(
                (i for i, ch in enumerate(raw_token) if ch in _TOKEN_TERMINATORS),
                None,
            )
            token = raw_token if term_idx is None else raw_token[:term_idx]
            if token:
                if token.startswith("-"):
                    break
                if _is_placeholder(token):
                    if not path:
                        # Leading placeholder — unresolvable by construction.
                        path = []
                    break
                path.append(token)
            if term_idx is not None:
                break
        if not path:
            continue
        citations.append(tuple(path))
    return citations


@dataclass(frozen=True)
class _CommandTree:
    """The live CLI command tree, split by node kind (D5 hardening).

    The distinction matters: a *leaf* resolves regardless of what follows
    (trailing words are arguments); a *group* resolves only when the
    citation stops exactly there (a bare group mention) — a further plain
    word that does not extend into any known child is a stale subcommand,
    not an argument, and must NOT resolve (RAISE-15773).
    """

    groups: frozenset[tuple[str, ...]]
    leaves: frozenset[tuple[str, ...]]

    @property
    def all_paths(self) -> frozenset[tuple[str, ...]]:
        return self.groups | self.leaves


def _cli_command_tree() -> _CommandTree:
    """Derive the real CLI command tree via in-process Click introspection (D1).

    The import is deferred here, not at module scope: ``raise_cli.cli.main``
    imports ``cli.commands.gate`` -> ``gates.registry``, and the registry
    loads this gate via entry point. A module-level import would invite a
    cycle and make every unrelated ``rai gate check`` pay the full CLI
    import cost.
    """
    import click
    import typer.main

    from raise_cli.cli.main import app as _rai_app

    root = typer.main.get_command(_rai_app)
    groups: set[tuple[str, ...]] = set()
    leaves: set[tuple[str, ...]] = set()

    def _walk(command: click.Command, prefix: tuple[str, ...]) -> None:
        if isinstance(command, click.Group):
            groups.add(prefix)
            for name, sub in command.commands.items():
                _walk(sub, (*prefix, name))
        else:
            leaves.add(prefix)

    if isinstance(root, click.Group):
        for name, sub in root.commands.items():
            _walk(sub, (name,))

    return _CommandTree(groups=frozenset(groups), leaves=frozenset(leaves))


def _alternation_branches(path: tuple[str, ...]) -> list[tuple[str, ...]]:
    """Expand ``/``-separated alternation shorthand in any segment.

    ``rai skill set create/list/diff`` cites three real subcommands via
    shorthand (rai-skillset-manage/SKILL.md:149); each branch is checked
    independently and the citation resolves only if every branch does. A
    path with no ``/`` yields a single branch — itself.
    """
    options = [segment.split("/") for segment in path]
    return [tuple(combo) for combo in itertools.product(*options)]


def _resolves_branch(path: tuple[str, ...], tree: _CommandTree) -> bool:
    """D5 (hardened) — longest-prefix resolution, leaf vs group aware.

    A leaf resolves regardless of trailing words (arguments). A group
    resolves only when the citation stops exactly at the group (a bare
    mention, e.g. ``rai backlog``) — a further plain-word segment that does
    not extend into any known child is a stale subcommand, not an
    argument, and must NOT resolve (RAISE-15773).
    """
    best_depth = 0
    for depth in range(len(path), 0, -1):
        if path[:depth] in tree.all_paths:
            best_depth = depth
            break
    if best_depth == 0:
        return False
    if path[:best_depth] in tree.leaves:
        return True
    # Prefix is a group: resolves only if the citation stops exactly there.
    return best_depth == len(path)


def _resolves(path: tuple[str, ...], tree: _CommandTree) -> bool:
    """D5 (hardened) — alternation-aware, leaf-vs-group resolution.

    Splits ``/`` alternation branches (D3 addendum) and requires every
    branch to resolve via ``_resolves_branch``.
    """
    return all(_resolves_branch(branch, tree) for branch in _alternation_branches(path))


@dataclass(frozen=True)
class _DiscoveredSkills:
    """Result of the D2 (revised) multi-root scan.

    ``files`` is the deduplicated list to actually scan for citations.
    ``divergences`` names skill pairs where the source and its distributed
    mirror disagree — reported as findings of their own, never silenced.
    """

    files: tuple[Path, ...]
    divergences: tuple[tuple[str, Path, Path], ...]


def _same_content(a: Path, b: Path) -> bool:
    try:
        return a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def _discover_skill_files(working_dir: Path) -> _DiscoveredSkills:
    """D2 (revised) — scan the real authoring source, not just its mirrors.

    ``.claude/skills/*/SKILL.md`` is the actual source of truth for ``rai
    skill sync`` (``raise_cli/cli/commands/skill.py:418``) — it is the
    **primary** root whenever it exists, not an excluded mirror. A
    violation written only there was invisible to the old
    skills_base-primary scan until someone ran ``rai skill sync``: gate
    enforcement depended on agent-side sync happening first, exactly the
    neutralizable gap this epic exists to close.

    ``packages/raise-cli/src/raise_cli/skills_base/*/SKILL.md`` (a sync
    *destination*, per D2's corrected understanding) and
    ``.raise/skills/*/*/SKILL.md`` (independent skill-set variants, never
    mirrors of ``.claude/skills``) are still scanned. For a skill name
    present in both the source and the ``skills_base`` mirror: identical
    content is deduplicated to one report; divergent content is scanned on
    *both* sides and additionally reported as its own finding — a
    source/mirror disagreement is exactly the class of defect this gate
    exists to catch, not something to silence.

    Consumer-project fallback when ``.claude/skills`` does not exist but
    ``skills_base/`` does: scan ``skills_base/`` + ``.raise/skills/``
    alone (unchanged from the original design).
    """
    claude_skills = working_dir / ".claude" / "skills"
    skills_base = (
        working_dir / "packages" / "raise-cli" / "src" / "raise_cli" / "skills_base"
    )
    raise_skills = working_dir / ".raise" / "skills"

    primary: dict[str, Path] = {}
    if claude_skills.is_dir():
        primary = {f.parent.name: f for f in sorted(claude_skills.glob("*/SKILL.md"))}

    mirror: dict[str, Path] = {}
    if skills_base.is_dir():
        mirror = {f.parent.name: f for f in sorted(skills_base.glob("*/SKILL.md"))}

    extra: list[Path] = []
    if raise_skills.is_dir():
        extra = sorted(raise_skills.glob("*/*/SKILL.md"))

    files: list[Path] = []
    divergences: list[tuple[str, Path, Path]] = []

    common = set(primary) & set(mirror)
    for name in sorted(set(primary) - common):
        files.append(primary[name])
    for name in sorted(set(mirror) - common):
        files.append(mirror[name])
    for name in sorted(common):
        source = primary[name]
        dest = mirror[name]
        if _same_content(source, dest):
            files.append(source)
        else:
            files.append(source)
            files.append(dest)
            divergences.append((name, source, dest))

    files.extend(extra)

    return _DiscoveredSkills(files=tuple(files), divergences=tuple(divergences))


def _discover_doc_surfaces(working_dir: Path) -> tuple[Path, ...]:
    """RAISE-15776 — scan operational doc surfaces for rai citations.

    ``dev/sops/**/*.md`` and ``.raise/gates/**/*.md`` are runbooks and gate
    definitions that cite ``rai`` commands. Unlike skills they have no
    mirror/sync mechanism — each file is scanned independently.
    """
    surfaces: list[Path] = []
    for sub in (
        working_dir / "dev" / "sops",
        working_dir / ".raise" / "gates",
    ):
        if sub.is_dir():
            surfaces.extend(sorted(sub.rglob("*.md")))
    return tuple(surfaces)


def _frontmatter_end(lines: list[str]) -> int:
    """Return the 0-based index of the closing frontmatter ``---``, or -1."""
    if not lines or lines[0].strip() != "---":
        return -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return idx
    return -1


@dataclass
class _FenceState:
    """Mutable fenced-code-block state carried across lines of one file."""

    in_fence: bool = False
    active: bool = False  # fence has a scannable info string (D3)


def _citations_in_line(raw_line: str, state: _FenceState) -> list[tuple[str, ...]]:
    """Return citations on one line, updating ``state`` for fence tracking.

    Inside an active fence (bash/sh/shell/console/empty info string), the
    whole line is scanned. Outside any fence, only inline code spans count
    (D3) — plain prose is never scanned.
    """
    fence_match = _FENCE_RE.match(raw_line)
    if fence_match is not None:
        if not state.in_fence:
            state.in_fence = True
            state.active = fence_match.group(1).lower() in _FENCED_INFO_STRINGS
        else:
            state.in_fence = False
            state.active = False
        return []

    if state.in_fence:
        return _extract_citations(raw_line) if state.active else []

    return [
        citation
        for span in _INLINE_SPAN_RE.findall(raw_line)
        for citation in _extract_citations(span)
    ]


def _scan_file(path: Path) -> list[tuple[int, tuple[str, ...]]]:
    """Extract (line_number, path) citations from bash blocks + inline spans (D3).

    Frontmatter (a leading ``---``/``---`` block) and plain prose are
    excluded.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.debug("skill-cli-refint-read-error: %s — %s", path, exc)
        return []

    lines = text.splitlines()
    frontmatter_end = _frontmatter_end(lines)
    state = _FenceState()
    found: list[tuple[int, tuple[str, ...]]] = []

    for idx, raw_line in enumerate(lines):
        if idx <= frontmatter_end:
            continue
        for path_tuple in _citations_in_line(raw_line, state):
            found.append((idx + 1, path_tuple))

    return found


class SkillCliReferentialIntegrityGate:
    """Fail-closed CI gate: every ``rai ...`` citation in a SKILL.md must resolve.

    Scans the authoring SKILL.md corpus (D2), tokenizes ``rai`` invocations
    in bash blocks and inline code spans (D3), and reports any citation
    whose command-path prefix is not present in the live Click command tree
    (D1/D5). No suppression mechanism exists (D7/D8/AC9) — the only
    remedies are fixing the citation, fixing the CLI, or (as an emergency
    lever, reviewable in an MR diff) ``allow_failure: true`` on the CI job.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "skill-cli-refint"
    description: ClassVar[str] = (
        "Every 'rai ...' command cited in skills and doc surfaces resolves "
        "against the live CLI command tree (RAISE-15763, RAISE-15776)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan the authoring corpus and report unresolved citations."""
        discovered = _discover_skill_files(context.working_dir)
        doc_surfaces = _discover_doc_surfaces(context.working_dir)
        tree = _cli_command_tree()

        total_citations = 0
        unresolved: list[str] = []
        violation_units: set[str] = set()

        all_files = list(discovered.files) + list(doc_surfaces)

        for scan_file in all_files:
            for line_no, path_tuple in _scan_file(scan_file):
                total_citations += 1
                if _resolves(path_tuple, tree):
                    continue
                rel = scan_file.relative_to(context.working_dir)
                violation_units.add(str(rel))
                citation = "rai " + " ".join(path_tuple)
                unresolved.append(f"{rel}:{line_no}: '{citation}' — no such command")

        for name, source, dest in discovered.divergences:
            rel_source = source.relative_to(context.working_dir)
            rel_dest = dest.relative_to(context.working_dir)
            violation_units.add(name)
            unresolved.append(
                f"{name}: source ({rel_source}) and mirror ({rel_dest}) "
                "diverge — run 'rai skill sync'"
            )

        file_count = len(all_files)
        if not unresolved:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"{total_citations} rai citation(s) across "
                    f"{file_count} file(s) all resolve"
                ),
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=(
                f"{len(unresolved)} unresolved rai command(s)/divergence(s) cited in "
                f"{len(violation_units)} file(s) across "
                f"{file_count} file(s)"
            ),
            details=tuple(unresolved),
        )
