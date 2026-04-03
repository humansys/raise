# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for BriefingJob, BriefingPipeline, and BRIEFING_PROMPT_TEMPLATE."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


# ─── BriefingJob ────────────────────────────────────────────────────────────


class TestBriefingJob:
    """BriefingJob builds a RunConfig for the daily briefing pipeline."""

    def test_creates_run_config_with_default_prompt(self) -> None:
        """BriefingJob.build_run_config() uses BRIEFING_PROMPT_TEMPLATE."""
        from rai_agent.daemon.briefing import (
            BRIEFING_PROMPT_TEMPLATE,
            BriefingJob,
        )

        job = BriefingJob(
            chat_id=12345,
        )
        config = job.build_run_config()
        assert config.prompt == BRIEFING_PROMPT_TEMPLATE

    def test_creates_run_config_with_bypass_permissions(self) -> None:
        """BriefingJob sets permission_mode to bypassPermissions."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(chat_id=1)
        config = job.build_run_config()
        assert config.permission_mode == "bypassPermissions"

    def test_creates_run_config_with_max_turns_20(self) -> None:
        """BriefingJob sets max_turns=20."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(chat_id=1)
        config = job.build_run_config()
        assert config.max_turns == 20

    def test_stores_chat_id(self) -> None:
        """BriefingJob stores chat_id for use by BriefingPipeline."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(chat_id=99999)
        assert job.chat_id == 99999

    def test_custom_prompt_overrides_default(self) -> None:
        """Custom prompt_template overrides BRIEFING_PROMPT_TEMPLATE (AC6)."""
        from rai_agent.daemon.briefing import BriefingJob

        custom = "Give me a haiku about the day."
        job = BriefingJob(
            chat_id=1,
            prompt_template=custom,
        )
        config = job.build_run_config()
        assert config.prompt == custom

    def test_skills_passed_to_run_config(self) -> None:
        """Skills are forwarded to RunConfig."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(
            chat_id=1,
            skills=["daily-briefing"],
        )
        config = job.build_run_config()
        assert config.skills == ["daily-briefing"]

    def test_memory_paths_passed_to_run_config(self) -> None:
        """Memory paths are forwarded to RunConfig."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(
            chat_id=1,
            memory_paths=["CLAUDE.md"],
        )
        config = job.build_run_config()
        assert config.memory_paths == ["CLAUDE.md"]

    def test_default_skills_and_memory_are_none(self) -> None:
        """Without explicit skills/memory, RunConfig fields are None."""
        from rai_agent.daemon.briefing import BriefingJob

        job = BriefingJob(chat_id=1)
        config = job.build_run_config()
        assert config.skills is None
        assert config.memory_paths is None


# ─── BriefingPipeline ──────────────────────────────────────────────────────


def _make_mock_bot() -> AsyncMock:
    """Create a mock Telegram Bot."""
    bot = AsyncMock()
    sent_msg = MagicMock()
    sent_msg.message_id = 42
    bot.send_message.return_value = sent_msg
    return bot


def _make_mock_runtime() -> AsyncMock:
    """Create a mock RaiAgentRuntime."""
    runtime = AsyncMock()
    runtime.run = AsyncMock(return_value="session-abc")
    return runtime


class TestBriefingPipeline:
    """BriefingPipeline subscribes to ScheduledRunEvent and dispatches runs."""

    def test_subscribe_registers_handler_on_event_bus(self) -> None:
        """subscribe() registers a handler for ScheduledRunEvent on EventBus."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.events import get_bus

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        bus = get_bus()
        pipeline.subscribe()

        # Verify handler is registered by checking bus internals
        # bubus 1.6.x stores handlers as dict[event_name, list[callable]]
        assert "ScheduledRunEvent" in bus.handlers

    async def test_handles_matching_job_id(self) -> None:
        """Pipeline calls runtime.run() when event.job_id matches."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.runtime import RunConfig

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        # Emit a matching event
        rc = RunConfig(prompt="test briefing")
        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        # Give async handler time to execute
        await asyncio.sleep(0.2)

        runtime.run.assert_called_once()
        call_args = runtime.run.call_args
        assert call_args[0][0].prompt == "test briefing"

    async def test_ignores_non_matching_job_id(self) -> None:
        """Pipeline ignores events with different job_id."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.runtime import RunConfig

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        # Emit a non-matching event
        rc = RunConfig(prompt="other job")
        event = ScheduledRunEvent(
            job_id="weekly-report",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        await asyncio.sleep(0.2)

        runtime.run.assert_not_called()

    async def test_creates_draft_streamer_per_run(self) -> None:
        """Pipeline creates a fresh DraftStreamer and flushes after run."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.runtime import RunConfig

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        rc = RunConfig(prompt="test briefing")
        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)

        await asyncio.sleep(0.2)

        # runtime.run was called with a callable (streamer.append)
        runtime.run.assert_called_once()
        call_args = runtime.run.call_args
        send_fn = call_args[0][1]
        # send_fn should be callable
        assert callable(send_fn)

    async def test_logs_error_on_runtime_exception(self) -> None:
        """Pipeline logs error on runtime exception without crashing (AC7)."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.runtime import RunConfig

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(side_effect=RuntimeError("SDK exploded"))
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        rc = RunConfig(prompt="test briefing")
        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        # Should not raise
        get_bus().emit(event)
        await asyncio.sleep(0.2)

        # Pipeline should have handled the error gracefully
        runtime.run.assert_called_once()

    async def test_sends_error_notification_on_failure(self) -> None:
        """Pipeline sends error message to Telegram on runtime failure."""
        from rai_agent.daemon.briefing import BriefingPipeline
        from rai_agent.daemon.cron import ScheduledRunEvent
        from rai_agent.daemon.events import get_bus
        from rai_agent.daemon.runtime import RunConfig

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(side_effect=RuntimeError("SDK exploded"))
        bot = _make_mock_bot()
        pipeline = BriefingPipeline(
            runtime=runtime,
            bot=bot,
            job_id="daily-briefing",
            chat_id=12345,
        )
        pipeline.subscribe()

        rc = RunConfig(prompt="test briefing")
        event = ScheduledRunEvent(
            job_id="daily-briefing",
            run_config=rc,
            scheduled_at=datetime.now(tz=UTC),
        )
        get_bus().emit(event)
        await asyncio.sleep(0.2)

        # Should have sent error notification to chat
        bot.send_message.assert_called_once_with(
            12345,
            "⚠ Briefing failed. Check logs for details.",
        )
