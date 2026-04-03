"""Tests for epic scope parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.epic import (
    extract_epic_details,
    extract_stories,
)


@pytest.fixture
def tmp_epic_file(tmp_path: Path) -> Path:
    """Create a temporary epic scope file for testing.

    Args:
        tmp_path: Pytest temp directory fixture.

    Returns:
        Path to temporary epic scope file.
    """
    epic_content = dedent(
        """\
        # Epic E8: Work Tracking Graph - Scope

        > **Status:** DRAFT
        > **Branch:** `feature/e8/work-tracking-graph`
        > **Created:** 2026-02-02
        > **Target:** Feb 9, 2026

        ---

        ## Objective

        Extend the governance graph to include work tracking concepts.

        ---

        ## Features

        | ID | Feature | Size | Status | Description |
        |----|---------|:----:|:------:|-------------|
        | F8.1 | Backlog Parser | S | Pending | Parse backlog.md |
        | F8.2 | **Epic Parser** | S | Pending | Parse epic scopes |
        | F8.3 | Graph Extension | M | Pending | Add work to graph |
        | F8.4 | Work Queries | S | **COMPLETE** | Query work items |
        """
    )

    epic_file = tmp_path / "work" / "epics" / "e08-backlog" / "scope.md"
    epic_file.parent.mkdir(parents=True, exist_ok=True)
    epic_file.write_text(epic_content)

    return epic_file


class TestExtractEpicDetails:
    """Tests for extract_epic_details function."""

    def test_extract_epic_id(self, tmp_epic_file: Path) -> None:
        """Should extract epic ID from parent directory."""
        # tmp_path / work / epics / e08-backlog / scope.md -> project_root is 4 levels up
        project_root = tmp_epic_file.parent.parent.parent.parent
        epic = extract_epic_details(tmp_epic_file, project_root)

        assert epic is not None
        assert epic.metadata["epic_id"] == "E08"

    def test_extract_epic_name(self, tmp_epic_file: Path) -> None:
        """Should extract epic name from H1."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.metadata["name"] == "Work Tracking Graph"

    def test_extract_concept_id(self, tmp_epic_file: Path) -> None:
        """Should generate correct concept ID."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.id == "epic-e08"

    def test_extract_concept_type(self, tmp_epic_file: Path) -> None:
        """Should have EPIC concept type."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.type == ConceptType.EPIC

    def test_extract_status(self, tmp_epic_file: Path) -> None:
        """Should extract status from frontmatter."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.metadata["status"] == "draft"

    def test_extract_target(self, tmp_epic_file: Path) -> None:
        """Should extract target date from frontmatter."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.metadata["target"] == "Feb 9, 2026"

    def test_extract_branch(self, tmp_epic_file: Path) -> None:
        """Should extract branch from frontmatter."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.metadata["branch"] == "`feature/e8/work-tracking-graph`"

    def test_extract_story_count(self, tmp_epic_file: Path) -> None:
        """Should count stories in table."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert epic.metadata["story_count"] == 4

    def test_extract_scope_doc(self, tmp_epic_file: Path) -> None:
        """Should include scope doc path in metadata."""
        # tmp_path / work / epics / e08-backlog / scope.md -> project_root is 4 levels up
        project_root = tmp_epic_file.parent.parent.parent.parent
        epic = extract_epic_details(tmp_epic_file, project_root)

        assert epic is not None
        assert epic.metadata["scope_doc"] == "work/epics/e08-backlog/scope.md"

    def test_content_includes_objective(self, tmp_epic_file: Path) -> None:
        """Should include objective in content."""
        epic = extract_epic_details(tmp_epic_file)

        assert epic is not None
        assert "work tracking" in epic.content.lower()

    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        """Should return None for missing file."""
        missing_file = tmp_path / "missing.md"

        epic = extract_epic_details(missing_file)

        assert epic is None

    def test_complete_status(self, tmp_path: Path) -> None:
        """Should normalize COMPLETE status."""
        epic_content = dedent(
            """\
            # Epic E3: Identity Core - Scope

            > **Status:** COMPLETE (100%)
            """
        )
        epic_file = tmp_path / "work" / "epics" / "e03-identity" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text(epic_content)

        epic = extract_epic_details(epic_file)

        assert epic is not None
        assert epic.metadata["status"] == "complete"

    def test_status_with_emoji(self, tmp_path: Path) -> None:
        """Should handle status with emoji."""
        epic_content = dedent(
            """\
            # Epic E2: Governance Toolkit - Scope

            > **Status:** COMPLETE ✅
            """
        )
        epic_file = tmp_path / "work" / "epics" / "e02-governance" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text(epic_content)

        epic = extract_epic_details(epic_file)

        assert epic is not None
        assert epic.metadata["status"] == "complete"


