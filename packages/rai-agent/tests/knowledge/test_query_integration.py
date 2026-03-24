"""Integration test: full query pipeline with real ScaleUp nodes.

Requires .raise/knowledge/scaleup/ with 447 extracted nodes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rai_agent.knowledge.domain import (
    load_domain,
    resolve_adapter,
    resolve_builder,
)
from rai_agent.knowledge.formatter import (
    format_query_compact,
    format_query_human,
    format_query_json,
)
from rai_agent.knowledge.retrieval.engine import retrieve

SCALEUP_DIR = Path(".raise/knowledge/scaleup")


@pytest.fixture(scope="module")
def scaleup_graph() -> object:
    """Build graph from real ScaleUp nodes (cached per module)."""
    manifest, config = load_domain(SCALEUP_DIR)
    builder = resolve_builder(manifest)
    return builder.build_from_directory(config.node_dir)


@pytest.fixture(scope="module")
def scaleup_adapter() -> object:
    """Resolve ScaleUp adapter from domain.yaml."""
    manifest, _ = load_domain(SCALEUP_DIR)
    return resolve_adapter(manifest)


@pytest.mark.skipif(
    not SCALEUP_DIR.exists(),
    reason="ScaleUp domain not available",
)
class TestRealScaleUpQuery:
    """Integration tests with 447 real extracted nodes."""

    def test_cash_query_returns_results(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="cash flow tools",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=10,
        )
        assert len(result.nodes) > 0
        # Top results should relate to cash
        top_ids = [n.node.id for n in result.nodes[:3]]
        assert any("cash" in nid for nid in top_ids)

    def test_people_query_returns_results(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="leadership team people",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=10,
        )
        assert len(result.nodes) > 0

    def test_scores_in_valid_range(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="execution rockefeller habits",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=5,
        )
        for scored in result.nodes:
            assert 0.0 <= scored.score <= 1.0

    def test_limit_respected(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="strategy",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=3,
        )
        assert len(result.nodes) <= 3

    def test_human_format_includes_prompting(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        manifest, _ = load_domain(SCALEUP_DIR)
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="cash flow",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=5,
        )
        output = format_query_human(
            result, manifest.display_name, manifest.prompting
        )
        assert "Scaling Up" in output
        assert "Eres experto" in output

    def test_compact_format(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        manifest, _ = load_domain(SCALEUP_DIR)
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="cash flow",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=5,
        )
        output = format_query_compact(result, manifest.name, manifest.prompting)
        assert "# Knowledge:" in output
        assert "**ctx**" in output

    def test_json_format_valid(
        self, scaleup_graph: object, scaleup_adapter: object
    ) -> None:
        manifest, _ = load_domain(SCALEUP_DIR)
        result = retrieve(
            graph=scaleup_graph,  # type: ignore[arg-type]
            query="people",
            adapter=scaleup_adapter,  # type: ignore[arg-type]
            top_k=5,
        )
        output = format_query_json(result, manifest.prompting)
        parsed = json.loads(output)
        assert "results" in parsed
        assert "prompting" in parsed
        assert parsed["prompting"]["system_context"] is not None
        assert len(parsed["results"]) > 0
