"""Gate evaluation for pipeline quality gates.

Evaluates deterministic and HITL gates between pipeline phases.
Returns immutable GateEvaluation results for the engine to act on.

Story: S1064.5 — Gate Evaluation (RAISE-1064)
Epic: E1064 — Pipeline Engine Core

Design decision D7: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import asyncio
import logging
import shlex
import shutil
from pathlib import Path

from pydantic import BaseModel
from rich.console import Console

from raise_core.workflow.models import (
    DelegationLevel,
    GateDefinition,
    TerminationReason,
)

logger = logging.getLogger(__name__)


class GateEvaluation(BaseModel, frozen=True):
    """Immutable result of evaluating a quality gate."""

    passed: bool
    crashed: bool = False
    message: str = ""
    termination_reason: TerminationReason = TerminationReason.GATE_FAILED
    hitl_paused: bool = False


def _resolve_argv(tokens: list[str]) -> list[str]:
    """Resolve the executable via ``shutil.which`` for Windows PATHEXT compat."""
    if not tokens:
        return tokens
    exe = shutil.which(tokens[0])
    if exe is not None:
        return [exe, *tokens[1:]]
    return tokens


async def evaluate_gate(
    gate_def: GateDefinition,
    cwd: Path,
    timeout: float = 300.0,
    *,
    is_interactive: bool = False,
    delegation_level: DelegationLevel = DelegationLevel.REVIEW,
) -> GateEvaluation:
    """Evaluate a quality gate and return an immutable result.

    For deterministic gates, runs each command in sequence.
    Stops on first failure. Timeout or unexpected exceptions
    produce a crashed result (GATE_CRASHED).

    For HITL gates, behavior depends on delegation_level and is_interactive.
    """
    if gate_def.type == "hitl":
        return _evaluate_hitl_gate(
            gate_def,
            delegation_level=delegation_level,
            is_interactive=is_interactive,
        )

    if not gate_def.commands:
        return GateEvaluation(passed=True)

    try:
        for cmd in gate_def.commands:
            argv = _resolve_argv(shlex.split(cmd))
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except TimeoutError:
                proc.kill()
                await proc.wait()
                raise
            except BaseException:
                proc.kill()
                await proc.wait()
                raise

            if proc.returncode != 0:
                msg_parts: list[str] = []
                if stdout:
                    msg_parts.append(stdout.decode())
                if stderr:
                    msg_parts.append(stderr.decode())
                return GateEvaluation(
                    passed=False,
                    message="".join(msg_parts),
                )

        return GateEvaluation(passed=True)

    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Gate crashed (not failed): %s", exc)
        return GateEvaluation(
            passed=False,
            crashed=True,
            message=str(exc),
            termination_reason=TerminationReason.GATE_CRASHED,
        )


def _evaluate_hitl_gate(
    gate_def: GateDefinition,
    *,
    delegation_level: DelegationLevel,
    is_interactive: bool,
) -> GateEvaluation:
    """Evaluate an HITL gate based on delegation level and interactivity.

    NOTE (QR R3/R4): This function is sync. The interactive path calls
    Prompt.ask() which blocks the event loop. Acceptable for single-pipeline
    CLI use. If concurrent pipelines are needed, wrap in run_in_executor().
    """
    # Mandatory gates always require explicit approval (S1065.6: story-iteration stop)
    if gate_def.mandatory:
        if is_interactive:
            return _resolve_interactive_decision(gate_def)
        return GateEvaluation(
            passed=False,
            hitl_paused=True,
            message=f"Mandatory HITL gate: {gate_def.level} approval required (paused for async resume)",
        )

    if delegation_level == DelegationLevel.AUTO:
        return GateEvaluation(
            passed=True,
            message="Auto-approved (delegation=AUTO)",
        )

    if delegation_level == DelegationLevel.NOTIFY:
        return GateEvaluation(
            passed=True,
            message=f"HITL: {gate_def.level} — auto-approved (delegation=NOTIFY)",
        )

    # REVIEW: need explicit human decision
    if is_interactive:
        return _resolve_interactive_decision(gate_def)
    return GateEvaluation(
        passed=False,
        hitl_paused=True,
        message=f"HITL: {gate_def.level} approval required (paused for async resume)",
    )


def _resolve_interactive_decision(gate_def: GateDefinition) -> GateEvaluation:
    """Prompt user at terminal and return the corresponding GateEvaluation."""
    decision = _prompt_hitl_decision(gate_def)
    if decision == "approve":
        return GateEvaluation(passed=True, message="Approved at terminal")
    if decision == "revise":
        return GateEvaluation(passed=False, message="Revision requested at terminal")
    return GateEvaluation(passed=False, message="Rejected at terminal")


def _prompt_hitl_decision(gate_def: GateDefinition) -> str:
    """Present HITL options at terminal, return decision string."""
    from rich.prompt import Prompt

    console = Console()
    console.print(
        f"\n[bold yellow]HITL Gate[/bold yellow] — {gate_def.level} approval required"
    )
    console.print("Phase completed. Review the results above.\n")

    return Prompt.ask(
        "Decision",
        choices=["approve", "revise", "reject"],
        default="approve",
    )
