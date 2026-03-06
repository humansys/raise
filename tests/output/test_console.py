"""Tests for OutputConsole class."""

from __future__ import annotations

import json

import pytest

from raise_cli.output import (
    OutputConsole,
    configure_console,
    get_console,
    set_console,
)


@pytest.fixture(autouse=True)
def reset_console() -> None:
    """Reset global console before each test."""
    set_console(None)


class TestOutputConsoleInit:
    """Tests for OutputConsole initialization."""

    def test_default_values(self) -> None:
        """Test default initialization values."""
        console = OutputConsole()
        assert console.format == "human"
        assert console.verbosity == 0
        assert console.color is True

    def test_custom_format(self) -> None:
        """Test custom format initialization."""
        console = OutputConsole(format="json")
        assert console.format == "json"

    def test_custom_verbosity(self) -> None:
        """Test custom verbosity initialization."""
        console = OutputConsole(verbosity=2)
        assert console.verbosity == 2

    def test_color_disabled(self) -> None:
        """Test color disabled initialization."""
        console = OutputConsole(color=False)
        assert console.color is False


class TestPrintMessage:
    """Tests for print_message method."""

    def test_human_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_message in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_message("Hello world")
        captured = capsys.readouterr()
        assert "Hello world" in captured.out

    def test_json_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_message in JSON format."""
        console = OutputConsole(format="json")
        console.print_message("Hello world")
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == {"message": "Hello world"}

    def test_table_format_same_as_human(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_message in table format (same as human for messages)."""
        console = OutputConsole(format="table", color=False)
        console.print_message("Hello world")
        captured = capsys.readouterr()
        assert "Hello world" in captured.out

    def test_with_style(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_message with style."""
        console = OutputConsole(format="human", color=False)
        console.print_message("Important", style="bold")
        captured = capsys.readouterr()
        assert "Important" in captured.out


class TestPrintSuccess:
    """Tests for print_success method."""

    def test_human_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_success in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_success("Task completed")
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Task completed" in captured.out

    def test_human_format_with_details(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_success with details in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_success("Done", details={"duration": "2.3s"})
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Done" in captured.out
        assert "duration: 2.3s" in captured.out

    def test_json_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_success in JSON format."""
        console = OutputConsole(format="json")
        console.print_success("Task completed")
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"
        assert output["message"] == "Task completed"

    def test_json_format_with_details(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_success with details in JSON format."""
        console = OutputConsole(format="json")
        console.print_success("Done", details={"duration": "2.3s", "items": 5})
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"
        assert output["message"] == "Done"
        assert output["details"] == {"duration": "2.3s", "items": 5}


class TestPrintWarning:
    """Tests for print_warning method."""

    def test_human_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_warning in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_warning("Config not found")
        captured = capsys.readouterr()
        assert "⚠" in captured.out
        assert "Config not found" in captured.out

    def test_human_format_with_details(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_warning with details in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_warning("Missing file", details={"path": "/tmp/foo"})
        captured = capsys.readouterr()
        assert "⚠" in captured.out
        assert "path: /tmp/foo" in captured.out

    def test_json_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_warning in JSON format."""
        console = OutputConsole(format="json")
        console.print_warning("Config not found")
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "warning"
        assert output["message"] == "Config not found"


class TestPrintData:
    """Tests for print_data method."""

    def test_json_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data in JSON format."""
        console = OutputConsole(format="json")
        data = {"name": "discovery", "steps": 5}
        console.print_data(data)
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == data

    def test_human_format_flat(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data with flat dict in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_data({"name": "discovery", "steps": 5})
        captured = capsys.readouterr()
        assert "name:" in captured.out
        assert "discovery" in captured.out
        assert "steps:" in captured.out

    def test_human_format_nested(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data with nested dict in human format (tree)."""
        console = OutputConsole(format="human", color=False)
        console.print_data({"kata": {"name": "discovery", "steps": 5}})
        captured = capsys.readouterr()
        assert "kata" in captured.out
        assert "name" in captured.out

    def test_table_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data in table format."""
        console = OutputConsole(format="table", color=False)
        console.print_data({"name": "discovery", "steps": 5})
        captured = capsys.readouterr()
        # Table format shows KEY and VALUE columns
        assert "KEY" in captured.out or "name" in captured.out

    def test_with_title(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data with title."""
        console = OutputConsole(format="human", color=False)
        console.print_data({"name": "test"}, title="Kata Info")
        captured = capsys.readouterr()
        assert "Kata Info" in captured.out


class TestPrintList:
    """Tests for print_list method."""

    def test_json_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list in JSON format."""
        console = OutputConsole(format="json")
        items = [
            {"id": "kata/discovery", "name": "Discovery"},
            {"id": "kata/design", "name": "Design"},
        ]
        console.print_list(items)
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == items

    def test_json_format_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list with empty list in JSON format."""
        console = OutputConsole(format="json")
        console.print_list([])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output == []

    def test_human_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list in human format (bullets)."""
        console = OutputConsole(format="human", color=False)
        items = [
            {"id": "kata/discovery", "name": "Discovery"},
            {"id": "kata/design", "name": "Design"},
        ]
        console.print_list(items)
        captured = capsys.readouterr()
        assert "•" in captured.out
        assert "kata/discovery" in captured.out
        assert "Discovery" in captured.out

    def test_human_format_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list with empty list in human format."""
        console = OutputConsole(format="human", color=False)
        console.print_list([])
        captured = capsys.readouterr()
        assert "(no items)" in captured.out

    def test_table_format(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list in table format."""
        console = OutputConsole(format="table", color=False)
        items = [
            {"id": "kata/discovery", "name": "Discovery"},
            {"id": "kata/design", "name": "Design"},
        ]
        console.print_list(items)
        captured = capsys.readouterr()
        # Table shows column headers
        assert "ID" in captured.out
        assert "NAME" in captured.out
        assert "kata/discovery" in captured.out

    def test_table_format_with_columns(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_list with specific columns."""
        console = OutputConsole(format="table", color=False)
        items = [
            {"id": "kata/discovery", "name": "Discovery", "extra": "ignored"},
        ]
        console.print_list(items, columns=["id", "name"])
        captured = capsys.readouterr()
        assert "ID" in captured.out
        assert "NAME" in captured.out
        # extra column should not appear as header
        assert "EXTRA" not in captured.out

    def test_with_title(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list with title."""
        console = OutputConsole(format="human", color=False)
        items = [{"id": "test", "name": "Test"}]
        console.print_list(items, title="Available katas")
        captured = capsys.readouterr()
        assert "Available katas:" in captured.out


class TestModuleLevelFunctions:
    """Tests for module-level singleton functions."""

    def test_get_console_creates_default(self) -> None:
        """Test get_console creates default console."""
        console = get_console()
        assert isinstance(console, OutputConsole)
        assert console.format == "human"

    def test_get_console_returns_same_instance(self) -> None:
        """Test get_console returns singleton."""
        console1 = get_console()
        console2 = get_console()
        assert console1 is console2

    def test_set_console(self) -> None:
        """Test set_console replaces singleton."""
        custom = OutputConsole(format="json")
        set_console(custom)
        assert get_console() is custom

    def test_set_console_none_resets(self) -> None:
        """Test set_console(None) resets singleton."""
        custom = OutputConsole(format="json")
        set_console(custom)
        set_console(None)
        # Next get_console creates new default
        new_console = get_console()
        assert new_console is not custom
        assert new_console.format == "human"

    def test_configure_console(self) -> None:
        """Test configure_console creates and sets console."""
        console = configure_console(format="json", verbosity=2, color=False)
        assert console.format == "json"
        assert console.verbosity == 2
        assert console.color is False
        assert get_console() is console


class TestQuietMode:
    """Tests for quiet mode (verbosity=-1)."""

    def test_print_message_suppressed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_message suppressed in quiet mode."""
        console = OutputConsole(verbosity=-1)
        console.print_message("Should not appear")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_success_suppressed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_success suppressed in quiet mode."""
        console = OutputConsole(verbosity=-1)
        console.print_success("Should not appear")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_warning_suppressed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_warning suppressed in quiet mode."""
        console = OutputConsole(verbosity=-1)
        console.print_warning("Should not appear")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_data_suppressed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_data suppressed in quiet mode."""
        console = OutputConsole(verbosity=-1)
        console.print_data({"key": "value"})
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_print_list_suppressed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test print_list suppressed in quiet mode."""
        console = OutputConsole(verbosity=-1)
        console.print_list([{"id": "test"}])
        captured = capsys.readouterr()
        assert captured.out == ""


class TestNestedDataStructures:
    """Tests for complex nested data handling."""

    def test_nested_dict_as_tree(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test nested dict renders as tree."""
        console = OutputConsole(format="human", color=False)
        data = {
            "kata": {
                "name": "discovery",
                "config": {"timeout": 30, "retries": 3},
            }
        }
        console.print_data(data)
        captured = capsys.readouterr()
        assert "kata" in captured.out
        assert "config" in captured.out

    def test_list_in_dict(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test dict with list value renders correctly."""
        console = OutputConsole(format="human", color=False)
        data = {"steps": ["step1", "step2", "step3"]}
        console.print_data(data)
        captured = capsys.readouterr()
        assert "steps" in captured.out
        assert "step1" in captured.out

    def test_json_nested_preserves_structure(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test JSON format preserves nested structure."""
        console = OutputConsole(format="json")
        data = {"outer": {"inner": {"deep": "value"}}}
        console.print_data(data)
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["outer"]["inner"]["deep"] == "value"
