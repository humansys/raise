"""EvalGate — retrieval quality gate using the evaluation harness."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, ClassVar

import yaml

from raise_cli.embeddings.provider import ModelNotConfiguredError
from raise_cli.eval._paths import FIXTURES_DIR
from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)


def resolve_cartridge_alpha(
    corpus: list[dict[str, Any]], working_dir: Path
) -> float | None:
    """Resolve sem_alpha from the corpus's cartridge CARTRIDGE.yaml.

    Returns the resolved alpha when the corpus belongs to exactly one cartridge
    that declares a retrieval profile or sem_alpha. Returns None otherwise.
    """
    cartridge_names = {
        n.get("metadata", {}).get("cartridge")
        for n in corpus
        if n.get("metadata", {}).get("cartridge")
    }
    if len(cartridge_names) != 1:
        return None

    name = next(iter(cartridge_names))
    search_paths = [
        working_dir / ".raise" / "cartridges" / name / "CARTRIDGE.yaml",
    ]
    for yaml_path in search_paths:
        if not yaml_path.exists():
            continue
        try:
            from raise_core.cartridges.models import CartridgeManifest

            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            manifest = CartridgeManifest.model_validate(raw)
            if manifest.retrieval:
                return manifest.retrieval.resolve_alpha()
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.debug("Failed to read cartridge alpha from %s", yaml_path)
    return None


DEFAULT_THRESHOLDS: dict[str, float] = {
    "ndcg@10": 0.0,
    "mrr": 0.0,
    "map": 0.0,
    "precision@5": 0.0,
}


class EvalGate:
    """Quality gate that evaluates retrieval metrics against thresholds.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-retrieval"
    description: ClassVar[str] = "Retrieval quality above baseline thresholds"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run evaluation harness and check metrics against thresholds."""
        try:
            return self._run(context)
        except ImportError as exc:
            logger.info("%s skipped: eval extras not installed (%s)", self.gate_id, exc)
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="skipped: eval extras not installed — pip install raise-cli[eval]",
            )
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("EvalGate failed: %s", exc)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Evaluation failed: {exc}",
            )

    @staticmethod
    def _resolve_fixtures(working_dir: Path) -> Path | None:
        """Find eval fixtures — check direct path first, then global."""
        if (working_dir / "qrels.tsv").exists():
            return working_dir
        global_path = working_dir / FIXTURES_DIR
        if global_path.exists():
            return global_path
        return None

    @staticmethod
    def _resolve_profile_weights(
        fixtures: Path,
    ) -> tuple[float, ...] | None:
        """Resolve per-cartridge weights from CARTRIDGE.yaml adjacent to eval/.

        Looks for CARTRIDGE.yaml in fixtures.parent (the cartridge root dir).
        Returns a 4-tuple (w_sa, w_attr, w_domain, w_sem) when a retrieval_profile
        is declared; None otherwise (engine defaults apply). Silently returns None
        on CartridgeConfigError or any YAML parse failure.
        """
        from raise_core.cartridges.loader import load_cartridge

        try:
            manifest, _ = load_cartridge(fixtures.parent)
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return None
        p = manifest.retrieval_profile
        if p is None:
            return None
        return p.to_weights()

    def _run(self, context: GateContext) -> GateResult:
        from raise_cli.eval import run_eval
        from raise_cli.eval.datasets import load_corpus, load_qrels, load_queries

        fixtures = self._resolve_fixtures(context.working_dir)
        if fixtures is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No eval fixtures found — skipping",
            )

        thresholds_path = fixtures / "thresholds.json"
        if thresholds_path.exists():
            thresholds: dict[str, float] = json.loads(
                thresholds_path.read_text(encoding="utf-8")
            )
        else:
            thresholds = DEFAULT_THRESHOLDS

        qrels = load_qrels(fixtures / "qrels.tsv")
        corpus = load_corpus(fixtures / "corpus.json")
        queries = load_queries(fixtures / "queries.json")

        from raise_cli.eval.harness import EvalSemanticScorer
        from raise_core.graph.retrieval.engine import SemanticScorer
        from raise_core.graph.scorers import (
            SEM_ALPHA,
            HybridSemanticScorer,
            InMemorySemanticScorer,
        )

        alpha = resolve_cartridge_alpha(corpus, context.working_dir)
        tfidf = InMemorySemanticScorer(corpus)
        scorer: SemanticScorer
        try:
            dense = EvalSemanticScorer(corpus)
            effective_alpha = alpha if alpha is not None else SEM_ALPHA
            scorer = HybridSemanticScorer(tfidf, dense, alpha=effective_alpha)
        except (ImportError, ModelNotConfiguredError):
            scorer = tfidf

        weights = self._resolve_profile_weights(fixtures)

        result = run_eval(
            qrels=qrels,
            corpus=corpus,
            queries=queries,
            thresholds=thresholds,
            use_cartridge_adapter=True,
            semantic_scorer=scorer,
            weights=weights,
        )

        failures: list[str] = []
        details: list[str] = []
        for metric, threshold in thresholds.items():
            actual = result.metrics.get(metric, 0.0)
            if actual < threshold:
                failures.append(
                    f"{metric}={actual:.3f} below threshold {threshold:.3f}"
                )
            details.append(f"{metric}={actual:.3f} (threshold: {threshold:.3f})")

        if failures:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Retrieval quality below thresholds: {', '.join(failures)}",
                details=tuple(details),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Retrieval quality OK: {', '.join(details)}",
            details=tuple(details),
        )


class FederatedEvalGate:
    """Quality gate for federated retrieval metrics."""

    gate_id: ClassVar[str] = "gate-eval-federated"
    description: ClassVar[str] = "Federated retrieval quality above baseline thresholds"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run federated evaluation and check metrics against thresholds."""
        try:
            return self._run(context)
        except ImportError as exc:
            logger.info("%s skipped: eval extras not installed (%s)", self.gate_id, exc)
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="skipped: eval extras not installed — pip install raise-cli[eval]",
            )
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("FederatedEvalGate failed: %s", exc)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Federated evaluation failed: {exc}",
            )

    def _run(self, context: GateContext) -> GateResult:
        from raise_cli.eval.datasets import load_corpus, load_qrels, load_queries
        from raise_cli.eval.harness import run_federated_eval_impl

        fixtures = context.working_dir / FIXTURES_DIR
        if not fixtures.exists():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No eval fixtures found — skipping",
            )

        corpus_path = fixtures / "corpus-federated.json.gz"
        qrels_path = fixtures / "qrels-federated.tsv"
        queries_path = fixtures / "queries-federated.json"

        if not corpus_path.exists() or not qrels_path.exists():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No federated eval fixtures found — skipping",
            )

        thresholds_path = fixtures / "thresholds-federated.json"
        if thresholds_path.exists():
            thresholds: dict[str, float] = json.loads(
                thresholds_path.read_text(encoding="utf-8")
            )
        else:
            thresholds = DEFAULT_THRESHOLDS

        qrels = load_qrels(qrels_path)
        corpus = load_corpus(corpus_path)
        queries = load_queries(queries_path)

        result = run_federated_eval_impl(
            qrels=qrels,
            corpus=corpus,
            queries=queries,
            thresholds=thresholds,
        )

        failures: list[str] = []
        details: list[str] = []
        for metric, threshold in thresholds.items():
            actual = result.metrics.get(metric, 0.0)
            if actual < threshold:
                failures.append(
                    f"{metric}={actual:.3f} below threshold {threshold:.3f}"
                )
            details.append(f"{metric}={actual:.3f} (threshold: {threshold:.3f})")

        if failures:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Federated retrieval quality below thresholds: "
                    f"{', '.join(failures)}"
                ),
                details=tuple(details),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Federated retrieval quality OK: {', '.join(details)}",
            details=tuple(details),
        )
