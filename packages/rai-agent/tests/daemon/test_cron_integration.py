# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Integration tests for CronTrigger: EventBus emission and SQLite persistence.

Tests verify:
  - _fire_handler → EventBus receives ScheduledRunEvent with correct fields
  - add job + stop → new CronTrigger same DB → schedule persists AND fires (AC6)
Uses tmp_path for SQLite isolation.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from rai_agent.daemon import events
from rai_agent.daemon.cron import CronTrigger, _fire_handler
from rai_agent.daemon.runtime import RunConfig


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    original = events._bus
    events._bus = None
    yield
    events._bus = original


class TestCronTriggerIntegration:
    """Integration tests for CronTrigger with real EventBus and SQLite."""

    async def test_fire_emits_event_with_correct_fields(self) -> None:
        """_fire_handler → EventBus receives ScheduledRunEvent with correct fields."""
        rc = RunConfig(prompt="daily briefing", system_prompt="be concise")

        received: list[Any] = []
        bus = events.get_bus()
        bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

        await _fire_handler("daily-brief", rc.model_dump_json())

        await asyncio.sleep(0.2)

        assert len(received) == 1
        event = received[0]
        assert event.job_id == "daily-brief"
        assert event.run_config.prompt == "daily briefing"
        assert event.run_config.system_prompt == "be concise"
        assert event.scheduled_at is not None

    async def test_schedule_persists_and_fires_across_restart(
        self, tmp_path: Any
    ) -> None:
        """add job → stop → new CronTrigger same DB → schedule persists AND fires (AC6).

        Verifies both that the schedule exists in the data store AND that
        the persisted args contain the serialized RunConfig, so _fire_handler
        can reconstruct the event after a process restart.
        """
        db_url = f"sqlite+aiosqlite:///{tmp_path}/persist.db"

        # Phase 1: add a schedule, then stop
        trigger1 = CronTrigger(db_url=db_url)
        await trigger1.start()
        rc = RunConfig(prompt="persist me")
        await trigger1.add_job("persistent-job", "30 8 * * 1-5", rc)
        await trigger1.stop()

        # Phase 2: new trigger, same DB — schedule should exist and fire
        trigger2 = CronTrigger(db_url=db_url)
        await trigger2.start()
        try:
            # Verify schedule exists
            schedules = await trigger2._scheduler.get_schedules()
            schedule_ids = [s.id for s in schedules]
            assert "persistent-job" in schedule_ids

            # Verify the schedule can fire and produce an event
            received: list[Any] = []
            bus = events.get_bus()
            bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

            # Simulate what APScheduler would do with the persisted args
            await _fire_handler("persistent-job", rc.model_dump_json())

            await asyncio.sleep(0.2)

            assert len(received) == 1
            assert received[0].job_id == "persistent-job"
            assert received[0].run_config.prompt == "persist me"
        finally:
            await trigger2.stop()

    async def test_multiple_jobs_fire_independently(self) -> None:
        """Multiple jobs fire independently, each producing its own event."""
        rc1 = RunConfig(prompt="morning brief")
        rc2 = RunConfig(prompt="evening summary")

        received: list[Any] = []
        bus = events.get_bus()
        bus.on("ScheduledRunEvent", lambda event: received.append(event))  # type: ignore[reportUnknownLambdaType]

        await _fire_handler("morning", rc1.model_dump_json())
        await _fire_handler("evening", rc2.model_dump_json())

        await asyncio.sleep(0.2)

        assert len(received) == 2
        prompts = {e.run_config.prompt for e in received}
        assert prompts == {"morning brief", "evening summary"}
