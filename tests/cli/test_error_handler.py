"""Tests for CLI error handler."""

from __future__ import annotations

import io
import json
import sys
from unittest.mock import patch

import pytest
from rich.console import Console

from raise_cli.cli.error_handler import (
    get_error_console,
    handle_error,
    set_error_console,
)
from raise_cli.exceptions import (
    ConfigurationError,
    GateFailedError,
    KataNotFoundError,
    RaiError,
)


class TestHandleErrorHuman:
    """Tests for human-readable error output."""

    def setup_method(self) -> None:
        """Reset console before each test."""
        set_error_console(None)

    def test_displays_error_message(self) -> None:
        """Error message is displayed."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Test error message")
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "Test error message" in result

    def test_displays_error_code(self) -> None:
        """Error code is displayed in panel title."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = ConfigurationError("Config error")
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "E001" in result

    def test_displays_hint_when_present(self) -> None:
        """Hint is displayed when provided."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Error", hint="Try this instead")
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "Hint" in result
        assert "Try this instead" in result

    def test_displays_details_when_present(self) -> None:
        """Details are displayed when provided."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Error", details={"file": "test.py", "line": 42})
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "Details" in result
        assert "file" in result
        assert "test.py" in result

    def test_no_hint_section_when_absent(self) -> None:
        """No hint section when hint is None."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Error")
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "Hint:" not in result

    def test_no_details_section_when_empty(self) -> None:
        """No details section when details is empty."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Error")
        handle_error(error, output_format="human")

        result = output.getvalue()
        assert "Details:" not in result


class TestHandleErrorJson:
    """Tests for JSON error output."""

    def setup_method(self) -> None:
        """Reset console before each test."""
        set_error_console(None)

    def test_outputs_valid_json(self) -> None:
        """JSON output is valid JSON."""
        error = RaiError("Test error")

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        # Should parse without error
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_contains_error_code(self) -> None:
        """JSON output contains error_code."""
        error = KataNotFoundError("Kata not found")

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        parsed = json.loads(output)
        assert parsed["error_code"] == "E002"

    def test_json_contains_exit_code(self) -> None:
        """JSON output contains exit_code."""
        error = GateFailedError("Gate failed")

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        parsed = json.loads(output)
        assert parsed["exit_code"] == 10

    def test_json_contains_message(self) -> None:
        """JSON output contains message."""
        error = RaiError("Test message")

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        parsed = json.loads(output)
        assert parsed["message"] == "Test message"

    def test_json_contains_hint(self) -> None:
        """JSON output contains hint when provided."""
        error = RaiError("Error", hint="Do this")

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        parsed = json.loads(output)
        assert parsed["hint"] == "Do this"

    def test_json_contains_details(self) -> None:
        """JSON output contains details when provided."""
        error = RaiError("Error", details={"key": "value"})

        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            handle_error(error, output_format="json")
            output = mock_stderr.getvalue()

        parsed = json.loads(output)
        assert parsed["details"] == {"key": "value"}


class TestHandleErrorReturnValue:
    """Tests for handle_error return value."""

    def setup_method(self) -> None:
        """Reset console before each test."""
        set_error_console(None)
        # Use a null console to suppress output
        set_error_console(Console(file=io.StringIO()))

    @pytest.mark.parametrize(
        ("exception_class", "expected_exit_code"),
        [
            (RaiError, 1),
            (ConfigurationError, 2),
            (KataNotFoundError, 3),
            (GateFailedError, 10),
        ],
    )
    def test_returns_exit_code(
        self,
        exception_class: type[RaiError],
        expected_exit_code: int,
    ) -> None:
        """handle_error returns the exception's exit_code."""
        error = exception_class("test")
        result = handle_error(error, output_format="human")
        assert result == expected_exit_code

    def test_returns_exit_code_json_format(self) -> None:
        """handle_error returns exit_code in JSON format too."""
        error = ConfigurationError("test")

        with patch.object(sys, "stderr", new_callable=io.StringIO):
            result = handle_error(error, output_format="json")

        assert result == 2


class TestErrorConsoleSingleton:
    """Tests for console singleton management."""

    def setup_method(self) -> None:
        """Reset console before each test."""
        set_error_console(None)

    def test_get_error_console_returns_console(self) -> None:
        """get_error_console returns a Console instance."""
        console = get_error_console()
        assert isinstance(console, Console)

    def test_get_error_console_returns_same_instance(self) -> None:
        """get_error_console returns the same instance on repeated calls."""
        console1 = get_error_console()
        console2 = get_error_console()
        assert console1 is console2

    def test_set_error_console_overrides(self) -> None:
        """set_error_console overrides the singleton."""
        custom = Console()
        set_error_console(custom)
        assert get_error_console() is custom

    def test_set_error_console_none_resets(self) -> None:
        """set_error_console(None) resets to create new instance."""
        original = get_error_console()
        set_error_console(None)
        new = get_error_console()
        assert original is not new


class TestTableFormat:
    """Tests for table format (falls back to human)."""

    def setup_method(self) -> None:
        """Reset console before each test."""
        set_error_console(None)

    def test_table_format_uses_human_output(self) -> None:
        """Table format uses human output (not JSON)."""
        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        error = RaiError("Test error")
        handle_error(error, output_format="table")

        result = output.getvalue()
        # Should have Rich formatting, not JSON
        assert "Test error" in result
        assert "{" not in result or "error_code" not in result
