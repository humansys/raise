"""Tests for changelog parsing and updating."""

from __future__ import annotations

from raise_cli.publish.changelog import has_unreleased_entries, promote_unreleased

SAMPLE_CHANGELOG = """\
# Changelog

## [Unreleased]

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

## [1.0.0] - 2026-01-01

### Added
- Initial release

[Unreleased]: https://github.com/org/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
"""

EMPTY_UNRELEASED = """\
# Changelog

## [Unreleased]

## [1.0.0] - 2026-01-01

### Added
- Initial release
"""

NO_CHANGELOG = ""


class TestHasUnreleasedEntries:
    """Test unreleased entry detection."""

    def test_has_entries(self) -> None:
        assert has_unreleased_entries(SAMPLE_CHANGELOG) is True

    def test_empty_unreleased(self) -> None:
        assert has_unreleased_entries(EMPTY_UNRELEASED) is False

    def test_no_content(self) -> None:
        assert has_unreleased_entries(NO_CHANGELOG) is False

    def test_unreleased_with_only_whitespace(self) -> None:
        content = "# Changelog\n\n## [Unreleased]\n\n\n\n## [1.0.0] - 2026-01-01\n"
        assert has_unreleased_entries(content) is False

    def test_unreleased_as_last_section(self) -> None:
        r"""Unreleased is the only/last section — hits \\Z branch (RAISE-536)."""
        content = "# Changelog\n\n## [Unreleased]\n\n### Added\n- First entry\n"
        assert has_unreleased_entries(content) is True

    def test_unreleased_as_last_section_empty(self) -> None:
        r"""Unreleased is the only section and empty — hits \\Z branch."""
        content = "# Changelog\n\n## [Unreleased]\n"
        assert has_unreleased_entries(content) is False


class TestPromoteUnreleased:
    """Test promoting unreleased entries to a versioned section."""

    def test_basic_promote(self) -> None:
        result = promote_unreleased(SAMPLE_CHANGELOG, "2.0.0", "2026-02-14")
        # New version section should exist
        assert "## [2.0.0] - 2026-02-14" in result
        # Unreleased section should be empty
        assert "## [Unreleased]" in result
        # Content should be under new version
        assert "New feature X" in result
        # Old version should still exist
        assert "## [1.0.0] - 2026-01-01" in result

    def test_promote_updates_links(self) -> None:
        result = promote_unreleased(SAMPLE_CHANGELOG, "2.0.0", "2026-02-14")
        assert "compare/v2.0.0...HEAD" in result
        assert "compare/v1.0.0...v2.0.0" in result

    def test_promote_empty_unreleased_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="No unreleased entries"):
            promote_unreleased(EMPTY_UNRELEASED, "2.0.0", "2026-02-14")

    def test_promote_preserves_categories(self) -> None:
        result = promote_unreleased(SAMPLE_CHANGELOG, "2.0.0", "2026-02-14")
        # Find the 2.0.0 section and verify it has the categories
        assert "### Added" in result
        assert "### Fixed" in result

    def test_promote_unreleased_as_last_section(self) -> None:
        """Promote succeeds when Unreleased is the last section (no prior version)."""
        content = (
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- First release feature\n"
        )
        result = promote_unreleased(content, "1.0.0", "2026-03-18")
        assert "## [1.0.0] - 2026-03-18" in result
        assert "## [Unreleased]" in result
        assert "First release feature" in result
