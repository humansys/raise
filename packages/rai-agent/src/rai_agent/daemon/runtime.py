"""Rai agent runtime abstraction.

RaiAgentRuntime is a Protocol (2 methods: run / resume).
ClaudeRuntime is the only file that imports claude_agent_sdk — all other modules
depend on the Protocol, keeping the SDK dependency isolated here.

Design decisions (S2.3):
  D1: query() over ClaudeSDKClient — stateless fits daemon's own state layer
  D2: stream all SDK messages — filter downstream (S2.5 DraftStreamer)
  D3: balanced RunConfig — 4 fields covering S2.3 needs + S2.6 governance hooks
"""

from __future__ import annotations

import dataclasses
import re
import time
from typing import TYPE_CHECKING, Any, Literal, Protocol

import structlog
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from pydantic import BaseModel

from rai_agent.daemon.protocol import EventFrame

if TYPE_CHECKING:
    from collections.abc import (
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        Callable,
    )

    from rai_agent.daemon.governance import (
        GovernanceHooks,
        PromptAssembler,
    )

# ─── RunResult ────────────────────────────────────────────────────────────────


@dataclasses.dataclass
class RunResult:
    """Result from an agent run, including session and usage metrics."""

    session_id: str | None = None
    input_tokens: int = 0


# ─── RunConfig ────────────────────────────────────────────────────────────────


class RunConfig(BaseModel):
    """Input contract for agent dispatch.

    Balanced surface: covers S2.3 needs + what S2.6 governance will inject.
    """

    prompt: str
    content_blocks: list[dict[str, Any]] | None = None
    """Multimodal content blocks (images + text). When present,
    runtime uses AsyncIterable mode to send structured content."""
    session_id: str | None = None
    system_prompt: str | None = None
    permission_mode: Literal["default", "acceptEdits", "bypassPermissions"] | None = (
        None
    )
    # S2.6 governance additions — all optional, backward compatible
    max_turns: int | None = None
    skills: list[str] | None = None
    memory_paths: list[str] | None = None
    sensitive_patterns: list[str] | None = None
    cwd: str | None = None


# ─── Protocol ─────────────────────────────────────────────────────────────────


