"""Tests for context bundle assembly."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

from rai_cli.context.models import ConceptNode
from rai_cli.onboarding.profile import (
    CoachingContext,
    CommunicationPreferences,
    CommunicationStyle,
    Correction,
    Deadline,
    DeveloperProfile,
    ExperienceLevel,
    RelationshipState,
)
from rai_cli.schemas.session_state import (
    CurrentWork,
    EpicProgress,
    LastSession,
    PendingItems,
    SessionState,
)
from rai_cli.session.bundle import (
    _format_governance_primes,
    _format_identity_primes,
    _format_progress,
    _format_recent_sessions,
    assemble_context_bundle,
    get_always_on_primes,
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

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_full_bundle_contains_all_sections(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Full bundle contains all sections including new ones."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba — observe before designing"),
        ]
        mock_always_on.return_value = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
            _make_always_on_node(
                "RAI-VAL-1", "principle", "Honesty over agreement"
            ),
        ]

        profile = _make_profile()
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15", stories_done=5, stories_total=8, sp_done=16, sp_total=25,
        )
        state.completed_epics = ["E1", "E2"]
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
        # New sections
        assert "# Governance Primes" in bundle
        assert "guardrail-must-code-001" in bundle
        assert "# Identity Primes" in bundle
        assert "RAI-VAL-1" in bundle
        assert "5/8" in bundle
        assert "16/25" in bundle
        assert "E1, E2" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_without_state(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle without session state is graceful."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="New")
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "Developer: New (shu)" in bundle
        assert "(no previous session state)" in bundle
        # No deadlines, coaching, pending sections
        assert "# Deadlines" not in bundle
        assert "# Coaching" not in bundle
        assert "# Pending" not in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_no_coaching(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle with empty coaching omits coaching section."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        state = _make_state()
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Coaching" not in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_no_pending(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle with empty pending omits pending section."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

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

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_deadline_days_remaining(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Deadlines show days remaining."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            deadlines=[Deadline(name="Soon", date=date.today())],
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "(today)" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_coaching_shows_last_3_corrections(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Coaching section shows only last 3 corrections for brevity."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

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

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_coaching_shows_trust_and_relationship(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Coaching section shows trust level, autonomy, and relationship."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            coaching=CoachingContext(
                trust_level="developing",
                strengths=["design"],
                autonomy="high within scope",
                relationship=RelationshipState(
                    quality="productive", trajectory="growing"
                ),
            ),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "Trust: developing" in bundle
        assert "Autonomy: high within scope" in bundle
        assert "Relationship: productive (growing)" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_coaching_omits_default_trust_and_relationship(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Coaching section omits trust and relationship at default values."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            coaching=CoachingContext(strengths=["design"]),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        assert "# Coaching" in bundle
        assert "Strengths: design" in bundle
        assert "Trust:" not in bundle
        assert "Autonomy:" not in bundle
        assert "Relationship:" not in bundle


def _make_always_on_node(
    node_id: str, node_type: str, content: str
) -> ConceptNode:
    """Create a mock always_on node."""
    return ConceptNode(
        id=node_id,
        type=node_type,
        content=content,
        source_file="test",
        created="2026-02-08",
        metadata={"always_on": True},
    )


class TestFormatDeveloperSection:
    """Tests for _format_developer_section communication preferences."""

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_includes_non_default_language(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Developer section includes language when not default 'en'."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            communication=CommunicationPreferences(language="mixed"),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))
        assert "Developer: Emilio (ri)" in bundle
        assert "language: mixed" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_omits_default_language(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Developer section omits language when default 'en'."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        bundle = assemble_context_bundle(profile, None, Path("/project"))
        assert "language:" not in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_includes_non_default_style(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Developer section includes style when not default 'balanced'."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            communication=CommunicationPreferences(
                style=CommunicationStyle.DIRECT,
            ),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))
        assert "style: direct" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_includes_skip_praise(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Developer section includes skip_praise when true."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            communication=CommunicationPreferences(skip_praise=True),
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))
        assert "skip_praise" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_omits_all_defaults(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Developer section omits communication when all defaults."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        bundle = assemble_context_bundle(profile, None, Path("/project"))
        assert "Communication:" not in bundle
        assert "language:" not in bundle
        assert "style:" not in bundle


class TestGetAlwaysOnPrimes:
    """Tests for get_always_on_primes."""

    def test_returns_empty_if_no_graph(self, tmp_path: Path) -> None:
        """Returns empty list when graph file doesn't exist."""
        result = get_always_on_primes(tmp_path)
        assert result == []

    def test_returns_always_on_nodes(self, tmp_path: Path) -> None:
        """Returns all nodes with always_on=true metadata."""
        from rai_cli.context.graph import UnifiedGraph

        graph = UnifiedGraph()
        graph.add_concept(
            _make_always_on_node("guardrail-must-code-001", "guardrail", "Type hints")
        )
        graph.add_concept(
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty over agreement")
        )
        graph.add_concept(
            ConceptNode(
                id="PAT-001",
                type="pattern",
                content="Not always_on",
                created="2026-02-08",
                metadata={},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        result = get_always_on_primes(tmp_path)
        assert len(result) == 2
        ids = {n.id for n in result}
        assert "guardrail-must-code-001" in ids
        assert "RAI-VAL-1" in ids

    def test_excludes_non_always_on(self, tmp_path: Path) -> None:
        """Nodes without always_on=true are excluded."""
        from rai_cli.context.graph import UnifiedGraph

        graph = UnifiedGraph()
        graph.add_concept(
            ConceptNode(
                id="guardrail-should-001",
                type="guardrail",
                content="Optional rule",
                created="2026-02-08",
                metadata={"always_on": False},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        result = get_always_on_primes(tmp_path)
        assert result == []


class TestFormatGovernancePrimes:
    """Tests for _format_governance_primes."""

    def test_formats_guardrails_and_principles(self) -> None:
        """Governance primes include guardrails and non-identity principles."""
        nodes = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
            _make_always_on_node(
                "principle-lean", "principle", "Lean software development"
            ),
        ]
        result = _format_governance_primes(nodes)
        assert "# Governance Primes" in result
        assert "guardrail-must-code-001" in result
        assert "principle-lean" in result

    def test_excludes_identity_nodes(self) -> None:
        """Identity nodes (RAI-VAL-*, RAI-BND-*) are excluded from governance."""
        nodes = [
            _make_always_on_node(
                "RAI-VAL-1", "principle", "Honesty over agreement"
            ),
            _make_always_on_node(
                "RAI-BND-1", "principle", "Stop on incoherence"
            ),
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
        ]
        result = _format_governance_primes(nodes)
        assert "RAI-VAL-1" not in result
        assert "RAI-BND-1" not in result
        assert "guardrail-must-code-001" in result

    def test_returns_empty_string_when_no_governance(self) -> None:
        """Returns empty string when no governance nodes."""
        nodes = [
            _make_always_on_node(
                "RAI-VAL-1", "principle", "Honesty"
            ),
        ]
        result = _format_governance_primes(nodes)
        assert result == ""

    def test_truncates_long_content(self) -> None:
        """Long content is truncated to 80 chars."""
        nodes = [
            _make_always_on_node(
                "guardrail-must-code-001",
                "guardrail",
                "A" * 100,
            ),
        ]
        result = _format_governance_primes(nodes)
        assert "..." in result


class TestFormatIdentityPrimes:
    """Tests for _format_identity_primes."""

    def test_formats_identity_nodes(self) -> None:
        """Identity primes include RAI-VAL-* and RAI-BND-* nodes."""
        nodes = [
            _make_always_on_node(
                "RAI-VAL-1", "principle", "Honesty over agreement"
            ),
            _make_always_on_node(
                "RAI-BND-1", "principle", "Stop on incoherence"
            ),
        ]
        result = _format_identity_primes(nodes)
        assert "# Identity Primes" in result
        assert "RAI-VAL-1" in result
        assert "RAI-BND-1" in result

    def test_excludes_non_identity(self) -> None:
        """Non-identity nodes are excluded."""
        nodes = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "Type hints"
            ),
            _make_always_on_node(
                "RAI-VAL-1", "principle", "Honesty"
            ),
        ]
        result = _format_identity_primes(nodes)
        assert "guardrail-must-code-001" not in result
        assert "RAI-VAL-1" in result

    def test_returns_empty_string_when_no_identity(self) -> None:
        """Returns empty string when no identity nodes."""
        nodes = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "Type hints"
            ),
        ]
        result = _format_identity_primes(nodes)
        assert result == ""


