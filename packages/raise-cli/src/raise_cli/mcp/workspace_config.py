"""Single source of truth for the rai-workspace MCP server entry.

All local writers (codex_plugin, provision, kimi_plugin) must consume these
builders.  No writer may hand-compose the command/args/env/enabled_tools for
the rai-workspace entry — that is the clone-amplification defect this module
was created to close (S15457.3 / ADR-042 MCP infrastructure layer).

Architecture:
- ``workspace_project_args``  — identity assertion argv (absolute path only)
- ``workspace_server_entry``  — JSON-harness dict (.mcp.json / .kimi-code/mcp.json)
- ``render_codex_config_toml`` — TOML renderer for .codex/config.toml

Design decisions (design doc: work/epics/e15457-stateless-mcp-server/stories/s15457.3-design.md):
  D1: One builder, four consumers — no hand-composed literals elsewhere.
  D2: Absolute --project argv is canonical; Codex also carries env.RAISE_PROJECT_ROOT
      from the same root so the two values cannot disagree.
  D3: A writer that cannot produce an absolute path omits --project entirely;
      it NEVER emits ".".
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

# --- Public constants -------------------------------------------------------

WORKSPACE_SERVER_NAME = "rai-workspace"
WORKSPACE_COMMAND = "rai-mcp-pipeline"

CODEX_ENABLED_TOOLS: list[str] = [
    # Pipeline lifecycle
    "pipeline_list",
    "pipeline_start",
    "pipeline_advance",
    "pipeline_pause",
    "pipeline_cancel",
    "pipeline_restore",
    "pipeline_status",
    "pipeline_runs",
    "pipeline_decision",
    # Gates / signals / tasks
    "raise_gate_check",
    "raise_signal_emit",
    "raise_task_complete",
    # Session
    "raise_session_open",
    "raise_session_close_full",
    "raise_session_context",
    "raise_session_history",
    "raise_session_topic",
    "raise_session_bind",
    "raise_ledger_add",
    # Story
    "raise_story_open",
    "raise_story_close_full",
    "raise_epic_story_create",
    # Backlog
    "raise_backlog_context",
    "raise_backlog_create",
    "raise_backlog_transition",
    "raise_backlog_update",
    # Artifacts
    "raise_artifact_emit",
    "raise_artifact_query",
    # Docs
    "raise_docs_get",
    "raise_docs_search",
    "raise_docs_write",
    # Graph
    "raise_graph_context",
    "raise_graph_query",
    # Patterns
    "raise_pattern_add",
    "raise_pattern_query",
    "raise_pattern_reinforce",
]


# --- Public builder functions ------------------------------------------------


def workspace_project_args(project_root: Path) -> list[str]:
    """Identity assertion argv: always an absolute, resolved checkout path.

    AC3 invariant: never emits a relative path or the portability marker ".".
    Validated at MCP server boot by ``validate_asserted_root`` (S15457.2).
    """
    return ["--project", str(project_root.resolve())]


def workspace_server_entry(command: str, project_root: Path) -> dict[str, object]:
    """JSON-harness entry for .mcp.json, .kimi-code/mcp.json, plugin manifests.

    Returns only ``command`` and ``args`` (no ``env``): Kimi and .mcp.json
    harnesses do not carry env-level assertions (D2 — argv is canonical).
    """
    return {
        "command": command,
        "args": workspace_project_args(project_root),
    }


def render_codex_config_toml(
    *,
    command: str,
    project_root: Path,
    enabled_tools: Sequence[str] = CODEX_ENABLED_TOOLS,
    timeout: int = 60,
) -> str:
    """Render .codex/config.toml for the rai-workspace MCP entry.

    AC4: Deterministic renderer — same inputs always produce identical output.
    AC5: env.RAISE_PROJECT_ROOT and --project argv are derived from the same
         ``project_root``, so they cannot disagree.

    The inline env var block is intentionally hand-formatted (not via
    ``tomllib`` round-trip) so that the output is stable and human-readable.
    """
    root = str(project_root.resolve())
    args_json = json.dumps(workspace_project_args(project_root))
    return (
        f"[mcp_servers.{WORKSPACE_SERVER_NAME}]\n"
        f"command = {json.dumps(command)}\n"
        f"args = {args_json}\n"
        f"env = {{ RAISE_PROJECT_ROOT = {json.dumps(root)} }}\n"
        f"timeout = {timeout}\n"
        f"enabled_tools = {json.dumps(list(enabled_tools))}\n"
    )