class RaiAgentRuntime(Protocol):
    """Protocol for agent runtimes.

    Two methods only — thin abstraction.
    Swap ClaudeRuntime for another implementation without touching
    the daemon, governance, or trigger layers.
    """

    async def run(
        self,
        config: RunConfig,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Execute a prompt. Returns RunResult with session_id + metrics."""
        ...

    async def resume(
        self,
        config: RunConfig,
        session_id: str,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Resume an existing session. Returns RunResult."""
        ...


# ─── _to_event_frame ─────────────────────────────────────────────────────────


def _to_event_frame(msg: Any, seq: int) -> EventFrame:
    """Map a claude_agent_sdk message to an EventFrame for wire transport."""
    if isinstance(msg, AssistantMessage):
        return EventFrame(
            type="event",
            event="assistant_message",
            payload=dataclasses.asdict(msg),
            seq=seq,
        )
    if isinstance(msg, UserMessage):
        return EventFrame(
            type="event",
            event="user_message",
            payload=dataclasses.asdict(msg),
            seq=seq,
        )
    if isinstance(msg, ResultMessage):
        return EventFrame(
            type="event",
            event="result",
            payload=dataclasses.asdict(msg),
            seq=seq,
        )
    # SystemMessage, StreamEvent, TaskXxxMessage, and future SDK additions
    return EventFrame(
        type="event",
        event="sdk_event",
        payload={"type": type(msg).__name__, "data": _safe_dict(msg)},
        seq=seq,
    )


def _safe_dict(msg: Any) -> dict[str, Any]:
    """Convert a dataclass to dict, falling back to str for unknown types."""
    if dataclasses.is_dataclass(msg) and not isinstance(msg, type):
        return dataclasses.asdict(msg)
    return {"raw": str(msg)}


# ─── Verbose Logging Helpers (S4.4) ──────────────────────────────────────────

_TOOL_RESULT_MAX_LEN = 500
_DEFAULT_SENSITIVE = frozenset({"sk-ant-", r"bot\d+:", "xoxb-", "Bearer "})


def _truncate(text: str, max_len: int = _TOOL_RESULT_MAX_LEN) -> str:
    """Cap text at max_len chars with a truncation suffix."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"... [truncated {len(text) - max_len} chars]"


def _redact(text: str, patterns: frozenset[str]) -> str:
    """Replace sensitive patterns (and default patterns) with [REDACTED].

    Patterns in _DEFAULT_SENSITIVE are regex fragments (e.g. ``bot\\d+:``).
    Each is extended with ``\\S*`` to capture the value after the prefix.
    """
    for pattern in _DEFAULT_SENSITIVE | patterns:
        text = re.sub(pattern + r"\S*", "[REDACTED]", text)
    return text


_logger = structlog.get_logger("rai_agent.daemon.runtime")


def _log_sdk_message(
    msg: Any,
    seq: int,
    conversation_id: str,
    sensitive_patterns: frozenset[str],
) -> None:
    """Log SDK message content as structured JSONL with OTel GenAI attributes."""
    base: dict[str, Any] = {
        "gen_ai.agent.name": "rai",
        "gen_ai.conversation.id": conversation_id,
        "seq": seq,
    }

    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, ThinkingBlock):
                _logger.debug(
                    "llm.thinking",
                    **base,
                    content=_truncate(_redact(block.thinking, sensitive_patterns)),
                )
            elif isinstance(block, ToolUseBlock):
                _logger.debug(
                    "tool.start",
                    **base,
                    tool_name=block.name,
                    tool_input=_truncate(_redact(str(block.input), sensitive_patterns)),
                )
            elif isinstance(block, TextBlock):
                _logger.debug(
                    "message.out",
                    **base,
                    content=_truncate(_redact(block.text, sensitive_patterns)),
                )
    elif isinstance(msg, UserMessage):
        if isinstance(msg.content, list):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    content = str(block.content) if block.content else ""
                    _logger.debug(
                        "tool.end",
                        **base,
                        tool_use_id=block.tool_use_id,
                        is_error=block.is_error,
                        content=_truncate(_redact(content, sensitive_patterns)),
                    )
        else:
            _logger.debug("message.in", **base)
    elif isinstance(msg, ResultMessage):
        usage = msg.usage or {}
        _logger.info(
            "llm.usage",
            **base,
            gen_ai_usage_input_tokens=usage.get("input_tokens", 0),
            gen_ai_usage_output_tokens=usage.get("output_tokens", 0),
            duration_ms=msg.duration_ms,
            num_turns=msg.num_turns,
            cost_usd=str(msg.total_cost_usd),
        )


# ─── ClaudeRuntime ────────────────────────────────────────────────────────────


class ClaudeRuntime:
    """Wraps claude_agent_sdk.query() — the only file that imports the SDK.

    Optionally accepts GovernanceHooks and PromptAssembler for policy
    enforcement and system prompt assembly. Passing neither preserves
    the original behavior exactly (MUST-NOT-3).
    """

    def __init__(
        self,
        governance: GovernanceHooks | None = None,
        assembler: PromptAssembler | None = None,
        cwd: str | None = None,
        verbose: bool = False,
    ) -> None:
        self._governance = governance
        self._assembler = assembler
        self._cwd = cwd
        self._verbose = verbose
        self._sensitive_patterns: frozenset[str] = frozenset()

    async def _build_options(
        self,
        config: RunConfig,
        *,
        resume_id: str | None = None,
    ) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions from RunConfig + governance."""
        # System prompt: assemble if assembler is available
        system_prompt = config.system_prompt
        if self._assembler is not None:
            system_prompt = await self._assembler.assemble(
                system_prompt=config.system_prompt,
                skills=config.skills,
                memory_paths=config.memory_paths,
            )
            # Empty string → None (SDK treats None as no prompt)
            if not system_prompt:
                system_prompt = None

        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            permission_mode=(config.permission_mode or "bypassPermissions"),
            max_turns=config.max_turns,
            cwd=config.cwd or self._cwd,
            setting_sources=["project", "local"],
        )

        if resume_id is not None:
            options.resume = resume_id

        # Wire governance hooks into SDK hooks dict.
        # GovernanceHooks methods return dict[str, Any] which is
        # structurally compatible with SyncHookJSONOutput at runtime
        # but pyright can't verify TypedDict compatibility.
        if self._governance is not None:
            gov = self._governance
            options.hooks = {
                "PreToolUse": [
                    HookMatcher(
                        hooks=[gov.pre_tool_use],  # type: ignore[list-item]
                    )
                ],
                "PostToolUse": [
                    HookMatcher(
                        hooks=[gov.post_tool_use],  # type: ignore[list-item]
                    )
                ],
                "Stop": [
                    HookMatcher(
                        hooks=[gov.stop],  # type: ignore[list-item]
                    )
                ],
            }

        return options

    async def run(
        self,
        config: RunConfig,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Run a prompt from scratch. Returns RunResult."""
        self._sensitive_patterns = frozenset(config.sensitive_patterns or [])
        options = await self._build_options(config)
        conv_id = config.session_id or ""
        return await self._stream(
            config.prompt,
            options,
            send,
            conversation_id=conv_id,
            content_blocks=config.content_blocks,
        )

    async def resume(
        self,
        config: RunConfig,
        session_id: str,
        send: Callable[[str], Awaitable[None]],
    ) -> RunResult:
        """Resume an existing SDK session. Returns RunResult."""
        self._sensitive_patterns = frozenset(config.sensitive_patterns or [])
        options = await self._build_options(config, resume_id=session_id)
        conv_id = config.session_id or ""
        return await self._stream(
            config.prompt,
            options,
            send,
            conversation_id=conv_id,
            content_blocks=config.content_blocks,
        )

    async def _stream(
        self,
        prompt: str,
        options: ClaudeAgentOptions,
        send: Callable[[str], Awaitable[None]],
        conversation_id: str = "",
        content_blocks: list[dict[str, Any]] | None = None,
    ) -> RunResult:
        """Stream all SDK messages as EventFrames. Returns RunResult."""
        t0 = time.monotonic()
        captured_session_id: str | None = None
        captured_input_tokens: int = 0
        seq = 0

        if self._verbose:
            _logger.info(
                "agent.start",
                **{
                    "gen_ai.agent.name": "rai",
                    "gen_ai.conversation.id": conversation_id,
                },
            )

        # D6: Use AsyncIterable mode for multimodal content blocks
        source: str | AsyncIterable[dict[str, Any]]
        if content_blocks is not None:

            async def _image_prompt() -> AsyncIterator[dict[str, Any]]:
                yield {
                    "type": "user",
                    "session_id": "",
                    "message": {
                        "role": "user",
                        "content": content_blocks,
                    },
                    "parent_tool_use_id": None,
                }

            source = _image_prompt()
        else:
            source = prompt

        async for msg in query(prompt=source, options=options):
            if self._verbose:
                _log_sdk_message(
                    msg,
                    seq,
                    conversation_id,
                    self._sensitive_patterns,
                )
            frame = _to_event_frame(msg, seq)
            await send(frame.model_dump_json())
            if isinstance(msg, ResultMessage):
                captured_session_id = msg.session_id
                usage = msg.usage or {}
                captured_input_tokens = usage.get(
                    "input_tokens",
                    0,
                )
            seq += 1

        if self._verbose:
            duration_ms = int((time.monotonic() - t0) * 1000)
            _logger.info(
                "agent.end",
                **{
                    "gen_ai.agent.name": "rai",
                    "gen_ai.conversation.id": conversation_id,
                    "duration_ms": duration_ms,
                    "message_count": seq,
                },
            )

        return RunResult(
            session_id=captured_session_id,
            input_tokens=captured_input_tokens,
        )
