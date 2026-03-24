# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for TelegramRunEvent, TokenBucketRateLimiter, and DraftStreamer."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import UTC, datetime
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


# ─── TelegramRunEvent ────────────────────────────────────────────────────────


class TestTelegramRunEvent:
    """TelegramRunEvent model serialization and structure."""

    def test_round_trip_serialization(self) -> None:
        """TelegramRunEvent serializes to JSON and back without data loss."""
        from rai_agent.daemon.telegram import TelegramRunEvent

        rc = RunConfig(prompt="check jira")
        now = datetime.now(tz=UTC)
        event = TelegramRunEvent(
            chat_id=12345,
            user_id=67890,
            message_text="check jira",
            run_config=rc,
            timestamp=now,
        )
        data = event.model_dump(mode="json")
        restored = TelegramRunEvent.model_validate(data)
        assert restored.chat_id == 12345
        assert restored.user_id == 67890
        assert restored.message_text == "check jira"
        assert restored.run_config.prompt == "check jira"
        assert restored.timestamp == now

    def test_required_fields(self) -> None:
        """TelegramRunEvent requires all fields."""
        import pydantic

        from rai_agent.daemon.telegram import TelegramRunEvent

        with pytest.raises(pydantic.ValidationError):
            TelegramRunEvent()  # type: ignore[call-arg]

    def test_has_event_type(self) -> None:
        """TelegramRunEvent has an event_type compatible with bubus EventBus."""
        from rai_agent.daemon.telegram import TelegramRunEvent

        rc = RunConfig(prompt="test")
        event = TelegramRunEvent(
            chat_id=1,
            user_id=2,
            message_text="test",
            run_config=rc,
            timestamp=datetime.now(tz=UTC),
        )
        assert event.event_type == "TelegramRunEvent"


# ─── TokenBucketRateLimiter ──────────────────────────────────────────────────


class TestTokenBucketRateLimiter:
    """Token bucket rate limiter behavior."""

    def test_allows_within_burst_limit(self) -> None:
        """Allows requests up to max_tokens burst."""
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate=0.0)
        assert limiter.allow(1) is True
        assert limiter.allow(1) is True
        assert limiter.allow(1) is True

    def test_rejects_after_burst_exhaustion(self) -> None:
        """Rejects after all burst tokens consumed."""
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(max_tokens=2, refill_rate=0.0)
        assert limiter.allow(1) is True
        assert limiter.allow(1) is True
        assert limiter.allow(1) is False

    def test_refills_over_time(self) -> None:
        """Tokens refill based on elapsed time and refill_rate."""
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        # 1 token max, refill at 100 tokens/sec (fast for testing)
        limiter = TokenBucketRateLimiter(max_tokens=1, refill_rate=100.0)
        assert limiter.allow(1) is True
        assert limiter.allow(1) is False
        # Wait just a tiny bit — 100 tokens/sec means 0.01s = 1 token
        time.sleep(0.02)
        assert limiter.allow(1) is True

    def test_independent_per_user(self) -> None:
        """Each user has an independent token bucket."""
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(max_tokens=1, refill_rate=0.0)
        assert limiter.allow(1) is True
        assert limiter.allow(1) is False
        # Different user still has tokens
        assert limiter.allow(2) is True


# ─── DraftStreamer ────────────────────────────────────────────────────────────


