"""SubagentDispatcher — coordinator state machine for fleet dispatch.

S9507.2: Implements the dispatch coordinator that returns DispatchInstructions
for the CC session to execute as Agent() Task calls. This module holds live
FleetState and computes instructions — it NEVER spawns threads, calls Agent(),
or does git/pipeline I/O.

Design: instruction-not-execution pattern (mirrors mcp_tools_pipeline._phase_instruction).
"""

from __future__ import annotations

import dataclasses
import logging
import threading
from dataclasses import dataclass
from typing import Any

from raise_cli.fleet.prompt_builder import DefaultFleetPromptBuilder
from raise_cli.pipeline.skill_model import VALID_MODELS, parse_skill_model
from raise_core.fleet.protocols import FleetPromptBuilder
from raise_core.workflow.models import RunStatus

logger = logging.getLogger(__name__)

#: Terminal run statuses across both orchestrators.
#:
#: The PipelineEngine (raise-core) writes RunStatus.COMPLETED/"completed" and
#: RunStatus.FAILED/"failed" on terminal runs. The MCP orchestrator uses its
#: own ad-hoc vocabulary ("complete"/"cancelled"). A run whose status is NOT
#: in this set is still active/resumable (pending, running, paused_hitl,
#: started, etc.) and must remain a phase-extraction candidate.
_TERMINAL_STATUSES = {RunStatus.COMPLETED, RunStatus.FAILED, "complete", "cancelled"}


def is_active_run_status(status: object) -> bool:
    """True iff `status` is NOT one of the terminal run statuses (public accessor).

    `_TERMINAL_STATUSES` stays private to this module (it's an
    implementation detail of `_get_current_phase`'s active-run filter) —
    external callers that need the same "is this run still active" check
    (e.g. `raise_cli.hooks.git_commit_block`, D8.b) use this function
    instead of reaching into the private set directly.
    """
    return status not in _TERMINAL_STATUSES


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class StoryProgress:
    """Live progress record for a single fleet story.

    Attributes:
        story_key: Jira key (e.g. "RAISE-9507").
        phase: Current pipeline phase id (e.g. "design", "plan").
        status: Lifecycle status: pending | running | hitl | awaiting_advance |
            complete | blocked. "awaiting_advance" (RAISE-15766, D3.a) is set
            by record_phase_complete() and cleared back to "running" (or
            "complete") by record_advanced() once the run store is proven
            to have moved.
        task_id: Optional CC task id from the subagent (best-effort, may be None).
        model: Model used for the current phase.
        run_id: Pipeline run id from FleetPipelineBinding.bind() — non-secret
            (RAISE-15765, D3.a). Empty string when no binding exists yet
            (e.g. seeded outside the bind→dispatch_one flow).
        phase_index: Run store's current_phase_index as last observed by
            FleetState (D3.a). Populated at bind time (dispatch_one) and on
            every transition (record_advanced) as of RAISE-15766 — this is
            the field `_FleetStateStore.compare_and_advance` compares
            against the run store's live index to prove an "advanced"
            signal is genuine, not a premature/duplicate call (D3.b).
        worktree_path: The story's resolved worktree, mirroring run_id's
            pattern (RAISE-15772 quality-review C1). Populated at bind time
            (dispatch_one) alongside run_id and carried forward unchanged by
            record_advanced/approve (dataclasses.replace never overrides
            it) — without this field, phases 2..N had no worktree_path to
            route through FleetPromptBuilder.build() with, so they silently
            fell back to the bare one-liner (rc1's exact failure). Empty
            string when no binding exists yet, same as run_id.
    """

    story_key: str
    phase: str
    status: str
    task_id: str | None
    model: str
    run_id: str = ""
    phase_index: int = 0
    worktree_path: str = ""


