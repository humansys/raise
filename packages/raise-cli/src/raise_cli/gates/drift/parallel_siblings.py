"""ParallelSiblingGate — CAND-04 drift detector.

Rule: module contains ≥2 classes implementing the same Protocol with ≥5
matching method names (structural Protocol inference).
Advisory: returns passed=True with violation details.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from raise_cli.gates.drift._base import (
    DriftGate,
    classify_graph,
    is_file_in_scope,
    load_graph,
)
from raise_cli.gates.models import GateContext, GateResult

_METHOD_THRESHOLD = 5


def _find_sibling_groups(
    graph: Any, changed_files: tuple[Path, ...] | None = None
) -> list[str]:
    """Return descriptions of sibling class groups with matching method sets ≥5."""
    symbols = list(graph.get_concepts_by_type("symbol"))

    # Group methods by their parent class (via module + class prefix heuristic)
    class_methods: defaultdict[str, set[str]] = defaultdict(set)
    class_files: dict[str, str] = {}
    for sym in symbols:
        if sym.metadata.get("kind") == "method":
            sig = sym.metadata.get("signature", "")
            # Extract method name without params
            method_name = sig.split("(")[0].strip() if "(" in sig else sig
            # Group key: module + class (if available from id pattern)
            mod = sym.metadata.get("module", "unknown")
            file_path = sym.metadata.get("file", "")
            class_key = f"{mod}:{file_path}"
            class_methods[class_key].add(method_name)
            class_files[class_key] = file_path

    # Find groups sharing ≥5 method names — flagged only when at least one
    # side of the pair is a file the story touched (RAISE-10933).
    keys = list(class_methods.keys())
    violations: list[str] = []
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1 :]:
            shared = class_methods[k1] & class_methods[k2]
            if len(shared) < _METHOD_THRESHOLD:
                continue
            if not (
                is_file_in_scope(class_files.get(k1), changed_files)
                or is_file_in_scope(class_files.get(k2), changed_files)
            ):
                continue
            violations.append(f"Sibling pair {k1} / {k2}: {len(shared)} shared methods")
    return violations


class ParallelSiblingGate(DriftGate):
    """Flags parallel protocol-implementing siblings with ≥5 shared methods.

    Evidence: κ=0.802, precision=0.20 (E2161 CAND-04).
    v1: method-name overlap heuristic (no full Protocol inference).
    """

    gate_id = "drift-parallel-siblings"
    description = "Parallel protocol-implementing siblings (CAND-04)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for parallel sibling class groups."""
        graph = load_graph(context.working_dir)
        skip = classify_graph(graph, self.gate_id)
        if skip is not None:
            return skip

        violations = _find_sibling_groups(graph, context.changed_files)
        return self._advisory(self.gate_id, violations)
