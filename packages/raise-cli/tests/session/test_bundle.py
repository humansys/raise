"""Tests for context bundle assembly."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from raise_cli.onboarding.profile import (
    CoachingContext,
    CommunicationPreferences,
    CommunicationStyle,
    Correction,
    Deadline,
    DeveloperProfile,
    ExperienceLevel,
    RelationshipState,
)
from raise_cli.schemas.session_state import (
    CurrentWork,
    EpicProgress,
    LastSession,
    PendingItems,
    SessionState,
)
from raise_cli.session.bundle import (
    SECTION_REGISTRY,
    assemble_context_bundle,
    assemble_orientation,
    assemble_sections,
    count_section_items,
)
from raise_cli.session.bundle_data import (
    LiveBacklogStatus,
    SectionManifest,
    fetch_live_status,
    get_always_on_primes,
    get_foundational_patterns,
)
from raise_cli.session.bundle_formatters import (
    format_governance_primes,
    format_manifest,
    format_narrative,
    format_next_session_prompt,
    format_progress,
    format_recent_sessions,
    format_work_section,
)
from raise_core.graph.models import GraphNode


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


def _make_pattern(pat_id: str, content: str) -> GraphNode:
    """Create a mock foundational pattern node."""
    return GraphNode(
        id=pat_id,
        type="pattern",
        content=content,
        source_file=".raise/rai/memory/patterns.jsonl",
        created="2026-02-08",
        metadata={"foundational": True},
    )


class TestAssembleContextBundle:
    """Tests for assemble_context_bundle."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_lean_bundle_has_orientation_and_manifest(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Lean bundle contains orientation + manifest, NOT priming sections."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba — observe before designing"),
        ]
        mock_always_on.return_value = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty over agreement"),
        ]

        profile = _make_profile()
        state = _make_state()
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        # Orientation sections present
        assert "# Session Context" in bundle
        assert "Developer: Emilio (ri)" in bundle
        assert "Story: S15.7 [implement]" in bundle
        assert "Epic: E15" in bundle
        assert "SES-097" in bundle
        assert "# Pending" in bundle
        assert "Pattern curation" in bundle

        # Manifest present
        assert "# Available Context" in bundle
        assert "governance:" in bundle
        assert "behavioral:" in bundle

        # Priming sections NOT present (moved to rai session context)
        assert "# Governance Primes" not in bundle
        assert "guardrail-must-code-001" not in bundle
        assert "# Behavioral Primes" not in bundle
        assert "PAT-187" not in bundle
        assert "# Coaching" not in bundle
        assert "# Deadlines" not in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_deadline_in_manifest_not_inline(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Deadlines appear in manifest count, not inline."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(
            name="Test",
            deadlines=[Deadline(name="Soon", date=date.today())],
        )
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        # Deadline count in manifest
        assert "deadlines: 1 items" in bundle
        # Deadline details NOT inline (moved to rai session context)
        assert "Soon" not in bundle
        assert "(today)" not in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_coaching_corrections_suppressed(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Coaching corrections are suppressed from context bundle."""
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

        # Corrections should not appear — suppressed until retro-skill integration
        for i in range(5):
            assert f"SES-{i:03d}" not in bundle
        assert "corrections" not in bundle.lower()

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_coaching_in_manifest_not_inline(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Coaching appears in manifest count, not inline."""
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

        # Coaching count in manifest
        assert "coaching: 1 items" in bundle
        # Coaching details NOT inline (moved to rai session context)
        assert "Trust: developing" not in bundle
        assert "# Coaching" not in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_session_id_in_context(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Session ID appears in context bundle when provided."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = _make_profile()
        state = _make_state()
        bundle = assemble_context_bundle(
            profile, state, Path("/project"), session_id="SES-177"
        )

        # Session ID should appear in a visible location
        assert "Session: SES-177" in bundle


def _make_always_on_node(node_id: str, node_type: str, content: str) -> GraphNode:
    """Create a mock always_on node."""
    return GraphNode(
        id=node_id,
        type=node_type,
        content=content,
        source_file="test",
        created="2026-02-08",
        metadata={"always_on": True},
    )


class TestFormatDeveloperSection:
    """Tests for _format_developer_section communication preferences."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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
        from raise_core.graph.backends.filesystem import FilesystemGraphBackend
        from raise_core.graph.engine import Graph

        graph = Graph()
        graph.add_concept(
            _make_always_on_node("guardrail-must-code-001", "guardrail", "Type hints")
        )
        graph.add_concept(
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty over agreement")
        )
        graph.add_concept(
            GraphNode(
                id="PAT-001",
                type="pattern",
                content="Not always_on",
                created="2026-02-08",
                metadata={},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        FilesystemGraphBackend(graph_path).persist(graph)

        result = get_always_on_primes(tmp_path)
        assert len(result) == 2
        ids = {n.id for n in result}
        assert "guardrail-must-code-001" in ids
        assert "RAI-VAL-1" in ids

    def test_excludes_non_always_on(self, tmp_path: Path) -> None:
        """Nodes without always_on=true are excluded."""
        from raise_core.graph.backends.filesystem import FilesystemGraphBackend
        from raise_core.graph.engine import Graph

        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="guardrail-should-001",
                type="guardrail",
                content="Optional rule",
                created="2026-02-08",
                metadata={"always_on": False},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        FilesystemGraphBackend(graph_path).persist(graph)

        result = get_always_on_primes(tmp_path)
        assert result == []


class TestFormatGovernancePrimes:
    """Tests for format_governance_primes."""

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
        result = format_governance_primes(nodes)
        assert "# Governance Primes" in result
        assert "guardrail-must-code-001" in result
        assert "principle-lean" in result

    def test_excludes_identity_nodes(self) -> None:
        """Identity nodes (RAI-VAL-*, RAI-BND-*) are excluded from governance."""
        nodes = [
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty over agreement"),
            _make_always_on_node("RAI-BND-1", "principle", "Stop on incoherence"),
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
        ]
        result = format_governance_primes(nodes)
        assert "RAI-VAL-1" not in result
        assert "RAI-BND-1" not in result
        assert "guardrail-must-code-001" in result

    def test_returns_empty_string_when_no_governance(self) -> None:
        """Returns empty string when no governance nodes."""
        nodes = [
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty"),
        ]
        result = format_governance_primes(nodes)
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
        result = format_governance_primes(nodes)
        assert "..." in result


class TestIdentityPrimesRemoved:
    """Verify identity primes are no longer emitted (ADR-012)."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_identity_nodes_not_in_bundle(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Identity nodes (RAI-VAL-*, RAI-BND-*) are not emitted in lean bundle."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = [
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty over agreement"),
            _make_always_on_node("RAI-BND-1", "principle", "Stop on incoherence"),
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
        ]

        profile = DeveloperProfile(name="Test")
        bundle = assemble_context_bundle(profile, None, Path("/project"))

        # Lean bundle has no governance inline — only in manifest
        assert "# Governance Primes" not in bundle
        assert "guardrail-must-code-001" not in bundle
        # Identity primes also absent
        assert "# Identity Primes" not in bundle
        assert "RAI-VAL-1" not in bundle
        assert "RAI-BND-1" not in bundle
        # Governance count in manifest (2 non-identity out of 3)
        assert "governance: 1 items" in bundle


class TestFormatProgress:
    """Tests for format_progress."""

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
        result = format_progress(state)
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
        result = format_progress(state)
        assert "2/8" in result
        assert "Completed:" not in result

    def test_returns_empty_when_no_progress(self) -> None:
        """Returns empty string when no progress set."""
        state = _make_state()
        result = format_progress(state)
        assert result == ""

    def test_returns_empty_when_state_is_none(self) -> None:
        """Returns empty string when state is None."""
        result = format_progress(None)
        assert result == ""


class TestFormatRecentSessions:
    """Tests for format_recent_sessions."""

    def test_reads_last_3_sessions(self, tmp_path: Path) -> None:
        """Reads last 3 sessions from index.jsonl."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        index_file = index_dir / "index.jsonl"

        sessions = [
            {
                "id": f"SES-{i:03d}",
                "date": "2026-02-08",
                "type": "feature",
                "topic": f"Topic {i}",
            }
            for i in range(5)
        ]
        index_file.write_text("\n".join(json.dumps(s) for s in sessions))

        result = format_recent_sessions(tmp_path, limit=3)
        assert "SES-004" in result
        assert "SES-003" in result
        assert "SES-002" in result
        assert "SES-001" not in result
        assert "SES-000" not in result

    def test_returns_empty_when_no_index(self, tmp_path: Path) -> None:
        """Returns empty string when index file doesn't exist."""
        result = format_recent_sessions(tmp_path)
        assert result == ""

    def test_returns_empty_when_empty_index(self, tmp_path: Path) -> None:
        """Returns empty string when index is empty."""
        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        (index_dir / "index.jsonl").write_text("")
        result = format_recent_sessions(tmp_path)
        assert result == ""

    def test_fewer_sessions_than_limit(self, tmp_path: Path) -> None:
        """Works when fewer sessions than limit."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        sessions = [
            {
                "id": "SES-001",
                "date": "2026-02-08",
                "type": "feature",
                "topic": "Only session",
            },
        ]
        (index_dir / "index.jsonl").write_text(json.dumps(sessions[0]))

        result = format_recent_sessions(tmp_path, limit=3)
        assert "SES-001" in result

    def test_truncates_long_topics(self, tmp_path: Path) -> None:
        """Long topics are truncated."""
        import json

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        session = {
            "id": "SES-001",
            "date": "2026-02-08",
            "type": "feature",
            "topic": "A" * 120,
        }
        (index_dir / "index.jsonl").write_text(json.dumps(session))

        result = format_recent_sessions(tmp_path, limit=3)
        assert "..." in result


class TestFormatRecentSessionsSharedIndex:
    """Tests for format_recent_sessions reading from shared index."""

    def test_reads_shared_index_with_names(self, tmp_path: Path) -> None:
        """Should read from shared index and show session names."""
        from datetime import datetime

        from raise_cli.session.index import SessionIndexEntry, write_session_entry

        for i, name in enumerate(["gemba research", "epic design", "implementation"]):
            entry = SessionIndexEntry(
                id=f"S-E-26032{i}-1430",
                name=name,
                started=datetime(2026, 3, 20 + i, 14, 30),
                closed=datetime(2026, 3, 20 + i, 16, 0),
                type="feature",
            )
            write_session_entry("E", entry, project_root=tmp_path)

        result = format_recent_sessions(tmp_path, limit=3, developer_prefix="E")
        assert "implementation" in result
        assert "epic design" in result
        assert "gemba research" in result
        assert "1h30m" in result  # Duration

    def test_shared_index_empty_falls_back(self, tmp_path: Path) -> None:
        """Empty shared index with no personal index returns empty."""
        result = format_recent_sessions(tmp_path, limit=3, developer_prefix="E")
        assert result == ""

    def test_no_prefix_falls_back_to_personal(self, tmp_path: Path) -> None:
        """Without prefix, should fall back to personal index."""
        import json as json_mod

        index_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        index_dir.mkdir(parents=True)
        session = {
            "id": "SES-001",
            "date": "2026-02-08",
            "type": "feature",
            "topic": "legacy session",
        }
        (index_dir / "index.jsonl").write_text(json_mod.dumps(session))

        result = format_recent_sessions(tmp_path, limit=3, developer_prefix=None)
        assert "SES-001" in result
        assert "legacy session" in result

    def test_shared_index_shows_duration(self, tmp_path: Path) -> None:
        """Should format duration correctly for sessions with closed timestamp."""
        from datetime import datetime

        from raise_cli.session.index import SessionIndexEntry, write_session_entry

        entry = SessionIndexEntry(
            id="S-E-260322-0900",
            name="long session",
            started=datetime(2026, 3, 22, 9, 0),
            closed=datetime(2026, 3, 22, 9, 45),
            type="research",
        )
        write_session_entry("E", entry, project_root=tmp_path)

        result = format_recent_sessions(tmp_path, limit=3, developer_prefix="E")
        assert "45m" in result
        assert "research" in result


class TestActiveSessionNameInBundle:
    """Test that active session name appears in orientation output."""

    def test_orientation_shows_session_name(self, tmp_path: Path) -> None:
        """assemble_orientation should show session name from active pointer."""
        from raise_cli.session.index import ActiveSessionPointer, write_active_session

        pointer = ActiveSessionPointer(
            id="S-E-260322-1430",
            name="gemba research",
            started=date.today(),
        )
        write_active_session(pointer, project_root=tmp_path)

        profile = DeveloperProfile(name="Emilio")
        result = assemble_orientation(
            profile, None, tmp_path, session_id="S-E-260322-1430"
        )
        assert "Session: S-E-260322-1430" in result
        assert "gemba research" in result


class TestBundleReleaseContext:
    """Tests for release context in session bundle."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_includes_release_when_graph_has_release_edge(
        self, mock_patterns: object, mock_always_on: object, tmp_path: Path
    ) -> None:
        """Bundle includes release line when graph has epic→release edge."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        # Build a graph with epic→release edge
        from raise_core.graph.backends.filesystem import FilesystemGraphBackend
        from raise_core.graph.engine import Graph
        from raise_core.graph.models import GraphEdge

        graph = Graph()
        graph.add_concept(
            GraphNode(
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
            GraphNode(
                id="epic-e19",
                type="epic",
                content="V3 Product Design",
                source_file="governance/backlog.md",
                created="2026-02-11",
            )
        )
        graph.add_relationship(
            GraphEdge(source="epic-e19", target="rel-v3.0", type="part_of")
        )
        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        FilesystemGraphBackend(graph_path).persist(graph)

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E19",
                story="S19.3",
                phase="implement",
                branch="epic/e19/v3",
            ),
            last_session=LastSession(
                id="SES-100",
                date=date(2026, 2, 13),
                developer="Test",
                summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release: REL-V3.0" in bundle
        assert "V3.0 Commercial Launch" in bundle
        assert "2026-03-14" in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
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
                epic="E19",
                story="S19.3",
                phase="implement",
                branch="epic/e19/v3",
            ),
            last_session=LastSession(
                id="SES-100",
                date=date(2026, 2, 13),
                developer="Test",
                summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release:" not in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_omits_release_when_epic_has_no_release(
        self, mock_patterns: object, mock_always_on: object, tmp_path: Path
    ) -> None:
        """Bundle omits release line when epic has no release in graph."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        # Graph exists but epic has no release edge
        from raise_core.graph.backends.filesystem import FilesystemGraphBackend
        from raise_core.graph.engine import Graph

        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="epic-e18",
                type="epic",
                content="V2 Open Core",
                source_file="governance/backlog.md",
                created="2026-02-11",
            )
        )
        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        FilesystemGraphBackend(graph_path).persist(graph)

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E18",
                story="S18.1",
                phase="implement",
                branch="epic/e18/v2",
            ),
            last_session=LastSession(
                id="SES-100",
                date=date(2026, 2, 13),
                developer="Test",
                summary="test",
            ),
        )

        bundle = assemble_context_bundle(profile, state, tmp_path)
        assert "Release:" not in bundle


