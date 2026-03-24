# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for TelegramHandler and named session routing."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from rai_agent.daemon.dispatcher import SessionRequest
from rai_agent.daemon.registry import Session, SessionKey


def _make_mock_bot() -> AsyncMock:
    """Create a mock Telegram Bot."""
    bot = AsyncMock()
    sent_msg = MagicMock()
    sent_msg.message_id = 42
    bot.send_message.return_value = sent_msg
    return bot


def _make_mock_runtime() -> AsyncMock:
    """Create a mock RaiAgentRuntime returning RunResult."""
    from rai_agent.daemon.runtime import RunResult

    runtime = AsyncMock()
    runtime.run = AsyncMock(
        return_value=RunResult(session_id="session-xyz"),
    )
    runtime.resume = AsyncMock(
        return_value=RunResult(session_id="session-xyz-2"),
    )
    return runtime


def _make_session(
    *,
    sdk_session_id: str | None = None,
    key: str = "telegram:default:dm:123",
) -> Session:
    """Create a Session for testing."""
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


def _make_request(
    *,
    prompt: str = "hello rai",
    session: Session | None = None,
    chat_id: str = "123",
    key: str = "telegram:default:dm:123",
) -> SessionRequest:
    """Create a SessionRequest for testing."""
    if session is None:
        session = _make_session(key=key)

    async def _noop() -> None:
        pass

    async def _on_error(exc: Exception) -> None:
        pass

    return SessionRequest(
        session_key=key,
        prompt=prompt,
        send=AsyncMock(),
        on_complete=_noop,
        on_error=_on_error,
        metadata={"session": session, "chat_id": chat_id},
    )


# ─── RunResult ───────────────────────────────────────────────────────


class TestRunResult:
    """RunResult dataclass from runtime."""

    def test_run_result_defaults_zero_tokens(self) -> None:
        """RunResult() defaults input_tokens=0."""
        from rai_agent.daemon.runtime import RunResult

        result = RunResult()
        assert result.session_id is None
        assert result.input_tokens == 0

    def test_run_result_captures_input_tokens(self) -> None:
        """RunResult with explicit input_tokens."""
        from rai_agent.daemon.runtime import RunResult

        result = RunResult(
            session_id="abc-123", input_tokens=150000,
        )
        assert result.session_id == "abc-123"
        assert result.input_tokens == 150000


# ─── TelegramHandler ──────────────────────────────────────────────────


class TestTelegramHandlerHandle:
    """TelegramHandler.handle processes SessionRequests."""

    @pytest.mark.asyncio
    async def test_handle_runs_runtime_and_persists_session(
        self,
    ) -> None:
        """runtime.run() called, registry.update() called."""
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        runtime.run.assert_called_once()
        call_args = runtime.run.call_args
        assert call_args[0][0].prompt == "hello rai"

        registry.update.assert_called_once()
        update_args = registry.update.call_args
        assert update_args[0][0] == SessionKey.parse(
            "telegram:default:dm:123",
        )
        assert update_args[1]["sdk_session_id"] == "session-xyz"

    @pytest.mark.asyncio
    async def test_handle_resumes_existing_session(self) -> None:
        """When session has sdk_session_id, runtime.resume() is used."""
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session(sdk_session_id="existing-sid")
        request = _make_request(
            prompt="follow up", session=session,
        )

        await handler.handle(request)

        runtime.resume.assert_called_once()
        resume_args = runtime.resume.call_args[0]
        assert resume_args[0].prompt == "follow up"
        assert resume_args[1] == "existing-sid"
        runtime.run.assert_not_called()

    @pytest.mark.asyncio
    async def test_new_command_passes_through_to_runtime(self) -> None:
        """/new is NOT intercepted by TelegramHandler — passes to runtime."""
        from unittest.mock import patch

        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session(sdk_session_id=None)
        request = _make_request(prompt="/new", session=session)

        with patch(
            "rai_agent.daemon.telegram_pipeline.DraftStreamer",
        ) as mock_streamer_cls:
            mock_streamer = AsyncMock()
            mock_streamer_cls.return_value = mock_streamer
            await handler.handle(request)

        # /new should NOT be intercepted — runtime.run should be called
        runtime.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_streams_to_draft_streamer(self) -> None:
        """DraftStreamer receives text chunks from runtime."""
        from unittest.mock import patch

        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        mock_streamer = MagicMock()
        mock_streamer.append = AsyncMock()
        mock_streamer.flush = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        with patch(
            "rai_agent.daemon.telegram_pipeline.DraftStreamer",
            return_value=mock_streamer,
        ):
            await handler.handle(request)

        mock_streamer.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handle_passes_session_cwd_to_run_config_on_run(
        self,
    ) -> None:
        """RunConfig gets session.cwd when calling runtime.run()."""
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        session.cwd = "/projects/myapp"
        request = _make_request(session=session)

        await handler.handle(request)

        runtime.run.assert_called_once()
        run_config = runtime.run.call_args[0][0]
        assert run_config.cwd == "/projects/myapp"

    @pytest.mark.asyncio
    async def test_handle_passes_session_cwd_to_run_config_on_resume(
        self,
    ) -> None:
        """RunConfig gets session.cwd when calling runtime.resume()."""
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session(sdk_session_id="existing-sid")
        session.cwd = "/projects/other"
        request = _make_request(
            prompt="follow up", session=session,
        )

        await handler.handle(request)

        runtime.resume.assert_called_once()
        run_config = runtime.resume.call_args[0][0]
        assert run_config.cwd == "/projects/other"


