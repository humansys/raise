"""JSON structured reporter for evaluation results."""

from __future__ import annotations

import json

from raise_cli.eval._models import EvalResult

SCHEMA_VERSION = "1.0"


class JsonReporter:
    """Render EvalResult as structured JSON."""

    def render(self, result: EvalResult) -> str:
        """Produce JSON with schema version, metrics, and per-query data."""
        data = {
            "schema_version": SCHEMA_VERSION,
            "suite": result.suite,
            "num_queries": result.num_queries,
            "corpus_hash": result.corpus_hash,
            "metrics": result.metrics,
            "per_query": result.per_query,
            "thresholds": result.thresholds,
            "ci": result.ci,
        }
        return json.dumps(data, indent=2)
