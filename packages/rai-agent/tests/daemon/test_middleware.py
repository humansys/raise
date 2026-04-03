"""Tests for middleware pipeline — compose(), MessageContext, and middlewares."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from rai_agent.daemon.middleware import (
    CoalescingConfig,
    MessageContext,
    Middleware,
    NextFn,
    _SessionBuffer,  # pyright: ignore[reportPrivateUsage]
    compose,
    make_auth_middleware,
    make_coalescing_middleware,
    make_rate_limit_middleware,
)
from rai_agent.daemon.telegram import TokenBucketRateLimiter

# ── Helpers ──────────────────────────────────────────────────────────────────


def _tracking_middleware(name: str, log: list[str]) -> Middleware:
    """Create a middleware that logs its name before and after next()."""

    async def mw(ctx: Any, next_fn: NextFn) -> None:
        log.append(f"{name}:before")
        await next_fn()
        log.append(f"{name}:after")

    return mw


def _blocking_middleware(name: str, log: list[str]) -> Middleware:
    """Create a middleware that does NOT call next()."""

    async def mw(ctx: Any, next_fn: NextFn) -> None:
        log.append(f"{name}:blocked")
        # intentionally not calling next_fn()

    return mw


# ── compose() tests ──────────────────────────────────────────────────────────


class TestCompose:
    @pytest.mark.asyncio
    async def test_executes_middlewares_in_order(self) -> None:
        log: list[str] = []
        m1 = _tracking_middleware("m1", log)
        m2 = _tracking_middleware("m2", log)
        m3 = _tracking_middleware("m3", log)

        await compose([m1, m2, m3], ctx=None)

        assert log == [
            "m1:before",
            "m2:before",
            "m3:before",
            "m3:after",
            "m2:after",
            "m1:after",
        ]

    @pytest.mark.asyncio
    async def test_middleware_can_skip_next(self) -> None:
        log: list[str] = []
        m1 = _tracking_middleware("m1", log)
        m2 = _blocking_middleware("m2", log)
        m3 = _tracking_middleware("m3", log)

        await compose([m1, m2, m3], ctx=None)

        # m3 should never execute
        assert log == [
            "m1:before",
            "m2:blocked",
            "m1:after",
        ]

    @pytest.mark.asyncio
    async def test_empty_chain_does_not_error(self) -> None:
        await compose([], ctx=None)  # should not raise

    @pytest.mark.asyncio
    async def test_single_middleware(self) -> None:
        log: list[str] = []
        m1 = _tracking_middleware("m1", log)

        await compose([m1], ctx=None)

        assert log == ["m1:before", "m1:after"]

    @pytest.mark.asyncio
    async def test_context_is_passed_to_all_middlewares(self) -> None:
        seen_contexts: list[Any] = []

        async def capture(ctx: Any, next_fn: NextFn) -> None:
            seen_contexts.append(ctx)
            await next_fn()

        sentinel = object()
        await compose([capture, capture], ctx=sentinel)

        assert all(c is sentinel for c in seen_contexts)
        assert len(seen_contexts) == 2

    @pytest.mark.asyncio
    async def test_middleware_can_modify_context(self) -> None:
        """Middlewares can mutate shared context for downstream consumers."""

        class MutableCtx:
            value: str = "original"

        async def modifier(ctx: MutableCtx, next_fn: NextFn) -> None:
            ctx.value = "modified"
            await next_fn()

        async def reader(ctx: MutableCtx, next_fn: NextFn) -> None:
            assert ctx.value == "modified"
            await next_fn()

        ctx = MutableCtx()
        await compose([modifier, reader], ctx=ctx)
        assert ctx.value == "modified"


# ── MessageContext tests ─────────────────────────────────────────────────────


def _make_ctx(
    *,
    user_id: int = 456,
    replies: list[str] | None = None,
) -> MessageContext:
    """Create a MessageContext with sensible defaults for testing."""
    captured: list[str] = replies if replies is not None else []

    async def mock_reply(text: str) -> None:
        captured.append(text)

    return MessageContext(
        session_key="tg:default:dm:123",
        provider="telegram",
        account="default",
        scope="dm",
        channel_id="123",
        user_id=user_id,
        prompt="hello rai",
        reply_text=mock_reply,
    )


class TestMessageContext:
    def test_has_all_required_fields(self) -> None:
        ctx = _make_ctx()
        assert ctx.session_key == "tg:default:dm:123"
        assert ctx.provider == "telegram"
        assert ctx.account == "default"
        assert ctx.scope == "dm"
        assert ctx.channel_id == "123"
        assert ctx.user_id == 456
        assert ctx.prompt == "hello rai"
        assert callable(ctx.reply_text)
        assert ctx.metadata == {}

    def test_metadata_defaults_to_empty_dict(self) -> None:
        ctx = _make_ctx()
        assert ctx.metadata == {}

    def test_metadata_can_be_set(self) -> None:
        ctx = _make_ctx()
        ctx.metadata["chat_type"] = "private"
        assert ctx.metadata["chat_type"] == "private"

    def test_prompt_is_mutable(self) -> None:
        ctx = _make_ctx()
        ctx.prompt = "modified"
        assert ctx.prompt == "modified"

    @pytest.mark.asyncio
    async def test_reply_text_calls_callback(self) -> None:
        replies: list[str] = []
        ctx = _make_ctx(replies=replies)
        await ctx.reply_text("hello")
        assert replies == ["hello"]


# ── auth middleware tests ────────────────────────────────────────────────────


class TestAuthMiddleware:
    @pytest.mark.asyncio
    async def test_authorized_user_passes(self) -> None:
        ctx = _make_ctx(user_id=456)
        executed: list[bool] = []

        async def handler(ctx: MessageContext, next_fn: NextFn) -> None:
            executed.append(True)
            await next_fn()

        auth = make_auth_middleware(allowed_users={456})
        await compose([auth, handler], ctx)

        assert executed == [True]

    @pytest.mark.asyncio
    async def test_unauthorized_user_rejected(self) -> None:
        replies: list[str] = []
        ctx = _make_ctx(user_id=999, replies=replies)
        executed: list[bool] = []

        async def handler(ctx: MessageContext, next_fn: NextFn) -> None:
            executed.append(True)
            await next_fn()

        auth = make_auth_middleware(allowed_users={456})
        await compose([auth, handler], ctx)

        assert executed == []
        assert replies == ["Not authorized."]

    @pytest.mark.asyncio
    async def test_empty_allowed_set_rejects_all(self) -> None:
        replies: list[str] = []
        ctx = _make_ctx(user_id=456, replies=replies)

        auth = make_auth_middleware(allowed_users=set())
        await compose([auth], ctx)

        assert replies == ["Not authorized."]


# ── rate limit middleware tests ──────────────────────────────────────────────


class TestRateLimitMiddleware:
    @pytest.mark.asyncio
    async def test_under_limit_passes(self) -> None:
        limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=0.0)
        ctx = _make_ctx()
        executed: list[bool] = []

        async def handler(ctx: MessageContext, next_fn: NextFn) -> None:
            executed.append(True)
            await next_fn()

        rl = make_rate_limit_middleware(limiter)
        await compose([rl, handler], ctx)

        assert executed == [True]

    @pytest.mark.asyncio
    async def test_over_limit_rejected(self) -> None:
        # Exhaust all tokens
        limiter = TokenBucketRateLimiter(max_tokens=1, refill_rate=0.0)
        limiter.allow(456)  # consume the only token

        replies: list[str] = []
        ctx = _make_ctx(user_id=456, replies=replies)
        executed: list[bool] = []

        async def handler(ctx: MessageContext, next_fn: NextFn) -> None:
            executed.append(True)
            await next_fn()

        rl = make_rate_limit_middleware(limiter)
        await compose([rl, handler], ctx)

        assert executed == []
        assert replies == ["Rate limit exceeded. Try again later."]

    @pytest.mark.asyncio
    async def test_full_pipeline_auth_then_rate_limit(self) -> None:
        """Integration: auth + rate_limit + handler in a single pipeline."""
        limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=0.0)
        ctx = _make_ctx(user_id=456)
        executed: list[bool] = []

        async def handler(ctx: MessageContext, next_fn: NextFn) -> None:
            executed.append(True)
            await next_fn()

        pipeline = [
            make_auth_middleware(allowed_users={456}),
            make_rate_limit_middleware(limiter),
            handler,
        ]
        await compose(pipeline, ctx)

        assert executed == [True]


# ── CoalescingConfig tests ─────────────────────────────────────────────────


class TestCoalescingConfig:
    def test_defaults(self) -> None:
        cfg = CoalescingConfig()
        assert cfg.window_seconds == 0.5
        assert cfg.max_parts == 10
        assert cfg.max_chars == 10_000

    def test_custom_values(self) -> None:
        cfg = CoalescingConfig(window_seconds=0.5, max_parts=5, max_chars=500)
        assert cfg.window_seconds == 0.5
        assert cfg.max_parts == 5
        assert cfg.max_chars == 500

    def test_rejects_zero_window(self) -> None:
        with pytest.raises(ValueError, match="greater than 0"):
            CoalescingConfig(window_seconds=0)

    def test_rejects_negative_max_parts(self) -> None:
        with pytest.raises(ValueError, match="greater than 0"):
            CoalescingConfig(max_parts=-1)

    def test_rejects_zero_max_chars(self) -> None:
        with pytest.raises(ValueError, match="greater than 0"):
            CoalescingConfig(max_chars=0)


# ── _SessionBuffer tests ──────────────────────────────────────────────────


class TestSessionBuffer:
    def _make_buffer(
        self,
        parts: list[str] | None = None,
        total_chars: int = 0,
    ) -> _SessionBuffer:
        async def _noop() -> None:
            pass

        ctx = _make_coalescing_ctx(prompt="test")
        return _SessionBuffer(
            ctx=ctx,
            next_fn=_noop,
            parts=parts if parts is not None else [],
            total_chars=total_chars,
        )

    def test_should_flush_true_when_parts_at_max(self) -> None:
        buf = self._make_buffer(parts=["x"] * 10, total_chars=10)
        cfg = CoalescingConfig(max_parts=10)
        assert buf.should_flush(cfg) is True

    def test_should_flush_true_when_chars_at_max(self) -> None:
        buf = self._make_buffer(parts=["x"], total_chars=10_000)
        cfg = CoalescingConfig(max_chars=10_000)
        assert buf.should_flush(cfg) is True

    def test_should_flush_false_under_thresholds(self) -> None:
        buf = self._make_buffer(parts=["x", "y"], total_chars=5)
        cfg = CoalescingConfig()
        assert buf.should_flush(cfg) is False


# ── Coalescing middleware tests ────────────────────────────────────────────


def _make_coalescing_ctx(
    *,
    session_key: str = "tg:default:dm:123",
    prompt: str = "hello",
    user_id: int = 456,
    replies: list[str] | None = None,
) -> MessageContext:
    """Create a MessageContext for coalescing tests."""
    captured: list[str] = replies if replies is not None else []

    async def mock_reply(text: str) -> None:
        captured.append(text)

    return MessageContext(
        session_key=session_key,
        provider="telegram",
        account="default",
        scope="dm",
        channel_id="123",
        user_id=user_id,
        prompt=prompt,
        reply_text=mock_reply,
    )


class TestCoalescingMiddleware:
    """Tests for make_coalescing_middleware."""

    @pytest.mark.asyncio
    async def test_single_message_dispatched_after_timeout(self) -> None:
        """A single message is dispatched after the window expires."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)
        ctx = _make_coalescing_ctx(prompt="hello")
        await compose([coalesce, handler], ctx)

        # Not dispatched yet — waiting for window
        assert dispatched == []

        # Wait for window to expire
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["hello"]

    @pytest.mark.asyncio
    async def test_two_messages_merged(self) -> None:
        """Two messages within window are merged with newline separator."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        ctx1 = _make_coalescing_ctx(prompt="hello")
        await compose([coalesce, handler], ctx1)

        ctx2 = _make_coalescing_ctx(prompt="world")
        await compose([coalesce, handler], ctx2)

        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["hello\nworld"]

    @pytest.mark.asyncio
    async def test_three_messages_all_merged(self) -> None:
        """Three messages within window are all merged."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        for text in ["a", "b", "c"]:
            ctx = _make_coalescing_ctx(prompt=text)
            await compose([coalesce, handler], ctx)

        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["a\nb\nc"]

    @pytest.mark.asyncio
    async def test_max_parts_triggers_immediate_flush(self) -> None:
        """Reaching max_parts flushes immediately without timeout."""
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=3, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        for text in ["a", "b", "c"]:
            ctx = _make_coalescing_ctx(prompt=text)
            await compose([coalesce, handler], ctx)

        # Should be dispatched immediately — no sleep needed
        assert dispatched == ["a\nb\nc"]

    @pytest.mark.asyncio
    async def test_max_chars_triggers_immediate_flush(self) -> None:
        """Reaching max_chars flushes immediately without timeout."""
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=100, max_chars=10)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        # "hello" is 5 chars, two of them = 10 chars -> triggers flush
        for text in ["hello", "world"]:
            ctx = _make_coalescing_ctx(prompt=text)
            await compose([coalesce, handler], ctx)

        assert dispatched == ["hello\nworld"]

    @pytest.mark.asyncio
    async def test_independent_sessions_coalesce_separately(self) -> None:
        """Two different session_keys are coalesced independently."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[tuple[str, str]] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append((ctx.session_key, ctx.prompt))

        coalesce = make_coalescing_middleware(cfg)

        ctx_a = _make_coalescing_ctx(session_key="session:a", prompt="a1")
        await compose([coalesce, handler], ctx_a)

        ctx_b = _make_coalescing_ctx(session_key="session:b", prompt="b1")
        await compose([coalesce, handler], ctx_b)

        ctx_a2 = _make_coalescing_ctx(session_key="session:a", prompt="a2")
        await compose([coalesce, handler], ctx_a2)

        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)

        # Both sessions should have flushed independently
        assert len(dispatched) == 2
        keys = {k for k, _ in dispatched}
        assert keys == {"session:a", "session:b"}
        # Session a got both messages
        a_prompt = next(p for k, p in dispatched if k == "session:a")
        assert a_prompt == "a1\na2"
        # Session b got its single message
        b_prompt = next(p for k, p in dispatched if k == "session:b")
        assert b_prompt == "b1"

    @pytest.mark.asyncio
    async def test_compose_with_auth_and_coalesce(self) -> None:
        """Middleware works inside compose() with auth + coalesce + handler."""
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=2, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)
            await next_fn()

        auth = make_auth_middleware(allowed_users={456})
        coalesce = make_coalescing_middleware(cfg)

        # First message — goes into buffer
        ctx1 = _make_coalescing_ctx(prompt="first")
        await compose([auth, coalesce, handler], ctx1)

        # Second message — triggers flush (max_parts=2)
        ctx2 = _make_coalescing_ctx(prompt="second")
        await compose([auth, coalesce, handler], ctx2)

        assert dispatched == ["first\nsecond"]

    @pytest.mark.asyncio
    async def test_buffer_cleaned_after_flush(self) -> None:
        """After flush, next message starts a new buffer."""
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=2, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        # First batch — 2 messages -> immediate flush
        for text in ["a", "b"]:
            ctx = _make_coalescing_ctx(prompt=text)
            await compose([coalesce, handler], ctx)

        assert dispatched == ["a\nb"]

        # Second batch — should start fresh
        for text in ["c", "d"]:
            ctx = _make_coalescing_ctx(prompt=text)
            await compose([coalesce, handler], ctx)

        assert dispatched == ["a\nb", "c\nd"]

    @pytest.mark.asyncio
    async def test_handler_exception_propagates_on_immediate_flush(self) -> None:
        """If next_fn raises during immediate flush, exception propagates."""
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=2, max_chars=10_000)

        async def failing_handler(ctx: Any, _next_fn: NextFn) -> None:
            raise RuntimeError("handler boom")

        coalesce = make_coalescing_middleware(cfg)

        ctx1 = _make_coalescing_ctx(prompt="a")
        await compose([coalesce, failing_handler], ctx1)

        ctx2 = _make_coalescing_ctx(prompt="b")
        with pytest.raises(RuntimeError, match="handler boom"):
            await compose([coalesce, failing_handler], ctx2)

    @pytest.mark.asyncio
    async def test_handler_exception_on_timer_flush_is_logged(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """If next_fn raises during timer flush, the error is logged."""
        import logging

        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        exception_seen = asyncio.Event()

        async def failing_handler(ctx: Any, _next_fn: NextFn) -> None:
            exception_seen.set()
            raise RuntimeError("timer boom")

        coalesce = make_coalescing_middleware(cfg)

        ctx = _make_coalescing_ctx(prompt="hello")
        with caplog.at_level(logging.ERROR, logger="rai_agent.daemon.middleware"):
            await compose([coalesce, failing_handler], ctx)
            # Wait for timer flush
            await asyncio.wait_for(exception_seen.wait(), timeout=1.0)
            # Give the logger time to capture
            await asyncio.sleep(0.01)

        assert "Coalescing flush failed" in caplog.text
        assert "timer boom" in caplog.text


# ── Coalescing integration tests ──────────────────────────────────────────


class TestCoalescingIntegration:
    """Per-provider config, edge cases, and full pipeline integration."""

    @pytest.mark.asyncio
    async def test_two_instances_with_different_configs(self) -> None:
        """Two middleware instances with different configs (per-provider)."""
        fast_cfg = CoalescingConfig(window_seconds=10.0, max_parts=2, max_chars=10_000)
        slow_cfg = CoalescingConfig(window_seconds=10.0, max_parts=3, max_chars=10_000)
        fast_dispatched: list[str] = []
        slow_dispatched: list[str] = []

        async def fast_handler(ctx: Any, _next_fn: NextFn) -> None:
            fast_dispatched.append(ctx.prompt)

        async def slow_handler(ctx: Any, _next_fn: NextFn) -> None:
            slow_dispatched.append(ctx.prompt)

        fast_mw = make_coalescing_middleware(fast_cfg)
        slow_mw = make_coalescing_middleware(slow_cfg)

        # Send 2 messages to fast — should flush immediately (max_parts=2)
        for text in ["f1", "f2"]:
            ctx = _make_coalescing_ctx(session_key="fast:session", prompt=text)
            await compose([fast_mw, fast_handler], ctx)

        assert fast_dispatched == ["f1\nf2"]

        # Send 2 messages to slow — should NOT flush yet (max_parts=3)
        for text in ["s1", "s2"]:
            ctx = _make_coalescing_ctx(session_key="slow:session", prompt=text)
            await compose([slow_mw, slow_handler], ctx)

        assert slow_dispatched == []

        # Third message to slow — now it flushes
        ctx = _make_coalescing_ctx(session_key="slow:session", prompt="s3")
        await compose([slow_mw, slow_handler], ctx)
        assert slow_dispatched == ["s1\ns2\ns3"]

    @pytest.mark.asyncio
    async def test_message_after_flush_starts_new_window(self) -> None:
        """A message arriving after flush starts a fresh coalescing window."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        # First message — buffered
        ctx1 = _make_coalescing_ctx(prompt="batch1")
        await compose([coalesce, handler], ctx1)

        # Wait for flush
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["batch1"]

        # New message after flush — should start new window
        ctx2 = _make_coalescing_ctx(prompt="batch2")
        await compose([coalesce, handler], ctx2)

        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["batch1", "batch2"]

    @pytest.mark.asyncio
    async def test_single_message_passes_unchanged(self) -> None:
        """A single message passes through with its text unchanged."""
        cfg = CoalescingConfig(window_seconds=0.05, max_parts=10, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        ctx = _make_coalescing_ctx(prompt="just one message")
        await compose([coalesce, handler], ctx)

        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert dispatched == ["just one message"]


# ── Image content_blocks tests (S7.5) ───────────────────────────────────────


class TestContentBlocksField:
    """Tests for the content_blocks field on MessageContext."""

    def test_default_is_none(self) -> None:
        ctx = _make_coalescing_ctx(prompt="text only")
        assert ctx.content_blocks is None

    def test_accepts_content_blocks(self) -> None:
        ctx = _make_coalescing_ctx(prompt="caption")
        ctx.content_blocks = [
            {"type": "image", "source": {"type": "base64"}},
            {"type": "text", "text": "caption"},
        ]
        assert ctx.content_blocks is not None
        assert len(ctx.content_blocks) == 2


class TestCoalescingBypassForImages:
    """D7: Coalescing middleware bypasses messages with content_blocks."""

    @pytest.mark.asyncio
    async def test_image_message_dispatched_immediately(self) -> None:
        """Messages with content_blocks bypass coalescing entirely."""
        cfg = CoalescingConfig(
            window_seconds=10.0,
            max_parts=10,
            max_chars=10_000,
        )
        dispatched: list[Any] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(
                (ctx.prompt, ctx.content_blocks),
            )

        coalesce = make_coalescing_middleware(cfg)
        ctx = _make_coalescing_ctx(prompt="what is this?")
        ctx.content_blocks = [
            {"type": "image", "source": {"type": "base64"}},
            {"type": "text", "text": "what is this?"},
        ]
        await compose([coalesce, handler], ctx)

        # Dispatched immediately — no waiting for timer
        assert len(dispatched) == 1
        prompt, blocks = dispatched[0]
        assert prompt == "what is this?"
        assert blocks is not None

    @pytest.mark.asyncio
    async def test_text_still_coalesced_after_image(self) -> None:
        """Text messages are still coalesced normally after an image."""
        cfg = CoalescingConfig(
            window_seconds=0.05,
            max_parts=10,
            max_chars=10_000,
        )
        dispatched: list[str] = []

        async def handler(ctx: Any, _next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)

        coalesce = make_coalescing_middleware(cfg)

        # Send image — dispatched immediately
        img_ctx = _make_coalescing_ctx(prompt="caption")
        img_ctx.content_blocks = [{"type": "image"}]
        await compose([coalesce, handler], img_ctx)
        assert len(dispatched) == 1

        # Send text — should be coalesced (not immediate)
        txt_ctx = _make_coalescing_ctx(prompt="hello")
        await compose([coalesce, handler], txt_ctx)
        # Not dispatched yet
        assert len(dispatched) == 1

        # Wait for coalescing window
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
        assert len(dispatched) == 2
        assert dispatched[1] == "hello"

    @pytest.mark.asyncio
    async def test_full_pipeline_auth_rate_limit_coalesce(self) -> None:
        """Full pipeline: auth -> rate_limit -> coalesce -> handler."""
        limiter = TokenBucketRateLimiter(max_tokens=10, refill_rate=0.0)
        cfg = CoalescingConfig(window_seconds=10.0, max_parts=2, max_chars=10_000)
        dispatched: list[str] = []

        async def handler(ctx: Any, next_fn: NextFn) -> None:
            dispatched.append(ctx.prompt)
            await next_fn()

        auth = make_auth_middleware(allowed_users={456})
        rate_limit = make_rate_limit_middleware(limiter)
        coalesce = make_coalescing_middleware(cfg)

        pipeline = [auth, rate_limit, coalesce, handler]

        ctx1 = _make_coalescing_ctx(prompt="msg1")
        await compose(pipeline, ctx1)

        ctx2 = _make_coalescing_ctx(prompt="msg2")
        await compose(pipeline, ctx2)

        assert dispatched == ["msg1\nmsg2"]

    @pytest.mark.asyncio
    async def test_existing_middleware_tests_still_pass(self) -> None:
        """Regression: auth and rate_limit still work correctly."""
        # Auth
        replies: list[str] = []
        ctx = _make_ctx(user_id=999, replies=replies)

        auth = make_auth_middleware(allowed_users={456})
        await compose([auth], ctx)
        assert replies == ["Not authorized."]

        # Rate limit
        limiter = TokenBucketRateLimiter(max_tokens=1, refill_rate=0.0)
        limiter.allow(456)
        replies2: list[str] = []
        ctx2 = _make_ctx(user_id=456, replies=replies2)
        rl = make_rate_limit_middleware(limiter)
        await compose([rl], ctx2)
        assert replies2 == ["Rate limit exceeded. Try again later."]


# ── dispatch middleware tests ────────────────────────────────────────────


class TestDispatchMiddleware:
    """Tests for make_dispatch_middleware factory."""

    @pytest.mark.asyncio
    async def test_dispatch_middleware_creates_request_and_dispatches(
        self,
    ) -> None:
        """Verify SessionRequest built from ctx and dispatched."""
        from unittest.mock import AsyncMock

        from rai_agent.daemon.middleware import make_dispatch_middleware
        from rai_agent.daemon.registry import Session, SessionKey

        # Mock dispatcher
        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()

        # Mock registry
        registry = AsyncMock()
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="Session 1",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd=".",
            status="open",
            created_at=now,
            last_active_at=now,
        )
        registry.get_current = AsyncMock(return_value=mock_session)

        mw = make_dispatch_middleware(dispatcher, registry, ".")

        ctx = _make_ctx()
        ctx.session_key = "telegram:default:dm:123"
        await compose([mw], ctx)

        registry.get_current.assert_called_once()
        call_key = registry.get_current.call_args[0][0]
        assert isinstance(call_key, SessionKey)
        assert call_key.provider == "telegram"

        dispatcher.dispatch.assert_called_once()
        request = dispatcher.dispatch.call_args[0][0]
        assert request.session_key == "telegram:default:dm:123"
        assert request.prompt == "hello rai"
        assert request.metadata["session"] is mock_session
        assert request.metadata["chat_id"] == "123"

    @pytest.mark.asyncio
    async def test_dispatch_middleware_handles_session_busy_error(
        self,
    ) -> None:
        """Verifies SessionBusyError leads to user-facing reply."""
        from unittest.mock import AsyncMock

        from rai_agent.daemon.dispatcher import SessionBusyError
        from rai_agent.daemon.middleware import make_dispatch_middleware
        from rai_agent.daemon.registry import Session

        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock(
            side_effect=SessionBusyError("telegram:default:dm:123")
        )

        registry = AsyncMock()
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="Session 1",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd=".",
            status="open",
            created_at=now,
            last_active_at=now,
        )
        registry.get_current = AsyncMock(return_value=mock_session)

        mw = make_dispatch_middleware(dispatcher, registry, ".")

        replies: list[str] = []
        ctx = _make_ctx(replies=replies)
        ctx.session_key = "telegram:default:dm:123"
        await compose([mw], ctx)

        assert any("queued" in r.lower() or "try again" in r.lower() for r in replies)

    @pytest.mark.asyncio
    async def test_dispatch_middleware_calls_get_current_then_create(
        self,
    ) -> None:
        """Verify registry.get_current called; create_named if None."""
        from unittest.mock import AsyncMock

        from rai_agent.daemon.middleware import make_dispatch_middleware
        from rai_agent.daemon.registry import Session, SessionKey

        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()

        registry = AsyncMock()
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="Session 1",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd="/home/user/project",
            status="open",
            created_at=now,
            last_active_at=now,
        )
        # get_current returns None -> create_named should be called
        registry.get_current = AsyncMock(return_value=None)
        registry.create_named = AsyncMock(return_value=mock_session)

        mw = make_dispatch_middleware(
            dispatcher,
            registry,
            "/home/user/project",
        )

        ctx = _make_ctx()
        ctx.session_key = "telegram:default:dm:123"
        await compose([mw], ctx)

        registry.get_current.assert_called_once_with(
            SessionKey.parse("telegram:default:dm:123"),
        )
        registry.create_named.assert_called_once_with(
            SessionKey.parse("telegram:default:dm:123"),
            cwd="/home/user/project",
        )


