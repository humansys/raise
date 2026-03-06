"""Tests for lifecycle hook events."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from raise_cli.hooks.events import (
    AdapterFailedEvent,
    AdapterLoadedEvent,
    BeforeReleasePublishEvent,
    BeforeSessionCloseEvent,
    DiscoverScanEvent,
    EmitResult,
    GraphBuildEvent,
    HookEvent,
    HookResult,
    InitCompleteEvent,
    PatternAddedEvent,
    ReleasePublishEvent,
    SessionCloseEvent,
    SessionStartEvent,
    WorkCloseEvent,
    WorkStartEvent,
)


class TestHookEvent:
    """Base event type tests."""

    def test_hook_event_accepts_explicit_timestamp(self) -> None:
        ts = datetime(2026, 2, 23, 12, 0, 0, tzinfo=UTC)
        event = SessionStartEvent(session_id="SES-1", developer="emilio", timestamp=ts)
        assert event.timestamp == ts


class TestHookResult:
    """HookResult tests."""

    def test_is_frozen(self) -> None:
        result = HookResult(status="ok")
        with pytest.raises(FrozenInstanceError):
            result.status = "abort"  # type: ignore[misc]


class TestEmitResult:
    """EmitResult tests."""

    def test_default_not_aborted(self) -> None:
        result = EmitResult()
        assert not result.aborted
        assert result.abort_message == ""
        assert result.handler_errors == ()

    def test_is_frozen(self) -> None:
        result = EmitResult()
        with pytest.raises(FrozenInstanceError):
            result.aborted = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Parametrized test for all 9 after-events + 2 before-events
# ---------------------------------------------------------------------------

_ALL_EVENTS = [
    (SessionStartEvent, "session:start", {"session_id": "S1", "developer": "e"}),
    (SessionCloseEvent, "session:close", {"session_id": "S1", "outcome": "success"}),
    (
        GraphBuildEvent,
        "graph:build",
        {"project_path": Path("/tmp"), "node_count": 1, "edge_count": 0},
    ),
    (
        PatternAddedEvent,
        "pattern:added",
        {"pattern_id": "PAT-1", "content": "test", "context": "testing"},
    ),
    (
        DiscoverScanEvent,
        "discover:scan",
        {"project_path": Path("/tmp"), "language": "python", "component_count": 5},
    ),
    (
        InitCompleteEvent,
        "init:complete",
        {"project_path": Path("/tmp"), "project_name": "my-project"},
    ),
    (
        AdapterLoadedEvent,
        "adapter:loaded",
        {
            "adapter_name": "jira",
            "group": "rai.adapters.pm",
            "adapter_type": "JiraAdapter",
        },
    ),
    (
        AdapterFailedEvent,
        "adapter:failed",
        {"adapter_name": "jira", "group": "rai.adapters.pm", "error": "import failed"},
    ),
    (
        ReleasePublishEvent,
        "release:publish",
        {"version": "2.1.0", "project_path": Path("/tmp")},
    ),
    (
        BeforeSessionCloseEvent,
        "before:session:close",
        {"session_id": "S1", "outcome": "success"},
    ),
    (
        BeforeReleasePublishEvent,
        "before:release:publish",
        {"version": "2.1.0", "project_path": Path("/tmp")},
    ),
    (
        WorkStartEvent,
        "work:start",
        {"work_type": "story", "work_id": "S301.6", "issue_key": "RAISE-301"},
    ),
    (
        WorkCloseEvent,
        "work:close",
        {"work_type": "story", "work_id": "S301.6", "issue_key": "RAISE-301"},
    ),
]


class TestAllEvents:
    """Parametrized tests covering all 13 event classes."""

    @pytest.mark.parametrize(
        ("cls", "expected_name", "kwargs"),
        _ALL_EVENTS,
        ids=[e[1] for e in _ALL_EVENTS],
    )
    def test_event_name(
        self, cls: type[HookEvent], expected_name: str, kwargs: dict[str, object]
    ) -> None:
        event = cls(**kwargs)
        assert event.event_name == expected_name

    @pytest.mark.parametrize(
        ("cls", "expected_name", "kwargs"),
        _ALL_EVENTS,
        ids=[e[1] for e in _ALL_EVENTS],
    )
    def test_is_frozen(
        self, cls: type[HookEvent], expected_name: str, kwargs: dict[str, object]
    ) -> None:
        event = cls(**kwargs)
        with pytest.raises(FrozenInstanceError):
            event.event_name = "tampered"  # type: ignore[misc]

    @pytest.mark.parametrize(
        ("cls", "expected_name", "kwargs"),
        _ALL_EVENTS,
        ids=[e[1] for e in _ALL_EVENTS],
    )
    def test_is_hook_event(
        self, cls: type[HookEvent], expected_name: str, kwargs: dict[str, object]
    ) -> None:
        event = cls(**kwargs)
        assert isinstance(event, HookEvent)

    @pytest.mark.parametrize(
        ("cls", "expected_name", "kwargs"),
        _ALL_EVENTS,
        ids=[e[1] for e in _ALL_EVENTS],
    )
    def test_has_timestamp(
        self, cls: type[HookEvent], expected_name: str, kwargs: dict[str, object]
    ) -> None:
        before = datetime.now(UTC)
        event = cls(**kwargs)
        after = datetime.now(UTC)
        assert before <= event.timestamp <= after
