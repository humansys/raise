"""Tests for PythonAnalyzer."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from raise_cli.context.analyzers.protocol import CodeAnalyzer
from raise_cli.context.analyzers.python import PythonAnalyzer


class TestPythonAnalyzerDetect:
    """Tests for PythonAnalyzer.detect()."""

    def test_detects_python_project_with_pyproject_toml(self, tmp_path: Path) -> None:
        """Should detect Python when pyproject.toml exists."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        analyzer = PythonAnalyzer(src_dir="src/pkg")
        assert analyzer.detect(tmp_path) is True

    def test_detects_python_project_with_setup_py(self, tmp_path: Path) -> None:
        """Should detect Python when setup.py exists."""
        (tmp_path / "setup.py").write_text("from setuptools import setup\n")
        analyzer = PythonAnalyzer(src_dir="src/pkg")
        assert analyzer.detect(tmp_path) is True

    def test_does_not_detect_without_python_markers(self, tmp_path: Path) -> None:
        """Should not detect Python without pyproject.toml or setup.py."""
        analyzer = PythonAnalyzer(src_dir="src/pkg")
        assert analyzer.detect(tmp_path) is False

    def test_implements_code_analyzer_protocol(self) -> None:
        """PythonAnalyzer should satisfy CodeAnalyzer Protocol."""
        analyzer = PythonAnalyzer(src_dir="src/pkg")
        assert isinstance(analyzer, CodeAnalyzer)