# ── Command middleware tests ──────────────────────────────────────────────


def _make_command_ctx(
    *,
    prompt: str = "hello",
    user_id: int = 456,
    replies: list[str] | None = None,
    session_key: str = "telegram:default:dm:123",
) -> MessageContext:
    """Create a MessageContext for command middleware tests."""
    captured: list[str] = replies if replies is not None else []

    async def mock_reply(text: str) -> None:
        captured.append(text)

    return MessageContext(
        session_key=session_key,
        provider="telegram",
        account="default",
        scope="dm",
        channel_id="123",
        user_id=user_id,
        prompt=prompt,
        reply_text=mock_reply,
    )


# ── Session command middleware tests ─────────────────────────────────────


class TestSessionCommandMiddleware:
    """Tests for make_session_command_middleware factory."""

    @pytest.mark.asyncio
    async def test_bare_session_shows_help(self) -> None:
        """Bare /session shows help text listing subcommands."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(prompt="/session", replies=replies)
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "new" in replies[0].lower()
        assert "list" in replies[0].lower()
        assert "switch" in replies[0].lower()
        assert "close" in replies[0].lower()
        assert "delete" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_unknown_subcommand_shows_error(self) -> None:
        """/session unknown replies with error message."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session foobar",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "unknown" in replies[0].lower()
        assert "foobar" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_non_session_command_passes_through(self) -> None:
        """Unknown /foo command passes through to next middleware."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        next_called: list[bool] = []

        async def track_next() -> None:
            next_called.append(True)

        ctx = _make_command_ctx(prompt="/other")
        await mw(ctx, track_next)

        assert next_called == [True]

    @pytest.mark.asyncio
    async def test_regular_text_passes_through(self) -> None:
        """Regular text passes through to next middleware."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        next_called: list[bool] = []

        async def track_next() -> None:
            next_called.append(True)

        ctx = _make_command_ctx(prompt="hello world")
        await mw(ctx, track_next)

        assert next_called == [True]

    # ── /session new ──────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_new_with_name(self) -> None:
        """/session new MyChat creates session with given name."""
        from datetime import UTC, datetime

        from rai_agent.daemon.middleware import make_session_command_middleware
        from rai_agent.daemon.registry import Session

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="MyChat",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd="/tmp",
            status="open",
            is_current=True,
            created_at=now,
            last_active_at=now,
        )

        registry = AsyncMock()
        registry.create_named = AsyncMock(return_value=mock_session)
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session new MyChat",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        registry.create_named.assert_called_once()
        assert len(replies) == 1
        assert "mychat" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_new_without_name(self) -> None:
        """/session new creates session with auto-name."""
        from datetime import UTC, datetime

        from rai_agent.daemon.middleware import make_session_command_middleware
        from rai_agent.daemon.registry import Session

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="Session 1",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd="/tmp",
            status="open",
            is_current=True,
            created_at=now,
            last_active_at=now,
        )

        registry = AsyncMock()
        registry.create_named = AsyncMock(return_value=mock_session)
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session new",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        # name=None means auto-naming
        call_kwargs = registry.create_named.call_args
        assert call_kwargs[1].get("name") is None
        assert len(replies) == 1

    @pytest.mark.asyncio
    async def test_new_at_limit(self) -> None:
        """/session new when max_sessions exceeded replies error."""
        from rai_agent.daemon.middleware import make_session_command_middleware
        from rai_agent.daemon.registry import SessionLimitError

        registry = AsyncMock()
        registry.create_named = AsyncMock(
            side_effect=SessionLimitError("Session limit reached (10)"),
        )
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session new overflow",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "limit" in replies[0].lower()

    # ── /session list ──────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_list_with_sessions(self) -> None:
        """/session list shows sessions with name, tokens, active marker."""
        from datetime import UTC, datetime

        from rai_agent.daemon.middleware import make_session_command_middleware
        from rai_agent.daemon.registry import Session

        now = datetime.now(UTC)
        sessions = [
            Session(
                id=1,
                session_key="telegram:default:dm:123",
                name="Work",
                provider="telegram",
                account="default",
                scope="dm",
                channel_id="123",
                sdk_session_id=None,
                cwd=".",
                status="open",
                is_current=True,
                created_at=now,
                last_active_at=now,
                last_input_tokens=45000,
            ),
            Session(
                id=2,
                session_key="telegram:default:dm:123",
                name="Research",
                provider="telegram",
                account="default",
                scope="dm",
                channel_id="123",
                sdk_session_id=None,
                cwd=".",
                status="open",
                is_current=False,
                created_at=now,
                last_active_at=now,
                last_input_tokens=12000,
            ),
        ]

        registry = AsyncMock()
        registry.list_named = AsyncMock(return_value=sessions)
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session list",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        reply = replies[0]
        assert "Work" in reply
        assert "Research" in reply
        assert "45k" in reply
        assert "12k" in reply
        # Active marker on Work
        assert "*" in reply

    @pytest.mark.asyncio
    async def test_list_empty(self) -> None:
        """/session list with no sessions replies 'No sessions'."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.list_named = AsyncMock(return_value=[])
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session list",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "no sessions" in replies[0].lower()

    # ── /session switch ───────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_switch_by_name(self) -> None:
        """/session switch MyChat switches and replies confirmation."""
        from datetime import UTC, datetime

        from rai_agent.daemon.middleware import make_session_command_middleware
        from rai_agent.daemon.registry import Session

        now = datetime.now(UTC)
        mock_session = Session(
            id=1,
            session_key="telegram:default:dm:123",
            name="MyChat",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="123",
            sdk_session_id=None,
            cwd=".",
            status="open",
            is_current=True,
            created_at=now,
            last_active_at=now,
        )

        registry = AsyncMock()
        registry.switch_to = AsyncMock(return_value=mock_session)
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session switch MyChat",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        registry.switch_to.assert_called_once()
        assert len(replies) == 1
        assert "switched" in replies[0].lower()
        assert "mychat" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_switch_missing_arg(self) -> None:
        """/session switch without arg replies usage error."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session switch",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "usage" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_switch_not_found(self) -> None:
        """/session switch NonExistent replies 'not found'."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.switch_to = AsyncMock(
            side_effect=KeyError("Session 'NonExistent' not found"),
        )
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session switch NonExistent",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "not found" in replies[0].lower()

    # ── /session close ────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_close_current(self) -> None:
        """/session close closes the current session."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.close_named = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session close",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        registry.close_named.assert_called_once()
        # Called with name=None (close current)
        call_kwargs = registry.close_named.call_args
        assert call_kwargs[1].get("name") is None
        assert len(replies) == 1
        assert "closed" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_close_by_name(self) -> None:
        """/session close MyChat closes the named session."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.close_named = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session close MyChat",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        registry.close_named.assert_called_once()
        call_kwargs = registry.close_named.call_args
        assert call_kwargs[1].get("name") == "MyChat"
        assert len(replies) == 1
        assert "closed" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_close_not_found(self) -> None:
        """/session close on nonexistent session replies error."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.close_named = AsyncMock(
            side_effect=KeyError("No current session"),
        )
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session close",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "not found" in replies[0].lower()

    # ── /session delete ───────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_delete_by_name(self) -> None:
        """/session delete MyChat deletes the named session."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.delete_named = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session delete MyChat",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        registry.delete_named.assert_called_once()
        assert len(replies) == 1
        assert "deleted" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_delete_missing_arg(self) -> None:
        """/session delete without arg replies usage error."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session delete",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "usage" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_delete_current_session_error(self) -> None:
        """/session delete on current session replies 'switch first'."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.delete_named = AsyncMock(
            side_effect=ValueError(
                "Cannot delete the current active session",
            ),
        )
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session delete Current",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "switch" in replies[0].lower()

    @pytest.mark.asyncio
    async def test_delete_not_found(self) -> None:
        """/session delete NonExistent replies 'not found'."""
        from rai_agent.daemon.middleware import make_session_command_middleware

        registry = AsyncMock()
        registry.delete_named = AsyncMock(
            side_effect=KeyError("Session 'NonExistent' not found"),
        )
        mw = make_session_command_middleware(registry, "/tmp")

        replies: list[str] = []
        ctx = _make_command_ctx(
            prompt="/session delete NonExistent",
            replies=replies,
        )
        await mw(ctx, AsyncMock())

        assert len(replies) == 1
        assert "not found" in replies[0].lower()
