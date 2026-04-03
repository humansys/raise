"""Governance hooks for the Rai agent runtime.

GovernanceHooks implements PreToolUse/PostToolUse/Stop callbacks that match
the Claude Agent SDK HookCallback signature. The governance module does NOT
import claude_agent_sdk — runtime.py translates between SDK types and
GovernanceHooks methods, keeping the SDK dependency isolated.

PromptAssembler loads skills and memory into the system prompt.
HITL event models enable human-in-the-loop approval via EventBus.

Design decisions (S2.6):
  D1: Daemon-level hooks + per-run overrides via RunConfig
  D2: HITL via EventBus + asyncio.wait_for + timeout-to-deny
  D3: PromptAssembler with simple concatenation
  D4: Minimal governance for S2.7 Daily Briefing
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any

from rai_agent.daemon.events import BaseEvent

_log = logging.getLogger(__name__)

# Edit tools that acceptEdits mode auto-approves
_EDIT_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})


# ─── HITL Event Models ──────────────────────────────────────────────────────


class HitlApprovalRequest(BaseEvent):  # type: ignore[misc]
    """Published to EventBus when a sensitive tool needs human approval."""

    request_id: str
    tool_name: str
    tool_input: dict[str, Any]
    session_id: str


class HitlApprovalResponse(BaseEvent):  # type: ignore[misc]
    """Published to EventBus when human responds to an approval request."""

    request_id: str
    approved: bool


# ─── GovernanceHooks ─────────────────────────────────────────────────────────

# Type aliases for SDK hook signatures (avoids importing SDK types)
HookOutput = dict[str, Any]
HookInput = dict[str, Any]
HookCtx = dict[str, Any]


class GovernanceHooks:
    """Policy layer for agent tool calls.

    Callbacks match the Claude Agent SDK HookCallback signature:
        (input, tool_use_id_or_none, context) -> dict

    runtime.py wraps these into SDK HookMatcher entries.
    """

    def __init__(
        self,
        sensitive_patterns: list[str],
        permission_mode: str,
        max_turns: int | None = None,
        hitl_timeout: float = 300.0,
    ) -> None:
        self._sensitive_patterns = set(sensitive_patterns)
        self._permission_mode = permission_mode
        self._max_turns = max_turns
        self._hitl_timeout = hitl_timeout
        self._turn_count = 0
        # HITL pending futures: request_id -> Future
        self._pending_hitl: dict[str, asyncio.Future[bool]] = {}

    @property
    def turn_count(self) -> int:
        """Current turn count (incremented by post_tool_use)."""
        return self._turn_count

    # ── PreToolUse ───────────────────────────────────────────────────────

    async def pre_tool_use(
        self,
        input_data: HookInput,
        tool_use_id: str | None,
        context: HookCtx,
    ) -> HookOutput:
        """Evaluate a tool call before execution.

        Returns empty dict for allow, or deny output for blocked tools.
        """
        tool_name: str = input_data["tool_name"]

        # bypassPermissions → always allow
        if self._permission_mode == "bypassPermissions":
            return {}

        # acceptEdits → allow edit tools even if in sensitive_patterns
        if self._permission_mode == "acceptEdits" and tool_name in _EDIT_TOOLS:
            return {}

        # Check if tool matches sensitive patterns → HITL gate
        if tool_name in self._sensitive_patterns:
            session_id: str = input_data.get("session_id", "unknown")
            tool_input: dict[str, Any] = input_data.get("tool_input", {})
            approved = await self._request_hitl_approval(
                tool_name, tool_input, session_id
            )
            if approved:
                return {}
            return self._deny(
                tool_name,
                f"Tool '{tool_name}' denied (HITL rejected/timeout)",
            )

        return {}

    # ── PostToolUse ──────────────────────────────────────────────────────

    async def post_tool_use(
        self,
        input_data: HookInput,
        tool_use_id: str | None,
        context: HookCtx,
    ) -> HookOutput:
        """Log tool use and increment turn counter."""
        self._turn_count += 1
        tool_name: str = input_data["tool_name"]
        _log.info(
            "tool_audit",
            extra={
                "tool_name": tool_name,
                "tool_input_keys": list(input_data.get("tool_input", {}).keys()),
                "turn": self._turn_count,
            },
        )
        return {}

    # ── Stop ─────────────────────────────────────────────────────────────

    async def stop(
        self,
        input_data: HookInput,
        tool_use_id: str | None,
        context: HookCtx,
    ) -> HookOutput:
        """Enforce turn limit. Returns halt when exceeded."""
        if self._max_turns is not None and self._turn_count >= self._max_turns:
            reason = f"Turn limit exceeded ({self._turn_count}/{self._max_turns})"
            _log.warning("governance_stop", extra={"reason": reason})
            return {"continue_": False, "stopReason": reason}
        return {}

    # ── HITL Gate ────────────────────────────────────────────────────────

    def resolve_hitl(self, request_id: str, approved: bool) -> None:
        """Resolve a pending HITL approval request.

        Called by external subscribers (Telegram, CLI) when user responds.
        Must be called from the same event loop that created the future.
        For cross-thread callers, use ``loop.call_soon_threadsafe``.
        """
        future = self._pending_hitl.get(request_id)
        if future is not None and not future.done():
            future.set_result(approved)

    async def _request_hitl_approval(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        session_id: str,
    ) -> bool:
        """Publish HITL request to EventBus and await response.

        Returns True if approved, False on deny or timeout.
        """
        from rai_agent.daemon.events import get_bus

        request_id = f"hitl-{uuid.uuid4().hex[:8]}"
        loop = asyncio.get_running_loop()
        future: asyncio.Future[bool] = loop.create_future()
        self._pending_hitl[request_id] = future

        # Emit request to EventBus — subscribers handle approval UI
        bus = get_bus()
        request = HitlApprovalRequest(
            request_id=request_id,
            tool_name=tool_name,
            tool_input=tool_input,
            session_id=session_id,
        )
        bus.emit(request)

        try:
            approved = await asyncio.wait_for(future, timeout=self._hitl_timeout)
            return approved
        except TimeoutError:
            _log.warning(
                "hitl_timeout",
                extra={
                    "request_id": request_id,
                    "tool_name": tool_name,
                },
            )
            return False
        finally:
            # Clean up: cancel future if still pending, remove
            if not future.done():
                future.cancel()
            self._pending_hitl.pop(request_id, None)

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _deny(tool_name: str, reason: str) -> HookOutput:
        """Build a deny hook output."""
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }


# ─── PromptAssembler ─────────────────────────────────────────────────────────


class PromptAssembler:
    """Loads skills and memory into a system prompt string.

    Simple concatenation with section headers. No template engine.
    """

    def __init__(self, project_root: str | Path) -> None:
        self._root = Path(project_root)

    async def assemble(
        self,
        *,
        system_prompt: str | None = None,
        skills: list[str] | None = None,
        memory_paths: list[str] | None = None,
    ) -> str:
        """Build system prompt from skills, memory, and explicit prompt.

        Args:
            system_prompt: Explicit prompt to prepend (takes priority).
            skills: Skill names to resolve and load.
            memory_paths: File paths (relative to project_root) to load as memory.

        Returns:
            Assembled system prompt string.
        """
        sections: list[str] = []

        # Explicit prompt first
        if system_prompt:
            sections.append(system_prompt)

        # Memory
        if memory_paths:
            memory_parts: list[str] = []
            for path_str in memory_paths:
                content = self._read_file(path_str)
                if content is not None:
                    memory_parts.append(content)
            if memory_parts:
                sections.append("# Memory\n\n" + "\n\n".join(memory_parts))

        # Skills
        if skills:
            skill_parts: list[str] = []
            for skill_name in skills:
                content = self._load_skill(skill_name)
                if content is not None:
                    skill_parts.append(f"## {skill_name}\n\n{content}")
            if skill_parts:
                sections.append("# Skills\n\n" + "\n\n".join(skill_parts))

        return "\n\n".join(sections)

    def _read_file(self, path_str: str) -> str | None:
        """Read a file relative to project root, returning None on error."""
        try:
            full_path = self._root / path_str
            return full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            _log.warning(
                "prompt_assemble_read_error",
                extra={"path": path_str, "error": str(e)},
            )
            return None

    def _load_skill(self, skill_name: str) -> str | None:
        """Resolve and load a skill by name.

        Searches .raise/skills/{name}/ for a prompt.md file.
        """
        skill_dir = self._root / ".raise" / "skills" / skill_name
        prompt_file = skill_dir / "prompt.md"
        if prompt_file.exists():
            try:
                return prompt_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as e:
                _log.warning(
                    "prompt_assemble_skill_error",
                    extra={"skill": skill_name, "error": str(e)},
                )
                return None
        _log.warning(
            "prompt_assemble_skill_not_found",
            extra={"skill": skill_name, "path": str(prompt_file)},
        )
        return None
