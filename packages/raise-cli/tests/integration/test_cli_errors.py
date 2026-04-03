"""Integration tests for CLI error handling."""

from __future__ import annotations

import io
import json
import sys
from unittest.mock import patch

import pytest

from raise_cli.__main__ import main
from raise_cli.cli.error_handler import set_error_console
from raise_cli.exceptions import (
    ConfigurationError,
    GateFailedError,
    KataNotFoundError,
    RaiError,
)


class TestCLIErrorHandling:
    """Integration tests for end-to-end error handling."""

    def setup_method(self) -> None:
        """Reset error console before each test."""
        set_error_console(None)

    def test_raise_error_exits_with_correct_code(self) -> None:
        """RaiError causes exit with exit_code=1."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch.object(sys, "stderr", new_callable=io.StringIO),
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_app.side_effect = RaiError("General error")
            main()

        assert exc_info.value.code == 1

    def test_configuration_error_exits_with_code_2(self) -> None:
        """ConfigurationError causes exit with exit_code=2."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch.object(sys, "stderr", new_callable=io.StringIO),
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_app.side_effect = ConfigurationError("Config error")
            main()

        assert exc_info.value.code == 2

    def test_kata_not_found_error_exits_with_code_3(self) -> None:
        """KataNotFoundError causes exit with exit_code=3."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch.object(sys, "stderr", new_callable=io.StringIO),
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_app.side_effect = KataNotFoundError("Kata not found")
            main()

        assert exc_info.value.code == 3

    def test_gate_failed_error_exits_with_code_10(self) -> None:
        """GateFailedError causes exit with exit_code=10."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch.object(sys, "stderr", new_callable=io.StringIO),
            pytest.raises(SystemExit) as exc_info,
        ):
            mock_app.side_effect = GateFailedError("Gate failed")
            main()

        assert exc_info.value.code == 10

    def test_error_message_displayed_to_stderr(self) -> None:
        """Error message is displayed on stderr."""
        from rich.console import Console

        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        with (
            patch("raise_cli.__main__.app") as mock_app,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = RaiError("Test error message")
            main()

        result = output.getvalue()
        assert "Test error message" in result

    def test_error_code_displayed(self) -> None:
        """Error code is displayed in output."""
        from rich.console import Console

        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        with (
            patch("raise_cli.__main__.app") as mock_app,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = ConfigurationError("Config error")
            main()

        result = output.getvalue()
        assert "E001" in result

    def test_hint_displayed_when_provided(self) -> None:
        """Hint is displayed when error includes it."""
        from rich.console import Console

        output = io.StringIO()
        console = Console(file=output, force_terminal=True, width=80)
        set_error_console(console)

        with (
            patch("raise_cli.__main__.app") as mock_app,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = RaiError(
                "Error occurred",
                hint="Try running with --verbose",
            )
            main()

        result = output.getvalue()
        assert "Try running with --verbose" in result


class TestCLIErrorHandlingJsonFormat:
    """Integration tests for JSON error output."""

    def setup_method(self) -> None:
        """Reset error console before each test."""
        set_error_console(None)

    def test_json_format_outputs_valid_json(self) -> None:
        """JSON format outputs valid JSON to stderr."""
        # Set format to json before triggering error
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch("raise_cli.cli.main.get_output_format", return_value="json"),
            patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = RaiError("Test error")
            main()

        output = mock_stderr.getvalue()
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed["message"] == "Test error"
        assert parsed["exit_code"] == 1
        assert parsed["error_code"] == "E000"

    def test_json_format_includes_hint(self) -> None:
        """JSON output includes hint when provided."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch("raise_cli.cli.main.get_output_format", return_value="json"),
            patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = RaiError("Error", hint="Do this")
            main()

        output = mock_stderr.getvalue()
        parsed = json.loads(output)
        assert parsed["hint"] == "Do this"

    def test_json_format_includes_details(self) -> None:
        """JSON output includes details when provided."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            patch("raise_cli.cli.main.get_output_format", return_value="json"),
            patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr,
            pytest.raises(SystemExit),
        ):
            mock_app.side_effect = RaiError("Error", details={"file": "test.py"})
            main()

        output = mock_stderr.getvalue()
        parsed = json.loads(output)
        assert parsed["details"] == {"file": "test.py"}


class TestNonRaiErrorPassthrough:
    """Tests that non-RaiError exceptions are not caught."""

    def test_value_error_not_caught(self) -> None:
        """ValueError is not caught by error handler."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            pytest.raises(ValueError, match="not a RaiError"),
        ):
            mock_app.side_effect = ValueError("not a RaiError")
            main()

    def test_runtime_error_not_caught(self) -> None:
        """RuntimeError is not caught by error handler."""
        with (
            patch("raise_cli.__main__.app") as mock_app,
            pytest.raises(RuntimeError, match="unexpected"),
        ):
            mock_app.side_effect = RuntimeError("unexpected")
            main()
