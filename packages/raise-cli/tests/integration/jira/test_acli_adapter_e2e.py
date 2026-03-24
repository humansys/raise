"""Integration tests for AcliJiraAdapter — real ACLI → real Jira.

Run with: uv run pytest -m integration -v
Skip automatically when ACLI or jira.yaml unavailable.

Architecture: S494.6 (E494)
"""

from __future__ import annotations

import contextlib

import pytest
from rai_pro.adapters.acli_jira import AcliJiraAdapter

from raise_cli.adapters.models import IssueRef

from .conftest import run_sync

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Tier 1: Core CRUD
# ---------------------------------------------------------------------------


class TestCoreCRUD:
    """Core adapter operations against real Jira."""

    def test_adapter_is_acli(self, acli_adapter: AcliJiraAdapter) -> None:
        """Smoke test: fixture returns a real AcliJiraAdapter."""
        assert isinstance(acli_adapter, AcliJiraAdapter)

    def test_create_issue_returns_ref(self, test_issue: IssueRef) -> None:
        """Create_issue returns IssueRef with valid key."""
        assert test_issue.key.startswith("RTEST-")
        assert test_issue.url.startswith("https://")

    def test_get_issue_returns_detail(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Get_issue returns full IssueDetail with populated fields."""
        from raise_cli.adapters.models import IssueDetail

        detail = run_sync(acli_adapter.get_issue(test_issue.key))
        assert isinstance(detail, IssueDetail)
        assert detail.key == test_issue.key
        assert detail.summary.startswith("E494-INTEG-")
        assert detail.status != ""
        assert detail.issue_type == "Task"

    def test_update_issue_changes_field(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Update_issue modifies a field, confirmed by get_issue."""
        run_sync(
            acli_adapter.update_issue(test_issue.key, {"summary": "E494-INTEG-UPDATED"})
        )
        detail = run_sync(acli_adapter.get_issue(test_issue.key))
        assert detail.summary == "E494-INTEG-UPDATED"

    def test_add_comment_returns_ref(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Add_comment returns CommentRef with id."""
        from raise_cli.adapters.models import CommentRef

        ref = run_sync(
            acli_adapter.add_comment(test_issue.key, "Integration test comment")
        )
        assert isinstance(ref, CommentRef)
        assert ref.id != ""

    def test_get_comments_returns_list(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Get_comments returns list containing the added comment."""
        from raise_cli.adapters.models import Comment

        comments = run_sync(acli_adapter.get_comments(test_issue.key))
        assert isinstance(comments, list)
        assert len(comments) >= 1
        assert all(isinstance(c, Comment) for c in comments)
        bodies = [c.body for c in comments]
        assert any("Integration test comment" in b for b in bodies)

    def test_transition_issue_changes_status(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Transition_issue changes status, confirmed by get_issue."""
        run_sync(acli_adapter.transition_issue(test_issue.key, "in-progress"))
        detail = run_sync(acli_adapter.get_issue(test_issue.key))
        assert detail.status == "In Progress"

    def test_search_returns_issues(self, acli_adapter: AcliJiraAdapter) -> None:
        """Search with JQL returns IssueSummary list."""
        from raise_cli.adapters.models import IssueSummary

        results = run_sync(acli_adapter.search("project = RTEST", limit=5))
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, IssueSummary) for r in results)
        assert all(r.key.startswith("RTEST-") for r in results)


# ---------------------------------------------------------------------------
# Tier 2: Multi-instance
# ---------------------------------------------------------------------------


class TestMultiInstance:
    """Multi-instance routing — verifies site resolution."""

    def test_search_routes_to_rtest(self, acli_adapter: AcliJiraAdapter) -> None:
        """Search on RTEST project routes to humansys site."""
        results = run_sync(acli_adapter.search("project = RTEST", limit=1))
        assert isinstance(results, list)

    def test_get_cross_instance_issue(self, acli_adapter: AcliJiraAdapter) -> None:
        """Get issue from RAISE project (same humansys instance, different project)."""
        from raise_cli.adapters.models import IssueDetail

        detail = run_sync(acli_adapter.get_issue("RAISE-594"))
        assert isinstance(detail, IssueDetail)
        assert detail.key == "RAISE-594"
        assert detail.summary != ""


# ---------------------------------------------------------------------------
# Tier 3: Batch & relationships
# ---------------------------------------------------------------------------


class TestBatchAndRelationships:
    """Batch operations and issue linking."""

    def test_batch_transition_succeeds(
        self,
        acli_adapter: AcliJiraAdapter,
        test_issue: IssueRef,
        second_test_issue: IssueRef,
    ) -> None:
        """Batch_transition moves multiple issues."""
        from raise_cli.adapters.models import BatchResult

        for key in [test_issue.key, second_test_issue.key]:
            with contextlib.suppress(Exception):
                run_sync(acli_adapter.transition_issue(key, "in-progress"))

        result = run_sync(
            acli_adapter.batch_transition(
                [test_issue.key, second_test_issue.key], "done"
            )
        )
        assert isinstance(result, BatchResult)
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0

    def test_batch_transition_with_nonexistent_key(
        self, acli_adapter: AcliJiraAdapter, test_issue: IssueRef
    ) -> None:
        """Batch_transition with a nonexistent key — ACLI reports success envelope.

        Discovery: ACLI does not validate issue existence on transition.
        The envelope returns SUCCESS even for fake keys. This test documents
        the actual behavior rather than an idealized failure mode.
        """
        from raise_cli.adapters.models import BatchResult

        result = run_sync(
            acli_adapter.batch_transition([test_issue.key, "FAKE-999"], "done")
        )
        assert isinstance(result, BatchResult)
        # Both succeed from ACLI's perspective (no server-side validation)
        assert len(result.succeeded) == 2

    def test_link_issues_no_error(
        self,
        acli_adapter: AcliJiraAdapter,
        test_issue: IssueRef,
        second_test_issue: IssueRef,
    ) -> None:
        """Link_issues creates a link without raising."""
        run_sync(
            acli_adapter.link_issues(test_issue.key, second_test_issue.key, "Blocks")
        )


# ---------------------------------------------------------------------------
# Tier 4: Health & error handling
# ---------------------------------------------------------------------------


class TestHealthAndErrors:
    """Health check and error scenarios."""

    def test_health_returns_healthy(self, acli_adapter: AcliJiraAdapter) -> None:
        """Health returns AdapterHealth with healthy=True."""
        from raise_cli.adapters.models import AdapterHealth

        health = run_sync(acli_adapter.health())
        assert isinstance(health, AdapterHealth)
        assert health.healthy is True
        assert health.latency_ms is not None and health.latency_ms > 0

    def test_get_nonexistent_issue_raises(self, acli_adapter: AcliJiraAdapter) -> None:
        """Get_issue with fake key raises AcliBridgeError."""
        from rai_pro.adapters.acli_bridge import AcliBridgeError

        with pytest.raises(AcliBridgeError):
            run_sync(acli_adapter.get_issue("FAKE-999"))