class TestFormatProgress:
    """Tests for _format_progress."""

    def test_formats_progress(self) -> None:
        """Progress shows story and SP counts."""
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15",
            stories_done=5,
            stories_total=8,
            sp_done=16,
            sp_total=25,
        )
        state.completed_epics = ["E1", "E2", "E3"]
        result = _format_progress(state)
        assert "E15" in result
        assert "5/8" in result
        assert "16/25" in result
        assert "E1, E2, E3" in result

    def test_progress_without_completed_epics(self) -> None:
        """Progress works without completed epics."""
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15",
            stories_done=2,
            stories_total=8,
            sp_done=6,
            sp_total=25,
        )
        result = _format_progress(state)
        assert "2/8" in result
        assert "Completed:" not in result

    def test_returns_empty_when_no_progress(self) -> None:
        """Returns empty string when no progress set."""
        state = _make_state()
        result = _format_progress(state)
        assert result == ""

    def test_returns_empty_when_state_is_none(self) -> None:
        """Returns empty string when state is None."""
        result = _format_progress(None)
        assert result == ""


class TestFormatRecentSessions:
    """Tests for _format_recent_sessions."""

    def test_reads_last_3_sessions(self, tmp_path: Path) -> None:
        """Reads last 3 sessions from index.jsonl."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        index_file = index_dir / "index.jsonl"

        sessions = [
            {"id": f"SES-{i:03d}", "date": "2026-02-08", "type": "feature", "topic": f"Topic {i}"}
            for i in range(5)
        ]
        index_file.write_text("\n".join(json.dumps(s) for s in sessions))

        result = _format_recent_sessions(tmp_path, limit=3)
        assert "SES-004" in result
        assert "SES-003" in result
        assert "SES-002" in result
        assert "SES-001" not in result
        assert "SES-000" not in result

    def test_returns_empty_when_no_index(self, tmp_path: Path) -> None:
        """Returns empty string when index file doesn't exist."""
        result = _format_recent_sessions(tmp_path)
        assert result == ""

    def test_returns_empty_when_empty_index(self, tmp_path: Path) -> None:
        """Returns empty string when index is empty."""
        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        (index_dir / "index.jsonl").write_text("")
        result = _format_recent_sessions(tmp_path)
        assert result == ""

    def test_fewer_sessions_than_limit(self, tmp_path: Path) -> None:
        """Works when fewer sessions than limit."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        sessions = [
            {"id": "SES-001", "date": "2026-02-08", "type": "feature", "topic": "Only session"},
        ]
        (index_dir / "index.jsonl").write_text(json.dumps(sessions[0]))

        result = _format_recent_sessions(tmp_path, limit=3)
        assert "SES-001" in result

    def test_truncates_long_topics(self, tmp_path: Path) -> None:
        """Long topics are truncated."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        session = {"id": "SES-001", "date": "2026-02-08", "type": "feature", "topic": "A" * 120}
        (index_dir / "index.jsonl").write_text(json.dumps(session))

        result = _format_recent_sessions(tmp_path, limit=3)
        assert "..." in result


