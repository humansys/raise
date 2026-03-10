"""Tests for --format agent in rai graph commands (S325.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _create_graph(tmp_path: Path) -> Path:
    """Create a graph index with diverse node types."""
    memory_dir = tmp_path / ".raise" / "rai" / "memory"
    memory_dir.mkdir(parents=True)

    graph_data: dict[str, Any] = {
        "nodes": [
            {
                "id": "mod-memory",
                "type": "module",
                "content": "Manage Rai's persistent memory",
                "source_file": "governance/architecture/modules/memory.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "bc-ontology",
                "type": "bounded_context",
                "content": "Persist and query accumulated knowledge",
                "source_file": "governance/architecture/domain-model.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "lyr-domain",
                "type": "layer",
                "content": "Domain layer",
                "source_file": "governance/architecture/system-design.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "guardrail-must-code-001",
                "type": "guardrail",
                "content": "[MUST] Type hints on all code",
                "source_file": "governance/guardrails.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "guardrail-should-test-001",
                "type": "guardrail",
                "content": "[SHOULD] Test edge cases",
                "source_file": "governance/guardrails.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "mod-context",
                "type": "module",
                "content": "Unified context graph",
                "source_file": "governance/architecture/modules/context.md",
                "created": "2026-02-08",
                "metadata": {},
            },
            {
                "id": "PAT-001",
                "type": "pattern",
                "content": "Singleton pattern with get/set for module state",
                "source_file": ".raise/rai/memory/patterns.jsonl",
                "created": "2026-01-31",
                "metadata": {},
            },
            {
                "id": "decision-adr-001",
                "type": "decision",
                "content": "Use Pydantic for all data models",
                "source_file": "governance/adrs/adr-001.md",
                "created": "2026-01-31",
                "metadata": {},
            },
        ],
        "edges": [
            {
                "source": "mod-memory",
                "target": "bc-ontology",
                "type": "belongs_to",
                "weight": 1.0,
            },
            {
                "source": "mod-memory",
                "target": "lyr-domain",
                "type": "in_layer",
                "weight": 1.0,
            },
            {
                "source": "bc-ontology",
                "target": "guardrail-must-code-001",
                "type": "constrained_by",
                "weight": 1.0,
            },
            {
                "source": "bc-ontology",
                "target": "guardrail-should-test-001",
                "type": "constrained_by",
                "weight": 1.0,
            },
            {
                "source": "mod-memory",
                "target": "mod-context",
                "type": "depends_on",
                "weight": 1.0,
            },
        ],
        "metadata": {"version": "1.0"},
    }

    index_path = memory_dir / "index.json"
    index_path.write_text(json.dumps(graph_data, indent=2))
    return index_path


class TestGraphQueryAgentFormat:
    """Tests for rai graph query --format agent."""

    def test_query_agent_pipe_delimited(self, tmp_path: Path) -> None:
        """Agent format produces type|id|content lines."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "memory",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        lines = [ln for ln in result.output.strip().split("\n") if "|" in ln]
        assert len(lines) >= 1
        # Each line: type|id|content
        parts = lines[0].split("|")
        assert len(parts) == 3

    def test_query_agent_no_markdown(self, tmp_path: Path) -> None:
        """Agent format has no markdown decorations."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "memory",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        assert "**" not in result.output
        assert "# " not in result.output
        assert "---" not in result.output

    def test_query_agent_no_truncation(self, tmp_path: Path) -> None:
        """Agent format does not truncate content."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "Singleton",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        assert "Singleton pattern with get/set for module state" in result.output

    def test_query_agent_empty(self, tmp_path: Path) -> None:
        """Agent format with no results produces empty output."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "xyznonexistent",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        # No pipe-delimited lines in output
        lines = [ln for ln in result.output.strip().split("\n") if "|" in ln]
        assert len(lines) == 0

    def test_query_compact_still_works(self, tmp_path: Path) -> None:
        """Compact format (backward compat) still works."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "memory",
                "--index",
                str(index_path),
                "--format",
                "compact",
            ],
        )
        assert result.exit_code == 0


