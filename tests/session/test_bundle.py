"""Tests for context bundle assembly."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

from raise_cli.context.models import ConceptNode
from raise_cli.onboarding.profile import (
    CoachingContext,
    Correction,
    Deadline,
    DeveloperProfile,
    ExperienceLevel,
)
from raise_cli.schemas.session_state import (
    CurrentWork,
    LastSession,
    PendingItems,
    SessionState,
)
from raise_cli.session.bundle import (
    assemble_context_bundle,
    get_foundational_patterns,
)


def _make_profile() -> DeveloperProfile:
    """Create a typical profile for testing."""
    return DeveloperProfile(
        name="Emilio",
        experience_level=ExperienceLevel.RI,
        coaching=CoachingContext(
            strengths=["architecture", "naming"],
            growth_edge="speed over process",
            corrections=[
                Correction(
                    session="SES-096",
                    what="Offered to skip design",
                    lesson="Knowledge != behavior",
                ),
                Correction(
                    session="SES-097",
                    what="Defaulted to speed",
                    lesson="Reliability > velocity",
                ),
            ],
        ),
        deadlines=[
            Deadline(name="F&F", date=date(2026, 2, 9)),
            Deadline(name="Launch", date=date(2026, 2, 15)),
        ],
    )


def _make_state() -> SessionState:
    """Create a typical session state for testing."""
    return SessionState(
        current_work=CurrentWork(
            epic="E15",
            story="S15.7",
            phase="implement",
            branch="story/s15.7/session-protocol",
        ),
        last_session=LastSession(
            id="SES-097",
            date=date(2026, 2, 8),
            developer="Emilio",
            summary="session protocol design",
            patterns_captured=["PAT-187", "PAT-188"],
        ),
        pending=PendingItems(
            decisions=["Pattern curation"],
            next_actions=["Implement session-state schema"],
        ),
    )


def _make_pattern(pat_id: str, content: str) -> ConceptNode:
    """Create a mock foundational pattern node."""
    return ConceptNode(
        id=pat_id,
        type="pattern",
        content=content,
        source_file=".raise/rai/memory/patterns.jsonl",
        created="2026-02-08",
        metadata={"foundational": True},
    )


class TestAssembleContextBundle:
    """Tests for assemble_context_bundle."""

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_full_bundle_contains_all_sections(
        self, mock_patterns: object
    ) -> None:
        """Full bundle contains developer, work, deadlines, primes, coaching, pending."""
        assert callable(mock_patterns)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba — observe before designing"),
        ]

        profile = _make_profile()
        state = _make_state()
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Session Context" in bundle
        assert "Developer: Emilio (ri)" in bundle
        assert "Story: S15.7 [implement]" in bundle
        assert "Epic: E15" in bundle
        assert "SES-097" in bundle
        assert "# Deadlines" in bundle
        assert "F&F" in bundle
        assert "# Behavioral Primes" in bundle
        assert "PAT-187" in bundle
        assert "# Coaching" in bundle
        assert "architecture" in bundle
        assert "# Pending" in bundle
        assert "Pattern curation" in bundle

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_without_state(self, mock_patterns: object) -> None:
        """Bundle without session state is graceful."""
        assert callable(mock_patterns)
        mock_patterns.return_value = []

        profile = DeveloperProfile(name="New")
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "Developer: New (shu)" in bundle
        assert "(no previous session state)" in bundle
        # No deadlines, coaching, pending sections
        assert "# Deadlines" not in bundle
        assert "# Coaching" not in bundle
        assert "# Pending" not in bundle

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_no_coaching(self, mock_patterns: object) -> None:
        """Bundle with empty coaching omits coaching section."""
        assert callable(mock_patterns)
        mock_patterns.return_value = []

        profile = DeveloperProfile(name="Test")
        state = _make_state()
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Coaching" not in bundle

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_no_pending(self, mock_patterns: object) -> None:
        """Bundle with empty pending omits pending section."""
        assert callable(mock_patterns)
        mock_patterns.return_value = []

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.7", phase="design", branch="main"
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 2, 8),
                developer="Test",
                summary="test",
            ),
        )
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Pending" not in bundle

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_deadline_days_remaining(self, mock_patterns: object) -> None:
        """Deadlines show days remaining."""
        assert callable(mock_patterns)
        mock_patterns.return_value = []

        profile = DeveloperProfile(
            name="Test",
            deadlines=[Deadline(name="Soon", date=date.today())],
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "(today)" in bundle

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_coaching_shows_last_3_corrections(self, mock_patterns: object) -> None:
        """Coaching section shows only last 3 corrections for brevity."""
        assert callable(mock_patterns)
        mock_patterns.return_value = []

        corrections = [
            Correction(session=f"SES-{i:03d}", what=f"what-{i}", lesson=f"lesson-{i}")
            for i in range(5)
        ]
        profile = DeveloperProfile(
            name="Test",
            coaching=CoachingContext(
                strengths=["test"],
                corrections=corrections,
            ),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        # Only last 3 should appear
        assert "SES-002" in bundle
        assert "SES-003" in bundle
        assert "SES-004" in bundle
        assert "SES-000" not in bundle
        assert "SES-001" not in bundle


class TestGetFoundationalPatterns:
    """Tests for get_foundational_patterns."""

    def test_returns_empty_if_no_graph(self, tmp_path: Path) -> None:
        """Returns empty list when graph file doesn't exist."""
        result = get_foundational_patterns(tmp_path)
        assert result == []

    def test_returns_foundational_patterns_from_graph(self, tmp_path: Path) -> None:
        """Returns patterns with foundational=true from graph."""
        from raise_cli.context.graph import UnifiedGraph

        graph = UnifiedGraph()
        graph.add_concept(
            ConceptNode(
                id="PAT-187",
                type="pattern",
                content="Code as Gemba",
                created="2026-02-08",
                metadata={"foundational": True},
            )
        )
        graph.add_concept(
            ConceptNode(
                id="PAT-001",
                type="pattern",
                content="Not foundational",
                created="2026-02-08",
                metadata={},
            )
        )
        graph.add_concept(
            ConceptNode(
                id="guardrail-001",
                type="guardrail",
                content="Not a pattern",
                created="2026-02-08",
                metadata={"foundational": True},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        result = get_foundational_patterns(tmp_path)
        assert len(result) == 1
        assert result[0].id == "PAT-187"
