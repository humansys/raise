"""Daily briefing pipeline for the Rai daemon.

BriefingJob builds a RunConfig for the daily briefing use case.
BriefingPipeline subscribes to ScheduledRunEvent and dispatches runs
through ClaudeRuntime, streaming output via DraftStreamer to Telegram.

Design decisions (S2.7):
  D1: Single module for all wiring — follows cron.py/telegram.py flat pattern
  D2: Pipeline subscriber filters by job_id — allows multiple cron jobs
  D3: RunConfig with bypassPermissions + max_turns=20 — trusted cron, cost guard
  D4: Prompt template as module constant — overridable via constructor
  D5: Error handling — log and fail fast (no retry)
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from rai_agent.daemon.events import get_bus
from rai_agent.daemon.runtime import RunConfig
from rai_agent.daemon.telegram import DraftStreamer
from rai_agent.daemon.telegram_pipeline import extract_text_from_frame

if TYPE_CHECKING:
    from telegram import Bot  # type: ignore[import-untyped]

    from rai_agent.daemon.cron import ScheduledRunEvent
    from rai_agent.daemon.runtime import RaiAgentRuntime

_log = logging.getLogger(__name__)

# ─── Prompt Template ─────────────────────────────────────────────────────────

BRIEFING_PROMPT_TEMPLATE = """\
You are Rai, an autonomous agent executing a daily briefing.

Query the following sources and produce a structured briefing:

1. **Jira** — Open and in-progress issues assigned to me. Summarize by priority.
2. **Gmail** — Unread priority emails. Summarize sender and subject.
3. **Google Calendar** — Today's events. List time, title, and attendees.

Format the briefing as:
## Daily Briefing

### Jira
- [priority] ISSUE-KEY: summary (status)

### Email
- From: sender — Subject: subject

### Calendar
- HH:MM — Event title (attendees)

### Notes
- Any blockers, deadlines, or items needing attention.

If a source is unavailable, note it and continue with the others.\
"""


# ─── BriefingJob ─────────────────────────────────────────────────────────────


class BriefingJob:
    """Builds a RunConfig for the daily briefing pipeline.

    Encapsulates briefing-specific configuration: prompt template,
    skills, memory paths, and Telegram chat_id.
    """

    def __init__(
        self,
        *,
        chat_id: int,
        prompt_template: str | None = None,
        skills: list[str] | None = None,
        memory_paths: list[str] | None = None,
    ) -> None:
        self.chat_id = chat_id
        self._prompt_template = prompt_template or BRIEFING_PROMPT_TEMPLATE
        self._skills = skills
        self._memory_paths = memory_paths

    def build_run_config(self) -> RunConfig:
        """Build a RunConfig for the daily briefing."""
        return RunConfig(
            prompt=self._prompt_template,
            permission_mode="bypassPermissions",
            max_turns=20,
            skills=self._skills,
            memory_paths=self._memory_paths,
        )


# ─── BriefingPipeline ───────────────────────────────────────────────────────


class BriefingPipeline:
    """Subscribes to ScheduledRunEvent and dispatches briefing runs.

    On matching event: creates a fresh DraftStreamer, calls runtime.run(),
    then flushes the streamer. Errors are logged, not retried.
    """

    def __init__(
        self,
        *,
        runtime: RaiAgentRuntime,
        bot: Bot,
        job_id: str,
        chat_id: int,
    ) -> None:
        self._runtime = runtime
        self._bot = bot
        self._job_id = job_id
        self._chat_id = chat_id

    def subscribe(self) -> None:
        """Register handler on EventBus for ScheduledRunEvent."""
        bus = get_bus()
        bus.on("ScheduledRunEvent", self._handle_event)

    def _handle_event(self, event: ScheduledRunEvent) -> None:
        """Sync callback for EventBus — schedules async handler."""
        if event.job_id != self._job_id:
            return
        task = asyncio.create_task(self._handle_async(event))
        task.add_done_callback(self._task_done)

    @staticmethod
    def _task_done(task: asyncio.Task[None]) -> None:
        """Suppress 'Task exception was never retrieved' warnings."""
        if not task.cancelled():
            task.exception()  # retrieves (and discards) the exception

    async def _handle_async(self, event: ScheduledRunEvent) -> None:
        """Async handler: create DraftStreamer, run, flush."""
        streamer = DraftStreamer(
            bot=self._bot,
            chat_id=self._chat_id,
        )

        async def _text_only(frame_json: str) -> None:
            text = extract_text_from_frame(frame_json)
            if text:
                await streamer.append(text)

        try:
            await self._runtime.run(event.run_config, _text_only)
            await streamer.flush()
        except Exception:
            _log.exception(
                "briefing_run_error",
                extra={
                    "job_id": self._job_id,
                    "chat_id": self._chat_id,
                },
            )
            try:
                await self._bot.send_message(
                    self._chat_id,
                    "⚠ Briefing failed. Check logs for details.",
                )
            except Exception:
                _log.exception("briefing_error_notification_failed")
