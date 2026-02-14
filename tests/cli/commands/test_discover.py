"""Tests for discover CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from typer.testing import CliRunner

from rai_cli.cli.main import app

runner = CliRunner()


class TestDiscoverScan:
    """Tests for discover scan command."""

    def test_scan_python_directory(self, tmp_path: Path) -> None:
        """Should scan Python files and output symbols."""
        # Create a simple Python file
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "example.py").write_text(
            dedent("""\
            '''Module docstring.'''

            class MyClass:
                '''A test class.'''
                def my_method(self):
                    pass

            def my_function():
                pass
        """)
        )

        result = runner.invoke(
            app, ["discover", "scan", str(src_dir), "--output", "summary"]
        )

        assert result.exit_code == 0
        assert "Scan Summary" in result.output
        assert "Classes: 1" in result.output
        assert "Functions: 1" in result.output
        assert "Methods: 1" in result.output

    def test_scan_json_output(self, tmp_path: Path) -> None:
        """Should output JSON when requested."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "example.py").write_text("class Foo: pass")

        result = runner.invoke(
            app, ["discover", "scan", str(src_dir), "--output", "json"]
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert "symbols" in output
        assert "files_scanned" in output
        assert output["files_scanned"] == 1

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Should handle empty directories gracefully."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = runner.invoke(
            app, ["discover", "scan", str(empty_dir), "--output", "summary"]
        )

        assert result.exit_code == 0
        assert "Symbols found: 0" in result.output

    def test_scan_invalid_language(self, tmp_path: Path) -> None:
        """Should error on invalid language."""
        result = runner.invoke(
            app, ["discover", "scan", str(tmp_path), "--language", "rust"]
        )

        assert result.exit_code == 7  # ValidationError
        assert "Unsupported language" in result.output


class TestDiscoverBuild:
    """Tests for discover build command."""

    def test_build_creates_graph(self, tmp_path: Path) -> None:
        """Should create unified graph from validated components."""
        # Create discovery directory with validated components
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "source_file": "work/discovery/components-draft.yaml",
                    "component_count": 1,
                    "components": [
                        {
                            "id": "comp-test-class",
                            "type": "component",
                            "content": "A test class for validation",
                            "source_file": "src/test.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "TestClass",
                                "kind": "class",
                                "line": 10,
                                "category": "model",
                            },
                        },
                    ],
                }
            )
        )

        result = runner.invoke(
            app,
            [
                "discover",
                "build",
                "--project-root",
                str(tmp_path),
                "--output",
                "summary",
            ],
        )

        assert result.exit_code == 0
        assert "Components loaded: 1" in result.output
        assert "Total nodes:" in result.output

        # Verify graph file was created
        graph_file = tmp_path / ".raise" / "graph" / "unified.json"
        assert graph_file.exists()

    def test_build_json_output(self, tmp_path: Path) -> None:
        """Should output JSON when requested."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-test",
                            "type": "component",
                            "content": "Test",
                            "source_file": "src/test.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {},
                        },
                    ],
                }
            )
        )

        result = runner.invoke(
            app,
            ["discover", "build", "--project-root", str(tmp_path), "--output", "json"],
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "success"
        assert output["components_loaded"] == 1
        assert "total_nodes" in output

    def test_build_errors_on_missing_file(self, tmp_path: Path) -> None:
        """Should error when components file doesn't exist."""
        result = runner.invoke(
            app,
            ["discover", "build", "--project-root", str(tmp_path)],
        )

        assert result.exit_code == 4  # ArtifactNotFoundError
        assert "Components file not found" in result.output

    def test_build_errors_on_empty_components(self, tmp_path: Path) -> None:
        """Should error when no components in file."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [],
                }
            )
        )

        result = runner.invoke(
            app,
            ["discover", "build", "--project-root", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "No components found" in result.output

    def test_build_custom_input_file(self, tmp_path: Path) -> None:
        """Should accept custom input file path."""
        # Note: The builder loads from work/discovery/components-validated.json
        # even with custom --input, because build() always checks that path.
        # The --input validates the file exists and has components, but the
        # actual loading happens via load_components() which uses the standard path.
        # For this test, we put the file in both places.
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        component_data = json.dumps(
            {
                "generated_at": "2026-02-04T12:10:00Z",
                "components": [
                    {
                        "id": "comp-custom",
                        "type": "component",
                        "content": "Custom component",
                        "source_file": "src/custom.py",
                        "created": "2026-02-04T12:10:00Z",
                        "metadata": {"name": "Custom"},
                    },
                ],
            }
        )

        # Create custom file and standard file
        custom_file = tmp_path / "custom-components.json"
        custom_file.write_text(component_data)
        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(component_data)

        result = runner.invoke(
            app,
            [
                "discover",
                "build",
                "--input",
                str(custom_file),
                "--project-root",
                str(tmp_path),
                "--output",
                "summary",
            ],
        )

        assert result.exit_code == 0
        assert "Components loaded: 1" in result.output

    def test_build_human_output_shows_categories(self, tmp_path: Path) -> None:
        """Should show category breakdown in human output."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-model",
                            "type": "component",
                            "content": "A model class",
                            "source_file": "src/model.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "Model",
                                "kind": "class",
                                "category": "model",
                            },
                        },
                        {
                            "id": "comp-service",
                            "type": "component",
                            "content": "A service class",
                            "source_file": "src/service.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "Service",
                                "kind": "class",
                                "category": "service",
                            },
                        },
                    ],
                }
            )
        )

        result = runner.invoke(
            app,
            ["discover", "build", "--project-root", str(tmp_path), "--output", "human"],
        )

        assert result.exit_code == 0
        assert "By Category:" in result.output
        assert "model: 1" in result.output
        assert "service: 1" in result.output


