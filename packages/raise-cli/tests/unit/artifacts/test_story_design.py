"""Tests for story-design artifact schema and governance validators."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from raise_cli.artifacts.models import ArtifactType
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    Decision,
    IntegrationPoint,
    StoryDesignArtifact,
    StoryDesignContent,
)

# --- Sub-models ---


class TestComplexity:
    def test_values(self) -> None:
        assert Complexity.SIMPLE == "simple"
        assert Complexity.MODERATE == "moderate"
        assert Complexity.COMPLEX == "complex"


class TestAcceptanceCriterion:
    def test_creation(self) -> None:
        ac = AcceptanceCriterion(id="AC1", description="CLI produces YAML")
        assert ac.verifiable is True

    def test_verifiable_can_be_false(self) -> None:
        ac = AcceptanceCriterion(
            id="AC2", description="UX feels natural", verifiable=False
        )
        assert ac.verifiable is False


class TestIntegrationPoint:
    def test_creation(self) -> None:
        ip = IntegrationPoint(
            module="raise_cli.artifacts",
            change_type="new",
            files=["src/raise_cli/artifacts/story_design.py"],
        )
        assert ip.module == "raise_cli.artifacts"
        assert ip.change_type == "new"


class TestDecision:
    def test_creation(self) -> None:
        d = Decision(
            id="D1",
            choice="Pydantic validators",
            rationale="Simple, no engine needed",
        )
        assert d.alternatives_considered == []

    def test_with_alternatives(self) -> None:
        d = Decision(
            id="D1",
            choice="X",
            rationale="Y",
            alternatives_considered=["A", "B"],
        )
        assert len(d.alternatives_considered) == 2


# --- StoryDesignContent ---


class TestStoryDesignContent:
    def _make_content(self, **overrides) -> StoryDesignContent:
        defaults = {
            "summary": "Base artifact model",
            "complexity": Complexity.SIMPLE,
            "acceptance_criteria": [
                AcceptanceCriterion(id="AC1", description="Model validates"),
                AcceptanceCriterion(id="AC2", description="Writer works"),
            ],
        }
        defaults.update(overrides)
        return StoryDesignContent(**defaults)

    def test_creation_with_required_fields(self) -> None:
        content = self._make_content()
        assert content.summary == "Base artifact model"
        assert content.complexity == Complexity.SIMPLE
        assert len(content.acceptance_criteria) == 2
        assert content.integration_points == []
        assert content.decisions == []

    def test_ac_count_min_1(self) -> None:
        with pytest.raises(ValidationError, match="at least 1"):
            self._make_content(acceptance_criteria=[])

    def test_ac_count_max_10(self) -> None:
        many_ac = [
            AcceptanceCriterion(id=f"AC{i}", description=f"Criterion {i}")
            for i in range(11)
        ]
        with pytest.raises(ValidationError, match="at most 10"):
            self._make_content(acceptance_criteria=many_ac)

    def test_decisions_must_have_rationale(self) -> None:
        with pytest.raises(ValidationError, match="rationale"):
            self._make_content(
                decisions=[
                    Decision(id="D1", choice="X", rationale=""),
                ]
            )

    def test_valid_decisions_pass(self) -> None:
        content = self._make_content(
            decisions=[
                Decision(id="D1", choice="X", rationale="Because Y"),
            ]
        )
        assert len(content.decisions) == 1


# --- StoryDesignArtifact ---


class TestStoryDesignArtifact:
    def test_artifact_type_locked(self, sample_created: datetime) -> None:
        artifact = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            story="S354.2",
            content=StoryDesignContent(
                summary="Test",
                complexity=Complexity.SIMPLE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Works"),
                ],
            ),
        )
        assert artifact.artifact_type == ArtifactType.STORY_DESIGN

    def test_content_is_typed(self, sample_created: datetime) -> None:
        artifact = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            content=StoryDesignContent(
                summary="Test",
                complexity=Complexity.MODERATE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Works"),
                ],
            ),
        )
        assert isinstance(artifact.content, StoryDesignContent)
        assert artifact.content.complexity == Complexity.MODERATE

    def test_model_dump_includes_typed_content(self, sample_created: datetime) -> None:
        artifact = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            content=StoryDesignContent(
                summary="Test",
                complexity=Complexity.SIMPLE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Works"),
                ],
            ),
        )
        data = artifact.model_dump()
        assert data["content"]["complexity"] == "simple"
        assert data["content"]["acceptance_criteria"][0]["id"] == "AC1"