class TestFormatNarrative:
    """Tests for narrative section in context bundle."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_includes_narrative_when_present(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle includes narrative section when state has narrative."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E21", story="S21.1", phase="implement", branch="epic/e21"
            ),
            last_session=LastSession(
                id="SES-159",
                date=date(2026, 2, 14),
                developer="Test",
                summary="test session",
            ),
            narrative="## Decisions\n- Architecture = sync model\n\n## Artifacts\n- scope.md created",
        )
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Session Narrative" in bundle
        assert "Architecture = sync model" in bundle
        assert "scope.md created" in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_omits_narrative_when_empty(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle omits narrative section when narrative is empty."""
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

        assert "# Session Narrative" not in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_narrative_not_truncated(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Narrative content is NOT truncated regardless of length."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        long_narrative = (
            "## Decisions\n" + "- Decision line that is quite long and detailed " * 20
        )

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E21", story="S21.1", phase="implement", branch="epic/e21"
            ),
            last_session=LastSession(
                id="SES-159",
                date=date(2026, 2, 14),
                developer="Test",
                summary="test",
            ),
            narrative=long_narrative,
        )
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        # Full content should be present, no "..." truncation
        assert long_narrative in bundle
        assert "..." not in bundle.split("# Session Narrative")[1].split("#")[0]

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_narrative_appears_after_last_session(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Narrative section appears after Last: line and before manifest."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = [
            _make_always_on_node(
                "guardrail-must-code-001", "guardrail", "[MUST] Type hints"
            ),
        ]

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E21", story="S21.1", phase="implement", branch="epic/e21"
            ),
            last_session=LastSession(
                id="SES-159",
                date=date(2026, 2, 14),
                developer="Test",
                summary="test session",
            ),
            narrative="## Decisions\n- Chose sync model",
        )
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        last_pos = bundle.find("Last:")
        narrative_pos = bundle.find("# Session Narrative")
        manifest_pos = bundle.find("# Available Context")

        assert last_pos < narrative_pos < manifest_pos