@dataclass(frozen=True)
class DispatchInstruction:
    """Immutable instruction for the CC session to spawn one Agent() Task.

    The CC session reads ``agent_prompt`` and issues the actual Agent() call.
    This module never spawns.

    Attributes:
        story_key: Jira key.
        phase: Pipeline phase id.
        skill: Full skill name (e.g. "rai-story-design").
        model: Resolved model — validated against VALID_MODELS.
        agent_prompt: Ready-to-execute instruction string for the CC session,
            mirroring mcp_tools_pipeline._phase_instruction format:
            ``Spawn Agent(model="<model>") to execute skill: /rai-<skill> <key>``.
        worktree_path: Resolved story worktree (D10.b). Empty string until
            RAISE-15764 threads the verified path in; carried here so
            downstream stories (15764, 15772, 15882) have a field to fill
            and consume rather than inventing one later.
    """

    story_key: str
    phase: str
    skill: str
    model: str
    agent_prompt: str
    worktree_path: str = ""


# ---------------------------------------------------------------------------
# FleetState singleton
# ---------------------------------------------------------------------------


class _FleetStateStore:
    """Module-level in-process singleton holding story_key → StoryProgress.

    Process-lifetime only (no DB, no cross-process share). YAGNI — D5.
    Volatile by explicit decision (D3.b) — a director/MCP-server restart
    empties it; crash recovery goes through the durable run store
    (`pipeline_runs` / `pipeline_restore` + `rai pipeline token reissue`),
    never through this store.

    D3.b: every accessor runs under `self._lock` because fleet MCP-tool
    handlers execute on `asyncio.to_thread` worker threads — an unlocked
    dict lets two concurrent `fleet_signal(event="advanced")` calls for one
    story both read-then-write across a non-atomic boundary and
    double-dispatch (the TOCTOU the round-2 adversarial review flagged).
    `compare_and_advance` is the single serialization point the `advanced`
    handler's check-then-act runs inside.
    """

    def __init__(self) -> None:
        self._store: dict[str, StoryProgress] = {}
        self._lock = threading.RLock()

    def get(self, story_key: str) -> StoryProgress | None:
        """Return StoryProgress for key, or None if unknown."""
        with self._lock:
            return self._store.get(story_key)

    def set(self, story_key: str, progress: StoryProgress) -> None:
        """Store or replace progress for story_key."""
        with self._lock:
            self._store[story_key] = progress

    def snapshot(self) -> list[StoryProgress]:
        """Return a snapshot of all current progress records."""
        with self._lock:
            return list(self._store.values())

    def clear(self) -> None:
        """Remove all stored progress. Used between tests and on new dispatch."""
        with self._lock:
            self._store.clear()

    def delete(self, story_key: str) -> None:
        """Remove story_key's progress, if present (idempotent).

        RAISE-15765/R1: dispatch_one() seeds FleetState before it can raise
        (e.g. while building the prompt) — a caller whose post-bind failure
        path cancels the run must also call this so a cancelled/failed story
        leaves no phantom FleetState entry (stale run_id surfacing in
        fleet_status for a story that will never actually run).
        """
        with self._lock:
            self._store.pop(story_key, None)

    def compare_and_advance(
        self, story_key: str, expected_phase_index: int, new: StoryProgress
    ) -> bool:
        """Atomically replace progress only if the stored phase_index still matches.

        D3.b: the single serialization point for the `advanced` handler's
        check-then-act. Returns False (and writes nothing) when the story is
        unknown OR another thread already advanced it past
        `expected_phase_index` — the caller MUST then emit no instruction.
        This is what makes `record_advanced` race-safe: two concurrent
        callers can both read the same stale index, but only one CAS wins.
        """
        with self._lock:
            current = self._store.get(story_key)
            if current is None or current.phase_index != expected_phase_index:
                return False
            self._store[story_key] = new
            return True


#: Module-level singleton — the single source of truth for in-process fleet state.
FleetState = _FleetStateStore()


# ---------------------------------------------------------------------------
# SubagentDispatcher
# ---------------------------------------------------------------------------


