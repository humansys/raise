"""Pipeline engine — orchestrates phase execution.

Story: S1064.3 — Pipeline Engine Core (RAISE-1075)
Story: S1064.8 — CLI Integration & Dogfooding (RAISE-1080)
Epic: E1064 — Pipeline Engine Core

S1064.8 enhancement: gate evaluation, state persistence, worktree lifecycle.
Design decision D7: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from raise_cli.pipeline.epic_story_iteration import pending_epic_stories
from raise_cli.pipeline.executor import PhaseExecutor
from raise_cli.pipeline.gates import evaluate_gate
from raise_cli.pipeline.loader import PipelineError, PipelineLoader
from raise_cli.pipeline.run_store import PipelineRunStore
from raise_cli.pipeline.transitions import (
    TransitionDepsProvider,
    apply_phase_transition_async,
    resolve_transition_deps,
)
from raise_cli.pipeline.worktree import WorktreeManager
from raise_core.workflow.models import (
    DelegationLevel,
    HitlDecision,
    PhaseExecution,
    PipelineDefinition,
    PipelineRun,
    RunStatus,
)
from raise_core.workflow.state_machine import WorkflowStateMachine

logger = logging.getLogger(__name__)

# ─── When conditional support (S1065.3) ──────────────────────────────────────

_WHEN_RE_EQ = re.compile(r"^(\w+)\s*==\s*'([^']*)'$")
_WHEN_RE_NEQ = re.compile(r"^(\w+)\s*!=\s*'([^']*)'$")
# Proportionality aspect (ADR-116): ordinal `size >= X` / `size > X`.
_WHEN_RE_SIZE = re.compile(r"^size\s*(>=|>)\s*([A-Za-z]+)$")

# Fixed ordinal size scale. Unknown/missing size resolves to the largest tier so
# nothing is ever silently skipped on ambiguity (fail-safe toward MORE ceremony).
_SIZE_ORDER: tuple[str, ...] = ("XS", "S", "M", "L")

_POST_TRANSITION_WORKFLOW_POINTS: dict[str, str] = {
    "before:bug:close": "after:bug:close",
}


def _size_rank(value: str) -> int:
    """Rank a size on the fixed scale; unknown/missing → largest (fail-safe)."""
    try:
        return _SIZE_ORDER.index(value.strip().upper())
    except ValueError:
        return len(_SIZE_ORDER) - 1


def evaluate_when(expr: str, context: dict[str, str]) -> bool:
    """Evaluate a simple when expression against a context dict.

    Supports ``key == 'value'``, ``key != 'value'``, and the ordinal size
    predicate ``size >= X`` / ``size > X`` over the scale XS < S < M < L
    (ADR-116). Missing ``size`` resolves to the largest tier (fail-safe).
    Other missing keys resolve to empty string.
    """
    expr = expr.strip()

    match = _WHEN_RE_EQ.match(expr)
    if match:
        key, value = match.group(1), match.group(2)
        return context.get(key, "") == value

    match = _WHEN_RE_NEQ.match(expr)
    if match:
        key, value = match.group(1), match.group(2)
        return context.get(key, "") != value

    match = _WHEN_RE_SIZE.match(expr)
    if match:
        op, threshold = match.group(1), match.group(2)
        actual = _size_rank(context.get("size", ""))
        wanted = _size_rank(threshold)
        return actual >= wanted if op == ">=" else actual > wanted

    logger.warning("Unsupported when expression (treating as True): %s", expr)
    return True


def post_transition_workflow_point(workflow_point: str | None) -> str | None:
    """Return the blocking postcondition point paired with a pre-transition point."""
    if workflow_point is None:
        return None
    return _POST_TRANSITION_WORKFLOW_POINTS.get(workflow_point)


class PipelineEngine:
    """Orchestrates sequential phase execution for a named pipeline.

    Loads a pipeline definition via the loader, then runs each phase
    through the executor. Stops on first phase failure or gate failure.

    S1064.8 enhancement: optional state_store and worktree_manager enable
    gate evaluation, state persistence, and worktree lifecycle. When not
    provided, the engine operates in minimal mode (backward compat with S3).

    Args:
        loader: Resolves pipeline names to definitions.
        executor: Executes individual phases.
        state_store: Optional — persists run state after each phase.
        worktree_manager: Optional — creates/cleans worktrees.
    """

    def __init__(
        self,
        loader: PipelineLoader,
        executor: PhaseExecutor,
        state_store: PipelineRunStore | None = None,
        worktree_manager: WorktreeManager | None = None,
        *,
        transition_deps_provider: TransitionDepsProvider = resolve_transition_deps,
        transitions_enabled: bool = True,
    ) -> None:
        self._loader = loader
        self._executor = executor
        self._state_store = state_store
        self._worktree_manager = worktree_manager
        self._transition_deps_provider = transition_deps_provider
        self._transitions_enabled = transitions_enabled

    async def run(
        self,
        name: str,
        issue_id: str | None = None,
        *,
        is_interactive: bool = False,
        delegation_level: DelegationLevel = DelegationLevel.REVIEW,
        metadata: dict[str, str] | None = None,
    ) -> PipelineRun:
        """Load and execute a pipeline by name.

        Args:
            name: Pipeline name (resolved via loader).
            issue_id: Optional issue identifier for traceability.
            is_interactive: Whether a terminal is available for HITL prompts.
            delegation_level: How much autonomy at HITL gates.
            metadata: Optional key/value pairs persisted on the PipelineRun
                (e.g. CC session id, story slug) for later correlation.

        Returns:
            Completed PipelineRun with phase results.
        """
        pipeline = self._loader.load(name)

        # T4 (RAISE-14938): fail-closed quality_gates ID validation before
        # any phase executes. PipelineError propagates to the caller unchanged.
        from raise_cli.gates.execution import validate_quality_gate_ids

        validate_quality_gate_ids(pipeline.phases)

        run = PipelineRun(
            run_id=str(uuid4()),
            pipeline_name=pipeline.name,
            status=RunStatus.RUNNING,
            issue_id=issue_id,
            started_at=datetime.now(UTC),
            phases={p.id: PhaseExecution(phase_id=p.id) for p in pipeline.phases},
            metadata=metadata or {},
        )

        # Worktree lifecycle
        worktree_path: Path | None = None
        if (
            self._worktree_manager
            and issue_id
            and pipeline.execution.worktree_isolation
        ):
            branch = pipeline.execution.branch_pattern.format(
                issue_id=issue_id.replace("/", "--"),
                slug=pipeline.name,
            )
            try:
                worktree_path = await self._worktree_manager.create(
                    branch=branch,
                    base="HEAD",
                )
                run.worktree_path = worktree_path
                run.branch = branch
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("Worktree creation failed: %s", exc)

        try:
            await self._execute_phases(
                pipeline,
                run,
                worktree_path,
                is_interactive=is_interactive,
                delegation_level=delegation_level,
            )
        finally:
            if self._worktree_manager and run.branch:
                try:
                    await self._worktree_manager.cleanup(run.branch)
                except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                    logger.warning("Worktree cleanup failed: %s", exc)

        return run

    async def _execute_phases(  # noqa: C901 -- sequential phase loop: when-skip, gate eval (hitl-pause/crash/fail), and workflow-point enforcement are one linear flow; splitting fragments the per-phase state machine
        self,
        pipeline: PipelineDefinition,
        run: PipelineRun,
        worktree_path: Path | None,
        *,
        is_interactive: bool = False,
        delegation_level: DelegationLevel = DelegationLevel.REVIEW,
    ) -> None:
        """Execute all phases sequentially with gate evaluation and state persistence."""
        # Merge pipeline defaults with run metadata (caller overrides defaults)
        if pipeline.defaults:
            merged = {**pipeline.defaults, **run.metadata}
            run.metadata = merged

        from raise_cli.project import resolve_project_root

        all_passed = True
        cwd = worktree_path or resolve_project_root()
        _deps = self._transition_deps(cwd)

        for phase_def in pipeline.phases:
            execution = run.phases[phase_def.id]

            # When conditional (S1065.3): skip phase if condition is false
            if phase_def.when is not None and not evaluate_when(
                phase_def.when, run.metadata
            ):
                execution.status = "skipped"
                execution.completed_at = datetime.now(UTC)
                await self._save_state(run)
                logger.info("Phase %s skipped (when: %s)", phase_def.id, phase_def.when)
                continue

            execution.status = "running"
            execution.started_at = datetime.now(UTC)

            result = await self._executor.execute(phase_def, run, pipeline.execution)

            execution.result = result
            execution.completed_at = datetime.now(UTC)

            if result.success:
                execution.status = "passed"
            else:
                execution.status = "failed"
                all_passed = False
                await self._save_state(run)
                break

            # Gate evaluation (S1064.8, S1065.1 HITL)
            if phase_def.gate is not None:
                gate_eval = await evaluate_gate(
                    phase_def.gate,
                    cwd=cwd,
                    is_interactive=is_interactive,
                    delegation_level=delegation_level,
                )
                execution.gate_result_passed = gate_eval.passed
                execution.gate_result_message = gate_eval.message

                if gate_eval.passed and phase_def.gate.type == "hitl":
                    # Sync HITL approve — log the decision
                    execution.hitl_decision = HitlDecision(
                        phase_id=phase_def.id,
                        decision="approve",
                        actor="terminal" if is_interactive else "auto",
                        timestamp=datetime.now(UTC),
                        message=gate_eval.message,
                    )

                if not gate_eval.passed:
                    if gate_eval.hitl_paused:
                        # Async HITL: save state and return
                        execution.status = "pending"
                        run.status = RunStatus.PAUSED_HITL
                        run.paused_at_phase = phase_def.id
                        await self._save_state(run)
                        logger.info(
                            "Pipeline paused at HITL gate: phase=%s, run_id=%s",
                            phase_def.id,
                            run.run_id,
                        )
                        return  # exit without setting completed_at
                    if gate_eval.crashed:
                        execution.status = "failed"
                        execution.error = f"Gate crashed: {gate_eval.message}"
                    else:
                        execution.status = "failed"
                        execution.error = f"Gate failed: {gate_eval.message}"
                    all_passed = False
                    await self._save_state(run)
                    break

            # Workflow-point enforcement parity with the MCP _advance_once path
            # (RAISE-12207): a phase bound to a before-point emits it in-process
            # so its point-bound gates are engine-forced. Abort => phase failure.
            if phase_def.workflow_point is not None and not self.enforce_workflow_point(
                phase_def.workflow_point,
                run.issue_id,
                cwd,
                run.metadata.get("agent_session_id"),
            ):
                execution.status = "failed"
                execution.error = (
                    f"Workflow-point gates failed: {phase_def.workflow_point}"
                )
                all_passed = False
                await self._save_state(run)
                break

            # quality_gates execution (RAISE-14934 T5): declarative gates declared
            # in phase definition run after workflow_point enforcement.
            if phase_def.quality_gates:
                from raise_cli.gates.execution import blocking_failures, run_gates_by_id

                _qg = run_gates_by_id(
                    phase_def.quality_gates,
                    cwd,
                    session_id=run.metadata.get("agent_session_id"),
                )
                _qg_blocking = blocking_failures(_qg, phase_def.gate_mode)
                if _qg_blocking:
                    execution.status = "failed"
                    execution.error = "quality_gates blocked: " + "; ".join(
                        f"{r.gate_id}: {r.message}" for r in _qg_blocking
                    )
                    all_passed = False
                    await self._save_state(run)
                    break
                if any(not r.passed for r in _qg):
                    logger.info(
                        "quality_gates advisory: phase=%s gates=%s",
                        phase_def.id,
                        [r.gate_id for r in _qg if not r.passed],
                    )

            # Backlog transition (S3, RAISE-15030 → S10 RAISE-15037 blocking).
            # blocking mode: halt run on failed/illegal outcome.
            _transition_halted = await self._record_phase_transition(
                phase_def, run, execution, _deps
            )
            saved = await self._save_state(run)
            if not saved and execution.backlog_transition is not None:
                logger.warning(
                    "transition-record-not-persisted: run=%s phase=%s outcome=%s",
                    run.run_id,
                    phase_def.id,
                    execution.backlog_transition.outcome,
                )
            if _transition_halted:
                execution.status = "failed"
                execution.error = (
                    f"blocking transition failed: phase={phase_def.id} "
                    f"outcome={execution.backlog_transition.outcome if execution.backlog_transition else 'unknown'}"
                )
                all_passed = False
                await self._save_state(run)
                break

            _post_point = post_transition_workflow_point(phase_def.workflow_point)
            if (
                _post_point is not None
                and phase_def.target_status is not None
                and self._transitions_enabled
                and not self.enforce_workflow_point(
                    _post_point,
                    run.issue_id,
                    cwd,
                    run.metadata.get("agent_session_id"),
                )
            ):
                execution.status = "failed"
                execution.error = f"Workflow-point gates failed: {_post_point}"
                all_passed = False
                await self._save_state(run)
                break

        run.completed_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETED if all_passed else RunStatus.FAILED
        await self._save_state(run)

    @staticmethod
    def enforce_workflow_point(
        workflow_point: str,
        issue_id: str | None,
        cwd: Path,
        session_id: str | None = None,
    ) -> bool:
        """Enforce a phase's bound workflow point in-process.

        Before-points route through GateBridgeHook. Post-transition points run
        the same gate seam directly because an ``after:`` hook cannot abort an
        operation that already happened; the engine still blocks phase
        completion when its postcondition fails.
        """
        if workflow_point.startswith("after:"):
            from raise_cli.gates.execution import run_gates_for_point

            report = run_gates_for_point(
                workflow_point,
                cwd,
                session_id=session_id,
                issue_id=issue_id,
            )
            return not report.failures

        from raise_cli.hooks.emitter import create_emitter
        from raise_cli.hooks.events import (
            BeforeBugCloseEvent,
            BeforeInitiativeConcludedEvent,
            BeforeInitiativeValidatedEvent,
            BeforeStoryCloseEvent,
        )

        # S14263.6 (RAISE-14712): advisory points — engine emits and runs
        # gates but never aborts the phase on gate failure (mirrors CI
        # allow_failure:true, ADR-130 D2). Parity with mcp_tools_pipeline.py.
        _advisory: frozenset[str] = frozenset({"before:story:close"})

        event_map = {
            "before:bug:close": BeforeBugCloseEvent,
            "before:story:close": BeforeStoryCloseEvent,
            "before:initiative:validated": BeforeInitiativeValidatedEvent,
            "before:initiative:concluded": BeforeInitiativeConcludedEvent,
        }
        event_cls = event_map.get(workflow_point)
        if event_cls is None:
            return True
        result = create_emitter().emit(
            event_cls(
                issue_id=issue_id or "",
                working_dir=str(cwd),
                session_id=session_id,
            )
        )
        if workflow_point in _advisory:
            return True  # advisory — run gates, log, but never abort
        return not result.aborted

    async def resume(
        self,
        run_id: str,
        decision: HitlDecision,
    ) -> PipelineRun:
        """Resume a paused pipeline run.

        Loads the saved run state, validates it's PAUSED_HITL,
        applies the decision, and continues execution from the paused phase.

        Args:
            run_id: ID of the paused run.
            decision: Human decision (approve/revise/reject).

        Returns:
            PipelineRun after decision is applied and remaining phases execute.

        Raises:
            PipelineError: If run not found, not in PAUSED_HITL state, or no state store.
        """
        if self._state_store is None:
            msg = "Cannot resume without a state store"
            raise PipelineError(msg)

        run, paused_phase, execution = await self._load_paused_run(run_id)

        # Log the decision on the paused phase (C1: override phase_id)
        execution.hitl_decision = (
            decision.model_copy(update={"phase_id": paused_phase})
            if decision.phase_id != paused_phase
            else decision
        )

        if decision.decision == "reject":
            await self._reject_paused_run(run, execution, decision)
            return run

        # approve or revise: continue execution
        run.status = RunStatus.RUNNING
        run.paused_at_phase = None

        pipeline = self._loader.load(run.pipeline_name)

        # Find the resume point
        phase_ids = [p.id for p in pipeline.phases]
        paused_index = phase_ids.index(paused_phase)

        if decision.decision == "revise":
            # Re-execute from paused phase
            resume_index = paused_index
            execution.status = "pending"  # reset for re-execution
        else:
            if not await self._resume_epic_story_iteration_if_complete(
                run, execution, paused_phase
            ):
                return run
            # approve: mark paused phase as passed, continue from next
            execution.status = "passed"
            # Backlog transition for the approved phase (RAISE-15030 / S10 blocking)
            from raise_cli.project import resolve_project_root as _rpr

            _cwd = run.worktree_path or _rpr()
            _approved_phase_def = pipeline.phases[paused_index]
            _rdeps = self._transition_deps(_cwd)
            _approve_halted = await self._record_phase_transition(
                _approved_phase_def, run, execution, _rdeps
            )
            _rs = await self._save_state(run)
            if not _rs and execution.backlog_transition is not None:
                logger.warning(
                    "transition-record-not-persisted: run=%s phase=%s outcome=%s",
                    run.run_id,
                    _approved_phase_def.id,
                    execution.backlog_transition.outcome,
                )
            if _approve_halted:
                execution.status = "failed"
                execution.error = (
                    f"blocking transition failed on approve: phase={_approved_phase_def.id} "
                    f"outcome={execution.backlog_transition.outcome if execution.backlog_transition else 'unknown'}"
                )
                run.status = RunStatus.FAILED
                run.completed_at = datetime.now(UTC)
                await self._state_store.save(run.model_dump(mode="json"))
                return run
            resume_index = paused_index + 1

        if resume_index >= len(pipeline.phases):
            # No more phases
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.now(UTC)
            await self._state_store.save(run.model_dump(mode="json"))
            return run

        # Execute remaining phases.
        # QR R2: resume always runs non-interactive (is_interactive=False,
        # delegation_level=REVIEW). This is intentional — async resume callers
        # are not sitting at a terminal expecting prompts. If a downstream
        # HITL gate is hit, it will pause again for another resume cycle.
        remaining_phases = pipeline.phases[resume_index:]
        remaining_pipeline = pipeline.model_copy(update={"phases": remaining_phases})

        # Ensure remaining phases have execution entries
        for p in remaining_phases:
            if p.id not in run.phases:
                run.phases[p.id] = PhaseExecution(phase_id=p.id)

        from raise_cli.project import resolve_project_root

        cwd = run.worktree_path or resolve_project_root()
        await self._execute_phases(remaining_pipeline, run, cwd)
        return run

    async def get_run(self, run_id: str) -> PipelineRun | None:
        """Load a pipeline run by ID from the state store.

        Returns None if run not found or no state store configured.
        """
        if self._state_store is None:
            return None
        data = await self._state_store.load(run_id)
        if data is None:
            return None
        return PipelineRun.model_validate(data)

    async def _load_paused_run(
        self,
        run_id: str,
    ) -> tuple[PipelineRun, str, PhaseExecution]:
        """Load a paused run and its current execution entry."""
        if self._state_store is None:
            msg = "State store not configured"
            raise PipelineError(msg)

        data = await self._state_store.load(run_id)
        if data is None:
            msg = f"Run not found: {run_id}"
            raise PipelineError(msg)
        run = PipelineRun.model_validate(data)

        if run.status != RunStatus.PAUSED_HITL:
            msg = f"Run {run_id} is {run.status}, not PAUSED_HITL"
            raise PipelineError(msg)

        paused_phase = run.paused_at_phase
        if paused_phase is None:
            msg = f"Run {run_id} has no paused_at_phase"
            raise PipelineError(msg)

        return run, paused_phase, run.phases[paused_phase]

    async def _resume_epic_story_iteration_if_complete(
        self,
        run: PipelineRun,
        execution: PhaseExecution,
        paused_phase: str,
    ) -> bool:
        """Return False and keep the run paused when epic child stories are incomplete."""
        # S14770.9: "epic" is now the default pipeline; enterprise epic renamed to "epic-enterprise"
        if (
            run.pipeline_name not in ("epic", "epic-enterprise")
            or paused_phase != "story-iteration"
        ):
            return True

        from raise_cli.project import resolve_project_root

        search_root = run.worktree_path or resolve_project_root()
        pending, reason = await pending_epic_stories(
            search_root, run.issue_id or "", run_store=self._state_store
        )
        if reason is None and not pending:
            return True

        execution.error = f"Epic cannot leave story-iteration: {reason or 'child stories still incomplete'}"
        execution.gate_result_passed = False
        run.status = RunStatus.PAUSED_HITL
        run.paused_at_phase = paused_phase
        await self._save_state(run)
        return False

    async def _reject_paused_run(
        self,
        run: PipelineRun,
        execution: PhaseExecution,
        decision: HitlDecision,
    ) -> None:
        """Mark the paused phase and run as rejected."""
        execution.status = "failed"
        execution.error = (
            f"Rejected by {decision.actor}: {decision.message or 'no reason'}"
        )
        run.status = RunStatus.FAILED
        run.completed_at = datetime.now(UTC)
        run.paused_at_phase = None
        await self._save_state(run)

    def _transition_deps(
        self, cwd: Path
    ) -> tuple["object | None", "WorkflowStateMachine | None"] | None:
        """Resolve adapter + machine once per run. Returns None when disabled."""
        if not self._transitions_enabled:
            return None
        try:
            return self._transition_deps_provider(cwd)
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("transition-deps-failed: %s (%s)", type(exc).__name__, exc)
            return None

    async def _record_phase_transition(
        self,
        phase_def: "object",
        run: PipelineRun,
        execution: PhaseExecution,
        deps: "tuple[object | None, WorkflowStateMachine | None] | None",
    ) -> bool:
        """Attempt transition + attach record.  Returns True when caller must halt.

        Halting occurs only when ``phase_def.transition_mode == "blocking"`` and
        the transition outcome is ``"failed"`` or ``"illegal"`` (Stage 3,
        RAISE-15037).  Advisory mode always returns ``False`` (fail-open).
        Never raises.
        """
        from raise_core.workflow.models import PhaseDefinition

        if not isinstance(phase_def, PhaseDefinition):
            return False
        if phase_def.target_status is None or deps is None:
            return False
        adapter, machine = deps
        record = await apply_phase_transition_async(
            phase_id=phase_def.id,
            target_status=phase_def.target_status,
            issue_key=run.issue_id,
            adapter=adapter,  # type: ignore[arg-type]
            machine=machine,
        )
        execution.backlog_transition = record
        if record.outcome == "applied":
            import contextlib

            from raise_cli.hooks.emitter import create_emitter
            from raise_cli.hooks.events import BacklogTransitionEvent

            with contextlib.suppress(Exception):
                create_emitter().emit(
                    BacklogTransitionEvent(
                        run_id=run.run_id,
                        phase_id=record.phase_id,
                        issue_key=record.issue_key,
                        from_status=record.from_status,
                        to_slug=record.to_slug,
                    )
                )
        if record.outcome in ("failed", "illegal"):
            if phase_def.transition_mode == "blocking":
                logger.error(
                    "Backlog transition %s: phase=%s issue=%s -> %s (%s) — halting run",
                    record.outcome,
                    phase_def.id,
                    record.issue_key,
                    record.to_slug,
                    record.message,
                )
                return True
            logger.warning(
                "Backlog transition %s: phase=%s issue=%s -> %s (%s)",
                record.outcome,
                phase_def.id,
                record.issue_key,
                record.to_slug,
                record.message,
            )
        return False

    async def _save_state(self, run: PipelineRun) -> bool:
        """Persist run state if state_store is available. Returns True on success."""
        if self._state_store is not None:
            try:
                await self._state_store.save(run.model_dump(mode="json"))
                return True
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                logger.warning("State save failed: %s", exc)
                return False
        return False