class TestFormatNextSessionPrompt:
    """Tests for next_session_prompt section in context bundle."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_includes_next_session_prompt_when_present(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle includes next_session_prompt section when state has it."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(epic="RAISE-144", story="", phase="", branch="v2"),
            last_session=LastSession(
                id="SES-200",
                date=date(2026, 2, 17),
                developer="Test",
                summary="test session",
            ),
            next_session_prompt="Verify encoding fix covers discovery tests. Check backlog abstraction interest.",
        )
        bundle = assemble_context_bundle(profile, state, Path("/project"))

        assert "# Next Session Prompt" in bundle
        assert "encoding fix" in bundle

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_bundle_omits_next_session_prompt_when_empty(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Bundle omits next_session_prompt section when empty."""
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

        assert "# Next Session Prompt" not in bundle


class TestGetFoundationalPatterns:
    """Tests for get_foundational_patterns."""

    def test_returns_empty_if_no_graph(self, tmp_path: Path) -> None:
        """Returns empty list when graph file doesn't exist."""
        result = get_foundational_patterns(tmp_path)
        assert result == []

    def test_returns_foundational_patterns_from_graph(self, tmp_path: Path) -> None:
        """Returns patterns with foundational=true from graph."""
        from raise_core.graph.backends.filesystem import FilesystemGraphBackend
        from raise_core.graph.engine import Graph

        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="PAT-187",
                type="pattern",
                content="Code as Gemba",
                created="2026-02-08",
                metadata={"foundational": True},
            )
        )
        graph.add_concept(
            GraphNode(
                id="PAT-001",
                type="pattern",
                content="Not foundational",
                created="2026-02-08",
                metadata={},
            )
        )
        graph.add_concept(
            GraphNode(
                id="guardrail-001",
                type="guardrail",
                content="Not a pattern",
                created="2026-02-08",
                metadata={"foundational": True},
            )
        )

        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        FilesystemGraphBackend(graph_path).persist(graph)

        result = get_foundational_patterns(tmp_path)
        assert len(result) == 1
        assert result[0].id == "PAT-187"


