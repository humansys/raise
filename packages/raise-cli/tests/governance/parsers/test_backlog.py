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
        project = extract_project(tmp_backlog_file, tmp_backlog_file.parent.parent)

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


class TestJiraLinkFormat:
    """Tests for epics with [RAISE-XXX](url) ID format."""

    @pytest.fixture
    def mixed_backlog(self, tmp_path: Path) -> Path:
        backlog_content = dedent(
            """\
            # Backlog: test-project

            > **Status**: Active

            ## 1. Epics Overview

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E1 | **Core Foundation** | ✅ Complete | `scope.md` | — |
            | [RAISE-275](https://example.atlassian.net/browse/RAISE-275) | **Shared Memory Backend** | ✅ Complete | `work/epics/e275/scope.md` | — |
            | [RAISE-301](https://example.atlassian.net/browse/RAISE-301) | **Agent Tool Abstraction** | 🚀 In Progress | `work/epics/e301/scope.md` | P0 |
            | [RAISE-325](https://example.atlassian.net/browse/RAISE-325) | **Agent-Orchestrated Workflow** | 📋 Backlog | — | P1 |
            """
        )
        backlog_file = tmp_path / "governance" / "backlog.md"
        backlog_file.parent.mkdir(parents=True, exist_ok=True)
        backlog_file.write_text(backlog_content)
        return backlog_file

    def test_extracts_jira_link_epics(self, mixed_backlog: Path) -> None:
        epics = extract_epics(mixed_backlog)
        ids = {e.metadata["epic_id"] for e in epics}
        assert "E1" in ids
        assert "RAISE-275" in ids
        assert "RAISE-301" in ids
        assert "RAISE-325" in ids

    def test_total_count_includes_both_formats(self, mixed_backlog: Path) -> None:
        epics = extract_epics(mixed_backlog)
        assert len(epics) == 4

    def test_jira_link_epic_metadata(self, mixed_backlog: Path) -> None:
        epics = extract_epics(mixed_backlog)
        e301 = next(e for e in epics if e.metadata["epic_id"] == "RAISE-301")
        assert e301.metadata["name"] == "Agent Tool Abstraction"
        assert e301.metadata["status"] == "in_progress"
        assert e301.metadata["scope_doc"] == "work/epics/e301/scope.md"
        assert e301.metadata["priority"] == "P0"

    def test_jira_link_epic_id_format(self, mixed_backlog: Path) -> None:
        epics = extract_epics(mixed_backlog)
        e275 = next(e for e in epics if e.metadata["epic_id"] == "RAISE-275")
        assert e275.id == "epic-raise-275"

    def test_epic_count_in_project(self, mixed_backlog: Path) -> None:
        project = extract_project(mixed_backlog, mixed_backlog.parent.parent)
        assert project is not None
        assert project.metadata["epic_count"] == 4