class TestBundleReleaseContext:
    """Tests for release context in session bundle."""

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_includes_release_when_graph_has_release_edge(
        self, mock_patterns: object, mock_always_on: object, tmp_path: Path
    ) -> None:
        """Bundle includes release line when graph has epic→release edge."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        # Build a graph with epic→release edge
        from rai_cli.context.graph import UnifiedGraph
        from rai_cli.context.models import ConceptEdge

        graph = UnifiedGraph()
        graph.add_concept(
            ConceptNode(
                id="rel-v3.0",
                type="release",
                content="V3.0 Commercial Launch",
                source_file="governance/roadmap.md",
                created="2026-02-11",
                metadata={
                    "release_id": "REL-V3.0",
                    "name": "V3.0 Commercial Launch",
                    "target": "2026-03-14",
                },
            )
        )
        graph.add_concept(
            ConceptNode(
                id="epic-e19",
                type="epic",
                content="V3 Product Design",
                source_file="governance/backlog.md",
                created="2026-02-11",
            )
        )
        graph.add_relationship(
            ConceptEdge(source="epic-e19", target="rel-v3.0", type="part_of")
        )
        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E19", story="S19.3", phase="implement",
                branch="epic/e19/v3",
            ),
            last_session=LastSession(
                id="SES-100", date=date(2026, 2, 13),
                developer="Test", summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release: REL-V3.0" in bundle
        assert "V3.0 Commercial Launch" in bundle
        assert "2026-03-14" in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_omits_release_when_no_graph(
        self, mock_patterns: object, mock_always_on: object, tmp_path: Path
    ) -> None:
        """Bundle omits release line when no graph exists."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E19", story="S19.3", phase="implement",
                branch="epic/e19/v3",
            ),
            last_session=LastSession(
                id="SES-100", date=date(2026, 2, 13),
                developer="Test", summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release:" not in bundle

    @patch("rai_cli.session.bundle.get_always_on_primes")
    @patch("rai_cli.session.bundle.get_foundational_patterns")
    def test_bundle_omits_release_when_epic_has_no_release(
        self, mock_patterns: object, mock_always_on: object, tmp_path: Path
    ) -> None:
        """Bundle omits release line when epic has no release in graph."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        # Graph exists but epic has no release edge
        from rai_cli.context.graph import UnifiedGraph

        graph = UnifiedGraph()
        graph.add_concept(
            ConceptNode(
                id="epic-e18",
                type="epic",
                content="V2 Open Core",
                source_file="governance/backlog.md",
                created="2026-02-11",
            )
        )
        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E18", story="S18.1", phase="implement",
                branch="epic/e18/v2",
            ),
            last_session=LastSession(
                id="SES-100", date=date(2026, 2, 13),
                developer="Test", summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release:" not in bundle


class TestGetFoundationalPatterns:
    """Tests for get_foundational_patterns."""

    def test_returns_empty_if_no_graph(self, tmp_path: Path) -> None:
        """Returns empty list when graph file doesn't exist."""
        result = get_foundational_patterns(tmp_path)
        assert result == []

    def test_returns_foundational_patterns_from_graph(self, tmp_path: Path) -> None:
        """Returns patterns with foundational=true from graph."""
        from rai_cli.context.graph import UnifiedGraph

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
