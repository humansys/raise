"""Shared fixtures for daemon tests."""

from __future__ import annotations

import pytest

from rai_agent.daemon.events import reset_bus


@pytest.fixture(autouse=True)
def _reset_event_bus() -> None:  # type: ignore[misc]
    """Reset the EventBus singleton between tests."""
    yield  # type: ignore[misc]
    reset_bus()
