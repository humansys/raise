# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for verbose pipeline logging — S4.4 (RAI-33).

Uses structlog.testing.capture_logs() for log assertion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

import structlog.testing
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from rai_agent.daemon.runtime import (
    _TOOL_RESULT_MAX_LEN,
    _log_sdk_message,
    _redact,
    _truncate,
)

if TYPE_CHECKING:
    import pytest

# ─── T2: _truncate() ─────────────────────────────────────────────────────────


class TestTruncate:
    """_truncate() caps text at configurable length with suffix."""

    def test_short_text_unchanged(self) -> None:
        assert _truncate("hello world") == "hello world"

    def test_long_text_with_suffix(self) -> None:
        text = "x" * 1000
        result = _truncate(text)
        assert result.startswith("x" * _TOOL_RESULT_MAX_LEN)
        assert result.endswith("... [truncated 500 chars]")

    def test_exact_boundary_unchanged(self) -> None:
        text = "x" * _TOOL_RESULT_MAX_LEN
        assert _truncate(text) == text


# ─── T2: _redact() ───────────────────────────────────────────────────────────


class TestRedact:
    """_redact() substitutes sensitive patterns with [REDACTED]."""

    def test_redact_anthropic_api_key(self) -> None:
        text = "key is sk-ant-abc123xyz789 here"
        result = _redact(text, frozenset())
        assert "sk-ant-" not in result
        assert "[REDACTED]" in result

    def test_redact_telegram_bot_token(self) -> None:
        text = "token bot123456:AAF_xxxyyyzzz end"
        result = _redact(text, frozenset())
        assert "bot123456:" not in result
        assert "[REDACTED]" in result

    def test_redact_bearer_token(self) -> None:
        text = "Authorization: Bearer eyJhbGciOi..."
        result = _redact(text, frozenset())
        assert "Bearer eyJ" not in result
        assert "[REDACTED]" in result

    def test_redact_custom_patterns(self) -> None:
        text = "my-secret-value-12345 is here"
        result = _redact(text, frozenset({"my-secret-"}))
        assert "my-secret-" not in result
        assert "[REDACTED]" in result

    def test_redact_preserves_safe_text(self) -> None:
        text = "this is perfectly safe text"
        assert _redact(text, frozenset()) == text


# ─── T3: _log_sdk_message() ──────────────────────────────────────────────────

_CONV_ID = "telegram:42"
_NO_PATTERNS: frozenset[str] = frozenset()


def _call_log(
    msg: Any,
    seq: int = 0,
    conv_id: str = _CONV_ID,
    patterns: frozenset[str] = _NO_PATTERNS,
) -> list[dict[str, Any]]:
    """Helper: call _log_sdk_message and return captured logs."""
    with structlog.testing.capture_logs() as logs:
        _log_sdk_message(
            msg,
            seq=seq,
            conversation_id=conv_id,
            sensitive_patterns=patterns,
        )
    return logs  # type: ignore[return-value]


class TestLogThinkingBlock:
    """AssistantMessage with ThinkingBlock -> event=llm.thinking."""

    def test_log_thinking_block(self) -> None:
        msg = AssistantMessage(
            content=[
                ThinkingBlock(
                    thinking="I need to check the file",
                    signature="sig",
                )
            ],
            model="claude-sonnet-4-20250514",
        )
        logs = _call_log(msg, seq=1)

        assert len(logs) == 1
        assert logs[0]["event"] == "llm.thinking"
        assert "I need to check" in logs[0]["content"]


class TestLogToolStart:
    """AssistantMessage with ToolUseBlock -> event=tool.start."""

    def test_log_tool_start(self) -> None:
        msg = AssistantMessage(
            content=[
                ToolUseBlock(
                    id="tu_123",
                    name="Bash",
                    input={"command": "ls"},
                )
            ],
            model="claude-sonnet-4-20250514",
        )
        logs = _call_log(msg, seq=2)

        assert len(logs) == 1
        assert logs[0]["event"] == "tool.start"
        assert logs[0]["tool_name"] == "Bash"
        assert "ls" in str(logs[0]["tool_input"])


