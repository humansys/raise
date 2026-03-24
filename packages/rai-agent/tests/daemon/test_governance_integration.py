# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Integration tests for governance pipeline.

Verifies GovernanceHooks + PromptAssembler + ClaudeRuntime wiring
produces correct SDK options for real agent dispatch.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from claude_agent_sdk import HookMatcher
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

from rai_agent.daemon.governance import (
    GovernanceHooks,
    PromptAssembler,
)
from rai_agent.daemon.runtime import ClaudeRuntime, RunConfig


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


def _make_sdk_messages(
    session_id: str = "ses-int",
) -> list[Any]:
    """Minimal SDK message sequence."""
    return [
        AssistantMessage(
            content=[TextBlock(text="ok")],
            model="claude-3-5-sonnet",
        ),
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


class TestGovernanceIntegration:
    """Full pipeline: GovernanceHooks + ClaudeRuntime."""

    @pytest.mark.skip(
        reason="BUG(RAI-29): hooks disabled — SDK ProcessTransport crash on shutdown"
    )
    async def test_hooks_dict_has_correct_structure(
        self,
    ) -> None:
        """SDK options.hooks has HookMatcher for each event."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write"],
            permission_mode="default",
        )
        captured: list[Any] = []

        def mock_query(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured.append(kwargs["options"])
            return _async_gen(_make_sdk_messages())

        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query,
        ):
            runtime = ClaudeRuntime(governance=hooks)
            await runtime.run(
                RunConfig(prompt="test"), AsyncMock()
            )

        opts = captured[0]
        assert opts.hooks is not None
        for event_name in ("PreToolUse", "PostToolUse", "Stop"):
            matchers = opts.hooks[event_name]
            assert len(matchers) == 1
            assert isinstance(matchers[0], HookMatcher)
            assert len(matchers[0].hooks) == 1
            assert callable(matchers[0].hooks[0])

    async def test_assembler_plus_runtime(
        self, tmp_path: Any
    ) -> None:
        """PromptAssembler + RunConfig with skills/memory → prompt."""
        # Set up files
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("# Rai Rules\nAlways be concise.")
        skill_dir = (
            tmp_path / ".raise" / "skills" / "daily-briefing"
        )
        skill_dir.mkdir(parents=True)
        (skill_dir / "prompt.md").write_text(
            "Generate a morning briefing."
        )

        captured: list[Any] = []

        def mock_query(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured.append(kwargs["options"])
            return _async_gen(_make_sdk_messages())

        assembler = PromptAssembler(project_root=tmp_path)
        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query,
        ):
            runtime = ClaudeRuntime(assembler=assembler)
            await runtime.run(
                RunConfig(
                    prompt="briefing",
                    skills=["daily-briefing"],
                    memory_paths=["CLAUDE.md"],
                ),
                AsyncMock(),
            )

        prompt = captured[0].system_prompt
        assert prompt is not None
        assert "Rai Rules" in prompt
        assert "daily-briefing" in prompt
        assert "morning briefing" in prompt

    @pytest.mark.skip(
        reason="BUG(RAI-29): hooks disabled — SDK ProcessTransport crash on shutdown"
    )
    async def test_full_pipeline_options(
        self, tmp_path: Any
    ) -> None:
        """Full pipeline: governance + assembler + max_turns."""
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("Memory content.")

        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write", "Edit"],
            permission_mode="bypassPermissions",
            max_turns=20,
        )
        assembler = PromptAssembler(project_root=tmp_path)
        captured: list[Any] = []

        def mock_query(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured.append(kwargs["options"])
            return _async_gen(_make_sdk_messages())

        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query,
        ):
            runtime = ClaudeRuntime(
                governance=hooks, assembler=assembler
            )
            await runtime.run(
                RunConfig(
                    prompt="Do the daily briefing",
                    permission_mode="bypassPermissions",
                    max_turns=20,
                    memory_paths=["CLAUDE.md"],
                ),
                AsyncMock(),
            )

        opts = captured[0]
        # Governance hooks wired
        assert opts.hooks is not None
        assert "PreToolUse" in opts.hooks
        # Max turns forwarded
        assert opts.max_turns == 20
        # System prompt assembled
        assert "Memory content." in (opts.system_prompt or "")
        # Permission mode forwarded
        assert opts.permission_mode == "bypassPermissions"

    async def test_backward_compat_no_governance(self) -> None:
        """No governance/assembler → identical to pre-S2.6 behavior."""
        captured: list[Any] = []

        def mock_query(**kwargs: Any):  # type: ignore[return]
            if "options" in kwargs:
                captured.append(kwargs["options"])
            return _async_gen(_make_sdk_messages())

        with patch(
            "rai_agent.daemon.runtime.query",
            side_effect=mock_query,
        ):
            runtime = ClaudeRuntime()
            await runtime.run(
                RunConfig(
                    prompt="hello",
                    system_prompt="You are Rai.",
                ),
                AsyncMock(),
            )

        opts = captured[0]
        assert opts.hooks is None
        assert opts.system_prompt == "You are Rai."
        assert opts.max_turns is None
        assert opts.permission_mode == "bypassPermissions"

    async def test_governance_hooks_deny_sensitive_tool(
        self,
    ) -> None:
        """GovernanceHooks PreToolUse denies sensitive tool in test."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=0.1,
        )
        input_data = {
            "hook_event_name": "PreToolUse",
            "session_id": "ses-test",
            "transcript_path": "/tmp/t",
            "cwd": "/tmp",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
            "tool_use_id": "tu-1",
        }
        result = await hooks.pre_tool_use(
            input_data, "tu-1", {"signal": None}
        )
        assert (
            result["hookSpecificOutput"]["permissionDecision"]
            == "deny"
        )

    async def test_governance_stop_enforces_turn_limit(
        self,
    ) -> None:
        """GovernanceHooks Stop halts after max_turns."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="bypassPermissions",
            max_turns=3,
        )
        post_input: dict[str, Any] = {
            "hook_event_name": "PostToolUse",
            "session_id": "ses-test",
            "transcript_path": "/tmp/t",
            "cwd": "/tmp",
            "tool_name": "Read",
            "tool_input": {},
            "tool_response": "ok",
            "tool_use_id": "tu-1",
        }
        for _ in range(3):
            await hooks.post_tool_use(
                post_input, "tu-x", {"signal": None}
            )

        stop_input = {
            "hook_event_name": "Stop",
            "session_id": "ses-test",
            "transcript_path": "/tmp/t",
            "cwd": "/tmp",
            "stop_hook_active": True,
        }
        result = await hooks.stop(
            stop_input, None, {"signal": None}
        )
        assert result["continue_"] is False
        assert "3/3" in result["stopReason"]