class TestDraftStreamer:
    """DraftStreamer shows status via drafts, sends final response as message."""

    def _make_bot(self) -> AsyncMock:
        """Create a mock Bot with send_message and send_message_draft."""
        bot = AsyncMock()
        sent_msg = MagicMock()
        sent_msg.message_id = 42
        bot.send_message.return_value = sent_msg
        bot.send_message_draft.return_value = True
        return bot

    async def test_set_status_sends_draft(self) -> None:
        """set_status sends an ephemeral draft via send_message_draft."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        await streamer.set_status("\U0001f9e0 Thinking...")
        bot.send_message_draft.assert_called_once_with(
            chat_id=100, draft_id=streamer._draft_id,
            text="\U0001f9e0 Thinking...",
        )

    async def test_set_status_throttled(self) -> None:
        """Rapid set_status calls are throttled."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        await streamer.set_status("status 1")
        await streamer.set_status("status 2")
        await streamer.set_status("status 3")
        bot.send_message_draft.assert_called_once()

    async def test_set_status_allows_after_interval(self) -> None:
        """After throttle interval, another status draft is sent."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.01)
        await streamer.set_status("status 1")
        await asyncio.sleep(0.02)
        await streamer.set_status("status 2")
        assert bot.send_message_draft.call_count == 2

    async def test_append_does_not_send_draft(self) -> None:
        """append() accumulates text silently — no draft sent."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        await streamer.append("hello")
        await streamer.append(" world")
        bot.send_message_draft.assert_not_called()

    async def test_flush_sends_final_content(self) -> None:
        """flush() sends complete buffered content via send_message with entities."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        await streamer.append("hello ")
        await streamer.append("world")
        await streamer.flush()
        call_kwargs = bot.send_message.call_args
        assert call_kwargs is not None
        args, kwargs = call_kwargs
        assert args[0] == 100  # chat_id
        assert args[1] == "hello world"  # text
        assert "parse_mode" not in kwargs
        assert "entities" in kwargs

    async def test_flush_noop_when_empty(self) -> None:
        """flush() does nothing when buffer is empty."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        await streamer.flush()
        bot.send_message.assert_not_called()

    async def test_buffer_accumulates_full_content(self) -> None:
        """Buffer accumulates all content without truncation (RAI-34)."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        await streamer.append("hello ")
        await streamer.append("world!!")
        await streamer.flush()
        all_calls = bot.send_message.call_args_list
        all_text = " ".join(str(c[0][1]) for c in all_calls if c[0])
        assert "hello" in all_text
        assert "world" in all_text

    async def test_flush_splits_long_message(self) -> None:
        """flush() splits long content into multiple send_message calls (RAI-34)."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        long_text = "\n\n".join(f"Paragraph {i}: " + "X" * 200 for i in range(30))
        await streamer.append(long_text)
        await streamer.flush()
        assert bot.send_message.call_count >= 2

    async def test_draft_id_generated_at_construction(self) -> None:
        """DraftStreamer generates an int draft_id > 0 at construction."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        assert isinstance(streamer._draft_id, int)
        assert streamer._draft_id > 0

    async def test_no_message_thread_id_in_draft_calls(self) -> None:
        """send_message_draft calls must NOT include message_thread_id."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        await streamer.set_status("working")
        call_kwargs = bot.send_message_draft.call_args
        assert call_kwargs is not None
        _, kwargs = call_kwargs
        assert "message_thread_id" not in kwargs

    async def test_final_flush_uses_entities(self) -> None:
        """flush() converts Markdown and sends with entities, no parse_mode."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        await streamer.append("**bold text**")
        await streamer.flush()
        call_kwargs = bot.send_message.call_args
        assert call_kwargs is not None
        _, kwargs = call_kwargs
        assert "parse_mode" not in kwargs
        assert "entities" in kwargs
        assert kwargs["entities"] is not None

    async def test_intermediate_draft_no_entities(self) -> None:
        """Non-final drafts send plain text without entities or parse_mode."""
        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=0.0)
        await streamer.set_status("working...")
        # set_status → send_message_draft (plain, no entities)
        call_kwargs = bot.send_message_draft.call_args
        assert call_kwargs is not None
        _, kwargs = call_kwargs
        assert "entities" not in kwargs
        assert "parse_mode" not in kwargs

    async def test_flush_fallback_on_convert_error(self) -> None:
        """If conversion fails, flush sends plain text via send_message."""
        from unittest.mock import patch

        from rai_agent.daemon.telegram import DraftStreamer

        bot = self._make_bot()
        streamer = DraftStreamer(bot=bot, chat_id=100, throttle_s=10.0)
        await streamer.append("**bold**")
        with patch(
            "rai_agent.daemon.telegram.telegramify_markdown_convert",
            side_effect=ValueError("boom"),
        ):
            await streamer.flush()
        call_kwargs = bot.send_message.call_args
        assert call_kwargs is not None
        args, kwargs = call_kwargs
        # Should send raw buffer as plain text
        assert args[0] == 100  # chat_id
        assert args[1] == "**bold**"  # text
        assert kwargs.get("entities") is None


# ─── split_for_telegram ─────────────────────────────────────────────────────


class TestSplitForTelegram:
    """split_for_telegram converts markdown and splits into ≤4096 UTF-16 chunks."""

    def test_short_text_returns_single_chunk(self) -> None:
        """Short text produces a single chunk with entities."""
        from rai_agent.daemon.telegram import split_for_telegram

        chunks = split_for_telegram("Hello **world**")
        assert len(chunks) == 1
        text, entities = chunks[0]
        assert "world" in text
        assert entities is not None
        assert len(entities) > 0

    def test_long_text_returns_multiple_chunks(self) -> None:
        """Text exceeding 4096 UTF-16 code units is split into multiple chunks."""
        from rai_agent.daemon.telegram import split_for_telegram

        # Build a markdown string well over 4096 chars
        long_md = "\n\n".join(
            f"Paragraph {i}: " + "A" * 200 for i in range(30)
        )
        assert len(long_md) > 5000
        chunks = split_for_telegram(long_md)
        assert len(chunks) >= 2
        # Each chunk text must be ≤4096 UTF-16 code units
        for chunk_text, _ in chunks:
            utf16_len = len(chunk_text.encode("utf-16-le")) // 2
            assert utf16_len <= 4096, f"Chunk too long: {utf16_len}"

    def test_all_content_preserved(self) -> None:
        """Concatenating chunk texts reproduces the full content (no data loss)."""
        from rai_agent.daemon.telegram import split_for_telegram

        long_md = "\n\n".join(f"Section {i}: " + "B" * 300 for i in range(25))
        chunks = split_for_telegram(long_md)
        reassembled = "".join(text for text, _ in chunks)
        # All original section markers must be present
        for i in range(25):
            assert f"Section {i}" in reassembled

    def test_fallback_on_conversion_error(self) -> None:
        """When markdown conversion fails, returns single plain-text chunk."""
        from unittest.mock import patch

        from rai_agent.daemon.telegram import split_for_telegram

        with patch(
            "rai_agent.daemon.telegram.telegramify_markdown_convert",
            side_effect=ValueError("boom"),
        ):
            chunks = split_for_telegram("some **text**")
        assert len(chunks) == 1
        text, entities = chunks[0]
        assert text == "some **text**"
        assert entities is None


# ─── Table pipeline integration ──────────────────────────────────────────────


class TestTablePipelineIntegration:
    """Verify table transformation is wired into conversion pipeline."""

    _WIDE_TABLE = (
        "| Epic | Stories | Status | Notes |\n"
        "|------|---------|--------|-------|\n"
        "| E7 Telegram UX | 3 | Complete | sendMessageDraft + keepalive |"
    )

    def test_convert_for_telegram_transforms_tables(self) -> None:
        """convert_for_telegram transforms wide tables before entity conversion."""
        from rai_agent.daemon.telegram import convert_for_telegram

        text, _entities = convert_for_telegram(self._WIDE_TABLE)
        # Raw table pipes should not appear in output
        assert "| Epic |" not in text
        # Key-value format should be present (bold rendered as entity, text remains)
        assert "Epic:" in text

    def test_split_for_telegram_transforms_tables(self) -> None:
        """split_for_telegram transforms wide tables before splitting."""
        from rai_agent.daemon.telegram import split_for_telegram

        chunks = split_for_telegram(self._WIDE_TABLE)
        all_text = "".join(text for text, _ in chunks)
        assert "| Epic |" not in all_text
        assert "Epic:" in all_text


# ─── TelegramTrigger wiring ─────────────────────────────────────────────────


class TestTelegramTriggerWiring:
    """Verify pipeline order and filter change."""

    def test_pipeline_includes_command_middleware(self) -> None:
        """Pipeline has 5 middlewares: auth, rate, coalesce, cmd, dispatch."""
        from unittest.mock import AsyncMock

        from rai_agent.daemon.telegram import TelegramTrigger

        dispatcher = AsyncMock()
        registry = AsyncMock()
        handler = AsyncMock()

        trigger = TelegramTrigger(
            bot_token="fake:token",
            allowed_users={1},
            dispatcher=dispatcher,
            registry=registry,
            handler=handler,
            cwd="/tmp",
        )

        assert len(trigger._pipeline) == 5  # noqa: SLF001

    def test_filter_includes_commands(self) -> None:
        """PTB handler filter accepts command messages like /sessions."""
        from unittest.mock import AsyncMock

        from telegram.ext import filters  # type: ignore[import-untyped]

        from rai_agent.daemon.telegram import TelegramTrigger

        dispatcher = AsyncMock()
        registry = AsyncMock()
        handler = AsyncMock()

        trigger = TelegramTrigger(
            bot_token="fake:token",
            allowed_users={1},
            dispatcher=dispatcher,
            registry=registry,
            handler=handler,
            cwd="/tmp",
        )

        # The handler's filters should accept TEXT (including commands)
        handlers = trigger._app.handlers  # noqa: SLF001
        # PTB stores handlers in a dict of group -> list
        assert 0 in handlers
        msg_handler = handlers[0][0]
        # The filter should be filters.TEXT (not TEXT & ~COMMAND)
        assert msg_handler.filters == filters.TEXT

    async def test_existing_new_command_still_works(self) -> None:
        """The /new command passes through session command middleware.

        /new is not a /session subcommand — it passes through to
        the next middleware in the pipeline.
        """
        from rai_agent.daemon.middleware import (
            MessageContext,
            make_session_command_middleware,
        )

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        next_called: list[bool] = []

        async def track_next() -> None:
            next_called.append(True)

        async def mock_reply(text: str) -> None:
            pass

        ctx = MessageContext(
            session_key="telegram:default:dm:123",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            user_id=1,
            prompt="/new",
            reply_text=mock_reply,
        )
        await mw(ctx, track_next)
        assert next_called == [True]


# ─── extract_status_from_frame ──────────────────────────────────────────────


class TestExtractStatusFromFrame:
    """Tests for extract_status_from_frame."""

    def test_tool_use_read(self) -> None:
        """Returns status for Read tool with filename."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({
            "event": "assistant_message",
            "payload": {"content": [
                {"id": "t1", "name": "Read",
                 "input": {"file_path": "/home/user/src/foo.py"}},
            ]},
        })
        result = extract_status_from_frame(frame)
        assert result is not None
        assert "Reading" in result
        assert "foo.py" in result

    def test_tool_use_bash(self) -> None:
        """Returns status for Bash tool with command preview."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({
            "event": "assistant_message",
            "payload": {"content": [
                {"id": "t2", "name": "Bash",
                 "input": {"command": "uv run pytest"}},
            ]},
        })
        result = extract_status_from_frame(frame)
        assert result is not None
        assert "Running command" in result
        assert "pytest" in result

    def test_thinking_block(self) -> None:
        """Returns thinking status for thinking blocks."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({
            "event": "assistant_message",
            "payload": {"content": [
                {"thinking": "Let me analyze...", "signature": "sig"},
            ]},
        })
        result = extract_status_from_frame(frame)
        assert result is not None
        assert "Thinking" in result

    def test_text_block_returns_none(self) -> None:
        """Returns None for text blocks (handled by extract_text_from_frame)."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({
            "event": "assistant_message",
            "payload": {"content": [
                {"text": "Here is the answer"},
            ]},
        })
        assert extract_status_from_frame(frame) is None

    def test_unknown_tool(self) -> None:
        """Returns generic status for unknown tools."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({
            "event": "assistant_message",
            "payload": {"content": [
                {"id": "t3", "name": "CustomTool", "input": {}},
            ]},
        })
        result = extract_status_from_frame(frame)
        assert result is not None
        assert "CustomTool" in result

    def test_non_assistant_event_returns_none(self) -> None:
        """Returns None for non-assistant_message events."""
        from rai_agent.daemon.telegram_pipeline import extract_status_from_frame

        frame = json.dumps({"event": "user_message", "payload": {}})
        assert extract_status_from_frame(frame) is None