class TestSectionRegistry:
    """Tests for SECTION_REGISTRY and manifest model."""

    def test_registry_has_all_five_sections(self) -> None:
        """Registry contains all defined queryable sections."""
        expected = {"governance", "behavioral", "coaching", "deadlines", "progress"}
        assert set(SECTION_REGISTRY.keys()) == expected

    def test_registry_values_are_callable(self) -> None:
        """All registry values are callable format functions."""
        for name, fn in SECTION_REGISTRY.items():
            assert callable(fn), f"Section '{name}' is not callable"


class TestSectionManifest:
    """Tests for SectionManifest model."""

    def test_manifest_creation(self) -> None:
        """Manifest can be created with section name, count, and token estimate."""
        m = SectionManifest(name="governance", count=14, token_estimate=350)
        assert m.name == "governance"
        assert m.count == 14
        assert m.token_estimate == 350

    def test_manifest_zero_count(self) -> None:
        """Manifest with zero count is valid."""
        m = SectionManifest(name="deadlines", count=0, token_estimate=0)
        assert m.count == 0


class TestCountSectionItems:
    """Tests for count_section_items."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    def test_count_governance(self, mock_always_on: object) -> None:
        """Counts governance items (always_on minus identity)."""
        assert callable(mock_always_on)
        mock_always_on.return_value = [
            _make_always_on_node("guardrail-must-001", "guardrail", "Type hints"),
            _make_always_on_node("guardrail-must-002", "guardrail", "Ruff"),
            _make_always_on_node("RAI-VAL-1", "principle", "Honesty"),
        ]
        result = count_section_items(
            "governance", Path("/project"), _make_profile(), _make_state()
        )
        assert result == 2  # 3 always_on minus 1 identity

    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_count_behavioral(self, mock_patterns: object) -> None:
        """Counts behavioral items (foundational patterns)."""
        assert callable(mock_patterns)
        mock_patterns.return_value = [
            _make_pattern("PAT-1", "Pattern one"),
            _make_pattern("PAT-2", "Pattern two"),
        ]
        result = count_section_items(
            "behavioral", Path("/project"), _make_profile(), _make_state()
        )
        assert result == 2

    def test_count_coaching_with_content(self) -> None:
        """Counts coaching as 1 when content exists."""
        profile = _make_profile()
        result = count_section_items(
            "coaching", Path("/project"), profile, _make_state()
        )
        assert result == 1

    def test_count_coaching_empty(self) -> None:
        """Counts coaching as 0 when no content."""
        profile = DeveloperProfile(name="New")
        result = count_section_items(
            "coaching", Path("/project"), profile, _make_state()
        )
        assert result == 0

    def test_count_deadlines(self) -> None:
        """Counts deadlines from profile."""
        profile = _make_profile()  # has 2 deadlines
        result = count_section_items(
            "deadlines", Path("/project"), profile, _make_state()
        )
        assert result == 2

    def test_count_deadlines_empty(self) -> None:
        """Counts deadlines as 0 when none."""
        profile = DeveloperProfile(name="New")
        result = count_section_items(
            "deadlines", Path("/project"), profile, _make_state()
        )
        assert result == 0

    def test_count_progress_with_data(self) -> None:
        """Counts progress as 1 when data exists."""
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15", stories_done=2, stories_total=5, sp_done=6, sp_total=15
        )
        result = count_section_items(
            "progress", Path("/project"), _make_profile(), state
        )
        assert result == 1

    def test_count_progress_without_data(self) -> None:
        """Counts progress as 0 when no progress data."""
        result = count_section_items(
            "progress", Path("/project"), _make_profile(), _make_state()
        )
        assert result == 0

    def test_count_unknown_section_raises(self) -> None:
        """Unknown section name raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Unknown section"):
            count_section_items(
                "unknown", Path("/project"), _make_profile(), _make_state()
            )


