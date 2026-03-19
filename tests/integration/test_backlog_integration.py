"""Integration tests for backlog automation (E347).

Cross-component tests exercising real FilesystemPMAdapter with real file I/O.
Only ``resolve_adapter()`` is patched to inject the real FileAdapter —
all other calls are genuine (real YAML files, real Pydantic validation).

Architecture: S347.7 (E347 Backlog Automation)

Dogfood Review — E347 Lifecycle Evidence
=========================================
This epic (E347: Backlog Automation) was managed using the tools it built:

- S347.1: FilesystemPMAdapter — YAML store for backlog items
- S347.2: FileAdapter protocol parity — all 11 methods implemented
- S347.3: BacklogHook — auto-sync on work lifecycle events
- S347.4: Hook wiring — BacklogHook -> resolve_adapter -> FileAdapter
- S347.5: Session-start live query — _fetch_live_status with real adapter
- S347.6: Sync guard — sync_backlog rejects FilesystemPMAdapter
- S347.7: This module — integration tests proving components work together

Test categories:
  TestProtocolParity    — Full lifecycle round-trip through real FileAdapter
  TestHookAdapterFlow   — BacklogHook.handle() with real FileAdapter (no mocks)
  TestSessionLiveQuery  — _fetch_live_status with real YAML items
  TestSyncGuard         — sync_backlog rejects FilesystemPMAdapter
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from raise_cli.adapters.filesystem import FilesystemPMAdapter
from raise_cli.adapters.models import IssueSpec

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
        epic = adapter.create_issue(
            "TEST", IssueSpec(summary="Epic One", issue_type="Epic")
        )
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

        # Reload from disk to verify persistence (read YAML directly, no private API)
        raw = yaml.safe_load((backlog_dir / "S1.1.yaml").read_text(encoding="utf-8"))
        assert len(raw["links"]) == 1
        assert raw["links"][0]["target"] == "E1"
        assert raw["links"][0]["link_type"] == "blocks"


# ---------------------------------------------------------------------------
# T2: BacklogHook -> FileAdapter flow
# ---------------------------------------------------------------------------


class TestHookAdapterFlow:
    """Integration: BacklogHook.handle() with real FilesystemPMAdapter."""

    def test_hook_start_event_creates_and_transitions_epic(
        self,
        tmp_path: Path,
        backlog_dir: Path,
        jira_yaml_setup: Path,
    ) -> None:
        """Epic start event -> creates YAML item and transitions to in-progress."""
        from raise_cli.hooks.builtin.backlog import BacklogHook
        from raise_cli.hooks.events import WorkLifecycleEvent

        adapter = FilesystemPMAdapter(project_root=tmp_path)
        hook = BacklogHook(project_root=tmp_path)
        event = WorkLifecycleEvent(
            work_type="epic", work_id="E99", event="start", phase="design"
        )

        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"

        # Verify YAML file created on disk
        items = list(backlog_dir.glob("*.yaml"))
        assert len(items) == 1

        # Verify issue was transitioned to in-progress
        detail = adapter.get_issue(items[0].stem)
        assert detail.status == "in-progress"
        assert detail.summary == "E99"

    def test_hook_complete_event_transitions_to_done(
        self,
        tmp_path: Path,
        backlog_dir: Path,
        jira_yaml_setup: Path,
    ) -> None:
        """Complete event -> transitions existing issue to done."""
        from raise_cli.hooks.builtin.backlog import BacklogHook
        from raise_cli.hooks.events import WorkLifecycleEvent

        adapter = FilesystemPMAdapter(project_root=tmp_path)

        # Pre-create an epic so complete can find it
        adapter.create_issue("TEST", IssueSpec(summary="E99", issue_type="Epic"))
        adapter.transition_issue("E1", "in-progress")

        hook = BacklogHook(project_root=tmp_path)
        event = WorkLifecycleEvent(
            work_type="epic", work_id="E99", event="complete", phase="close"
        )

        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter", return_value=adapter
        ):
            result = hook.handle(event)

        assert result.status == "ok"

        # Verify status is now done
        detail = adapter.get_issue("E1")
        assert detail.status == "done"

    def test_hook_with_unavailable_adapter_returns_error(
        self,
        tmp_path: Path,
        jira_yaml_setup: Path,
    ) -> None:
        """BacklogHook degrades gracefully when adapter raises."""
        from raise_cli.hooks.builtin.backlog import BacklogHook
        from raise_cli.hooks.events import WorkLifecycleEvent

        hook = BacklogHook(project_root=tmp_path)
        event = WorkLifecycleEvent(
            work_type="epic", work_id="E1", event="start", phase="design"
        )

        with patch(
            "raise_cli.hooks.builtin.backlog.resolve_adapter",
            side_effect=RuntimeError("MCP bridge down"),
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert "adapter" in result.message.lower()


# ---------------------------------------------------------------------------
# T3: Session-start live query with real FileAdapter
# ---------------------------------------------------------------------------


class TestSessionLiveQuery:
    """Integration: _fetch_live_status() with real YAML items via FileAdapter."""

    def test_fetch_live_status_with_file_adapter(
        self,
        tmp_path: Path,
        backlog_dir: Path,
        write_yaml_item: Callable[..., None],
    ) -> None:
        """Pre-populated YAML items -> correct LiveBacklogStatus fields."""
        from raise_cli.schemas.session_state import (
            CurrentWork,
            LastSession,
            SessionState,
        )
        from raise_cli.session.bundle_data import fetch_live_status

        # Write YAML items on disk
        write_yaml_item(
            backlog_dir / "E1.yaml",
            key="E1",
            summary="My Epic",
            status="in_progress",
            issue_type="Epic",
        )
        write_yaml_item(
            backlog_dir / "S1.1.yaml",
            key="S1.1",
            summary="My Story",
            status="in_progress",
            issue_type="Story",
            parent="E1",
        )

        state = SessionState(
            current_work=CurrentWork(
                epic="E1",
                story="S1.1",
                branch="story/s1.1/test",
                phase="implement",
            ),
            last_session=LastSession(
                id="SES-001",
                date="2026-03-03",
                developer="test",
                summary="test session",
            ),
        )

        adapter = FilesystemPMAdapter(project_root=tmp_path)

        with patch(
            "raise_cli.cli.commands._resolve.resolve_adapter", return_value=adapter
        ):
            live = fetch_live_status(state, timeout=10.0)

        assert live.epic_status == "in_progress"
        assert live.epic_summary == "My Epic"
        assert live.story_status == "in_progress"
        assert live.story_summary == "My Story"
        assert live.warning == ""

    def test_fetch_live_status_with_no_work_returns_empty(self) -> None:
        """No current work -> empty LiveBacklogStatus without adapter call."""
        from raise_cli.session.bundle_data import LiveBacklogStatus, fetch_live_status

        result = fetch_live_status(None)
        assert result == LiveBacklogStatus()

    def test_manifest_adapter_default_selects_filesystem(
        self, tmp_path: Path, backlog_dir: Path
    ) -> None:
        """manifest.yaml with backlog.adapter_default=filesystem selects FileAdapter."""
        from raise_cli.cli.commands._resolve import resolve_adapter
        from raise_cli.onboarding.manifest import load_manifest

        # Write manifest.yaml
        manifest_dir = tmp_path / ".raise"
        manifest_dir.mkdir(exist_ok=True)
        (manifest_dir / "manifest.yaml").write_text(
            "project:\n  name: test\nbacklog:\n  adapter_default: filesystem\n"
        )

        # Patch CWD for manifest loading and entry points
        with (
            patch("raise_cli.cli.commands._resolve.load_manifest") as mock_manifest,
            patch("raise_cli.cli.commands._resolve._discover_pm") as mock_discover,
        ):
            # Simulate manifest returning adapter_default=filesystem
            manifest = load_manifest(tmp_path)
            mock_manifest.return_value = manifest

            # Simulate entry points including filesystem
            mock_discover.return_value = {
                "filesystem": lambda: FilesystemPMAdapter(project_root=tmp_path),
            }

            adapter = resolve_adapter(None)

        assert isinstance(adapter, FilesystemPMAdapter)


# ---------------------------------------------------------------------------
# T4: Sync guard — sync_backlog rejects FilesystemPMAdapter
# ---------------------------------------------------------------------------


class TestSyncGuard:
    """Integration: sync_backlog guard rejects real FilesystemPMAdapter instance."""

    def test_sync_rejects_filesystem_adapter(
        self, file_adapter: FilesystemPMAdapter, tmp_path: Path
    ) -> None:
        """sync_backlog raises ValueError for FilesystemPMAdapter (source of truth)."""
        from raise_cli.backlog.sync import sync_backlog

        output_path = tmp_path / "governance" / "backlog.md"

        with pytest.raises(ValueError, match="source of truth"):
            sync_backlog(
                adapter=file_adapter,
                adapter_name="filesystem",
                project_filter=None,
                output_path=output_path,
            )

        # Verify output file was NOT created (guard fires before write)
        assert not output_path.exists()
