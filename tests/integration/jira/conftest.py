"""Fixtures for ACLI Jira adapter integration tests.

Reusable pattern for adapter integration suites:
  1. Check binary in PATH → skip if missing
  2. Check config file exists → skip if missing
  3. Return session-scoped adapter instance
  4. Provide session-scoped test issue (create on setup, Done on teardown)

To replicate for another adapter (e.g. Confluence):
  - Copy this file to tests/integration/confluence/conftest.py
  - Replace binary check, config path, adapter class, and test issue logic

Architecture: S494.6 (E494)
"""

from __future__ import annotations

import asyncio
import contextlib
import shutil
import time
from collections.abc import Coroutine, Generator
from pathlib import Path
from typing import Any

import pytest
from rai_pro.adapters.acli_jira import AcliJiraAdapter

from raise_cli.adapters.models import IssueRef, IssueSpec

# Test project — sandbox, safe to create/delete issues
TEST_PROJECT = "RTEST"

_JIRA_YAML = Path(".raise/jira.yaml")


def run_sync[T](coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


@pytest.fixture(scope="session")
def acli_adapter() -> AcliJiraAdapter:
    """Session-scoped AcliJiraAdapter. Skips if preconditions unmet.

    Precondition chain:
      1. acli binary in PATH
      2. .raise/jira.yaml exists
      3. Adapter instantiates without error
    """
    if not shutil.which("acli"):
        pytest.skip("ACLI binary not in PATH")
    if not _JIRA_YAML.exists():
        pytest.skip(f"No Jira config at {_JIRA_YAML}")

    try:
        adapter = AcliJiraAdapter()
    except Exception as exc:
        pytest.skip(f"AcliJiraAdapter init failed: {exc}")
    return adapter


@pytest.fixture(scope="session")
def test_issue(acli_adapter: AcliJiraAdapter) -> Generator[IssueRef, None, None]:
    """Create a test issue in RTEST for the session. Transition to Done on teardown."""
    spec = IssueSpec(
        summary=f"E494-INTEG-{int(time.time())}",
        issue_type="Task",
        description="Auto-created by S494.6 integration tests. Safe to delete.",
        labels=["e494-test"],
    )
    ref = run_sync(acli_adapter.create_issue(TEST_PROJECT, spec))
    yield ref
    with contextlib.suppress(Exception):
        run_sync(acli_adapter.transition_issue(ref.key, "done"))


@pytest.fixture(scope="session")
def second_test_issue(acli_adapter: AcliJiraAdapter) -> Generator[IssueRef, None, None]:
    """Second test issue for batch operations."""
    spec = IssueSpec(
        summary=f"E494-INTEG-BATCH-{int(time.time())}",
        issue_type="Task",
        description="Batch test issue. Safe to delete.",
        labels=["e494-test"],
    )
    ref = run_sync(acli_adapter.create_issue(TEST_PROJECT, spec))
    yield ref
    with contextlib.suppress(Exception):
        run_sync(acli_adapter.transition_issue(ref.key, "done"))
