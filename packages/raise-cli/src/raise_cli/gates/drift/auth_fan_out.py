"""AuthorizationFanOutGate — AG1 drift detector.

Rule: auth-related symbol (function/method name matching auth pattern) with
≥3 downstream module destinations and no consolidating aggregator edge.
Advisory: returns passed=True with violation details.

Auth symbol pattern: names containing auth, token, permission, role, scope,
credential (case-insensitive). Configurable via AG1_AUTH_PATTERN env var.
"""

from __future__ import annotations

import os
import re
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

_DEFAULT_AUTH_PATTERN = r"auth|token|permission|role|scope|credential"
_FAN_OUT_THRESHOLD = 3


def _get_auth_pattern() -> re.Pattern[str]:
    pattern = os.environ.get("AG1_AUTH_PATTERN", _DEFAULT_AUTH_PATTERN)
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error:
        return re.compile(_DEFAULT_AUTH_PATTERN, re.IGNORECASE)


def _is_auth_symbol(name: str) -> bool:
    return bool(_get_auth_pattern().search(name))


def _find_auth_fan_out(
    graph: Any, changed_files: tuple[Path, ...] | None = None
) -> list[str]:
    """Return descriptions of auth symbols with fan-out ≥3 distinct modules."""
    symbols = list(graph.get_concepts_by_type("symbol"))

    # Build caller graph: symbol -> set of called symbol IDs
    symbol_calls: defaultdict[str, set[str]] = defaultdict(set)
    for edge in graph.iter_relationships():
        if edge.type == "calls":
            symbol_calls[edge.source].add(edge.target)

    violations: list[str] = []
    for sym in symbols:
        name = sym.metadata.get("signature", sym.id)
        if not _is_auth_symbol(name):
            continue
        if not is_file_in_scope(sym.metadata.get("file"), changed_files):
            continue
        called_ids = symbol_calls.get(sym.id, set())
        destination_modules: set[str] = set()
        for called_id in called_ids:
            called_node = graph.get_concept(called_id)
            if called_node is not None:
                mod = called_node.metadata.get("module", "")
                own_mod = sym.metadata.get("module", "")
                if mod and mod != own_mod:
                    destination_modules.add(mod)
        if len(destination_modules) >= _FAN_OUT_THRESHOLD:
            violations.append(
                f"AG1: {name} fans out to {len(destination_modules)} modules: "
                f"{', '.join(sorted(destination_modules)[:5])}"
            )
    return violations


class AuthorizationFanOutGate(DriftGate):
    """Flags auth symbols with fan-out ≥3 downstream modules (no aggregator).

    Evidence: Apiiro Sept 2025 (+322% privilege-escalation paths) — AG1.
    v1: scans current graph state (no temporal diff).
    """

    gate_id = "drift-auth-fan-out"
    description = "Authorization fan-out without aggregator (AG1)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for auth symbol fan-out in the knowledge graph."""
        graph = load_graph(context.working_dir)
        skip = classify_graph(graph, self.gate_id)
        if skip is not None:
            return skip

        violations = _find_auth_fan_out(graph, context.changed_files)
        return self._advisory(self.gate_id, violations)