class TestPythonAnalyzerImports:
    """Tests for import extraction."""

    def _make_module(self, tmp_path: Path, module_name: str, code: str) -> Path:
        """Helper to create a module with given code."""
        src_dir = tmp_path / "src" / "pkg"
        mod_dir = src_dir / module_name
        mod_dir.mkdir(parents=True)
        (mod_dir / "__init__.py").write_text("")
        (mod_dir / "core.py").write_text(dedent(code))
        return src_dir

    def test_extracts_absolute_imports(self, tmp_path: Path) -> None:
        """Should extract absolute imports from the same package."""
        src_dir = tmp_path / "src" / "pkg"

        # Module 'alpha' imports from 'beta'
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text("from pkg.beta.utils import helper\n")

        beta = src_dir / "beta"
        beta.mkdir(parents=True)
        (beta / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert "beta" in alpha_info.imports

    def test_extracts_relative_imports(self, tmp_path: Path) -> None:
        """Should extract relative imports resolving to sibling modules."""
        src_dir = tmp_path / "src" / "pkg"

        # Module 'alpha' has relative import from sibling 'beta'
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text("from ..beta import something\n")

        beta = src_dir / "beta"
        beta.mkdir(parents=True)
        (beta / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert "beta" in alpha_info.imports

    def test_skips_type_checking_imports(self, tmp_path: Path) -> None:
        """Should NOT include imports inside TYPE_CHECKING blocks."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text(
            dedent("""\
            from __future__ import annotations
            from typing import TYPE_CHECKING

            from pkg.beta import real_thing

            if TYPE_CHECKING:
                from pkg.gamma import TypeOnly
            """)
        )

        for name in ["beta", "gamma"]:
            mod = src_dir / name
            mod.mkdir(parents=True)
            (mod / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert "beta" in alpha_info.imports
        assert "gamma" not in alpha_info.imports

    def test_includes_try_except_imports(self, tmp_path: Path) -> None:
        """Should include imports inside try/except blocks (runtime deps)."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text(
            dedent("""\
            try:
                from pkg.beta import fast_impl
            except ImportError:
                from pkg.gamma import slow_impl
            """)
        )

        for name in ["beta", "gamma"]:
            mod = src_dir / name
            mod.mkdir(parents=True)
            (mod / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert "beta" in alpha_info.imports
        assert "gamma" in alpha_info.imports

    def test_skips_stdlib_imports(self, tmp_path: Path) -> None:
        """Should not include stdlib or external package imports."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text(
            dedent("""\
            import json
            from pathlib import Path
            from pydantic import BaseModel
            """)
        )

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert alpha_info.imports == []

    def test_deduplicates_imports(self, tmp_path: Path) -> None:
        """Should not list the same import module twice."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "a.py").write_text("from pkg.beta import foo\n")
        (alpha / "b.py").write_text("from pkg.beta import bar\n")

        beta = src_dir / "beta"
        beta.mkdir(parents=True)
        (beta / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert alpha_info.imports == ["beta"]

    def test_excludes_self_imports(self, tmp_path: Path) -> None:
        """Should not include self-references in imports."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text("from pkg.alpha.utils import helper\n")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert "alpha" not in alpha_info.imports


class TestPythonAnalyzerExports:
    """Tests for export extraction from __init__.py."""

    def test_extracts_all_exports(self, tmp_path: Path) -> None:
        """Should extract names from __all__ list."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text(
            dedent("""\
            from pkg.alpha.core import Foo, Bar

            __all__ = ["Foo", "Bar"]
            """)
        )

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert sorted(alpha_info.exports) == ["Bar", "Foo"]

    def test_extracts_imports_as_exports_when_no_all(self, tmp_path: Path) -> None:
        """When no __all__, should extract import names from __init__.py."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text(
            dedent("""\
            from pkg.alpha.core import Foo
            from pkg.alpha.utils import helper
            """)
        )

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert sorted(alpha_info.exports) == ["Foo", "helper"]

    def test_empty_init_means_no_exports(self, tmp_path: Path) -> None:
        """Empty __init__.py should produce no exports."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert alpha_info.exports == []


class TestPythonAnalyzerComponents:
    """Tests for component counting."""

    def test_counts_classes_and_functions(self, tmp_path: Path) -> None:
        """Should count top-level classes and functions across all .py files."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "models.py").write_text(
            dedent("""\
            class Foo:
                pass

            class Bar:
                pass
            """)
        )
        (alpha / "utils.py").write_text(
            dedent("""\
            def helper():
                pass

            def another():
                pass
            """)
        )

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        assert alpha_info.component_count == 4

    def test_does_not_count_nested_functions(self, tmp_path: Path) -> None:
        """Should only count top-level definitions, not nested."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "main.py").write_text(
            dedent("""\
            def outer():
                def inner():
                    pass
                return inner

            class Outer:
                def method(self):
                    pass
            """)
        )

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None
        # outer + Outer = 2 (inner and method are not top-level)
        assert alpha_info.component_count == 2


class TestPythonAnalyzerModuleDiscovery:
    """Tests for module directory detection."""

    def test_discovers_all_module_directories(self, tmp_path: Path) -> None:
        """Should find all directories with __init__.py under src_dir."""
        src_dir = tmp_path / "src" / "pkg"
        for name in ["alpha", "beta", "gamma"]:
            mod = src_dir / name
            mod.mkdir(parents=True)
            (mod / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        names = sorted(m.name for m in modules)
        assert names == ["alpha", "beta", "gamma"]

    def test_skips_pycache_and_non_package_dirs(self, tmp_path: Path) -> None:
        """Should skip __pycache__ and dirs without __init__.py."""
        src_dir = tmp_path / "src" / "pkg"

        # Valid module
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")

        # __pycache__ — skip
        pycache = src_dir / "__pycache__"
        pycache.mkdir(parents=True)

        # Dir without __init__.py — skip
        data = src_dir / "data"
        data.mkdir(parents=True)
        (data / "readme.txt").write_text("not a package")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        names = [m.name for m in modules]
        assert names == ["alpha"]

    def test_sets_language_to_python(self, tmp_path: Path) -> None:
        """All modules should have language='python'."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules[0].language == "python"

    def test_sets_source_path(self, tmp_path: Path) -> None:
        """source_path should be relative path to the module dir."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules[0].source_path == "src/pkg/alpha"

    def test_handles_no_modules(self, tmp_path: Path) -> None:
        """Should return empty list when src_dir has no subdirs."""
        src_dir = tmp_path / "src" / "pkg"
        src_dir.mkdir(parents=True)

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules == []

    def test_handles_missing_src_dir(self, tmp_path: Path) -> None:
        """Should return empty list when src_dir doesn't exist."""
        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        assert modules == []

    def test_handles_unparseable_files(self, tmp_path: Path) -> None:
        """Should gracefully handle Python files with syntax errors."""
        src_dir = tmp_path / "src" / "pkg"
        alpha = src_dir / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "__init__.py").write_text("")
        (alpha / "broken.py").write_text("def broken(\n")  # syntax error

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)

        # Should still produce a result, just with partial data
        alpha_info = next((m for m in modules if m.name == "alpha"), None)
        assert alpha_info is not None

    def test_imports_extracted_from_init_and_regular_files(
        self, tmp_path: Path
    ) -> None:
        """Imports from __init__.py and regular files both contribute (RAISE-535)."""
        pkg = tmp_path / "src" / "pkg"
        mod = pkg / "mymod"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text("from pkg.alpha import Foo\n")
        (mod / "core.py").write_text("from pkg.beta import Bar\n")

        # sibling modules so imports resolve
        for name in ("alpha", "beta"):
            d = pkg / name
            d.mkdir()
            (d / "__init__.py").write_text("")

        analyzer = PythonAnalyzer(src_dir="src/pkg")
        modules = analyzer.analyze_modules(tmp_path)
        mymod = next((m for m in modules if m.name == "mymod"), None)
        assert mymod is not None
        # Both __init__.py and core.py imports must appear
        assert "alpha" in mymod.imports
        assert "beta" in mymod.imports
