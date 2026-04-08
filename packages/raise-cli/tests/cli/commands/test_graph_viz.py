"""Tests for `rai memory viz` CLI command."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def graph_project(tmp_path: Path) -> Path:
    """Create a tmp project with a valid memory index."""
    memory_dir = tmp_path / ".raise" / "rai" / "memory"
    memory_dir.mkdir(parents=True)

    graph = {
        "directed": True,
        "multigraph": True,
        "graph": {},
        "nodes": [
            {
                "id": "PAT-001",
                "type": "pattern",
                "content": "Test pattern",
                "source_file": "patterns.jsonl",
                "created": "2026-01-01",
                "metadata": {"context": ["testing"]},
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
    index_path = memory_dir / "index.json"
    index_path.write_text(json.dumps(graph))
    return tmp_path


class TestGraphVizCommand:
    """Tests for `rai memory viz` CLI command."""

    def test_viz_no_graph(self, tmp_path: Path) -> None:
        """Fails with exit code 4 when no index exists."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["graph", "viz", "--no-open"])

            assert result.exit_code == 4
            assert "index not found" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_viz_generates_html(self, graph_project: Path) -> None:
        """Generates HTML file at default location."""
        original_cwd = os.getcwd()
        try:
            os.chdir(graph_project)
            result = runner.invoke(app, ["graph", "viz", "--no-open"])

            assert result.exit_code == 0
            assert "Written to" in result.output

            default_output = graph_project / ".raise" / "rai" / "memory" / "graph.html"
            assert default_output.exists()
            content = default_output.read_text(encoding="utf-8")
            assert "<!DOCTYPE html>" in content
            assert "PAT-001" in content
        finally:
            os.chdir(original_cwd)

    def test_viz_custom_output(self, graph_project: Path) -> None:
        """Generates HTML at custom output path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(graph_project)
            output = graph_project / "custom" / "viz.html"
            result = runner.invoke(
                app, ["graph", "viz", "--no-open", "--output", str(output)]
            )

            assert result.exit_code == 0
            assert output.exists()
        finally:
            os.chdir(original_cwd)

    def test_viz_custom_index(self, graph_project: Path) -> None:
        """Reads from custom index path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(graph_project)
            index = graph_project / ".raise" / "rai" / "memory" / "index.json"
            output = graph_project / "out.html"
            result = runner.invoke(
                app,
                [
                    "memory",
                    "viz",
                    "--no-open",
                    "--index",
                    str(index),
                    "--output",
                    str(output),
                ],
            )

            assert result.exit_code == 0
            assert output.exists()
        finally:
            os.chdir(original_cwd)
