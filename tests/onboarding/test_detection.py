"""Tests for project detection module."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.onboarding.detection import (
    CODE_EXTENSIONS,
    ProjectType,
    count_code_files,
    detect_project_type,
)


class TestProjectType:
    """Tests for ProjectType enum."""

    def test_project_type_values(self) -> None:
        """ProjectType has expected values."""
        assert ProjectType.GREENFIELD.value == "greenfield"
        assert ProjectType.BROWNFIELD.value == "brownfield"


class TestCountCodeFiles:
    """Tests for count_code_files function."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Empty directory returns 0."""
        assert count_code_files(tmp_path) == 0

    def test_no_code_files(self, tmp_path: Path) -> None:
        """Directory with non-code files returns 0."""
        (tmp_path / "README.md").write_text("# Hello")
        (tmp_path / "config.yaml").write_text("key: value")
        assert count_code_files(tmp_path) == 0

    def test_python_files(self, tmp_path: Path) -> None:
        """Counts Python files."""
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")
        assert count_code_files(tmp_path) == 2

    def test_nested_files(self, tmp_path: Path) -> None:
        """Counts files in subdirectories."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "app.py").write_text("# app")
        (src / "lib.py").write_text("# lib")
        (tmp_path / "main.py").write_text("# main")
        assert count_code_files(tmp_path) == 3

    def test_excludes_hidden_directories(self, tmp_path: Path) -> None:
        """Excludes files in hidden directories."""
        hidden = tmp_path / ".venv"
        hidden.mkdir()
        (hidden / "lib.py").write_text("# venv")
        (tmp_path / "main.py").write_text("# main")
        assert count_code_files(tmp_path) == 1

    def test_excludes_node_modules(self, tmp_path: Path) -> None:
        """Excludes node_modules directory."""
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "dep.js").write_text("// dep")
        (tmp_path / "app.js").write_text("// app")
        assert count_code_files(tmp_path) == 1

    def test_excludes_pycache(self, tmp_path: Path) -> None:
        """Excludes __pycache__ directory."""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "module.cpython-312.pyc").write_text("")
        (tmp_path / "module.py").write_text("# module")
        assert count_code_files(tmp_path) == 1

    def test_multiple_languages(self, tmp_path: Path) -> None:
        """Counts files from multiple languages."""
        (tmp_path / "app.py").write_text("# python")
        (tmp_path / "app.ts").write_text("// typescript")
        (tmp_path / "app.js").write_text("// javascript")
        (tmp_path / "App.java").write_text("// java")
        assert count_code_files(tmp_path) == 4


class TestDetectProjectType:
    """Tests for detect_project_type function."""

    def test_greenfield_empty(self, tmp_path: Path) -> None:
        """Empty directory is greenfield."""
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD
        assert result.code_file_count == 0

    def test_greenfield_only_docs(self, tmp_path: Path) -> None:
        """Directory with only docs is greenfield."""
        (tmp_path / "README.md").write_text("# Project")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text("Guide")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.GREENFIELD

    def test_brownfield_with_code(self, tmp_path: Path) -> None:
        """Directory with code files is brownfield."""
        (tmp_path / "main.py").write_text("print('hello')")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD
        assert result.code_file_count == 1

    def test_brownfield_many_files(self, tmp_path: Path) -> None:
        """Directory with many code files is brownfield."""
        for i in range(20):
            (tmp_path / f"module_{i}.py").write_text(f"# module {i}")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD
        assert result.code_file_count == 20


class TestCodeExtensions:
    """Tests for CODE_EXTENSIONS constant."""

    def test_includes_python(self) -> None:
        """Includes Python extension."""
        assert ".py" in CODE_EXTENSIONS

    def test_includes_typescript(self) -> None:
        """Includes TypeScript extensions."""
        assert ".ts" in CODE_EXTENSIONS
        assert ".tsx" in CODE_EXTENSIONS

    def test_includes_javascript(self) -> None:
        """Includes JavaScript extensions."""
        assert ".js" in CODE_EXTENSIONS
        assert ".jsx" in CODE_EXTENSIONS

    def test_includes_common_languages(self) -> None:
        """Includes other common language extensions."""
        common = {".java", ".go", ".rs", ".rb", ".c", ".cpp", ".cs"}
        assert common.issubset(CODE_EXTENSIONS)
