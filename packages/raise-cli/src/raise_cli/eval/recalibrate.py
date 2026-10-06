# pyright: reportPrivateUsage=false
"""Threshold recalibration for knowledge cartridges — S10343.4.

Provides ``derive_thresholds`` (pure function) and ``recalibrate_cartridge``
(high-level runner that executes the eval harness and writes thresholds.json).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# The four standard IR metrics produced by the eval harness.
_KNOWN_METRICS: frozenset[str] = frozenset({"ndcg@10", "mrr", "map", "precision@5"})


def derive_thresholds(
    metrics: dict[str, float],
    margin: float = 0.05,
) -> dict[str, float]:
    """Derive thresholds from eval metrics with a safety margin.

    Filters to the four standard IR metrics (ndcg@10, mrr, map, precision@5)
    and applies ``threshold = metric_value * (1 - margin)``, rounded to 3 dp.

    Args:
        metrics: Metric name → value mapping from a run_eval call.
        margin: Safety margin in [0, 1). Default 0.05 (5%).

    Returns:
        Dict of known metric → derived threshold.
    """
    return {
        metric: round(value * (1 - margin), 3)
        for metric, value in metrics.items()
        if metric in _KNOWN_METRICS
    }


def recalibrate_cartridge(
    cartridge_dir: Path,
    margin: float = 0.05,
) -> dict[str, float]:
    """Run the eval harness and write derived thresholds.json.

    Executes the evaluation harness against the cartridge's eval/ fixtures
    using the same scorer that EvalGate would use (hybrid if retrieval.profile
    or retrieval.sem_alpha is declared, global SEM_ALPHA fallback otherwise).
    Derives thresholds with ``margin`` and writes them to
    ``{cartridge_dir}/eval/thresholds.json``.

    Args:
        cartridge_dir: Cartridge root directory (contains CARTRIDGE.yaml).
        margin: Safety margin (default 0.05 = 5%).

    Returns:
        The derived thresholds dict (also written to thresholds.json).

    Raises:
        FileNotFoundError: If eval fixtures are missing.
        ImportError: If eval dependencies are not installed.
    """
    from raise_cli.eval import run_eval
    from raise_cli.eval.datasets import load_corpus, load_qrels, load_queries
    from raise_cli.eval.gate import resolve_cartridge_alpha
    from raise_cli.eval.harness import _resolve_eval_scorer

    fixtures = cartridge_dir / "eval"
    if not fixtures.exists():
        raise FileNotFoundError(
            f"No eval fixtures found at {fixtures}. "
            "Run 'rai eval run' to confirm fixtures exist."
        )

    qrels = load_qrels(fixtures / "qrels.tsv")
    corpus = load_corpus(fixtures / "corpus.json")
    queries = load_queries(fixtures / "queries.json")

    # cartridge_dir = <project>/.raise/cartridges/<name>
    # resolve_cartridge_alpha needs project root to build .raise/cartridges/<name>/CARTRIDGE.yaml
    working_dir = cartridge_dir.parent.parent.parent
    alpha = resolve_cartridge_alpha(corpus, working_dir)

    scorer = _resolve_eval_scorer(corpus, alpha=alpha)
    logger.info("Resolved eval scorer: %s", type(scorer).__name__)

    result = run_eval(
        qrels=qrels,
        corpus=corpus,
        queries=queries,
        suite="cartridge",
        use_cartridge_adapter=True,
        semantic_scorer=scorer,
    )

    thresholds = derive_thresholds(result.metrics, margin=margin)

    out_path = fixtures / "thresholds.json"
    out_path.write_text(json.dumps(thresholds, indent=2), encoding="utf-8")
    logger.info("Wrote thresholds to %s: %s", out_path, thresholds)

    return thresholds
