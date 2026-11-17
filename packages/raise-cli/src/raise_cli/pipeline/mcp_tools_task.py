"""Composite task bookend MCP tool — S8370.1 (E8370 K1, ADR-093/ADR-024).

raise_task_complete collapses the inner task loop: scoped gates, branch-assert,
git add, git commit, and WorkLifecycle signal — all in one call.

Mirrors mcp_tools_story.py: thin @local_only async wrapper that runs the
service in asyncio.to_thread and returns compact_response(report.model_dump()).
The lifecycle signal is emitted inside the service (server-side side-effect,
K3 pattern) — never an LLM turn.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only


async def _task_complete_impl(
    work_id: str,
    task_name: str,
    expected_branch: str,
    commit_message: str,
    gate_scope: str = "",
    files: str = "",
    cwd: str = "",
) -> str:
    """Run the task-complete service and return a compact JSON response."""

    def _run() -> str:
        from raise_cli.task.complete_service import build_task_complete_report

        if not cwd:
            return compact_response(
                {
                    "status": "error",
                    "reason": (
                        "cwd is required — the MCP server CWD is pinned to the "
                        "main worktree and does not reflect the caller's checkout"
                    ),
                }
            )
        resolved_cwd = Path(cwd).resolve()
        report = build_task_complete_report(
            project_path=resolved_cwd,
            cwd=resolved_cwd,
            work_id=work_id,
            task_name=task_name,
            expected_branch=expected_branch,
            commit_message=commit_message,
            gate_scope=gate_scope,
            files=files,
        )
        payload: dict[str, Any] = report.model_dump()
        return compact_response(payload)

    return await asyncio.to_thread(_run)


@local_only
async def raise_task_complete(
    work_id: str,
    task_name: str,
    expected_branch: str,
    commit_message: str,
    gate_scope: str = "",
    files: str = "",
    cwd: str = "",
) -> str:
    """Collapse the inner task loop: gates + branch-assert + add + commit + signal.

    One call replaces the deterministic per-task sequence of the
    rai-story-implement skill. Statuses are ok|warn|blocked — blocked
    requires a human decision (the tool never auto-resolves); steps after
    a block are skipped.

    Response contract (RAISE-15493 F1 — hard, machine-readable):
    - ``committed`` (bool) — True only when a commit sha was produced.
      False on any block, including gate failures where the commit step was
      skipped but its status is "ok".  Never read per-step status alone to
      infer commit success — use this field.
    - ``blocking_gate`` (str | None) — name of the first blocked step
      ("gates", "branch", "stage", "commit"), or null on success.
    - ``remediation`` (str | None) — a single action string describing the
      required fix, or null on success.  Named for the specific gate that
      failed (lint / types / tests / format); no parsing of nested failures
      required.

    A blocked-gate response therefore CANNOT be misread as success::

        {"status":"blocked","committed":false,
         "blocking_gate":"gates",
         "remediation":"lint gate blocked — run ruff and fix violations before committing",
         "gates":{"name":"gates","status":"blocked","data":{"failures":["gate-lint: 3 violations"]}},
         "commit":{"name":"commit","status":"ok","data":{"skipped":true}}}

    Re-calling with the same failing state re-blocks (gates re-run every call;
    no persistent lock needed).  The manual ``git commit`` bypass (agent
    abandons the tool) is explicitly out of scope — this tool only governs
    commits made through ``raise_task_complete``.

    Args:
        work_id: Story/bugfix identifier (e.g. "S8370.1") for signal correlation.
        task_name: Free-text task name (e.g. "T2: step functions") — used
            in the WorkLifecycle signal ``task`` field.
        expected_branch: Branch that must be current before any git mutation.
        commit_message: Full commit message (LLM judgment, including Co-Author).
        gate_scope: Bare scope path for scoped gate run (e.g.
            "packages/raise-cli/tests/task/"); empty → full suite.
        files: Space-separated file paths to stage; empty → ``git add -u``
            (staged tracked changes only).
        cwd: Project/worktree directory. Required — omitting it returns an
            explicit error; the MCP server's own CWD is pinned to the main
            worktree and is never a valid substitute.
    """
    return await _task_complete_impl(
        work_id=work_id,
        task_name=task_name,
        expected_branch=expected_branch,
        commit_message=commit_message,
        gate_scope=gate_scope,
        files=files,
        cwd=cwd,
    )
