"""Tests for SessionDispatcher — SessionRequest, backpressure, FIFO, workers."""

from __future__ import annotations

from typing import Any

from rai_agent.daemon.dispatcher import (
    SessionBusyError,
    SessionDispatcher,
    SessionRequest,
)

# ── Helpers ─────────────────────────────────────────────────────────────────


async def _noop_send(text: str) -> None:
    pass


async def _noop_complete() -> None:
    pass


async def _noop_error(exc: Exception) -> None:
    pass


def _make_request(
    session_key: str = "tg:default:dm:123",
    prompt: str = "hello",
    **kwargs: Any,
) -> SessionRequest:
    return SessionRequest(
        session_key=session_key,
        prompt=prompt,
        send=kwargs.get("send", _noop_send),
        on_complete=kwargs.get("on_complete", _noop_complete),
        on_error=kwargs.get("on_error", _noop_error),
        metadata=kwargs.get("metadata", {}),
    )


# ── SessionRequest ──────────────────────────────────────────────────────────


class TestSessionRequest:
    def test_construction_all_fields(self) -> None:
        req = _make_request(prompt="test msg")
        assert req.session_key == "tg:default:dm:123"
        assert req.prompt == "test msg"
        assert req.send is _noop_send
        assert req.on_complete is _noop_complete
        assert req.on_error is _noop_error
        assert req.metadata == {}

    def test_metadata_defaults_to_empty(self) -> None:
        req = _make_request()
        assert req.metadata == {}

    def test_custom_metadata(self) -> None:
        req = _make_request(metadata={"chat_type": "group"})
        assert req.metadata == {"chat_type": "group"}


# ── SessionBusyError ────────────────────────────────────────────────────────


class TestSessionBusyError:
    def test_is_exception(self) -> None:
        assert issubclass(SessionBusyError, Exception)

    def test_carries_session_key(self) -> None:
        err = SessionBusyError("tg:default:dm:123")
        assert "tg:default:dm:123" in str(err)


# ── SessionDispatcher: dispatch + FIFO + lazy worker ────────────────────────


class TestDispatch:
    async def test_handler_called_with_request(self) -> None:
        received: list[SessionRequest] = []

        async def handler(req: SessionRequest) -> None:
            received.append(req)

        dispatcher = SessionDispatcher(handler=handler)
        req = _make_request()
        await dispatcher.dispatch(req)

        import asyncio

        await asyncio.sleep(0.05)

        assert len(received) == 1
        assert received[0].prompt == "hello"
        await dispatcher.shutdown()

    async def test_on_complete_called_on_success(self) -> None:
        completed: list[bool] = []

        async def handler(req: SessionRequest) -> None:
            pass  # success

        async def on_complete() -> None:
            completed.append(True)

        dispatcher = SessionDispatcher(handler=handler)
        req = _make_request(on_complete=on_complete)
        await dispatcher.dispatch(req)

        import asyncio

        await asyncio.sleep(0.05)

        assert completed == [True]
        await dispatcher.shutdown()

    async def test_fifo_order_within_session(self) -> None:
        order: list[str] = []

        async def handler(req: SessionRequest) -> None:
            import asyncio

            await asyncio.sleep(0.01)
            order.append(req.prompt)

        dispatcher = SessionDispatcher(handler=handler)
        for i in range(3):
            await dispatcher.dispatch(
                _make_request(prompt=f"msg-{i}"),
            )

        import asyncio

        await asyncio.sleep(0.15)

        assert order == ["msg-0", "msg-1", "msg-2"]
        await dispatcher.shutdown()

    async def test_independent_sessions(self) -> None:
        order: list[str] = []

        async def handler(req: SessionRequest) -> None:
            import asyncio

            await asyncio.sleep(0.01)
            order.append(f"{req.session_key}:{req.prompt}")

        dispatcher = SessionDispatcher(handler=handler)
        await dispatcher.dispatch(
            _make_request(session_key="a", prompt="a1"),
        )
        await dispatcher.dispatch(
            _make_request(session_key="b", prompt="b1"),
        )

        import asyncio

        await asyncio.sleep(0.1)

        # Both processed — order may interleave
        assert "a:a1" in order
        assert "b:b1" in order
        assert len(order) == 2
        await dispatcher.shutdown()

    async def test_creates_worker_lazily(self) -> None:
        async def handler(req: SessionRequest) -> None:
            pass

        dispatcher = SessionDispatcher(handler=handler)
        assert dispatcher.active_session_count == 0

        await dispatcher.dispatch(_make_request())

        assert dispatcher.active_session_count == 1
        await dispatcher.shutdown()


# ── Backpressure ────────────────────────────────────────────────────────────


