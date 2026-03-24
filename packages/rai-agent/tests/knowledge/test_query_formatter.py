"""Tests for knowledge query result formatters."""

from __future__ import annotations

from rai_agent.knowledge.formatter import (
    format_query_compact,
    format_query_human,
    format_query_json,
)
from rai_agent.knowledge.models import PromptingConfig
from rai_agent.knowledge.retrieval.models import (
    DomainHints,
    RetrievalResult,
    ScoredNode,
)
from raise_core.graph.models import GraphNode


def _make_node(node_id: str, node_type: str, content: str) -> GraphNode:
    return GraphNode(
        id=node_id,
        type=node_type,
        content=content,
        source_file="test.yaml",
        created="2026-03-21",
    )


def _make_result(n_nodes: int = 3) -> RetrievalResult:
    nodes = [
        ScoredNode(
            node=_make_node(f"tool-{i}", "scaleup.tool", f"Tool {i} description"),
            score=0.9 - i * 0.1,
            explanation=f"SA={0.5 - i * 0.05:.2f}",
        )
        for i in range(n_nodes)
    ]
    return RetrievalResult(
        nodes=nodes,
        query="cash flow tools",
        hints=DomainHints(domain="scaleup"),
    )


def _prompting() -> PromptingConfig:
    return PromptingConfig(
        system_context="You are a Scaling Up expert.",
        response_format="1. Diagnosis\n2. Tools\n3. Next step",
    )


class TestFormatQueryHuman:
    def test_includes_domain_header(self) -> None:
        result = _make_result()
        output = format_query_human(result, "Scaling Up", _prompting())
        assert "Scaling Up" in output
        assert "cash flow tools" in output

    def test_includes_prompting_context(self) -> None:
        result = _make_result()
        output = format_query_human(result, "Scaling Up", _prompting())
        assert "You are a Scaling Up expert." in output

    def test_includes_scored_results(self) -> None:
        result = _make_result()
        output = format_query_human(result, "Scaling Up", _prompting())
        assert "tool-0" in output
        assert "0.90" in output or "0.9" in output
        assert "Tool 0 description" in output

    def test_empty_results(self) -> None:
        result = RetrievalResult(nodes=[], query="nothing", hints=None)
        output = format_query_human(result, "Test", None)
        assert "No relevant nodes found" in output

    def test_no_prompting(self) -> None:
        result = _make_result(1)
        output = format_query_human(result, "Test", None)
        assert "System Context" not in output
        assert "tool-0" in output


class TestFormatQueryCompact:
    def test_header_line(self) -> None:
        result = _make_result()
        output = format_query_compact(result, "scaleup", _prompting())
        assert "# Knowledge:" in output
        assert "scaleup" in output
        assert "3 results" in output

    def test_includes_ctx_line(self) -> None:
        result = _make_result()
        output = format_query_compact(result, "scaleup", _prompting())
        assert "**ctx**" in output
        assert "Scaling Up expert" in output

    def test_one_line_per_node(self) -> None:
        result = _make_result(2)
        output = format_query_compact(result, "scaleup", None)
        lines = [
            line for line in output.strip().split("\n")
            if line.startswith("**")
        ]
        assert len(lines) == 2

    def test_empty_results(self) -> None:
        result = RetrievalResult(nodes=[], query="nothing", hints=None)
        output = format_query_compact(result, "test", None)
        assert "No results" in output


class TestFormatQueryJson:
    def test_valid_json(self) -> None:
        import json

        result = _make_result()
        output = format_query_json(result, _prompting())
        parsed = json.loads(output)
        assert "results" in parsed
        assert "prompting" in parsed

    def test_results_have_scores(self) -> None:
        import json

        result = _make_result()
        output = format_query_json(result, _prompting())
        parsed = json.loads(output)
        assert len(parsed["results"]) == 3
        assert parsed["results"][0]["score"] == 0.9

    def test_no_prompting(self) -> None:
        import json

        result = _make_result()
        output = format_query_json(result, None)
        parsed = json.loads(output)
        assert parsed["prompting"] is None

    def test_empty_results(self) -> None:
        import json

        result = RetrievalResult(nodes=[], query="nothing", hints=None)
        output = format_query_json(result, None)
        parsed = json.loads(output)
        assert parsed["results"] == []
