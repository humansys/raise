"""Tests for discover analyze CLI command."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _scan_result_json(tmp_path: Path) -> Path:
    """Create a minimal scan result JSON file."""
    data = {
        "files_scanned": 1,
        "symbols": [
            {
                "name": "MyClass",
                "kind": "class",
                "file": "src/service/handler.py",
                "line": 10,
                "signature": "class MyClass(BaseModel)",
                "docstring": "A class that handles service requests.",
                "parent": None,
            },
            {
                "name": "process",
                "kind": "method",
                "file": "src/service/handler.py",
                "line": 20,
                "signature": "def process(self, data: dict) -> bool",
                "docstring": "Process incoming data.",
                "parent": "MyClass",
            },
            {
                "name": "helper",
                "kind": "function",
                "file": "src/service/handler.py",
                "line": 30,
                "signature": "def helper(x: int) -> str",
                "docstring": None,
                "parent": None,
            },
        ],
        "errors": [],
    }
    path = tmp_path / "scan-result.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestDiscoverAnalyze:
    """Tests for discover analyze command."""

    def test_analyze_from_file_human(self, tmp_path: Path) -> None:
        """Should analyze scan result and output human format."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "human"],
        )
        assert result.exit_code == 0
        assert "Discovery Analysis" in result.output
        assert "Confidence Distribution" in result.output
        assert "Module Groups" in result.output

    def test_analyze_from_file_json(self, tmp_path: Path) -> None:
        """Should output valid JSON."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "scan_summary" in data
        assert "confidence_distribution" in data
        assert "components" in data
        assert "module_groups" in data

    def test_analyze_from_file_summary(self, tmp_path: Path) -> None:
        """Should output summary format."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "summary"],
        )
        assert result.exit_code == 0
        assert "Discovery Analysis Summary" in result.output
        assert "High confidence" in result.output
        assert "Module groups" in result.output

    def test_analyze_missing_input_file(self) -> None:
        """Should error on missing input file."""
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", "/nonexistent/file.json"],
        )
        assert result.exit_code != 0

    def test_analyze_invalid_json(self, tmp_path: Path) -> None:
        """Should error on invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json at all", encoding="utf-8")
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(bad_file)],
        )
        assert result.exit_code != 0

    def test_analyze_saves_analysis_json(
        self, tmp_path: Path, monkeypatch: object
    ) -> None:
        """Should save analysis.json to work/discovery/."""
        scan_file = _scan_result_json(tmp_path)
        # Change to tmp_path so analysis.json is saved there
        import os

        monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))  # type: ignore[attr-defined]
        monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]

        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "summary"],
        )
        assert result.exit_code == 0
        analysis_path = tmp_path / "work" / "discovery" / "analysis.json"
        assert analysis_path.exists()
        data = json.loads(analysis_path.read_text(encoding="utf-8"))
        assert "components" in data

    def test_analyze_method_folding(self, tmp_path: Path) -> None:
        """Methods should be folded into parent class."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        # MyClass + helper = 2 components (process method folded into MyClass)
        assert len(data["components"]) == 2
        my_class = next(c for c in data["components"] if c["name"] == "MyClass")
        assert "process" in my_class["methods"]

    def test_analyze_confidence_scoring(self, tmp_path: Path) -> None:
        """Components should have confidence scores."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        for comp in data["components"]:
            assert "confidence" in comp
            assert comp["confidence"]["score"] >= 0
            assert comp["confidence"]["tier"] in ("high", "medium", "low")

    def test_analyze_empty_scan_json(self, tmp_path: Path) -> None:
        """Should handle empty scan result in JSON format."""
        empty = tmp_path / "empty.json"
        empty.write_text(
            json.dumps({"files_scanned": 0, "symbols": [], "errors": []}),
            encoding="utf-8",
        )
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(empty), "--output", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["components"] == []

    def test_analyze_empty_scan_human(self, tmp_path: Path) -> None:
        """Should show 'no components' message for empty scan in human format."""
        empty = tmp_path / "empty.json"
        empty.write_text(
            json.dumps({"files_scanned": 0, "symbols": [], "errors": []}),
            encoding="utf-8",
        )
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(empty), "--output", "human"],
        )
        assert result.exit_code == 0
        assert "No components to analyze" in result.output

    def test_analyze_category_breakdown(self, tmp_path: Path) -> None:
        """Human output should show category breakdown."""
        scan_file = _scan_result_json(tmp_path)
        result = runner.invoke(
            app,
            ["discover", "analyze", "--input", str(scan_file), "--output", "human"],
        )
        assert result.exit_code == 0
        assert "Category Breakdown" in result.output
