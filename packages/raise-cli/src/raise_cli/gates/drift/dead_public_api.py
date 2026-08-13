"""DeadPublicApiGate — P4 + CAND-10 drift detector.

Two sub-checks:
- P4: public symbol with 0 non-test callers, absent from module __all__
- CAND-10: module __all__ covers < 50% of substantive public classes/functions

Advisory: returns passed=True with both sub-check results in details.

S14263.3 (D1/D4/D5/D6): P4 (`_check_dead_symbols`) gains the same temporal
(delta) + entry-point treatment as P1 `post_refactor_orphan` — a symbol is
only flaggable when genuinely NEW at HEAD vs the merge-base (AC1) and not
an architectural entry point (AC2). CAND-10 (`_check_all_coverage`) is
DELIBERATELY untouched — no new params, no delta filtering — its demotion
is scoped to S14263.5, not this story (D6/AC5).
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any

from raise_cli.gates.drift._base import (
    DriftGate,
    base_unresolvable_result,
    classify_graph,
    is_excluded,
    is_file_in_scope,
    load_graph,
    scoped_rglob,
)
from raise_cli.gates.drift._delta import (
    bare_symbol_name,
    collect_delta,
    normalize_file,
    resolve_merge_base,
)
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.story.open_service import resolve_dev_branch
from raise_core.discovery.symbols import (
    _package_qualifier,  # pyright: ignore[reportPrivateUsage]
    qualified_module_id,
)

_CAND10_THRESHOLD = 0.5


def _read_all_exports(init_path: Path) -> set[str]:
    """Return names listed in __all__ in the given __init__.py."""
    try:
        source = init_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__all__"
                    and isinstance(node.value, ast.List)
                ):
                    return {
                        elt.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    }
    return set()


def _check_dead_symbols(
    graph: Any,
    changed_files: tuple[Path, ...] | None = None,
    new_names: frozenset[tuple[str, str]] | None = None,
    entry_point_names: frozenset[tuple[str, str]] = frozenset(),
) -> list[str]:
    """P4: public symbols with 0 external callers absent from __all__.

    `new_names=None` disables delta filtering (no diff to compute it
    against — see `evaluate()`'s unscoped branch): falls back to the
    pre-S14263.3 "any 0-caller symbol in scope" behavior. When `new_names`
    is a frozenset of `(file, name)` pairs, a symbol is flaggable only when
    its `(file, bare name)` pair is a member (AC1) and is not in
    `entry_point_names` (AC2). File-qualifying the membership check
    (RAISE-14669) prevents a newly-added symbol in one changed file from
    incorrectly "covering" a same-named, pre-existing, untouched symbol in
    another changed file. The file-path component is run through
    `normalize_file` before the membership check (QR finding, RAISE-14669
    follow-up) — graph symbol file paths can carry a `./` prefix under the
    flat-layout discovery fallback, which would otherwise never match
    `collect_delta`'s `./`-free git-diff-relative keys.
    """
    symbols = list(graph.get_concepts_by_type("symbol"))

    callee_to_callers: defaultdict[str, set[str]] = defaultdict(set)
    for edge in graph.iter_relationships():
        if edge.type == "calls":
            callee_to_callers[edge.target].add(edge.source)

    dead: list[str] = []
    for symbol in symbols:
        sym_module = symbol.metadata.get("module", "")
        sym_file = symbol.metadata.get("file")
        if not is_file_in_scope(sym_file, changed_files):
            continue
        name_raw = symbol.metadata.get("signature", symbol.id)
        if new_names is not None:
            key = (normalize_file(sym_file or ""), bare_symbol_name(name_raw))
            if key not in new_names or key in entry_point_names:
                continue
        callers = callee_to_callers.get(symbol.id, set())
        non_test_external = {
            c
            for c in callers
            if graph.get_concept(c) is not None
            and graph.get_concept(c).metadata.get("module", "") != sym_module  # type: ignore[union-attr]
            and "test" not in graph.get_concept(c).metadata.get("module", "")  # type: ignore[union-attr]
        }
        if not non_test_external:
            dead.append(f"P4: {name_raw} [{sym_module}]")
    return dead


def _check_all_coverage(
    working_dir: Path, graph: Any, changed_files: tuple[Path, ...] | None = None
) -> list[str]:
    """CAND-10: modules whose __all__ covers < 50% of public symbols."""
    symbols = list(graph.get_concepts_by_type("symbol"))

    by_module: defaultdict[str, list[str]] = defaultdict(list)
    for sym in symbols:
        mod = sym.metadata.get("module", "")
        if mod:
            name = sym.metadata.get("signature", "").split("(")[0].strip()
            if name:
                by_module[mod].append(name)

    violations: list[str] = []
    for init_path in scoped_rglob(working_dir, "__init__.py", changed_files):
        if is_excluded(init_path, working_dir):
            continue
        parent_dir = init_path.parent
        mod_key = parent_dir.name
        # RAISE-16033 R1: a module under packages/<pkg>/... gets a
        # package-qualified graph id (mod-<pkg>--<name>) — the bare
        # f"mod-{mod_key}" lookup this used to be always misses for
        # those, silently disabling this check repo-wide (empty
        # public_names short-circuits below before flagging anything).
        rel_parts = init_path.relative_to(working_dir).parts
        package = _package_qualifier(rel_parts)
        mod_id = qualified_module_id(mod_key, package)
        public_names = by_module.get(mod_id, [])
        if len(public_names) < 2:
            continue
        all_exports = _read_all_exports(init_path)
        covered = len(all_exports & set(public_names))
        coverage = covered / len(public_names)
        if coverage < _CAND10_THRESHOLD:
            rel = init_path.relative_to(working_dir)
            violations.append(
                f"CAND-10: {rel} __all__ covers {covered}/{len(public_names)} ({coverage:.0%})"
            )
    return violations


class DeadPublicApiGate(DriftGate):
    """Flags dead public symbols (P4) and under-exported modules (CAND-10).

    Evidence: E2099 P4 + E2161 CAND-10 (κ=0.802, precision=0.20).
    """

    gate_id = "drift-dead-public-api"
    description = "Dead public API + __init__ omission (P4 + CAND-10)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run P4 + CAND-10 sub-checks.

        S14263.3 (D4/D6): resolves the delta base ref once for P4 only —
        CAND-10 (`_check_all_coverage`) is called exactly as before, with no
        new_names/entry_point_names, and is unaffected by an unresolvable
        base ref short-circuit (both sub-checks skip together, matching the
        gate-level honest-skip contract; the alternative — running CAND-10
        while P4 skips — would split one gate into two silently-different
        evaluation states, which is worse than a shared, visible skip).
        """
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

        violations: list[str] = []
        violations.extend(
            _check_all_coverage(context.working_dir, graph, context.changed_files)
        )
        violations.extend(
            _check_dead_symbols(
                graph,
                context.changed_files,
                new_names=new_names,
                entry_point_names=entry_point_names,
            )[:10]
        )  # cap P4 items
        return self._advisory(self.gate_id, violations)
