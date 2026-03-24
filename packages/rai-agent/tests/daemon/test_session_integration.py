"""Integration tests for multi-chat concurrent sessions.

Tests the full pipeline: auth -> rate_limit -> coalesce -> command -> dispatch,
using real components (SessionRegistry, SessionDispatcher, middleware compose)
and a FakeRuntime that replaces the SDK call layer.

S5.8: Multi-Chat Concurrent Sessions integration tests.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from rai_agent.daemon.dispatcher import SessionDispatcher, SessionRequest
from rai_agent.daemon.middleware import (
    CoalescingConfig,
    MessageContext,
    Middleware,
    compose,
    make_auth_middleware,
    make_coalescing_middleware,
    make_dispatch_middleware,
    make_rate_limit_middleware,
    make_session_command_middleware,
)
from rai_agent.daemon.registry import SessionKey, SessionRegistry
from rai_agent.daemon.runtime import RunConfig, RunResult
from rai_agent.daemon.telegram import TokenBucketRateLimiter

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path


# ── FakeRuntime ────────────────────────────────────────────────────────────


class FakeRuntime:
    """Test double satisfying RaiAgentRuntime protocol.

    Tracks calls per session_key, returns deterministic RunResult.
    Optionally gates execution via asyncio.Event for timing control.
    """

    def __init__(self, *, gate: asyncio.Event | None = None) -> None:
        self.run_calls: dict[str, list[str]] = {}
        self.resume_calls: dict[str, list[str]] = {}
        self._call_count: int = 0
        self._gate = gate

    async def run(
        self,
        config: RunConfig,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Execute a prompt. Tracks calls by session_key from config."""
        if self._gate is not None:
            await self._gate.wait()
        key = config.session_id or "unknown"
        self.run_calls.setdefault(key, []).append(config.prompt)
        self._call_count += 1
        sdk_sid = f"sdk-{key}-{self._call_count}"
        await send(f"reply: {config.prompt}")
        return RunResult(session_id=sdk_sid, input_tokens=100)

    async def resume(
        self,
        config: RunConfig,
        session_id: str,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Resume an existing session. Tracks calls by session_key."""
        if self._gate is not None:
            await self._gate.wait()
        key = config.session_id or "unknown"
        self.resume_calls.setdefault(key, []).append(config.prompt)
        self._call_count += 1
        await send(f"resumed: {config.prompt}")
        return RunResult(session_id=session_id, input_tokens=200)

    @property
    def total_run_count(self) -> int:
        return sum(len(v) for v in self.run_calls.values())

    @property
    def total_resume_count(self) -> int:
        return sum(len(v) for v in self.resume_calls.values())


# ── Integration handler ───────────────────────────────────────────────────


def make_integration_handler(
    runtime: FakeRuntime,
    registry: SessionRegistry,
) -> Callable[[SessionRequest], Awaitable[None]]:
    """Build a handler that wires FakeRuntime to SessionDispatcher.

    Mirrors TelegramHandler.handle logic but without Telegram-specific
    parts (DraftStreamer, bot, typing indicator).
    """

    async def handler(request: SessionRequest) -> None:
        session = request.metadata["session"]
        key = SessionKey.parse(request.session_key)

        existing_sid = session.sdk_session_id
        run_config = RunConfig(
            prompt=request.prompt,
            session_id=request.session_key,
            cwd=session.cwd,
        )

        if existing_sid is not None:
            result = await runtime.resume(
                run_config, existing_sid, request.send,
            )
        else:
            result = await runtime.run(run_config, request.send)

        if result.session_id is not None:
            await registry.update(
                key,
                sdk_session_id=result.session_id,
                input_tokens=result.input_tokens,
            )

    return handler


# ── Helper: build pipeline + send message ─────────────────────────────────


def _make_ctx(
    session_key: str,
    prompt: str,
    *,
    user_id: int = 1,
    replies: list[str] | None = None,
) -> MessageContext:
    """Build a MessageContext for testing."""
    parsed = SessionKey.parse(session_key)

    async def reply_text(text: str) -> None:
        if replies is not None:
            replies.append(text)

    return MessageContext(
        session_key=session_key,
        provider=parsed.provider,
        account=parsed.account,
        scope=parsed.scope,
        channel_id=parsed.channel_id,
        user_id=user_id,
        prompt=prompt,
        reply_text=reply_text,
    )


# ── T1: Smoke test ────────────────────────────────────────────────────────


class TestSmoke:
    async def test_smoke_single_message_through_pipeline(
        self, tmp_path: Path,
    ) -> None:
        """Single message through full pipeline: FakeRuntime.run() called once."""
        # Setup
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(handler=handler, idle_timeout=1.0)

        cwd = str(tmp_path)
        middlewares = [
            make_auth_middleware(allowed_users={1}),
            make_rate_limit_middleware(
                TokenBucketRateLimiter(max_tokens=10, refill_rate=10.0),
            ),
            make_coalescing_middleware(
                CoalescingConfig(window_seconds=0.05, max_parts=10),
            ),
            make_session_command_middleware(registry, cwd),
            make_dispatch_middleware(dispatcher, registry, cwd),
        ]

        replies: list[str] = []
        session_key = "telegram:default:dm:100"
        ctx = _make_ctx(session_key, "Hello world", replies=replies)

        # Act + Assert
        try:
            await compose(middlewares, ctx)

            # Wait for coalescing flush + dispatcher processing
            await asyncio.sleep(0.2)

            assert runtime.total_run_count == 1
            assert session_key in runtime.run_calls
            assert runtime.run_calls[session_key] == ["Hello world"]

            # Verify session persisted in registry
            key = SessionKey.parse(session_key)
            session = await registry.get_current(key)
            assert session is not None
            assert session.status == "open"
            assert session.sdk_session_id is not None
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── T2: Isolation + FIFO + Backpressure ───────────────────────────────────


def _build_pipeline(
    registry: SessionRegistry,
    dispatcher: SessionDispatcher,
    cwd: str,
    *,
    coalesce_window: float = 0.05,
) -> list[Middleware]:
    """Build the standard middleware pipeline for integration tests."""
    return [
        make_auth_middleware(allowed_users={1, 2, 3}),
        make_rate_limit_middleware(
            TokenBucketRateLimiter(max_tokens=100, refill_rate=100.0),
        ),
        make_coalescing_middleware(
            CoalescingConfig(
                window_seconds=coalesce_window, max_parts=10,
            ),
        ),
        make_session_command_middleware(registry, cwd),
        make_dispatch_middleware(dispatcher, registry, cwd),
    ]


class TestMultiChatIsolation:
    async def test_two_chats_no_context_leakage(
        self, tmp_path: Path,
    ) -> None:
        """Concurrent chats have independent sessions, no cross-talk."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        key_a = "telegram:default:dm:100"
        key_b = "telegram:default:dm:200"

        ctx_a = _make_ctx(key_a, "Hello from A")
        ctx_b = _make_ctx(key_b, "Hello from B")

        try:
            # Send both concurrently
            await asyncio.gather(
                compose(middlewares, ctx_a),
                compose(middlewares, ctx_b),
            )

            # Wait for coalescing + processing
            await asyncio.sleep(0.3)

            # Each chat got exactly one run call with its own prompt
            assert key_a in runtime.run_calls
            assert key_b in runtime.run_calls
            assert runtime.run_calls[key_a] == ["Hello from A"]
            assert runtime.run_calls[key_b] == ["Hello from B"]

            # Registry has independent sessions
            sess_a = await registry.get_current(SessionKey.parse(key_a))
            sess_b = await registry.get_current(SessionKey.parse(key_b))
            assert sess_a is not None
            assert sess_b is not None
            assert sess_a.sdk_session_id != sess_b.sdk_session_id
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_three_chats_concurrent(
        self, tmp_path: Path,
    ) -> None:
        """Scale test: 3 concurrent chats, each independent."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        keys = [
            f"telegram:default:dm:{i}" for i in range(300, 303)
        ]
        ctxs = [
            _make_ctx(k, f"msg from {k}") for k in keys
        ]

        try:
            await asyncio.gather(
                *[compose(middlewares, ctx) for ctx in ctxs],
            )
            await asyncio.sleep(0.3)

            # All 3 chats processed independently
            assert runtime.total_run_count == 3
            for k in keys:
                assert k in runtime.run_calls
                assert len(runtime.run_calls[k]) == 1

            # All sessions exist in registry
            for k in keys:
                s = await registry.get_current(SessionKey.parse(k))
                assert s is not None
        finally:
            await dispatcher.shutdown()
            await registry.close()


class TestFIFOOrdering:
    async def test_messages_processed_in_order_through_pipeline(
        self, tmp_path: Path,
    ) -> None:
        """FIFO: messages to same session processed in order."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)

        # Use max_parts=1 to flush immediately (no coalescing)
        middlewares = _build_pipeline(
            registry, dispatcher, cwd,
            coalesce_window=0.01,
        )

        key = "telegram:default:dm:400"

        try:
            # Send 3 messages sequentially with tiny delays
            # to ensure each gets its own coalescing window
            for prompt in ["A", "B", "C"]:
                ctx = _make_ctx(key, prompt)
                await compose(middlewares, ctx)
                # Small delay to let coalescing flush each individually
                await asyncio.sleep(0.05)

            # Wait for all processing
            await asyncio.sleep(0.3)

            # FakeRuntime tracks prompts per session key
            assert key in runtime.run_calls or key in runtime.resume_calls
            # First call is run(), subsequent are resume() because
            # the handler updates sdk_session_id
            all_prompts: list[str] = []
            all_prompts.extend(runtime.run_calls.get(key, []))
            all_prompts.extend(runtime.resume_calls.get(key, []))
            assert all_prompts == ["A", "B", "C"]
        finally:
            await dispatcher.shutdown()
            await registry.close()


class TestBackpressure:
    async def test_queue_full_replies_to_user(
        self, tmp_path: Path,
    ) -> None:
        """Backpressure: queue full sends reply to user."""
        gate = asyncio.Event()
        runtime = FakeRuntime(gate=gate)
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        # maxsize=1 so queue fills fast
        dispatcher = SessionDispatcher(
            handler=handler, maxsize=1, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        # No coalescing — direct dispatch
        middlewares = [
            make_auth_middleware(allowed_users={1}),
            make_dispatch_middleware(dispatcher, registry, cwd),
        ]

        key = "telegram:default:dm:500"
        replies: list[str] = []

        try:
            # First message: gets picked up by worker (blocked on gate)
            ctx1 = _make_ctx(key, "msg1")
            await compose(middlewares, ctx1)
            await asyncio.sleep(0.02)  # let worker pick it up

            # Second message: fills the queue (maxsize=1)
            ctx2 = _make_ctx(key, "msg2")
            await compose(middlewares, ctx2)

            # Third message: queue full -> should get backpressure reply
            ctx3 = _make_ctx(key, "msg3", replies=replies)
            await compose(middlewares, ctx3)

            # Verify backpressure reply
            assert any("queued" in r.lower() for r in replies)
        finally:
            # Unblock and cleanup
            gate.set()
            await asyncio.sleep(0.2)
            await dispatcher.shutdown()
            await registry.close()


# ── T3: Lifecycle tests ───────────────────────────────────────────────────


class TestCoalescing:
    async def test_rapid_messages_coalesced(
        self, tmp_path: Path,
    ) -> None:
        """Rapid messages within window coalesced into single dispatch."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(
            registry, dispatcher, cwd,
            coalesce_window=0.1,
        )

        key = "telegram:default:dm:600"

        try:
            # Send two messages rapidly (within coalescing window)
            ctx1 = _make_ctx(key, "Hello")
            ctx2 = _make_ctx(key, "World")
            await compose(middlewares, ctx1)
            await compose(middlewares, ctx2)

            # Wait for coalescing flush + processing
            await asyncio.sleep(0.4)

            # Should be coalesced into a single run call
            assert runtime.total_run_count == 1
            assert key in runtime.run_calls
            assert runtime.run_calls[key] == ["Hello\nWorld"]
        finally:
            await dispatcher.shutdown()
            await registry.close()



class TestSessionResumeAfterRestart:
    async def test_resume_after_registry_reopen(
        self, tmp_path: Path,
    ) -> None:
        """Close + reopen registry from same file; resume() called."""
        runtime = FakeRuntime()
        db_path = str(tmp_path / "test.db")
        registry = SessionRegistry(db_path=db_path)
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:800"

        try:
            # First message: creates session with sdk_session_id
            ctx1 = _make_ctx(key, "initial")
            await compose(middlewares, ctx1)
            await asyncio.sleep(0.3)

            session = await registry.get_current(SessionKey.parse(key))
            assert session is not None
            assert session.sdk_session_id is not None

            # Shutdown dispatcher + close registry (simulate restart)
            await dispatcher.shutdown()
            await registry.close()
        except BaseException:
            await dispatcher.shutdown()
            await registry.close()
            raise

        # Reopen from same SQLite file
        registry2 = SessionRegistry(db_path=db_path)
        await registry2.init()

        runtime2 = FakeRuntime()
        handler2 = make_integration_handler(runtime2, registry2)
        dispatcher2 = SessionDispatcher(
            handler=handler2, idle_timeout=1.0,
        )
        middlewares2 = _build_pipeline(
            registry2, dispatcher2, cwd,
        )

        try:
            # Second message: should call resume() because session exists
            ctx2 = _make_ctx(key, "after restart")
            await compose(middlewares2, ctx2)
            await asyncio.sleep(0.3)

            # resume() should be called (not run())
            assert runtime2.total_resume_count == 1
            assert runtime2.total_run_count == 0
            assert key in runtime2.resume_calls
            assert runtime2.resume_calls[key] == ["after restart"]
        finally:
            await dispatcher2.shutdown()
            await registry2.close()


class TestSessionSwitch:
    async def test_switch_via_session_command_middleware(
        self, tmp_path: Path,
    ) -> None:
        """'/session switch first' through pipeline switches to session by name."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:900"
        parsed_key = SessionKey.parse(key)

        try:
            # Create two sessions directly via registry
            await registry.create_named(parsed_key, name="first", cwd=cwd)
            await registry.create_named(parsed_key, name="second", cwd=cwd)

            # Current should be "second"
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "second"

            # Send /session switch first through the pipeline
            replies: list[str] = []
            ctx_switch = _make_ctx(
                key, "/session switch first", replies=replies,
            )
            await compose(middlewares, ctx_switch)
            await asyncio.sleep(0.1)

            # Verify user got confirmation reply
            assert any("switched" in r.lower() for r in replies)

            # Verify current switched to "first"
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "first"
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── T4: Provider-agnostic harness validation ──────────────────────────────


class TestProviderAgnosticHarness:
    async def test_harness_works_with_telegram_keys(
        self, tmp_path: Path,
    ) -> None:
        """Pipeline processes telegram:default:dm:X keys correctly."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:12345"
        ctx = _make_ctx(key, "telegram test")

        try:
            await compose(middlewares, ctx)
            await asyncio.sleep(0.3)

            # Verify processed
            assert runtime.total_run_count == 1
            assert key in runtime.run_calls

            # Verify session stored with correct provider fields
            session = await registry.get_current(SessionKey.parse(key))
            assert session is not None
            assert session.provider == "telegram"
            assert session.scope == "dm"
            assert session.channel_id == "12345"
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_harness_works_with_gchat_keys(
        self, tmp_path: Path,
    ) -> None:
        """Pipeline processes gchat:default:group:spaces/X keys."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        key = "gchat:default:group:spaces/ABC123"
        ctx = _make_ctx(key, "gchat test")

        try:
            await compose(middlewares, ctx)
            await asyncio.sleep(0.3)

            # Verify processed
            assert runtime.total_run_count == 1
            assert key in runtime.run_calls

            # Verify session with correct provider fields
            session = await registry.get_current(SessionKey.parse(key))
            assert session is not None
            assert session.provider == "gchat"
            assert session.scope == "group"
            assert session.channel_id == "spaces/ABC123"
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_different_providers_isolated(
        self, tmp_path: Path,
    ) -> None:
        """Telegram + GChat sessions are fully isolated."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_pipeline(registry, dispatcher, cwd)

        tg_key = "telegram:default:dm:999"
        gc_key = "gchat:default:group:spaces/XYZ"

        ctx_tg = _make_ctx(tg_key, "from telegram")
        ctx_gc = _make_ctx(gc_key, "from gchat")

        try:
            await asyncio.gather(
                compose(middlewares, ctx_tg),
                compose(middlewares, ctx_gc),
            )
            await asyncio.sleep(0.3)

            # Both processed independently
            assert runtime.total_run_count == 2
            assert tg_key in runtime.run_calls
            assert gc_key in runtime.run_calls
            assert runtime.run_calls[tg_key] == ["from telegram"]
            assert runtime.run_calls[gc_key] == ["from gchat"]

            # Independent sessions in registry
            tg_sess = await registry.get_current(SessionKey.parse(tg_key))
            gc_sess = await registry.get_current(SessionKey.parse(gc_key))
            assert tg_sess is not None
            assert gc_sess is not None
            assert tg_sess.provider == "telegram"
            assert gc_sess.provider == "gchat"
            assert tg_sess.sdk_session_id != gc_sess.sdk_session_id

            # Verify both sessions exist
            tg_list = await registry.list_named(SessionKey.parse(tg_key))
            gc_list = await registry.list_named(SessionKey.parse(gc_key))
            assert len(tg_list) == 1
            assert len(gc_list) == 1
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 Helpers ─────────────────────────────────────────────────────────


def _build_command_pipeline(
    registry: SessionRegistry,
    dispatcher: SessionDispatcher,
    cwd: str,
) -> list[Middleware]:
    """Build a pipeline for session command tests (no coalescing).

    Skips coalescing so /session commands execute synchronously within
    compose(), making reply assertions deterministic.
    """
    return [
        make_auth_middleware(allowed_users={1, 2, 3}),
        make_rate_limit_middleware(
            TokenBucketRateLimiter(max_tokens=100, refill_rate=100.0),
        ),
        make_session_command_middleware(registry, cwd),
        make_dispatch_middleware(dispatcher, registry, cwd),
    ]


# ── S6.4 T1: Multi-Session Create ────────────────────────────────────────


class TestMultiSessionCreate:
    async def test_create_three_sessions_last_is_current(
        self, tmp_path: Path,
    ) -> None:
        """Create 3 named sessions via /session new, last one is current."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1100"
        parsed_key = SessionKey.parse(key)

        try:
            # Create 3 named sessions through pipeline
            for name in ["alpha", "beta", "gamma"]:
                replies: list[str] = []
                ctx = _make_ctx(
                    key, f"/session new {name}", replies=replies,
                )
                await compose(middlewares, ctx)
                assert any("created" in r.lower() for r in replies)

            # All 3 exist in registry
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 3
            names = {s.name for s in sessions}
            assert names == {"alpha", "beta", "gamma"}

            # Last created is current
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "gamma"
            assert current.is_current is True

            # First two are not current
            non_current = [s for s in sessions if not s.is_current]
            assert len(non_current) == 2
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_create_auto_named_sessions(
        self, tmp_path: Path,
    ) -> None:
        """Create sessions without names, verify auto-naming."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1101"
        parsed_key = SessionKey.parse(key)

        try:
            for _ in range(2):
                replies: list[str] = []
                ctx = _make_ctx(key, "/session new", replies=replies)
                await compose(middlewares, ctx)
                assert any("created" in r.lower() for r in replies)

            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 2
            names = {s.name for s in sessions}
            assert names == {"Session 1", "Session 2"}
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_create_with_duplicate_name_rejected(
        self, tmp_path: Path,
    ) -> None:
        """Create session with duplicate name raises IntegrityError.

        The registry enforces UNIQUE(session_key, name) at the DB level.
        The middleware does not yet catch IntegrityError, so it propagates.
        This test documents that behavior.
        """
        import sqlite3

        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1102"
        parsed_key = SessionKey.parse(key)

        try:
            # Create first session
            replies1: list[str] = []
            ctx1 = _make_ctx(
                key, "/session new myname", replies=replies1,
            )
            await compose(middlewares, ctx1)
            assert any("created" in r.lower() for r in replies1)

            # Try duplicate — IntegrityError propagates (not yet handled)
            ctx2 = _make_ctx(key, "/session new myname")
            with pytest.raises(sqlite3.IntegrityError):
                await compose(middlewares, ctx2)

            # Only 1 session with that name
            sessions = await registry.list_named(parsed_key)
            names = [s.name for s in sessions]
            assert names.count("myname") == 1
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 T2: Multi-Session Switch ────────────────────────────────────────


class TestMultiSessionSwitch:
    async def test_switch_changes_current_session(
        self, tmp_path: Path,
    ) -> None:
        """Switch to a named session makes it current."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1200"
        parsed_key = SessionKey.parse(key)

        try:
            # Create two sessions
            ctx1 = _make_ctx(key, "/session new inbox")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new coding")
            await compose(middlewares, ctx2)

            # Current should be "coding" (last created)
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "coding"

            # Switch to inbox
            replies: list[str] = []
            ctx_switch = _make_ctx(
                key, "/session switch inbox", replies=replies,
            )
            await compose(middlewares, ctx_switch)

            # Verify switched
            assert any("switched" in r.lower() for r in replies)
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "inbox"
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_switch_routes_messages_to_new_session(
        self, tmp_path: Path,
    ) -> None:
        """After switching, messages route to the switched-to session."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1201"
        parsed_key = SessionKey.parse(key)

        try:
            # Create two sessions
            ctx1 = _make_ctx(key, "/session new first")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new second")
            await compose(middlewares, ctx2)

            # Send a message (goes to "second" — the current)
            ctx_msg1 = _make_ctx(key, "hello second")
            await compose(middlewares, ctx_msg1)
            await asyncio.sleep(0.1)

            # "second" should now have an sdk_session_id
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "second"
            second_sdk_id = current.sdk_session_id
            assert second_sdk_id is not None

            # Switch to "first"
            ctx_switch = _make_ctx(key, "/session switch first")
            await compose(middlewares, ctx_switch)

            # Send a message (goes to "first")
            ctx_msg2 = _make_ctx(key, "hello first")
            await compose(middlewares, ctx_msg2)
            await asyncio.sleep(0.1)

            # "first" should have its own sdk_session_id
            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "first"
            first_sdk_id = current.sdk_session_id
            assert first_sdk_id is not None

            # Different SDK sessions
            assert first_sdk_id != second_sdk_id
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_switch_to_nonexistent_session_replies_error(
        self, tmp_path: Path,
    ) -> None:
        """Switching to non-existent session gives error reply."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1202"

        try:
            # Create one session so the chat has context
            ctx1 = _make_ctx(key, "/session new exists")
            await compose(middlewares, ctx1)

            # Try to switch to non-existent
            replies: list[str] = []
            ctx_switch = _make_ctx(
                key, "/session switch ghost", replies=replies,
            )
            await compose(middlewares, ctx_switch)

            assert any("not found" in r.lower() for r in replies)
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 T3: Multi-Session Concurrent ────────────────────────────────────


class TestMultiSessionConcurrent:
    async def test_concurrent_sessions_have_distinct_sdk_ids(
        self, tmp_path: Path,
    ) -> None:
        """Two sessions in same chat have distinct SDK session IDs."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1300"
        parsed_key = SessionKey.parse(key)

        try:
            # Create session "a", send message
            ctx_new_a = _make_ctx(key, "/session new a")
            await compose(middlewares, ctx_new_a)

            ctx_msg_a = _make_ctx(key, "message to a")
            await compose(middlewares, ctx_msg_a)
            await asyncio.sleep(0.1)

            sess_a = await registry.get_current(parsed_key)
            assert sess_a is not None
            sdk_id_a = sess_a.sdk_session_id
            assert sdk_id_a is not None

            # Create session "b" (auto-switches), send message
            ctx_new_b = _make_ctx(key, "/session new b")
            await compose(middlewares, ctx_new_b)

            ctx_msg_b = _make_ctx(key, "message to b")
            await compose(middlewares, ctx_msg_b)
            await asyncio.sleep(0.1)

            sess_b = await registry.get_current(parsed_key)
            assert sess_b is not None
            sdk_id_b = sess_b.sdk_session_id
            assert sdk_id_b is not None

            # Distinct SDK IDs
            assert sdk_id_a != sdk_id_b
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_message_only_dispatched_to_active_session(
        self, tmp_path: Path,
    ) -> None:
        """Message dispatched only to the active session's SDK session."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1301"

        try:
            # Create two sessions
            ctx_new_a = _make_ctx(key, "/session new a")
            await compose(middlewares, ctx_new_a)
            ctx_new_b = _make_ctx(key, "/session new b")
            await compose(middlewares, ctx_new_b)

            # "b" is current — send a message
            ctx_msg = _make_ctx(key, "only for b")
            await compose(middlewares, ctx_msg)
            await asyncio.sleep(0.1)

            # Runtime should have exactly 1 run call
            assert runtime.total_run_count == 1
            assert key in runtime.run_calls
            assert runtime.run_calls[key] == ["only for b"]
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 T4: Multi-Session Limits ────────────────────────────────────────


class TestMultiSessionLimits:
    async def test_max_sessions_rejects_creation(
        self, tmp_path: Path,
    ) -> None:
        """Creating beyond max_sessions limit is rejected."""
        runtime = FakeRuntime()
        registry = SessionRegistry(
            db_path=str(tmp_path / "test.db"), max_sessions=2,
        )
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1400"
        parsed_key = SessionKey.parse(key)

        try:
            # Create 2 sessions (at limit)
            for name in ["one", "two"]:
                ctx = _make_ctx(key, f"/session new {name}")
                await compose(middlewares, ctx)

            # Attempt a 3rd
            replies: list[str] = []
            ctx_over = _make_ctx(
                key, "/session new three", replies=replies,
            )
            await compose(middlewares, ctx_over)

            # Should be rejected
            assert any("limit" in r.lower() for r in replies)

            # Still only 2 sessions
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 2
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_close_then_create_allows_new_session(
        self, tmp_path: Path,
    ) -> None:
        """After closing a session, a new one can be created within limit."""
        runtime = FakeRuntime()
        registry = SessionRegistry(
            db_path=str(tmp_path / "test.db"), max_sessions=2,
        )
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1401"
        parsed_key = SessionKey.parse(key)

        try:
            # Fill to limit
            ctx1 = _make_ctx(key, "/session new one")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new two")
            await compose(middlewares, ctx2)

            # Close "one"
            ctx_close = _make_ctx(key, "/session close one")
            await compose(middlewares, ctx_close)

            # Now create a new session — should succeed
            replies: list[str] = []
            ctx_new = _make_ctx(
                key, "/session new three", replies=replies,
            )
            await compose(middlewares, ctx_new)

            assert any("created" in r.lower() for r in replies)

            # 2 open sessions (two + three; one is closed)
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 2
            names = {s.name for s in sessions}
            assert names == {"two", "three"}
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 T5: Multi-Session Lifecycle ─────────────────────────────────────


class TestMultiSessionLifecycle:
    async def test_close_session_by_name(
        self, tmp_path: Path,
    ) -> None:
        """Close a specific session by name via /session close."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1500"
        parsed_key = SessionKey.parse(key)

        try:
            # Create two sessions
            ctx1 = _make_ctx(key, "/session new alpha")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new beta")
            await compose(middlewares, ctx2)

            # Close alpha by name
            replies: list[str] = []
            ctx_close = _make_ctx(
                key, "/session close alpha", replies=replies,
            )
            await compose(middlewares, ctx_close)

            assert any("closed" in r.lower() for r in replies)

            # Only beta remains in open list
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 1
            assert sessions[0].name == "beta"
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_delete_closed_session_not_found(
        self, tmp_path: Path,
    ) -> None:
        """Deleting a closed session replies 'not found'.

        The registry's _lookup filters by status='open', so a closed
        session is invisible to delete. This documents that behavior.
        """
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1501"

        try:
            # Create two sessions
            ctx1 = _make_ctx(key, "/session new alpha")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new beta")
            await compose(middlewares, ctx2)

            # Close alpha
            ctx_close = _make_ctx(key, "/session close alpha")
            await compose(middlewares, ctx_close)

            # Try to delete alpha (closed) — lookup won't find it
            replies: list[str] = []
            ctx_del = _make_ctx(
                key, "/session delete alpha", replies=replies,
            )
            await compose(middlewares, ctx_del)

            assert any("not found" in r.lower() for r in replies)
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_delete_active_session_rejected(
        self, tmp_path: Path,
    ) -> None:
        """Deleting the current active session is rejected."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1502"
        parsed_key = SessionKey.parse(key)

        try:
            # Create a session (it becomes current)
            ctx1 = _make_ctx(key, "/session new active")
            await compose(middlewares, ctx1)

            # Try to delete the current session
            replies: list[str] = []
            ctx_del = _make_ctx(
                key, "/session delete active", replies=replies,
            )
            await compose(middlewares, ctx_del)

            assert any("cannot delete" in r.lower() for r in replies)

            # Session still exists
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 1
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_close_then_switch_to_remaining(
        self, tmp_path: Path,
    ) -> None:
        """Close active session, switch to remaining one."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1503"
        parsed_key = SessionKey.parse(key)

        try:
            # Create two sessions
            ctx1 = _make_ctx(key, "/session new first")
            await compose(middlewares, ctx1)
            ctx2 = _make_ctx(key, "/session new second")
            await compose(middlewares, ctx2)

            # Close current (second)
            ctx_close = _make_ctx(key, "/session close")
            await compose(middlewares, ctx_close)

            # Switch to remaining (first)
            replies: list[str] = []
            ctx_switch = _make_ctx(
                key, "/session switch first", replies=replies,
            )
            await compose(middlewares, ctx_switch)

            assert any("switched" in r.lower() for r in replies)

            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.name == "first"
        finally:
            await dispatcher.shutdown()
            await registry.close()


# ── S6.4 T6: Multi-Session Auto-Create ───────────────────────────────────


class TestMultiSessionAutoCreate:
    async def test_fresh_chat_auto_creates_session(
        self, tmp_path: Path,
    ) -> None:
        """Regular message to empty chat auto-creates a named session."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1600"
        parsed_key = SessionKey.parse(key)

        try:
            # No sessions exist yet — send a regular message
            ctx = _make_ctx(key, "hello world")
            await compose(middlewares, ctx)
            await asyncio.sleep(0.1)

            # Session auto-created with name "Session 1"
            sessions = await registry.list_named(parsed_key)
            assert len(sessions) == 1
            assert sessions[0].name == "Session 1"

            # Message was dispatched
            assert runtime.total_run_count == 1
        finally:
            await dispatcher.shutdown()
            await registry.close()

    async def test_auto_created_session_is_current(
        self, tmp_path: Path,
    ) -> None:
        """Auto-created session is marked current with sdk_session_id."""
        runtime = FakeRuntime()
        registry = SessionRegistry(db_path=str(tmp_path / "test.db"))
        await registry.init()

        handler = make_integration_handler(runtime, registry)
        dispatcher = SessionDispatcher(
            handler=handler, idle_timeout=1.0,
        )
        cwd = str(tmp_path)
        middlewares = _build_command_pipeline(registry, dispatcher, cwd)

        key = "telegram:default:dm:1601"
        parsed_key = SessionKey.parse(key)

        try:
            ctx = _make_ctx(key, "auto create test")
            await compose(middlewares, ctx)
            await asyncio.sleep(0.1)

            current = await registry.get_current(parsed_key)
            assert current is not None
            assert current.is_current is True
            assert current.sdk_session_id is not None
            assert current.name == "Session 1"
        finally:
            await dispatcher.shutdown()
            await registry.close()