class TestExtractFeatures:
    """Tests for extract_stories function."""

    def test_extract_all_features(self, tmp_epic_file: Path) -> None:
        """Should extract all features from table."""
        features = extract_stories(tmp_epic_file)

        assert len(features) == 4

    def test_feature_type(self, tmp_epic_file: Path) -> None:
        """Should have FEATURE concept type."""
        features = extract_stories(tmp_epic_file)

        assert all(f.type == ConceptType.STORY for f in features)

    def test_story_ids(self, tmp_epic_file: Path) -> None:
        """Should generate correct feature IDs."""
        features = extract_stories(tmp_epic_file)

        ids = [f.id for f in features]
        assert "story-f8-1" in ids
        assert "story-f8-2" in ids
        assert "story-f8-3" in ids
        assert "story-f8-4" in ids

    def test_feature_names(self, tmp_epic_file: Path) -> None:
        """Should extract feature names without bold markers."""
        features = extract_stories(tmp_epic_file)

        f2 = next(f for f in features if f.id == "story-f8-2")
        assert f2.metadata["name"] == "Epic Parser"

    def test_feature_status_normalization(self, tmp_epic_file: Path) -> None:
        """Should normalize feature statuses."""
        features = extract_stories(tmp_epic_file)

        f1 = next(f for f in features if f.id == "story-f8-1")
        assert f1.metadata["status"] == "pending"

        f4 = next(f for f in features if f.id == "story-f8-4")
        assert f4.metadata["status"] == "complete"

    def test_feature_size(self, tmp_epic_file: Path) -> None:
        """Should extract feature size."""
        features = extract_stories(tmp_epic_file)

        f1 = next(f for f in features if f.id == "story-f8-1")
        assert f1.metadata["size"] == "S"

        f3 = next(f for f in features if f.id == "story-f8-3")
        assert f3.metadata["size"] == "M"

    def test_feature_epic_id(self, tmp_epic_file: Path) -> None:
        """Should include epic_id for relationship inference."""
        features = extract_stories(tmp_epic_file)

        for feature in features:
            assert feature.metadata["epic_id"] == "E08"

    def test_feature_section(self, tmp_epic_file: Path) -> None:
        """Should have correct section format."""
        features = extract_stories(tmp_epic_file)

        f1 = next(f for f in features if f.id == "story-f8-1")
        assert f1.section == "F8.1: Backlog Parser"

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        features = extract_stories(missing_file)

        assert features == []

    def test_sp_format_table(self, tmp_path: Path) -> None:
        """Should handle SP format table (E2 style)."""
        epic_content = dedent(
            """\
            # Epic E2: Governance Toolkit - Scope

            ## Features (9 SP)

            | ID | Feature | SP | Status | Actual Time | Velocity |
            |----|---------|:--:|:------:|:-----------:|:--------:|
            | F2.1 | Concept Extraction | 3 | ✅ Complete | 52 min | 3.5x |
            | F2.2 | Graph Builder | 2 | ✅ Complete | 65 min | 2.8x |
            """
        )
        epic_file = tmp_path / "work" / "epics" / "e02-governance" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text(epic_content)

        features = extract_stories(epic_file)

        assert len(features) == 2

        f1 = next(f for f in features if f.id == "story-f2-1")
        assert f1.metadata["sp"] == 3
        assert f1.metadata["status"] == "complete"

    def test_relative_file_path(self, tmp_epic_file: Path) -> None:
        """Should calculate correct relative file path."""
        # tmp_path / work / epics / e08-backlog / scope.md -> project_root is 4 levels up
        project_root = tmp_epic_file.parent.parent.parent.parent
        features = extract_stories(tmp_epic_file, project_root)

        for feature in features:
            assert feature.file == "work/epics/e08-backlog/scope.md"