class TestAssembleOrientation:
    """Tests for assemble_orientation (always-on sections only)."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_orientation_contains_always_on_sections(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Orientation includes developer, work, sessions, narrative, pending."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba"),
        ]
        mock_always_on.return_value = [
            _make_always_on_node("guardrail-must-001", "guardrail", "Type hints"),
        ]

        profile = _make_profile()
        state = _make_state()
        state.narrative = "## Decisions\n- Chose sync model"
        state.next_session_prompt = "Continue with RAISE-169"
        result = assemble_orientation(
            profile, state, Path("/project"), session_id="SES-210"
        )

        # Always-on sections present
        assert "# Session Context" in result
        assert "Developer: Emilio" in result
        assert "Session: SES-210" in result
        assert "Story: S15.7 [implement]" in result
        assert "Epic: E15" in result
        assert "SES-097" in result  # last session
        assert "# Session Narrative" in result
        assert "Chose sync model" in result
        assert "# Next Session Prompt" in result
        assert "Continue with RAISE-169" in result
        assert "# Pending" in result
        assert "Pattern curation" in result

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_orientation_excludes_priming_sections(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Orientation does NOT include governance, behavioral, coaching, deadlines, progress."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba"),
        ]
        mock_always_on.return_value = [
            _make_always_on_node("guardrail-must-001", "guardrail", "Type hints"),
        ]

        profile = _make_profile()  # has deadlines and coaching
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15", stories_done=5, stories_total=8, sp_done=16, sp_total=25
        )
        result = assemble_orientation(profile, state, Path("/project"))

        assert "# Governance Primes" not in result
        assert "# Behavioral Primes" not in result
        assert "# Coaching" not in result
        assert "# Deadlines" not in result
        assert "Progress:" not in result

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_orientation_without_state(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Orientation works gracefully without session state."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = []
        mock_always_on.return_value = []

        profile = DeveloperProfile(name="New")
        result = assemble_orientation(profile, None, Path("/project"))

        assert "Developer: New (shu)" in result
        assert "(no previous session state)" in result


class TestFormatManifest:
    """Tests for format_manifest."""

    def test_manifest_format(self) -> None:
        """Manifest formats section counts and token estimates."""
        manifests = [
            SectionManifest(name="governance", count=14, token_estimate=350),
            SectionManifest(name="behavioral", count=12, token_estimate=240),
            SectionManifest(name="coaching", count=1, token_estimate=80),
            SectionManifest(name="deadlines", count=0, token_estimate=0),
        ]
        result = format_manifest(manifests)

        assert "# Available Context" in result
        assert "governance: 14 items (~350 tokens)" in result
        assert "behavioral: 12 items (~240 tokens)" in result
        assert "coaching: 1 items (~80 tokens)" in result
        assert "deadlines: 0 items" in result

    def test_manifest_empty_list(self) -> None:
        """Empty manifest list returns empty string."""
        result = format_manifest([])
        assert result == ""

    def test_manifest_zero_count_omits_tokens(self) -> None:
        """Zero-count sections don't show token estimate."""
        manifests = [SectionManifest(name="deadlines", count=0, token_estimate=0)]
        result = format_manifest(manifests)
        assert "deadlines: 0 items" in result
        assert "tokens" not in result.split("deadlines")[1]


