"""Workflow domain — pipeline definitions, runs, and phase executions."""

from raise_core.workflow.coverage import CoverageResult, run_coverage_checks
from raise_core.workflow.models import (
    ContextGraphSpec,
    ExecutionConfig,
    GateDefinition,
    PhaseContextSpec,
    PhaseDefinition,
    PhaseExecution,
    PhaseResult,
    PipelineDefinition,
    PipelineRun,
    RunStatus,
    ShuHariOverride,
    TerminationReason,
    TransitionRecord,
)
from raise_core.workflow.state_machine import StateSpec, WorkflowStateMachine
from raise_core.workflow.status_sets import ACTIVE_RUN_STATUSES, TERMINAL_RUN_STATUSES

__all__ = [
    "ACTIVE_RUN_STATUSES",
    "ContextGraphSpec",
    "CoverageResult",
    "ExecutionConfig",
    "GateDefinition",
    "PhaseContextSpec",
    "PhaseDefinition",
    "PhaseExecution",
    "PhaseResult",
    "PipelineDefinition",
    "PipelineRun",
    "RunStatus",
    "ShuHariOverride",
    "StateSpec",
    "TERMINAL_RUN_STATUSES",
    "TerminationReason",
    "TransitionRecord",
    "WorkflowStateMachine",
    "run_coverage_checks",
]
