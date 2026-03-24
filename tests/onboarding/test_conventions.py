"""Tests for convention detection."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from raise_cli.onboarding.conventions import (
    Confidence,
    ConventionResult,
    IndentationConvention,
    LineLengthConvention,
    NamingConvention,
    NamingConventions,
    QuoteConvention,
    StructureConventions,
    StyleConventions,
    calculate_confidence,
    classify_name,
    collect_python_files,
    detect_conventions,
    detect_indentation,
    detect_line_length,
    detect_naming,
    detect_quotes,
    detect_structure,
)


class TestSchemas:
    """Test that all convention schemas can be instantiated."""

    def test_confidence_enum_values(self) -> None:
        """Confidence enum has expected values."""
        assert Confidence.HIGH == "high"
        assert Confidence.MEDIUM == "medium"
        assert Confidence.LOW == "low"

    def test_indentation_convention_spaces(self) -> None:
        """IndentationConvention can represent spaces."""
        conv = IndentationConvention(
            style="spaces",
            width=4,
            confidence=Confidence.HIGH,
            sample_count=50,
            consistent_count=48,
        )
        assert conv.style == "spaces"
        assert conv.width == 4
        assert conv.confidence == Confidence.HIGH

    def test_indentation_convention_tabs(self) -> None:
        """IndentationConvention can represent tabs (no width)."""
        conv = IndentationConvention(
            style="tabs",
            width=None,
            confidence=Confidence.MEDIUM,
            sample_count=10,
            consistent_count=8,
        )
        assert conv.style == "tabs"
        assert conv.width is None

    def test_quote_convention(self) -> None:
        """QuoteConvention can be instantiated."""
        conv = QuoteConvention(
            style="double",
            confidence=Confidence.HIGH,
            sample_count=100,
            consistent_count=95,
        )
        assert conv.style == "double"

    def test_line_length_convention(self) -> None:
        """LineLengthConvention can be instantiated."""
        conv = LineLengthConvention(
            max_length=88,
            confidence=Confidence.MEDIUM,
            sample_count=1000,
        )
        assert conv.max_length == 88

    def test_naming_convention(self) -> None:
        """NamingConvention can represent different patterns."""
        snake = NamingConvention(
            pattern="snake_case",
            confidence=Confidence.HIGH,
            sample_count=50,
            consistent_count=48,
        )
        pascal = NamingConvention(
            pattern="PascalCase",
            confidence=Confidence.HIGH,
            sample_count=20,
            consistent_count=20,
        )
        assert snake.pattern == "snake_case"
        assert pascal.pattern == "PascalCase"

    def test_structure_conventions(self) -> None:
        """StructureConventions can be instantiated."""
        struct = StructureConventions(
            source_dir="src/mypackage",
            test_dir="tests",
            has_src_layout=True,
            common_patterns=["cli/commands/", "schemas/"],
        )
        assert struct.source_dir == "src/mypackage"
        assert struct.has_src_layout is True
        assert len(struct.common_patterns) == 2

    def test_structure_conventions_defaults(self) -> None:
        """StructureConventions has sensible defaults."""
        struct = StructureConventions()
        assert struct.source_dir is None
        assert struct.test_dir is None
        assert struct.has_src_layout is False
        assert struct.common_patterns == []

    def test_convention_result_full(self) -> None:
        """ConventionResult can hold all convention types."""
        result = ConventionResult(
            style=StyleConventions(
                indentation=IndentationConvention(
                    style="spaces",
                    width=4,
                    confidence=Confidence.HIGH,
                    sample_count=47,
                    consistent_count=45,
                ),
                quote_style=QuoteConvention(
                    style="double",
                    confidence=Confidence.HIGH,
                    sample_count=200,
                    consistent_count=190,
                ),
                line_length=LineLengthConvention(
                    max_length=88,
                    confidence=Confidence.MEDIUM,
                    sample_count=5000,
                ),
            ),
            naming=NamingConventions(
                functions=NamingConvention(
                    pattern="snake_case",
                    confidence=Confidence.HIGH,
                    sample_count=156,
                    consistent_count=152,
                ),
                classes=NamingConvention(
                    pattern="PascalCase",
                    confidence=Confidence.HIGH,
                    sample_count=23,
                    consistent_count=23,
                ),
                constants=NamingConvention(
                    pattern="UPPER_SNAKE_CASE",
                    confidence=Confidence.MEDIUM,
                    sample_count=8,
                    consistent_count=6,
                ),
            ),
            structure=StructureConventions(
                source_dir="src/raise_cli",
                test_dir="tests",
                has_src_layout=True,
                common_patterns=["schemas/", "cli/commands/"],
            ),
            overall_confidence=Confidence.HIGH,
            files_analyzed=47,
            analysis_time_ms=234,
        )
        assert result.overall_confidence == Confidence.HIGH
        assert result.files_analyzed == 47
        assert result.style.indentation.width == 4
        assert result.naming.functions.pattern == "snake_case"


class TestConfidenceCalculation:
    """Test confidence calculation logic."""

    def test_less_than_5_samples_is_low(self) -> None:
        """<5 samples always returns LOW regardless of consistency."""
        # 4 samples, 100% consistent -> still LOW
        assert calculate_confidence(4, 4) == Confidence.LOW
        # 3 samples, 100% consistent -> still LOW
        assert calculate_confidence(3, 3) == Confidence.LOW
        # 1 sample
        assert calculate_confidence(1, 1) == Confidence.LOW
        # 0 samples
        assert calculate_confidence(0, 0) == Confidence.LOW

    def test_5_to_10_samples_capped_at_medium(self) -> None:
        """5-10 samples caps at MEDIUM even with 100% consistency."""
        # 5 samples, 100% consistent -> MEDIUM (not HIGH)
        assert calculate_confidence(5, 5) == Confidence.MEDIUM
        # 10 samples, 100% consistent -> MEDIUM (not HIGH)
        assert calculate_confidence(10, 10) == Confidence.MEDIUM
        # 7 samples, 100% consistent -> MEDIUM
        assert calculate_confidence(7, 7) == Confidence.MEDIUM

    def test_5_to_10_samples_low_consistency_is_low(self) -> None:
        """5-10 samples with <70% consistency is LOW."""
        # 5 samples, 60% consistent -> LOW
        assert calculate_confidence(3, 5) == Confidence.LOW
        # 10 samples, 50% consistent -> LOW
        assert calculate_confidence(5, 10) == Confidence.LOW

    def test_more_than_10_samples_high_consistency(self) -> None:
        """>10 samples with >90% consistency is HIGH."""
        # 11 samples, 100% consistent -> HIGH
        assert calculate_confidence(11, 11) == Confidence.HIGH
        # 20 samples, 95% consistent -> HIGH
        assert calculate_confidence(19, 20) == Confidence.HIGH
        # 100 samples, 91% consistent -> HIGH
        assert calculate_confidence(91, 100) == Confidence.HIGH

    def test_more_than_10_samples_medium_consistency(self) -> None:
        """>10 samples with 70-90% consistency is MEDIUM."""
        # 20 samples, 80% consistent -> MEDIUM
        assert calculate_confidence(16, 20) == Confidence.MEDIUM
        # 100 samples, 75% consistent -> MEDIUM
        assert calculate_confidence(75, 100) == Confidence.MEDIUM
        # 11 samples, 90% consistent (boundary) -> MEDIUM
        assert calculate_confidence(9, 10) == Confidence.MEDIUM  # Actually 10 samples

    def test_more_than_10_samples_low_consistency(self) -> None:
        """>10 samples with <70% consistency is LOW."""
        # 20 samples, 50% consistent -> LOW
        assert calculate_confidence(10, 20) == Confidence.LOW
        # 100 samples, 65% consistent -> LOW
        assert calculate_confidence(65, 100) == Confidence.LOW

    def test_boundary_at_90_percent(self) -> None:
        """Test boundary between HIGH and MEDIUM at exactly 90%."""
        # 90% exactly with >10 samples -> MEDIUM (not >90%, so not HIGH)
        assert calculate_confidence(18, 20) == Confidence.MEDIUM
        # 91% with >10 samples -> HIGH
        assert calculate_confidence(91, 100) == Confidence.HIGH

    def test_boundary_at_70_percent(self) -> None:
        """Test boundary between MEDIUM and LOW at exactly 70%."""
        # 70% exactly with >10 samples -> MEDIUM
        assert calculate_confidence(14, 20) == Confidence.MEDIUM
        # 69% with >10 samples -> LOW
        assert calculate_confidence(69, 100) == Confidence.LOW


class TestClassifyName:
    """Test name classification into patterns."""

    def test_snake_case(self) -> None:
        """snake_case names are classified correctly."""
        assert classify_name("my_function") == "snake_case"
        assert classify_name("get_user_by_id") == "snake_case"
        assert classify_name("x") == "snake_case"
        assert classify_name("a1") == "snake_case"

    def test_pascal_case(self) -> None:
        """PascalCase names are classified correctly."""
        assert classify_name("MyClass") == "PascalCase"
        assert classify_name("UserManager") == "PascalCase"
        assert classify_name("X") == "PascalCase"

    def test_upper_snake_case(self) -> None:
        """UPPER_SNAKE_CASE names are classified correctly."""
        assert classify_name("MY_CONSTANT") == "UPPER_SNAKE_CASE"
        assert classify_name("MAX_SIZE") == "UPPER_SNAKE_CASE"
        assert classify_name("X") == "PascalCase"  # Single uppercase is PascalCase
        assert classify_name("X1") == "UPPER_SNAKE_CASE"

    def test_camel_case(self) -> None:
        """CamelCase names are classified correctly."""
        assert classify_name("myFunction") == "camelCase"
        assert classify_name("getUserById") == "camelCase"

    def test_private_names(self) -> None:
        """Private names (with leading underscores) are handled."""
        assert classify_name("_private") == "snake_case"
        assert classify_name("__dunder__") == "snake_case"
        assert classify_name("_PrivateClass") == "PascalCase"


class TestStyleDetection:
    """Test style convention detection."""

    def test_detect_indentation_spaces(self, tmp_path: Path) -> None:
        """Detects 4-space indentation."""
        # Create files with 4-space indentation
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text(
                dedent("""\
                    def foo():
                        return 1
                """)
            )

        files = collect_python_files(tmp_path)
        result = detect_indentation(files)

        assert result.style == "spaces"
        assert result.width == 4
        assert result.confidence == Confidence.HIGH

    def test_detect_indentation_2_spaces(self, tmp_path: Path) -> None:
        """Detects 2-space indentation."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text("def foo():\n  return 1\n")

        files = collect_python_files(tmp_path)
        result = detect_indentation(files)

        assert result.style == "spaces"
        assert result.width == 2

    def test_detect_indentation_tabs(self, tmp_path: Path) -> None:
        """Detects tab indentation."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text("def foo():\n\treturn 1\n")

        files = collect_python_files(tmp_path)
        result = detect_indentation(files)

        assert result.style == "tabs"
        assert result.width is None

    def test_detect_indentation_mixed(self, tmp_path: Path) -> None:
        """Detects mixed indentation."""
        # Some files with spaces, some with tabs
        for i in range(8):
            (tmp_path / f"spaces{i}.py").write_text("def foo():\n    return 1\n")
        for i in range(7):
            (tmp_path / f"tabs{i}.py").write_text("def foo():\n\treturn 1\n")

        files = collect_python_files(tmp_path)
        result = detect_indentation(files)

        assert result.style == "mixed"
        assert result.confidence == Confidence.LOW

    def test_detect_quotes_double(self, tmp_path: Path) -> None:
        """Detects double quote preference."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text('x = "hello"\ny = "world"\n')

        files = collect_python_files(tmp_path)
        result = detect_quotes(files)

        assert result.style == "double"

    def test_detect_quotes_single(self, tmp_path: Path) -> None:
        """Detects single quote preference."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text("x = 'hello'\ny = 'world'\n")

        files = collect_python_files(tmp_path)
        result = detect_quotes(files)

        assert result.style == "single"

    def test_detect_line_length(self, tmp_path: Path) -> None:
        """Detects reasonable line length."""
        # Create files with lines around 80-90 chars
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text(
                "x = 1\n" + "y = " + "a" * 80 + "\n" + "z = 3\n"
            )

        files = collect_python_files(tmp_path)
        result = detect_line_length(files)

        # Should round to a common value (79 or 88)
        assert result.max_length in [79, 88]


class TestNamingDetection:
    """Test naming convention detection."""

    def test_detect_snake_case_functions(self, tmp_path: Path) -> None:
        """Detects snake_case function naming."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text(
                dedent("""\
                    def my_function():
                        pass

                    def another_function():
                        pass
                """)
            )

        files = collect_python_files(tmp_path)
        result = detect_naming(files)

        assert result.functions.pattern == "snake_case"
        assert result.functions.confidence == Confidence.HIGH

    def test_detect_pascal_case_classes(self, tmp_path: Path) -> None:
        """Detects PascalCase class naming."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text(
                dedent("""\
                    class MyClass:
                        pass

                    class AnotherClass:
                        pass
                """)
            )

        files = collect_python_files(tmp_path)
        result = detect_naming(files)

        assert result.classes.pattern == "PascalCase"
        assert result.classes.confidence == Confidence.HIGH

    def test_detect_upper_snake_constants(self, tmp_path: Path) -> None:
        """Detects UPPER_SNAKE_CASE constant naming."""
        for i in range(15):
            (tmp_path / f"file{i}.py").write_text(
                dedent("""\
                    MY_CONSTANT = 1
                    ANOTHER_CONSTANT = 2
                """)
            )

        files = collect_python_files(tmp_path)
        result = detect_naming(files)

        assert result.constants.pattern == "UPPER_SNAKE_CASE"


class TestStructureDetection:
    """Test structure convention detection."""

    def test_detect_src_layout(self, tmp_path: Path) -> None:
        """Detects src/ layout."""
        # Create src/mypackage structure
        (tmp_path / "src" / "mypackage").mkdir(parents=True)
        (tmp_path / "src" / "mypackage" / "__init__.py").write_text("")
        (tmp_path / "tests").mkdir()

        result = detect_structure(tmp_path)

        assert result.has_src_layout is True
        assert result.source_dir == "src/mypackage"
        assert result.test_dir == "tests"

    def test_detect_flat_layout(self, tmp_path: Path) -> None:
        """Detects flat (non-src) layout."""
        # Create mypackage at root
        (tmp_path / "mypackage").mkdir()
        (tmp_path / "mypackage" / "__init__.py").write_text("")
        (tmp_path / "tests").mkdir()

        result = detect_structure(tmp_path)

        assert result.has_src_layout is False
        assert result.source_dir == "mypackage"
        assert result.test_dir == "tests"

    def test_detect_test_directory(self, tmp_path: Path) -> None:
        """Detects test directory variants."""
        (tmp_path / "test").mkdir()

        result = detect_structure(tmp_path)

        assert result.test_dir == "test"

    def test_detect_common_patterns(self, tmp_path: Path) -> None:
        """Detects common subdirectory patterns."""
        (tmp_path / "src" / "mypackage").mkdir(parents=True)
        (tmp_path / "src" / "mypackage" / "__init__.py").write_text("")
        (tmp_path / "src" / "mypackage" / "cli").mkdir()
        (tmp_path / "src" / "mypackage" / "schemas").mkdir()
        (tmp_path / "src" / "mypackage" / "core").mkdir()

        result = detect_structure(tmp_path)

        assert "cli/" in result.common_patterns
        assert "schemas/" in result.common_patterns
        assert "core/" in result.common_patterns


class TestIntegration:
    """Integration tests for full convention detection."""

    def test_detect_conventions_empty_directory(self, tmp_path: Path) -> None:
        """Handles empty directory gracefully."""
        result = detect_conventions(tmp_path)

        assert result.files_analyzed == 0
        assert result.overall_confidence == Confidence.LOW

    def test_detect_conventions_minimal_project(self, tmp_path: Path) -> None:
        """Detects conventions in minimal project (low confidence)."""
        (tmp_path / "main.py").write_text(
            dedent("""\
                def main():
                    print("hello")

                if __name__ == "__main__":
                    main()
            """)
        )

        result = detect_conventions(tmp_path)

        assert result.files_analyzed == 1
        assert result.overall_confidence == Confidence.LOW  # Too few files

    def test_detect_conventions_consistent_project(self, tmp_path: Path) -> None:
        """Detects conventions in a well-organized project."""
        # Create src/mypackage structure with consistent conventions
        pkg = tmp_path / "src" / "mypackage"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("")

        # Create 15 consistent Python files
        for i in range(15):
            (pkg / f"module{i}.py").write_text(
                dedent('''\
                    """Module docstring."""

                    MY_CONSTANT = 42

                    def my_function():
                        """Do something."""
                        return "result"

                    class MyClass:
                        """A class."""
                        pass
                ''')
            )

        # Create tests directory
        (tmp_path / "tests").mkdir()

        result = detect_conventions(tmp_path)

        assert result.files_analyzed >= 15
        assert result.style.indentation.style == "spaces"
        assert result.style.indentation.width == 4
        assert result.naming.functions.pattern == "snake_case"
        assert result.naming.classes.pattern == "PascalCase"
        assert result.structure.has_src_layout is True
        assert result.structure.source_dir == "src/mypackage"
        assert result.structure.test_dir == "tests"


class TestRaiseCommons:
    """Test convention detection on raise-commons itself."""

    def test_detect_raise_commons_conventions(self) -> None:
        """Validates detection on raise-commons matches known conventions."""
        # Get project root (this test file is in tests/onboarding/)
        project_root = Path(__file__).parent.parent.parent

        result = detect_conventions(project_root)

        # Known conventions for raise-commons
        assert result.files_analyzed > 30, "Should analyze many files"
        assert result.style.indentation.style == "spaces"
        assert result.style.indentation.width == 4
        assert result.naming.functions.pattern == "snake_case"
        assert result.naming.classes.pattern == "PascalCase"
        assert result.structure.has_src_layout is True
        assert result.structure.source_dir in [
            "src/raise_cli",
            "src/raise_core",
            "src/rai_pro",
        ]
        assert result.structure.test_dir == "tests"
        # Overall confidence should be HIGH for a well-organized project
        assert result.overall_confidence in [Confidence.HIGH, Confidence.MEDIUM]