class TestAssembleSections:
    """Tests for assemble_sections (queryable priming sections)."""

    @patch("raise_cli.session.bundle.get_always_on_primes")
    @patch("raise_cli.session.bundle.get_foundational_patterns")
    def test_governance_and_behavioral(
        self, mock_patterns: object, mock_always_on: object
    ) -> None:
        """Loading governance and behavioral returns both formatted sections."""
        assert callable(mock_patterns)
        assert callable(mock_always_on)
        mock_patterns.return_value = [
            _make_pattern("PAT-187", "Code as Gemba — observe before designing"),
        ]
        mock_always_on.return_value = [
            _make_always_on_node("guardrail-must-001", "guardrail", "Type hints"),
        ]

        result = assemble_sections(
            ["governance", "behavioral"],
            Path("/project"),
            _make_profile(),
            _make_state(),
        )

        assert "# Governance Primes" in result
        assert "guardrail-must-001" in result
        assert "# Behavioral Primes" in result
        assert "PAT-187" in result

    def test_coaching_only(self) -> None:
        """Loading coaching alone returns coaching section."""
        result = assemble_sections(
            ["coaching"],
            Path("/project"),
            _make_profile(),
            _make_state(),
        )

        assert "# Coaching" in result
        assert "architecture" in result

    def test_empty_sections_returns_empty(self) -> None:
        """Empty section list returns empty string."""
        result = assemble_sections(
            [],
            Path("/project"),
            _make_profile(),
            _make_state(),
        )
        assert result == ""

    def test_unknown_section_raises(self) -> None:
        """Unknown section name raises ValueError with valid names."""
        import pytest

        with pytest.raises(ValueError, match="Unknown section"):
            assemble_sections(
                ["unknown"],
                Path("/project"),
                _make_profile(),
                _make_state(),
            )

    def test_progress_with_data(self) -> None:
        """Loading progress returns progress section when data exists."""
        state = _make_state()
        state.progress = EpicProgress(
            epic="E15", stories_done=3, stories_total=8, sp_done=10, sp_total=25
        )
        result = assemble_sections(
            ["progress"],
            Path("/project"),
            _make_profile(),
            state,
        )
        assert "E15" in result
        assert "3/8" in result

    def test_deadlines_with_data(self) -> None:
        """Loading deadlines returns deadline section."""
        result = assemble_sections(
            ["deadlines"],
            Path("/project"),
            _make_profile(),  # has 2 deadlines
            _make_state(),
        )
        assert "# Deadlines" in result
        assert "F&F" in result

    def test_section_with_no_content_omitted(self) -> None:
        """Sections with no content are omitted from output."""
        profile = DeveloperProfile(name="New")  # no coaching, no deadlines
        result = assemble_sections(
            ["coaching", "deadlines"],
            Path("/project"),
            profile,
            _make_state(),
        )
        assert result == ""