# ─── Token tracking + context suggestion ──────────────────────────────


class TestTelegramHandlerTokenTracking:
    """TelegramHandler tracks input_tokens and suggests context window."""

    @pytest.mark.asyncio
    async def test_handler_updates_input_tokens(self) -> None:
        """After runtime returns RunResult, registry.update gets tokens."""
        from rai_agent.daemon.runtime import RunResult
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(
            return_value=RunResult(
                session_id="x", input_tokens=140000,
            ),
        )
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        registry.update.assert_called_once()
        update_kwargs = registry.update.call_args[1]
        assert update_kwargs["input_tokens"] == 140000

    @pytest.mark.asyncio
    async def test_handler_context_suggestion_at_75_percent(
        self,
    ) -> None:
        """When input_tokens >= 75% of 200k, suggestion is sent."""
        from rai_agent.daemon.runtime import RunResult
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(
            return_value=RunResult(
                session_id="x", input_tokens=155000,
            ),
        )
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        send_mock: AsyncMock = request.send  # type: ignore[assignment]
        calls = [str(c) for c in send_mock.call_args_list]
        suggestion_sent = any("77%" in c for c in calls)
        assert suggestion_sent, (
            f"Expected 77% suggestion, got calls: {calls}"
        )

    @pytest.mark.asyncio
    async def test_handler_no_suggestion_below_75_percent(
        self,
    ) -> None:
        """No suggestion when input_tokens < 75% of 200k."""
        from rai_agent.daemon.runtime import RunResult
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(
            return_value=RunResult(
                session_id="x", input_tokens=140000,
            ),
        )
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        send_mock: AsyncMock = request.send  # type: ignore[assignment]
        calls = [str(c) for c in send_mock.call_args_list]
        suggestion_sent = any("Context" in c for c in calls)
        assert not suggestion_sent

    @pytest.mark.asyncio
    async def test_handler_no_suggestion_for_zero_tokens(
        self,
    ) -> None:
        """No suggestion when input_tokens=0."""
        from rai_agent.daemon.runtime import RunResult
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(
            return_value=RunResult(session_id="x", input_tokens=0),
        )
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        send_mock: AsyncMock = request.send  # type: ignore[assignment]
        calls = [str(c) for c in send_mock.call_args_list]
        suggestion_sent = any("Context" in c for c in calls)
        assert not suggestion_sent


# ─── Named Session Routing ────────────────────────────────────────────


class TestNamedSessionRouting:
    """Verify TelegramHandler routes via named sessions."""

    @pytest.mark.asyncio
    async def test_context_suggestion_mentions_session_new(self) -> None:
        """Context window suggestion includes /session new."""
        from rai_agent.daemon.runtime import RunResult
        from rai_agent.daemon.telegram_pipeline import TelegramHandler

        runtime = _make_mock_runtime()
        runtime.run = AsyncMock(
            return_value=RunResult(
                session_id="x", input_tokens=160000,
            ),
        )
        bot = _make_mock_bot()
        registry = AsyncMock()
        registry.update = AsyncMock()

        handler = TelegramHandler(
            runtime=runtime, bot=bot, registry=registry,
        )
        session = _make_session()
        request = _make_request(session=session)

        await handler.handle(request)

        send_mock: AsyncMock = request.send  # type: ignore[assignment]
        calls = [str(c) for c in send_mock.call_args_list]
        assert any("/session new" in c for c in calls), (
            f"Expected /session new in suggestion, got: {calls}"
        )
