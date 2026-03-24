"""Telegram run pipeline for the Rai daemon.

TelegramHandler processes SessionRequests dispatched by the SessionDispatcher,
streaming output via DraftStreamer to Telegram.

Design decisions (S5.5):
  D1: TelegramHandler.handle receives SessionRequest from dispatcher
  D2: Session lookup/persist via SessionRegistry
  D3: No EventBus subscription — called directly by dispatcher worker
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from rai_agent.daemon.runtime import RunConfig
from rai_agent.daemon.telegram import DraftStreamer

# Re-export for backward compatibility
__all__ = [
    "CONTEXT_THRESHOLD",
    "CONTEXT_WINDOW",
    "TelegramHandler",
    "extract_status_from_frame",
    "extract_text_from_frame",
]

# ── Constants ──────────────────────────────────────────────────────────

CONTEXT_WINDOW = 200_000
"""Maximum input tokens for the Claude context window."""

CONTEXT_THRESHOLD = 0.75
"""Fraction of context window that triggers a user suggestion."""

if TYPE_CHECKING:
    from telegram import Bot  # type: ignore[import-untyped]

    from rai_agent.daemon.dispatcher import SessionRequest
    from rai_agent.daemon.registry import SessionRegistry
    from rai_agent.daemon.runtime import RaiAgentRuntime

_log = logging.getLogger(__name__)


def extract_text_from_frame(frame_json: str) -> str | None:
    """Extract human-readable text from an EventFrame JSON string.

    Only assistant_message frames with a 'text' content block produce
    output. All other frame types are ignored.
    """
    try:
        frame: dict[str, Any] = json.loads(frame_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if frame.get("event") != "assistant_message":
        return None
    payload: dict[str, Any] = frame.get("payload", {})
    content: list[dict[str, Any]] = payload.get("content", [])
    parts: list[str] = []
    for block in content:
        if "text" in block:
            parts.append(str(block["text"]))
    return "".join(parts) if parts else None


# ── Tool name → status emoji mapping ────────────────────────────────
_TOOL_STATUS: dict[str, str] = {
    "Read": "\U0001f4d6 Reading",
    "Edit": "\u270f\ufe0f Editing",
    "Write": "\u270f\ufe0f Writing",
    "Bash": "\u2699\ufe0f Running command",
    "Grep": "\U0001f50d Searching",
    "Glob": "\U0001f50d Searching files",
    "Agent": "\U0001f916 Spawning agent",
    "WebSearch": "\U0001f310 Searching web",
    "WebFetch": "\U0001f310 Fetching page",
}


def extract_status_from_frame(frame_json: str) -> str | None:
    """Extract agent activity status from an EventFrame JSON string.

    Returns a human-readable status for tool_use and thinking blocks.
    Returns None for text blocks and other frame types.
    """
    try:
        frame: dict[str, Any] = json.loads(frame_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if frame.get("event") != "assistant_message":
        return None
    payload: dict[str, Any] = frame.get("payload", {})
    content: list[dict[str, Any]] = payload.get("content", [])
    for block in content:
        # ToolUseBlock serializes as {id, name, input} (no "type" field)
        if "name" in block and "input" in block:
            name = str(block["name"])
            status = _TOOL_STATUS.get(name, f"\U0001f527 {name}")
            tool_input: dict[str, Any] = block.get("input", {})
            if name == "Read" and "file_path" in tool_input:
                path = str(tool_input["file_path"]).rsplit("/", 1)[-1]
                status = f"{status}: {path}"
            elif name == "Bash" and "command" in tool_input:
                cmd = str(tool_input["command"])[:40]
                status = f"{status}: {cmd}"
            elif name == "Grep" and "pattern" in tool_input:
                status = f"{status}: {tool_input['pattern']}"
            return status
        # ThinkingBlock serializes as {thinking, signature} (no "type" field)
        if "thinking" in block:
            return "\U0001f9e0 Thinking..."
    return None


# ─── TelegramHandler (S5.5) ──────────────────────────────────────────


class TelegramHandler:
    """Processes SessionRequests from the SessionDispatcher.

    Handles streaming via DraftStreamer and session persistence via
    SessionRegistry. Called by the dispatcher worker — no EventBus
    subscription. Session commands are handled by the session command
    middleware upstream.
    """

    def __init__(
        self,
        *,
        runtime: RaiAgentRuntime,
        bot: Bot,
        registry: SessionRegistry,
    ) -> None:
        self._runtime = runtime
        self._bot = bot
        self._registry = registry

    async def handle(self, request: SessionRequest) -> None:
        """Process a single SessionRequest.

        Extracts session from request.metadata, runs or resumes the
        runtime, and persists session state.
        """
        from rai_agent.daemon.registry import SessionKey

        session = request.metadata["session"]
        key = SessionKey.parse(request.session_key)
        chat_id = int(request.metadata["chat_id"])

        # Show "typing..." indicator while Claude thinks
        await self._bot.send_chat_action(chat_id, "typing")

        streamer = DraftStreamer(bot=self._bot, chat_id=chat_id)
        streamer.start_keepalive()

        async def _on_event(frame_json: str) -> None:
            # Show activity status via ephemeral draft
            status = extract_status_from_frame(frame_json)
            if status:
                await streamer.set_status(status)
                return
            # Accumulate response text silently
            text = extract_text_from_frame(frame_json)
            if text:
                await streamer.append(text)

        existing_sid = session.sdk_session_id
        run_config = RunConfig(
            prompt=request.prompt,
            content_blocks=request.content_blocks,
            cwd=session.cwd,
        )

        try:
            if existing_sid is not None:
                result = await self._runtime.resume(
                    run_config,
                    existing_sid,
                    _on_event,
                )
            else:
                result = await self._runtime.run(
                    run_config,
                    _on_event,
                )

            if result.session_id is not None:
                await self._registry.update(
                    key,
                    sdk_session_id=result.session_id,
                    input_tokens=result.input_tokens,
                )
        finally:
            await streamer.flush()

        # Context window suggestion
        if (
            result.input_tokens > 0
            and result.input_tokens / CONTEXT_WINDOW >= CONTEXT_THRESHOLD
        ):
            pct = int(
                result.input_tokens / CONTEXT_WINDOW * 100,
            )
            await request.send(
                f"\U0001f4a1 Context is {pct}% full. "
                "Consider /compact or /session new to start fresh.",
            )
