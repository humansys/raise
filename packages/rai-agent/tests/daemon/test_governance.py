# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for governance.py — GovernanceHooks, PromptAssembler, HITL events."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from rai_agent.daemon.governance import (
    GovernanceHooks,
    HitlApprovalRequest,
    HitlApprovalResponse,
    PromptAssembler,
)


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


# ─── PreToolUse ──────────────────────────────────────────────────────────────


class TestPreToolUseDeny:
    """PreToolUse denies sensitive tools in default mode."""

    async def test_denies_sensitive_tool_default_mode(self) -> None:
        """Bash matches sensitive_patterns → deny (HITL timeout)."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write", "Edit"],
            permission_mode="default",
            hitl_timeout=0.1,
        )
        input_data = _make_pre_tool_input("Bash", {"command": "rm -rf /"})
        result = await hooks.pre_tool_use(input_data, "tu-1", {"signal": None})
        out = result["hookSpecificOutput"]
        assert out["permissionDecision"] == "deny"
        assert "Bash" in out["permissionDecisionReason"]

    async def test_allows_non_sensitive_tool_default_mode(self) -> None:
        """Read does not match sensitive_patterns → allow (empty dict)."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write"],
            permission_mode="default",
        )
        input_data = _make_pre_tool_input("Read", {"file_path": "/tmp/x"})
        result = await hooks.pre_tool_use(input_data, "tu-2", {"signal": None})
        assert result == {}


class TestPreToolUseBypass:
    """PreToolUse auto-approves all tools when permission_mode='bypassPermissions'."""

    async def test_bypass_approves_sensitive_tool(self) -> None:
        """BypassPermissions → empty dict (no intervention) even for sensitive tools."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write"],
            permission_mode="bypassPermissions",
        )
        input_data = _make_pre_tool_input("Bash", {"command": "rm -rf /"})
        result = await hooks.pre_tool_use(input_data, "tu-3", {"signal": None})
        assert result == {}

    async def test_bypass_approves_any_tool(self) -> None:
        """BypassPermissions → empty dict for any tool."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="bypassPermissions",
        )
        input_data = _make_pre_tool_input("Read", {"file_path": "/tmp/x"})
        result = await hooks.pre_tool_use(input_data, "tu-4", {"signal": None})
        assert result == {}


class TestPreToolUseAcceptEdits:
    """PreToolUse with acceptEdits mode allows Edit/Write but denies Bash."""

    async def test_accept_edits_allows_write(self) -> None:
        """AcceptEdits → allow Write tool."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write", "Edit"],
            permission_mode="acceptEdits",
        )
        input_data = _make_pre_tool_input("Write", {"file_path": "/tmp/x"})
        result = await hooks.pre_tool_use(input_data, "tu-5", {"signal": None})
        assert result == {}

    async def test_accept_edits_allows_edit(self) -> None:
        """AcceptEdits → allow Edit tool."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write", "Edit"],
            permission_mode="acceptEdits",
        )
        input_data = _make_pre_tool_input("Edit", {"file_path": "/tmp/x"})
        result = await hooks.pre_tool_use(input_data, "tu-6", {"signal": None})
        assert result == {}

    async def test_accept_edits_allows_notebook_edit(self) -> None:
        """AcceptEdits → allow NotebookEdit tool."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "NotebookEdit"],
            permission_mode="acceptEdits",
        )
        input_data = _make_pre_tool_input("NotebookEdit", {"cell": "0"})
        result = await hooks.pre_tool_use(input_data, "tu-6b", {"signal": None})
        assert result == {}

    async def test_accept_edits_denies_bash(self) -> None:
        """AcceptEdits → deny Bash (not an edit tool)."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash", "Write", "Edit"],
            permission_mode="acceptEdits",
            hitl_timeout=0.1,
        )
        input_data = _make_pre_tool_input("Bash", {"command": "ls"})
        result = await hooks.pre_tool_use(input_data, "tu-7", {"signal": None})
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"


# ─── PostToolUse ─────────────────────────────────────────────────────────────


class TestPostToolUse:
    """PostToolUse logs audit trail."""

    async def test_post_tool_use_returns_empty(self) -> None:
        """PostToolUse returns empty dict (no intervention), logging is side-effect."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="default",
        )
        input_data = _make_post_tool_input("Bash", {"command": "ls"}, "output")
        result = await hooks.post_tool_use(input_data, "tu-8", {"signal": None})
        assert result == {}

    async def test_post_tool_use_increments_turn_count(self) -> None:
        """Each PostToolUse call increments the internal turn counter."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="default",
        )
        assert hooks.turn_count == 0
        input_data = _make_post_tool_input("Bash", {"command": "ls"}, "output")
        await hooks.post_tool_use(input_data, "tu-9", {"signal": None})
        assert hooks.turn_count == 1
        await hooks.post_tool_use(input_data, "tu-10", {"signal": None})
        assert hooks.turn_count == 2


# ─── Stop ────────────────────────────────────────────────────────────────────