class TestLogToolEnd:
    """UserMessage with ToolResultBlock -> event=tool.end."""

    def test_log_tool_end(self) -> None:
        msg = UserMessage(
            content=[
                ToolResultBlock(
                    tool_use_id="tu_123",
                    content="file1.py\nfile2.py",
                    is_error=False,
                ),
            ]
        )
        logs = _call_log(msg, seq=3)

        assert len(logs) == 1
        assert logs[0]["event"] == "tool.end"
        assert logs[0]["tool_use_id"] == "tu_123"
        assert logs[0]["is_error"] is False

    def test_log_tool_end_truncation(self) -> None:
        long_content = "x" * 1000
        msg = UserMessage(
            content=[
                ToolResultBlock(
                    tool_use_id="tu_456",
                    content=long_content,
                    is_error=False,
                ),
            ]
        )
        logs = _call_log(msg, seq=4)

        assert "truncated" in logs[0]["content"]


class TestLogMessageOut:
    """AssistantMessage with TextBlock -> event=message.out."""

    def test_log_message_out(self) -> None:
        msg = AssistantMessage(
            content=[TextBlock(text="Here is the answer")],
            model="claude-sonnet-4-20250514",
        )
        logs = _call_log(msg, seq=5)

        assert len(logs) == 1
        assert logs[0]["event"] == "message.out"
        assert "Here is the answer" in logs[0]["content"]


class TestLogUsage:
    """ResultMessage -> event=llm.usage with token counts and cost."""

    def test_log_usage(self) -> None:
        msg = ResultMessage(
            subtype="result",
            duration_ms=3000,
            duration_api_ms=2500,
            is_error=False,
            num_turns=2,
            session_id="sess_abc",
            stop_reason="end_turn",
            total_cost_usd=0.0123,
            usage={"input_tokens": 1200, "output_tokens": 340},
            result="done",
            structured_output=None,
        )
        logs = _call_log(msg, seq=6)

        assert len(logs) == 1
        assert logs[0]["event"] == "llm.usage"
        assert logs[0]["gen_ai_usage_input_tokens"] == 1200
        assert logs[0]["gen_ai_usage_output_tokens"] == 340
        assert logs[0]["duration_ms"] == 3000
        assert logs[0]["num_turns"] == 2
        assert logs[0]["cost_usd"] == "0.0123"


class TestOtelAttributes:
    """All log entries include gen_ai.* attributes."""

    def test_otel_attributes_present(self) -> None:
        msg = AssistantMessage(
            content=[TextBlock(text="test")],
            model="claude-sonnet-4-20250514",
        )
        logs = _call_log(msg, seq=0)

        log = logs[0]
        assert log["gen_ai.agent.name"] == "rai"
        assert log["gen_ai.conversation.id"] == _CONV_ID


# ─── T4: _stream() timing and opt-in guard ──────────────────────────────


def _make_result_message(
    session_id: str = "sess_test",
) -> ResultMessage:
    """Factory for a minimal ResultMessage."""
    return ResultMessage(
        subtype="result",
        duration_ms=1000,
        duration_api_ms=800,
        is_error=False,
        num_turns=1,
        session_id=session_id,
        stop_reason="end_turn",
        total_cost_usd=0.005,
        usage={"input_tokens": 100, "output_tokens": 50},
        result="ok",
        structured_output=None,
    )


class TestStreamTiming:
    """_stream() emits agent.start/agent.end when verbose=True."""

    async def test_agent_start_end_timing(self) -> None:
        """Verbose runtime emits agent.start and agent.end."""
        from unittest.mock import patch

        from rai_agent.daemon.runtime import ClaudeRuntime

        runtime = ClaudeRuntime(verbose=True)
        result_msg = _make_result_message()

        async def mock_query(
            **_kwargs: Any,
        ) -> Any:  # noqa: ANN401
            yield result_msg

        send = AsyncMock()

        with (
            patch(
                "rai_agent.daemon.runtime.query",
                mock_query,
            ),
            structlog.testing.capture_logs() as logs,
        ):
            await runtime._stream(
                "hello",
                None,  # type: ignore[arg-type]
                send,
                conversation_id="test:1",
            )

        events = [log["event"] for log in logs]
        assert "agent.start" in events
        assert "agent.end" in events

        end_log = next(log for log in logs if log["event"] == "agent.end")
        assert "duration_ms" in end_log
        assert isinstance(end_log["duration_ms"], int)
        assert "message_count" in end_log

    async def test_no_logging_when_verbose_false(self) -> None:
        """Non-verbose runtime produces zero log calls."""
        from unittest.mock import patch

        from rai_agent.daemon.runtime import ClaudeRuntime

        runtime = ClaudeRuntime(verbose=False)
        result_msg = _make_result_message()

        async def mock_query(
            **_kwargs: Any,
        ) -> Any:  # noqa: ANN401
            yield result_msg

        send = AsyncMock()

        with (
            patch(
                "rai_agent.daemon.runtime.query",
                mock_query,
            ),
            structlog.testing.capture_logs() as logs,
        ):
            await runtime._stream(
                "hello",
                None,  # type: ignore[arg-type]
                send,
            )

        assert len(logs) == 0


