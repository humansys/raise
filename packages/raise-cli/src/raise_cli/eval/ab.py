"""Fair A/B: single-cartridge global-scorer baseline vs per-cartridge RRF federation.

S-RFCC.W.4 (RAISE-9309). The first throwaway A/B was confounded — the baseline had
no semantic scorer (keyword-only) while the federated arm used TF-IDF. This runner
holds the scorer *type* fixed (TF-IDF on both arms) so the only variable is
partition + RRF fusion:

    baseline   = run_eval_impl with a *global* InMemorySemanticScorer over the whole corpus
    federated  = run_federated_eval_impl (per-cartridge TF-IDF + RRF → dedup → rank)

The verdict drives the ADR-103 measurement gate: federation must clear
NDCG@10 ≥ gate_ratio × baseline to be worth shipping default-on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Metrics for the A/B — superset of DEFAULT_METRICS plus recall (the epic hypothesis
# is specifically about cross-cartridge recall, which DEFAULT_METRICS omits).
AB_METRICS: list[str] = [
    "ndcg@10",
    "map",
    "mrr",
    "precision@5",
    "precision@10",
    "recall@10",
    "recall@20",
]


@dataclass(frozen=True)
class ABResult:
    """Outcome of a fair federated-vs-baseline A/B."""

    baseline: dict[str, float]
    federated: dict[str, float]
    deltas: dict[str, float]
    gate_metric: str
    gate_ratio: float
    gate_threshold: float
    gate_passed: bool
    num_queries: int


def run_ab(
    *,
    qrels: dict[str, dict[str, int]],
    corpus: list[dict[str, Any]],
    queries: dict[str, dict[str, Any]],
    metrics: list[str] | None = None,
    gate_metric: str = "ndcg@10",
    gate_ratio: float = 0.95,
) -> ABResult:
    """Run both arms over the same fixtures and compute per-metric deltas + verdict.

    Args:
        qrels: Gold-standard relevance judgments (query_id → {node_id: relevance}).
        corpus: All corpus nodes (each tagged with metadata.cartridge).
        queries: query_id → {text, source_cartridge}.
        metrics: IR metrics to compute (defaults to AB_METRICS).
        gate_metric: Metric the measurement gate is keyed on (default ndcg@10).
        gate_ratio: Federated must reach gate_ratio × baseline on gate_metric to pass.

    Returns:
        ABResult with both arms' aggregate metrics, deltas, and the gate verdict.
    """
    from raise_cli.eval.harness import (
        run_eval_impl,
        run_federated_eval_impl,
    )
    from raise_core.graph.scorers import InMemorySemanticScorer

    used_metrics = metrics or AB_METRICS

    # Baseline: one global TF-IDF scorer over the whole corpus (no partitioning).
    global_scorer = InMemorySemanticScorer(corpus)
    baseline = run_eval_impl(
        qrels=qrels,
        corpus=corpus,
        queries=queries,
        suite="baseline-global",
        semantic_scorer=global_scorer,
        metrics=used_metrics,
    )

    # Federated: per-cartridge TF-IDF + RRF fusion.
    federated = run_federated_eval_impl(
        qrels=qrels,
        corpus=corpus,
        queries=queries,
        suite="federated-rrf",
        metrics=used_metrics,
    )

    deltas = {
        m: federated.metrics.get(m, 0.0) - baseline.metrics.get(m, 0.0)
        for m in used_metrics
    }

    gate_threshold = gate_ratio * baseline.metrics.get(gate_metric, 0.0)
    gate_passed = federated.metrics.get(gate_metric, 0.0) >= gate_threshold

    return ABResult(
        baseline=baseline.metrics,
        federated=federated.metrics,
        deltas=deltas,
        gate_metric=gate_metric,
        gate_ratio=gate_ratio,
        gate_threshold=gate_threshold,
        gate_passed=gate_passed,
        num_queries=baseline.num_queries,
    )
