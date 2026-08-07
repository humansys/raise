"""JSONL transcript parser for the post-session distillation agent.

Reads Claude Code session JSONL files and converts each turn into a
TurnRecord with extracted text, tool names, and [RAI:] header attribution.
"""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel


class TurnType(str, Enum):
    """Canonical turn types in a Claude Code JSONL session."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL_RESULT = "tool_result"


class TurnRecord(BaseModel):
    """Parsed representation of a single JSONL turn."""

    index: int
    turn_type: TurnType
    content_text: str
    is_harness_noise: bool = False
    is_developer: bool = False
    timestamp_offset_s: float | None = None
    rai_header: dict[str, str] | None = None
    tool_names: list[str] = []
    tool_inputs: dict[str, Any] = {}
    # ^ {tool_use_id: {"name": str, "input": dict}} for gate-binding in RAISE-15327

    @property
    def has_tools(self) -> bool:
        """True if this assistant turn invoked at least one tool."""
        return len(self.tool_names) > 0


# Harness noise taxonomy — Claude Code injects these as user turns.
# Ordered by frequency; all use O(prefix) prefix or tag checks (no regex).
_NOISE_PREFIXES: tuple[str, ...] = (
    "Base directory for this skill:",  # skill injection
    "This session is being continued",  # compaction summary (highest FP risk)
    "(Re-invocation of /",  # re-injected skill after compaction
    "<system-reminder>",  # system-reminder block
    "<local-command-stdout>",  # tool stdout injected as user turn
    "<local-command-stderr>",  # tool stderr variant
    "Caveat: ",  # harness caveat wrapper
)


def _is_harness_noise(text: str) -> bool:
    """Return True if the user turn is harness-injected noise, not developer signal."""
    return text.startswith(_NOISE_PREFIXES)


_DEVELOPER_SOURCES = frozenset({"typed", "queued", "suggestion_accepted"})

# When RAISE_DISTILL_DEV_TURNS=1, developer turn text is persisted; otherwise blanked.
_DEV_TURNS_ALLOWED = os.environ.get("RAISE_DISTILL_DEV_TURNS", "0") == "1"

# System-generated structural markers embedded in developer turns.
# These are NOT developer speech and must survive the privacy gate.
_STRUCTURAL_MARKERS = ("[Request interrupted by user]",)


def _classify_record_type(
    obj: dict[str, Any],
) -> Literal["developer", "tool_result", "assistant", "meta"]:
    """Classify a raw JSONL object into a processing category.

    Developer turns have message.content as a plain string in Claude Code JSONL.
    OR-logic covers all promptSource variants and old CC versions (origin.kind only).
    """
    turn_type = obj.get("type", "")
    if turn_type == "assistant":
        return "assistant"
    if turn_type != "user":
        return "meta"

    if obj.get("isMeta") is True:
        return "meta"

    prompt_src = obj.get("promptSource", "")
    origin_kind = ""
    origin_raw = obj.get("origin")
    if isinstance(origin_raw, dict):
        origin_kind = origin_raw.get("kind", "")

    is_developer_authored = prompt_src in _DEVELOPER_SOURCES or origin_kind == "human"
    if is_developer_authored:
        msg = obj.get("message", {})
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, str):
            return "developer"
        # List content with developer authorship (e.g. [Request interrupted])
        # — handled as developer turn with list-content path
        if isinstance(content, list):
            return "developer"

    return "tool_result"


def parse_session_jsonl(path: Path) -> list[TurnRecord]:
    """Parse a Claude Code JSONL file into a list of TurnRecords."""
    return parse_session_jsonl_string(
        path.read_text(encoding="utf-8", errors="replace")
    )


def _parse_one(
    obj: dict[str, Any],
    index: int,
    parse_rai_header: Any,
) -> TurnRecord | None:
    """Dispatch a single JSONL object to the appropriate parser. Returns None for meta."""
    message: Any = obj.get("message", {})
    if not isinstance(message, dict):
        return None
    kind = _classify_record_type(obj)
    if kind == "assistant":
        blocks: Any = message.get("content", [])
        return _parse_assistant_turn(
            index, blocks if isinstance(blocks, list) else [], parse_rai_header
        )
    if kind == "developer":
        return _parse_developer_turn(index, message.get("content", ""))
    if kind == "tool_result":
        content_raw: Any = message.get("content", [])
        if isinstance(content_raw, str):
            # Harness-injected noise (system-reminder, skill injections, etc.) arrives
            # as a plain string — not a block list.  Detect noise flag directly.
            return TurnRecord(
                index=index,
                turn_type=TurnType.USER,
                content_text=content_raw,
                is_harness_noise=_is_harness_noise(content_raw),
            )
        return _parse_user_turn(
            index, content_raw if isinstance(content_raw, list) else []
        )
    return None  # "meta"


def parse_session_jsonl_string(text: str) -> list[TurnRecord]:
    """Parse JSONL text (one JSON object per line) into TurnRecords."""
    from raise_cli.pipeline.rai_header import parse_rai_header

    records: list[TurnRecord] = []
    index = 0
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj: Any = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        record = _parse_one(obj, index, parse_rai_header)
        if record is not None:
            records.append(record)
            index += 1
    return records


def _parse_developer_turn(index: int, content: Any) -> TurnRecord:
    """Build a TurnRecord from a developer message.

    message.content is a plain string in modern Claude Code JSONL.
    In older versions it may be a list of text blocks.
    Privacy gate: content_text is blanked unless RAISE_DISTILL_DEV_TURNS=1,
    except structural markers (e.g. [Request interrupted]) which always survive.
    """
    if isinstance(content, str):
        raw_text = content
    elif isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif isinstance(block, str):
                parts.append(block)
        raw_text = "\n".join(parts)
    else:
        raw_text = ""

    if _DEV_TURNS_ALLOWED:
        stored_text = raw_text
    else:
        # Preserve structural markers even with privacy gate active
        found_markers = [m for m in _STRUCTURAL_MARKERS if m in raw_text]
        stored_text = "\n".join(found_markers) if found_markers else ""

    return TurnRecord(
        index=index,
        turn_type=TurnType.USER,
        content_text=stored_text,
        is_developer=True,
        is_harness_noise=False,
    )


def _parse_assistant_turn(
    index: int,
    content_blocks: list[Any],
    parse_rai_header: Any,
) -> TurnRecord:
    """Build a TurnRecord from an assistant message's content blocks."""
    text_parts: list[str] = []
    tool_names: list[str] = []
    tool_inputs: dict[str, Any] = {}
    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text_parts.append(str(block.get("text", "")))
        elif block.get("type") == "tool_use":
            name: Any = block.get("name")
            tool_use_id: Any = block.get("id", "")
            inp: Any = block.get("input", {})
            if isinstance(name, str):
                tool_names.append(name)
                if tool_use_id:
                    tool_inputs[str(tool_use_id)] = {
                        "name": name,
                        "input": inp if isinstance(inp, dict) else {},
                    }
    content_text = "\n".join(text_parts)
    header = parse_rai_header(content_text) if content_text else None
    return TurnRecord(
        index=index,
        turn_type=TurnType.ASSISTANT,
        content_text=content_text,
        rai_header=header,
        tool_names=tool_names,
        tool_inputs=tool_inputs,
    )


def _parse_user_turn(index: int, content_blocks: list[Any]) -> TurnRecord:
    """Build a TurnRecord from a user message's content blocks."""
    text_parts: list[str] = []
    is_tool_result = False
    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        block_type: Any = block.get("type")
        if block_type == "text":
            text_parts.append(str(block.get("text", "")))
        elif block_type == "tool_result":
            is_tool_result = True
            inner: Any = block.get("content", [])
            if isinstance(inner, list):
                for ib in inner:
                    if isinstance(ib, dict) and ib.get("type") == "text":
                        text_parts.append(str(ib.get("text", "")))
            elif isinstance(inner, str):
                text_parts.append(inner)
    turn_type = TurnType.TOOL_RESULT if is_tool_result else TurnType.USER
    content = "\n".join(text_parts)
    return TurnRecord(
        index=index,
        turn_type=turn_type,
        content_text=content,
        is_harness_noise=turn_type == TurnType.USER and _is_harness_noise(content),
        rai_header=None,
        tool_names=[],
    )
