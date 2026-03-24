# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Integration tests for TelegramTrigger middleware pipeline."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from rai_agent.daemon.dispatcher import (
    SessionDispatcher,
    SessionRequest,
)
from rai_agent.daemon.middleware import CoalescingConfig, MessageContext, compose
from rai_agent.daemon.registry import Session, SessionKey
from rai_agent.daemon.telegram import TelegramTrigger
from rai_agent.daemon.triggers import RaiTrigger


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


def _make_update(
    *,
    user_id: int,
    chat_id: int = 100,
    text: str = "hello",
) -> MagicMock:
    """Create a mock PTB Update."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = user_id
    update.message = AsyncMock()
    update.message.text = text
    update.message.chat_id = chat_id
    update.message.reply_text = AsyncMock()
    return update


def _make_session(
    key: str = "telegram:default:dm:100",
    sdk_session_id: str | None = None,
) -> Session:
    """Create a test Session."""
    now = datetime.now(UTC)
    parsed = SessionKey.parse(key)
    return Session(
        id=1,
        session_key=key,
        name="Session 1",
        provider=parsed.provider,
        account=parsed.account,
        scope=parsed.scope,
        channel_id=parsed.channel_id,
        sdk_session_id=sdk_session_id,
        cwd=".",
        status="open",
        created_at=now,
        last_active_at=now,
    )


# ─── Protocol compliance ──────────────────────────────────────────────


class TestTelegramTriggerProtocol:
    """TelegramTrigger RaiTrigger Protocol conformance."""

    def test_satisfies_rai_trigger_protocol(self) -> None:
        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={12345},
            dispatcher=AsyncMock(),
            registry=AsyncMock(),
            handler=MagicMock(),
        )
        assert isinstance(trigger, RaiTrigger)


# ─── Trigger middleware pipeline tests ────────────────────────────────


class TestTriggerMiddlewarePipeline:
    """TelegramTrigger builds and composes middleware pipeline."""

    @pytest.mark.asyncio
    async def test_handle_message_builds_context_and_composes(
        self,
    ) -> None:
        """_handle_message builds MessageContext and composes."""
        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()
        registry = AsyncMock()
        registry.get_current = AsyncMock(
            return_value=_make_session(),
        )
        handler = MagicMock()
        handler.handle = AsyncMock()

        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={67890},
            dispatcher=dispatcher,
            registry=registry,
            handler=handler,
            coalescing_config=CoalescingConfig(max_parts=1),
        )

        update = _make_update(
            user_id=67890,
            chat_id=100,
            text="test msg",
        )
        context = MagicMock()
        await trigger._handle_message(update, context)

        dispatcher.dispatch.assert_called_once()
        request = dispatcher.dispatch.call_args[0][0]
        assert request.prompt == "test msg"
        assert request.session_key == "telegram:default:dm:100"

    @pytest.mark.asyncio
    async def test_pipeline_has_5_middlewares(self) -> None:
        """Pipeline: [auth, rate_limit, coalesce, command, dispatch]."""
        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={12345},
            dispatcher=AsyncMock(),
            registry=AsyncMock(),
            handler=MagicMock(),
        )
        assert len(trigger._pipeline) == 5  # noqa: PLR2004

    @pytest.mark.asyncio
    async def test_no_eventbus_emit(self) -> None:
        """EventBus.emit is NOT called by _handle_message."""
        from rai_agent.daemon import events

        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()
        registry = AsyncMock()
        registry.get_current = AsyncMock(
            return_value=_make_session(),
        )
        handler = MagicMock()
        handler.handle = AsyncMock()

        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={67890},
            dispatcher=dispatcher,
            registry=registry,
            handler=handler,
            coalescing_config=CoalescingConfig(max_parts=1),
        )

        update = _make_update(user_id=67890, chat_id=100)
        context = MagicMock()

        received: list[Any] = []
        bus = events.get_bus()
        bus.on(  # pyright: ignore[reportUnknownMemberType]
            "TelegramRunEvent",
            lambda e: received.append(e),  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
        )

        await trigger._handle_message(update, context)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_unauthorized_user_rejected(self) -> None:
        """Unauthorized user gets rejection, no dispatch."""
        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()

        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={67890},
            dispatcher=dispatcher,
            registry=AsyncMock(),
            handler=MagicMock(),
        )

        update = _make_update(user_id=99999, text="hack")
        context = MagicMock()
        await trigger._handle_message(update, context)

        dispatcher.dispatch.assert_not_called()
        update.message.reply_text.assert_called_once_with(
            "Not authorized.",
        )

    @pytest.mark.asyncio
    async def test_rate_limited_user_rejected(self) -> None:
        """Rate-limited user gets rejection, no dispatch."""
        dispatcher = AsyncMock()
        dispatcher.dispatch = AsyncMock()
        registry = AsyncMock()
        registry.get_current = AsyncMock(
            return_value=_make_session(),
        )

        trigger = TelegramTrigger(
            bot_token="fake-token",
            allowed_users={67890},
            max_tokens=1,
            refill_rate=0.0,
            dispatcher=dispatcher,
            registry=registry,
            handler=MagicMock(),
            coalescing_config=CoalescingConfig(max_parts=1),
        )
        context = MagicMock()

        update1 = _make_update(user_id=67890, text="msg 1")
        await trigger._handle_message(update1, context)

        update2 = _make_update(user_id=67890, text="msg 2")
        await trigger._handle_message(update2, context)

        assert dispatcher.dispatch.call_count == 1
        update2.message.reply_text.assert_called_once_with(
            "Rate limit exceeded. Try again later.",
        )


# ─── Full pipeline integration tests ─────────────────────────────────


class TestFullPipelineIntegration:
    """End-to-end: MessageContext -> compose -> dispatcher -> handler."""

    @pytest.mark.asyncio
    async def test_message_flows_through_full_pipeline(
        self,
    ) -> None:
        """Full pipeline: ctx -> middlewares -> dispatcher -> handler."""
        from rai_agent.daemon.middleware import (
            make_auth_middleware,
            make_coalescing_middleware,
            make_dispatch_middleware,
            make_rate_limit_middleware,
        )
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        handler_called: list[SessionRequest] = []

        async def mock_handler(request: SessionRequest) -> None:
            handler_called.append(request)

        dispatcher = SessionDispatcher(handler=mock_handler)
        registry = AsyncMock()
        registry.get_current = AsyncMock(
            return_value=_make_session(),
        )
        limiter = TokenBucketRateLimiter(
            max_tokens=10,
            refill_rate=0.0,
        )

        pipeline = [
            make_auth_middleware({42}),
            make_rate_limit_middleware(limiter),
            make_coalescing_middleware(
                CoalescingConfig(max_parts=1),
            ),
            make_dispatch_middleware(dispatcher, registry, "."),
        ]

        async def _reply(text: str) -> None:
            pass

        ctx = MessageContext(
            session_key="telegram:default:dm:100",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="100",
            user_id=42,
            prompt="hello from integration",
            reply_text=_reply,
        )

        await compose(pipeline, ctx)

        # Give dispatcher worker time to process
        await asyncio.sleep(0.1)

        assert len(handler_called) == 1
        assert handler_called[0].prompt == "hello from integration"

        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_fifo_ordering(self) -> None:
        """Two messages to same session processed sequentially."""
        processed_order: list[str] = []

        async def mock_handler(request: SessionRequest) -> None:
            processed_order.append(request.prompt)
            # Simulate some work
            await asyncio.sleep(0.05)

        dispatcher = SessionDispatcher(handler=mock_handler)
        registry = AsyncMock()
        registry.get_current = AsyncMock(
            return_value=_make_session(),
        )

        async def _noop() -> None:
            pass

        async def _on_error(exc: Exception) -> None:
            pass

        async def _send(text: str) -> None:
            pass

        r1 = SessionRequest(
            session_key="telegram:default:dm:100",
            prompt="first",
            send=_send,
            on_complete=_noop,
            on_error=_on_error,
        )
        r2 = SessionRequest(
            session_key="telegram:default:dm:100",
            prompt="second",
            send=_send,
            on_complete=_noop,
            on_error=_on_error,
        )

        await dispatcher.dispatch(r1)
        await dispatcher.dispatch(r2)

        # Wait for both to complete
        await asyncio.sleep(0.3)

        assert processed_order == ["first", "second"]

        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_backpressure_replies_to_user(self) -> None:
        """Fill queue -> SessionBusyError -> user reply."""
        from rai_agent.daemon.dispatcher import SessionBusyError

        # Gate to hold the handler so queue fills up
        gate = asyncio.Event()

        async def slow_handler(
            request: SessionRequest,
        ) -> None:
            await gate.wait()  # Block until released

        # maxsize=1: worker takes first, queue holds second
        dispatcher = SessionDispatcher(
            handler=slow_handler,
            maxsize=1,
        )

        async def _noop() -> None:
            pass

        async def _on_error(exc: Exception) -> None:
            pass

        async def _send(text: str) -> None:
            pass

        key = "telegram:default:dm:100"

        # First message: picked up by worker (blocked on gate)
        r1 = SessionRequest(
            session_key=key,
            prompt="msg 0",
            send=_send,
            on_complete=_noop,
            on_error=_on_error,
        )
        await dispatcher.dispatch(r1)
        await asyncio.sleep(0.05)  # Let worker start

        # Second message: fills the queue (maxsize=1)
        r2 = SessionRequest(
            session_key=key,
            prompt="msg 1",
            send=_send,
            on_complete=_noop,
            on_error=_on_error,
        )
        await dispatcher.dispatch(r2)

        # Third should raise SessionBusyError
        r3 = SessionRequest(
            session_key=key,
            prompt="overflow",
            send=_send,
            on_complete=_noop,
            on_error=_on_error,
        )
        with pytest.raises(SessionBusyError):
            await dispatcher.dispatch(r3)

        gate.set()
        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_auth_rejection_before_dispatch(self) -> None:
        """Unauthorized user never reaches handler."""
        from rai_agent.daemon.middleware import (
            make_auth_middleware,
            make_coalescing_middleware,
            make_dispatch_middleware,
            make_rate_limit_middleware,
        )
        from rai_agent.daemon.telegram import TokenBucketRateLimiter

        handler_called: list[SessionRequest] = []

        async def mock_handler(request: SessionRequest) -> None:
            handler_called.append(request)

        dispatcher = SessionDispatcher(handler=mock_handler)
        registry = AsyncMock()
        limiter = TokenBucketRateLimiter(
            max_tokens=10,
            refill_rate=0.0,
        )

        pipeline = [
            make_auth_middleware({42}),
            make_rate_limit_middleware(limiter),
            make_coalescing_middleware(
                CoalescingConfig(max_parts=1),
            ),
            make_dispatch_middleware(dispatcher, registry, "."),
        ]

        replies: list[str] = []

        async def _reply(text: str) -> None:
            replies.append(text)

        ctx = MessageContext(
            session_key="telegram:default:dm:100",
            provider="telegram",
            account="default",
            scope="dm",
            channel_id="100",
            user_id=999,  # Not in allowed set
            prompt="should not reach handler",
            reply_text=_reply,
        )

        await compose(pipeline, ctx)
        await asyncio.sleep(0.1)

        assert len(handler_called) == 0
        assert replies == ["Not authorized."]

        await dispatcher.shutdown()
