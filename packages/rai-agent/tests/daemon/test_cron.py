# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for CronTrigger, RaiTrigger Protocol, and ScheduledRunEvent."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import pytest

from rai_agent.daemon.cron import CronTrigger, ScheduledRunEvent, _fire_handler
from rai_agent.daemon.runtime import RunConfig
from rai_agent.daemon.triggers import RaiTrigger


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


class TestScheduledRunEvent:
    """ScheduledRunEvent model serialization and structure."""

    def test_round_trip_serialization(self) -> None:
        """ScheduledRunEvent serializes to JSON and back without data loss."""
        rc = RunConfig(prompt="daily briefing")
        now = datetime.now(tz=UTC)
        event = ScheduledRunEvent(
            job_id="daily-brief",
            run_config=rc,
            scheduled_at=now,
        )
        data = event.model_dump(mode="json")
        restored = ScheduledRunEvent.model_validate(data)
        assert restored.job_id == "daily-brief"
        assert restored.run_config.prompt == "daily briefing"
        assert restored.scheduled_at == now

    def test_required_fields(self) -> None:
        """ScheduledRunEvent requires job_id, run_config, and scheduled_at."""
        import pydantic

        try:
            ScheduledRunEvent()  # type: ignore[call-arg]
            raise AssertionError("Expected ValidationError")
        except pydantic.ValidationError:
            pass

    def test_has_event_type(self) -> None:
        """ScheduledRunEvent has an event_type compatible with bubus EventBus."""
        rc = RunConfig(prompt="test")
        event = ScheduledRunEvent(
            job_id="j1",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        assert event.event_type == "ScheduledRunEvent"


class TestRaiTriggerProtocol:
    """RaiTrigger Protocol conformance checks."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """RaiTrigger should be runtime_checkable."""
        assert hasattr(RaiTrigger, "__protocol_attrs__") or hasattr(
            RaiTrigger, "_is_runtime_protocol"
        )

    def test_conforming_class_satisfies_protocol(self) -> None:
        """A class with start() and stop() async methods satisfies RaiTrigger."""

        class FakeTrigger:
            async def start(self) -> None: ...
            async def stop(self) -> None: ...

        assert isinstance(FakeTrigger(), RaiTrigger)

    def test_non_conforming_class_rejected(self) -> None:
        """A class missing start()/stop() does not satisfy RaiTrigger."""

        class BadTrigger:
            def go(self) -> None: ...

        assert not isinstance(BadTrigger(), RaiTrigger)


# ─── CronTrigger unit tests ─────────────────────────────────────────────────


class TestCronTrigger:
    """CronTrigger lifecycle, add/remove tests."""

    def test_satisfies_rai_trigger_protocol(self) -> None:
        """CronTrigger satisfies RaiTrigger Protocol."""
        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        assert isinstance(trigger, RaiTrigger)

    async def test_start_stop_lifecycle(self) -> None:
        """CronTrigger can start and stop without errors."""
        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        await trigger.start()
        await trigger.stop()

    async def test_add_job_registers_schedule(self) -> None:
        """add_job registers a schedule on the APScheduler data store."""
        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        await trigger.start()
        try:
            rc = RunConfig(prompt="daily brief")
            await trigger.add_job("daily", "0 7 * * *", rc)
            # Verify the schedule exists in APScheduler
            schedules = await trigger._scheduler.get_schedules()
            schedule_ids = [s.id for s in schedules]
            assert "daily" in schedule_ids
        finally:
            await trigger.stop()

    async def test_remove_job_removes_schedule(self) -> None:
        """remove_job removes a previously added schedule."""
        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        await trigger.start()
        try:
            rc = RunConfig(prompt="daily brief")
            await trigger.add_job("daily", "0 7 * * *", rc)
            await trigger.remove_job("daily")
            schedules = await trigger._scheduler.get_schedules()
            schedule_ids = [s.id for s in schedules]
            assert "daily" not in schedule_ids
        finally:
            await trigger.stop()


# ─── _fire_handler tests ────────────────────────────────────────────────────


class TestFireHandler:
    """Tests for the module-level _fire_handler (APScheduler entry point)."""

    async def test_fire_handler_emits_event(self) -> None:
        """_fire_handler deserializes RunConfig and emits ScheduledRunEvent."""
        from rai_agent.daemon import events

        rc = RunConfig(prompt="handler test")
        received: list[Any] = []
        bus = events.get_bus()
        bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

        await _fire_handler("handler-job", rc.model_dump_json())

        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].job_id == "handler-job"
        assert received[0].run_config.prompt == "handler test"

    async def test_fire_handler_invalid_json_noop(self) -> None:
        """_fire_handler logs warning and returns on invalid RunConfig JSON."""
        from rai_agent.daemon import events

        received: list[Any] = []
        bus = events.get_bus()
        bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

        # Should not raise — logs warning and returns
        await _fire_handler("bad-job", "not valid json!!!")

        await asyncio.sleep(0.1)

        assert len(received) == 0

    async def test_fire_handler_end_to_end_via_trigger(self) -> None:
        """CronTrigger.add_job → _fire_handler → EventBus (full path)."""
        from rai_agent.daemon import events

        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        await trigger.start()
        try:
            rc = RunConfig(prompt="e2e test")
            await trigger.add_job("e2e", "0 7 * * *", rc)

            received: list[Any] = []
            bus = events.get_bus()
            bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

            # Simulate what APScheduler would call
            await _fire_handler("e2e", rc.model_dump_json())

            await asyncio.sleep(0.1)

            assert len(received) == 1
            assert received[0].job_id == "e2e"
            assert received[0].run_config.prompt == "e2e test"
        finally:
            await trigger.stop()
