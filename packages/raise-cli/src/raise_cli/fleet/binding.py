"""PipelineBinder — implements FleetPipelineBinding (ADR-2026-08-05 §2, amended).

`bind()` mints a pipeline run via `pipeline_start` BEFORE the fleet subagent
is launched, and returns only the non-secret `run_id` onward (to
`SubagentDispatcher`/`FleetPromptBuilder`); the `advance_token` is returned
to the caller of `fleet_dispatch`, in the top-level `bindings` field (D9) —
never to a subagent, storage, or env var (RAISE-13580, RAISE-14555).

Lives at the `mcp_tools_fleet` MCP-tool boundary (D1) — `pipeline_start` is
pipeline I/O, forbidden inside `SubagentDispatcher` (F7).
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from raise_core.fleet.protocols import FleetRunBinding

logger = logging.getLogger(__name__)

#: Pipeline used for every fleet-dispatched story. fleet_dispatch only ever
#: queries Jira issuetype=Story (mcp_tools_fleet.py's jql), so "story" is the
#: single correct pipeline name — not a caller-supplied parameter (ADR §2).
_FLEET_PIPELINE_NAME = "story"


class PipelineBinder:
    """Implements `FleetPipelineBinding` — calls `pipeline_start` per story."""

    def __init__(self, cwd: str) -> None:
        self._cwd = cwd

    def bind(self, work_id: str) -> FleetRunBinding:
        """Start a "story" pipeline run for `work_id`; return (run_id, advance_token).

        Raises RuntimeError when `pipeline_start` does not return a running
        run (e.g. duplicate_run, lease rejection, cwd errors) or omits
        run_id/advance_token. Callers (D8.a) treat a raise here as
        `bind_failed` — nothing was minted, so nothing needs disposal.
        """
        from raise_cli.pipeline.mcp_tools_pipeline import pipeline_start

        async def _start() -> dict[str, Any]:
            raw = await pipeline_start(_FLEET_PIPELINE_NAME, work_id, cwd=self._cwd)
            result: dict[str, Any] = json.loads(raw)
            return result

        result = asyncio.run(_start())

        if result.get("status") != "running":
            reason = result.get("reason", result.get("status", "unknown"))
            raise RuntimeError(f"pipeline_start failed for {work_id}: {reason}")

        run_id = result.get("run_id")
        advance_token = result.get("advance_token")
        if not run_id or not advance_token:
            raise RuntimeError(
                f"pipeline_start for {work_id} returned no run_id/advance_token"
            )

        return FleetRunBinding(run_id=run_id, advance_token=advance_token)