class TestEpicIdPreservesOriginalNumber:
    """Tests that epic IDs preserve directory number without int() normalization.

    Regression: RAISE-1199, RAISE-1128, RAISE-648.
    e03-identity and e3-something must produce DIFFERENT node IDs.
    """

    def test_leading_zeros_preserved(self, tmp_path: Path) -> None:
        """e08-backlog should produce E08, not E8."""
        epic_file = tmp_path / "work" / "epics" / "e08-backlog" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text("# Epic E08: Backlog\n\n> **Status:** DRAFT\n")

        epic = extract_epic_details(epic_file)

        assert epic is not None
        assert epic.metadata["epic_id"] == "E08"
        assert epic.id == "epic-e08"

    def test_no_leading_zeros_unchanged(self, tmp_path: Path) -> None:
        """e8-backlog should produce E8."""
        epic_file = tmp_path / "work" / "epics" / "e8-backlog" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text("# Epic E8: Backlog\n\n> **Status:** DRAFT\n")

        epic = extract_epic_details(epic_file)

        assert epic is not None
        assert epic.metadata["epic_id"] == "E8"
        assert epic.id == "epic-e8"

    def test_no_collision_between_e03_and_e3(self, tmp_path: Path) -> None:
        """e03 and e3 directories must produce different IDs."""
        e03_file = tmp_path / "work" / "epics" / "e03-identity" / "scope.md"
        e03_file.parent.mkdir(parents=True, exist_ok=True)
        e03_file.write_text("# Epic E03: Identity\n\n> **Status:** COMPLETE\n")

        e3_file = tmp_path / "work" / "epics" / "e3-something" / "scope.md"
        e3_file.parent.mkdir(parents=True, exist_ok=True)
        e3_file.write_text("# Epic E3: Something\n\n> **Status:** DRAFT\n")

        epic_03 = extract_epic_details(e03_file)
        epic_3 = extract_epic_details(e3_file)

        assert epic_03 is not None
        assert epic_3 is not None
        assert epic_03.id != epic_3.id, (
            f"COLLISION: {epic_03.id} == {epic_3.id} — "
            f"e03 and e3 must produce different node IDs"
        )

    def test_four_digit_ids_preserved(self, tmp_path: Path) -> None:
        """e1134-cc-alignment should produce E1134."""
        epic_file = tmp_path / "work" / "epics" / "e1134-cc-alignment" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text("# Epic E1134: CC Alignment\n\n> **Status:** DRAFT\n")

        epic = extract_epic_details(epic_file)

        assert epic is not None
        assert epic.metadata["epic_id"] == "E1134"
        assert epic.id == "epic-e1134"

    def test_stories_inherit_preserved_epic_id(self, tmp_path: Path) -> None:
        """Stories should use the preserved (non-normalized) epic ID."""
        epic_content = (
            "# Epic E03: Identity\n\n"
            "## Stories\n\n"
            "| ID | Story | Size | Status |\n"
            "|----|-------|:----:|:------:|\n"
            "| F3.1 | Core | S | Pending |\n"
        )
        epic_file = tmp_path / "work" / "epics" / "e03-identity" / "scope.md"
        epic_file.parent.mkdir(parents=True, exist_ok=True)
        epic_file.write_text(epic_content)

        stories = extract_stories(epic_file)

        assert len(stories) >= 1
        assert stories[0].metadata["epic_id"] == "E03"


class TestIntegrationWithRealEpics:
    """Integration tests with real epic scope documents."""

    def test_extract_details_from_real_e3(self) -> None:
        """Should extract details from real E3 scope."""
        scope_path = Path("work/epics/e03-identity/scope.md")

        if not scope_path.exists():
            pytest.skip("Real epic scope file not found")

        epic = extract_epic_details(scope_path)

        assert epic is not None
        assert epic.id == "epic-e03"
        assert epic.type == ConceptType.EPIC
        assert epic.metadata["epic_id"] == "E03"
        assert "Identity" in epic.metadata["name"]

    def test_extract_stories_from_real_e3(self) -> None:
        """Should extract features from real E3 scope."""
        scope_path = Path("work/epics/e03-identity/scope.md")

        if not scope_path.exists():
            pytest.skip("Real epic scope file not found")

        features = extract_stories(scope_path)

        # E3 has 5 features (F3.1-F3.5)
        assert len(features) >= 4

        story_ids = {f.metadata["story_id"] for f in features}
        assert "F3.1" in story_ids

    def test_extract_all_real_epics(self) -> None:
        """Should extract details from all real epic scopes."""
        epic_files = list(Path("work/epics").glob("*/scope.md"))

        if not epic_files:
            pytest.skip("No real epic scope files found")

        for epic_file in epic_files:
            epic = extract_epic_details(epic_file)
            assert epic is not None, f"Failed to parse {epic_file}"
            assert epic.type == ConceptType.EPIC
            assert epic.metadata["epic_id"] is not None