class TestStop:
    """Stop hook enforces max_turns."""

    async def test_stop_halts_when_turn_limit_exceeded(self) -> None:
        """Stop returns continue_=False when turn_count >= max_turns."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="default",
            max_turns=2,
        )
        # Simulate 2 tool calls
        post_input = _make_post_tool_input("Bash", {}, "")
        await hooks.post_tool_use(post_input, "tu-a", {"signal": None})
        await hooks.post_tool_use(post_input, "tu-b", {"signal": None})

        stop_input = _make_stop_input()
        result = await hooks.stop(stop_input, None, {"signal": None})
        assert result["continue_"] is False
        assert "2/2" in result["stopReason"]

    async def test_stop_continues_when_under_limit(self) -> None:
        """Stop returns empty dict when under max_turns."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="default",
            max_turns=10,
        )
        stop_input = _make_stop_input()
        result = await hooks.stop(stop_input, None, {"signal": None})
        assert result == {}

    async def test_stop_continues_when_no_limit(self) -> None:
        """Stop returns empty dict when max_turns is None (no limit)."""
        hooks = GovernanceHooks(
            sensitive_patterns=[],
            permission_mode="default",
            max_turns=None,
        )
        # Simulate many tool calls
        post_input = _make_post_tool_input("Bash", {}, "")
        for _ in range(100):
            await hooks.post_tool_use(post_input, "tu-x", {"signal": None})

        stop_input = _make_stop_input()
        result = await hooks.stop(stop_input, None, {"signal": None})
        assert result == {}


# ─── HITL Event Models ───────────────────────────────────────────────────────


class TestHitlEvents:
    """HitlApprovalRequest and HitlApprovalResponse model tests."""

    def test_request_serialization(self) -> None:
        req = HitlApprovalRequest(
            request_id="hitl-1",
            tool_name="Bash",
            tool_input={"command": "git push --force"},
            session_id="ses-1",
        )
        data = req.model_dump(mode="json")
        restored = HitlApprovalRequest.model_validate(data)
        assert restored.request_id == "hitl-1"
        assert restored.tool_name == "Bash"

    def test_response_serialization(self) -> None:
        resp = HitlApprovalResponse(
            request_id="hitl-1",
            approved=True,
        )
        data = resp.model_dump(mode="json")
        restored = HitlApprovalResponse.model_validate(data)
        assert restored.request_id == "hitl-1"
        assert restored.approved is True

    def test_request_has_event_type(self) -> None:
        """HitlApprovalRequest has event_type for bubus."""
        req = HitlApprovalRequest(
            request_id="hitl-1",
            tool_name="Bash",
            tool_input={},
            session_id="ses-1",
        )
        assert req.event_type == "HitlApprovalRequest"

    def test_response_has_event_type(self) -> None:
        """HitlApprovalResponse has event_type for bubus."""
        resp = HitlApprovalResponse(
            request_id="hitl-1",
            approved=False,
        )
        assert resp.event_type == "HitlApprovalResponse"


# ─── HITL Gate ───────────────────────────────────────────────────────────────


