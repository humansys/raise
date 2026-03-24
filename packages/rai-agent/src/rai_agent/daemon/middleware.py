"""Composable middleware pipeline for the Rai daemon.

Koa-style middleware composition: each middleware receives a context and a
next function. Calling next() invokes the next middleware in the chain.
Not calling next() stops the chain (e.g., auth rejection).

Provider-agnostic — Telegram, Google Chat, and future providers share
the same middleware pipeline via MessageContext.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from rai_agent.daemon.dispatcher import SessionDispatcher
    from rai_agent.daemon.registry import SessionRegistry
    from rai_agent.daemon.telegram import TokenBucketRateLimiter

__all__ = [
    "NextFn",
    "Middleware",
    "MessageContext",
    "CoalescingConfig",
    "compose",
    "make_auth_middleware",
    "make_rate_limit_middleware",
    "make_coalescing_middleware",
    "make_session_command_middleware",
    "make_dispatch_middleware",
]

# ── Type aliases ─────────────────────────────────────────────────────────────

NextFn = Callable[[], Awaitable[None]]
"""Async function that invokes the next middleware in the chain."""

Middleware = Callable[[Any, NextFn], Awaitable[None]]
"""Async middleware: receives context and next function."""


# ── Coalescing data structures ──────────────────────────────────────────────


class CoalescingConfig(BaseModel):
    """Configuration for message coalescing middleware.

    Controls how multiple rapid messages from the same session are merged
    into a single prompt before dispatching to the handler.
    """

    window_seconds: float = Field(default=0.5, gt=0)
    """Time window to wait for additional messages before flushing."""

    max_parts: int = Field(default=10, gt=0)
    """Maximum number of message parts before immediate flush."""

    max_chars: int = Field(default=10_000, gt=0)
    """Maximum total characters before immediate flush."""


@dataclass
class _SessionBuffer:
    """Internal buffer accumulating message parts for one session."""

    ctx: MessageContext
    """MessageContext from the first message in the coalescing window."""

    next_fn: NextFn
    """The next function captured from the middleware chain."""

    parts: list[str] = field(default_factory=lambda: [])
    """Accumulated message parts."""

    total_chars: int = 0
    """Running total of characters across all parts."""

    timer_task: asyncio.Task[None] | None = None
    """Pending flush timer task, if any."""

    def should_flush(self, config: CoalescingConfig) -> bool:
        """Return True if the buffer should be flushed immediately."""
        return (
            len(self.parts) >= config.max_parts
            or self.total_chars >= config.max_chars
        )


# ── MessageContext ───────────────────────────────────────────────────────────


@dataclass
class MessageContext:
    """Provider-agnostic message context for the middleware pipeline.

    Built by each provider trigger (Telegram, Google Chat, etc.) and
    passed through the middleware chain. Mutable — middlewares can
    modify fields (e.g., coalescing modifies ``prompt``).
    """

    session_key: str
    """Unique session identifier: ``{provider}:{account}:{scope}:{channel_id}``."""

    provider: str
    """Origin provider: ``telegram``, ``gchat``, ``websocket``, ``cron``."""

    account: str
    """Bot/account name from config (default: ``"default"``)."""

    scope: str
    """Context type: ``dm``, ``group``, ``session``, ``job``."""

    channel_id: str
    """Provider-specific channel/chat identifier."""

    user_id: int
    """Numeric user identifier (provider-specific)."""

    prompt: str
    """User message text. May be modified by coalescing middleware."""

    reply_text: Callable[[str], Awaitable[None]]
    """Callback to send a plain-text reply to the user."""

    content_blocks: list[dict[str, Any]] | None = None
    """Multimodal content blocks (images + text). When present, runtime
    uses these instead of ``prompt`` for the SDK call. Coalescing
    middleware skips messages with content_blocks (D7)."""

    metadata: dict[str, Any] = field(default_factory=lambda: dict[str, Any]())
    """Provider-specific extra data (chat_type, group_title, etc.)."""


# ── compose() ────────────────────────────────────────────────────────────────


async def compose(
    middlewares: Sequence[Middleware],
    ctx: Any,
) -> None:
    """Execute a middleware chain in order, Koa-style.

    Each middleware receives the shared ``ctx`` and a ``next_fn``.
    Calling ``await next_fn()`` invokes the next middleware.
    Not calling ``next_fn()`` stops the chain.

    Args:
        middlewares: Ordered sequence of middleware functions.
        ctx: Shared context object passed to every middleware.
    """

    async def dispatch(index: int) -> None:
        if index < len(middlewares):
            await middlewares[index](ctx, lambda: dispatch(index + 1))

    await dispatch(0)


# ── Middleware factories ─────────────────────────────────────────────────────


def make_auth_middleware(allowed_users: set[int]) -> Middleware:
    """Create an auth middleware that rejects users not in the allowed set.

    Args:
        allowed_users: Set of authorized user IDs.

    Returns:
        Middleware that checks ``ctx.user_id`` against ``allowed_users``.
    """

    async def middleware(ctx: Any, next_fn: NextFn) -> None:
        if ctx.user_id not in allowed_users:
            await ctx.reply_text("Not authorized.")
            return
        await next_fn()

    return middleware


def make_rate_limit_middleware(limiter: TokenBucketRateLimiter) -> Middleware:
    """Create a rate-limit middleware using a token bucket limiter.

    Args:
        limiter: A ``TokenBucketRateLimiter`` instance.

    Returns:
        Middleware that checks ``ctx.user_id`` against the limiter.
    """

    async def middleware(ctx: Any, next_fn: NextFn) -> None:
        if not limiter.allow(ctx.user_id):
            await ctx.reply_text("Rate limit exceeded. Try again later.")
            return
        await next_fn()

    return middleware


def make_coalescing_middleware(config: CoalescingConfig) -> Middleware:
    """Create a coalescing middleware that merges rapid messages per session.

    Multiple messages arriving within ``config.window_seconds`` for the same
    ``session_key`` are joined with ``\\n`` into a single prompt. Flushing
    happens either when the timer expires or when ``max_parts``/``max_chars``
    thresholds are reached (immediate flush).

    Args:
        config: Coalescing configuration (window, limits).

    Returns:
        Middleware that buffers and coalesces messages per session.
    """
    _log = logging.getLogger(__name__)
    buffers: dict[str, _SessionBuffer] = {}

    async def _flush(key: str) -> None:
        """Flush the buffer for *key*: merge parts, mutate ctx, call next."""
        if key not in buffers:
            return  # Already flushed (race guard)
        buf = buffers.pop(key)
        merged = "\n".join(buf.parts)
        buf.ctx.prompt = merged
        try:
            await buf.next_fn()
        except Exception:
            _log.exception(
                "Coalescing flush failed for session %s (%d parts lost)",
                key,
                len(buf.parts),
            )
            raise

    async def middleware(ctx: Any, next_fn: NextFn) -> None:
        # D7: Image messages bypass coalescing — process immediately
        if getattr(ctx, "content_blocks", None) is not None:
            await next_fn()
            return

        key: str = ctx.session_key
        if key not in buffers:
            buffers[key] = _SessionBuffer(ctx=ctx, next_fn=next_fn)
        buf = buffers[key]
        buf.parts.append(ctx.prompt)
        buf.total_chars += len(ctx.prompt)

        if buf.should_flush(config):
            # Immediate flush — cancel pending timer if any
            if buf.timer_task is not None and not buf.timer_task.done():
                buf.timer_task.cancel()
            await _flush(key)
        else:
            # Reset the timer
            if buf.timer_task is not None and not buf.timer_task.done():
                buf.timer_task.cancel()

            async def _flush_after_timeout(k: str = key) -> None:
                await asyncio.sleep(config.window_seconds)
                # _flush logs the error; suppress prevents task crash
                with contextlib.suppress(Exception):
                    await _flush(k)

            buf.timer_task = asyncio.create_task(_flush_after_timeout())

    return middleware


def make_session_command_middleware(
    registry: SessionRegistry,
    cwd: str,
) -> Middleware:
    """Create a session command middleware for ``/session`` subcommands.

    Handles ``/session new|list|switch|close|delete``.
    Bare ``/session`` shows help. Unknown subcommands reply with error.
    Non-``/session`` commands and regular text pass through to ``next()``.

    Args:
        registry: ``SessionRegistry`` for session queries and mutations.
        cwd: Working directory for new sessions.

    Returns:
        Middleware that intercepts ``/session`` commands.
    """
    from rai_agent.daemon.registry import SessionKey, SessionLimitError

    def _fmt_tokens(tokens: int) -> str:
        """Format token count as compact string."""
        return f"{tokens // 1000}k tokens"

    async def _resolve_name(
        ctx: MessageContext, arg: str,
    ) -> str | None:
        """Resolve #N index to session name, or return arg as-is.

        Returns None and replies with error if index is out of range.
        """
        if not arg.startswith("#"):
            return arg
        try:
            idx = int(arg[1:])
        except ValueError:
            await ctx.reply_text(f"Invalid index: {arg}")
            return None
        key = SessionKey.parse(ctx.session_key)
        sessions = await registry.list_named(key)
        if idx < 1 or idx > len(sessions):
            await ctx.reply_text(
                f"Index {arg} out of range (1-{len(sessions)}).",
            )
            return None
        return sessions[idx - 1].name

    async def _handle_new(ctx: MessageContext, arg: str) -> None:
        """Create a new session, optionally with a given name."""
        key = SessionKey.parse(ctx.session_key)
        name: str | None = arg if arg else None
        try:
            session = await registry.create_named(key, name=name, cwd=cwd)
        except SessionLimitError:
            await ctx.reply_text(
                "Session limit reached. Close or delete a session first."
            )
            return
        await ctx.reply_text(f"Created session: {session.name}")

    async def _handle_list(ctx: MessageContext, arg: str) -> None:
        """List open sessions for this chat."""
        key = SessionKey.parse(ctx.session_key)
        sessions = await registry.list_named(key)
        if not sessions:
            await ctx.reply_text("No sessions found.")
            return

        parts: list[str] = ["Sessions:"]
        for i, s in enumerate(sessions, 1):
            current = " *" if s.is_current else ""
            parts.append(
                f"  #{i}  {s.name}  "
                f"{_fmt_tokens(s.last_input_tokens)}{current}",
            )
        await ctx.reply_text("\n".join(parts))

    async def _handle_switch(ctx: MessageContext, arg: str) -> None:
        """Switch to a session by name or #index."""
        if not arg:
            await ctx.reply_text("Usage: /session switch <name or #N>")
            return
        name = await _resolve_name(ctx, arg)
        if name is None:
            return
        key = SessionKey.parse(ctx.session_key)
        try:
            await registry.switch_to(key, name=name)
        except KeyError:
            await ctx.reply_text(f"Session '{name}' not found.")
            return
        await ctx.reply_text(f"Switched to session: {name}")

    async def _handle_close(ctx: MessageContext, arg: str) -> None:
        """Close a session by name, #index, or current if omitted."""
        key = SessionKey.parse(ctx.session_key)
        if arg:
            resolved = await _resolve_name(ctx, arg)
            if resolved is None:
                return
            name: str | None = resolved
        else:
            name = None
        try:
            await registry.close_named(key, name=name)
        except KeyError:
            target = name if name else "current session"
            await ctx.reply_text(f"Session not found: {target}")
            return
        if name:
            await ctx.reply_text(f"Closed: {name}")
        else:
            await ctx.reply_text(
                "Closed current session. Next message starts a new one."
            )

    async def _handle_delete(ctx: MessageContext, arg: str) -> None:
        """Delete a session by name or #index."""
        if not arg:
            await ctx.reply_text("Usage: /session delete <name or #N>")
            return
        name = await _resolve_name(ctx, arg)
        if name is None:
            return
        key = SessionKey.parse(ctx.session_key)
        try:
            await registry.delete_named(key, name=name)
        except ValueError:
            await ctx.reply_text(
                "Cannot delete the current session. "
                "Switch to another session first.",
            )
            return
        except KeyError:
            await ctx.reply_text(f"Session '{name}' not found.")
            return
        await ctx.reply_text(f"Deleted session: {name}")

    handlers: dict[
        str,
        Callable[[MessageContext, str], Awaitable[None]],
    ] = {
        "new": _handle_new,
        "list": _handle_list,
        "switch": _handle_switch,
        "close": _handle_close,
        "delete": _handle_delete,
    }

    async def _show_help(ctx: MessageContext) -> None:
        """Show available /session subcommands."""
        lines = [
            "Available commands:",
            "  /session new [name] — Create a new session",
            "  /session list — List open sessions",
            "  /session switch <name or #N> — Switch to a session",
            "  /session close [name or #N] — Close a session",
            "  /session delete <name or #N> — Delete a session",
        ]
        await ctx.reply_text("\n".join(lines))

    async def middleware(ctx: MessageContext, next_fn: NextFn) -> None:
        prompt: str = ctx.prompt.strip()
        if not prompt.startswith("/"):
            await next_fn()
            return

        parts = prompt.split(maxsplit=2)
        command = parts[0].lower()

        if command != "/session":
            await next_fn()
            return

        subcommand = parts[1].lower() if len(parts) > 1 else ""
        arg = parts[2].strip() if len(parts) > 2 else ""

        if not subcommand:
            await _show_help(ctx)
        elif subcommand in handlers:
            await handlers[subcommand](ctx, arg)
        else:
            await ctx.reply_text(
                f"Unknown: /session {subcommand}\n"
                "Use /session for available commands.",
            )

    return middleware


