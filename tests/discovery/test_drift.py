"""Tests for drift detection module.

Tests the detection of architectural drift between new code
and established component patterns.
"""

from __future__ import annotations

from raise_cli.discovery.drift import (
    BaselineComponent,
    BaselineComponentMetadata,
    DriftSeverity,
    DriftWarning,
    detect_drift,
)
from raise_cli.discovery.scanner import Symbol


class TestDriftWarning:
    """Tests for DriftWarning model."""

    def test_create_warning(self) -> None:
        """DriftWarning can be created with required fields."""
        warning = DriftWarning(
            file="src/new_module/foo.py",
            issue="File in unexpected location",
            severity="warning",
            suggestion="Consider moving to src/raise_cli/",
        )
        assert warning.file == "src/new_module/foo.py"
        assert warning.severity == "warning"

    def test_warning_severity_values(self) -> None:
        """DriftWarning accepts valid severity values."""
        warning = DriftWarning(
            file="test.py",
            issue="Test issue",
            severity="error",
            suggestion="Fix it",
        )
        assert warning.severity == "error"


class TestDetectDrift:
    """Tests for detect_drift function."""

    def test_no_drift_when_empty(self) -> None:
        """Empty inputs produce no warnings."""
        warnings = detect_drift(baseline=[], scanned=[])
        assert warnings == []

    def test_no_drift_when_symbols_match_baseline(self) -> None:
        """No warnings when new symbols follow baseline patterns."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/services/user.py",
                metadata=BaselineComponentMetadata(name="UserService", kind="class"),
            )
        ]
        scanned = [
            Symbol(
                name="OrderService",
                kind="class",
                file="src/raise_cli/services/order.py",
                line=10,
                signature="class OrderService",
                docstring="Handles orders.",
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)
        assert len(warnings) == 0

    def test_detect_location_drift(self) -> None:
        """Detect when file is in unexpected location."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/discovery/scanner.py",
                metadata=BaselineComponentMetadata(name="Symbol", kind="class"),
            )
        ]
        # New class in wrong location (cli/ instead of discovery/)
        scanned = [
            Symbol(
                name="NewModel",
                kind="class",
                file="src/raise_cli/cli/new_model.py",
                line=5,
                signature="class NewModel(BaseModel)",
                docstring="A model in wrong place.",
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)

        # Should detect location drift
        location_warnings = [w for w in warnings if "location" in w.issue.lower()]
        assert len(location_warnings) >= 1

    def test_detect_missing_docstring(self) -> None:
        """Detect public class without docstring when baseline has them."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/discovery/scanner.py",
                content="Core data model representing an extracted code symbol.",
                metadata=BaselineComponentMetadata(name="Symbol", kind="class"),
            )
        ]
        # New class without docstring
        scanned = [
            Symbol(
                name="NewClass",
                kind="class",
                file="src/raise_cli/discovery/new.py",
                line=5,
                signature="class NewClass",
                docstring=None,  # Missing!
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)

        # Should detect missing docstring
        docstring_warnings = [w for w in warnings if "docstring" in w.issue.lower()]
        assert len(docstring_warnings) >= 1

    def test_detect_naming_drift(self) -> None:
        """Detect when naming doesn't follow conventions."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/discovery/scanner.py",
                metadata=BaselineComponentMetadata(
                    name="extract_python_symbols", kind="function"
                ),
            ),
            BaselineComponent(
                source_file="src/raise_cli/discovery/scanner.py",
                metadata=BaselineComponentMetadata(
                    name="extract_typescript_symbols", kind="function"
                ),
            ),
        ]
        # Function that doesn't follow extract_* pattern
        scanned = [
            Symbol(
                name="get_symbols",  # Should be extract_*
                kind="function",
                file="src/raise_cli/discovery/scanner.py",
                line=100,
                signature="def get_symbols()",
                docstring="Get symbols.",
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)

        # Should detect naming convention drift
        naming_warnings = [w for w in warnings if "naming" in w.issue.lower()]
        assert len(naming_warnings) >= 1

    def test_ignores_private_symbols(self) -> None:
        """Private symbols (starting with _) are not checked for drift."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/discovery/scanner.py",
                metadata=BaselineComponentMetadata(name="Symbol", kind="class"),
            )
        ]
        # Private function - should be ignored
        scanned = [
            Symbol(
                name="_helper",
                kind="function",
                file="src/raise_cli/cli/commands.py",
                line=5,
                signature="def _helper()",
                docstring=None,
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)
        assert len(warnings) == 0

    def test_multiple_drift_issues(self) -> None:
        """Multiple drift issues can be detected at once."""
        baseline = [
            BaselineComponent(
                source_file="src/raise_cli/services/user.py",
                content="User service with docstring.",
                metadata=BaselineComponentMetadata(name="UserService", kind="class"),
            )
        ]
        # File with multiple issues
        scanned = [
            Symbol(
                name="badlynamed",  # Bad naming (lowercase class)
                kind="class",
                file="src/somewhere/else.py",  # Wrong location
                line=5,
                signature="class badlynamed",
                docstring=None,  # Missing docstring
            )
        ]
        warnings = detect_drift(baseline=baseline, scanned=scanned)

        # Should have multiple warnings
        assert len(warnings) >= 2


class TestDriftSeverity:
    """Tests for drift severity classification."""

    def test_severity_is_literal(self) -> None:
        """DriftSeverity should be a type alias for valid values."""
        # Just verify the type exists and can be used
        severity: DriftSeverity = "warning"
        assert severity in ("warning", "error", "info")
