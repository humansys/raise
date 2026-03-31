"""Integration tests for PythonApiJiraAdapter (S1052.6 / RAISE-1052).

Tests exercise the full adapter protocol against live Jira Cloud.
All tests are **skipped** when ``JIRA_API_TOKEN`` is not set in the
environment, so they never fail in CI without credentials.

Requires: JIRA_API_TOKEN, JIRA_USERNAME (or defaults), JIRA_URL (optional).
Target instance: humansys.atlassian.net, project RAISE.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import TYPE_CHECKING

import pytest

from raise_cli.adapters.models import (
    AdapterHealth,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSummary,
)

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

_SKIP_REASON = "JIRA_API_TOKEN not set — skipping integration tests"
pytestmark = pytest.mark.skipif(
    not os.environ.get("JIRA_API_TOKEN"),
    reason=_SKIP_REASON,
)

_PROJECT_KEY = "RAISE"
_KNOWN_ISSUE = "RAISE-1052"
_TEST_LABEL = "rai-test"


def _run[T](coro: Coroutine[object, object, T]) -> T:
    """Run an async coroutine synchronously (no pytest-asyncio dependency)."""
    return asyncio.run(coro)


class TestJiraAdapterIntegration:
    """Live Jira API tests — require JIRA_API_TOKEN env var.

    Tests the full adapter protocol: create, get, search, transition,
    comment, link, and health. Uses real Jira instance.
    """

    def _make_adapter(self) -> PythonApiJiraAdapter:
        """Create a PythonApiJiraAdapter from environment + project config."""
        from pathlib import Path

        from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

        # Use the repo root (contains .raise/jira.yaml)
        project_root = Path(__file__).resolve().parents[4]
        return PythonApiJiraAdapter(project_root=project_root)

    # ── Search ─────────────────────────────────────────────────────

    def test_search_returns_issue_summaries(self) -> None:
        adapter = self._make_adapter()
        results: list[IssueSummary] = _run(
            adapter.search(f"project = {_PROJECT_KEY}", limit=5)
        )
        assert len(results) > 0
        assert all(isinstance(r, IssueSummary) for r in results)
        first = results[0]
        assert first.key.startswith(f"{_PROJECT_KEY}-")
        assert first.summary  # non-empty

    # ── Get issue ──────────────────────────────────────────────────

    def test_get_issue_returns_detail(self) -> None:
        adapter = self._make_adapter()
        detail: IssueDetail = _run(adapter.get_issue(_KNOWN_ISSUE))
        assert isinstance(detail, IssueDetail)
        assert detail.key == _KNOWN_ISSUE
        assert detail.summary  # non-empty
        assert detail.status  # non-empty
        assert detail.url
        assert _KNOWN_ISSUE in detail.url

    # ── Health ─────────────────────────────────────────────────────

    def test_health_returns_healthy(self) -> None:
        adapter = self._make_adapter()
        health: AdapterHealth = _run(adapter.health())
        assert isinstance(health, AdapterHealth)
        assert health.healthy is True
        assert health.name == "jira"
        assert health.latency_ms is not None
        assert health.latency_ms > 0

    # ── Create + Get + Transition ──────────────────────────────────

    def test_create_get_transition_lifecycle(self) -> None:
        """Create a test issue, verify get, transition to Done."""
        from raise_cli.adapters.models import IssueSpec

        adapter = self._make_adapter()
        tag = uuid.uuid4().hex[:8]
        spec = IssueSpec(
            summary=f"[rai-test] S1052.6 integration test {tag}",
            issue_type="Task",
            description=f"Auto-created by S1052.6 integration tests. Tag: {tag}",
            labels=[_TEST_LABEL],
        )

        # Create
        ref: IssueRef = _run(adapter.create_issue(_PROJECT_KEY, spec))
        assert isinstance(ref, IssueRef)
        assert ref.key.startswith(f"{_PROJECT_KEY}-")
        created_key = ref.key

        try:
            # Get — verify fields populated
            detail: IssueDetail = _run(adapter.get_issue(created_key))
            assert isinstance(detail, IssueDetail)
            assert detail.key == created_key
            assert tag in detail.summary
            assert _TEST_LABEL in detail.labels

            # Transition to Done
            result: IssueRef = _run(adapter.transition_issue(created_key, "done"))
            assert isinstance(result, IssueRef)
            assert result.key == created_key

            # Verify status changed
            updated: IssueDetail = _run(adapter.get_issue(created_key))
            assert updated.status.lower() == "done"
        except Exception:
            # Log the key for manual cleanup if something fails
            pytest.fail(
                f"Lifecycle test failed. Created issue {created_key} "
                f"may need manual cleanup (label: {_TEST_LABEL})"
            )

    # ── Comments ───────────────────────────────────────────────────

    def test_add_comment_and_get_comments(self) -> None:
        """Add a comment to a known issue, verify it appears."""
        adapter = self._make_adapter()
        tag = uuid.uuid4().hex[:8]
        body = f"[rai-test] S1052.6 comment test {tag}"

        # Add comment
        ref: CommentRef = _run(adapter.add_comment(_KNOWN_ISSUE, body))
        assert isinstance(ref, CommentRef)
        assert ref.id  # non-empty

        # Get comments — increase limit to catch our new comment
        comments: list[Comment] = _run(
            adapter.get_comments(_KNOWN_ISSUE, limit=50)
        )
        assert len(comments) > 0
        assert all(isinstance(c, Comment) for c in comments)

        # Find our comment by ID (body may be ADF-transformed)
        found = any(c.id == ref.id for c in comments)
        assert found, f"Comment {ref.id} not found in comments (got {len(comments)})"

    # ── Link issues ────────────────────────────────────────────────

    def test_link_issues(self) -> None:
        """Create a temp issue, then link it to RAISE-1052 via 'Relates'."""
        from raise_cli.adapters.models import IssueSpec

        adapter = self._make_adapter()
        tag = uuid.uuid4().hex[:8]
        spec = IssueSpec(
            summary=f"[rai-test] S1052.6 link test {tag}",
            issue_type="Task",
            labels=[_TEST_LABEL],
        )

        ref: IssueRef = _run(adapter.create_issue(_PROJECT_KEY, spec))
        created_key = ref.key

        try:
            # Link: created issue relates to RAISE-1052
            _run(adapter.link_issues(created_key, _KNOWN_ISSUE, "Relates"))
            # If no exception, link was created successfully
        except Exception:
            pytest.fail(
                f"Link test failed. Created issue {created_key} "
                f"may need manual cleanup (label: {_TEST_LABEL})"
            )