class TestHitlGate:
    """HITL gate publishes approval request and awaits response."""

    async def test_hitl_publishes_request_on_sensitive_tool(
        self,
    ) -> None:
        """Sensitive tool + default mode → HITL request emitted."""
        from rai_agent.daemon.events import get_bus

        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=0.5,
        )
        bus = get_bus()
        received: list[Any] = []
        bus.on(
            "HitlApprovalRequest",
            lambda e: received.append(e),  # type: ignore[reportUnknownLambdaType]
        )

        input_data = _make_pre_tool_input(
            "Bash", {"command": "ls"}
        )
        # Will timeout (no response) → deny
        result = await hooks.pre_tool_use(
            input_data, "tu-hitl", {"signal": None}
        )
        assert len(received) == 1
        assert received[0].tool_name == "Bash"
        # Timeout → deny
        out = result["hookSpecificOutput"]
        assert out["permissionDecision"] == "deny"

    async def test_hitl_returns_allow_on_approval(self) -> None:
        """HITL gate returns allow when approval received."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=5.0,
        )
        input_data = _make_pre_tool_input(
            "Bash", {"command": "ls"}
        )

        async def _approve_later() -> None:
            """Wait for pending HITL, then approve."""
            while not hooks._pending_hitl:
                await asyncio.sleep(0.01)
            rid = next(iter(hooks._pending_hitl))
            hooks.resolve_hitl(rid, approved=True)

        task = asyncio.create_task(_approve_later())
        result = await hooks.pre_tool_use(
            input_data, "tu-hitl2", {"signal": None}
        )
        await task
        assert result == {}

    async def test_hitl_returns_deny_on_rejection(self) -> None:
        """HITL gate returns deny when rejection received."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=5.0,
        )
        input_data = _make_pre_tool_input(
            "Bash", {"command": "rm -rf /"}
        )

        async def _reject_later() -> None:
            """Wait for pending HITL, then reject."""
            while not hooks._pending_hitl:
                await asyncio.sleep(0.01)
            rid = next(iter(hooks._pending_hitl))
            hooks.resolve_hitl(rid, approved=False)

        task = asyncio.create_task(_reject_later())
        result = await hooks.pre_tool_use(
            input_data, "tu-hitl3", {"signal": None}
        )
        await task
        out = result["hookSpecificOutput"]
        assert out["permissionDecision"] == "deny"

    async def test_hitl_deny_on_timeout(self) -> None:
        """HITL gate denies on timeout (no response)."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=0.1,
        )
        input_data = _make_pre_tool_input(
            "Bash", {"command": "ls"}
        )
        result = await hooks.pre_tool_use(
            input_data, "tu-timeout", {"signal": None}
        )
        out = result["hookSpecificOutput"]
        assert out["permissionDecision"] == "deny"

    async def test_hitl_no_dangling_future_after_timeout(
        self,
    ) -> None:
        """Future is cleaned up after timeout."""
        hooks = GovernanceHooks(
            sensitive_patterns=["Bash"],
            permission_mode="default",
            hitl_timeout=0.1,
        )
        input_data = _make_pre_tool_input(
            "Bash", {"command": "ls"}
        )
        await hooks.pre_tool_use(
            input_data, "tu-dangle", {"signal": None}
        )
        # No pending futures should remain
        assert len(hooks._pending_hitl) == 0


# ─── PromptAssembler ─────────────────────────────────────────────────────────


class TestPromptAssembler:
    """PromptAssembler loads skills and memory into system prompt."""

    async def test_memory_content_with_section_header(
        self, tmp_path: Any
    ) -> None:
        """Memory paths are loaded with # Memory header."""
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("# Project Rules\nBe concise.")
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(
            memory_paths=["CLAUDE.md"]
        )
        assert "# Memory" in result
        assert "Be concise." in result

    async def test_skill_content_with_section_header(
        self, tmp_path: Any
    ) -> None:
        """Skills are loaded with # Skills and ## name headers."""
        skill_dir = tmp_path / ".raise" / "skills" / "daily-briefing"
        skill_dir.mkdir(parents=True)
        (skill_dir / "prompt.md").write_text("Generate a daily briefing.")
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(skills=["daily-briefing"])
        assert "# Skills" in result
        assert "## daily-briefing" in result
        assert "Generate a daily briefing." in result

    async def test_existing_system_prompt_prepended(
        self, tmp_path: Any
    ) -> None:
        """Explicit system_prompt is prepended to assembled content."""
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("Memory content.")
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(
            system_prompt="You are Rai.",
            memory_paths=["CLAUDE.md"],
        )
        assert result.startswith("You are Rai.")
        assert "Memory content." in result

    async def test_missing_file_skipped_gracefully(
        self, tmp_path: Any
    ) -> None:
        """Missing memory paths are skipped without crash."""
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(
            memory_paths=["nonexistent.md"]
        )
        # Should not crash, result should be empty
        assert result == ""

    async def test_missing_skill_skipped_gracefully(
        self, tmp_path: Any
    ) -> None:
        """Missing skills are skipped without crash."""
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(
            skills=["nonexistent-skill"]
        )
        assert result == ""

    async def test_empty_config_returns_empty(
        self, tmp_path: Any
    ) -> None:
        """No skills, no memory, no prompt → empty string."""
        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble()
        assert result == ""

    async def test_multiple_skills_and_memory(
        self, tmp_path: Any
    ) -> None:
        """Multiple skills and memory files are concatenated."""
        # Memory
        mem = tmp_path / "CLAUDE.md"
        mem.write_text("Project memory.")
        # Skill 1
        s1 = tmp_path / ".raise" / "skills" / "s1"
        s1.mkdir(parents=True)
        (s1 / "prompt.md").write_text("Skill 1 content.")
        # Skill 2
        s2 = tmp_path / ".raise" / "skills" / "s2"
        s2.mkdir(parents=True)
        (s2 / "prompt.md").write_text("Skill 2 content.")

        assembler = PromptAssembler(project_root=tmp_path)
        result = await assembler.assemble(
            skills=["s1", "s2"],
            memory_paths=["CLAUDE.md"],
        )
        assert "Project memory." in result
        assert "Skill 1 content." in result
        assert "Skill 2 content." in result


# ─── Test helpers ────────────────────────────────────────────────────────────


def _make_pre_tool_input(
    tool_name: str, tool_input: dict[str, Any]
) -> dict[str, Any]:
    """Create a PreToolUseHookInput-like dict."""
    return {
        "hook_event_name": "PreToolUse",
        "session_id": "ses-test",
        "transcript_path": "/tmp/transcript",
        "cwd": "/home/test",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "tu-test",
    }


def _make_post_tool_input(
    tool_name: str, tool_input: dict[str, Any], tool_response: Any
) -> dict[str, Any]:
    """Create a PostToolUseHookInput-like dict."""
    return {
        "hook_event_name": "PostToolUse",
        "session_id": "ses-test",
        "transcript_path": "/tmp/transcript",
        "cwd": "/home/test",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_response": tool_response,
        "tool_use_id": "tu-test",
    }


def _make_stop_input() -> dict[str, Any]:
    """Create a StopHookInput-like dict."""
    return {
        "hook_event_name": "Stop",
        "session_id": "ses-test",
        "transcript_path": "/tmp/transcript",
        "cwd": "/home/test",
        "stop_hook_active": True,
    }
