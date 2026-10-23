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
import shutil
from collections.abc import Sequence
from pathlib import Path

from raise_cli.compat import IS_FROZEN

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


# --- Command resolution (RAISE-16279) ----------------------------------------


def _resolve_main_repo_mcp(worktree_path: Path) -> str | None:
    """Try to find rai-mcp-pipeline in the main repo's .venv-mcp (RAISE-15611)."""
    git_pointer = worktree_path / ".git"
    if not git_pointer.is_file():
        return None
    try:
        content = git_pointer.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not content.startswith("gitdir:"):
        return None
    raw = content.split(":", 1)[1].strip()
    gitdir = Path(raw) if Path(raw).is_absolute() else (worktree_path / raw).resolve()
    main_repo = gitdir.parent.parent.parent
    candidate = main_repo / ".venv-mcp" / "bin" / "rai-mcp-pipeline"
    if candidate.exists():
        return str(candidate.resolve())
    return None


def detect_mcp_pipeline_command(worktree_path: Path) -> str:
    """Resolve the ``rai-mcp-pipeline`` binary for a project/worktree.

    This is the **single** resolver for all writers (``codex_plugin``,
    ``provision``, etc.). No other module may perform its own resolution
    — doing so re-introduces the clone-amplification bug (RAISE-16279).

    Frozen (RAISE-15628): the installer guarantees ``rai-mcp-pipeline`` is
    on PATH, so ``.venv-mcp`` — a dev-only, per-worktree construct — is
    never checked. Resolves directly via ``shutil.which()``, falling back
    to the bare command name if PATH resolution fails.

    Dev (unchanged), resolution order:
      1. Absolute path inside the worktree's isolated ``.venv-mcp`` — preferred
         (RAISE-10767).
      2. ``shutil.which("rai-mcp-pipeline")`` — covers non-Python projects that
         have no local ``.venv-mcp`` and rely on a globally-installed rai
         (RAISE-15153).
      3. Main repo's ``.venv-mcp`` via git worktree pointer — covers non-Python
         worktrees where the parent repo has a Python venv (RAISE-15611).
      4. Bare ``"rai-mcp-pipeline"`` — last resort; accepted only when all
         above fail (e.g. CI bootstrap before first install).
    """
    if IS_FROZEN:
        return shutil.which("rai-mcp-pipeline") or "rai-mcp-pipeline"
    venv = worktree_path / ".venv-mcp"
    candidate = venv / "bin" / "rai-mcp-pipeline"
    if candidate.exists():
        return str(candidate.resolve())
    resolved = shutil.which("rai-mcp-pipeline")
    if resolved:
        resolved_path = Path(resolved)
        parts = resolved_path.parts
        in_foreign_venv = any(
            p in (".venv", ".venv-mcp") for p in parts
        ) and not resolved_path.is_relative_to(worktree_path)
        if not in_foreign_venv:
            return resolved
    main_resolved = _resolve_main_repo_mcp(worktree_path)
    if main_resolved:
        return main_resolved
    return "rai-mcp-pipeline"


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
