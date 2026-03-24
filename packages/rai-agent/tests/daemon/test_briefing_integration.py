# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""E2E integration test for the daily briefing pipeline.

Real infrastructure: EventBus, CronTrigger (in-memory SQLite), GovernanceHooks,
PromptAssembler. Mocked externals: Telegram Bot, Claude SDK.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from rai_agent.daemon.runtime import RunConfig


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


def _make_mock_bot() -> AsyncMock:
    """Create a mock Telegram Bot with send_message and send_message_draft."""
    bot = AsyncMock()
    sent_msg = MagicMock()
    sent_msg.message_id = 42
    bot.send_message.return_value = sent_msg
    bot.send_message_draft.return_value = True
    return bot


class TestBriefingE2E:
    """Full pipeline: EventBus -> BriefingPipeline -> runtime -> DraftStreamer."""

    async def test_event_triggers_full_pipeline(self) -> None:
        """EventBus -> BriefingPipeline -> runtime.run() -> DraftStreamer.

        Uses real EventBus, real GovernanceHooks/PromptAssembler.
        Mocks: Telegram Bot, ClaudeRuntime.
        """
        from datetime import UTC, datetime

        from rai_agent.daemon.briefing import (
            BRIEFING_PROMPT_TEMPLATE,
            BriefingJob,
            BriefingPipeline,
        )
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus

        # Real components
        bot = _make_mock_bot()
        runtime = AsyncMock()
        runtime.run = AsyncMock(return_value="session-e2e-001")

        # BriefingJob creates RunConfig
        job = BriefingJob(
            chat_id=12345,
        )
        config = job.build_run_config()

        # Pipeline subscribes to EventBus
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        # Simulate cron fire -> ScheduledRunEvent
        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=config,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        # Wait for async handler
        await asyncio.sleep(0.3)

        # Assert runtime.run() was called with correct RunConfig
        runtime.run.assert_called_once()
        call_args = runtime.run.call_args
        received_config = call_args[0][0]
        assert received_config.prompt == BRIEFING_PROMPT_TEMPLATE
        assert received_config.permission_mode == "bypassPermissions"
        assert received_config.max_turns == 20

        # Assert send callable was passed (DraftStreamer.append)
        send_fn = call_args[0][1]
        assert callable(send_fn)

    async def test_cron_trigger_fires_event_to_pipeline(self) -> None:
        """CronTrigger fires -> _fire_handler -> EventBus -> BriefingPipeline.

        Uses real CronTrigger (in-memory SQLite), real EventBus.
        Simulates APScheduler fire via _fire_handler direct call.
        """
        from rai_agent.daemon.briefing import BriefingJob, BriefingPipeline
        from rai_agent.daemon.cron import CronTrigger, _fire_handler

        bot = _make_mock_bot()
        runtime = AsyncMock()
        runtime.run = AsyncMock(return_value="session-cron-001")

        # Setup BriefingJob
        job = BriefingJob(
            chat_id=12345,
        )
        config = job.build_run_config()

        # Setup CronTrigger (real, in-memory SQLite)
        trigger = CronTrigger(db_url="sqlite+aiosqlite://")
        await trigger.start()
        try:
            await trigger.add_job(
                "daily-briefing", "0 8 * * *", config
            )

            # Subscribe pipeline
            pipeline = BriefingPipeline(
                runtime=runtime,
                bot=bot,
                job_id="daily-briefing",
                chat_id=12345,
            )
            pipeline.subscribe()

            # Simulate APScheduler calling _fire_handler
            await _fire_handler(
                "daily-briefing", config.model_dump_json()
            )

            await asyncio.sleep(0.3)

            # Assert runtime was called
            runtime.run.assert_called_once()
            call_config = runtime.run.call_args[0][0]
            assert call_config.prompt == config.prompt
            assert call_config.max_turns == 20
        finally:
            await trigger.stop()

    async def test_streamer_receives_output_from_runtime(self) -> None:
        """Runtime streams output -> _text_only filter -> DraftStreamer -> bot.

        Verifies the send callback wired by the pipeline extracts text
        from EventFrame JSON and reaches the Telegram Bot mock.
        """
        import json
        from datetime import UTC, datetime

        from rai_agent.daemon.briefing import BriefingJob, BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus

        bot = _make_mock_bot()

        # Runtime that calls the send function with EventFrame JSON
        # (matching what ClaudeRuntime._stream actually produces)
        async def fake_run(
            config: RunConfig,
            send: Any,
        ) -> str | None:
            frame = json.dumps({
                "type": "event",
                "event": "assistant_message",
                "payload": {
                    "content": [
                        {"text": "## Daily Briefing\n\nHere are your tasks..."}
                    ]
                },
                "seq": 0,
            })
            await send(frame)
            return "session-stream-001"

        runtime = AsyncMock()
        runtime.run = AsyncMock(side_effect=fake_run)

        job = BriefingJob(
            chat_id=12345,
        )
        config = job.build_run_config()

        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=config,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        await asyncio.sleep(0.3)

        # DraftStreamer accumulates text silently (no draft for text),
        # then flush sends the final message via send_message
        bot.send_message.assert_called_once()
        call_args = bot.send_message.call_args
        assert call_args[0][0] == 12345  # chat_id

    async def test_pipeline_with_real_governance(self) -> None:
        """Pipeline works with real GovernanceHooks and PromptAssembler.

        Verifies that GovernanceHooks (bypassPermissions) and
        PromptAssembler can be constructed alongside the pipeline
        without errors.
        """
        from datetime import UTC, datetime

        from rai_agent.daemon.briefing import BriefingJob, BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.governance import (
            GovernanceHooks,
            PromptAssembler,
        )

        bot = _make_mock_bot()
        runtime = AsyncMock()
        runtime.run = AsyncMock(return_value="session-gov-001")

        # Real governance components (as they would be in production)
        governance = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="bypassPermissions",
            max_turns=20,
        )
        assembler = PromptAssembler(project_root="/tmp")

        # Verify they construct without error
        assert governance is not None
        assert assembler is not None

        job = BriefingJob(
            chat_id=12345,
        )
        config = job.build_run_config()

        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=config,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        await asyncio.sleep(0.3)

        runtime.run.assert_called_once()

    async def test_multiple_events_only_matching_handled(self) -> None:
        """Multiple events with different job_ids — only matching one handled."""
        from datetime import UTC, datetime

        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus

        bot = _make_mock_bot()
        runtime = AsyncMock()
        runtime.run = AsyncMock(return_value="session-multi-001")

        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        now = datetime.now(tz=UTC)

        # Emit non-matching event
        event1 = ScheduledRunEvent(
            job_id="weekly-report",
            run_config=RunConfig(prompt="weekly"),
            scheduled_at=now,
        )
        get_bus().emit(event1)

        # Emit matching event
        event2 = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=RunConfig(prompt="daily"),
            scheduled_at=now,
        )
        get_bus().emit(event2)

        # Emit another non-matching event
        event3 = ScheduledRunEvent(
            job_id="health-check",
            run_config=RunConfig(prompt="health"),
            scheduled_at=now,
        )
        get_bus().emit(event3)

        await asyncio.sleep(0.3)

        # Only the matching event should have triggered runtime.run()
        runtime.run.assert_called_once()
        call_config = runtime.run.call_args[0][0]
        assert call_config.prompt == "daily"