class TestScopeDocSkipLogic:
    """Tests for RAISE-456: skip backlog epics when scope doc exists."""

    def test_skips_simple_id_when_scope_exists(self, tmp_path: Path) -> None:
        """E1 in backlog should be skipped when work/epics/e1-*/scope.md exists."""
        backlog = tmp_path / "governance" / "backlog.md"
        backlog.parent.mkdir(parents=True)
        backlog.write_text(
            dedent("""\
            # Backlog: test

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E1 | **Feature One** | Active | — | P0 |
            | E2 | **Feature Two** | Active | — | P1 |
        """)
        )
        # Only E1 has a scope doc
        scope = tmp_path / "work" / "epics" / "e1-feature" / "scope.md"
        scope.parent.mkdir(parents=True)
        scope.write_text("# Epic E1: Feature One - Scope\n")

        epics = extract_epics(backlog, tmp_path)
        epic_ids = {e.metadata["epic_id"] for e in epics}
        assert "E1" not in epic_ids, "E1 should be skipped — scope doc exists"
        assert "E2" in epic_ids, "E2 should remain — no scope doc"

    def test_skips_padded_id_when_dir_has_no_leading_zero(self, tmp_path: Path) -> None:
        """E08 in backlog + dir e8-feature/ (no leading zero) should still skip.

        EpicScopeParser normalizes e08 → E8 (int strips leading zero).
        BacklogParser must canonicalize the same way to detect the collision.
        """
        backlog = tmp_path / "governance" / "backlog.md"
        backlog.parent.mkdir(parents=True)
        backlog.write_text(
            dedent("""\
            # Backlog: test

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E08 | **Padded Epic** | Active | — | P0 |
        """)
        )
        # Dir named e8-feature (no leading zero) — still the same epic
        scope = tmp_path / "work" / "epics" / "e8-feature" / "scope.md"
        scope.parent.mkdir(parents=True)
        scope.write_text("# Epic E8: Padded Epic - Scope\n")

        epics = extract_epics(backlog, tmp_path)
        epic_ids = {e.metadata["epic_id"] for e in epics}
        assert "E08" not in epic_ids, (
            "E08 should be skipped — e8-feature/scope.md covers same epic"
        )

    def test_no_skip_for_jira_key_even_if_num_matches(self, tmp_path: Path) -> None:
        r"""RAISE-275 should NOT be skipped even if e275-*/scope.md exists.

        Jira keys produce a different node ID namespace (epic-raise-275 vs epic-e275).
        The naive re.sub(r'\D', '', id) approach wrongly extracts '275' and skips.
        """
        backlog = tmp_path / "governance" / "backlog.md"
        backlog.parent.mkdir(parents=True)
        backlog.write_text(
            dedent("""\
            # Backlog: test

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | [RAISE-275](https://jira.example.com/RAISE-275) | **Jira Epic** | Active | — | P0 |
        """)
        )
        # Coincidental e275 dir exists
        scope = tmp_path / "work" / "epics" / "e275-something" / "scope.md"
        scope.parent.mkdir(parents=True)
        scope.write_text("# Epic E275\n")

        epics = extract_epics(backlog, tmp_path)
        epic_ids = {e.metadata["epic_id"] for e in epics}
        assert "RAISE-275" in epic_ids, (
            "Jira key should never be skipped by scope doc logic"
        )

    def test_no_skip_when_no_scope_doc(self, tmp_path: Path) -> None:
        """E1 without scope doc should NOT be skipped."""
        backlog = tmp_path / "governance" / "backlog.md"
        backlog.parent.mkdir(parents=True)
        backlog.write_text(
            dedent("""\
            # Backlog: test

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E1 | **No Scope Yet** | Draft | — | P0 |
        """)
        )
        # No scope docs at all

        epics = extract_epics(backlog, tmp_path)
        assert len(epics) == 1
        assert epics[0].metadata["epic_id"] == "E1"


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
        # current_epic depends on F&F Scope / Epic: markers in backlog
        # None is valid when no such marker exists
        assert project.metadata["current_epic"] is None or isinstance(
            project.metadata["current_epic"], str
        )

    def test_extract_epics_from_real_backlog(self) -> None:
        """Should extract epics without scope docs from real raise-cli backlog.

        Epics with scope docs (work/epics/e{N}-*/scope.md) are delegated to
        EpicScopeParser and correctly skipped here.
        """
        backlog_path = Path("governance/backlog.md")

        if not backlog_path.exists():
            pytest.skip("Real backlog file not found")

        epics = extract_epics(backlog_path)

        # Some epics should be extracted (those without scope docs)
        assert len(epics) >= 1

        # Epics with scope docs should NOT appear (delegated to EpicScopeParser)
        epic_ids = {e.metadata["epic_id"] for e in epics}
        scope_dirs = list(Path("work/epics").glob("e*"))
        for scope_dir in scope_dirs:
            if (scope_dir / "scope.md").exists():
                import re as _re

                m = _re.search(r"^e0*(\d+)", scope_dir.name, _re.IGNORECASE)
                if m:
                    local_id = f"E{int(m.group(1))}"
                    assert local_id not in epic_ids, (
                        f"{local_id} has scope doc — should be skipped"
                    )
