"""Telegram bot trigger for the Rai daemon.

TelegramRunEvent is emitted on the EventBus when an authorized user sends a message.
DraftStreamer uses send_message_draft for streaming and send_message for finalization.
TelegramTrigger wraps python-telegram-bot (PTB) and satisfies RaiTrigger.

Design decisions (S2.5):
  D1: python-telegram-bot v20+ — async-native, well-typed
  D2: Flat daemon/telegram.py — follows cron.py pattern (YAGNI)
  D3: TelegramRunEvent extends bubus.BaseEvent — parallels ScheduledRunEvent
  D4: Middleware as early returns in handler — simple, PTB-idiomatic
  D5: DraftStreamer with asyncio.Lock + monotonic throttle
  D6: Token bucket rate limiter — simple, allows bursts
  D7: Config via constructor args — testable, no env coupling
  D8: Polling mode only — simple, sufficient for personal use
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Any

from telegram.ext import (  # type: ignore[import-untyped]
    Application,
    MessageHandler,
    filters,
)
from telegramify_markdown import (
    convert as telegramify_markdown_convert,  # type: ignore[import-untyped]  # pyright: ignore[reportUnknownVariableType]
)
from telegramify_markdown import (
    split_entities as telegramify_split_entities,  # type: ignore[import-untyped]  # pyright: ignore[reportUnknownVariableType]
)

from rai_agent.daemon.events import BaseEvent
from rai_agent.daemon.image import (
    SUPPORTED_MIMES,
    build_image_content_blocks,
    validate_image,
)
from rai_agent.daemon.middleware import (
    CoalescingConfig,
    MessageContext,
    compose,
)
from rai_agent.daemon.runtime import RunConfig  # noqa: TCH001

if TYPE_CHECKING:
    from telegram import Bot, MessageEntity, Update  # type: ignore[import-untyped]
    from telegram.ext import ContextTypes  # type: ignore[import-untyped]

    from rai_agent.daemon.dispatcher import SessionDispatcher
    from rai_agent.daemon.registry import SessionRegistry
    from rai_agent.daemon.telegram_pipeline import TelegramHandler

_log = logging.getLogger(__name__)


# ─── Table Transformation (S7.4) ─────────────────────────────────────────────

_TABLE_ROW_RE = re.compile(r"^\|.*\|$")
_SEPARATOR_RE = re.compile(r"^\|[\s:]*-{3,}[\s:]*(?:\|[\s:]*-{3,}[\s:]*)*\|$")

_WIDE_THRESHOLD = 35


def _parse_cells(row: str) -> list[str]:
    """Split a markdown table row into stripped cell values."""
    # Strip leading/trailing pipes then split on inner pipes
    inner = row.strip("|")
    return [cell.strip() for cell in inner.split("|")]


def _table_to_key_value(headers: list[str], data_rows: list[list[str]]) -> str:
    """Convert parsed table to bold key-value vertical format."""
    blocks: list[str] = []
    for row in data_rows:
        lines: list[str] = []
        for i, header in enumerate(headers):
            value = row[i] if i < len(row) else ""
            if value:
                lines.append(f"**{header}:** {value}")
        if lines:
            blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def transform_tables_for_telegram(md: str) -> str:
    """Pre-process markdown tables for Telegram mobile display.

    Wide tables (>35 char rows) are transformed to bold key-value vertical
    format. Narrow tables pass through unchanged.
    """
    lines = md.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        # Detect start of a potential table block
        if _TABLE_ROW_RE.match(lines[i].strip()):
            # Collect contiguous table rows
            table_lines: list[str] = []
            j = i
            while j < len(lines) and _TABLE_ROW_RE.match(lines[j].strip()):
                table_lines.append(lines[j])
                j += 1

            # Validate: must have separator row (at least 3 lines: header, sep, data)
            separator_idx: int | None = None
            for k, tl in enumerate(table_lines):
                if _SEPARATOR_RE.match(tl.strip()):
                    separator_idx = k
                    break

            if separator_idx is not None and len(table_lines) >= 2:
                # Parse the table
                headers = _parse_cells(table_lines[0])
                data_rows = [
                    _parse_cells(tl)
                    for idx, tl in enumerate(table_lines)
                    if idx != 0 and idx != separator_idx
                ]

                # Calculate max raw line width
                max_width = max(len(tl) for tl in table_lines)

                if max_width > _WIDE_THRESHOLD:
                    result.append(_table_to_key_value(headers, data_rows))
                else:
                    result.extend(table_lines)
                i = j
            else:
                # Not a valid table, pass through
                result.append(lines[i])
                i += 1
        else:
            result.append(lines[i])
            i += 1

    return "\n".join(result)


# ─── Markdown Conversion (RAI-31, ADR-001) ──────────────────────────────────


def convert_for_telegram(
    md: str,
) -> tuple[str, list[MessageEntity] | None]:
    """Convert Markdown to Telegram-compatible (text, entities) tuple.

    Uses telegramify-markdown (entity-based, AST parser).
    On conversion error, returns (original_text, None) as fallback.

    Note: telegramify-markdown is untyped; explicit str()/int() casts
    at the boundary satisfy runtime correctness. Pyright Unknown warnings
    are suppressed at function level.
    """
    from telegram import MessageEntity  # type: ignore[import-untyped]

    md = transform_tables_for_telegram(md)
    try:
        raw_result: Any = telegramify_markdown_convert(md)  # pyright: ignore[reportUnknownVariableType]
        text: str = str(raw_result[0])  # pyright: ignore[reportUnknownArgumentType]
        raw_entities: list[Any] = list(raw_result[1])  # pyright: ignore[reportUnknownArgumentType]
        # Adapt library entities → PTB MessageEntity
        ptb_entities: list[MessageEntity] = [
            MessageEntity(
                type=str(e.type),
                offset=int(e.offset),
                length=int(e.length),
                url=str(e.url) if e.url else None,
                language=str(e.language) if e.language else None,
            )
            for e in raw_entities
        ]
    except Exception:
        _log.warning(
            "Markdown→Telegram conversion failed, falling back to plain text",
            exc_info=True,
        )
        return md, None
    return text, ptb_entities


def split_for_telegram(
    md: str,
    max_utf16_len: int = 4096,
) -> list[tuple[str, list[MessageEntity] | None]]:
    """Convert Markdown to Telegram chunks of ≤max_utf16_len UTF-16 code units.

    Pipeline: telegramify_markdown_convert(md) → split_entities → adapt to PTB.
    Uses library-native entities for splitting (avoids type mismatch), then
    converts each chunk's entities to PTB MessageEntity.
    On conversion failure, returns [(original_text, None)] as fallback.
    """
    from telegram import MessageEntity  # type: ignore[import-untyped]

    md = transform_tables_for_telegram(md)
    try:
        raw_result: Any = telegramify_markdown_convert(md)  # pyright: ignore[reportUnknownVariableType]
        text: str = str(raw_result[0])  # pyright: ignore[reportUnknownArgumentType]
        raw_entities: list[Any] = list(raw_result[1])  # pyright: ignore[reportUnknownArgumentType]
    except Exception:
        _log.warning(
            "Markdown→Telegram conversion failed in split_for_telegram, "
            "falling back to plain text",
            exc_info=True,
        )
        return [(md[:max_utf16_len], None)]

    # Split using library-native entities (same type split_entities expects)
    raw_chunks: list[Any] = list(  # pyright: ignore[reportUnknownVariableType]
        telegramify_split_entities(text, raw_entities, max_utf16_len)  # pyright: ignore[reportUnknownArgumentType]
    )

    result: list[tuple[str, list[MessageEntity] | None]] = []
    for chunk_text, chunk_entities in raw_chunks:  # pyright: ignore[reportUnknownVariableType]
        ptb_entities: list[MessageEntity] = [
            MessageEntity(
                type=str(e.type),
                offset=int(e.offset),
                length=int(e.length),
                url=str(e.url) if e.url else None,
                language=str(e.language) if e.language else None,
            )
            for e in chunk_entities  # pyright: ignore[reportUnknownVariableType]
        ]
        result.append((str(chunk_text), ptb_entities if ptb_entities else None))
    return result if result else [(md[:max_utf16_len], None)]


# ─── Event Model ──────────────────────────────────────────────────────────────


class TelegramRunEvent(BaseEvent):  # type: ignore[misc]
    """Emitted on EventBus when an authorized Telegram user sends a message.

    Parallels ScheduledRunEvent from S2.4. The event carries a RunConfig
    ready for dispatch — it's not just a message, it's a run request.
    """

    chat_id: int
    user_id: int
    message_text: str
    run_config: RunConfig
    timestamp: datetime


# ─── Rate Limiter ─────────────────────────────────────────────────────────────


class TokenBucketRateLimiter:
    """Per-user token bucket rate limiter.

    Default: 5 burst tokens, refill at 1 token every 5 seconds (0.2/s).
    """

    def __init__(self, max_tokens: int = 5, refill_rate: float = 0.2) -> None:
        self._max_tokens = max_tokens
        self._refill_rate = refill_rate
        self._buckets: dict[int, tuple[float, float]] = {}

    def allow(self, user_id: int) -> bool:
        """Check if user_id is allowed to proceed. Consumes one token if yes."""
        now = time.monotonic()
        tokens, last_refill = self._buckets.get(user_id, (float(self._max_tokens), now))
        elapsed = now - last_refill
        tokens = min(float(self._max_tokens), tokens + elapsed * self._refill_rate)
        if tokens >= 1.0:
            self._buckets[user_id] = (tokens - 1.0, now)
            return True
        self._buckets[user_id] = (tokens, now)
        return False


# ─── DraftStreamer ────────────────────────────────────────────────────────────


class DraftStreamer:
    """Shows agent activity via ephemeral drafts, sends final response as message.

    Uses send_message_draft to show what the agent is doing (reading files,
    thinking, running tests). The draft is ephemeral — it disappears when
    the final response is sent via send_message.

    Buffer accumulates the full LLM response silently. Final flush sends
    each chunk as a new message via send_message, with entity-based
    formatting. Long responses are split into multiple messages if content
    exceeds 4096 UTF-16 code units (RAI-34).
    """

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        throttle_s: float = 0.3,
        keepalive_s: float = 4.0,
    ) -> None:
        self._bot = bot
        self._chat_id = chat_id
        self._throttle_s = throttle_s
        self._keepalive_s = keepalive_s
        self._buffer: str = ""
        self._draft_id: int = int(time.monotonic() * 1000)
        self._last_draft: float = 0.0
        self._last_status: str = ""
        self._lock = asyncio.Lock()
        self._keepalive_task: asyncio.Task[None] | None = None
        self._stopped = False

    def start_keepalive(self) -> None:
        """Start background task that re-sends last status + typing every keepalive_s."""
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _keepalive_loop(self) -> None:
        """Re-send last status draft and typing indicator periodically."""
        while not self._stopped:
            await asyncio.sleep(self._keepalive_s)
            if self._stopped:
                break
            async with self._lock:
                if self._last_status:
                    try:
                        await self._bot.send_chat_action(
                            self._chat_id,
                            "typing",
                        )
                        await self._bot.send_message_draft(
                            chat_id=self._chat_id,
                            draft_id=self._draft_id,
                            text=self._last_status,
                        )
                    except Exception:  # noqa: BLE001
                        pass  # best-effort, don't crash on network errors

    async def set_status(self, status: str) -> None:
        """Show an ephemeral status message via send_message_draft.

        Also sends typing indicator. Throttled to avoid rate limits.
        """
        async with self._lock:
            self._last_status = status
            now = time.monotonic()
            if now - self._last_draft >= self._throttle_s:
                await self._bot.send_chat_action(
                    self._chat_id,
                    "typing",
                )
                await self._bot.send_message_draft(
                    chat_id=self._chat_id,
                    draft_id=self._draft_id,
                    text=status,
                )
                self._last_draft = now

    async def append(self, text: str) -> None:
        """Accumulate response text in buffer (no draft sent)."""
        async with self._lock:
            self._buffer += text

    async def flush(self) -> None:
        """Stop keepalive and send final response (RAI-34)."""
        self._stopped = True
        if self._keepalive_task is not None:
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass
        async with self._lock:
            if self._buffer:
                await self._flush_final()

    async def _flush_final(self) -> None:
        """Convert, split, and deliver the full response (RAI-34)."""
        from telegram.error import BadRequest  # type: ignore[import-untyped]

        chunks = split_for_telegram(self._buffer)

        for text, entities in chunks:
            try:
                await self._bot.send_message(
                    self._chat_id,
                    text,
                    entities=entities,
                )
            except BadRequest:
                if entities is not None:
                    await self._bot.send_message(self._chat_id, text)
                else:
                    raise


# ─── Image download (provider-specific) ─────────────────────────────────────


async def download_telegram_image(
    msg: Any,
) -> tuple[bytes, str]:
    """Download image from a Telegram message.

    Handles both ``message.photo`` (compressed JPEG) and
    ``message.document`` with image MIME type (original format).

    Args:
        msg: Telegram Message object.

    Returns:
        Tuple of (image_bytes, mime_type).

    Raises:
        ValueError: If document has unsupported MIME type.
        telegram.error.TelegramError: On download failure.
    """
    if msg.photo:
        # photo[-1] is highest resolution
        file = await msg.photo[-1].get_file()
        data: bytearray = await file.download_as_bytearray()
        return bytes(data), "image/jpeg"

    if (
        msg.document
        and msg.document.mime_type
        and msg.document.mime_type.startswith("image/")
    ):
        mime: str = msg.document.mime_type
        if mime not in SUPPORTED_MIMES:
            supported = ", ".join(sorted(SUPPORTED_MIMES))
            raise ValueError(
                f"El formato {mime} no está soportado. Formatos válidos: {supported}"
            )
        file = await msg.document.get_file()
        data = await file.download_as_bytearray()
        return bytes(data), mime

    raise ValueError("Message contains no image")


# ─── TelegramTrigger ─────────────────────────────────────────────────────────


class TelegramTrigger:
    """PTB wrapper that builds MessageContext and composes a pipeline.

    Implements RaiTrigger Protocol (start/stop lifecycle).
    Pipeline: auth → rate_limit → coalesce → dispatch.
    """

    def __init__(
        self,
        bot_token: str,
        allowed_users: set[int],
        *,
        dispatcher: SessionDispatcher,
        registry: SessionRegistry,
        handler: TelegramHandler,
        cwd: str = ".",
        max_tokens: int = 5,
        refill_rate: float = 0.2,
        coalescing_config: CoalescingConfig | None = None,
    ) -> None:
        from rai_agent.daemon.middleware import (
            Middleware,
            make_auth_middleware,
            make_coalescing_middleware,
            make_dispatch_middleware,
            make_rate_limit_middleware,
            make_session_command_middleware,
        )

        self._allowed_users = allowed_users
        self._rate_limiter = TokenBucketRateLimiter(
            max_tokens=max_tokens,
            refill_rate=refill_rate,
        )

        # Build middleware pipeline once
        # Order: auth → rate_limit → command → coalesce → dispatch
        # Command BEFORE coalesce: /session commands must not be
        # merged with adjacent messages (they return immediately).
        self._pipeline: list[Middleware] = [
            make_auth_middleware(allowed_users),
            make_rate_limit_middleware(self._rate_limiter),
            make_session_command_middleware(registry, cwd),
            make_coalescing_middleware(
                coalescing_config or CoalescingConfig(),
            ),
            make_dispatch_middleware(dispatcher, registry, cwd),
        ]

        # PTB Application — Any due to 6 generic type params
        self._app: Any = Application.builder().token(bot_token).build()
        self._app.add_handler(
            MessageHandler(
                filters.TEXT,
                self._handle_message,
            ),
        )
        self._app.add_handler(
            MessageHandler(
                filters.PHOTO | filters.Document.IMAGE,
                self._handle_image_message,
            ),
        )

    @property
    def bot(self) -> Any:
        """Expose the PTB Bot instance for pipeline wiring."""
        return self._app.bot

    async def start(self) -> None:
        """Start polling for Telegram updates."""
        await self._app.initialize()
        await self._app.start()
        if self._app.updater:
            await self._app.updater.start_polling()

    async def stop(self) -> None:
        """Gracefully shut down the bot."""
        if self._app.updater:
            await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()

    async def _handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Build MessageContext and compose the middleware pipeline."""
        user = update.effective_user
        if not user or not update.message or not update.message.text:
            return

        msg = update.message
        ctx = self._build_ctx(msg, user, msg.text or "")
        await compose(self._pipeline, ctx)

    def _build_ctx(
        self,
        msg: Any,
        user: Any,
        prompt: str,
        content_blocks: list[dict[str, Any]] | None = None,
    ) -> MessageContext:
        """Build a MessageContext for the middleware pipeline."""

        async def _reply(text: str) -> None:
            await msg.reply_text(text)

        return MessageContext(
            session_key=f"telegram:default:dm:{msg.chat_id}",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id=str(msg.chat_id),
            user_id=user.id,
            prompt=prompt,
            reply_text=_reply,
            content_blocks=content_blocks,
        )

    async def _handle_image_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Handle photo/document-image messages (S7.5)."""
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return

        # Download image
        try:
            image_bytes, mime_type = await download_telegram_image(msg)
        except ValueError as exc:
            await msg.reply_text(str(exc))
            return
        except Exception:
            _log.warning(
                "Image download failed for chat %s",
                msg.chat_id,
                exc_info=True,
            )
            await msg.reply_text("No pude descargar la imagen. ¿Podrías reenviarla?")
            return

        # Validate image
        try:
            validate_image(image_bytes, mime_type)
        except ValueError as exc:
            await msg.reply_text(str(exc))
            return

        # Build content blocks and dispatch
        caption = msg.caption or ""
        content_blocks = build_image_content_blocks(
            images=[(image_bytes, mime_type)],
            caption=caption or None,
        )

        ctx = self._build_ctx(
            msg,
            user,
            caption,
            content_blocks,
        )
        await compose(self._pipeline, ctx)
