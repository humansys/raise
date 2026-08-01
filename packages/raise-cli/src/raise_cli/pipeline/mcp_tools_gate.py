"""Gate MCP tools — raise_gate_check."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raise_cli.gates.execution import GateNotFoundError, run_all_gates, run_gate
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only


def _gate_result_entry(r: Any) -> dict[str, Any]:
    """Render one GateResult as an MCP-friendly dict.

    RAISE-14280: surfaces ``advisory`` findings to MCP callers too — never
    silent, even though ``passed`` stays True. Blocking mode
    (``--strict-drift``) is CI-only (ADR-130): the agent-facing MCP path
    does not expose that flag.
    """
    entry: dict[str, Any] = {
        "gate_id": r.gate_id,
        "passed": r.passed,
        "message": r.message,
    }
    details = list(r.details)
    if details:
        entry["details"] = details
    if r.advisory:
        entry["advisory"] = True
    return entry


@local_only
def raise_gate_check(gate_id: str | None = None, cwd: str = "", scope: str = "") -> str:
    """Run quality gate checks.

    Args:
        gate_id: Specific gate to check (e.g., "lint", "coverage").
                 If omitted, checks all gates (timeout 60s).
        cwd: Working directory for gate resolution. Required — omitting it
             returns an explicit error; the MCP server's own CWD is pinned to
             the main worktree and is never a valid substitute.
        scope: Path argument appended to the gate command — parity with the CLI
               `rai gate check --scope` (RAISE-10441 / E10436). Lets worktree
               agents scope a test gate to the story's tests instead of the full
               suite. Empty means unscoped (full gate).

    Delegates to the gate-execution seam (RAISE-13749 T10): single gate_id →
    run_gate, omitted → run_all_gates. H2 (human-accepted): run_gate always
    sets GateContext.workflow_point=gate.workflow_point, so context-aware
    gates (e.g. gate-ar-bugfix) that used to silently pass via this MCP path
    (workflow_point was never set) now enforce — parity with the CLI.
    """
    if not cwd:
        return json.dumps(
            {
                "status": "error",
                "reason": (
                    "cwd is required — the MCP server CWD is pinned to the "
                    "main worktree and does not reflect the caller's checkout"
                ),
            }
        )
    working_dir = Path(cwd).resolve()
    extra_args: tuple[str, ...] = (scope,) if scope else ()

    try:
        if gate_id:
            try:
                results = [run_gate(gate_id, working_dir, extra_args=extra_args)]
            except GateNotFoundError:
                return json.dumps(
                    {"status": "error", "reason": f"Gate '{gate_id}' not found"}
                )
        else:
            report = run_all_gates(working_dir, extra_args=extra_args)
            results = list(report.results)

    except Exception as exc:  # noqa: BLE001
        return json.dumps({"status": "error", "reason": str(exc)})

    gates_data = [_gate_result_entry(r) for r in results]
    status = "ok" if all(r.passed for r in results) else "failed"
    if status == "failed":
        return json.dumps({"status": status, "gates": gates_data})
    return compact_response({"status": status, "gates": gates_data})
