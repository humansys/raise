"""Runtime contracts and Protocols for agent runtimes.

Public API:
    RaiAgentRuntime        — Protocol for swappable agent runtimes
    RunConfig              — Input contract for agent dispatch
    RunResult              — Result with session, usage, and cost metrics
    AgentTelemetryAdapter  — Protocol for cross-runtime telemetry (ADR-062)
    RawSessionWindow       — Normalized session metrics DTO
    ModelCostBreakdown     — Per-model cost breakdown DTO
    AgentRunEvent          — Governed Rai-Agent run event
    MeetingBacklogRun      — Meeting-to-backlog governed run state
    EvidenceRef            — Source-backed evidence reference
    TranscriptSpan         — Stable transcript source span
    TranscriptExtractionResult — Meeting transcript extraction output
    extract_meeting_transcript — Deterministic transcript extraction helper

Extracted from rai_agent.runtime (RAISE-1430, S1305.8).
Canonical location since v3.0.0a1.
"""

from raise_core.runtime.agent import (
    AgentActor,
    AgentArtifactRef,
    AgentArtifactType,
    AgentRunEvent,
    AgentRunStatus,
    EvidenceRef,
    EvidenceSourceType,
    KnowledgeCartridgeBinding,
    MeetingBacklogRun,
    SourceAuthority,
    TranscriptAction,
    TranscriptDecision,
    TranscriptQuestion,
    TranscriptRisk,
    TranscriptRiskSeverity,
    TranscriptSpan,
)
from raise_core.runtime.models import RunConfig, RunResult
from raise_core.runtime.protocol import RaiAgentRuntime
from raise_core.runtime.telemetry_adapter import (
    AgentTelemetryAdapter,
    ModelCostBreakdown,
    RawSessionWindow,
)
from raise_core.runtime.transcript import (
    TranscriptExtractionError,
    TranscriptExtractionResult,
    extract_meeting_transcript,
)

__all__ = [
    "AgentActor",
    "AgentArtifactRef",
    "AgentArtifactType",
    "AgentRunEvent",
    "AgentRunStatus",
    "AgentTelemetryAdapter",
    "EvidenceRef",
    "EvidenceSourceType",
    "KnowledgeCartridgeBinding",
    "MeetingBacklogRun",
    "ModelCostBreakdown",
    "RaiAgentRuntime",
    "RawSessionWindow",
    "RunConfig",
    "RunResult",
    "SourceAuthority",
    "TranscriptAction",
    "TranscriptDecision",
    "TranscriptExtractionError",
    "TranscriptExtractionResult",
    "TranscriptQuestion",
    "TranscriptRisk",
    "TranscriptRiskSeverity",
    "TranscriptSpan",
    "extract_meeting_transcript",
]
