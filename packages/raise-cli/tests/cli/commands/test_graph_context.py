"""Tests for `raise memory context` CLI command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _create_arch_graph(tmp_path: Path) -> Path:
    """Create a graph with architectural structure for CLI testing."""
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
                "content": "Persist, integrate, and query accumulated knowledge",
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
                "id": "mod-context",
                "type": "module",
                "content": "Unified context graph",
                "source_file": "governance/architecture/modules/context.md",
                "created": "2026-02-08",
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


class TestGraphContextCommand:
    """Tests for `raise memory context` command."""

    def test_context_human_output(self, tmp_path: Path) -> None:
        """Human output shows module, domain, layer, constraints."""
        index_path = _create_arch_graph(tmp_path)
        result = runner.invoke(
            app, ["graph", "context", "mod-memory", "--index", str(index_path)]
        )
        assert result.exit_code == 0
        assert "mod-memory" in result.output
        assert "bc-ontology" in result.output
        assert "lyr-domain" in result.output
        assert "guardrail-must-code-001" in result.output

    def test_context_json_output(self, tmp_path: Path) -> None:
        """JSON output is valid and contains all fields."""
        index_path = _create_arch_graph(tmp_path)
        result = runner.invoke(
            app,
            [
                "graph",
                "context",
                "mod-memory",
                "--index",
                str(index_path),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["module"]["id"] == "mod-memory"
        assert data["domain"]["id"] == "bc-ontology"
        assert data["layer"]["id"] == "lyr-domain"
        assert len(data["constraints"]) == 1
        assert len(data["dependencies"]) == 1

    def test_context_nonexistent_module(self, tmp_path: Path) -> None:
        """Non-existent module shows error message."""
        index_path = _create_arch_graph(tmp_path)
        result = runner.invoke(
            app,
            ["graph", "context", "mod-nonexistent", "--index", str(index_path)],
        )
        assert result.exit_code != 0 or "not found" in result.output.lower()

    def test_context_no_index(self, tmp_path: Path) -> None:
        """Missing index file shows helpful error."""
        result = runner.invoke(
            app,
            [
                "memory",
                "context",
                "mod-memory",
                "--index",
                str(tmp_path / "nonexistent.json"),
            ],
        )
        assert result.exit_code != 0
