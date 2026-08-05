"""GraphAppliesToGate — RC1 applies_to resolution threshold (RAISE-15811, E14781).

Blocks a release when the knowledge graph's ``applies_to`` resolution falls
below 80% over *module-backed* patterns: patterns holding at least one context
keyword for which a module node demonstrably exists. Patterns whose keywords are
all pure concepts (``gemba``, ``fastapi``) are excluded — the graph has nothing
for them to point at, so counting them would measure vocabulary coverage rather
than resolver quality.

The measurement itself lives in
:func:`raise_cli.context.extractors.relationships.compute_filtered_applicability`
so it stays unit-testable and reusable by build-time health output; this module
owns only graph loading and the pass/fail verdict.

The gate reads an already-built graph and never rebuilds it (design D1): a
build is a full source scan, and gates are inspectors, not mutators. A stale or
absent graph fails with the command to run.

Architecture: ADR-039 §5 (Built-in gates).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from raise_cli.config.paths import get_memory_dir
from raise_cli.context.extractors.relationships import compute_filtered_applicability
from raise_cli.gates.models import GateResult
from raise_cli.graph.backends import get_active_backend

if TYPE_CHECKING:
    from pathlib import Path

    from raise_cli.gates.models import GateContext
    from raise_core.graph.models import GraphNode

_INDEX_FILE = "index.json"
_BUILD_HINT = "Run `rai graph build` first."
# A failure lists offenders, but a graph-wide regression can produce hundreds.
_MAX_LISTED_KEYWORDS = 20


def _load_nodes(working_dir: Path) -> list[GraphNode]:
    """Load every node of ``working_dir``'s graph via the active backend.

    Resolution mirrors ``cli/commands/graph.py`` exactly — the legacy
    ``index.json`` path as migration source, then whatever backend
    :func:`get_active_backend` selects. Since RAISE-15607 ``project_root`` is an
    identity key, not a hint: it selects which checkout's partition is read.
    Passing ``working_dir`` is what makes the gate measure the checkout it was
    asked about rather than the process's cwd.

    ``index.json`` is *not* read directly: the active backend in this repo is
    SQLite and no such file is written any more, so a JSON reader would report
    "index not found" forever.

    Args:
        working_dir: The checkout being gated.

    Returns:
        All nodes in the graph; empty when the graph has never been built.
    """
    backend = get_active_backend(
        get_memory_dir(working_dir) / _INDEX_FILE, project_root=working_dir
    )
    return list(backend.load().iter_concepts())


class GraphAppliesToGate:
    """Blocking gate: ``applies_to`` resolves for >=80% of module-backed patterns.

    Registered via the ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "graph-applies-to-rc1"
    description: ClassVar[str] = (
        "applies_to resolves for >=80% of module-backed patterns (E14781 RC1)"
    )
    workflow_point: ClassVar[str] = "before:release:publish"
    is_blocker: ClassVar[bool] = True
    THRESHOLD: ClassVar[float] = 0.80

    def evaluate(self, context: GateContext) -> GateResult:
        """Measure filtered ``applies_to`` resolution and compare to THRESHOLD."""
        try:
            nodes = _load_nodes(context.working_dir)
        except Exception as exc:  # noqa: BLE001 - any backend fault is a gate failure
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Could not load the knowledge graph: {exc}. {_BUILD_HINT}",
            )

        if not nodes:
            # Deliberately not a vacuous pass: an empty graph is a failed build,
            # and passing here would let that failure through the release gate.
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Knowledge graph is empty — no nodes found. {_BUILD_HINT}",
            )

        report = compute_filtered_applicability(nodes, {n.id: n for n in nodes})

        if report.filtered_denominator == 0:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    "Vacuous pass: no module-backed patterns to measure "
                    f"({report.no_candidate} pattern(s) excluded, no-candidate). "
                    "The rate is undefined, not perfect."
                ),
            )

        passed = report.rate >= self.THRESHOLD
        message = (
            f"applies_to {report.resolved}/{report.filtered_denominator} "
            f"({report.rate:.1%}) of module-backed patterns; "
            f"threshold {self.THRESHOLD:.0%}; "
            f"{report.no_candidate} excluded (no-candidate)"
        )
        if passed:
            return GateResult(passed=True, gate_id=self.gate_id, message=message)

        listed = report.unresolved_keywords[:_MAX_LISTED_KEYWORDS]
        details = [f"unresolved module-backed keyword: {kw}" for kw in listed]
        if len(report.unresolved_keywords) > len(listed):
            details.append(
                f"... and {len(report.unresolved_keywords) - len(listed)} more"
            )
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=message,
            details=tuple(details),
        )
