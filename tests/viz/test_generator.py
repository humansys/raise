"""Tests for memory graph visualization generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from raise_cli.viz.generator import generate_viz_html


@pytest.fixture
def minimal_graph(tmp_path: Path) -> Path:
    """Create a minimal valid graph index."""
    graph = {
        "directed": True,
        "multigraph": True,
        "graph": {},
        "nodes": [
            {
                "id": "PAT-001",
                "type": "pattern",
                "content": "Test pattern content",
                "source_file": "patterns.jsonl",
                "created": "2026-01-01",
                "metadata": {"context": ["testing", "python"], "learned_from": "F1.1"},
            },
            {
                "id": "mod-cli",
                "type": "module",
                "content": "CLI module",
                "source_file": "architecture.md",
                "created": "2026-01-01",
                "metadata": {},
            },
        ],
        "links": [
            {"source": "PAT-001", "target": "mod-cli", "type": "related_to"},
        ],
    }
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(graph))
    return index_path


@pytest.fixture
def rich_graph(tmp_path: Path) -> Path:
    """Create a graph with multiple domains and pattern categories."""
    nodes = [
        # Governance
        {
            "id": "principle-01",
            "type": "principle",
            "content": "Simplicity",
            "source_file": "constitution.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "guardrail-01",
            "type": "guardrail",
            "content": "Type hints",
            "source_file": "guardrails.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        # Architecture
        {
            "id": "mod-memory",
            "type": "module",
            "content": "Memory module",
            "source_file": "architecture.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "comp-query",
            "type": "component",
            "content": "Query engine",
            "source_file": "architecture.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "layer-core",
            "type": "layer",
            "content": "Core layer",
            "source_file": "architecture.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        # Memory — patterns with different categories
        {
            "id": "PAT-001",
            "type": "pattern",
            "content": "Architecture pattern",
            "source_file": "patterns.jsonl",
            "created": "2026-01-01",
            "metadata": {"context": ["architecture", "design"]},
        },
        {
            "id": "PAT-002",
            "type": "pattern",
            "content": "Process pattern",
            "source_file": "patterns.jsonl",
            "created": "2026-01-01",
            "metadata": {"context": ["process", "workflow"]},
        },
        {
            "id": "PAT-003",
            "type": "pattern",
            "content": "Testing pattern",
            "source_file": "patterns.jsonl",
            "created": "2026-01-01",
            "metadata": {"context": ["testing"]},
        },
        {
            "id": "PAT-004",
            "type": "pattern",
            "content": "No context pattern",
            "source_file": "patterns.jsonl",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "CAL-001",
            "type": "calibration",
            "content": "Calibration data",
            "source_file": "calibration.jsonl",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "SES-001",
            "type": "session",
            "content": "Session record",
            "source_file": "sessions.jsonl",
            "created": "2026-01-01",
            "metadata": {},
        },
        # Work
        {
            "id": "epic-e01",
            "type": "epic",
            "content": "Foundation epic",
            "source_file": "scope.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        {
            "id": "story-f1.1",
            "type": "story",
            "content": "First story",
            "source_file": "scope.md",
            "created": "2026-01-01",
            "metadata": {},
        },
        # Skills
        {
            "id": "skill-session-start",
            "type": "skill",
            "content": "Session start skill",
            "source_file": "SKILL.md",
            "created": "2026-01-01",
            "metadata": {},
        },
    ]
    links = [
        {"source": "PAT-001", "target": "mod-memory", "type": "related_to"},
        {"source": "guardrail-01", "target": "mod-memory", "type": "constrained_by"},
        {"source": "story-f1.1", "target": "epic-e01", "type": "belongs_to"},
    ]
    graph = {
        "directed": True,
        "multigraph": True,
        "graph": {},
        "nodes": nodes,
        "links": links,
    }
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(graph))
    return index_path


class TestGenerateVizHtml:
    """Tests for generate_viz_html function."""

    def test_generates_html_file(self, minimal_graph: Path, tmp_path: Path) -> None:
        """Output file is created and is valid HTML."""
        output = tmp_path / "output" / "graph.html"
        result = generate_viz_html(minimal_graph, output)

        assert result == output
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert content.startswith("<!DOCTYPE html>")
        assert "</html>" in content

    def test_embeds_graph_data(self, minimal_graph: Path, tmp_path: Path) -> None:
        """Graph data is embedded as JSON in the HTML."""
        output = tmp_path / "graph.html"
        generate_viz_html(minimal_graph, output)
        content = output.read_text(encoding="utf-8")

        assert "PAT-001" in content
        assert "mod-cli" in content
        assert "related_to" in content

    def test_includes_d3_script(self, minimal_graph: Path, tmp_path: Path) -> None:
        """D3.js is loaded in the HTML."""
        output = tmp_path / "graph.html"
        generate_viz_html(minimal_graph, output)
        content = output.read_text(encoding="utf-8")

        assert "d3.v7.min.js" in content

    def test_pattern_metadata_preserved(
        self, minimal_graph: Path, tmp_path: Path
    ) -> None:
        """Pattern nodes include category, tags, and learned_from."""
        output = tmp_path / "graph.html"
        generate_viz_html(minimal_graph, output)
        content = output.read_text(encoding="utf-8")

        # The embedded JSON should contain pattern metadata
        assert '"category"' in content
        assert '"tags"' in content
        assert '"learned_from"' in content

    def test_pattern_content_not_truncated(self, tmp_path: Path) -> None:
        """Pattern content is preserved in full (not truncated to 200 chars)."""
        long_content = "A" * 500
        graph = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [
                {
                    "id": "PAT-LONG",
                    "type": "pattern",
                    "content": long_content,
                    "source_file": "",
                    "created": "",
                    "metadata": {"context": ["testing"]},
                }
            ],
            "links": [],
        }
        index_path = tmp_path / "index.json"
        index_path.write_text(json.dumps(graph))

        output = tmp_path / "graph.html"
        generate_viz_html(index_path, output)
        content = output.read_text(encoding="utf-8")

        assert long_content in content

    def test_non_pattern_content_truncated(self, tmp_path: Path) -> None:
        """Non-pattern nodes have content truncated to 200 chars."""
        long_content = "B" * 500
        graph = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [
                {
                    "id": "mod-big",
                    "type": "module",
                    "content": long_content,
                    "source_file": "",
                    "created": "",
                    "metadata": {},
                }
            ],
            "links": [],
        }
        index_path = tmp_path / "index.json"
        index_path.write_text(json.dumps(graph))

        output = tmp_path / "graph.html"
        generate_viz_html(index_path, output)
        content = output.read_text(encoding="utf-8")

        assert long_content not in content
        assert "B" * 200 in content

    def test_pattern_without_context_gets_general_category(
        self, rich_graph: Path, tmp_path: Path
    ) -> None:
        """Patterns with no context tags get category 'general'."""
        output = tmp_path / "graph.html"
        generate_viz_html(rich_graph, output)
        content = output.read_text(encoding="utf-8")

        assert '"general"' in content

    def test_all_domain_types_present(self, rich_graph: Path, tmp_path: Path) -> None:
        """HTML contains nodes from all domains."""
        output = tmp_path / "graph.html"
        generate_viz_html(rich_graph, output)
        content = output.read_text(encoding="utf-8")

        # Governance
        assert "principle-01" in content
        assert "guardrail-01" in content
        # Architecture
        assert "mod-memory" in content
        assert "layer-core" in content
        # Memory
        assert "PAT-001" in content
        assert "CAL-001" in content
        assert "SES-001" in content
        # Work
        assert "epic-e01" in content
        assert "story-f1.1" in content
        # Skills
        assert "skill-session-start" in content

    def test_edge_types_preserved(self, rich_graph: Path, tmp_path: Path) -> None:
        """Edge relationship types are preserved in the output."""
        output = tmp_path / "graph.html"
        generate_viz_html(rich_graph, output)
        content = output.read_text(encoding="utf-8")

        assert "related_to" in content
        assert "constrained_by" in content
        assert "belongs_to" in content

    def test_creates_parent_directories(
        self, minimal_graph: Path, tmp_path: Path
    ) -> None:
        """Output path parent directories are created if missing."""
        output = tmp_path / "deep" / "nested" / "dir" / "graph.html"
        generate_viz_html(minimal_graph, output)

        assert output.exists()

    def test_empty_graph(self, tmp_path: Path) -> None:
        """Handles an empty graph without errors."""
        graph = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [],
            "links": [],
        }
        index_path = tmp_path / "index.json"
        index_path.write_text(json.dumps(graph))

        output = tmp_path / "graph.html"
        generate_viz_html(index_path, output)

        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content

    def test_edges_with_missing_nodes_excluded(self, tmp_path: Path) -> None:
        """Edges referencing non-existent nodes are handled gracefully."""
        graph = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [
                {
                    "id": "A",
                    "type": "module",
                    "content": "",
                    "source_file": "",
                    "created": "",
                    "metadata": {},
                }
            ],
            "links": [{"source": "A", "target": "MISSING", "type": "related_to"}],
        }
        index_path = tmp_path / "index.json"
        index_path.write_text(json.dumps(graph))

        output = tmp_path / "graph.html"
        generate_viz_html(index_path, output)

        assert output.exists()
