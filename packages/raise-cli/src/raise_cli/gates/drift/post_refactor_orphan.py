"""PostRefactorOrphanGate — P1 drift detector.

Rule: public symbol in the working module with 0 callers outside the module
is flagged as a potential post-refactor orphan.
Advisory: returns passed=True with violation details.

S14263.3 (D1/D4/D5): adds temporal (delta) semantics on top of the v1 rule.
A symbol is only flaggable when it is genuinely NEW at HEAD vs the merge-base
(AC1) and is not an architectural entry point (AC2) — this removes the
"stock-on-touch" / touch-tax false positive RAISE-14568 named ("no temporal
comparison"). When there is no diff to compute delta against
(`changed_files=None`, unscoped blanket sweeps), delta filtering does not
apply and the pre-S14263.3 "any 0-caller symbol in scope" behavior is
preserved. An unresolvable base ref degrades to an honest-skip (D4), never
"all symbols new" (ACN2).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from raise_cli.gates.drift._base import (
    DriftGate,
    base_unresolvable_result,
    classify_graph,
    is_file_in_scope,
    load_graph,
)
from raise_cli.gates.drift._delta import (
    bare_symbol_name,
    collect_delta,
    normalize_file,
    resolve_merge_base,
)
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.story.open_service import resolve_dev_branch


def _find_orphan_symbols(
    graph: Any,
    changed_files: tuple[Path, ...] | None = None,
    new_names: frozenset[tuple[str, str]] | None = None,
    entry_point_names: frozenset[tuple[str, str]] = frozenset(),
) -> list[str]:
    """Return symbol names with 0 incoming 'calls' edges from outside their module.

    `new_names=None` disables delta filtering (no diff to compute it
    against — see `evaluate()`'s unscoped branch): falls back to the
    pre-S14263.3 "any 0-caller symbol in scope" behavior. When `new_names`
    is a frozenset of `(file, name)` pairs, a symbol is flaggable only when
    its `(file, bare name)` pair is a member (AC1 — newly added at HEAD vs
    merge-base, in THIS file) and is not in `entry_point_names` (AC2 —
    architectural entry points are 0-caller by design, never flagged even
    when new). File-qualifying the membership check (RAISE-14669) prevents
    a newly-added symbol in one changed file from incorrectly "covering" a
    same-named, pre-existing, untouched symbol in another changed file. The
    file-path component is run through `normalize_file` before the
    membership check (QR finding, RAISE-14669 follow-up) — graph symbol
    file paths can carry a `./` prefix under the flat-layout discovery
    fallback, which would otherwise never match `collect_delta`'s
    `./`-free git-diff-relative keys.
    """
    symbols = list(graph.get_concepts_by_type("symbol"))

    callee_to_callers: defaultdict[str, set[str]] = defaultdict(set)
    for edge in graph.iter_relationships():
        if edge.type == "calls":
            callee_to_callers[edge.target].add(edge.source)

    orphans: list[str] = []
    for symbol in symbols:
        symbol_module: str = symbol.metadata.get("module", "")
        symbol_file: str = symbol.metadata.get("file", "")
        if not is_file_in_scope(symbol.metadata.get("file"), changed_files):
            continue
        name: str = symbol.metadata.get("signature", symbol.id)
        if new_names is not None:
            key = (normalize_file(symbol_file), bare_symbol_name(name))
            if key not in new_names or key in entry_point_names:
                continue
        callers = callee_to_callers.get(symbol.id, set())
        external_callers = {
            c
            for c in callers
            if graph.get_concept(c) is not None
            and graph.get_concept(c).metadata.get("module", "") != symbol_module
        }
        if not external_callers:
            orphans.append(f"{name} [{symbol_module}]")
    return orphans


class PostRefactorOrphanGate(DriftGate):
    """Flags public symbols with 0 external callers — potential refactor orphans.

    Evidence: E2099 P1 pattern. Advisory until temporal comparison available.
    """

    gate_id = "drift-post-refactor-orphan"
    description = "Post-refactor orphan symbols (P1)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for orphan symbols in the knowledge graph."""
        graph = load_graph(context.working_dir)
        skip = classify_graph(graph, self.gate_id)
        if skip is not None:
            return skip

        new_names: frozenset[tuple[str, str]] | None = None
        entry_point_names: frozenset[tuple[str, str]] = frozenset()
        if context.changed_files is not None:
            base = resolve_dev_branch(context.working_dir)
            merge_base = resolve_merge_base(base, context.working_dir)
            if merge_base is None:
                return base_unresolvable_result(self.gate_id)
            delta = collect_delta(
                context.changed_files, merge_base, context.working_dir
            )
            new_names = delta.added
            entry_point_names = delta.entry_points

        orphans = _find_orphan_symbols(
            graph,
            context.changed_files,
            new_names=new_names,
            entry_point_names=entry_point_names,
        )
        return self._advisory(self.gate_id, orphans[:20])  # cap at 20 for readability
