"""Transcript extraction contracts for Rai-Agent meeting-to-backlog runs."""

from __future__ import annotations

import hashlib
import re

from pydantic import BaseModel, ConfigDict, Field

from raise_core.runtime.agent import (
    EvidenceRef,
    TranscriptAction,
    TranscriptDecision,
    TranscriptQuestion,
    TranscriptRisk,
    TranscriptSpan,
)

_ACTION_RE = re.compile(
    r"^(?P<owner>[A-Z][\w .'-]*?)\s+will\s+(?P<title>.+?)(?:\s+by\s+(?P<due_date>[^.]+))?\.?$"
)
_AMBIGUOUS_ACTION_RE = re.compile(
    r"^(?:Someone|Somebody)\s+should\s+(?P<title>.+?)\.?$"
)


class TranscriptExtractionError(ValueError):
    """Raised when transcript input cannot be extracted reliably."""


class TranscriptExtractionResult(BaseModel):
    """Structured facts extracted from a meeting transcript."""

    model_config = ConfigDict(frozen=True)

    transcript_id: str = Field(..., min_length=1)
    actions: list[TranscriptAction] = Field(default_factory=list)
    decisions: list[TranscriptDecision] = Field(default_factory=list)
    risks: list[TranscriptRisk] = Field(default_factory=list)
    questions: list[TranscriptQuestion] = Field(default_factory=list)
    spans: list[TranscriptSpan] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)


def extract_meeting_transcript(
    *, transcript_id: str, text: str
) -> TranscriptExtractionResult:
    """Extract typed meeting facts from transcript text."""
    if not text.strip():
        msg = "transcript text must not be empty"
        raise TranscriptExtractionError(msg)

    actions: list[TranscriptAction] = []
    decisions: list[TranscriptDecision] = []
    risks: list[TranscriptRisk] = []
    questions: list[TranscriptQuestion] = []
    spans: list[TranscriptSpan] = []

    for line, start_offset in _iter_lines_with_offsets(text):
        speaker, content = _parse_speaker_turn(line)
        span = _build_span(
            transcript_id=transcript_id,
            sequence=len(spans) + 1,
            start_offset=start_offset,
            text=line,
            speaker=speaker,
        )
        evidence = _build_evidence(span=span, quote=content)

        action_match = _ACTION_RE.match(content)
        if action_match is not None:
            actions.append(
                TranscriptAction(
                    title=action_match.group("title").strip(),
                    owner=action_match.group("owner").strip(),
                    due_date=_clean_optional(action_match.group("due_date")),
                    confidence=0.7,
                    evidence_refs=[evidence],
                )
            )
            spans.append(span)
            continue

        ambiguous_action_match = _AMBIGUOUS_ACTION_RE.match(content)
        if ambiguous_action_match is not None:
            actions.append(
                TranscriptAction(
                    title=ambiguous_action_match.group("title").strip(),
                    confidence=0.55,
                    evidence_refs=[evidence],
                )
            )
            spans.append(span)
            continue

        if decision := _strip_prefixed_fact(content, "Decision:"):
            decisions.append(
                TranscriptDecision(
                    decision=decision,
                    confidence=0.75,
                    evidence_refs=[evidence],
                )
            )
            spans.append(span)
            continue

        if risk := _strip_prefixed_fact(content, "Risk:"):
            risks.append(
                TranscriptRisk(
                    risk=risk,
                    confidence=0.75,
                    evidence_refs=[evidence],
                )
            )
            spans.append(span)
            continue

        if question := _strip_prefixed_fact(content, "Question:"):
            questions.append(
                TranscriptQuestion(
                    question=question,
                    confidence=0.75,
                    evidence_refs=[evidence],
                )
            )
            spans.append(span)

    return TranscriptExtractionResult(
        transcript_id=transcript_id,
        actions=actions,
        decisions=decisions,
        risks=risks,
        questions=questions,
        spans=spans,
    )


def _iter_lines_with_offsets(text: str) -> list[tuple[str, int]]:
    lines: list[tuple[str, int]] = []
    offset = 0
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        if line.strip():
            lines.append((line, offset))
        offset += len(raw_line)
    return lines


def _parse_speaker_turn(line: str) -> tuple[str | None, str]:
    speaker, separator, content = line.partition(":")
    if separator and speaker.strip():
        return speaker.strip(), content.strip()
    return None, line.strip()


def _build_span(
    *,
    transcript_id: str,
    sequence: int,
    start_offset: int,
    text: str,
    speaker: str | None,
) -> TranscriptSpan:
    return TranscriptSpan(
        span_id=f"span-{sequence:03d}",
        transcript_id=transcript_id,
        start_offset=start_offset,
        end_offset=start_offset + len(text),
        text_hash=f"sha256:{hashlib.sha256(text.encode()).hexdigest()}",
        speaker=speaker,
    )


def _build_evidence(*, span: TranscriptSpan, quote: str) -> EvidenceRef:
    return EvidenceRef(
        evidence_id=f"ev-{span.span_id}",
        source_type="transcript_span",
        source_ref=span.span_id,
        quote=quote,
        relevance="Direct transcript evidence for extracted meeting fact.",
    )


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().rstrip(".")
    return cleaned or None


def _strip_prefixed_fact(content: str, prefix: str) -> str | None:
    if not content.startswith(prefix):
        return None
    fact = content.removeprefix(prefix).strip()
    return fact or None


__all__ = [
    "TranscriptExtractionError",
    "TranscriptExtractionResult",
    "extract_meeting_transcript",
]