# ─── transform_tables_for_telegram ──────────────────────────────────────────


class TestTransformTablesForTelegram:
    """Pre-process markdown tables for Telegram mobile display."""

    def test_narrow_table_unchanged(self) -> None:
        """Table with short rows (<=35 chars) passes through as-is."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = "| Name | Size |\n|------|------|\n| S7.1 | M    |\n| S7.2 | S    |"
        result = transform_tables_for_telegram(md)
        assert result == md

    def test_wide_table_transforms_to_key_value(self) -> None:
        """Table with rows >35 chars becomes bold key-value format."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = (
            "| Epic | Stories | Status | Notes |\n"
            "|------|---------|--------|-------|\n"
            "| E7 Telegram UX | 3 | Complete | sendMessageDraft + keepalive |\n"
            "| E8 ECC Analysis | 1/3 | In Progress | Subsystem mapping done |"
        )
        result = transform_tables_for_telegram(md)
        assert "| Epic |" not in result
        assert "**Epic:** E7 Telegram UX" in result
        assert "**Stories:** 3" in result
        assert "**Status:** Complete" in result
        assert "**Notes:** sendMessageDraft + keepalive" in result
        assert "**Epic:** E8 ECC Analysis" in result
        assert "**Notes:** Subsystem mapping done" in result
        # Rows separated by blank line
        assert "\n\n" in result

    def test_mixed_content_only_transforms_tables(self) -> None:
        """Surrounding text preserved, only wide table changed."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = (
            "Here is the summary:\n\n"
            "| Epic | Stories | Status | Notes |\n"
            "|------|---------|--------|-------|\n"
            "| E7   | 3       | Done   | shipped |\n\n"
            "And here is more text."
        )
        result = transform_tables_for_telegram(md)
        assert result.startswith("Here is the summary:")
        assert result.endswith("And here is more text.")
        assert "**Epic:** E7" in result

    def test_no_table_unchanged(self) -> None:
        """Plain markdown without tables returns identical."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = "# Hello\n\nSome **bold** text and a [link](url)."
        result = transform_tables_for_telegram(md)
        assert result == md

    def test_multiple_tables(self) -> None:
        """Two tables: narrow unchanged, wide transformed."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        narrow = "| A | B |\n|---|---|\n| 1 | 2 |"
        wide = (
            "| Column One | Column Two | Column Three | Column Four |\n"
            "|------------|------------|--------------|-------------|\n"
            "| value one  | value two  | value three  | value four  |"
        )
        md = f"Before\n\n{narrow}\n\nMiddle\n\n{wide}\n\nAfter"
        result = transform_tables_for_telegram(md)
        # Narrow table preserved
        assert "| A | B |" in result
        # Wide table transformed
        assert "**Column One:** value one" in result
        assert "**Column Four:** value four" in result

    def test_empty_cells(self) -> None:
        """Table with empty cells handled gracefully."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = (
            "| Name | Description | Category | Priority | Owner |\n"
            "|------|-------------|----------|----------|-------|\n"
            "| Task1 |  | Bug | High |  |"
        )
        result = transform_tables_for_telegram(md)
        assert "**Name:** Task1" in result
        assert "**Category:** Bug" in result
        assert "**Priority:** High" in result

    def test_single_row_wide_table(self) -> None:
        """Header + one data row transforms correctly."""
        from rai_agent.daemon.telegram import transform_tables_for_telegram

        md = (
            "| Epic | Stories | Status | Notes |\n"
            "|------|---------|--------|-------|\n"
            "| E7 Telegram UX | 3 | Complete | sendMessageDraft + keepalive |"
        )
        result = transform_tables_for_telegram(md)
        assert "**Epic:** E7 Telegram UX" in result
        assert "**Notes:** sendMessageDraft + keepalive" in result
        # Should NOT have double blank lines (only one row)
        assert "\n\n\n" not in result
