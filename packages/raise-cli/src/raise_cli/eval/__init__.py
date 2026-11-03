"""RaiSE evaluation harness — IR metrics for neurosymbolic retrieval.

Requires the ``[eval]`` optional dependency group::

    pip install raise-cli[eval]
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from raise_cli.eval._models import EvalResult

if TYPE_CHECKING:
    from raise_core.graph.retrieval.engine import SemanticScorer

__all__ = ["EvalResult", "run_eval"]


def _check_eval_deps() -> None:
    try:
        __import__("ranx")
    except ImportError:
        msg = (
            "Evaluation dependencies not installed. "
            "Install with: pip install raise-cli[eval]"
        )
        raise ImportError(msg) from None


def run_eval(
    *,
    qrels: dict[str, dict[str, int]],
    corpus: list[dict[str, object]],
    queries: dict[str, dict[str, object]],
    suite: str = "cartridge",
    thresholds: dict[str, float] | None = None,
    weights: tuple[float, ...] | None = None,
    use_cartridge_adapter: bool = False,
    semantic_scorer: SemanticScorer | None = None,
) -> EvalResult:
    """Run evaluation harness against a corpus with gold-standard qrels."""
    _check_eval_deps()
    from raise_cli.eval.harness import run_eval_impl

    return run_eval_impl(
        qrels=qrels,
        corpus=corpus,
        queries=queries,
        suite=suite,
        thresholds=thresholds,
        weights=weights,
        use_cartridge_adapter=use_cartridge_adapter,
        semantic_scorer=semantic_scorer,
    )
