"""Tests for artifact Markdown renderer."""

from __future__ import annotations

from datetime import UTC, datetime

from raise_cli.artifacts.renderer import render_artifact
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    Decision,
    IntegrationPoint,
    StoryDesignArtifact,
    StoryDesignContent,
)


def _make_full_artifact() -> StoryDesignArtifact:
    return StoryDesignArtifact(
        skill="rai-story-design",
        created=datetime(2026, 3, 3, 10, 0, 0, tzinfo=UTC),
        story="S354.1",
        epic="E354",
        content=StoryDesignContent(
            summary="Base artifact model",
            complexity=Complexity.SIMPLE,
            acceptance_criteria=[
                AcceptanceCriterion(id="AC1", description="Model validates"),
                AcceptanceCriterion(id="AC2", description="Writer works"),
            ],
            integration_points=[
                IntegrationPoint(
                    module="raise_cli.artifacts",
                    change_type="new",
                    files=["src/raise_cli/artifacts/models.py"],
                ),
            ],
            decisions=[
                Decision(
                    id="D1",
                    choice="Flat YAML",
                    rationale="Simple serialization",
                    alternatives_considered=["Nested", "TOML"],
                ),
            ],
        ),
    )


def _make_minimal_artifact() -> StoryDesignArtifact:
    return StoryDesignArtifact(
        skill="rai-story-design",
        created=datetime(2026, 3, 3, 10, 0, 0, tzinfo=UTC),
        story="S354.2",
        epic="E354",
        content=StoryDesignContent(
            summary="Minimal story",
            complexity=Complexity.SIMPLE,
            acceptance_criteria=[
                AcceptanceCriterion(id="AC1", description="It works"),
            ],
        ),
    )


class TestRenderArtifact:
    def test_title_and_metadata(self) -> None:
        md = render_artifact(_make_full_artifact())
        assert "# S354.1 Design: Base artifact model" in md
        assert "**Story:** S354.1" in md
        assert "**Epic:** E354" in md
        assert "**Complexity:** simple" in md
        assert "**Skill:** rai-story-design" in md

    def test_summary_section(self) -> None:
        md = render_artifact(_make_full_artifact())
        assert "## Summary" in md
        assert "Base artifact model" in md

    def test_acceptance_criteria_numbered(self) -> None:
        md = render_artifact(_make_full_artifact())
        assert "1. [AC1] Model validates" in md
        assert "2. [AC2] Writer works" in md

    def test_integration_points(self) -> None:
        md = render_artifact(_make_full_artifact())
        assert "## Integration Points" in md
        assert "`raise_cli.artifacts`" in md
        assert "new" in md

    def test_decisions_with_rationale(self) -> None:
        md = render_artifact(_make_full_artifact())
        assert "### D1: Flat YAML" in md
        assert "**Rationale:** Simple serialization" in md
        assert "Nested" in md

    def test_empty_sections_omitted(self) -> None:
        md = render_artifact(_make_minimal_artifact())
        assert "## Integration Points" not in md
        assert "## Decisions" not in md

    def test_ac_section_always_present(self) -> None:
        md = render_artifact(_make_minimal_artifact())
        assert "## Acceptance Criteria" in md
        assert "1. [AC1] It works" in md
