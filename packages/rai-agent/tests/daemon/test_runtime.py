"""Tests for runtime.py — RunConfig, RaiAgentRuntime, ClaudeRuntime, _to_event_frame."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    TextBlock,
    UserMessage,
)

from rai_agent.daemon.protocol import EventFrame
from rai_agent.daemon.runtime import (
    ClaudeRuntime,
    RunConfig,
    _to_event_frame,  # pyright: ignore[reportPrivateUsage]
)

# ─── RunConfig ────────────────────────────────────────────────────────────────


class TestRunConfig:
    def test_minimal_config(self) -> None:
        config = RunConfig(prompt="hello")
        assert config.prompt == "hello"
        assert config.session_id is None
        assert config.system_prompt is None
        assert config.permission_mode is None
        # S2.6 fields default to None
        assert config.max_turns is None
        assert config.skills is None
        assert config.memory_paths is None
        assert config.sensitive_patterns is None

    def test_full_config(self) -> None:
        config = RunConfig(
            prompt="hello",
            session_id="ses-abc",
            system_prompt="You are helpful.",
            permission_mode="bypassPermissions",
            max_turns=10,
            skills=["daily-briefing"],
            memory_paths=["CLAUDE.md"],
            sensitive_patterns=["Bash"],
        )
        assert config.session_id == "ses-abc"
        assert config.permission_mode == "bypassPermissions"
        assert config.max_turns == 10
        assert config.skills == ["daily-briefing"]
        assert config.memory_paths == ["CLAUDE.md"]
        assert config.sensitive_patterns == ["Bash"]

    def test_cwd_defaults_to_none(self) -> None:
        config = RunConfig(prompt="hello")
        assert config.cwd is None

    def test_cwd_accepts_value(self) -> None:
        config = RunConfig(prompt="hello", cwd="/tmp/project")
        assert config.cwd == "/tmp/project"

    def test_invalid_permission_mode_rejected(self) -> None:
        with pytest.raises(ValueError):
            RunConfig(prompt="x", permission_mode="invalid")  # type: ignore[arg-type]


# ─── _to_event_frame ─────────────────────────────────────────────────────────


class TestToEventFrame:
    def test_assistant_message(self) -> None:
        msg = AssistantMessage(
            content=[TextBlock(text="hi")], model="claude-3-5-sonnet"
        )
        frame = _to_event_frame(msg, seq=0)
        assert isinstance(frame, EventFrame)
        assert frame.event == "assistant_message"
        assert frame.seq == 0
        assert frame.payload["content"] == [{"text": "hi"}]
        assert frame.payload["model"] == "claude-3-5-sonnet"

    def test_user_message(self) -> None:
        msg = UserMessage(content="user says hi")
        frame = _to_event_frame(msg, seq=1)
        assert frame.event == "user_message"
        assert frame.seq == 1
        assert frame.payload["content"] == "user says hi"

    def test_result_message(self) -> None:
        msg = ResultMessage(
            subtype="success",
            duration_ms=500,
            duration_api_ms=400,
            is_error=False,
            num_turns=2,
            session_id="ses-xyz",
            stop_reason="end_turn",
            total_cost_usd=0.002,
        )
        frame = _to_event_frame(msg, seq=5)
        assert frame.event == "result"
        assert frame.seq == 5
        assert frame.payload["session_id"] == "ses-xyz"
        assert frame.payload["is_error"] is False
        assert frame.payload["total_cost_usd"] == pytest.approx(0.002)  # type: ignore[reportUnknownMemberType]

    def test_stream_event(self) -> None:
        msg = StreamEvent(
            uuid="u1", session_id="s1", event={"type": "content_block_delta"}
        )
        frame = _to_event_frame(msg, seq=2)
        assert frame.event == "sdk_event"
        assert frame.seq == 2
        assert frame.payload["type"] == "StreamEvent"

    def test_system_message(self) -> None:
        msg = SystemMessage(subtype="init", data={"key": "val"})
        frame = _to_event_frame(msg, seq=3)
        assert frame.event == "sdk_event"
        assert frame.payload["type"] == "SystemMessage"

    def test_frame_is_json_serializable(self) -> None:
        msg = AssistantMessage(content=[TextBlock(text="test")], model="claude")
        frame = _to_event_frame(msg, seq=0)
        # Must round-trip through JSON without error
        serialized = frame.model_dump_json()
        parsed = json.loads(serialized)
        assert parsed["event"] == "assistant_message"


# ─── ClaudeRuntime ────────────────────────────────────────────────────────────


def _make_sdk_messages(
    *,
    session_id: str = "ses-test",
    text: str = "Paris",
) -> list[Any]:
    """Minimal realistic SDK message sequence for a one-turn run."""
    return [
        AssistantMessage(content=[TextBlock(text=text)], model="claude-3-5-sonnet"),
        ResultMessage(
            subtype="success",
            duration_ms=100,
            duration_api_ms=80,
            is_error=False,
            num_turns=1,
            session_id=session_id,
            stop_reason="end_turn",
            total_cost_usd=0.001,
        ),
    ]


async def _async_gen(items: list[Any]):  # type: ignore[return]
    for item in items:
        yield item


class TestClaudeRuntime:
    async def test_run_sends_event_frames(self) -> None:
        """run() streams EventFrames for each SDK message."""
        sent: list[str] = []

        async def capture(text: str) -> None:
            sent.append(text)

        messages = _make_sdk_messages(session_id="ses-abc", text="Paris")

        with patch("rai_agent.daemon.runtime.query") as mock_query:
            mock_query.return_value = _async_gen(messages)
            runtime = ClaudeRuntime()
            session_id = await runtime.run(
                RunConfig(prompt="capital of France?"), capture
            )

        assert len(sent) == 2  # AssistantMessage + ResultMessage
        first = json.loads(sent[0])
        assert first["event"] == "assistant_message"
        assert first["payload"]["content"][0]["text"] == "Paris"
        last = json.loads(sent[-1])
        assert last["event"] == "result"
        assert last["payload"]["session_id"] == "ses-abc"
        assert session_id.session_id == "ses-abc"

    async def test_run_returns_session_id_from_result_message(self) -> None:
        """run() returns the session_id extracted from ResultMessage."""
        messages = _make_sdk_messages(session_id="ses-xyz")

        with patch("rai_agent.daemon.runtime.query") as mock_query:
            mock_query.return_value = _async_gen(messages)
            runtime = ClaudeRuntime()
            result = await runtime.run(RunConfig(prompt="test"), AsyncMock())

        assert result.session_id == "ses-xyz"

    async def test_run_returns_none_when_no_result_message(self) -> None:
        """run() returns None session_id if no ResultMessage."""
        messages = [AssistantMessage(content=[TextBlock(text="hi")], model="m")]

        with patch("rai_agent.daemon.runtime.query") as mock_query:
            mock_query.return_value = _async_gen(messages)
            runtime = ClaudeRuntime()
            result = await runtime.run(RunConfig(prompt="test"), AsyncMock())

        assert result.session_id is None
        assert result.input_tokens == 0

    async def test_resume_passes_session_id_to_options(self) -> None:
        """resume() passes options.resume=session_id to the SDK."""
        messages = _make_sdk_messages(session_id="ses-resumed")
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        with patch("rai_agent.daemon.runtime.query", side_effect=mock_query_factory):
            runtime = ClaudeRuntime()
            result = await runtime.resume(
                RunConfig(prompt="continue"), "ses-previous", AsyncMock()
            )

        assert result.session_id == "ses-resumed"
        assert len(captured_options) == 1
        assert captured_options[0].resume == "ses-previous"

    async def test_system_prompt_passed_to_options(self) -> None:
        """system_prompt in RunConfig is forwarded to ClaudeAgentOptions."""
        messages = _make_sdk_messages()
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        with patch("rai_agent.daemon.runtime.query", side_effect=mock_query_factory):
            runtime = ClaudeRuntime()
            await runtime.run(
                RunConfig(prompt="test", system_prompt="You are Rai."), AsyncMock()
            )

        assert captured_options[0].system_prompt == "You are Rai."

    async def test_no_governance_preserves_behavior(self) -> None:
        """ClaudeRuntime() without governance has no hooks dict."""
        messages = _make_sdk_messages()
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query_factory,
        ):
            runtime = ClaudeRuntime()
            await runtime.run(RunConfig(prompt="test"), AsyncMock())

        assert captured_options[0].hooks is None

    @pytest.mark.skip(
        reason="BUG(RAI-29): hooks disabled — SDK ProcessTransport crash on shutdown"
    )
    async def test_governance_builds_hooks_dict(self) -> None:
        """ClaudeRuntime with governance builds hooks dict."""
        from rai_agent.daemon.governance import GovernanceHooks

        messages = _make_sdk_messages()
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="bypassPermissions",
        )
        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query_factory,
        ):
            runtime = ClaudeRuntime(governance=hooks)
            await runtime.run(RunConfig(prompt="test"), AsyncMock())

        opts = captured_options[0]
        assert opts.hooks is not None
        assert "PreToolUse" in opts.hooks
        assert "PostToolUse" in opts.hooks
        assert "Stop" in opts.hooks
        # Each entry is a list of HookMatcher
        assert len(opts.hooks["PreToolUse"]) == 1
        assert len(opts.hooks["PreToolUse"][0].hooks) == 1

    async def test_max_turns_passed_to_options(self) -> None:
        """max_turns in RunConfig is forwarded to SDK options."""
        messages = _make_sdk_messages()
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query_factory,
        ):
            runtime = ClaudeRuntime()
            await runtime.run(
                RunConfig(prompt="test", max_turns=20),
                AsyncMock(),
            )

        assert captured_options[0].max_turns == 20

    async def test_build_options_prefers_config_cwd_over_instance(
        self,
    ) -> None:
        """_build_options uses config.cwd when set, ignoring self._cwd."""
        runtime = ClaudeRuntime(cwd="/default/dir")
        config = RunConfig(prompt="test", cwd="/override/dir")
        options = await runtime._build_options(config)  # pyright: ignore[reportPrivateUsage]
        assert options.cwd == "/override/dir"

    async def test_build_options_falls_back_to_instance_cwd(
        self,
    ) -> None:
        """_build_options uses self._cwd when config.cwd is None."""
        runtime = ClaudeRuntime(cwd="/default/dir")
        config = RunConfig(prompt="test")
        options = await runtime._build_options(config)  # pyright: ignore[reportPrivateUsage]
        assert options.cwd == "/default/dir"

    async def test_build_options_cwd_none_when_both_none(self) -> None:
        """_build_options returns cwd=None when neither is set."""
        runtime = ClaudeRuntime()
        config = RunConfig(prompt="test")
        options = await runtime._build_options(config)  # pyright: ignore[reportPrivateUsage]
        assert options.cwd is None

    async def test_assembler_builds_system_prompt(self, tmp_path: Any) -> None:
        """ClaudeRuntime with assembler builds system_prompt."""
        from rai_agent.daemon.governance import PromptAssembler

        # Create memory file
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("Project rules here.")

        messages = _make_sdk_messages()
        captured_options: list[Any] = []

        def mock_query_factory(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured_options.append(kwargs["options"])
            return _async_gen(messages)

        assembler = PromptAssembler(project_root=tmp_path)
        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query_factory,
        ):
            runtime = ClaudeRuntime(assembler=assembler)
            await runtime.run(
                RunConfig(
                    prompt="test",
                    memory_paths=["CLAUDE.md"],
                ),
                AsyncMock(),
            )

        assert "Project rules here." in (captured_options[0].system_prompt or "")