class TestBackpressure:
    async def test_raises_when_queue_full(self) -> None:
        import asyncio

        # Handler that blocks forever so queue fills up
        block = asyncio.Event()

        async def slow_handler(req: SessionRequest) -> None:
            await block.wait()

        dispatcher = SessionDispatcher(
            handler=slow_handler,
            maxsize=2,
        )

        # First fills the worker, second and third fill the queue
        await dispatcher.dispatch(_make_request(prompt="1"))
        await asyncio.sleep(0.01)  # let worker pick up first
        await dispatcher.dispatch(_make_request(prompt="2"))
        await dispatcher.dispatch(_make_request(prompt="3"))

        # Fourth should raise — queue full
        import pytest

        with pytest.raises(SessionBusyError):
            await dispatcher.dispatch(_make_request(prompt="4"))

        block.set()
        await dispatcher.shutdown()


# ── on_error ────────────────────────────────────────────────────────────────


class TestOnError:
    async def test_on_error_called_when_handler_raises(self) -> None:
        errors: list[Exception] = []

        async def bad_handler(req: SessionRequest) -> None:
            msg = "boom"
            raise RuntimeError(msg)

        async def on_error(exc: Exception) -> None:
            errors.append(exc)

        dispatcher = SessionDispatcher(handler=bad_handler)
        await dispatcher.dispatch(
            _make_request(on_error=on_error),
        )

        import asyncio

        await asyncio.sleep(0.05)

        assert len(errors) == 1
        assert isinstance(errors[0], RuntimeError)
        assert str(errors[0]) == "boom"
        await dispatcher.shutdown()

    async def test_worker_continues_after_error(self) -> None:
        """Worker doesn't die on handler exception — processes next."""
        results: list[str] = []

        async def handler(req: SessionRequest) -> None:
            if req.prompt == "bad":
                msg = "fail"
                raise RuntimeError(msg)
            results.append(req.prompt)

        dispatcher = SessionDispatcher(handler=handler)
        await dispatcher.dispatch(_make_request(prompt="bad"))
        await dispatcher.dispatch(_make_request(prompt="good"))

        import asyncio

        await asyncio.sleep(0.1)

        assert results == ["good"]
        await dispatcher.shutdown()

    async def test_worker_survives_on_error_failure(self) -> None:
        """C1: if on_error itself raises, worker must not crash."""
        import asyncio

        results: list[str] = []

        async def handler(req: SessionRequest) -> None:
            if req.prompt == "explode":
                msg = "handler fail"
                raise RuntimeError(msg)
            results.append(req.prompt)

        async def broken_on_error(exc: Exception) -> None:
            msg = "on_error also broken"
            raise RuntimeError(msg)

        dispatcher = SessionDispatcher(handler=handler)
        await dispatcher.dispatch(
            _make_request(prompt="explode", on_error=broken_on_error),
        )
        await dispatcher.dispatch(_make_request(prompt="after"))

        await asyncio.sleep(0.1)

        assert results == ["after"]
        await dispatcher.shutdown()


# ── Idle timeout ────────────────────────────────────────────────────────────


class TestIdleTimeout:
    async def test_worker_exits_after_timeout(self) -> None:
        async def handler(req: SessionRequest) -> None:
            pass

        dispatcher = SessionDispatcher(
            handler=handler,
            idle_timeout=0.1,
        )
        await dispatcher.dispatch(_make_request())

        import asyncio

        await asyncio.sleep(0.05)
        assert dispatcher.active_session_count == 1

        # Wait for idle timeout
        await asyncio.sleep(0.2)
        assert dispatcher.active_session_count == 0

    async def test_cleanup_removes_queue_and_worker(self) -> None:
        async def handler(req: SessionRequest) -> None:
            pass

        dispatcher = SessionDispatcher(
            handler=handler,
            idle_timeout=0.1,
        )
        await dispatcher.dispatch(_make_request())

        import asyncio

        await asyncio.sleep(0.3)

        assert dispatcher.active_session_count == 0
        # Queue also cleaned
        assert dispatcher.active_queue_count == 0


# ── Shutdown ────────────────────────────────────────────────────────────────


class TestShutdown:
    async def test_cancels_all_workers(self) -> None:
        import asyncio

        block = asyncio.Event()

        async def blocking_handler(req: SessionRequest) -> None:
            await block.wait()

        dispatcher = SessionDispatcher(handler=blocking_handler)
        await dispatcher.dispatch(
            _make_request(session_key="a"),
        )
        await dispatcher.dispatch(
            _make_request(session_key="b"),
        )

        await asyncio.sleep(0.02)
        assert dispatcher.active_session_count == 2

        await dispatcher.shutdown()
        assert dispatcher.active_session_count == 0

    async def test_shutdown_idempotent(self) -> None:
        async def handler(req: SessionRequest) -> None:
            pass

        dispatcher = SessionDispatcher(handler=handler)
        await dispatcher.shutdown()
        await dispatcher.shutdown()  # must not raise
