"""Pipeline command parsing and dispatch for daemon integration.

Parses chat messages into typed pipeline commands and dispatches them
to PipelineEngine. Provider-agnostic — communicates via send callbacks.

Story: S1065.9 — Daemon Pipeline Dispatch (RAISE-1206)
Epic: E1065 — Dev Lifecycle Pipelines

Design decision D7: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import logging
import shlex
from collections.abc import Awaitable, Callable
from typing import Literal

from pydantic import BaseModel

from raise_cli.pipeline.engine import PipelineEngine
from raise_cli.pipeline.loader import PipelineError, PipelineLoader
from raise_core.workflow.models import PipelineDefinition, PipelineRun, RunStatus

logger = logging.getLogger(__name__)

SendFn = Callable[[str], Awaitable[None]]

# ─── Command models ──────────────────────────────────────────────────


class RunCommand(BaseModel, frozen=True):
    """Parsed /pipeline run command."""

    type: Literal["run"] = "run"
    name: str
    issue: str | None = None
    story_type: str = "code"


class ResumeCommand(BaseModel, frozen=True):
    """Parsed /pipeline resume command."""

    type: Literal["resume"] = "resume"
    run_id: str
    decision: Literal["approve", "revise", "reject"] = "approve"


class ListCommand(BaseModel, frozen=True):
    """Parsed /pipeline list command."""

    type: Literal["list"] = "list"


class StatusCommand(BaseModel, frozen=True):
    """Parsed /pipeline status command."""

    type: Literal["status"] = "status"
    run_id: str


PipelineCommand = RunCommand | ResumeCommand | ListCommand | StatusCommand


# ─── Parser ──────────────────────────────────────────────────────────


def parse_pipeline_command(text: str) -> PipelineCommand | None:
    """Parse a chat message into a pipeline command, or None if not a command.

    Recognizes:
        /pipeline run <name> [--issue/-i ID] [--story-type/-t TYPE]
        /pipeline resume <run_id> [--decision/-d approve|revise|reject]
        /pipeline list
        /pipeline status <run_id>
    """
    text = text.strip()
    if not text.startswith("/pipeline"):
        return None

    try:
        tokens = shlex.split(text)
    except ValueError:
        return None

    if len(tokens) < 2:
        return None

    subcommand = tokens[1]

    if subcommand == "run":
        return _parse_run(tokens[2:])
    if subcommand == "resume":
        return _parse_resume(tokens[2:])
    if subcommand == "list":
        return ListCommand()
    if subcommand == "status":
        return _parse_status(tokens[2:])

    return None


def _parse_run(args: list[str]) -> RunCommand | None:
    """Parse arguments for /pipeline run."""
    if not args:
        return None

    name = args[0]
    issue: str | None = None
    story_type = "code"

    i = 1
    while i < len(args):
        if args[i] in ("--issue", "-i") and i + 1 < len(args):
            issue = args[i + 1]
            i += 2
        elif args[i] in ("--story-type", "-t") and i + 1 < len(args):
            story_type = args[i + 1]
            i += 2
        else:
            i += 1

    return RunCommand(name=name, issue=issue, story_type=story_type)


def _parse_resume(args: list[str]) -> ResumeCommand | None:
    """Parse arguments for /pipeline resume."""
    if not args:
        return None

    run_id = args[0]
    decision: str = "approve"

    i = 1
    while i < len(args):
        if args[i] in ("--decision", "-d") and i + 1 < len(args):
            decision = args[i + 1]
            i += 2
        else:
            i += 1

    if decision not in ("approve", "revise", "reject"):
        decision = "approve"

    return ResumeCommand(
        run_id=run_id,
        decision=decision,  # type: ignore[arg-type]
    )


def _parse_status(args: list[str]) -> StatusCommand | None:
    """Parse arguments for /pipeline status."""
    if not args:
        return None
    return StatusCommand(run_id=args[0])


# ─── Format helpers ──────────────────────────────────────────────────


def format_run_result(run: PipelineRun, pipeline: PipelineDefinition) -> str:
    """Format a pipeline run result as a chat message."""
    total = len(pipeline.phases)
    passed = sum(1 for e in run.phases.values() if e.status == "passed")
    skipped = sum(1 for e in run.phases.values() if e.status == "skipped")

    lines: list[str] = []

    # Phase summary
    for phase_def in pipeline.phases:
        execution = run.phases.get(phase_def.id)
        if execution is None:
            lines.append(f"  {phase_def.id}: -")
            continue
        status_icon = {
            "passed": "\u2705",
            "failed": "\u274c",
            "skipped": "\u23ed\ufe0f",
            "pending": "\u23f3",
        }.get(execution.status, "\u2753")
        lines.append(f"  {status_icon} {phase_def.id}")

    phase_detail = "\n".join(lines)

    # Status line
    skip_info = f", {skipped} skipped" if skipped else ""
    if run.status == RunStatus.COMPLETED:
        header = f"\u2705 COMPLETED — {passed}/{total} phases passed{skip_info}"
    elif run.status == RunStatus.PAUSED_HITL:
        header = f"\u23f8\ufe0f PAUSED at {run.paused_at_phase} — {passed}/{total} phases passed"
    elif run.status == RunStatus.FAILED:
        header = f"\u274c FAILED — {passed}/{total} phases passed"
    else:
        header = f"{run.status.value} — {passed}/{total} phases"

    return f"Pipeline: {run.pipeline_name}\n{header}\n\n{phase_detail}\n\nRun ID: {run.run_id}"


def format_pause_message(run: PipelineRun) -> str:
    """Format a HITL pause notification with resume instructions."""
    return (
        f"Pipeline paused at phase: {run.paused_at_phase}\n\n"
        f"To continue:\n"
        f"  /pipeline resume {run.run_id}\n"
        f"  /pipeline resume {run.run_id} --decision revise\n"
        f"  /pipeline resume {run.run_id} --decision reject"
    )


def format_pipeline_list(names: list[str]) -> str:
    """Format available pipeline names for chat display."""
    if not names:
        return "No pipelines available."
    items = "\n".join(f"  - {name}" for name in sorted(names))
    return f"Available pipelines:\n{items}"


# ─── Dispatch handler ────────────────────────────────────────────────


class PipelineDispatchHandler:
    """Dispatches parsed pipeline commands to PipelineEngine.

    Provider-agnostic — communicates results via the send callback.

    RAISE-13580 SAFEGUARD (advance-authority reachability):
    ``RunCommand``/``ResumeCommand`` reach ``PipelineEngine.run``/``resume``
    WITHOUT the per-run advance token that gates the MCP ``pipeline_advance``
    surface. They are NOT threaded a token, and deliberately so: the ONLY
    producer of these commands is ``parse_pipeline_command`` (daemon CHAT
    text), wired ONLY from ``rai_agent.pipeline.middleware`` — the Telegram
    daemon, a SEPARATE process/package. A Task/Agent subagent runs in-process
    inside the raise_cli MCP server and can only invoke registered MCP tools;
    it has no channel to the daemon chat socket, so it cannot construct or
    dispatch a RunCommand/ResumeCommand at all. Threading a token here would
    instead fail-CLOSE a legitimate human daemon resume (the chat parser has
    no ``--token`` flag). The reachability barrier — not a token — is the
    safeguard for this surface. Enforced by test_dispatch_reachability.py.
    If this class ever becomes reachable from the MCP/subagent surface, that
    barrier is void and the design must be revisited.
    """

    def __init__(
        self,
        engine: PipelineEngine,
        loader: PipelineLoader,
    ) -> None:
        self._engine = engine
        self._loader = loader

    async def handle(self, command: PipelineCommand, send: SendFn) -> None:
        """Dispatch a pipeline command and send results via callback."""
        if isinstance(command, RunCommand):
            await self._handle_run(command, send)
        elif isinstance(command, ResumeCommand):
            await self._handle_resume(command, send)
        elif isinstance(command, ListCommand):
            await self._handle_list(send)
        else:
            await self._handle_status(command, send)

    async def _handle_run(self, command: RunCommand, send: SendFn) -> None:
        """Execute a pipeline run and report results.

        No advance-token check here — see the class SAFEGUARD note: this path
        is daemon-chat only (rai_agent Telegram middleware), unreachable by an
        in-process MCP/subagent caller (RAISE-13580).
        """
        try:
            pipeline = self._loader.load(command.name)
        except PipelineError as exc:
            await send(f"Error: {exc}")
            return

        await send(f"Starting pipeline: {command.name} ({len(pipeline.phases)} phases)")

        metadata = {"story_type": command.story_type}

        run = await self._engine.run(
            command.name,
            issue_id=command.issue,
            metadata=metadata,
        )

        await send(format_run_result(run, pipeline))

        if run.status == RunStatus.PAUSED_HITL:
            await send(format_pause_message(run))

    async def _handle_resume(self, command: ResumeCommand, send: SendFn) -> None:
        """Resume a paused pipeline and report results.

        No advance-token check here — see the class SAFEGUARD note: daemon-chat
        only, unreachable by an in-process MCP/subagent caller (RAISE-13580).
        """
        from datetime import UTC, datetime

        from raise_core.workflow.models import HitlDecision

        decision = HitlDecision(
            phase_id="",
            decision=command.decision,  # type: ignore[arg-type]
            actor="daemon-chat",
            timestamp=datetime.now(UTC),
        )

        try:
            run = await self._engine.resume(command.run_id, decision)
        except PipelineError as exc:
            await send(f"Error: {exc}")
            return

        pipeline = self._loader.load(run.pipeline_name)
        await send(format_run_result(run, pipeline))

        if run.status == RunStatus.PAUSED_HITL:
            await send(format_pause_message(run))

    async def _handle_list(self, send: SendFn) -> None:
        """List available pipelines."""
        names = self._loader.list_available()
        await send(format_pipeline_list(names))

    async def _handle_status(self, command: StatusCommand, send: SendFn) -> None:
        """Show status of a pipeline run."""
        run = await self._engine.get_run(command.run_id)
        if run is None:
            await send(f"Error: run {command.run_id} not found")
            return

        pipeline = self._loader.load(run.pipeline_name)
        await send(format_run_result(run, pipeline))