def make_dispatch_middleware(
    dispatcher: SessionDispatcher,
    registry: SessionRegistry,
    cwd: str,
) -> Middleware:
    """Create a dispatch middleware that bridges the pipeline to the dispatcher.

    Parses ``SessionKey`` from ``ctx.session_key``, looks up or creates a
    ``Session`` via the registry, builds a ``SessionRequest``, and enqueues
    it on the ``SessionDispatcher``. Catches ``SessionBusyError`` and replies
    to the user.

    The handler is wired into the dispatcher at construction time — it is not
    a parameter of this middleware.

    Args:
        dispatcher: ``SessionDispatcher`` for per-session FIFO queueing.
        registry: ``SessionRegistry`` for session lookup/creation.
        cwd: Working directory for new sessions.

    Returns:
        Middleware that dispatches messages through the session pipeline.
    """
    from rai_agent.daemon.dispatcher import SessionBusyError, SessionRequest
    from rai_agent.daemon.registry import SessionKey

    _dispatch_log = logging.getLogger(__name__)

    async def _async_noop() -> None:
        """No-op on_complete callback."""

    async def middleware(ctx: Any, _next_fn: NextFn) -> None:
        key = SessionKey.parse(ctx.session_key)
        session = await registry.get_current(key)
        if session is None:
            session = await registry.create_named(key, cwd=cwd)

        async def _on_error(exc: Exception) -> None:
            _dispatch_log.error(
                "Run failed for session %s: %s", ctx.session_key, exc,
            )
            await ctx.reply_text("Run failed. Check logs for details.")

        request = SessionRequest(
            session_key=ctx.session_key,
            prompt=ctx.prompt,
            send=ctx.reply_text,
            on_complete=_async_noop,
            on_error=_on_error,
            content_blocks=getattr(ctx, "content_blocks", None),
            metadata={"chat_id": ctx.channel_id, "session": session},
        )
        try:
            await dispatcher.dispatch(request)
        except SessionBusyError:
            await ctx.reply_text(
                "Too many messages queued. Try again shortly.",
            )

    return middleware
