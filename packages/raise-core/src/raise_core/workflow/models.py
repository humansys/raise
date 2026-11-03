"""Pipeline domain models.

Pure data models for pipeline definitions, runs, and phase executions.
No business logic beyond validation. No I/O. No dependencies on rai-agent.

Story: S1064.1 — Pipeline Domain Models (RAISE-1073)
Epic: E1064 — Pipeline Engine Core
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RunStatus(StrEnum):
    """Pipeline run lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED_HITL = "paused_hitl"
    COMPLETED = "completed"
    FAILED = "failed"


class DelegationLevel(StrEnum):
    """How much autonomy the pipeline has at HITL gates."""

    REVIEW = "REVIEW"
    NOTIFY = "NOTIFY"
    AUTO = "AUTO"


class HitlDecision(BaseModel, frozen=True):
    """Immutable record of a human decision at an HITL gate."""

    phase_id: str
    decision: Literal["approve", "revise", "reject"]
    actor: str
    timestamp: datetime
    message: str | None = None


class TerminationReason(StrEnum):
    """Why a phase ended — distinguishes normal completion from limits.

    CC SAR F15: observable diagnostics for phase termination.
    """

    COMPLETED = "completed"
    BUDGET_EXCEEDED = "budget_exceeded"
    TURNS_EXCEEDED = "turns_exceeded"
    GATE_FAILED = "gate_failed"
    GATE_CRASHED = "gate_crashed"
    ERROR = "error"


class ExecutionConfig(BaseModel):
    """Pipeline execution settings."""

    parallel: bool = False
    max_parallel: int = 1
    worktree_isolation: bool = True
    branch_pattern: str = "story/{issue_id}/{slug}"


class GateDefinition(BaseModel):
    """Quality gate between phases.

    ``impact`` (ADR-093 K2): hitl gates with ``low`` impact are
    auto-approved by ``pipeline_advance`` with recorded evidence;
    ``high`` (the conservative default) always requires a human.
    """

    type: Literal["deterministic", "hitl"] = "deterministic"
    level: Literal["AUTO", "NOTIFY", "REVIEW", "APPROVE"] = "REVIEW"
    impact: Literal["high", "low"] = "high"
    commands: list[str] = []
    on_fail: Literal["retry", "rework", "stop"] = "stop"
    max_retries: int = 1
    mandatory: bool = False


class ShuHariOverride(BaseModel):
    """Mastery-level gate behavior override."""

    gate: GateDefinition | None = None
    max_turns: int | None = None
    skip_if: str | None = None


class PhaseResult(BaseModel):
    """Result of executing a single phase."""

    success: bool
    output: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    termination_reason: TerminationReason = TerminationReason.COMPLETED


class ArtifactRequirement(BaseModel, frozen=True):
    """Required artifact for phase completion — glob-pattern or SQLite form.

    Used by pipeline_advance to validate that expected deliverables
    exist before allowing phase advancement (gated notes pattern).
    Three mutually-exclusive shapes (RAISE-11147, RAISE-15496):
    - glob: ``{"pattern": ..., "description": ...}``
    - alternative globs: ``{"patterns": [...], "description": ...}`` —
      satisfied when any listed pattern matches
    - sqlite: ``{"store": "sqlite", "type": ..., "description": ...}`` —
      checked against ``ArtifactStore`` (issue-scoped by construction)
      instead of a repo-wide file glob.
    """

    pattern: str | None = None
    """Glob pattern relative to CWD, e.g. ``**/*-design.md``. Mutually
    exclusive with ``patterns`` and ``store``."""

    patterns: list[str] = Field(default_factory=list)
    """Alternative glob patterns relative to CWD. At least one must match.
    Mutually exclusive with ``pattern`` and ``store``."""

    store: Literal["sqlite"] | None = None
    """Set to ``"sqlite"`` to check a structured artifact via ``ArtifactStore``
    instead of a file glob. Requires ``type``."""

    type: str | None = None
    """Artifact type key (e.g. ``"implement"``, ``"retro"``) — required
    when ``store`` is set."""

    description: str = ""
    """Human-readable description, e.g. "Story design document"."""

    @model_validator(mode="after")
    def _pattern_or_store(self) -> Self:
        source_count = sum(
            (bool(self.pattern), bool(self.patterns), self.store is not None)
        )
        if source_count != 1:
            msg = (
                "ArtifactRequirement: set exactly one of 'pattern', "
                "'patterns', or 'store'+'type'"
            )
            raise ValueError(msg)
        if self.patterns and any(not pattern for pattern in self.patterns):
            msg = "ArtifactRequirement: 'patterns' entries must be non-empty"
            raise ValueError(msg)
        if self.store is not None and not self.type:
            msg = "ArtifactRequirement: 'store' requires 'type'"
            raise ValueError(msg)
        return self


class ContextGraphSpec(BaseModel, frozen=True):
    """Declarative graph query for a pipeline phase.

    Specifies what node types to retrieve and how many.
    """

    types: list[str] = []
    """Node types to query: pattern, module, decision, guardrail, etc."""

    limit: int = 3
    """Maximum results for this query."""