class TestGraphContextAgentFormat:
    """Tests for rai graph context --format agent."""

    def test_context_agent_pipe_delimited(self, tmp_path: Path) -> None:
        """Agent format produces pipe-delimited lines for each section."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-memory",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        output = result.output.strip()
        lines = output.split("\n")
        # Must contain module, domain, layer, must, should, dependencies
        assert any(ln.startswith("module|") for ln in lines)
        assert any(ln.startswith("domain|") for ln in lines)
        assert any(ln.startswith("layer|") for ln in lines)
        assert any(ln.startswith("dependencies|") for ln in lines)

    def test_context_agent_constraints_by_severity(self, tmp_path: Path) -> None:
        """Agent format groups constraints by MUST/SHOULD."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-memory",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        output = result.output.strip()
        lines = output.split("\n")
        must_lines = [ln for ln in lines if ln.startswith("must|")]
        should_lines = [ln for ln in lines if ln.startswith("should|")]
        assert len(must_lines) == 1
        assert "guardrail-must-code-001" in must_lines[0]
        assert len(should_lines) == 1
        assert "guardrail-should-test-001" in should_lines[0]

    def test_context_agent_no_markup(self, tmp_path: Path) -> None:
        """Agent format has no Rich markup."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-memory",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        assert "[bold]" not in result.output
        assert "[cyan]" not in result.output

    def test_context_agent_not_found(self, tmp_path: Path) -> None:
        """Agent format for nonexistent module produces error."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-nonexistent",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        # Either exit code != 0, or error|message in output
        assert result.exit_code != 0 or "not found" in result.output.lower()

    def test_context_human_unchanged(self, tmp_path: Path) -> None:
        """Human format is unchanged (regression check)."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app, ["graph", "context", "mod-memory", "--index", str(index_path)]
        )
        assert result.exit_code == 0
        assert "Module:" in result.output
        assert "mod-memory" in result.output


class TestGraphListAgentFormat:
    """Tests for rai graph list --format agent."""

    def test_list_agent_type_summary(self, tmp_path: Path) -> None:
        """Agent format produces type|count summary."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app, ["graph", "list", "--index", str(index_path), "--format", "agent"]
        )
        assert result.exit_code == 0
        output = result.output.strip()
        lines = output.split("\n")
        # Should have type|count lines
        pipe_lines = [ln for ln in lines if "|" in ln]
        assert len(pipe_lines) >= 1
        # Check a known type
        assert any("module|2" in ln for ln in pipe_lines)
        assert any("guardrail|2" in ln for ln in pipe_lines)

    def test_list_agent_no_rich_table(self, tmp_path: Path) -> None:
        """Agent format has no Rich table decorations."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(
            app, ["graph", "list", "--index", str(index_path), "--format", "agent"]
        )
        assert result.exit_code == 0
        assert "┏" not in result.output
        assert "┃" not in result.output
        assert "Graph Concepts" not in result.output

    def test_list_table_format_unchanged(self, tmp_path: Path) -> None:
        """Table format (default) is unchanged."""
        index_path = _create_graph(tmp_path)
        result = runner.invoke(app, ["graph", "list", "--index", str(index_path)])
        assert result.exit_code == 0
        # Default is table format
        assert "Graph Concepts" in result.output or "mod-memory" in result.output


class TestGraphAgentPipeSanitization:
    """Tests for pipe character sanitization in agent format (QR-1)."""

    def test_query_pipe_in_content_sanitized(self, tmp_path: Path) -> None:
        """Pipe in concept content is replaced to preserve field boundaries."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)
        graph_data: dict[str, Any] = {
            "nodes": [
                {
                    "id": "PAT-PIPE",
                    "type": "pattern",
                    "content": "Use X | Y pattern for fallback",
                    "source_file": "test.md",
                    "created": "2026-01-31",
                    "metadata": {},
                },
            ],
            "edges": [],
            "metadata": {"version": "1.0"},
        }
        index_path = memory_dir / "index.json"
        index_path.write_text(json.dumps(graph_data, indent=2))

        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "fallback",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        lines = [ln for ln in result.output.strip().split("\n") if ln]
        assert len(lines) >= 1
        # Exactly 3 fields when split on pipe
        parts = lines[0].split("|")
        assert len(parts) == 3
        assert parts[0] == "pattern"
        assert parts[1] == "PAT-PIPE"


class TestGraphContextSeverityClassification:
    """Tests for ID-based constraint severity classification (QR-4)."""

    def test_context_agent_classifies_by_id_not_content(self, tmp_path: Path) -> None:
        """Constraints are classified by ID convention (-must-/-should-), not content."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)
        graph_data: dict[str, Any] = {
            "nodes": [
                {
                    "id": "mod-test",
                    "type": "module",
                    "content": "Test module",
                    "source_file": "test.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
                {
                    "id": "bc-test",
                    "type": "bounded_context",
                    "content": "Test domain",
                    "source_file": "test.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
                {
                    "id": "guardrail-must-tricky-001",
                    "type": "guardrail",
                    "content": "You SHOULD also consider this MUST rule",
                    "source_file": "test.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
            ],
            "edges": [
                {
                    "source": "mod-test",
                    "target": "bc-test",
                    "type": "belongs_to",
                    "weight": 1.0,
                },
                {
                    "source": "bc-test",
                    "target": "guardrail-must-tricky-001",
                    "type": "constrained_by",
                    "weight": 1.0,
                },
            ],
            "metadata": {"version": "1.0"},
        }
        index_path = memory_dir / "index.json"
        index_path.write_text(json.dumps(graph_data, indent=2))

        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-test",
                "--index",
                str(index_path),
                "--format",
                "agent",
            ],
        )
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        must_lines = [ln for ln in lines if ln.startswith("must|")]
        should_lines = [ln for ln in lines if ln.startswith("should|")]
        # ID has -must-, so classified as must despite content mentioning SHOULD
        assert len(must_lines) == 1
        assert "guardrail-must-tricky-001" in must_lines[0]
        assert len(should_lines) == 0
