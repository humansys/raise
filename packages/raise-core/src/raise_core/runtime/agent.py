"""Governed Rai-Agent run and evidence contracts.

These models describe workflow state for governed agentic work. They are
separate from ``RunConfig`` / ``RunResult``, which describe low-level runtime
invocation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AgentActor = Literal["human", "agent", "tool", "system"]
AgentRunStatus = Literal[
    "created",
    "extracting",
    "planning",
    "awaiting_hitl",
    "executing",
    "completed",
    "failed",
    "cancelled",
]
AgentArtifactType = Literal[
    "transcript",
    "extraction",
    "operation_plan",
    "hitl_request",
    "execution_result",
    "summary",
    "other",
]
EvidenceSourceType = Literal["transcript_span", "kc_node", "backlog_issue", "artifact"]
SourceAuthority = Literal["local", "remote"]
TranscriptRiskSeverity = Literal["low", "medium", "high", "unknown"]


class TranscriptSpan(BaseModel):
    """Stable reference to a span inside a transcript artifact."""

    model_config = ConfigDict(frozen=True)

    span_id: str = Field(..., min_length=1)
    transcript_id: str = Field(..., min_length=1)
    start_offset: int = Field(..., ge=0)
    end_offset: int = Field(..., ge=0)
    text_hash: str = Field(..., min_length=1)
    speaker: str | None = None
    timestamp: str | None = None

    @model_validator(mode="after")
    def _validate_offsets(self) -> TranscriptSpan:
        if self.end_offset < self.start_offset:
            msg = "end_offset must be greater than or equal to start_offset"
            raise ValueError(msg)
        return self


class EvidenceRef(BaseModel):
    """Reference to evidence used to justify a claim or operation."""

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(..., min_length=1)
    source_type: EvidenceSourceType
    source_ref: str = Field(..., min_length=1)
    quote: str = ""
    relevance: str = Field(..., min_length=1)


class AgentArtifactRef(BaseModel):
    """Reference to an artifact produced or consumed by a Rai-Agent run."""

    model_config = ConfigDict(frozen=True)

    artifact_id: str = Field(..., min_length=1)
    artifact_type: AgentArtifactType
    uri: str = Field(..., min_length=1)
    media_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeCartridgeBinding(BaseModel):
    """Knowledge cartridge metadata bound to a governed agent run."""

    model_config = ConfigDict(frozen=True)

    cartridge_name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    org_id: str | None = None
    project_id: str | None = None
    source_authority: SourceAuthority
    valid_from: datetime | None = None
    superseded_at: datetime | None = None
    allowed_uses: list[str] = Field(default_factory=list)


class MeetingBacklogRun(BaseModel):
    """Governed run state for the meeting-to-backlog Rai-Agent workflow."""

    model_config = ConfigDict(frozen=True)

    run_id: str = Field(..., min_length=1)
    status: AgentRunStatus
    transcript_artifact: AgentArtifactRef
    cartridge_bindings: list[KnowledgeCartridgeBinding]
    created_by: str = Field(..., min_length=1)
    created_at: datetime
    updated_at: datetime


class AgentRunEvent(BaseModel):
    """Append-only event describing what happened during a governed run."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(..., min_length=1)
    run_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime
    actor: AgentActor
    summary: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    artifact_refs: list[AgentArtifactRef] = Field(default_factory=list)
    work_item_ref: str | None = None


class _EvidenceBearingTranscriptItem(BaseModel):
    """Base model for extracted transcript items that require evidence."""

    model_config = ConfigDict(frozen=True)

    evidence_refs: list[EvidenceRef] = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)


class TranscriptAction(_EvidenceBearingTranscriptItem):
    """Action item extracted from a transcript."""

    title: str = Field(..., min_length=1)
    owner: str | None = None
    due_date: str | None = None


class TranscriptDecision(_EvidenceBearingTranscriptItem):
    """Decision extracted from a transcript."""

    decision: str = Field(..., min_length=1)
    rationale: str = ""


class TranscriptRisk(_EvidenceBearingTranscriptItem):
    """Risk extracted from a transcript."""

    risk: str = Field(..., min_length=1)
    severity: TranscriptRiskSeverity = "unknown"


class TranscriptQuestion(_EvidenceBearingTranscriptItem):
    """Unresolved question extracted from a transcript."""

    question: str = Field(..., min_length=1)


__all__ = [
    "AgentActor",
    "AgentArtifactRef",
    "AgentArtifactType",
    "AgentRunEvent",
    "AgentRunStatus",
    "EvidenceRef",
    "EvidenceSourceType",
    "KnowledgeCartridgeBinding",
    "MeetingBacklogRun",
    "SourceAuthority",
    "TranscriptAction",
    "TranscriptDecision",
    "TranscriptQuestion",
    "TranscriptRisk",
    "TranscriptRiskSeverity",
    "TranscriptSpan",
]