class TestLiveBacklogStatus:
    """Tests for LiveBacklogStatus model and fetch_live_status()."""

    def testfetch_live_status_no_work(self) -> None:
        """When current_work has no epic/story keys, return empty status immediately."""
        state = SessionState(
            current_work=CurrentWork(epic="", story="", phase="", branch=""),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        result = fetch_live_status(state)
        assert result == LiveBacklogStatus()
        assert result.epic_status == ""
        assert result.story_status == ""
        assert result.warning == ""

    @patch("raise_cli.cli.commands._resolve.resolve_adapter")
    def testfetch_live_status_success(self, mock_resolve: MagicMock) -> None:
        """When adapter returns IssueDetail, populate status/summary fields."""
        from raise_cli.adapters.models import IssueDetail

        mock_adapter = MagicMock()
        mock_resolve.return_value = mock_adapter

        epic_detail = IssueDetail(
            key="RAISE-347",
            summary="Backlog Automation",
            status="in_progress",
            issue_type="Epic",
        )
        story_detail = IssueDetail(
            key="RAISE-390",
            summary="Session-start live query",
            status="selected_for_development",
            issue_type="Story",
        )
        mock_adapter.get_issue.side_effect = lambda k: (
            epic_detail if k == "RAISE-347" else story_detail
        )

        state = SessionState(
            current_work=CurrentWork(
                epic="RAISE-347",
                story="RAISE-390",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        result = fetch_live_status(state, timeout=5.0)
        assert result.epic_status == "in_progress"
        assert result.epic_summary == "Backlog Automation"
        assert result.story_status == "selected_for_development"
        assert result.story_summary == "Session-start live query"
        assert result.warning == ""

    @patch("raise_cli.cli.commands._resolve.resolve_adapter")
    def testfetch_live_status_timeout(self, mock_resolve: MagicMock) -> None:
        """When adapter.get_issue hangs, return warning with 'timeout'."""
        mock_adapter = MagicMock()
        mock_resolve.return_value = mock_adapter

        def slow_get_issue(key: str) -> None:
            time.sleep(10)

        mock_adapter.get_issue.side_effect = slow_get_issue

        state = SessionState(
            current_work=CurrentWork(
                epic="RAISE-347",
                story="",
                phase="implement",
                branch="epic/e347/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        # Use very short timeout to trigger quickly
        result = fetch_live_status(state, timeout=0.1)
        assert "timeout" in result.warning.lower()

    @patch("raise_cli.cli.commands._resolve.resolve_adapter")
    def testfetch_live_status_unavailable(self, mock_resolve: MagicMock) -> None:
        """When resolve_adapter raises SystemExit, return warning with 'unavailable'."""
        mock_resolve.side_effect = SystemExit(1)

        state = SessionState(
            current_work=CurrentWork(
                epic="RAISE-347",
                story="RAISE-390",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        result = fetch_live_status(state)
        assert "unavailable" in result.warning.lower()

    def testformat_work_section_with_live_status(self) -> None:
        """Live status adds annotation to epic and story lines."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E347",
                story="S347.5",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        live = LiveBacklogStatus(
            epic_status="in_progress",
            epic_summary="Backlog Automation",
            story_status="selected_for_development",
            story_summary="Session-start live query",
        )
        result = format_work_section(state, live=live)
        assert "in_progress (live)" in result
        assert "selected_for_development (live)" in result

    def testformat_work_section_with_live_warning(self) -> None:
        """Warning line appended when live has warning."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E347",
                story="S347.5",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        live = LiveBacklogStatus(
            warning="Backlog adapter unavailable — showing cached state"
        )
        result = format_work_section(state, live=live)
        assert "⚠" in result
        assert "unavailable" in result.lower()

    def testformat_work_section_no_live(self) -> None:
        """Existing behavior unchanged when live=None."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E347",
                story="S347.5",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        result = format_work_section(state, live=None)
        assert "(live)" not in result
        assert "⚠" not in result
        assert "Story: S347.5 [implement]" in result
        assert "Epic: E347" in result

    @patch("raise_cli.session.bundle.fetch_live_status")
    @patch("raise_cli.session.bundle.find_release_for_current_epic")
    def test_assemble_orientation_calls_live_status(
        self, mock_release: MagicMock, mock_fetch: MagicMock
    ) -> None:
        """assemble_orientation calls fetch_live_status and includes annotation."""
        mock_release.return_value = None
        mock_fetch.return_value = LiveBacklogStatus(
            epic_status="in_progress",
            story_status="done",
        )
        state = SessionState(
            current_work=CurrentWork(
                epic="E347",
                story="S347.5",
                phase="implement",
                branch="story/s347.5/test",
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 3, 3),
                developer="Test",
                summary="test",
            ),
        )
        profile = DeveloperProfile(name="Test")
        result = assemble_orientation(profile, state, Path("/project"))
        mock_fetch.assert_called_once_with(state)
        assert "in_progress (live)" in result
        assert "done (live)" in result


class TestStalenessDisclaimer:
    """Regression tests for RAISE-214: stale session state caveat.

    next_session_prompt and narrative are captured at session close.
    If work continues after close, they contain stale git/branch state.
    The fix adds a staleness caveat with the capture date so the reader
    knows to verify volatile state before acting on it.
    """

    def test_next_session_prompt_includes_staleness_caveat(self) -> None:
        """next_session_prompt includes capture date and staleness warning."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.7", phase="implement", branch="dev"
            ),
            last_session=LastSession(
                id="SES-300",
                date=date(2026, 3, 1),
                developer="Test",
                summary="session with stale state",
            ),
            next_session_prompt="ADR-015 still uncommitted. Branch has 3 commits ahead of dev.",
        )
        result = format_next_session_prompt(state)

        assert "# Next Session Prompt" in result
        assert "2026-03-01" in result
        assert "stale" in result.lower()
        assert "verify" in result.lower()
        # Original content still present
        assert "ADR-015 still uncommitted" in result

    def test_narrative_includes_staleness_caveat(self) -> None:
        """Narrative includes capture date and staleness warning."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.7", phase="implement", branch="dev"
            ),
            last_session=LastSession(
                id="SES-300",
                date=date(2026, 3, 1),
                developer="Test",
                summary="session with stale state",
            ),
            narrative="## Branch State\n- 3 commits ahead of dev, ADR-015 uncommitted",
        )
        result = format_narrative(state)

        assert "# Session Narrative" in result
        assert "2026-03-01" in result
        assert "stale" in result.lower()
        assert "verify" in result.lower()
        # Original content still present
        assert "ADR-015 uncommitted" in result

    def test_empty_next_session_prompt_no_caveat(self) -> None:
        """Empty next_session_prompt returns empty string — no caveat noise."""
        state = SessionState(
            current_work=CurrentWork(),
            last_session=LastSession(
                id="SES-300", date=date(2026, 3, 1), developer="Test", summary="test"
            ),
            next_session_prompt="",
        )
        assert format_next_session_prompt(state) == ""

    def test_empty_narrative_no_caveat(self) -> None:
        """Empty narrative returns empty string — no caveat noise."""
        state = SessionState(
            current_work=CurrentWork(),
            last_session=LastSession(
                id="SES-300", date=date(2026, 3, 1), developer="Test", summary="test"
            ),
            narrative="",
        )
        assert format_narrative(state) == ""

    def test_none_state_no_caveat(self) -> None:
        """None state returns empty string for both formatters."""
        assert format_next_session_prompt(None) == ""
        assert format_narrative(None) == ""