# ─── T5: Integration test — full pipeline run ───────────────────────────


class TestFullPipelineLogSequence:
    """End-to-end: mock SDK messages -> verify full log sequence."""

    async def test_full_pipeline_log_sequence(self) -> None:
        from unittest.mock import patch

        from rai_agent.daemon.runtime import ClaudeRuntime

        runtime = ClaudeRuntime(verbose=True)

        messages = [
            AssistantMessage(
                content=[
                    ThinkingBlock(
                        thinking="Let me check the files",
                        signature="sig1",
                    ),
                    ToolUseBlock(
                        id="tu_1",
                        name="Bash",
                        input={"command": "ls"},
                    ),
                ],
                model="claude-sonnet-4-20250514",
            ),
            UserMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="tu_1",
                        content="file1.py\nfile2.py",
                        is_error=False,
                    ),
                ]
            ),
            AssistantMessage(
                content=[TextBlock(text="I found 2 files.")],
                model="claude-sonnet-4-20250514",
            ),
            _make_result_message(),
        ]

        async def mock_query(
            **_kwargs: Any,
        ) -> Any:  # noqa: ANN401
            for m in messages:
                yield m

        send = AsyncMock()

        with (
            patch(
                "rai_agent.daemon.runtime.query",
                mock_query,
            ),
            structlog.testing.capture_logs() as logs,
        ):
            await runtime._stream(
                "check files",
                None,  # type: ignore[arg-type]
                send,
                conversation_id="test:full",
            )

        events = [log["event"] for log in logs]

        # Verify expected sequence
        assert events[0] == "agent.start"
        assert "llm.thinking" in events
        assert "tool.start" in events
        assert "tool.end" in events
        assert "message.out" in events
        assert "llm.usage" in events
        assert events[-1] == "agent.end"

        # Verify agent.end has timing info
        end_log = logs[-1]
        assert end_log["duration_ms"] >= 0
        assert end_log["message_count"] == 4

        # Verify all logs have OTel attributes
        for log in logs:
            assert log["gen_ai.agent.name"] == "rai"
            assert log["gen_ai.conversation.id"] == "test:full"

    async def test_redaction_in_pipeline(self) -> None:
        """Sensitive content in tool results is redacted."""
        from unittest.mock import patch

        from rai_agent.daemon.runtime import ClaudeRuntime

        runtime = ClaudeRuntime(verbose=True)
        runtime._sensitive_patterns = frozenset()

        messages = [
            UserMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="tu_1",
                        content="secret: sk-ant-abc123xyz789",
                        is_error=False,
                    ),
                ]
            ),
            _make_result_message(),
        ]

        async def mock_query(
            **_kwargs: Any,
        ) -> Any:  # noqa: ANN401
            for m in messages:
                yield m

        send = AsyncMock()

        with (
            patch(
                "rai_agent.daemon.runtime.query",
                mock_query,
            ),
            structlog.testing.capture_logs() as logs,
        ):
            await runtime._stream(
                "test",
                None,  # type: ignore[arg-type]
                send,
                conversation_id="test:redact",
            )

        tool_end_log = next(log for log in logs if log["event"] == "tool.end")
        assert "sk-ant-" not in tool_end_log["content"]
        assert "[REDACTED]" in tool_end_log["content"]


class TestVerboseConfigFromEnv:
    """Validate the full config-to-runtime path."""

    def test_verbose_config_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """RAI_DAEMON_VERBOSE_LOGGING=1 -> verbose_logging=True."""
        from rai_agent.daemon.config import DaemonConfig

        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_VERBOSE_LOGGING", "1")

        cfg = DaemonConfig()
        assert cfg.verbose_logging is True
