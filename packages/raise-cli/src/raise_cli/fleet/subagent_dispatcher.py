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
from dataclasses import dataclass
from typing import Any

from raise_cli.pipeline.skill_model import VALID_MODELS, parse_skill_model
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


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class StoryProgress:
    """Live progress record for a single fleet story.

    Attributes:
        story_key: Jira key (e.g. "RAISE-9507").
        phase: Current pipeline phase id (e.g. "design", "plan").
        status: Lifecycle status: pending | running | hitl | complete | blocked.
        task_id: Optional CC task id from the subagent (best-effort, may be None).
        model: Model used for the current phase.
    """

    story_key: str
    phase: str
    status: str
    task_id: str | None
    model: str


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
    """

    story_key: str
    phase: str
    skill: str
    model: str
    agent_prompt: str


# ---------------------------------------------------------------------------
# FleetState singleton
# ---------------------------------------------------------------------------


class _FleetStateStore:
    """Module-level in-process singleton holding story_key → StoryProgress.

    Process-lifetime only (no DB, no cross-process share). YAGNI — D5.
    """

    def __init__(self) -> None:
        self._store: dict[str, StoryProgress] = {}

    def get(self, story_key: str) -> StoryProgress | None:
        """Return StoryProgress for key, or None if unknown."""
        return self._store.get(story_key)

    def set(self, story_key: str, progress: StoryProgress) -> None:
        """Store or replace progress for story_key."""
        self._store[story_key] = progress

    def snapshot(self) -> list[StoryProgress]:
        """Return a snapshot of all current progress records."""
        return list(self._store.values())

    def clear(self) -> None:
        """Remove all stored progress. Used between tests and on new dispatch."""
        self._store.clear()


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
    return base


class SubagentDispatcher:
    """Coordinator state machine — computes DispatchInstructions, holds FleetState.

    MUST NOT: call Agent()/Task tool, spawn threads, do git/pipeline I/O.
    """

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

    def _get_current_phase(
        self,
        story_key: str,
        cwd: str = "",  # noqa: ARG002
    ) -> tuple[str, str] | None:
        """Return (phase_id, skill_name) for the story's current pipeline phase.

        Queries the run store for the most recent active run for this issue.
        Returns None if no active run exists (terminal or unknown story).

        This is the lazy one-call-per-story pattern from the plan (OQ2 resolution).
        """
        import asyncio

        from raise_cli.pipeline.run_store import get_run_store

        async def _lookup() -> tuple[str, str] | None:
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
                        return phase_id, skill
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

    def _make_instruction(
        self,
        story_key: str,
        phase_id: str,
        skill: str,
        default_model: str,
        cwd: str,
        *,
        parent_session: str | None = None,
    ) -> DispatchInstruction:
        """Build a DispatchInstruction with resolved model."""
        model = self._resolve_model(skill, default_model, cwd)
        prompt = _build_agent_prompt(
            skill, story_key, model, phase_id=phase_id, parent_session=parent_session
        )
        return DispatchInstruction(
            story_key=story_key,
            phase=phase_id,
            skill=skill,
            model=model,
            agent_prompt=prompt,
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
        """
        if dry_run:
            return []

        # Clear stale state from any prior dispatch run before seeding fresh state.
        # Re-dispatching without clearing would silently clobber in-flight progress
        # and leave orphan records from stories not in the new plan.
        FleetState.clear()

        instructions: list[DispatchInstruction] = []

        for story_key in plan.dispatchable:
            phase_info = self._get_current_phase(story_key, cwd)
            if phase_info is None:
                # No active run — default to design phase
                phase_id = "design"
                skill = "rai-story-design"
            else:
                phase_id, skill = phase_info

            model = self._resolve_model(skill, default_model, cwd)

            # Seed FleetState
            FleetState.set(
                story_key,
                StoryProgress(
                    story_key=story_key,
                    phase=phase_id,
                    status="pending",
                    task_id=None,
                    model=model,
                ),
            )

            from raise_cli._agent_session import discover_agent_session_id

            _parent_session = discover_agent_session_id()
            prompt = _build_agent_prompt(
                skill,
                story_key,
                model,
                phase_id=phase_id,
                parent_session=_parent_session,
            )
            instructions.append(
                DispatchInstruction(
                    story_key=story_key,
                    phase=phase_id,
                    skill=skill,
                    model=model,
                    agent_prompt=prompt,
                )
            )

        return instructions

    def record_phase_complete(
        self,
        story_key: str,
        task_id: str | None,
        default_model: str,
        cwd: str,
    ) -> DispatchInstruction | None:
        """Record phase completion and return next-phase instruction.

        Contract (Q2): the *subagent itself* must advance its pipeline run
        (via pipeline_advance) BEFORE calling fleet_signal(phase_complete).
        This method reads the run store to find the *new* current phase —
        if the subagent has not advanced, _get_current_phase returns the same
        phase that just completed, producing a duplicate next-instruction.

        Updates FleetState for story_key with the completed task_id.
        Returns next DispatchInstruction, or None if story is complete (terminal phase).

        Args:
            story_key: Jira key of the completing story.
            task_id: Optional CC task id (best-effort).
            default_model: Fallback model for next phase resolution.
            cwd: Working directory for skill resolution.
        """
        progress = FleetState.get(story_key)
        if progress is None:
            logger.warning(
                "record_phase_complete called for unknown story: %s", story_key
            )
            return None

        # Update task_id
        updated = dataclasses.replace(progress, task_id=task_id, status="running")
        FleetState.set(story_key, updated)

        # Get next phase (lazy lookup)
        phase_info = self._get_current_phase(story_key, cwd)
        if phase_info is None:
            # Terminal — mark complete
            FleetState.set(story_key, dataclasses.replace(updated, status="complete"))
            return None

        phase_id, skill = phase_info
        model = self._resolve_model(skill, default_model, cwd)

        # Advance state
        FleetState.set(
            story_key,
            dataclasses.replace(updated, phase=phase_id, model=model),
        )

        from raise_cli._agent_session import discover_agent_session_id

        _parent_session = discover_agent_session_id()
        prompt = _build_agent_prompt(
            skill,
            story_key,
            model,
            phase_id=phase_id,
            parent_session=_parent_session,
        )
        return DispatchInstruction(
            story_key=story_key,
            phase=phase_id,
            skill=skill,
            model=model,
            agent_prompt=prompt,
        )

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

        # Mark approved (was hitl → pending)
        FleetState.set(story_key, dataclasses.replace(progress, status="pending"))

        # Get current phase for the next instruction
        phase_info = self._get_current_phase(story_key, cwd)
        if phase_info is None:
            phase_id = progress.phase
            skill = f"rai-story-{phase_id}"
        else:
            phase_id, skill = phase_info

        model = self._resolve_model(skill, default_model, cwd)
        from raise_cli._agent_session import discover_agent_session_id

        _parent_session = discover_agent_session_id()
        prompt = _build_agent_prompt(
            skill,
            story_key,
            model,
            phase_id=phase_id,
            parent_session=_parent_session,
        )
        return DispatchInstruction(
            story_key=story_key,
            phase=phase_id,
            skill=skill,
            model=model,
            agent_prompt=prompt,
        )
