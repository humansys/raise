"""Tests for lifecycle hook events."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rai_cli.hooks.events import (
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
)


class TestHookEvent:
    """Base event type tests."""

    def test_hook_event_is_frozen(self) -> None:
        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        with pytest.raises(FrozenInstanceError):
            event.event_name = "other"  # type: ignore[misc]

    def test_hook_event_has_timestamp(self) -> None:
        before = datetime.now(timezone.utc)
        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        after = datetime.now(timezone.utc)
        assert before <= event.timestamp <= after

    def test_hook_event_accepts_explicit_timestamp(self) -> None:
        ts = datetime(2026, 2, 23, 12, 0, 0, tzinfo=timezone.utc)
        event = SessionStartEvent(
            session_id="SES-1", developer="emilio", timestamp=ts
        )
        assert event.timestamp == ts


class TestSessionStartEvent:
    """SessionStartEvent specific tests."""

    def test_event_name_is_session_start(self) -> None:
        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        assert event.event_name == "session:start"

    def test_payload_fields(self) -> None:
        event = SessionStartEvent(session_id="SES-42", developer="emilio")
        assert event.session_id == "SES-42"
        assert event.developer == "emilio"

    def test_is_hook_event_subclass(self) -> None:
        event = SessionStartEvent(session_id="SES-1", developer="emilio")
        assert isinstance(event, HookEvent)


class TestGraphBuildEvent:
    """GraphBuildEvent specific tests."""

    def test_event_name_is_graph_build(self) -> None:
        event = GraphBuildEvent(
            project_path=Path("/tmp/proj"), node_count=42, edge_count=15
        )
        assert event.event_name == "graph:build"

    def test_payload_fields(self) -> None:
        event = GraphBuildEvent(
            project_path=Path("/tmp/proj"), node_count=42, edge_count=15
        )
        assert event.project_path == Path("/tmp/proj")
        assert event.node_count == 42
        assert event.edge_count == 15

    def test_is_frozen(self) -> None:
        event = GraphBuildEvent(
            project_path=Path("/tmp/proj"), node_count=42, edge_count=15
        )
        with pytest.raises(FrozenInstanceError):
            event.node_count = 99  # type: ignore[misc]


class TestHookResult:
    """HookResult tests."""

    def test_ok_result(self) -> None:
        result = HookResult(status="ok")
        assert result.status == "ok"
        assert result.message == ""

    def test_abort_result(self) -> None:
        result = HookResult(status="abort", message="Compliance failed")
        assert result.status == "abort"
        assert result.message == "Compliance failed"

    def test_error_result(self) -> None:
        result = HookResult(status="error", message="oops")
        assert result.status == "error"

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

    def test_aborted_result(self) -> None:
        result = EmitResult(aborted=True, abort_message="blocked")
        assert result.aborted
        assert result.abort_message == "blocked"

    def test_is_frozen(self) -> None:
        result = EmitResult()
        with pytest.raises(FrozenInstanceError):
            result.aborted = True  # type: ignore[misc]


class TestBeforeSessionCloseEvent:
    """BeforeSessionCloseEvent tests."""

    def test_event_name(self) -> None:
        event = BeforeSessionCloseEvent(session_id="SES-1", outcome="success")
        assert event.event_name == "before:session:close"

    def test_payload_fields(self) -> None:
        event = BeforeSessionCloseEvent(session_id="SES-42", outcome="partial")
        assert event.session_id == "SES-42"
        assert event.outcome == "partial"

    def test_is_frozen(self) -> None:
        event = BeforeSessionCloseEvent(session_id="SES-1", outcome="success")
        with pytest.raises(FrozenInstanceError):
            event.session_id = "other"  # type: ignore[misc]

    def test_is_hook_event(self) -> None:
        event = BeforeSessionCloseEvent(session_id="SES-1", outcome="success")
        assert isinstance(event, HookEvent)


class TestBeforeReleasePublishEvent:
    """BeforeReleasePublishEvent tests."""

    def test_event_name(self) -> None:
        event = BeforeReleasePublishEvent(version="2.1.0", project_path=Path("/tmp"))
        assert event.event_name == "before:release:publish"

    def test_payload_fields(self) -> None:
        event = BeforeReleasePublishEvent(
            version="2.1.0", project_path=Path("/home/proj")
        )
        assert event.version == "2.1.0"
        assert event.project_path == Path("/home/proj")

    def test_is_frozen(self) -> None:
        event = BeforeReleasePublishEvent(version="2.1.0", project_path=Path("/tmp"))
        with pytest.raises(FrozenInstanceError):
            event.version = "3.0.0"  # type: ignore[misc]


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
        {"adapter_name": "jira", "group": "rai.adapters.pm", "adapter_type": "JiraAdapter"},
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
]


class TestAllEvents:
    """Parametrized tests covering all 11 event classes."""

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
        before = datetime.now(timezone.utc)
        event = cls(**kwargs)
        after = datetime.now(timezone.utc)
        assert before <= event.timestamp <= after
