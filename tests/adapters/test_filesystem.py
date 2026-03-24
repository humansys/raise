"""Tests for FilesystemPMAdapter."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from raise_cli.adapters.filesystem import FilesystemPMAdapter
from raise_cli.adapters.models import (
    AdapterHealth,
    BacklogComment,
    BacklogItem,
    BacklogLink,
    BatchResult,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
)

# ── T1: Pydantic models ────────────────────────────────────────────────


class TestBacklogModels:
    """T1: BacklogItem, BacklogComment, BacklogLink validation."""

    def test_backlog_item_validates(self) -> None:
        item = BacklogItem(
            key="E1", summary="Test", issue_type="Epic", status="pending"
        )
        assert item.key == "E1"
        assert item.status == "pending"

    def test_backlog_item_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            BacklogItem(key="E1", summary="Test")  # type: ignore[call-arg]

    def test_backlog_comment_validates(self) -> None:
        c = BacklogComment(
            id="E1-1", body="text", author="rai", created="2026-03-03T10:00:00Z"
        )
        assert c.id == "E1-1"
        assert c.author == "rai"

    def test_backlog_link_validates(self) -> None:
        link = BacklogLink(target="E2", link_type="blocks")
        assert link.target == "E2"
        assert link.link_type == "blocks"

    def test_backlog_item_round_trip(self) -> None:
        item = BacklogItem(
            key="E1",
            summary="Test",
            issue_type="Epic",
            status="pending",
            labels=["v2.2"],
        )
        data = item.model_dump()
        restored = BacklogItem(**data)
        assert restored == item

    def test_comments_and_links_default_empty(self) -> None:
        item = BacklogItem(
            key="E1", summary="Test", issue_type="Epic", status="pending"
        )
        assert item.comments == []
        assert item.links == []

    def test_optional_fields_default_none(self) -> None:
        item = BacklogItem(
            key="E1", summary="Test", issue_type="Epic", status="pending"
        )
        assert item.parent is None
        assert item.priority is None
        assert item.assignee is None


# ── T2: YAML store fixtures ─────────────────────────────────────────────


@pytest.fixture
def yaml_store(tmp_path: Path) -> Path:
    """Create a temp project with .raise/backlog/items/ YAML files."""
    items = tmp_path / ".raise" / "backlog" / "items"
    items.mkdir(parents=True)
    (items / "E1.yaml").write_text(
        "key: E1\n"
        "summary: Core Foundation\n"
        "issue_type: Epic\n"
        "status: complete\n"
        'created: "2026-01-01T00:00:00Z"\n'
        'updated: "2026-02-01T00:00:00Z"\n',
        encoding="utf-8",
    )
    (items / "E2.yaml").write_text(
        "key: E2\n"
        "summary: API Layer\n"
        "issue_type: Epic\n"
        "status: in_progress\n"
        'created: "2026-01-15T00:00:00Z"\n'
        'updated: "2026-02-15T00:00:00Z"\n',
        encoding="utf-8",
    )
    (items / "S1.1.yaml").write_text(
        "key: S1.1\n"
        "summary: First Story\n"
        "issue_type: Story\n"
        "status: pending\n"
        "parent: E1\n"
        'created: "2026-02-01T00:00:00Z"\n'
        'updated: "2026-02-01T00:00:00Z"\n',
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def yaml_adapter(yaml_store: Path) -> FilesystemPMAdapter:
    return FilesystemPMAdapter(project_root=yaml_store)


class TestYamlStoreGetIssue:
    """T2: get_issue over YAML store."""

    def test_get_epic(self, yaml_adapter: FilesystemPMAdapter) -> None:
        detail = yaml_adapter.get_issue("E1")
        assert isinstance(detail, IssueDetail)
        assert detail.key == "E1"
        assert detail.summary == "Core Foundation"
        assert detail.status == "complete"
        assert detail.issue_type == "Epic"

    def test_get_story_with_parent(self, yaml_adapter: FilesystemPMAdapter) -> None:
        detail = yaml_adapter.get_issue("S1.1")
        assert detail.key == "S1.1"
        assert detail.issue_type == "Story"
        assert detail.parent_key == "E1"

    def test_get_missing_raises_key_error(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.get_issue("S999.1")

    def test_malformed_yaml_raises(self, yaml_store: Path) -> None:
        items = yaml_store / ".raise" / "backlog" / "items"
        (items / "BAD.yaml").write_text(
            "key: BAD\nsummary: x\nissue_type: X\n", encoding="utf-8"
        )
        a = FilesystemPMAdapter(project_root=yaml_store)
        with pytest.raises(ValidationError):
            a.get_issue("BAD")


class TestYamlStoreHealth:
    """T2: health() over YAML store."""

    def test_healthy_with_items(self, yaml_adapter: FilesystemPMAdapter) -> None:
        h = yaml_adapter.health()
        assert isinstance(h, AdapterHealth)
        assert h.name == "filesystem"
        assert h.healthy is True
        assert "3 items" in h.message

    def test_healthy_empty_store(self, tmp_path: Path) -> None:
        items = tmp_path / ".raise" / "backlog" / "items"
        items.mkdir(parents=True)
        a = FilesystemPMAdapter(project_root=tmp_path)
        h = a.health()
        assert h.healthy is True
        assert "0 items" in h.message

    def test_unhealthy_missing_dir(self, tmp_path: Path) -> None:
        a = FilesystemPMAdapter(project_root=tmp_path)
        h = a.health()
        assert h.healthy is False


# ── T3: search over YAML store ──────────────────────────────────────────


class TestYamlStoreSearch:
    """T3: search() over YAML store."""

    def test_search_all(self, yaml_adapter: FilesystemPMAdapter) -> None:
        results = yaml_adapter.search("")
        assert len(results) == 3
        assert all(isinstance(r, IssueSummary) for r in results)

    def test_search_by_key_substring(self, yaml_adapter: FilesystemPMAdapter) -> None:
        results = yaml_adapter.search("E1")
        assert len(results) == 1
        assert results[0].key == "E1"

    def test_search_by_summary_case_insensitive(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        results = yaml_adapter.search("core foundation")
        assert len(results) == 1
        assert results[0].key == "E1"

    def test_search_status_field_value(self, yaml_adapter: FilesystemPMAdapter) -> None:
        results = yaml_adapter.search("status=complete")
        assert len(results) == 1
        assert results[0].key == "E1"

    def test_search_status_whitespace_tolerant(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        results = yaml_adapter.search("status = in_progress")
        assert len(results) == 1
        assert results[0].key == "E2"

    def test_search_limit(self, yaml_adapter: FilesystemPMAdapter) -> None:
        results = yaml_adapter.search("", limit=1)
        assert len(results) == 1

    def test_search_empty_store(self, tmp_path: Path) -> None:
        a = FilesystemPMAdapter(project_root=tmp_path)
        results = a.search("")
        assert results == []

    def test_search_no_match(self, yaml_adapter: FilesystemPMAdapter) -> None:
        results = yaml_adapter.search("nonexistent")
        assert results == []

    def test_search_results_sorted_by_key(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        results = yaml_adapter.search("")
        keys = [r.key for r in results]
        assert keys == sorted(keys)


# ── T4: create_issue + key generation over YAML store ──────────────────


class TestYamlStoreCreate:
    """T4: create_issue() over YAML store."""

    def test_create_epic_next_key(self, yaml_adapter: FilesystemPMAdapter) -> None:
        ref = yaml_adapter.create_issue(
            "PROJ", IssueSpec(summary="New Epic", issue_type="Epic")
        )
        assert isinstance(ref, IssueRef)
        assert ref.key == "E3"  # next after E2

    def test_create_epic_persisted(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.create_issue(
            "PROJ", IssueSpec(summary="New Epic", issue_type="Epic")
        )
        detail = yaml_adapter.get_issue("E3")
        assert detail.summary == "New Epic"
        assert detail.status == "pending"
        assert detail.issue_type == "Epic"
        assert detail.created != ""
        assert detail.updated != ""

    def test_create_story_under_parent(self, yaml_adapter: FilesystemPMAdapter) -> None:
        ref = yaml_adapter.create_issue(
            "PROJ",
            IssueSpec(
                summary="New Story",
                issue_type="Story",
                metadata={"parent_key": "E1"},
            ),
        )
        assert ref.key == "S1.2"  # next after S1.1
        detail = yaml_adapter.get_issue("S1.2")
        assert detail.parent_key == "E1"
        assert detail.issue_type == "Story"

    def test_create_story_without_parent_raises(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        with pytest.raises(KeyError, match="Story creation requires parent_key"):
            yaml_adapter.create_issue(
                "PROJ", IssueSpec(summary="Orphan Story", issue_type="Story")
            )

    def test_create_first_epic_in_empty_store(self, tmp_path: Path) -> None:
        items = tmp_path / ".raise" / "backlog" / "items"
        items.mkdir(parents=True)
        a = FilesystemPMAdapter(project_root=tmp_path)
        ref = a.create_issue("PROJ", IssueSpec(summary="First", issue_type="Epic"))
        assert ref.key == "E1"

    def test_create_first_story_under_epic(self, tmp_path: Path) -> None:
        items = tmp_path / ".raise" / "backlog" / "items"
        items.mkdir(parents=True)
        # Create epic E1 first
        (items / "E1.yaml").write_text(
            "key: E1\nsummary: Epic\nissue_type: Epic\nstatus: pending\n",
            encoding="utf-8",
        )
        a = FilesystemPMAdapter(project_root=tmp_path)
        ref = a.create_issue(
            "PROJ",
            IssueSpec(
                summary="First Story",
                issue_type="Story",
                metadata={"parent_key": "E1"},
            ),
        )
        assert ref.key == "S1.1"

    def test_create_epic_yaml_file_exists(
        self, yaml_store: Path, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        yaml_adapter.create_issue(
            "PROJ", IssueSpec(summary="New Epic", issue_type="Epic")
        )
        path = yaml_store / ".raise" / "backlog" / "items" / "E3.yaml"
        assert path.exists()


# ── T5: transition + update + batch over YAML store ────────────────────


class TestYamlStoreTransition:
    """T5: transition_issue() over YAML store."""

    def test_transition_returns_ref(self, yaml_adapter: FilesystemPMAdapter) -> None:
        ref = yaml_adapter.transition_issue("E1", "in_progress")
        assert isinstance(ref, IssueRef)
        assert ref.key == "E1"

    def test_transition_updates_status(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.transition_issue("E1", "in_progress")
        detail = yaml_adapter.get_issue("E1")
        assert detail.status == "in_progress"

    def test_transition_updates_timestamp(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        original = yaml_adapter.get_issue("E1")
        yaml_adapter.transition_issue("E1", "in_progress")
        updated = yaml_adapter.get_issue("E1")
        assert updated.updated != original.updated

    def test_transition_missing_raises(self, yaml_adapter: FilesystemPMAdapter) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.transition_issue("S999.1", "done")


class TestYamlStoreUpdate:
    """T5: update_issue() over YAML store."""

    def test_update_summary(self, yaml_adapter: FilesystemPMAdapter) -> None:
        ref = yaml_adapter.update_issue("E1", {"summary": "New Name"})
        assert isinstance(ref, IssueRef)
        detail = yaml_adapter.get_issue("E1")
        assert detail.summary == "New Name"

    def test_update_priority(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.update_issue("E1", {"priority": "P0"})
        detail = yaml_adapter.get_issue("E1")
        assert detail.priority == "P0"

    def test_update_preserves_other_fields(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        yaml_adapter.update_issue("E1", {"summary": "New Name"})
        detail = yaml_adapter.get_issue("E1")
        assert detail.status == "complete"  # unchanged
        assert detail.issue_type == "Epic"  # unchanged

    def test_update_ignores_key_mutation(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        """Mutating 'key' via update_issue must be silently ignored (C1 guard)."""
        yaml_adapter.update_issue("E1", {"key": "EVIL"})
        detail = yaml_adapter.get_issue("E1")
        assert detail.key == "E1"  # unchanged

    def test_update_ignores_created_mutation(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        original = yaml_adapter.get_issue("E1")
        yaml_adapter.update_issue("E1", {"created": "1970-01-01T00:00:00Z"})
        detail = yaml_adapter.get_issue("E1")
        assert detail.created == original.created

    def test_update_missing_raises(self, yaml_adapter: FilesystemPMAdapter) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.update_issue("S999.1", {"summary": "x"})


class TestYamlStoreBatch:
    """T5: batch_transition() over YAML store."""

    def test_batch_all_succeed(self, yaml_adapter: FilesystemPMAdapter) -> None:
        result = yaml_adapter.batch_transition(["E1", "E2"], "complete")
        assert isinstance(result, BatchResult)
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0

    def test_batch_partial_failure(self, yaml_adapter: FilesystemPMAdapter) -> None:
        result = yaml_adapter.batch_transition(["E1", "S999.1"], "complete")
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.failed[0].key == "S999.1"


# ── T6: comments + links over YAML store ───────────────────────────────


class TestYamlStoreComments:
    """T6: add_comment() and get_comments() over YAML store."""

    def test_add_comment_returns_ref(self, yaml_adapter: FilesystemPMAdapter) -> None:
        ref = yaml_adapter.add_comment("E1", "Started work")
        assert isinstance(ref, CommentRef)
        assert ref.id == "E1-1"

    def test_add_comment_persists(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.add_comment("E1", "Started work")
        comments = yaml_adapter.get_comments("E1")
        assert len(comments) == 1
        assert comments[0].body == "Started work"
        assert comments[0].author == "rai"
        assert comments[0].created != ""

    def test_add_second_comment_sequential_id(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        yaml_adapter.add_comment("E1", "First")
        ref2 = yaml_adapter.add_comment("E1", "Second")
        assert ref2.id == "E1-2"

    def test_add_comment_missing_raises(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.add_comment("S999.1", "text")

    def test_get_comments_returns_all(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.add_comment("E1", "First")
        yaml_adapter.add_comment("E1", "Second")
        comments = yaml_adapter.get_comments("E1")
        assert len(comments) == 2

    def test_get_comments_respects_limit(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        yaml_adapter.add_comment("E1", "First")
        yaml_adapter.add_comment("E1", "Second")
        comments = yaml_adapter.get_comments("E1", limit=1)
        assert len(comments) == 1

    def test_get_comments_missing_returns_empty(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        comments = yaml_adapter.get_comments("S999.1")
        assert comments == []


class TestYamlStoreLinks:
    """T6: link_issues() and link_to_parent() over YAML store."""

    def test_link_issues_adds_link(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.link_issues("E1", "E2", "blocks")
        item = yaml_adapter._load_item("E1")
        assert len(item.links) == 1
        assert item.links[0].target == "E2"
        assert item.links[0].link_type == "blocks"

    def test_link_issues_appends(self, yaml_adapter: FilesystemPMAdapter) -> None:
        yaml_adapter.link_issues("E1", "E2", "blocks")
        yaml_adapter.link_issues("E1", "S1.1", "relates_to")
        item = yaml_adapter._load_item("E1")
        assert len(item.links) == 2

    def test_link_issues_missing_raises(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.link_issues("S999.1", "E1", "blocks")

    def test_link_to_parent_sets_parent(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        yaml_adapter.link_to_parent("S1.1", "E2")
        detail = yaml_adapter.get_issue("S1.1")
        assert detail.parent_key == "E2"

    def test_link_to_parent_missing_raises(
        self, yaml_adapter: FilesystemPMAdapter
    ) -> None:
        with pytest.raises(KeyError, match="S999.1"):
            yaml_adapter.link_to_parent("S999.1", "E1")


# ── T7: Protocol compliance + integration ──────────────────────────────


class TestYamlProtocolCompliance:
    """T7: YAML adapter satisfies ProjectManagementAdapter protocol."""

    def test_isinstance_check(self, yaml_adapter: FilesystemPMAdapter) -> None:
        from raise_cli.adapters.protocols import ProjectManagementAdapter

        assert isinstance(yaml_adapter, ProjectManagementAdapter)


class TestYamlIntegration:
    """T7: End-to-end scenario over YAML store."""

    def test_full_lifecycle(self, tmp_path: Path) -> None:
        """Create epic -> create story -> transition -> comment -> search."""
        items = tmp_path / ".raise" / "backlog" / "items"
        items.mkdir(parents=True)
        a = FilesystemPMAdapter(project_root=tmp_path)

        # 1. Create epic
        epic_ref = a.create_issue(
            "PROJ", IssueSpec(summary="Integration Epic", issue_type="Epic")
        )
        assert epic_ref.key == "E1"

        # 2. Create story under epic
        story_ref = a.create_issue(
            "PROJ",
            IssueSpec(
                summary="Integration Story",
                issue_type="Story",
                metadata={"parent_key": "E1"},
            ),
        )
        assert story_ref.key == "S1.1"

        # 3. Transition story
        a.transition_issue("S1.1", "in_progress")
        detail = a.get_issue("S1.1")
        assert detail.status == "in_progress"
        assert detail.parent_key == "E1"

        # 4. Add comment to story
        cref = a.add_comment("S1.1", "Work started")
        assert cref.id == "S1.1-1"

        # 5. Search returns both
        results = a.search("")
        assert len(results) == 2
        keys = {r.key for r in results}
        assert keys == {"E1", "S1.1"}

        # 6. Get issue reflects comment count
        comments = a.get_comments("S1.1")
        assert len(comments) == 1
        assert comments[0].body == "Work started"

        # 7. Link issues
        a.link_issues("S1.1", "E1", "depends_on")
        item = a._load_item("S1.1")
        assert len(item.links) == 1

        # 8. Update issue
        a.update_issue("E1", {"summary": "Renamed Epic", "priority": "P0"})
        epic = a.get_issue("E1")
        assert epic.summary == "Renamed Epic"
        assert epic.priority == "P0"

        # 9. Batch transition
        result = a.batch_transition(["E1", "S1.1"], "complete")
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0