class TransitionRecord(BaseModel, frozen=True):
    """Immutable record of a backlog status transition attempt.

    Captures the intent, outcome, and idempotence evidence for
    workflow-driven state transitions during a phase.

    Story: S1 (RAISE-15028) — Foundation models
    """

    phase_id: str
    """Phase that initiated the transition."""

    issue_key: str
    """Issue/work item being transitioned."""

    from_status: str
    """Status slug before transition."""

    to_slug: str
    """Target status slug."""

    outcome: Literal["applied", "noop", "skipped", "illegal", "failed", "drift-noop"]
    """Transition outcome:
    - applied: successfully transitioned
    - noop: idempotent re-apply (current == target)
    - skipped: no target_status defined for phase
    - illegal: transition violates state machine rules
    - failed: adapter raised an exception
    - drift-noop: current ahead of target (already passed it)
    """

    verified: bool = False
    """Read-back confirmation that adapter reflected the change."""

    message: str = ""
    """Diagnostic: reason code or error message."""

    timestamp: datetime
    """When the transition was attempted."""

    remote_synced: bool | None = None
    """Adapter delivery signal copied from IssueRef.remote_synced.
    True = landed on remote; False = queued locally for later replay;
    None = adapter did not report / no IssueRef returned (Stage 1 default).
    Typed so PMO consumers never parse message strings for delivery state."""


class PhaseContextSpec(BaseModel, frozen=True):
    """Declarative context specification for a pipeline phase.

    Defines what knowledge graph queries to run when building
    phase context during pipeline_advance.
    """

    graph: list[ContextGraphSpec] = []
    """Graph queries to execute for this phase."""


class PhaseDefinition(BaseModel):
    """Single phase in a pipeline."""

    model_config = ConfigDict(extra="forbid")

    id: str
    type: Literal["llm", "deterministic"]
    skill: str | None = None
    prompt: str | None = None
    commands: list[str] = []
    model: str | None = None
    max_turns: int = 50
    max_budget_usd: float = 5.0
    gate: GateDefinition | None = None
    validates: list[ArtifactRequirement] = []
    shuhari: dict[str, ShuHariOverride] = {}
    when: str | None = None
    workflow_point: str | None = None
    quality_gates: list[str] = []
    gate_mode: Literal["blocking", "advisory"] = "blocking"
    depends_on: list[str] = []
    context: PhaseContextSpec | None = None
    review_mode: Literal["adversarial"] | None = None
    review_template: str | None = None
    target_status: str | None = None
    """Target backlog status slug for workflow-driven transitions.
    When set, engine will attempt to transition issue to this status
    after phase passes. None means no transition (advisory governance only)."""
    transition_mode: Literal["blocking", "advisory"] = "advisory"
    """Whether a transition failure blocks phase advancement."""
    post_transition: list[str] = Field(default_factory=list)
    """Phase IDs to run only if this phase's transition succeeds.
    Ignored in Stage 1; implemented in Stage 2."""
    pipeline: str | None = None
    foreach: Literal["stories"] | None = None
    success_policy: Literal["all_success"] = "all_success"
    harness: str | None = None
    """Harness override for this phase (e.g. 'cursor', 'codex').
    When None, falls back to developer profile harness or CC default."""

    @model_validator(mode="after")
    def _skill_prompt_pipeline_exclusive(self) -> Self:
        dispatch_fields = [
            f for f in ("skill", "prompt", "pipeline") if getattr(self, f) is not None
        ]
        if len(dispatch_fields) > 1:
            msg = (
                f"{', '.join(dispatch_fields)} are mutually exclusive — set at most one"
            )
            raise ValueError(msg)
        if self.foreach is not None and self.pipeline is None:
            msg = "foreach requires pipeline — set pipeline when using foreach"
            raise ValueError(msg)
        return self


class PipelineDefinition(BaseModel):
    """Complete pipeline definition loaded from YAML."""

    name: str
    description: str = ""
    issue_types: list[str] = []
    model: str = "claude-sonnet-4-6"
    defaults: dict[str, str] = {}
    execution: ExecutionConfig = ExecutionConfig()
    phases: list[PhaseDefinition]

    @model_validator(mode="after")
    def _reject_cyclic_deps(self) -> Self:
        """Detect cycles in phase depends_on using DFS."""
        graph: dict[str, list[str]] = {p.id: list(p.depends_on) for p in self.phases}

        visited: set[str] = set()
        in_stack: set[str] = set()

        def _dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor in in_stack:
                    return True
                if neighbor not in visited and _dfs(neighbor):
                    return True
            in_stack.discard(node)
            return False

        for phase_id in graph:
            if phase_id not in visited and _dfs(phase_id):
                msg = "cyclic dependency detected in phase depends_on"
                raise ValueError(msg)

        return self


class PhaseExecution(BaseModel):
    """Runtime state of a single phase within a run."""

    phase_id: str
    status: Literal["pending", "running", "passed", "failed", "skipped"] = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: PhaseResult | None = None
    gate_result_passed: bool | None = None
    gate_result_message: str = ""
    error: str | None = None
    retries: int = 0
    hitl_decision: HitlDecision | None = None
    backlog_transition: TransitionRecord | None = None
    """Record of workflow-driven status transition for this phase.
    Populated by engine after apply_phase_transition (Stage 1+)."""


_TERMINAL_STATUSES = frozenset({"passed", "failed", "skipped"})


class PipelineRun(BaseModel):
    """Runtime state of a pipeline execution."""

    run_id: str
    pipeline_name: str
    status: RunStatus = RunStatus.PENDING
    issue_id: str | None = None
    worktree_path: Path | None = None
    branch: str | None = None
    phases: dict[str, PhaseExecution] = {}
    started_at: datetime | None = None
    completed_at: datetime | None = None
    paused_at_phase: str | None = None
    trace_dir: Path | None = None
    final_commit: str | None = None
    metadata: dict[str, str] = {}

    @property
    def current_phase(self) -> str | None:
        """First non-terminal phase."""
        for phase_id, execution in self.phases.items():
            if execution.status not in _TERMINAL_STATUSES:
                return phase_id
        return None

    @property
    def total_cost_usd(self) -> float:
        """Sum of all phase costs."""
        return sum(
            ex.result.cost_usd for ex in self.phases.values() if ex.result is not None
        )
