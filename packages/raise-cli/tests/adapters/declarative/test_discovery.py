"""Tests for YAML adapter discovery.

Covers: S337.3 MUST-1 (discover_yaml_adapters returns factory closures),
        MUST-5 (malformed YAML skipped with warning).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def adapters_dir(tmp_path: Path) -> Path:
    """Create a .raise/adapters/ dir with test YAML files."""
    d = tmp_path / ".raise" / "adapters"
    d.mkdir(parents=True)
    return d


class TestDiscoverYamlAdapters:
    """discover_yaml_adapters() — scan YAML files and return factory closures."""

    def test_returns_pm_adapter_from_yaml(self, adapters_dir: Path) -> None:
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "minimal.yaml")
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert "minimal" in result

    def test_factory_closure_produces_adapter(self, adapters_dir: Path) -> None:
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "minimal.yaml")
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        adapter = result["minimal"]()
        from raise_cli.adapters.declarative.adapter import DeclarativeMcpAdapter

        assert isinstance(adapter, DeclarativeMcpAdapter)

    def test_filters_by_protocol(self, adapters_dir: Path) -> None:
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "minimal.yaml")
        shutil.copy(FIXTURES / "docs_adapter.yaml", adapters_dir / "wiki.yaml")
        pm_result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        docs_result = discover_yaml_adapters("docs", adapters_dir=adapters_dir)
        assert "minimal" in pm_result
        assert "wiki" not in pm_result
        assert "wiki" in docs_result
        assert "minimal" not in docs_result

    def test_malformed_yaml_skipped_with_warning(
        self, adapters_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        (adapters_dir / "bad.yaml").write_text("not: valid: yaml: {{{}}")
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "minimal.yaml")
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert "minimal" in result
        assert "bad" not in result
        assert any("bad.yaml" in r.message for r in caplog.records)

    def test_invalid_schema_skipped_with_warning(
        self, adapters_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        shutil.copy(
            FIXTURES / "invalid_missing_name.yaml",
            adapters_dir / "noname.yaml",
        )
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert "noname" not in result
        assert len(result) == 0
        assert any("noname.yaml" in r.message for r in caplog.records)

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "does_not_exist"
        result = discover_yaml_adapters("pm", adapters_dir=nonexistent)
        assert result == {}

    def test_empty_dir_returns_empty(self, adapters_dir: Path) -> None:
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert result == {}

    def test_duplicate_name_skipped_with_warning(
        self, adapters_dir: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "first.yaml")
        # Second file with same adapter.name = "minimal"
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "second.yaml")
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert "minimal" in result
        assert len(result) == 1
        assert any("already defined" in r.message for r in caplog.records)

    def test_multiple_yaml_files(self, adapters_dir: Path) -> None:
        shutil.copy(FIXTURES / "minimal.yaml", adapters_dir / "adapter1.yaml")
        # Create a second PM adapter with different name
        (adapters_dir / "adapter2.yaml").write_text(
            "adapter:\n  name: second\n  protocol: pm\n\n"
            "server:\n  command: echo\n  args: [test]\n\n"
            "methods:\n  search:\n    tool: test_search\n"
        )
        result = discover_yaml_adapters("pm", adapters_dir=adapters_dir)
        assert "minimal" in result
        assert "second" in result
        assert len(result) == 2
