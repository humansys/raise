"""Tests for roadmap parser."""

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.governance.models import ConceptType
from raise_cli.governance.parsers.roadmap import extract_releases

ROADMAP_CONTENT = dedent(
    """\
    # Roadmap: raise-cli

    > **Status:** Active
    > **Date:** 2026-02-13

    ---

    ## Releases

    | ID | Release | Target | Status | Epics |
    |----|---------|--------|--------|-------|
    | REL-V2.0 | V2.0 Open Core | 2026-02-15 | In Progress | E18 |
    | REL-V3.0 | V3.0 Commercial Launch | 2026-03-14 | Planning | E19, E20, E21, E22 |

    ---

    ## REL-V3.0: V3.0 Commercial Launch

    > **Target:** 2026-03-14
    > **Status:** Planning
    > **Objective:** BYOK trial offering with COMMUNITY/PRO/ENTERPRISE tiers

    ### Epics
    - E19: V3 Product Design
    - E20: Shared Memory Architecture
    - E21: Platform Integration
    - E22: Enterprise Readiness
    """
)


@pytest.fixture
def tmp_roadmap_file(tmp_path: Path) -> Path:
    """Create a temporary roadmap file for testing."""
    roadmap_file = tmp_path / "governance" / "roadmap.md"
    roadmap_file.parent.mkdir(parents=True, exist_ok=True)
    roadmap_file.write_text(ROADMAP_CONTENT)
    return roadmap_file


class TestExtractReleases:
    """Tests for extract_releases function."""

    def test_extracts_all_releases(self, tmp_roadmap_file: Path) -> None:
        """Should extract both releases from table."""
        releases = extract_releases(tmp_roadmap_file)

        assert len(releases) == 2

    def test_release_type(self, tmp_roadmap_file: Path) -> None:
        """Should have RELEASE concept type."""
        releases = extract_releases(tmp_roadmap_file)

        assert all(r.type == ConceptType.RELEASE for r in releases)

    def test_release_ids(self, tmp_roadmap_file: Path) -> None:
        """Should generate lowercase IDs."""
        releases = extract_releases(tmp_roadmap_file)

        ids = [r.id for r in releases]
        assert "rel-v2.0" in ids
        assert "rel-v3.0" in ids

    def test_release_names(self, tmp_roadmap_file: Path) -> None:
        """Should extract release names from table."""
        releases = extract_releases(tmp_roadmap_file)

        v2 = next(r for r in releases if r.id == "rel-v2.0")
        assert v2.metadata["name"] == "V2.0 Open Core"

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert v3.metadata["name"] == "V3.0 Commercial Launch"

    def test_release_targets(self, tmp_roadmap_file: Path) -> None:
        """Should extract target dates."""
        releases = extract_releases(tmp_roadmap_file)

        v2 = next(r for r in releases if r.id == "rel-v2.0")
        assert v2.metadata["target"] == "2026-02-15"

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert v3.metadata["target"] == "2026-03-14"

    def test_status_normalization(self, tmp_roadmap_file: Path) -> None:
        """Should normalize statuses to lowercase."""
        releases = extract_releases(tmp_roadmap_file)

        v2 = next(r for r in releases if r.id == "rel-v2.0")
        assert v2.metadata["status"] == "in_progress"

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert v3.metadata["status"] == "planning"

    def test_epics_parsing(self, tmp_roadmap_file: Path) -> None:
        """Should parse epics column into list."""
        releases = extract_releases(tmp_roadmap_file)

        v2 = next(r for r in releases if r.id == "rel-v2.0")
        assert v2.metadata["epics"] == ["E18"]

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert v3.metadata["epics"] == ["E19", "E20", "E21", "E22"]

    def test_release_content(self, tmp_roadmap_file: Path) -> None:
        """Should build content summary."""
        releases = extract_releases(tmp_roadmap_file)

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert "V3.0 Commercial Launch" in v3.content
        assert "Planning" in v3.content
        assert "2026-03-14" in v3.content

    def test_release_section(self, tmp_roadmap_file: Path) -> None:
        """Should have correct section format."""
        releases = extract_releases(tmp_roadmap_file)

        v3 = next(r for r in releases if r.id == "rel-v3.0")
        assert v3.section == "REL-V3.0: V3.0 Commercial Launch"

    def test_release_id_in_metadata(self, tmp_roadmap_file: Path) -> None:
        """Should include original release ID in metadata."""
        releases = extract_releases(tmp_roadmap_file)

        v2 = next(r for r in releases if r.id == "rel-v2.0")
        assert v2.metadata["release_id"] == "REL-V2.0"

    def test_relative_file_path(self, tmp_roadmap_file: Path) -> None:
        """Should calculate correct relative file path."""
        project_root = tmp_roadmap_file.parent.parent
        releases = extract_releases(tmp_roadmap_file, project_root)

        for release in releases:
            assert release.file == "governance/roadmap.md"

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list for missing file."""
        missing_file = tmp_path / "missing.md"

        releases = extract_releases(missing_file)

        assert releases == []

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list for empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        releases = extract_releases(empty_file)

        assert releases == []

    def test_no_table_returns_empty(self, tmp_path: Path) -> None:
        """Should return empty list if no release table found."""
        no_table = tmp_path / "no_table.md"
        no_table.write_text("# Roadmap: test\n\nNo table here.")

        releases = extract_releases(no_table)

        assert releases == []

    def test_empty_epics_column(self, tmp_path: Path) -> None:
        """Should handle empty epics column gracefully."""
        content = dedent(
            """\
            # Roadmap: test

            ## Releases

            | ID | Release | Target | Status | Epics |
            |----|---------|--------|--------|-------|
            | REL-V1.0 | V1.0 MVP | 2026-01-01 | Complete | |
            """
        )
        roadmap_file = tmp_path / "roadmap.md"
        roadmap_file.write_text(content)

        releases = extract_releases(roadmap_file)

        assert len(releases) == 1
        assert releases[0].metadata["epics"] == []
