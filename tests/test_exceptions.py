"""Tests for raise-cli exception hierarchy."""

from __future__ import annotations

import pytest

from raise_cli.exceptions import (
    ArtifactNotFoundError,
    ConfigurationError,
    DependencyError,
    GateFailedError,
    GateNotFoundError,
    KataNotFoundError,
    RaiError,
    StateError,
    ValidationError,
)


class TestRaiError:
    """Tests for base RaiError class."""

    def test_basic_creation(self) -> None:
        """RaiError can be created with just a message."""
        error = RaiError("Something went wrong")

        assert error.message == "Something went wrong"
        assert str(error) == "Something went wrong"
        assert error.hint is None
        assert error.details == {}

    def test_with_hint(self) -> None:
        """RaiError accepts an optional hint."""
        error = RaiError("Config not found", hint="Run 'raise init' first")

        assert error.message == "Config not found"
        assert error.hint == "Run 'raise init' first"

    def test_with_details(self) -> None:
        """RaiError accepts optional details dict."""
        error = RaiError(
            "Validation failed",
            details={"field": "name", "value": None},
        )

        assert error.details == {"field": "name", "value": None}

    def test_default_exit_code(self) -> None:
        """RaiError has exit_code 1 by default."""
        error = RaiError("error")
        assert error.exit_code == 1

    def test_default_error_code(self) -> None:
        """RaiError has error_code E000 by default."""
        error = RaiError("error")
        assert error.error_code == "E000"

    def test_to_dict(self) -> None:
        """RaiError.to_dict() returns complete error info."""
        error = RaiError(
            "Test error",
            hint="Try again",
            details={"key": "value"},
        )

        result = error.to_dict()

        assert result == {
            "error_code": "E000",
            "exit_code": 1,
            "message": "Test error",
            "hint": "Try again",
            "details": {"key": "value"},
        }

    def test_to_dict_without_optional_fields(self) -> None:
        """RaiError.to_dict() works without hint."""
        error = RaiError("Test error")

        result = error.to_dict()

        assert result["hint"] is None
        assert result["details"] == {}

    def test_is_exception(self) -> None:
        """RaiError is a proper Exception subclass."""
        error = RaiError("error")
        assert isinstance(error, Exception)

    def test_can_be_raised(self) -> None:
        """RaiError can be raised and caught."""
        with pytest.raises(RaiError) as exc_info:
            raise RaiError("test", hint="hint")

        assert exc_info.value.message == "test"
        assert exc_info.value.hint == "hint"


class TestExceptionHierarchy:
    """Tests for specific exception subclasses."""

    @pytest.mark.parametrize(
        ("exception_class", "expected_exit_code", "expected_error_code"),
        [
            (RaiError, 1, "E000"),
            (ConfigurationError, 2, "E001"),
            (KataNotFoundError, 3, "E002"),
            (GateNotFoundError, 3, "E003"),
            (ArtifactNotFoundError, 4, "E004"),
            (DependencyError, 5, "E005"),
            (StateError, 6, "E006"),
            (ValidationError, 7, "E007"),
            (GateFailedError, 10, "E010"),
        ],
    )
    def test_exit_codes(
        self,
        exception_class: type[RaiError],
        expected_exit_code: int,
        expected_error_code: str,
    ) -> None:
        """Each exception has correct exit_code and error_code."""
        error = exception_class("test message")

        assert error.exit_code == expected_exit_code
        assert error.error_code == expected_error_code

    @pytest.mark.parametrize(
        "exception_class",
        [
            ConfigurationError,
            KataNotFoundError,
            GateNotFoundError,
            ArtifactNotFoundError,
            DependencyError,
            StateError,
            ValidationError,
            GateFailedError,
        ],
    )
    def test_inherits_from_raise_error(
        self,
        exception_class: type[RaiError],
    ) -> None:
        """All exceptions inherit from RaiError."""
        error = exception_class("test")
        assert isinstance(error, RaiError)

    @pytest.mark.parametrize(
        "exception_class",
        [
            ConfigurationError,
            KataNotFoundError,
            GateNotFoundError,
            ArtifactNotFoundError,
            DependencyError,
            StateError,
            ValidationError,
            GateFailedError,
        ],
    )
    def test_subclasses_accept_hint_and_details(
        self,
        exception_class: type[RaiError],
    ) -> None:
        """All exceptions accept hint and details kwargs."""
        error = exception_class(
            "test message",
            hint="test hint",
            details={"key": "value"},
        )

        assert error.message == "test message"
        assert error.hint == "test hint"
        assert error.details == {"key": "value"}


class TestSpecificExceptions:
    """Tests for exception-specific behavior and documentation."""

    def test_configuration_error_docstring(self) -> None:
        """ConfigurationError has proper docstring."""
        assert "Configuration" in ConfigurationError.__doc__

    def test_kata_not_found_error_docstring(self) -> None:
        """KataNotFoundError has proper docstring."""
        assert "Kata" in KataNotFoundError.__doc__

    def test_gate_not_found_error_docstring(self) -> None:
        """GateNotFoundError has proper docstring."""
        assert "Gate" in GateNotFoundError.__doc__

    def test_artifact_not_found_error_docstring(self) -> None:
        """ArtifactNotFoundError has proper docstring."""
        assert "Artifact" in ArtifactNotFoundError.__doc__

    def test_dependency_error_docstring(self) -> None:
        """DependencyError has proper docstring."""
        assert "dependency" in DependencyError.__doc__.lower()

    def test_state_error_docstring(self) -> None:
        """StateError has proper docstring."""
        assert "State" in StateError.__doc__

    def test_validation_error_docstring(self) -> None:
        """ValidationError has proper docstring."""
        assert "validation" in ValidationError.__doc__.lower()

    def test_gate_failed_error_docstring(self) -> None:
        """GateFailedError has proper docstring."""
        assert "Gate" in GateFailedError.__doc__


class TestExceptionExports:
    """Tests for module exports."""

    def test_all_exceptions_in_all(self) -> None:
        """All exceptions are listed in __all__."""
        from raise_cli import exceptions

        expected = {
            "RaiError",
            "ConfigurationError",
            "KataNotFoundError",
            "GateNotFoundError",
            "ArtifactNotFoundError",
            "DependencyError",
            "StateError",
            "ValidationError",
            "GateFailedError",
            "RaiSessionNotFoundError",
        }

        assert set(exceptions.__all__) == expected
