"""Thin wrapper over ranx.evaluate() for IR metrics."""

from __future__ import annotations

from typing import Any

DEFAULT_METRICS: list[str] = [
    "precision@5",
    "precision@10",
    "ndcg@10",
    "mrr",
    "map",
]


def _get_ranx() -> Any:
    import ranx  # type: ignore[import-untyped]

    return ranx


def evaluate_run(
    qrels: dict[str, dict[str, int]],
    run: dict[str, dict[str, float]],
    metrics: list[str] | None = None,
) -> dict[str, float]:
    """Evaluate a retrieval run against gold-standard qrels.

    Returns:
        Dict of metric_name → aggregated score (float).
    """
    ranx = _get_ranx()
    metrics = metrics or DEFAULT_METRICS
    ranx_qrels = ranx.Qrels(qrels)
    ranx_run = ranx.Run(run)
    result: dict[str, Any] = ranx.evaluate(ranx_qrels, ranx_run, metrics)
    return {k: float(v) for k, v in result.items()}


def evaluate_run_per_query(
    qrels: dict[str, dict[str, int]],
    run: dict[str, dict[str, float]],
    metrics: list[str] | None = None,
) -> dict[str, dict[str, float]]:
    """Evaluate per-query metrics.

    Returns:
        Dict of query_id → {metric_name: score}.
    """
    ranx = _get_ranx()
    metrics = metrics or DEFAULT_METRICS
    ranx_qrels = ranx.Qrels(qrels)
    ranx_run = ranx.Run(run)
    query_ids = list(ranx_qrels.qrels)

    per_query: dict[str, dict[str, float]] = {}
    for metric in metrics:
        scores: Any = ranx.evaluate(ranx_qrels, ranx_run, metric, return_mean=False)
        for query_id, score in zip(query_ids, scores, strict=False):
            if query_id not in per_query:
                per_query[query_id] = {}
            per_query[query_id][metric] = float(score)

    return per_query