def _build_agent_prompt(
    skill: str,
    story_key: str,
    model: str,
    *,
    run_id: str | None = None,
    phase_id: str | None = None,
    parent_session: str | None = None,
) -> str:
    """Build instruction string mirroring mcp_tools_pipeline._phase_instruction."""
    clean = skill.removeprefix("rai-")
    base = f'Spawn Agent(model="{model}") to execute skill: /rai-{clean} {story_key}'
    from raise_cli.pipeline.rai_header import build_rai_header

    header = build_rai_header(
        type="fleet",
        skill=skill,
        phase=phase_id,
        run_id=run_id,
        parent_session=parent_session,
    )
    if header:
        return f"{header}\n{base}"
    if run_id:
        # R1 (RAISE-15772 quality-review): a live brief (real run_id) that
        # ends up headerless — usually parent_session resolving to None
        # (no session env vars, unrecognized PPID chain) — is a silent
        # classification gap for JSONL transcript tooling. Observable now.
        logger.warning(
            "[RAI:] header omitted for a live brief (run_id=%s, skill=%s, "
            "story=%s) — parent_session or another required header field "
            "could not be resolved",
            run_id,
            skill,
            story_key,
        )
    return base


class SubagentDispatcher:
    """Coordinator state machine — computes DispatchInstructions, holds FleetState.

    MUST NOT: call Agent()/Task tool, spawn threads, do git/pipeline I/O.
    """

    def __init__(self, prompt_builder: FleetPromptBuilder | None = None) -> None:
        """`prompt_builder` defaults to `DefaultFleetPromptBuilder()` (D4/D10.b).

        Injectable so tests (and future callers) can supply a stub — mirrors
        the injection pattern already used by `PipelineBinder`/verifier
        instances at the `mcp_tools_fleet` boundary.
        """
        self._prompt_builder = prompt_builder or DefaultFleetPromptBuilder()

    def _resolve_model(self, skill: str, default_model: str, cwd: str) -> str:
        """Resolve per-phase model from skill frontmatter, falling back to default.

        Both skill-declared and default models must be short names in VALID_MODELS
        (e.g. "sonnet", not "claude-sonnet-4-6"). Normalization of full IDs to short
        names is the caller's responsibility (see _FULL_TO_SHORT in mcp_tools_fleet).

        Unknown skill, unreadable frontmatter, or invalid model → "sonnet" fallback.
        """
        from pathlib import Path

        # C2: validate default_model before it can be returned unchecked
        if default_model not in VALID_MODELS:
            logger.warning(
                "default_model %r not in VALID_MODELS — falling back to 'sonnet'",
                default_model,
            )
            default_model = "sonnet"

        try:
            skill_base = Path(cwd).resolve() / ".claude" / "skills"
            model = parse_skill_model(skill, skill_base)
        except Exception:  # noqa: BLE001
            logger.debug("parse_skill_model failed for %s — using default", skill)
            model = None

        if model is None:
            return default_model

        if model not in VALID_MODELS:
            logger.warning(
                "Skill '%s' resolved invalid model '%s' — falling back to %s",
                skill,
                model,
                default_model,
            )
            return default_model

        return model

    def _build_prompt_for_progress(
        self,
        *,
        story_key: str,
        skill: str,
        phase_id: str,
        model: str,
        progress: StoryProgress,
    ) -> str:
        """Route a next-phase prompt through FleetPromptBuilder when bound, else the one-liner.

        RAISE-15772/C1 (quality-review): `record_advanced` and `approve` are
        the real advance-signal and HITL-approval flow for phases 2..N of a
        story — not a dry-run/test-only path. Before this fix they always
        called `_build_agent_prompt` (the bare one-liner), because
        `StoryProgress` never carried `worktree_path` past bind time — this
        recreated rc1's exact failure (a subagent with no governance
        preamble, no worktree cd instruction, no completion protocol for
        every phase after the first).

        Mirrors `dispatch_one`'s existing routing condition exactly: only
        when BOTH `run_id` AND `worktree_path` are non-empty on the stored
        `progress` does this call `FleetPromptBuilder.build()` for the full
        BRIEF. Callers missing either one (e.g. a story seeded outside the
        bind→dispatch_one flow, or unit tests that never set
        `worktree_path`) keep the pre-fix one-liner — never a
        partial/degraded brief.
        """
        if progress.run_id and progress.worktree_path:
            return self._prompt_builder.build(
                work_id=story_key,
                skill=skill,
                run_id=progress.run_id,
                worktree_path=progress.worktree_path,
            )

        from raise_cli._agent_session import discover_agent_session_id

        _parent_session = discover_agent_session_id()
        return _build_agent_prompt(
            skill,
            story_key,
            model,
            run_id=progress.run_id or None,
            phase_id=phase_id,
            parent_session=_parent_session,
        )

    def _get_current_phase(
        self,
        story_key: str,
        cwd: str = "",
    ) -> tuple[str, str, int] | None:
        """Return (phase_id, skill_name, phase_index) for the story's current phase.

        Queries the run store for the most recent active run for this issue.
        Returns None if no active run exists (terminal or unknown story).

        phase_index is the run store's live `current_phase_index` for the
        matched run — previously looked up and discarded (D3.a). The
        `record_advanced` handler needs it to compare against FleetState's
        last-recorded pair via `compare_and_advance`, which is how it
        proves the run store actually moved before emitting an instruction.

        This is the lazy one-call-per-story pattern from the plan (OQ2 resolution).
        """
        import asyncio

        from raise_cli.pipeline.run_store import get_run_store

        async def _lookup() -> tuple[str, str, int] | None:
            store = get_run_store()
            runs = await store.list_runs()
            # Find most recent active run for this story
            for run in runs:
                if (
                    run.get("issue_id") == story_key
                    and run.get("status") not in _TERMINAL_STATUSES
                ):
                    phases = run.get("phases", [])
                    idx: int = run.get("current_phase_index", 0)
                    if idx < len(phases):
                        phase = phases[idx]
                        if not isinstance(phase, dict):
                            # Observable skip: a malformed
                            # phase shape would otherwise be dropped silently —
                            # the exact "vanish without signal" class the fix
                            # attacks. Log before continuing; lookup keeps
                            # scanning remaining runs unchanged.
                            logger.warning(
                                "Skipping malformed phase for %s at index %d: "
                                "expected dict, got %s",
                                story_key,
                                idx,
                                type(phase).__name__,
                            )
                            continue
                        phase_id: str = phase.get("id", "design")
                        skill: str = phase.get("skill", f"rai-story-{phase_id}")
                        return phase_id, skill, idx
            return None

        try:
            return asyncio.run(_lookup())
        except Exception:  # noqa: BLE001
            # Broad on purpose (shape/lookup errors from either orchestrator's
            # run dicts), but observable: this swallow was previously at
            # debug level, which let terminal-status misclassification vanish
            # runs from fleet_status with zero signal. warning + exc_info
            # surfaces the shape mismatch without changing the None fallback.
            logger.warning("_get_current_phase failed for %s", story_key, exc_info=True)
            return None

    def dispatch_one(
        self,
        story_key: str,
        default_model: str,
        cwd: str,
        *,
        run_id: str | None = None,
        worktree_path: str = "",
    ) -> DispatchInstruction:
        """Resolve one story's current phase and build its DispatchInstruction.

        The per-story unit `mcp_tools_fleet.fleet_dispatch` calls AFTER
        `FleetPipelineBinding.bind()` succeeds (D1/D8) — binding itself never
        happens here (SubagentDispatcher MUST NOT do pipeline I/O, F7); the
        caller passes only the non-secret `run_id` it already minted.

        Seeds/overwrites FleetState for `story_key` but does NOT clear the
        rest of the store — callers seed a fresh batch via `FleetState.clear()`
        once before the first call (see `dispatch()`).

        `run_id` threads to `_build_agent_prompt` so the `[RAI:...]` header
        fires (F1/GAP-2). Omit it for callers with no active binding (e.g.
        dry-run inspection, unit tests without a bind() call) — the header
        is then omitted entirely, matching pre-fix behavior; never a
        partial header.

        `worktree_path` (D10.b, RAISE-15764) is the story's verified
        worktree, resolved and checked by `ProvisioningVerifier` BEFORE this
        call — this method does no resolution/verification itself (that
        would be pipeline/filesystem I/O duplicated across two stories).
        Threaded onto the returned `DispatchInstruction` so `fleet_status`
        and `FleetPromptBuilder` (RAISE-15772) have the value already
        available. Empty string when the caller has no resolved path yet.

        RAISE-15772/D4/D8: when BOTH `run_id` and `worktree_path` are
        supplied — the live `fleet_dispatch` shape, always true once
        `_bind_and_dispatch_story` calls this after a successful `bind()` —
        the agent_prompt is the full BRIEF.md from
        `FleetPromptBuilder.build()` (D4), not the old one-liner. Callers
        missing either one (dry-run inspection, unit tests without a full
        bind+resolve) keep the pre-fix one-liner via `_build_agent_prompt`
        — never a partial/degraded brief.
        """
        phase_info = self._get_current_phase(story_key, cwd)
        if phase_info is None:
            # No active run — default to design phase
            phase_id = "design"
            skill = "rai-story-design"
            phase_index = 0
        else:
            phase_id, skill, phase_index = phase_info

        model = self._resolve_model(skill, default_model, cwd)

        FleetState.set(
            story_key,
            StoryProgress(
                story_key=story_key,
                phase=phase_id,
                status="pending",
                task_id=None,
                model=model,
                run_id=run_id or "",
                phase_index=phase_index,
                worktree_path=worktree_path,
            ),
        )

        if run_id and worktree_path:
            # Live fleet_dispatch shape (D8): bind() already succeeded and
            # worktree resolution already passed — build the full BRIEF.
            prompt = self._prompt_builder.build(
                work_id=story_key,
                skill=skill,
                run_id=run_id,
                worktree_path=worktree_path,
            )
        else:
            from raise_cli._agent_session import discover_agent_session_id

            _parent_session = discover_agent_session_id()
            prompt = _build_agent_prompt(
                skill,
                story_key,
                model,
                run_id=run_id,
                phase_id=phase_id,
                parent_session=_parent_session,
            )
        return DispatchInstruction(
            story_key=story_key,
            phase=phase_id,
            skill=skill,
            model=model,
            agent_prompt=prompt,
            worktree_path=worktree_path,
        )

    def dispatch(
        self,
        plan: Any,
        default_model: str,
        cwd: str,
        dry_run: bool = False,
    ) -> list[DispatchInstruction]:
        """Seed FleetState and return first-phase DispatchInstructions.

        Args:
            plan: DispatchPlan with .dispatchable tuple of story keys.
            default_model: Fallback model when skill has no frontmatter model.
            cwd: Working directory for skill resolution.
            dry_run: When True, returns [] and does NOT seed FleetState.

        Returns:
            List of DispatchInstruction — one per dispatchable story.

        Note (RAISE-15765/D1): this batch method has no per-story run_id
        available at its boundary — binding happens at the mcp_tools_fleet
        MCP-tool boundary, one story at a time, via dispatch_one(). Callers
        that need bound run_ids (i.e. the live fleet_dispatch path) call
        dispatch_one() directly per story instead of this method.

        R2 (quality review, RAISE-15765): this method now has zero production
        callers — the same dead-code shape as the deleted `_make_instruction`
        (see `test_make_instruction_no_longer_exists` above). Left in place
        (still covered by tests) rather than deleted here; removal is
        tracked for RAISE-15766 alongside the completion-routing work.
        """
        if dry_run:
            return []

        # Clear stale state from any prior dispatch run before seeding fresh state.
        # Re-dispatching without clearing would silently clobber in-flight progress
        # and leave orphan records from stories not in the new plan.
        FleetState.clear()

        return [
            self.dispatch_one(story_key, default_model, cwd)
            for story_key in plan.dispatchable
        ]

    def record_phase_complete(
        self,
        story_key: str,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """event=phase_complete handler (D3) — bookkeeping only, never an instruction.

        Contract (amended ADR-2026-08-05 §2, inverting the old Q2 note): the
        DIRECTOR advances the pipeline run — via pipeline_advance, holding
        the advance_token it has held since fleet_dispatch — NEVER the
        subagent. A fleet subagent has no token and calling
        pipeline_advance itself is refused with AUTHORITY_DENIED (the live
        defense F3 restores).

        This method therefore does NOT read the run store and NEVER
        computes a next-phase instruction — that was exactly F2's
        duplicate-dispatch defect (the run store hadn't advanced yet, so
        the same just-completed phase was re-emitted). It only records that
        the subagent finished its current phase: flips status to
        "awaiting_advance" and best-effort records task_id. The advance
        directive is relayed to the director only because the subagent's
        Task ends and this return value surfaces in the director's context
        (there is no other channel — see design.md D3.a's closing note).

        The director must separately call pipeline_advance and then
        fleet_signal(event="advanced") — record_advanced() is what may
        return the next instruction, gated by compare_and_advance so a
        premature or duplicate "advanced" call cannot re-trigger F2.

        Args:
            story_key: Jira key of the completing story.
            task_id: Optional CC task id (best-effort).

        Returns a structured directive (never a DispatchInstruction):
            {"status": "awaiting_advance", "run_id": ..., "phase_index": ...}
            {"status": "unknown_story", "run_id": "", "phase_index": None}
                — D3.b fail-closed: an unseen story (e.g. after a FleetState
                reset) proves nothing, so it is never treated as advanceable.
        """
        progress = FleetState.get(story_key)
        if progress is None:
            logger.warning(
                "record_phase_complete called for unknown story: %s", story_key
            )
            return {"status": "unknown_story", "run_id": "", "phase_index": None}

        updated = dataclasses.replace(
            progress, task_id=task_id, status="awaiting_advance"
        )
        FleetState.set(story_key, updated)
        return {
            "status": "awaiting_advance",
            "run_id": updated.run_id,
            "phase_index": updated.phase_index,
        }

    def record_advanced(
        self,
        story_key: str,
        default_model: str,
        cwd: str,
    ) -> dict[str, Any]:
        """event=advanced handler (D3.a/D3.b) — CAS-gated, idempotent advance.

        Only meaningful once the DIRECTOR has itself called pipeline_advance
        (holding the advance_token). This method does not trust the event
        name alone (F9: fleet_signal has zero caller authentication) — it
        proves the run store actually moved by comparing its live
        (phase_id, phase_index) against FleetState's last-recorded pair,
        and performs that check-then-act INSIDE
        `_FleetStateStore.compare_and_advance`'s lock so two concurrent
        `advanced` calls for one story cannot both pass (D3.b's TOCTOU fix).

        Idempotent by construction: a second call for the same
        (run_id, phase_index) — a director retry after a timeout, or a
        compaction-induced double-call — hits the "not_advanced" no-op both
        times and never double-dispatches.

        Args:
            story_key: Jira key of the story to advance.
            default_model: Fallback model for next-phase resolution.
            cwd: Working directory for skill resolution.

        Returns exactly one of:
            {"status": "unknown_story", "run_id": "", "phase_index": None}
            {"status": "not_advanced", "run_id": ..., "phase_index": ...}
                — run store has not moved yet, or this call lost the CAS
                race to a concurrent one. No instruction emitted.
            {"status": "complete", "run_id": ..., "phase_index": ...}
                — terminal phase; no next instruction.
            {"status": "running", "run_id": ..., "phase_index": ...,
             "instruction": <agent_prompt>}
                — genuine advance; the next BRIEF to dispatch.
        """
        progress = FleetState.get(story_key)
        if progress is None:
            logger.warning("record_advanced called for unknown story: %s", story_key)
            return {"status": "unknown_story", "run_id": "", "phase_index": None}

        phase_info = self._get_current_phase(story_key, cwd)
        if phase_info is None:
            # Terminal (or no active run to read) — nothing to advance to.
            # Still routed through the CAS so a concurrent caller racing on
            # the same expected index can't double-mark this complete.
            FleetState.compare_and_advance(
                story_key,
                progress.phase_index,
                dataclasses.replace(progress, status="complete"),
            )
            return {
                "status": "complete",
                "run_id": progress.run_id,
                "phase_index": progress.phase_index,
            }

        phase_id, skill, live_index = phase_info
        if live_index == progress.phase_index:
            # D3.a's enforcement gate: the run store did NOT move. Emit no
            # instruction — this is the fix for F2's duplicate dispatch.
            return {
                "status": "not_advanced",
                "run_id": progress.run_id,
                "phase_index": progress.phase_index,
            }

        model = self._resolve_model(skill, default_model, cwd)
        new_progress = dataclasses.replace(
            progress,
            phase=phase_id,
            phase_index=live_index,
            model=model,
            status="running",
        )
        advanced = FleetState.compare_and_advance(
            story_key, progress.phase_index, new_progress
        )
        if not advanced:
            # Lost the CAS race — a concurrent `advanced` call already
            # moved this story (D3.b). No-op; report whatever is now
            # actually stored so the caller's retry sees the true state.
            current = FleetState.get(story_key)
            reported_index = (
                current.phase_index if current is not None else progress.phase_index
            )
            return {
                "status": "not_advanced",
                "run_id": progress.run_id,
                "phase_index": reported_index,
            }

        prompt = self._build_prompt_for_progress(
            story_key=story_key,
            skill=skill,
            phase_id=phase_id,
            model=model,
            progress=new_progress,
        )
        return {
            "status": "running",
            "run_id": new_progress.run_id,
            "phase_index": live_index,
            "instruction": prompt,
        }

    def approve(
        self,
        story_key: str,
        default_model: str,
        cwd: str,
    ) -> DispatchInstruction | None:
        """Approve a HITL-gated story and return its next instruction.

        Args:
            story_key: Jira key to approve.
            default_model: Fallback model for next phase.
            cwd: Working directory.

        Returns:
            Next DispatchInstruction, or None if story not in FleetState.
        """
        progress = FleetState.get(story_key)
        if progress is None:
            return None

        # Get current phase for the next instruction
        phase_info = self._get_current_phase(story_key, cwd)
        if phase_info is None:
            phase_id = progress.phase
            skill = f"rai-story-{phase_id}"
            live_index = progress.phase_index
        else:
            phase_id, skill, live_index = phase_info

        model = self._resolve_model(skill, default_model, cwd)

        # R1 (RAISE-15766 quality-review): write the observed (phase,
        # phase_index) back into FleetState atomically, same as
        # record_advanced's success path — otherwise a subsequent
        # fleet_signal(advanced) sees a stale recorded index, wins its CAS,
        # and re-emits this same phase (F2-class double dispatch via the
        # HITL path). compare_and_advance with the pre-approval index as
        # the expected value keeps this consistent with D3.b even though
        # approve() itself is not a race-prone entry point.
        new_progress = dataclasses.replace(
            progress,
            phase=phase_id,
            phase_index=live_index,
            model=model,
            status="pending",
        )
        if not FleetState.compare_and_advance(
            story_key, progress.phase_index, new_progress
        ):
            FleetState.set(story_key, new_progress)

        prompt = self._build_prompt_for_progress(
            story_key=story_key,
            skill=skill,
            phase_id=phase_id,
            model=model,
            progress=new_progress,
        )
        return DispatchInstruction(
            story_key=story_key,
            phase=phase_id,
            skill=skill,
            model=model,
            agent_prompt=prompt,
            worktree_path=new_progress.worktree_path,
        )
