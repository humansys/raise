"""Tests for backlog parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.backlog import (
    extract_epics,
    extract_project,
    normalize_status,
)


class TestNormalizeStatus:
    """Tests for normalize_status function."""

    def test_complete_with_emoji(self) -> None:
        """Should normalize '✅ Complete' to 'complete'."""
        assert normalize_status("✅ Complete") == "complete"

    def test_complete_text_only(self) -> None:
        """Should normalize 'Complete' to 'complete'."""
        assert normalize_status("Complete") == "complete"

    def test_complete_via_skills(self) -> None:
        """Should normalize '✅ Via Skills' to 'complete'."""
        assert normalize_status("✅ Via Skills") == "complete"

    def test_draft_with_emoji(self) -> None:
        """Should normalize '📋 DRAFT' to 'draft'."""
        assert normalize_status("📋 DRAFT") == "draft"

    def test_draft_text_only(self) -> None:
        """Should normalize 'DRAFT' to 'draft'."""
        assert normalize_status("DRAFT") == "draft"

    def test_deferred(self) -> None:
        """Should normalize 'Deferred' to 'deferred'."""
        assert normalize_status("Deferred") == "deferred"

    def test_replaced_by(self) -> None:
        """Should normalize '→ Replaced by E9' to 'deferred'."""
        assert normalize_status("→ Replaced by E9") == "deferred"

    def test_in_progress(self) -> None:
        """Should normalize 'In Progress' to 'in_progress'."""
        assert normalize_status("In Progress") == "in_progress"

    def test_unknown_defaults_to_pending(self) -> None:
        """Should normalize unknown status to 'pending'."""
        assert normalize_status("Unknown") == "pending"
        assert normalize_status("") == "pending"
        assert normalize_status("—") == "pending"


@pytest.fixture
def tmp_backlog_file(tmp_path: Path) -> Path:
    """Create a temporary backlog file for testing.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary backlog file.
    """
    backlog_content = dedent(
        """\
        # Backlog: test-project

        > **Status**: Active
        > **Date**: 2026-02-02

        ## 1. Epics Overview

        | ID | Epic | Status | Scope Doc | Priority |
        |----|------|--------|-----------|----------|
        | E1 | **Core Foundation** | ✅ Complete | `dev/epic-e1-scope.md` | — |
        | E2 | **Governance Toolkit** | ✅ Complete | `dev/epic-e2-scope.md` | — |
        | E3 | **Identity Core** | 📋 DRAFT | `dev/epic-e3-scope.md` | P0 |
        | E4 | **Deferred Feature** | Deferred | — | P2 |

        **F&F Scope (Feb 9):** E3 → E4
        """
    )

    backlog_file = tmp_path / "governance" / "backlog.md"
    backlog_file.parent.mkdir(parents=True, exist_ok=True)
    backlog_file.write_text(backlog_content)

    return backlog_file


class TestExtractProject:
    """Tests for extract_project function."""

    def test_extract_project_id(self, tmp_backlog_file: Path) -> None:
        """Should extract project with correct ID."""
        project = extract_project(
            tmp_backlog_file, tmp_backlog_file.parent.parent
        )

        assert project is not None
        assert project.id == "project-test-project"

    def test_extract_project_type(self, tmp_backlog_file: Path) -> None:
        """Should have PROJECT concept type."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.type == ConceptType.PROJECT

    def test_extract_project_name(self, tmp_backlog_file: Path) -> None:
        """Should extract project name from H1."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.metadata["name"] == "test-project"

    def test_extract_current_epic(self, tmp_backlog_file: Path) -> None:
        """Should extract current epic from F&F Scope line."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.metadata["current_epic"] == "E3"

    def test_extract_target_date(self, tmp_backlog_file: Path) -> None:
        """Should extract target date from F&F Scope."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.metadata["target_date"] == "Feb 9"

    def test_extract_epic_count(self, tmp_backlog_file: Path) -> None:
        """Should count epics in table."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.metadata["epic_count"] == 4

    def test_extract_status(self, tmp_backlog_file: Path) -> None:
        """Should extract status from frontmatter."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert project.metadata["status"] == "active"

    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        """Should return None for missing file."""
        missing_file = tmp_path / "missing.md"

        project = extract_project(missing_file)

        assert project is None

    def test_fallback_name_from_path(self, tmp_path: Path) -> None:
        """Should fallback to directory name if H1 missing."""
        backlog_content = dedent(
            """\
            ## Some heading without Backlog:

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E1 | Test | ✅ Complete | — | — |
            """
        )
        backlog_file = tmp_path / "governance" / "backlog.md"
        backlog_file.parent.mkdir(parents=True, exist_ok=True)
        backlog_file.write_text(backlog_content)

        project = extract_project(backlog_file)

        assert project is not None
        # Fallback extracts from parent dir name when no H1 header
        assert project.metadata["name"] == "governance"

    def test_content_includes_current_epic(self, tmp_backlog_file: Path) -> None:
        """Should include current epic in content summary."""
        project = extract_project(tmp_backlog_file)

        assert project is not None
        assert "E3" in project.content

    def test_relative_file_path(self, tmp_backlog_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_backlog_file.parent.parent
        project = extract_project(tmp_backlog_file, project_root)

        assert project is not None
        assert project.file == "governance/backlog.md"


class TestExtractEpics:
    """Tests for extract_epics function."""

    def test_extract_all_epics(self, tmp_backlog_file: Path) -> None:
        """Should extract all epics from table."""
        epics = extract_epics(tmp_backlog_file)

        assert len(epics) == 4

    def test_epic_type(self, tmp_backlog_file: Path) -> None:
        """Should have EPIC concept type."""
        epics = extract_epics(tmp_backlog_file)

        assert all(e.type == ConceptType.EPIC for e in epics)

    def test_epic_ids(self, tmp_backlog_file: Path) -> None:
        """Should generate correct IDs."""
        epics = extract_epics(tmp_backlog_file)

        ids = [e.id for e in epics]
        assert "epic-e1" in ids
        assert "epic-e2" in ids
        assert "epic-e3" in ids
        assert "epic-e4" in ids

    def test_epic_names(self, tmp_backlog_file: Path) -> None:
        """Should extract epic names without bold markers."""
        epics = extract_epics(tmp_backlog_file)

        e1 = next(e for e in epics if e.id == "epic-e1")
        assert e1.metadata["name"] == "Core Foundation"

    def test_epic_status_normalization(self, tmp_backlog_file: Path) -> None:
        """Should normalize epic statuses."""
        epics = extract_epics(tmp_backlog_file)

        e1 = next(e for e in epics if e.id == "epic-e1")
        assert e1.metadata["status"] == "complete"

        e3 = next(e for e in epics if e.id == "epic-e3")
        assert e3.metadata["status"] == "draft"

        e4 = next(e for e in epics if e.id == "epic-e4")
        assert e4.metadata["status"] == "deferred"

    def test_epic_scope_doc(self, tmp_backlog_file: Path) -> None:
        """Should extract scope doc path."""
        epics = extract_epics(tmp_backlog_file)

        e1 = next(e for e in epics if e.id == "epic-e1")
        assert e1.metadata["scope_doc"] == "dev/epic-e1-scope.md"

        e4 = next(e for e in epics if e.id == "epic-e4")
        assert e4.metadata["scope_doc"] is None

    def test_epic_priority(self, tmp_backlog_file: Path) -> None:
        """Should extract priority."""
        epics = extract_epics(tmp_backlog_file)

        e3 = next(e for e in epics if e.id == "epic-e3")
        assert e3.metadata["priority"] == "P0"

        e1 = next(e for e in epics if e.id == "epic-e1")
        assert e1.metadata["priority"] is None

    def test_epic_project_id(self, tmp_backlog_file: Path) -> None:
        """Should include project_id for relationship inference."""
        epics = extract_epics(tmp_backlog_file)

        for epic in epics:
            assert epic.metadata["project_id"] == "test-project"

    def test_epic_section(self, tmp_backlog_file: Path) -> None:
        """Should have correct section format."""
        epics = extract_epics(tmp_backlog_file)

        e1 = next(e for e in epics if e.id == "epic-e1")
        assert e1.section == "E1: Core Foundation"

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        epics = extract_epics(missing_file)

        assert epics == []

    def test_no_table_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list if no epic table found."""
        backlog_file = tmp_path / "no_table.md"
        backlog_file.write_text("# Backlog: test\n\nNo table here.")

        epics = extract_epics(backlog_file)

        assert epics == []

    def test_relative_file_path(self, tmp_backlog_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_backlog_file.parent.parent
        epics = extract_epics(tmp_backlog_file, project_root)

        for epic in epics:
            assert epic.file == "governance/backlog.md"


class TestIntegrationWithRealBacklog:
    """Integration tests with real raise-cli backlog."""

    def test_extract_project_from_real_backlog(self) -> None:
        """Should extract project from real raise-cli backlog."""
        backlog_path = Path("governance/backlog.md")

        if not backlog_path.exists():
            pytest.skip("Real backlog file not found")

        project = extract_project(backlog_path)

        assert project is not None
        assert project.id == "project-raise-cli"
        assert project.type == ConceptType.PROJECT
        assert project.metadata["name"] == "raise-cli"
        assert project.metadata["current_epic"] == "E7"

    def test_extract_epics_from_real_backlog(self) -> None:
        """Should extract all epics from real raise-cli backlog."""
        backlog_path = Path("governance/backlog.md")

        if not backlog_path.exists():
            pytest.skip("Real backlog file not found")

        epics = extract_epics(backlog_path)

        # Should have at least 12 epics (E1-E12+)
        assert len(epics) >= 12

        # Verify specific epics
        epic_ids = {e.metadata["epic_id"] for e in epics}
        assert "E1" in epic_ids
        assert "E8" in epic_ids
        assert "E12" in epic_ids

        # Verify statuses
        e1 = next(e for e in epics if e.metadata["epic_id"] == "E1")
        assert e1.metadata["status"] == "complete"

        e8 = next(e for e in epics if e.metadata["epic_id"] == "E8")
        assert e8.metadata["status"] == "complete"
