"""Tests for learning record model and I/O."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from raise_cli.memory.learning import (
    LearningRecord,
    PatternVote,
    read_record,
    write_record,
)


class TestPatternVote:
    """Tests for PatternVote model."""

    def test_valid_positive_vote(self) -> None:
        """Positive vote (+1) with why is valid."""
        vote = PatternVote(vote=1, why="Pattern was directly applicable")
        assert vote.vote == 1
        assert vote.why == "Pattern was directly applicable"

    def test_valid_negative_vote(self) -> None:
        """Negative vote (-1) with why is valid."""
        vote = PatternVote(vote=-1, why="Pattern was misleading in this context")
        assert vote.vote == -1

    def test_valid_neutral_vote(self) -> None:
        """Neutral vote (0) with why is valid."""
        vote = PatternVote(vote=0, why="Not relevant to this task")
        assert vote.vote == 0

    def test_why_is_required(self) -> None:
        """PatternVote requires a why field."""
        with pytest.raises(Exception):  # noqa: B017 — pydantic ValidationError
            PatternVote(vote=1, why="")  # min_length=1

    def test_why_cannot_be_missing(self) -> None:
        """PatternVote requires why field to be present."""
        with pytest.raises(Exception):  # noqa: B017
            PatternVote(vote=1)  # type: ignore[call-arg]

    def test_invalid_vote_value(self) -> None:
        """Vote values outside -1, 0, 1 are rejected."""
        with pytest.raises(Exception):  # noqa: B017
            PatternVote(vote=2, why="invalid")  # type: ignore[arg-type]


class TestLearningRecord:
    """Tests for LearningRecord model."""

    def _make_record(self, **overrides: object) -> LearningRecord:
        """Create a valid learning record with optional overrides."""
        defaults: dict[str, object] = {
            "skill": "rai-story-design",
            "work_id": "S1133.1",
            "version": "2.4.0",
            "timestamp": datetime(2026, 4, 1, 9, 15, 0, tzinfo=timezone.utc),
        }
        defaults.update(overrides)
        return LearningRecord(**defaults)  # type: ignore[arg-type]

    def test_minimal_record(self) -> None:
        """Minimal record with required fields only."""
        record = self._make_record()
        assert record.skill == "rai-story-design"
        assert record.work_id == "S1133.1"
        assert record.version == "2.4.0"

    def test_defaults_are_empty(self) -> None:
        """Optional fields default to empty collections or None."""
        record = self._make_record()
        assert record.primed_patterns == []
        assert record.tier1_queries == 0
        assert record.tier1_results == 0
        assert record.jit_queries == 0
        assert record.pattern_votes == {}
        assert record.gaps == []
        assert record.artifacts == []
        assert record.commit is None
        assert record.branch is None
        assert record.downstream == {}

    def test_full_record(self) -> None:
        """Full record with all fields populated."""
        record = self._make_record(
            primed_patterns=["PAT-E-590"],
            tier1_queries=2,
            tier1_results=2,
            jit_queries=1,
            pattern_votes={
                "PAT-E-590": PatternVote(
                    vote=1, why="hook extension pattern informed design"
                )
            },
            gaps=["No patterns for aspect-oriented composition"],
            artifacts=["s1133.1-design.md"],
            commit="abc123",
            branch="story/s1133.1/introspection-aspect",
            downstream={"plan_derivable": True},
        )
        assert record.primed_patterns == ["PAT-E-590"]
        assert record.tier1_queries == 2
        assert record.pattern_votes["PAT-E-590"].vote == 1
        assert len(record.gaps) == 1
        assert record.downstream["plan_derivable"] is True

    def test_downstream_is_open_dict(self) -> None:
        """Downstream field accepts arbitrary dict values (AR-R2)."""
        record = self._make_record(
            downstream={
                "plan_derivable": True,
                "tasks_clear": True,
                "custom_metric": 42,
                "nested": {"key": "value"},
            }
        )
        assert record.downstream["custom_metric"] == 42
        assert record.downstream["nested"]["key"] == "value"

    def test_tier1_queries_non_negative(self) -> None:
        """tier1_queries must be >= 0."""
        with pytest.raises(Exception):  # noqa: B017
            self._make_record(tier1_queries=-1)


class TestWriteRecord:
    """Tests for write_record function."""

    def test_creates_yaml_at_correct_path(self, tmp_path: Path) -> None:
        """write_record creates YAML at .raise/rai/learnings/{skill}/{work_id}/record.yaml."""
        record = LearningRecord(
            skill="rai-story-design",
            work_id="S1133.1",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 9, 15, 0, tzinfo=timezone.utc),
        )
        result_path = write_record(record, tmp_path)
        expected = tmp_path / ".raise" / "rai" / "learnings" / "rai-story-design" / "S1133.1" / "record.yaml"
        assert result_path == expected
        assert result_path.exists()

    def test_creates_directories(self, tmp_path: Path) -> None:
        """write_record creates intermediate directories."""
        record = LearningRecord(
            skill="rai-epic-plan",
            work_id="E1133",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 9, 15, 0, tzinfo=timezone.utc),
        )
        result_path = write_record(record, tmp_path)
        assert result_path.parent.is_dir()

    def test_output_is_valid_yaml(self, tmp_path: Path) -> None:
        """Written file is valid YAML."""
        record = LearningRecord(
            skill="rai-story-design",
            work_id="S1133.1",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 9, 15, 0, tzinfo=timezone.utc),
            primed_patterns=["PAT-001"],
            pattern_votes={
                "PAT-001": PatternVote(vote=1, why="useful")
            },
        )
        result_path = write_record(record, tmp_path)
        data = yaml.safe_load(result_path.read_text(encoding="utf-8"))
        assert data["skill"] == "rai-story-design"
        assert data["primed_patterns"] == ["PAT-001"]
        assert data["pattern_votes"]["PAT-001"]["vote"] == 1

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        """Rework overwrites existing record."""
        record1 = LearningRecord(
            skill="rai-story-design",
            work_id="S1133.1",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 9, 0, 0, tzinfo=timezone.utc),
            gaps=["gap1"],
        )
        record2 = LearningRecord(
            skill="rai-story-design",
            work_id="S1133.1",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 10, 0, 0, tzinfo=timezone.utc),
            gaps=["gap2"],
        )
        write_record(record1, tmp_path)
        result_path = write_record(record2, tmp_path)
        data = yaml.safe_load(result_path.read_text(encoding="utf-8"))
        assert data["gaps"] == ["gap2"]


class TestReadRecord:
    """Tests for read_record function."""

    def test_returns_none_for_missing(self, tmp_path: Path) -> None:
        """read_record returns None for non-existent record."""
        result = read_record("rai-story-design", "S9999", tmp_path)
        assert result is None

    def test_round_trip(self, tmp_path: Path) -> None:
        """Write then read produces equivalent record."""
        original = LearningRecord(
            skill="rai-story-design",
            work_id="S1133.1",
            version="2.4.0",
            timestamp=datetime(2026, 4, 1, 9, 15, 0, tzinfo=timezone.utc),
            primed_patterns=["PAT-E-590"],
            tier1_queries=2,
            tier1_results=2,
            jit_queries=1,
            pattern_votes={
                "PAT-E-590": PatternVote(vote=1, why="useful pattern")
            },
            gaps=["No aspect patterns found"],
            artifacts=["s1133.1-design.md"],
            commit="abc123",
            branch="story/s1133.1/foo",
            downstream={"plan_derivable": True},
        )
        write_record(original, tmp_path)
        loaded = read_record("rai-story-design", "S1133.1", tmp_path)

        assert loaded is not None
        assert loaded == original

    def test_returns_none_on_corrupted_file(self, tmp_path: Path) -> None:
        """read_record returns None for corrupted YAML."""
        path = tmp_path / ".raise" / "rai" / "learnings" / "skill" / "work" / "record.yaml"
        path.parent.mkdir(parents=True)
        path.write_text("{{invalid yaml: [", encoding="utf-8")
        result = read_record("skill", "work", tmp_path)
        assert result is None