class TestDiscoverDrift:
    """Tests for discover drift command."""

    def test_drift_no_baseline_exits_gracefully(self, tmp_path: Path) -> None:
        """Should exit with info when no baseline exists."""
        result = runner.invoke(
            app,
            ["discover", "drift", "--project-root", str(tmp_path)],
        )

        # No baseline = exit 0 with info message
        assert result.exit_code == 0
        assert (
            "No baseline" in result.output or "no components" in result.output.lower()
        )

    def test_drift_no_warnings(self, tmp_path: Path) -> None:
        """Should exit 0 when no drift detected."""
        # Create baseline with a class in discovery/
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-symbol",
                            "type": "component",
                            "content": "A symbol class.",
                            "source_file": "src/discovery/scanner.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "Symbol",
                                "kind": "class",
                                "line": 10,
                            },
                        },
                    ],
                }
            )
        )

        # Create source file that follows convention
        src_dir = tmp_path / "src" / "discovery"
        src_dir.mkdir(parents=True)
        (src_dir / "scanner.py").write_text(
            dedent("""\
            '''Scanner module.'''
            class Symbol:
                '''A symbol.'''
                pass
        """)
        )

        result = runner.invoke(
            app,
            ["discover", "drift", "--project-root", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "No drift" in result.output or "0 warnings" in result.output.lower()

    def test_drift_detects_location_drift(self, tmp_path: Path) -> None:
        """Should detect files in unexpected locations."""
        # Baseline: classes in src/discovery/
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-symbol",
                            "type": "component",
                            "content": "A model in discovery.",
                            "source_file": "src/discovery/scanner.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {
                                "name": "Symbol",
                                "kind": "class",
                            },
                        },
                    ],
                }
            )
        )

        # Create file in WRONG location (src/cli/ instead of src/discovery/)
        wrong_dir = tmp_path / "src" / "cli"
        wrong_dir.mkdir(parents=True)
        (wrong_dir / "wrong_place.py").write_text(
            dedent("""\
            '''Wrong module.'''
            class WrongClass:
                '''This class is in the wrong place.'''
                pass
        """)
        )

        result = runner.invoke(
            app,
            ["discover", "drift", "--project-root", str(tmp_path)],
        )

        # Should detect drift and exit with warning code
        assert result.exit_code == 1
        assert "drift" in result.output.lower() or "warning" in result.output.lower()

    def test_drift_json_output(self, tmp_path: Path) -> None:
        """Should output JSON when requested."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-1",
                            "type": "component",
                            "content": "Test component.",
                            "source_file": "src/module/test.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {"name": "Test", "kind": "class"},
                        },
                    ],
                }
            )
        )

        # Create matching source
        src_dir = tmp_path / "src" / "module"
        src_dir.mkdir(parents=True)
        (src_dir / "test.py").write_text("class Test:\n    '''Test.'''\n    pass\n")

        result = runner.invoke(
            app,
            ["discover", "drift", "--project-root", str(tmp_path), "--output", "json"],
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert "warnings" in output
        assert "warning_count" in output

    def test_drift_summary_output(self, tmp_path: Path) -> None:
        """Should show summary when requested."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": "comp-1",
                            "type": "component",
                            "content": "Test component.",
                            "source_file": "src/module/test.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {"name": "Test", "kind": "class"},
                        },
                    ],
                }
            )
        )

        # Create matching source
        src_dir = tmp_path / "src" / "module"
        src_dir.mkdir(parents=True)
        (src_dir / "test.py").write_text("class Test:\n    '''Test.'''\n    pass\n")

        result = runner.invoke(
            app,
            [
                "discover",
                "drift",
                "--project-root",
                str(tmp_path),
                "--output",
                "summary",
            ],
        )

        assert result.exit_code == 0
        assert "Drift" in result.output or "Summary" in result.output

    def test_drift_warns_on_small_baseline(self, tmp_path: Path) -> None:
        """Should warn when baseline has fewer than 10 components."""
        discovery_dir = tmp_path / "work" / "discovery"
        discovery_dir.mkdir(parents=True)

        # Create baseline with only 3 components (below threshold of 10)
        validated_file = discovery_dir / "components-validated.json"
        validated_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-02-04T12:10:00Z",
                    "components": [
                        {
                            "id": f"comp-{i}",
                            "type": "component",
                            "content": f"Component {i}",
                            "source_file": f"src/module/comp{i}.py",
                            "created": "2026-02-04T12:10:00Z",
                            "metadata": {"name": f"Comp{i}", "kind": "class"},
                        }
                        for i in range(3)  # Only 3 components
                    ],
                }
            )
        )

        # Create matching source
        src_dir = tmp_path / "src" / "module"
        src_dir.mkdir(parents=True)
        for i in range(3):
            (src_dir / f"comp{i}.py").write_text(
                f"class Comp{i}:\n    '''Component {i}.'''\n    pass\n"
            )

        result = runner.invoke(
            app,
            ["discover", "drift", "--project-root", str(tmp_path)],
        )

        # Should show warning about small baseline
        assert "only 3 component" in result.output.lower()
        assert "10+" in result.output or "10 " in result.output
