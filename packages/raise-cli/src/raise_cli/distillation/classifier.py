"""Rule-based turn classifier for the post-session distillation agent.

Classifies TurnRecords into TurnClass using keyword heuristics.
Intentionally simple — no ML, no embeddings (YAGNI in v1).
"""

from __future__ import annotations

import re
from enum import Enum

from raise_cli.distillation.parser import TurnRecord, TurnType


class TurnClass(str, Enum):
    """Semantic classification of a JSONL turn for distillation purposes."""

    DECISION = "decision"
    CORRECTION = "correction"
    INSIGHT = "insight"
    BLOCKER = "blocker"
    TOOL_USE = "tool_use"
    TOOL_REJECTION = "tool_rejection"
    NEUTRAL = "neutral"


_DECISION_RE = re.compile(
    r"\b(ok adelante|ok continuemos|adelante con|adelante|sí\b|"
    r"si[,.]?\s|yes\b|proceed|looks good|sounds good|perfect|dale\b)\b",
    re.IGNORECASE,
)
_CORRECTION_RE = re.compile(
    r"\b(no\b|wrong\b|don'?t\b|fix\b|revert\b|that'?s wrong)\b",
    re.IGNORECASE,
)
_TOOL_REJECTION_PREFIXES: tuple[str, ...] = (
    "The user doesn't want to proceed with this tool use",
    "The user doesn’t want to proceed with this tool use",
)
_USER_INTERRUPT_PREFIXES: tuple[str, ...] = (
    "[Request interrupted by user]",
    "[Request interrupted by user for tool use]",
)

_BLOCKER_RE = re.compile(
    r"(STOP\s*[—–-]|blocked\s*[—–:-])",
    re.IGNORECASE,
)
_INSIGHT_RE = re.compile(
    r"(rai pattern add|insight:|"
    r"critical finding|patr[oó]n cr[ií]tico|"
    r"key insight|constraint de diseño|design constraint|"
    r"descubr[eiío]|non.obvious|no.obvio)",
    re.IGNORECASE,
)
_SHELL_CMD_RE = re.compile(
    r"^(git\s|sed\s|grep\s|ls\s|head\s|cat\s|tail\s|"
    r"fly\s|gcloud\s|xdg-open\s|stripe\s|"
    r"/home/|Background agent|[0-9]+ background agent)",
    re.IGNORECASE,
)
_ENGINE_INJECTION_RE = re.compile(
    r"^(You are executing phase|Execute skill|Execute the\s|"
    r"## Rol\b|Eres el )",
    re.IGNORECASE,
)


def _is_tool_rejection(text: str) -> bool:
    """Check if text is a mechanical tool-use rejection or user interrupt."""
    return any(text.startswith(p) for p in _TOOL_REJECTION_PREFIXES) or any(
        text.startswith(p) for p in _USER_INTERRUPT_PREFIXES
    )


def classify_structural(record: TurnRecord) -> TurnClass | None:
    """Level 1: structural pre-filter before semantic classification.

    Returns a TurnClass for structural noise (harness, tool rejections,
    tool-only assistant turns), or None if the turn should proceed to
    semantic classification.
    """
    if record.is_harness_noise:
        return TurnClass.NEUTRAL
    if record.turn_type == TurnType.TOOL_RESULT:
        return TurnClass.NEUTRAL
    if record.content_text.lstrip().startswith("<task-notification>"):
        return TurnClass.NEUTRAL
    if _ENGINE_INJECTION_RE.match(record.content_text.lstrip()):
        return TurnClass.NEUTRAL
    if _is_tool_rejection(record.content_text):
        return TurnClass.TOOL_REJECTION
    if (
        record.turn_type == TurnType.ASSISTANT
        and record.tool_names
        and not record.content_text.strip()
    ):
        return TurnClass.TOOL_USE
    return None


def _classify_semantic_user(text: str) -> TurnClass:
    """Level 2: semantic classification for user/developer turns."""
    if not text:
        return TurnClass.NEUTRAL
    if _SHELL_CMD_RE.match(text):
        return TurnClass.NEUTRAL
    if _BLOCKER_RE.search(text):
        return TurnClass.BLOCKER
    if _CORRECTION_RE.search(text):
        return TurnClass.CORRECTION
    if _DECISION_RE.search(text):
        return TurnClass.DECISION
    return TurnClass.NEUTRAL


def _classify_semantic_assistant(record: TurnRecord) -> TurnClass:
    """Level 2: semantic classification for assistant turns."""
    text = record.content_text
    if _BLOCKER_RE.search(text) and (len(text) < 400 or _BLOCKER_RE.search(text[:100])):
        return TurnClass.BLOCKER
    if record.tool_names:
        return TurnClass.TOOL_USE
    if _INSIGHT_RE.search(text[:300]):
        return TurnClass.INSIGHT
    return TurnClass.NEUTRAL


def classify_turn(record: TurnRecord) -> TurnClass:
    """Two-level classifier: structural pre-filter, then semantic."""
    structural = classify_structural(record)
    if structural is not None:
        return structural
    if record.turn_type == TurnType.ASSISTANT:
        return _classify_semantic_assistant(record)
    return _classify_semantic_user(record.content_text)
