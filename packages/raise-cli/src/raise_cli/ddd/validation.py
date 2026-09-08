"""DDD classification validation against ground truth."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel

from raise_core.graph.engine import Graph
from raise_core.graph.models import CoreEdgeTypes

_EXPECTED_BC_NAMES: list[str] = [
    "governance",
    "discovery",
    "ontology",
    "skills",
    "experience",
    "observability",
    "integrations",
]


class BCValidationReport(BaseModel):
    """Validation report for BC assignment against domain-model.yaml ground truth."""

    bc_names_found: list[str]
    bc_names_missing: list[str]
    symbol_coverage_pct: float
    orphan_count: int
    inter_bc_ratio: float
    intra_bc_ratio: float
    coupling_goal_met: bool


def _symbol_bc_id(graph_nx: object, symbol_id: str) -> str | None:
    """Return the BC node ID that symbol_id belongs_to, or None."""
    import networkx as nx

    g: nx.MultiDiGraph = graph_nx  # type: ignore[assignment]
    for _, tgt, data in g.out_edges(symbol_id, data=True):
        if data.get("type") == CoreEdgeTypes.BELONGS_TO:
            return str(tgt)
    return None


def validate_bc_assignments_against_model(
    graph: Graph,
    expected_bc_names: list[str] | None = None,
) -> BCValidationReport:
    """Validate BC assignments against the expected BC ground truth list.

    Computes: BC coverage, symbol coverage, orphan count, coupling ratios.

    **Coupling metric scope — D-classified symbols only.**
    The ``coupling_goal_met`` field (and the inter/intra-BC ratios that back it)
    are computed from edges whose *both* endpoints hold a ``belongs_to`` edge to a
    BC node.  Only D-classified symbols receive ``belongs_to`` assignments; I-
    classified symbols do not.  Concretely, lines 83-84 below skip any edge where
    either endpoint lacks a BC assignment, so I-classified symbols are silently
    excluded from the coupling count.

    Practical impact: approximately 30 % of the codebase (all I-classified symbols)
    is excluded from coupling analysis.  The metric answers the question "are the
    Domain symbols well-separated?" not "is the entire codebase well-separated?"
    This is intentional — I-classified symbols are infrastructure/integration and
    their inter-BC edges do not violate DDD coupling goals — but it must be kept in
    mind when interpreting ``BCValidationReport.coupling_goal_met``.
    """
    if expected_bc_names is None:
        expected_bc_names = _EXPECTED_BC_NAMES

    bc_nodes = graph.get_concepts_by_type("bounded_context")
    bc_names_found = sorted({n.content for n in bc_nodes})
    bc_names_missing = sorted(set(expected_bc_names) - set(bc_names_found))

    # Symbol coverage — only D-classified symbols
    all_symbols = graph.get_concepts_by_type("symbol")
    d_symbols = [n for n in all_symbols if n.metadata.get("ddd_layer") == "D"]
    total_d = len(d_symbols)
    assigned_d = sum(
        1 for n in d_symbols if _symbol_bc_id(graph.graph, n.id) is not None
    )
    orphan_count = total_d - assigned_d
    coverage_pct = (assigned_d / total_d * 100.0) if total_d > 0 else 0.0

    # Coupling: symbol-to-symbol edges (excluding belongs_to)
    intra = 0
    inter = 0
    for src, tgt, data in graph.graph.edges(data=True):
        if data.get("type") == CoreEdgeTypes.BELONGS_TO:
            continue
        src_type = graph.graph.nodes[src].get("type") if src in graph.graph else None
        tgt_type = graph.graph.nodes[tgt].get("type") if tgt in graph.graph else None
        if src_type != "symbol" or tgt_type != "symbol":
            continue
        src_bc = _symbol_bc_id(graph.graph, src)
        tgt_bc = _symbol_bc_id(graph.graph, tgt)
        if src_bc is None or tgt_bc is None:
            continue
        if src_bc == tgt_bc:
            intra += 1
        else:
            inter += 1

    total_edges = intra + inter
    intra_bc_ratio = intra / total_edges if total_edges > 0 else 0.0
    inter_bc_ratio = inter / total_edges if total_edges > 0 else 0.0
    coupling_goal_met = inter_bc_ratio < intra_bc_ratio if total_edges > 0 else False

    return BCValidationReport(
        bc_names_found=bc_names_found,
        bc_names_missing=bc_names_missing,
        symbol_coverage_pct=coverage_pct,
        orphan_count=orphan_count,
        inter_bc_ratio=inter_bc_ratio,
        intra_bc_ratio=intra_bc_ratio,
        coupling_goal_met=coupling_goal_met,
    )


@dataclass
class Mismatch:
    """A single disagreement between classified and ground truth."""

    symbol_id: str
    classified: str
    ground_truth: str


@dataclass
class ValidationReport:
    """Accuracy report comparing classification results to ground truth."""

    total: int = 0
    agreed: int = 0
    disagreed: int = 0
    not_classified: int = 0
    skipped_ambiguous: int = 0
    mismatches: list[Mismatch] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Return agreement ratio (0.0–1.0)."""
        if self.total == 0:
            return 0.0
        return self.agreed / self.total

    def __str__(self) -> str:
        """Format as human-readable accuracy summary."""
        pct = f"{self.accuracy:.1%}"
        lines = [
            f"Validation: {self.agreed}/{self.total} agreed ({pct} accuracy)",
            f"  Disagreed: {self.disagreed}",
            f"  Not classified: {self.not_classified}",
            f"  Skipped (ambiguous GT): {self.skipped_ambiguous}",
        ]
        if self.mismatches:
            lines.append("  Mismatches:")
            for m in self.mismatches[:20]:
                lines.append(
                    f"    {m.symbol_id}: classified={m.classified} gt={m.ground_truth}"
                )
        return "\n".join(lines)


def validate_against_ground_truth(
    classified: dict[str, str],
    ground_truth_path: Path,
) -> ValidationReport:
    """Compare classified labels against a ground truth JSON file."""
    gt_data: list[dict[str, str]] = json.loads(
        ground_truth_path.read_text(encoding="utf-8")
    )
    report = ValidationReport()

    for entry in gt_data:
        sym_id = entry["id"]
        gt_label = entry["label"]

        if gt_label == "?":
            if sym_id in classified:
                report.skipped_ambiguous += 1
            continue

        if sym_id not in classified:
            report.not_classified += 1
            continue

        report.total += 1
        cls_label = classified[sym_id]

        if cls_label == gt_label:
            report.agreed += 1
        else:
            report.disagreed += 1
            report.mismatches.append(
                Mismatch(symbol_id=sym_id, classified=cls_label, ground_truth=gt_label)
            )

    return report
