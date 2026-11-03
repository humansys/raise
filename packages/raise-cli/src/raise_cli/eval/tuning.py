"""Weight tuning via grid search on the scoring simplex."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from raise_cli.eval._models import TuningResult
from raise_cli.eval.harness import run_eval_impl

if TYPE_CHECKING:
    from raise_core.graph.retrieval.engine import SemanticScorer


def _generate_weight_combos(
    step: float = 0.1,
    ndim: int = 3,
) -> list[tuple[float, ...]]:
    """Generate all weight tuples on the unit simplex.

    Each component is a multiple of *step*, all ndim values sum to 1.0,
    and each is >= 0.0. Supports 3D (SA, ATTR, DOMAIN) and 4D (+ SEM).
    """
    n = round(1.0 / step)
    combos: list[tuple[float, ...]] = []

    def _recurse(remaining: int, depth: int, current: list[float]) -> None:
        if depth == ndim - 1:
            current.append(round(remaining * step, 10))
            combos.append(tuple(current))
            current.pop()
            return
        for i in range(remaining + 1):
            current.append(round(i * step, 10))
            _recurse(remaining - i, depth + 1, current)
            current.pop()

    _recurse(n, 0, [])
    return combos


def grid_search(
    *,
    qrels: dict[str, dict[str, int]],
    corpus: list[dict[str, Any]],
    queries: dict[str, dict[str, Any]],
    step: float = 0.1,
    ndim: int = 3,
    semantic_scorer: SemanticScorer | None = None,
) -> list[TuningResult]:
    """Evaluate every weight combination and return sorted by NDCG@10."""
    combos = _generate_weight_combos(step, ndim=ndim)
    results: list[TuningResult] = []
    for weights in combos:
        eval_result = run_eval_impl(
            qrels=qrels,
            corpus=corpus,
            queries=queries,
            weights=weights,
            semantic_scorer=semantic_scorer,
        )
        results.append(TuningResult(weights=weights, metrics=eval_result.metrics))
    results.sort(key=lambda r: r.metrics.get("ndcg@10", 0.0), reverse=True)
    return results
