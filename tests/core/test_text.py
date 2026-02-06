"""Tests for core text utilities."""

from __future__ import annotations

from raise_cli.core.text import sanitize_id


class TestSanitizeId:
    """Tests for sanitize_id function."""

    def test_basic_lowercase(self) -> None:
        """Should convert to lowercase."""
        assert sanitize_id("Hello World") == "hello-world"

    def test_spaces_to_hyphens(self) -> None:
        """Should replace spaces with hyphens."""
        assert sanitize_id("foo bar baz") == "foo-bar-baz"

    def test_removes_parentheses(self) -> None:
        """Should remove parentheses."""
        assert sanitize_id("Context Generation (MVC)") == "context-generation-mvc"

    def test_removes_commas(self) -> None:
        """Should remove commas."""
        assert sanitize_id("Hello, World") == "hello-world"

    def test_removes_special_chars(self) -> None:
        """Should remove special characters."""
        assert sanitize_id("Test!@#$%^&*()") == "test"

    def test_collapses_multiple_hyphens(self) -> None:
        """Should collapse multiple hyphens into one."""
        assert sanitize_id("foo  bar   baz") == "foo-bar-baz"
        assert sanitize_id("foo--bar") == "foo-bar"

    def test_strips_leading_trailing_hyphens(self) -> None:
        """Should strip leading and trailing hyphens."""
        assert sanitize_id(" foo ") == "foo"
        assert sanitize_id("-foo-") == "foo"

    def test_preserves_numbers(self) -> None:
        """Should preserve numbers."""
        assert sanitize_id("Version 2.0") == "version-20"

    def test_governance_as_code(self) -> None:
        """Should handle constitution principle names."""
        assert sanitize_id("Governance as Code") == "governance-as-code"

    def test_empty_string(self) -> None:
        """Should handle empty strings."""
        assert sanitize_id("") == ""

    def test_only_special_chars(self) -> None:
        """Should handle strings with only special chars."""
        assert sanitize_id("!@#$%") == ""
