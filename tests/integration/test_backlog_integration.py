"""Integration tests for backlog automation (E347).

Cross-component tests exercising real FilesystemPMAdapter with real file I/O.
Only ``resolve_adapter()`` is patched to inject the real FileAdapter —
all other calls are genuine (real YAML files, real Pydantic validation).

Architecture: S347.7 (E347 Backlog Automation)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rai_cli.adapters.filesystem import FilesystemPMAdapter
from rai_cli.adapters.models import IssueSpec


# ---------------------------------------------------------------------------
# T1: Protocol parity — full lifecycle round-trip
# ---------------------------------------------------------------------------


class TestProtocolParity:
    """Integration: all 11 ProjectManagementAdapter methods through real FileAdapter."""

    def test_full_lifecycle_round_trip(
        self, file_adapter: FilesystemPMAdapter, backlog_dir: Path
    ) -> None:
        """Create -> transition -> comment -> link -> search -> get -> update -> batch."""
        adapter = file_adapter

        # Create epic
        epic = adapter.create_issue("TEST", IssueSpec(summary="Epic One", issue_type="Epic"))
        assert epic.key == "E1"

        # Create story under epic
        story = adapter.create_issue(
            "TEST",
            IssueSpec(
                summary="Story One",
                issue_type="Story",
                metadata={"parent_key": "E1"},
            ),
        )
        assert story.key == "S1.1"

        # Transition
        adapter.transition_issue("S1.1", "in_progress")
        detail = adapter.get_issue("S1.1")
        assert detail.status == "in_progress"

        # Comment
        cref = adapter.add_comment("S1.1", "Work started")
        assert cref.id == "S1.1-1"

        # Get comments
        comments = adapter.get_comments("S1.1")
        assert len(comments) == 1
        assert comments[0].body == "Work started"
        assert comments[0].author == "rai"

        # Link issues
        adapter.link_issues("S1.1", "E1", "depends_on")

        # Link to parent (set parent explicitly)
        adapter.link_to_parent("S1.1", "E1")
        detail_after_parent = adapter.get_issue("S1.1")
        assert detail_after_parent.parent_key == "E1"

        # Search (empty query = all)
        results = adapter.search("")
        assert len(results) == 2

        # Get issue detail
        epic_detail = adapter.get_issue("E1")
        assert epic_detail.summary == "Epic One"
        assert epic_detail.issue_type == "Epic"

        # Update issue
        adapter.update_issue("E1", {"summary": "Renamed Epic", "priority": "P0"})
        updated = adapter.get_issue("E1")
        assert updated.summary == "Renamed Epic"
        assert updated.priority == "P0"

        # Batch transition
        result = adapter.batch_transition(["E1", "S1.1"], "done")
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0

        # Health
        health = adapter.health()
        assert health.healthy is True
        assert health.name == "filesystem"
        assert "2 items" in health.message

    def test_create_issue_returns_correct_model_fields(
        self, file_adapter: FilesystemPMAdapter
    ) -> None:
        """Verify IssueRef and IssueDetail fields are correctly populated."""
        adapter = file_adapter

        ref = adapter.create_issue(
            "TEST",
            IssueSpec(
                summary="Detailed Epic",
                issue_type="Epic",
                description="A detailed description",
                labels=["v2.2", "automation"],
            ),
        )
        assert ref.key == "E1"

        detail = adapter.get_issue("E1")
        assert detail.key == "E1"
        assert detail.summary == "Detailed Epic"
        assert detail.description == "A detailed description"
        assert detail.labels == ["v2.2", "automation"]
        assert detail.issue_type == "Epic"
        assert detail.status == "pending"
        assert detail.created != ""
        assert detail.updated != ""

    def test_search_empty_returns_empty_list(
        self, file_adapter: FilesystemPMAdapter
    ) -> None:
        """Empty YAML store returns empty search results."""
        results = file_adapter.search("")
        assert results == []

    def test_batch_transition_partial_failure(
        self, file_adapter: FilesystemPMAdapter
    ) -> None:
        """Batch transition with a missing key reports partial failure."""
        adapter = file_adapter
        adapter.create_issue("TEST", IssueSpec(summary="Real Epic", issue_type="Epic"))

        result = adapter.batch_transition(["E1", "GHOST"], "done")
        assert len(result.succeeded) == 1
        assert result.succeeded[0].key == "E1"
        assert len(result.failed) == 1
        assert result.failed[0].key == "GHOST"

    def test_multiple_comments_ordering(
        self, file_adapter: FilesystemPMAdapter
    ) -> None:
        """Multiple comments are stored and retrieved in order."""
        adapter = file_adapter
        adapter.create_issue("TEST", IssueSpec(summary="Epic", issue_type="Epic"))

        adapter.add_comment("E1", "First")
        adapter.add_comment("E1", "Second")
        adapter.add_comment("E1", "Third")

        comments = adapter.get_comments("E1")
        assert len(comments) == 3
        assert [c.body for c in comments] == ["First", "Second", "Third"]
        assert [c.id for c in comments] == ["E1-1", "E1-2", "E1-3"]

    def test_link_issues_persisted(
        self, file_adapter: FilesystemPMAdapter, backlog_dir: Path
    ) -> None:
        """Links are persisted in the YAML file on disk."""
        adapter = file_adapter
        adapter.create_issue("TEST", IssueSpec(summary="E1", issue_type="Epic"))
        adapter.create_issue(
            "TEST",
            IssueSpec(summary="S1", issue_type="Story", metadata={"parent_key": "E1"}),
        )

        adapter.link_issues("S1.1", "E1", "blocks")

        # Reload from disk to verify persistence
        fresh = FilesystemPMAdapter(project_root=backlog_dir.parent.parent.parent)
        item = fresh._load_item("S1.1")
        assert len(item.links) == 1
        assert item.links[0].target == "E1"
        assert item.links[0].link_type == "blocks"
