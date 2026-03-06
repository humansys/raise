"""Tests for project detection module."""

from __future__ import annotations

from pathlib import Path

from raise_cli.onboarding.detection import (
    CODE_EXTENSIONS,
    LANGUAGE_TOOLCHAIN,
    ProjectType,
    ToolchainInfo,
    count_code_files,
    detect_language,
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


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_empty_directory_returns_none(self, tmp_path: Path) -> None:
        """No code files returns None."""
        result = detect_language(tmp_path)
        assert result is None

    def test_python_project(self, tmp_path: Path) -> None:
        """Detects Python as dominant language."""
        for i in range(5):
            (tmp_path / f"mod_{i}.py").write_text(f"# mod {i}")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "python"
        assert result.test_command == "uv run pytest --tb=short"
        assert result.lint_command == "uv run ruff check"
        assert result.type_check_command == "uv run pyright"

    def test_typescript_project(self, tmp_path: Path) -> None:
        """Detects TypeScript as dominant language."""
        for i in range(5):
            (tmp_path / f"component_{i}.tsx").write_text(f"// comp {i}")
        (tmp_path / "config.ts").write_text("// config")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "typescript"
        assert result.test_command == "npx vitest run"

    def test_csharp_project(self, tmp_path: Path) -> None:
        """Detects C# as dominant language."""
        for i in range(3):
            (tmp_path / f"Service{i}.cs").write_text(f"// svc {i}")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "csharp"
        assert result.test_command == "dotnet test --verbosity quiet"

    def test_go_project(self, tmp_path: Path) -> None:
        """Detects Go as dominant language."""
        (tmp_path / "main.go").write_text("package main")
        (tmp_path / "handler.go").write_text("package main")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "go"
        assert result.test_command == "go test ./..."

    def test_mixed_languages_picks_dominant(self, tmp_path: Path) -> None:
        """With mixed languages, picks the one with most files."""
        for i in range(5):
            (tmp_path / f"mod_{i}.py").write_text(f"# py {i}")
        (tmp_path / "config.ts").write_text("// ts")
        (tmp_path / "util.js").write_text("// js")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "python"

    def test_unknown_language_returns_no_toolchain(self, tmp_path: Path) -> None:
        """Language without toolchain entry returns ToolchainInfo with no commands."""
        for i in range(3):
            (tmp_path / f"mod_{i}.lua").write_text(f"-- lua {i}")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "lua"
        assert result.test_command is None
        assert result.lint_command is None

    def test_rust_project(self, tmp_path: Path) -> None:
        """Detects Rust as dominant language."""
        (tmp_path / "main.rs").write_text("fn main() {}")
        (tmp_path / "lib.rs").write_text("pub mod foo;")
        result = detect_language(tmp_path)
        assert result is not None
        assert result.language == "rust"
        assert result.test_command == "cargo test"


class TestDetectProjectTypeWithLanguage:
    """Tests for detect_project_type including language detection."""

    def test_greenfield_has_no_language(self, tmp_path: Path) -> None:
        """Greenfield project has no language detected."""
        result = detect_project_type(tmp_path)
        assert result.language is None
        assert result.toolchain is None

    def test_brownfield_detects_language(self, tmp_path: Path) -> None:
        """Brownfield project detects dominant language."""
        for i in range(3):
            (tmp_path / f"mod_{i}.py").write_text(f"# py {i}")
        result = detect_project_type(tmp_path)
        assert result.project_type == ProjectType.BROWNFIELD
        assert result.language == "python"
        assert result.toolchain is not None
        assert result.toolchain.test_command == "uv run pytest --tb=short"

    def test_brownfield_with_typescript(self, tmp_path: Path) -> None:
        """Brownfield TypeScript project gets correct toolchain."""
        (tmp_path / "app.ts").write_text("// app")
        (tmp_path / "index.tsx").write_text("// index")
        result = detect_project_type(tmp_path)
        assert result.language == "typescript"
        assert result.toolchain is not None
        assert result.toolchain.test_command == "npx vitest run"


class TestLanguageToolchain:
    """Tests for LANGUAGE_TOOLCHAIN mapping."""

    def test_has_core_languages(self) -> None:
        """Toolchain mapping includes core languages."""
        core = {"python", "typescript", "javascript", "csharp", "go", "php", "dart"}
        assert core.issubset(set(LANGUAGE_TOOLCHAIN.keys()))

    def test_all_entries_have_test_command(self) -> None:
        """Every toolchain entry has a test command."""
        for lang, info in LANGUAGE_TOOLCHAIN.items():
            assert info.test_command is not None, f"{lang} missing test_command"

    def test_toolchain_info_is_frozen(self) -> None:
        """ToolchainInfo is a frozen dataclass."""
        info = ToolchainInfo(language="test")
        assert info.language == "test"
        assert info.test_command is None
