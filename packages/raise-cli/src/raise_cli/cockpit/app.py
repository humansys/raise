"""Workspace cockpit TUI — main entry point (S14777.1 / S14777.2 / S14777.3 / S14777.4).

Provides run_cockpit() called by `rai` bare invocation.

Architecture:
- Rich Live for rendering
- stdlib tty/termios for raw keypress (Linux/macOS)
- SqliteWorktreeStore for worktree list
- S14777.2: type-to-filter + preview pane
- S14777.3: agent picker + exec (this module)
- S14777.4: direct mode (--mission/--agent/--last) + cold provision
"""

from __future__ import annotations

import os
import select
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console, Group
from rich.live import Live
from rich.style import Style
from rich.table import Table
from rich.text import Text

from raise_cli.cockpit.agent import DetectedAgent, detect_agents
from raise_cli.cockpit.data import (
    GitWorktreeEntry as _GitWtNew,
)
from raise_cli.cockpit.data import (
    PreviewData,
    evaluate_readiness_async,
    evaluate_readiness_cached,
    fetch_preview_data,
    load_all_worktrees,
    main_repo_root,
)
from raise_cli.cockpit.data import (
    _readiness_bg_cache as _readiness_bg_cache,  # pyright: ignore[reportPrivateUsage]
)
from raise_cli.cockpit.data import (
    _readiness_bg_lock as _readiness_bg_lock,  # pyright: ignore[reportPrivateUsage]
)
from raise_cli.cockpit.data import (
    _readiness_bg_pending as _readiness_bg_pending,  # pyright: ignore[reportPrivateUsage]
)
from raise_cli.cockpit.data import (
    _readiness_cache as _readiness_cache,  # pyright: ignore[reportPrivateUsage]
)
from raise_cli.cockpit.filter import fuzzy_filter
from raise_cli.cockpit.launch import (
    ActiveWorktreeError,
    exec_agent,
    prepare_agent_launch,
)
from raise_cli.cockpit.state import load_last, save_last
from raise_cli.cockpit.worktree_ops import (
    close_orphan_worktree,
    register_existing_worktree,
    slugify,
)
from raise_cli.workspace.readiness import (
    WorkspaceReadinessFinding,
    WorkspaceReadinessReport,
    evaluate_workspace_readiness,
)
from raise_cli.worktree.base_resolver import (
    list_branch_candidates,
    resolve_worktree_base,
)
from raise_cli.worktree.provision import (
    ProvisionResult,
    WorktreeProvisioner,
    git_worktree_readiness_policy,
)

if TYPE_CHECKING:
    from raise_cli.cockpit.config import CockpitConfigStore
    from raise_cli.cockpit.pipeline_view import PipelineOverview
    from raise_cli.cockpit.sessions import SessionRow
    from raise_cli.storage.leases import Lease, SqliteLeaseStore
    from raise_cli.storage.worktrees import Worktree


def _worktree_id_key(w: Worktree) -> str:
    return w.worktree_id


def _get_lease_store() -> SqliteLeaseStore | None:
    """Return a SqliteLeaseStore for the current project, or None on error."""
    try:
        from raise_cli.storage.leases import SqliteLeaseStore as _Store

        return _Store(Path.cwd())
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None


# ---------------------------------------------------------------------------
# Design tokens (from design.md)
# ---------------------------------------------------------------------------
_BLUE = "#58A6FF"
_GREEN = "#3FB950"
_AMBER = "#D29922"
_RED = "#F85149"
_PURPLE = "#BC8CFF"
_TEXT_BRIGHT = "#F0F6FC"
_TEXT = "#C9D1D9"
_TEXT_DIM = "#8B949E"

_DOT_PROVISIONED_UNI = "●"
_DOT_STALE_UNI = "◑"
_DOT_NONE_UNI = "○"
_DOT_PROVISIONED_ASCII = "*"
_DOT_STALE_ASCII = "~"
_DOT_NONE_ASCII = "."


def _supports_unicode() -> bool:
    """Return True when the terminal locale advertises UTF-8 support."""
    for var in ("LC_ALL", "LC_CTYPE", "LANG"):
        val = os.environ.get(var, "")
        if val:
            return "utf" in val.lower()
    return False


def _dot_provisioned() -> str:
    return _DOT_PROVISIONED_UNI if _supports_unicode() else _DOT_PROVISIONED_ASCII


def _dot_stale() -> str:
    return _DOT_STALE_UNI if _supports_unicode() else _DOT_STALE_ASCII


def _dot_none() -> str:
    return _DOT_NONE_UNI if _supports_unicode() else _DOT_NONE_ASCII


def _footer_nav() -> str:
    return "j·k ↑↓" if _supports_unicode() else "j/k up/dn"


def _footer_confirm() -> str:
    return "↵" if _supports_unicode() else "enter"


def _footer_back() -> str:  # pyright: ignore[reportUnusedFunction]
    return "esc"


_STALE_DAYS = 7


# ---------------------------------------------------------------------------
# Workspace readiness cache — dual-layer
#
# Synchronous cache (_readiness_cache): used by _apply_health_filter which
# needs results inline.  Time-bucketed (30s TTL).
#
# Async cache (_readiness_bg_cache): used by the render path so the first
# frame paints immediately with grey dots.  A background thread populates
# the cache per path; subsequent renders pick up the result.
# ---------------------------------------------------------------------------


def _evaluate_readiness_cached(wt_path: Path) -> WorkspaceReadinessReport | None:
    """Delegate to cockpit.data.evaluate_readiness_cached."""
    return evaluate_readiness_cached(wt_path)


def _evaluate_readiness_async(wt_path: Path) -> WorkspaceReadinessReport | None:
    """Delegate to cockpit.data.evaluate_readiness_async."""
    return evaluate_readiness_async(wt_path)


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


class Mode(Enum):
    """TUI interaction mode."""

    LIST = "list"
    FILTER = "filter"
    AGENT_PICKER = "agent_picker"
    CONFIG = "config"  # S5: agent config tab
    SESSIONS = "sessions"  # S5: active sessions tab
    DETAIL = "detail"  # RAISE-15049: pipeline DETAIL view


# Public alias for external imports (e.g. tests, downstream callers)
CockpitMode = Mode


# Tab cycling order: LIST → CONFIG → SESSIONS → LIST
_TAB_CYCLE: dict[Mode, Mode] = {
    Mode.LIST: Mode.CONFIG,
    Mode.CONFIG: Mode.SESSIONS,
    Mode.SESSIONS: Mode.LIST,
}


def _tab_next(mode: Mode, key: str) -> Mode | None:
    """Return the target Mode for a tab-switching key, or None if not a tab key."""
    if key == "\t":
        return _TAB_CYCLE.get(mode)
    if key == "1":
        return Mode.LIST
    if key == "2":
        return Mode.CONFIG
    if key == "3":
        return Mode.SESSIONS
    return None


def _next_state_list(filter_query: str, key: str) -> tuple[Mode, str, bool]:
    if key in ("q", "escape"):
        return Mode.LIST, filter_query, True
    if key == "/":
        return Mode.FILTER, filter_query, False
    if key == "enter":
        return Mode.AGENT_PICKER, filter_query, False
    new_tab = _tab_next(Mode.LIST, key)
    if new_tab is not None:
        return new_tab, filter_query, False
    return Mode.LIST, filter_query, False


def _next_state_tab(mode: Mode, filter_query: str, key: str) -> tuple[Mode, str, bool]:
    if key == "q":
        return mode, filter_query, True
    if key == "escape":
        return Mode.LIST, filter_query, False
    new_tab = _tab_next(mode, key)
    if new_tab is not None and new_tab != mode:
        return new_tab, filter_query, False
    return mode, filter_query, False


def _next_state_filter(filter_query: str, key: str) -> tuple[Mode, str, bool]:
    if key == "escape":
        return Mode.LIST, "", False
    if key == "backspace":
        return Mode.FILTER, filter_query[:-1], False
    if len(key) == 1 and 0x20 <= ord(key) <= 0x7E:
        return Mode.FILTER, filter_query + key, False
    return Mode.FILTER, filter_query, False


def _next_state(
    mode: Mode,
    filter_query: str,
    key: str,
) -> tuple[Mode, str, bool]:
    """Pure state transition for a single keypress.

    Args:
        mode: Current interaction mode.
        filter_query: Current filter query string.
        key: Normalized key name from _read_key().

    Returns:
        Tuple of (new_mode, new_filter_query, quit_requested).
        quit_requested=True signals the TUI loop to exit.
    """
    if mode == Mode.LIST:
        if key == "i":
            # RAISE-15049: 'i' opens DETAIL view
            return Mode.DETAIL, filter_query, False
        return _next_state_list(filter_query, key)
    if mode in {Mode.CONFIG, Mode.SESSIONS}:
        return _next_state_tab(mode, filter_query, key)
    if mode == Mode.AGENT_PICKER:
        if key == "escape":
            return Mode.LIST, filter_query, False
        # Any other key in picker is a no-op at this level;
        # hotkey dispatch is handled by _picker_handle_key separately.
        return Mode.AGENT_PICKER, filter_query, False

    # DETAIL mode — RAISE-15049
    if mode == Mode.DETAIL:
        if key in ("escape", "q", "i"):
            return Mode.LIST, filter_query, False
        # j/k and r are handled in _handle_key (require state mutation)
        return Mode.DETAIL, filter_query, False

    # FILTER mode
    return _next_state_filter(filter_query, key)


def _picker_handle_key(
    key: str,
    agents: list[DetectedAgent],
) -> DetectedAgent | None:
    """Return the DetectedAgent whose hotkey matches key, or None.

    Pure function — no side effects.

    Args:
        key: Single-char keypress from _read_key().
        agents: List of detected agents for the current worktree.

    Returns:
        Matching DetectedAgent, or None if no match.
    """
    for agent in agents:
        if agent.key == key:
            return agent
    return None


# ---------------------------------------------------------------------------
# Preview data — git stats fetched per selection
# ---------------------------------------------------------------------------


def _fetch_preview_data(
    worktree: Worktree,
    repo_root: Path,
) -> PreviewData:
    """Delegate to cockpit.data.fetch_preview_data."""
    return fetch_preview_data(worktree, repo_root)


def _get_or_fetch_preview(
    wt: Worktree | None,
    cache: dict[str, PreviewData],
    repo_root: Path,
) -> PreviewData | None:
    """Return cached preview data for wt, fetching on first access."""
    if wt is None:
        return None
    if wt.worktree_id not in cache:
        cache[wt.worktree_id] = _fetch_preview_data(wt, repo_root)
    return cache[wt.worktree_id]


def _selected_worktree(filtered: list[Worktree], idx: int) -> Worktree | None:
    """Return the selected worktree from filtered list, or None."""
    return filtered[idx] if filtered and 0 <= idx < len(filtered) else None


def _refilter(
    worktrees: list[Worktree],
    query: str,
    current_idx: int,
) -> tuple[list[Worktree], int]:
    """Re-apply fuzzy filter and clamp selection index."""
    filtered = fuzzy_filter(worktrees, query, key=_worktree_id_key)
    if not filtered:
        return filtered, 0
    if current_idx >= len(filtered):
        return filtered, len(filtered) - 1
    return filtered, current_idx


def _apply_health_filter(
    worktrees: list[Worktree],
    broken_only: bool,
) -> list[Worktree]:
    """Filter worktrees to only non-ready entries when broken_only is True.

    Uses the shared readiness cache so repeated renders do not hit the filesystem.
    When broken_only is False, returns the list unchanged (identity).

    Args:
        worktrees: Candidates (typically already fuzzy-filtered).
        broken_only: When True, keep only entries where not report.is_ready.

    Returns:
        Filtered list (may be empty); original list when broken_only=False.
    """
    if not broken_only:
        return worktrees
    result: list[Worktree] = []
    for wt in worktrees:
        report = _evaluate_readiness_cached(Path(wt.path))
        # None means eval error — treat as not-ready (include in broken view)
        if report is None or not report.is_ready:
            result.append(wt)
    return result


# ---------------------------------------------------------------------------
# Worktree display helpers
# ---------------------------------------------------------------------------


def _get_status_dot(worktree: Worktree, last_commit_ts: float | None = None) -> Text:
    """Return a colored status dot for a worktree row."""
    if worktree.status == "unregistered":
        return Text("?", style=Style(color=_BLUE, bold=True))
    if worktree.status == "orphan":
        return Text("✗", style=Style(color=_RED, bold=True))

    wt_path = Path(worktree.path)
    report = _evaluate_readiness_async(wt_path)

    # None = pending or eval error — show grey dot; re-render picks up result.
    if report is None:
        return Text(_dot_none(), style=Style(color=_TEXT_DIM))

    stale = _is_stale(worktree, last_commit_ts)
    if report.is_ready and not stale:
        return Text(_dot_provisioned(), style=Style(color=_GREEN))
    if report.is_ready and stale:
        return Text(_dot_stale(), style=Style(color=_AMBER))
    return Text(_dot_none(), style=Style(color=_TEXT_DIM, dim=True))


def _is_stale(worktree: Worktree, last_commit_ts: float | None = None) -> bool:
    """Return True if the worktree's last commit is older than _STALE_DAYS days.

    Uses the git commit timestamp from PreviewData when available (accurate).
    Falls back to created_at when preview hasn't been fetched yet (conservative:
    a worktree created within the threshold is never shown as stale prematurely).
    """
    threshold_days = _STALE_DAYS
    now = datetime.now(UTC)

    if last_commit_ts is not None:
        last = datetime.fromtimestamp(last_commit_ts, UTC)
        return (now - last).days > threshold_days

    # Fallback: no preview data yet — use created_at as proxy.
    # A worktree created recently is assumed fresh until git data loads.
    try:
        created = datetime.fromisoformat(worktree.created_at)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)
        return (now - created).days > threshold_days
    except (ValueError, TypeError):
        return True


def _get_badge(
    worktree: Worktree,
    current_path: Path,
    last_commit_ts: float | None = None,
    *,
    active_leases: dict[str, Lease] | None = None,
) -> Text | None:
    """Return a badge Text for the worktree, or None if no badge applies.

    Priority: unregistered > orphan > active > open-here > stale
    """
    wt_path = Path(worktree.path)

    if worktree.status == "unregistered":
        return Text(" ? unregistered ", style=Style(color=_BLUE, bold=True))
    if worktree.status == "orphan":
        return Text(" ✗ orphan ", style=Style(color=_RED, bold=True))

    if active_leases and worktree.worktree_id in active_leases:
        return Text(" active ", style=Style(color=_GREEN, bold=True))

    try:
        current_path.relative_to(wt_path)
        return Text(" open-here ", style=Style(color=_GREEN, bold=True))
    except ValueError:
        pass

    if _is_stale(worktree, last_commit_ts):
        return Text(" stale ", style=Style(color=_AMBER))

    return None


def _render_row(
    worktree: Worktree,
    selected: bool,
    current_path: Path,
    col_width: int = 60,
    last_commit_ts: float | None = None,
    pipeline_text: Text | None = None,
) -> Text:
    """Render a single worktree row, hard-truncated to col_width characters.

    Truncating here (not relying on Rich's no_wrap) guarantees the row never
    bleeds into the adjacent preview column regardless of terminal width.

    Args:
        worktree: The worktree to render.
        selected: Whether this row is currently selected.
        current_path: CWD (for open-here detection).
        col_width: Max character width before truncation.
        last_commit_ts: Unix timestamp of last git commit (for stale detection).
        pipeline_text: RAISE-15049 pipeline glyph Text to append after row content.
    """
    # Build the full row first, then truncate to col_width
    line = Text(no_wrap=True, overflow="ellipsis")

    prefix = "› " if selected else "  "
    line.append(prefix, style=Style(color=_BLUE, bold=True) if selected else Style())
    line.append_text(_get_status_dot(worktree, last_commit_ts))
    line.append(" ")

    name_style = (
        Style(color=_TEXT_BRIGHT, bold=True) if selected else Style(color=_TEXT)
    )
    line.append(worktree.worktree_id, style=name_style)

    badge = _get_badge(worktree, current_path, last_commit_ts)
    if badge is not None:
        line.append("  ")
        line.append_text(badge)

    if worktree.branch:
        short_branch = worktree.branch.split("/")[-1][:24]
        line.append(f"  {short_branch}", style=Style(color=_TEXT_DIM))

    # Hard-truncate: measure plain text length and trim the Rich Text
    plain = line.plain
    if len(plain) > col_width:
        line.truncate(col_width - 1, overflow="ellipsis")

    # RAISE-15049: append pipeline cell glyph after truncation (short, doesn't wrap)
    if pipeline_text is not None and pipeline_text.plain:
        line.append("  ")
        line.append_text(pipeline_text)

    return line


def _render_list_panel(
    worktrees: list[Worktree],
    selected_idx: int,
    current_path: Path,
    filter_query: str,
    col_width: int = 60,
    viewport_rows: int = 20,
    scroll_offset: int = 0,
    preview_cache: dict[str, PreviewData] | None = None,
    pipeline_overview: PipelineOverview | None = None,
    active_leases: dict[str, Lease] | None = None,
) -> Text:
    """Render the worktree list pane (left column).

    Only renders the rows visible in the viewport window [scroll_offset,
    scroll_offset + viewport_rows). Each row is hard-truncated to col_width
    so Rich never wraps list content into the preview column.

    Args:
        worktrees: Filtered list of worktrees to display.
        selected_idx: Index of the currently selected row.
        current_path: CWD (for open-here detection).
        filter_query: Active filter string (used for empty-state message).
        col_width: Max characters per row before truncation.
        viewport_rows: Number of visible rows in the list pane.
        scroll_offset: Index of the first visible row.
        preview_cache: Cached PreviewData keyed by worktree_id.
        pipeline_overview: RAISE-15049 snapshot of pipeline runs per worktree.
        active_leases: Active worktree leases keyed by worktree_id.
    """
    if not worktrees:
        empty = Text()
        if filter_query:
            empty.append(
                "\n  [no matches]\n",
                style=Style(color=_TEXT_DIM, dim=True),
            )
        else:
            empty.append(
                "\n  No open workspaces found.\n", style=Style(color=_TEXT_DIM)
            )
            empty.append(
                "  Run `rai worktree register` to register one.\n",
                style=Style(color=_TEXT_DIM),
            )
        return empty

    # RAISE-15049: build pipeline cell for each worktree (once per render)
    _now = datetime.now(UTC)
    _pipeline_cells: dict[str, Text] = {}
    if pipeline_overview is not None:
        import raise_cli.cockpit.pipeline_view as _pv

        for wt in worktrees:
            runs = pipeline_overview.runs_by_worktree.get(wt.worktree_id, [])
            lease = (active_leases or {}).get(wt.worktree_id)
            _pipeline_cells[wt.worktree_id] = _pv.pipeline_cell(runs, lease, _now)

    lines = Text()
    visible = worktrees[scroll_offset : scroll_offset + viewport_rows]
    for i, wt in enumerate(visible):
        abs_idx = scroll_offset + i
        cached = (preview_cache or {}).get(wt.worktree_id)
        ts = cached.last_commit_ts if cached else None
        pipe_cell = _pipeline_cells.get(wt.worktree_id)
        row = _render_row(
            wt,
            abs_idx == selected_idx,
            current_path,
            col_width,
            ts,
            pipeline_text=pipe_cell,
        )
        lines.append_text(row)
        lines.append("\n")
    return lines


def _format_age(ts: float) -> str:
    """Return a human-readable relative age string for a unix timestamp."""
    delta = datetime.now(UTC) - datetime.fromtimestamp(ts, UTC)
    days = delta.days
    if days == 0:
        hours = delta.seconds // 3600
        return f"{hours}h ago" if hours > 0 else "just now"
    if days < 7:
        return f"{days}d ago"
    if days < 30:
        return f"{days // 7}w ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def _render_git_block(preview_data: PreviewData, col_width: int = 60) -> Text:
    """Render dirty/behind/commits section from PreviewData.

    Args:
        preview_data: Git state for the selected worktree.
        col_width: Max characters per line before hard truncation with ellipsis.
    """
    block = Text()
    if not preview_data.path_exists:
        block.append(
            f"  {preview_data.error or 'path not found'}",
            style=Style(color=_RED),
        )
        block.append("\n")
        return block

    dirty_style = (
        Style(color=_AMBER) if preview_data.dirty_count > 0 else Style(color=_TEXT_DIM)
    )
    block.append(f"  dirty: {preview_data.dirty_count}", style=dirty_style)
    block.append("\n")

    behind_style = (
        Style(color=_AMBER) if preview_data.behind_count > 0 else Style(color=_TEXT_DIM)
    )
    block.append(f"  behind: {preview_data.behind_count}", style=behind_style)
    block.append("\n")

    if preview_data.commits:
        block.append("  ─────────────────────\n", style=Style(color=_TEXT_DIM))
        for commit in preview_data.commits:
            line = f"  {commit}"
            if len(line) > col_width:
                line = line[: col_width - 1] + "…"
            block.append(line + "\n", style=Style(color=_TEXT_DIM))

    return block


def _render_preview_panel(  # noqa: C901
    worktree: Worktree | None,
    preview_data: PreviewData | None,
    mode: Mode,
    filter_query: str,
    col_width: int = 60,
) -> Text:
    """Render the preview pane (right column) for the selected worktree.

    Args:
        worktree: Selected worktree, or None when nothing is selected.
        preview_data: Cached git data, or None while loading.
        mode: Current UI mode (LIST, FILTER, AGENT_PICKER).
        filter_query: Active filter text (used for empty-state message).
        col_width: Max characters per line before hard truncation with ellipsis.
    """
    panel = Text()

    if worktree is None:
        msg = (
            "type to filter workspaces"
            if (mode == Mode.FILTER and filter_query)
            else "select a workspace to preview"
        )
        panel.append(f"\n  {msg}", style=Style(color=_TEXT_DIM, dim=True))
        return panel

    # --- Drift items: special header ---
    if worktree.status == "unregistered":
        panel.append("? unregistered", style=Style(color=_BLUE, bold=True))
        panel.append("\n")
        panel.append("  in git, not in DB\n", style=Style(color=_TEXT_DIM))
        panel.append("  ─────────────────────\n", style=Style(color=_TEXT_DIM))
        if worktree.branch:
            branch_line = f"  {worktree.branch}"
            if len(branch_line) > col_width:
                branch_line = branch_line[: col_width - 1] + "…"
            panel.append(branch_line, style=Style(color=_BLUE))
            panel.append("\n")
        if preview_data is None:
            panel.append("  loading…\n", style=Style(color=_TEXT_DIM, dim=True))
        else:
            if preview_data.last_commit_ts:
                panel.append(
                    f"  last commit: {_format_age(preview_data.last_commit_ts)}\n",
                    style=Style(
                        color=_AMBER
                        if _is_stale(worktree, preview_data.last_commit_ts)
                        else _TEXT_DIM
                    ),
                )
            panel.append_text(_render_git_block(preview_data, col_width=col_width))
        panel.append("\n  r register  x delete\n", style=Style(color=_TEXT_DIM))
        return panel

    if worktree.status == "orphan":
        panel.append("✗ orphan", style=Style(color=_RED, bold=True))
        panel.append("\n")
        panel.append("  in DB, directory gone\n", style=Style(color=_TEXT_DIM))
        panel.append("  ─────────────────────\n", style=Style(color=_TEXT_DIM))
        if worktree.branch:
            panel.append(f"  {worktree.branch}\n", style=Style(color=_BLUE))
        try:
            created = datetime.fromisoformat(worktree.created_at)
            created_age = _format_age(created.timestamp())
            panel.append(f"  registered: {created_age}\n", style=Style(color=_TEXT_DIM))
        except (ValueError, TypeError):
            pass
        panel.append("\n  d remove from DB\n", style=Style(color=_TEXT_DIM))
        return panel

    # --- Normal registered worktree ---
    wt_path = Path(worktree.path)
    report = _evaluate_readiness_async(wt_path)
    last_commit_ts = preview_data.last_commit_ts if preview_data else None
    stale = _is_stale(worktree, last_commit_ts)
    if report is None:
        panel.append(_dot_none() + " loading…", style=Style(color=_TEXT_DIM))
    elif report.is_ready and not stale:
        panel.append(_dot_provisioned() + " provisioned", style=Style(color=_GREEN))
    elif report.is_ready:
        panel.append(_dot_stale() + " stale", style=Style(color=_AMBER))
    else:
        panel.append(
            _dot_none() + " not-provisioned", style=Style(color=_TEXT_DIM, dim=True)
        )
        for finding in report.required_findings:
            code_line = f"  [{finding.code}]"
            if len(code_line) > col_width:
                code_line = code_line[: col_width - 1] + "…"
            panel.append(f"\n{code_line}", style=Style(color=_TEXT_DIM, dim=True))
    panel.append("\n")

    # Branch (truncate to col_width so long branch names don't wrap)
    if worktree.branch:
        branch_line = f"  {worktree.branch}"
        if len(branch_line) > col_width:
            branch_line = branch_line[: col_width - 1] + "…"
        panel.append(branch_line, style=Style(color=_BLUE))
        panel.append("\n")

    # Git data
    panel.append("  ─────────────────────\n", style=Style(color=_TEXT_DIM))

    if preview_data is None:
        panel.append("  loading…\n", style=Style(color=_TEXT_DIM, dim=True))
        return panel

    # Path
    path_line = f"  {preview_data.relative_path}"
    if len(path_line) > col_width:
        path_line = path_line[: col_width - 1] + "…"
    panel.append(path_line, style=Style(color=_TEXT_DIM))
    panel.append("\n")

    # Last commit age
    if preview_data.last_commit_ts:
        age_str = _format_age(preview_data.last_commit_ts)
        age_style = Style(color=_AMBER if stale else _TEXT_DIM)
        panel.append(f"  last commit: {age_str}\n", style=age_style)

    panel.append_text(_render_git_block(preview_data, col_width=col_width))
    return panel


# ---------------------------------------------------------------------------
# Tab bar renderer (S5)
# ---------------------------------------------------------------------------

_TAB_DEFS: list[tuple[Mode, str, str]] = [
    (Mode.LIST, "1", "launcher"),
    (Mode.CONFIG, "2", "config"),
    (Mode.SESSIONS, "3", "sessions"),
]


def _render_tab_bar(mode: Mode, total: int) -> Text:
    """Render the top-bar tab line for non-FILTER modes.

    Active tab is the current mode (AGENT_PICKER falls back to launcher).
    Uses ❮❯ brackets on unicode terminals, [] on ASCII.
    """
    uni = _supports_unicode()
    active = mode if mode in (Mode.CONFIG, Mode.SESSIONS) else Mode.LIST
    bar = Text()
    bar.append("  rai ", style=Style(color=_BLUE, bold=True))
    for i, (tab_mode, num, label) in enumerate(_TAB_DEFS):
        if i > 0:
            bar.append("  ", style=Style(color=_TEXT_DIM))
        text = f"❮{num} {label}❯" if uni else f"[{num} {label}]"
        plain = f"{num} {label}"
        if tab_mode == active:
            bar.append(text, style=Style(color=_BLUE, bold=True))
        else:
            bar.append(plain, style=Style(color=_TEXT_DIM))
    bar.append(
        f"  — {total} workspace{'s' if total != 1 else ''}",
        style=Style(color=_TEXT_DIM),
    )
    return bar


def _render_config_panel(
    agents: list[DetectedAgent],
    config_store: CockpitConfigStore | None,
    config_idx: int,
    cols: int = 80,
) -> Text:
    """Render the agent config editor panel for the Config tab.

    Args:
        agents: Available agents.
        config_store: Per-agent config store.
        config_idx: Index of currently highlighted agent row.
        cols: Terminal width (used to compute panel width dynamically).
    """
    # --- Column layout (fits within cols - 2 margin) ---
    # Box total width: panel_w  (includes the two │ border chars)
    # Inner width: panel_w - 2
    # Layout: cursor(2) + agent(14) + model(dynamic) + effort(10) + perms(6)
    panel_w = min(cols - 2, 78)
    agent_w = 14
    effort_w = 10
    perms_w = 6
    col_fixed = 2 + agent_w + effort_w + perms_w  # cursor + named cols
    model_w = max(20, panel_w - 2 - col_fixed)  # fill remaining inner width

    dim = Style(color=_TEXT_DIM)
    purple = Style(color=_PURPLE, bold=True)
    blue = Style(color=_BLUE, bold=True)
    amber = Style(color=_AMBER, bold=True)

    panel = Text()

    # Top border: ┌─ config ────...────┐
    prefix = "┌─ config "  # 10 chars
    panel.append(prefix, style=purple)
    panel.append("─" * (panel_w - len(prefix) - 1), style=dim)
    panel.append("┐\n", style=dim)

    if not agents or config_store is None:
        inner = panel_w - 2
        panel.append("│  ", style=dim)
        panel.append(
            f"{'no agents available':<{inner - 2}}",
            style=Style(color=_TEXT_DIM, italic=True),
        )
        panel.append("│\n", style=dim)
    else:
        # Header row
        panel.append("│  ", style=dim)
        panel.append(f"{'agent':<{agent_w}}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append(f"{'model':<{model_w}}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append(f"{'effort':<{effort_w}}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append(f"{'perms':<{perms_w}}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append("│\n", style=dim)

        # Separator: │  ─────...─────│
        panel.append("│  ", style=dim)
        panel.append("─" * (panel_w - 4), style=dim)
        panel.append("│\n", style=dim)

        for i, agent in enumerate(agents):
            cfg = config_store.get(agent.cmd)
            models = config_store.available_models(agent.cmd)
            is_selected = i == config_idx
            row_style = purple if is_selected else dim
            cursor = "▶ " if is_selected else "  "

            panel.append("│", style=dim)
            panel.append(cursor, style=row_style)
            name_str = agent.name[:agent_w]
            panel.append(f"{name_str:<{agent_w}}", style=row_style)

            # model column
            if cfg.model is not None:
                model_val = cfg.model[:model_w]
                panel.append(
                    f"{model_val:<{model_w}}",
                    style=Style(color=_TEXT_BRIGHT, bold=is_selected),
                )
            elif models:
                default_str = f"{models[0]} (default)"[:model_w]
                panel.append(f"{default_str:<{model_w}}", style=dim)
            else:
                panel.append(f"{'—':<{model_w}}", style=dim)

            # effort column
            effort_str = (cfg.effort if cfg.effort is not None else "—")[:effort_w]
            panel.append(
                f"{effort_str:<{effort_w}}",
                style=Style(
                    color=_TEXT_BRIGHT if cfg.effort else _TEXT_DIM, bold=is_selected
                ),
            )

            # perms column
            perm_str = (cfg.permissions if cfg.permissions != "default" else "—")[
                :perms_w
            ]
            perm_style = amber if cfg.permissions == "full" else dim
            panel.append(f"{perm_str:<{perms_w}}", style=perm_style)
            panel.append("│\n", style=dim)

    panel.append("│\n│  ", style=dim)
    panel.append("m", style=blue)
    panel.append(" model  ", style=dim)
    panel.append("e", style=blue)
    panel.append(" effort  ", style=dim)
    panel.append("p", style=blue)
    panel.append(" perms  ", style=dim)
    panel.append("↑↓", style=blue)
    panel.append(" select\n", style=dim)

    # Bottom border: └─────...─────┘
    panel.append("└", style=dim)
    panel.append("─" * (panel_w - 2), style=dim)
    panel.append("┘\n", style=dim)
    return panel


# ---------------------------------------------------------------------------
# Agent picker overlay renderer
# ---------------------------------------------------------------------------


def _render_picker_overlay(
    worktree_id: str,
    agents: list[DetectedAgent],
    selected_idx: int,
    last_key: str | None = None,
    config_store: CockpitConfigStore | None = None,
) -> Text:
    """Render the agent picker overlay panel.

    Args:
        worktree_id: The selected worktree's ID (shown in overlay header).
        agents: Detected agents for this worktree.
        selected_idx: Currently highlighted agent index (for ↑↓ nav).
        last_key: Agent key from last-used state (shown as "← last" label).
        config_store: Optional config store for showing launch config.

    Returns:
        Rich Text renderable for the overlay.
    """
    panel = Text()
    panel.append("┌─ agent ", style=Style(color=_BLUE, bold=True))
    panel.append("─" * 42, style=Style(color=_TEXT_DIM))
    panel.append("┐\n", style=Style(color=_TEXT_DIM))

    panel.append("│  mission: ", style=Style(color=_TEXT_DIM))
    panel.append(worktree_id, style=Style(color=_TEXT_BRIGHT))
    panel.append("\n")

    panel.append("│\n", style=Style(color=_TEXT_DIM))

    for i, agent in enumerate(agents):
        selected = i == selected_idx
        row_style = Style(color=_BLUE, bold=True) if selected else Style(color=_TEXT)
        unavail_style = Style(color=_TEXT_DIM, dim=True)

        panel.append("│  ", style=Style(color=_TEXT_DIM))
        panel.append(f"[{agent.key}]", style=Style(color=_AMBER, bold=True))
        panel.append(" ")

        if agent.available:
            panel.append(f"{agent.name:<18}", style=row_style)
            panel.append(agent.description, style=Style(color=_TEXT_DIM))
        else:
            panel.append(f"{agent.name:<18}", style=unavail_style)
            panel.append(agent.description, style=unavail_style)
            panel.append("  (not found)", style=Style(color=_RED))

        # Mark the previously-used agent
        if last_key is not None and agent.key == last_key:
            panel.append("  ← last", style=Style(color=_PURPLE))

        panel.append("\n")

    # Config section for the highlighted agent
    if agents and config_store is not None:
        highlighted = agents[selected_idx] if selected_idx < len(agents) else None
        if highlighted is not None and highlighted.cmd != "bash":
            cfg = config_store.get(highlighted.cmd)
            models = config_store.available_models(highlighted.cmd)
            panel.append("│\n", style=Style(color=_TEXT_DIM))
            panel.append("│  ── config ", style=Style(color=_PURPLE, bold=True))
            panel.append("─" * 39, style=Style(color=_TEXT_DIM))
            panel.append("\n")

            model_val = cfg.model or "(default)"
            panel.append("│  ", style=Style(color=_TEXT_DIM))
            panel.append("[m]", style=Style(color=_AMBER, bold=True))
            panel.append(f" model:  {model_val}", style=Style(color=_TEXT))
            if models:
                panel.append(
                    f"  ({len(models)} available)", style=Style(color=_TEXT_DIM)
                )
            panel.append("\n")

            effort_val = cfg.effort or "(default)"
            panel.append("│  ", style=Style(color=_TEXT_DIM))
            panel.append("[e]", style=Style(color=_AMBER, bold=True))
            panel.append(f" effort: {effort_val}", style=Style(color=_TEXT))
            panel.append("\n")

            perm_val = cfg.permissions
            panel.append("│  ", style=Style(color=_TEXT_DIM))
            panel.append("[p]", style=Style(color=_AMBER, bold=True))
            perm_style = (
                Style(color=_RED, bold=True)
                if perm_val == "full"
                else Style(color=_TEXT)
            )
            panel.append(f" perms:  {perm_val}", style=perm_style)
            panel.append("\n")

    panel.append("│\n", style=Style(color=_TEXT_DIM))
    panel.append(
        "│  c/o/h/s select  ↑↓ nav  ↵ confirm  esc back\n",
        style=Style(color=_TEXT_DIM),
    )
    panel.append("└", style=Style(color=_TEXT_DIM))
    panel.append("─" * 51, style=Style(color=_TEXT_DIM))
    panel.append("┘\n", style=Style(color=_TEXT_DIM))
    return panel


def _footer_text_for_mode(
    mode: Mode,
    filtered: list[Worktree],
    selected_idx: int,
) -> str:
    nav = _footer_nav()
    confirm = _footer_confirm()
    if mode == Mode.AGENT_PICKER:
        return f"  c/o/h/s select  {confirm} confirm  esc back"
    if mode == Mode.FILTER:
        return f"  esc clear filter  {confirm} open  {nav} nav"
    if mode == Mode.CONFIG:
        return "  1/2/3 tabs  tab cycle  esc launcher  q quit"
    if mode == Mode.SESSIONS:
        return "  x kill stale  1/2/3 tabs  tab cycle  esc launcher  q quit"
    sel_wt = _selected_worktree(filtered, selected_idx)
    sel_status = sel_wt.status if sel_wt else "open"
    if sel_status == "unregistered":
        return f"  r register  x delete  {nav} nav  n new  esc quit"
    if sel_status == "orphan":
        return f"  d remove from DB  {nav} nav  n new  esc quit"
    return f"  {confirm} open  / filter  f  x delete  {nav} nav  n new  esc quit"


# ---------------------------------------------------------------------------
# Frame renderer — header + two-column body + footer
# ---------------------------------------------------------------------------


def _render_frame(
    worktrees: list[Worktree],
    filtered: list[Worktree],
    selected_idx: int,
    mode: Mode,
    filter_query: str,
    current_path: Path,
    preview_data: PreviewData | None = None,
    agents: list[DetectedAgent] | None = None,
    picker_idx: int = 0,
    last_key: str | None = None,
    scroll_offset: int = 0,
    viewport_rows: int = 20,
    col_width: int = 60,
    cols: int = 80,
    preview_cache: dict[str, PreviewData] | None = None,
    broken_only: bool = False,
    flash_message: str | None = None,
    config_store: CockpitConfigStore | None = None,
    config_agents: list[DetectedAgent] | None = None,
    config_idx: int = 0,
    sessions_rows: list[SessionRow] | None = None,
    pipeline_overview: PipelineOverview | None = None,
    detail_run_idx: int = 0,
    active_leases: dict[str, Lease] | None = None,
) -> Group:
    """Render the full TUI frame: header + two-column body + footer.

    Args:
        worktrees: Full unfiltered list (total count derived from this).
        filtered: Filtered list shown in the list pane.
        selected_idx: Index of selected row within filtered list.
        mode: Current interaction mode.
        filter_query: Current filter query string.
        current_path: CWD (for open-here detection).
        preview_data: Cached git data for the selected worktree.
        agents: Detected agents for the selected worktree (AGENT_PICKER mode).
        picker_idx: Currently highlighted agent index in picker.
        last_key: Agent key from last-used state (shown as "← last" in picker).
        scroll_offset: Index of the first visible row in the list pane viewport.
        viewport_rows: Number of rows visible in the list pane.
        col_width: Maximum character width of each list row before truncation.
        cols: Full terminal column count (used by tab panels for dynamic width).
        preview_cache: Cached PreviewData keyed by worktree_id for age display.
        broken_only: When True, show a filter-active indicator in the footer.
        flash_message: One-shot message displayed in the footer (cleared on next key).
        config_store: Agent config store for picker overlay and config tab display.
        config_agents: Available agents list for the config tab.
        config_idx: Currently highlighted agent index in the config tab.
        sessions_rows: Pre-collected SessionRow list for the Sessions tab
            (None → renders empty panel).
        pipeline_overview: Snapshot of pipeline runs per worktree (RAISE-15049).
        detail_run_idx: Selected run index in DETAIL mode j/k navigation.
        active_leases: Active worktree leases keyed by worktree_id.

    Returns:
        Rich Group renderable (header + body table + footer).
    """
    total = len(worktrees)

    # --- Header ---
    if mode == Mode.FILTER:
        header = Text()
        header.append("  rai ", style=Style(color=_BLUE, bold=True))
        filtered_count = len(filtered)
        header.append(
            f"  {filtered_count} / {total}  ",
            style=Style(color=_AMBER),
        )
        header.append("/ ", style=Style(color=_AMBER, bold=True))
        header.append(filter_query, style=Style(color=_AMBER))
        header.append("█", style=Style(color=_AMBER))
    else:
        header = _render_tab_bar(mode, total)

    header.append("\n")

    # --- Body ---
    selected_wt = _selected_worktree(filtered, selected_idx)

    # RAISE-15049: DETAIL mode — show pipeline DETAIL panel
    if mode == Mode.DETAIL and selected_wt is not None:
        from typing import Any

        import raise_cli.cockpit.pipeline_view as _pv_detail

        runs_for_wt: list[dict[str, Any]] = []
        if pipeline_overview is not None:
            runs_for_wt = pipeline_overview.runs_by_worktree.get(
                selected_wt.worktree_id, []
            )

        lease_for_wt = (active_leases or {}).get(selected_wt.worktree_id)

        detail_text = _pv_detail.render_detail_panel(
            worktree=selected_wt,
            runs=runs_for_wt,
            lease=lease_for_wt,
            now=datetime.now(UTC),
            selected_run_idx=detail_run_idx,
            col_width=col_width,
        )
        body = Table.grid(expand=True, padding=0)
        body.add_column(ratio=1)
        body.add_row(detail_text)
    elif mode == Mode.AGENT_PICKER and agents is not None and selected_wt is not None:
        # Show picker overlay instead of two-column layout
        body_text = _render_picker_overlay(
            selected_wt.worktree_id,
            agents,
            picker_idx,
            last_key=last_key,
            config_store=config_store,
        )
        body = Table.grid(expand=True, padding=0)
        body.add_column(ratio=1)
        body.add_row(body_text)
    elif mode == Mode.CONFIG:
        body = Table.grid(expand=True, padding=0)
        body.add_column(ratio=1)
        body.add_row(
            _render_config_panel(
                config_agents or [],
                config_store,
                config_idx,
                cols=cols,
            )
        )
    elif mode == Mode.SESSIONS:
        from raise_cli.cockpit.sessions import (
            _render_sessions_panel,  # pyright: ignore[reportPrivateUsage]
        )

        body = Table.grid(expand=True, padding=0)
        body.add_column(ratio=1)
        body.add_row(_render_sessions_panel(sessions_rows or []))
    else:
        list_panel = _render_list_panel(
            filtered,
            selected_idx,
            current_path,
            filter_query,
            col_width=col_width,
            viewport_rows=viewport_rows,
            scroll_offset=scroll_offset,
            preview_cache=preview_cache,
            pipeline_overview=pipeline_overview,
            active_leases=active_leases,
        )
        preview_panel = _render_preview_panel(
            selected_wt, preview_data, mode, filter_query, col_width=col_width
        )
        body = Table.grid(expand=True, padding=0)
        body.add_column(ratio=1)
        body.add_column(ratio=1)
        body.add_row(list_panel, preview_panel)

    # --- Footer ---
    if mode == Mode.DETAIL:
        # RAISE-15049: DETAIL mode footer
        import raise_cli.cockpit.pipeline_view as _pv_footer

        unattached = pipeline_overview.unattached_count if pipeline_overview else 0
        footer_text = (
            "  [r] resume  [j/k] select run  [i/esc] back  |  "
            + _pv_footer.render_unattached_footer(unattached)
        )
    else:
        footer_text = _footer_text_for_mode(mode, filtered, selected_idx)
    footer = Text()
    if flash_message:
        footer.append(f"  {flash_message}", style=Style(color=_AMBER))
    else:
        footer.append(footer_text, style=Style(color=_TEXT_DIM))
    if broken_only and mode not in (Mode.AGENT_PICKER, Mode.DETAIL):
        footer.append("  [FILTER: broken only]", style=Style(color=_AMBER, bold=True))

    return Group(header, body, footer)


# ---------------------------------------------------------------------------
# Keypress capture (stdlib tty/termios, Linux/macOS)
# ---------------------------------------------------------------------------


def _raw_input_supported() -> bool:
    """Whether this platform can put the terminal in cbreak mode.

    tty/termios are Unix-only.  Importing them at module scope made bare `rai`
    crash on Windows with ModuleNotFoundError before any command could run
    (RAISE-15650), so the check is a runtime probe rather than an import.
    """
    try:
        import termios
        import tty
    except ModuleNotFoundError:
        return False
    return bool(termios and tty)


def _read_key(fd: int) -> str:
    """Read a single keypress from fd using cbreak mode.

    Uses tty.setcbreak (not setraw) so OPOST stays enabled.  setraw clears
    OPOST and concurrent terminal writes (Rich refresh thread) produce a
    staircase drift because bare newlines no longer imply carriage-return.

    Handles escape sequences for arrow keys (ESC [ A/B/C/D).
    Returns a normalized string: 'up', 'down', 'enter', 'backspace',
    'escape', or the raw character (including 'q', '/', etc.).

    Imports tty/termios lazily: they are Unix-only and this is their sole
    consumer, so the rest of the module stays importable on Windows.
    """
    import termios
    import tty

    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = os.read(fd, 1).decode("utf-8", errors="replace")

        if ch == "\x1b":
            # Use select with 50ms timeout to distinguish:
            #   bare ESC    → no bytes follow within 50ms → return "escape"
            #   arrow keys  → \x1b[A/B/C/D arrive immediately → decode and route
            # Without this, (a) bare ESC blocks indefinitely waiting for a
            # follow-up byte, and (b) unrecognized sequences (\x1b[C right-arrow)
            # were returned as "escape", which quit the TUI unexpectedly.
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                return "escape"  # bare ESC key, no sequence follows
            try:
                ch2 = os.read(fd, 1).decode("utf-8", errors="replace")
                if ch2 == "[":
                    r2, _, _ = select.select([fd], [], [], 0.05)
                    if r2:
                        ch3 = os.read(fd, 1).decode("utf-8", errors="replace")
                        if ch3 == "A":
                            return "up"
                        if ch3 == "B":
                            return "down"
                        # Right/left arrow or other CSI sequence → no-op
                return ""  # unrecognized escape sequence, ignore silently
            except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                return "escape"
        if ch in ("\r", "\n"):
            return "enter"
        if ch in ("\x7f", "\x08"):
            return "backspace"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ---------------------------------------------------------------------------
# Loop state helpers (reduce _run_tui cyclomatic complexity)
# ---------------------------------------------------------------------------


@dataclass
class _LoopState:
    """Mutable state for the main TUI loop."""

    mode: Mode
    filter_query: str
    selected_idx: int
    scroll_offset: int
    filtered: list[Worktree]
    picker_agents: list[DetectedAgent]
    picker_idx: int
    quit: bool = False
    new_worktree_slug: str | None = None  # set by 'n' flow; signals restart with new id
    broken_only: bool = False  # RAISE-14929: 'f' key broken-only filter
    flash_message: str | None = None
    config_store: CockpitConfigStore | None = None
    config_agents: list[DetectedAgent] = field(default_factory=list)
    config_idx: int = 0
    sessions_rows: list[SessionRow] = field(default_factory=list)
    sessions_idx: int = 0
    # RAISE-15049: DETAIL mode state
    detail_run_idx: int = 0  # selected run index in DETAIL j/k navigation
    # RAISE-15050: pipeline overview snapshot for 'r' key recovery
    pipeline_overview: PipelineOverview | None = None


def _detail_run_id(sel: Worktree, st: _LoopState) -> str | None:
    """Return the run_id of the selected run in DETAIL mode, or None.

    Uses the pipeline_overview snapshot stored in _LoopState (RAISE-15050 AC5).
    """
    if st.pipeline_overview is None:
        return None
    runs = st.pipeline_overview.runs_by_worktree.get(sel.worktree_id, [])
    if not runs:
        return None
    idx = min(st.detail_run_idx, len(runs) - 1)
    return runs[idx].get("run_id")


def _apply_nav_key(state: _LoopState, key: str, viewport_rows: int = 20) -> bool:
    """Handle j/k/up/down navigation, mutating selected_idx and scroll_offset.

    Keeps the selected row inside the visible viewport window.

    Args:
        state: Current TUI loop state.
        key: Normalized key from _read_key().
        viewport_rows: Number of visible rows in the list pane.

    Returns:
        True if the key was a nav key and was handled.
    """
    n = len(state.filtered)
    if not n:
        return key in ("j", "down", "k", "up")

    if key in ("j", "down"):
        state.selected_idx = (state.selected_idx + 1) % n
    elif key in ("k", "up"):
        state.selected_idx = (state.selected_idx - 1) % n
    else:
        return False

    # Scroll viewport to keep selection visible
    if state.selected_idx < state.scroll_offset:
        state.scroll_offset = state.selected_idx
    elif state.selected_idx >= state.scroll_offset + viewport_rows:
        state.scroll_offset = state.selected_idx - viewport_rows + 1

    return True


def _apply_list_key(
    state: _LoopState,
    key: str,
    worktrees: list[Worktree],
) -> None:
    """Handle a keypress in LIST or FILTER mode, mutating state in place.

    Args:
        state: Current TUI loop state (mutated).
        key: Normalized key from _read_key().
        worktrees: Full unfiltered worktree list.
    """
    prev_mode = state.mode
    new_mode, new_query, quit_ = _next_state(state.mode, state.filter_query, key)
    state.quit = quit_
    state.mode = new_mode
    state.filter_query = new_query
    if quit_:
        return
    if new_mode in {Mode.AGENT_PICKER, Mode.CONFIG} and prev_mode == Mode.LIST:
        sel = _selected_worktree(state.filtered, state.selected_idx)
        if sel:
            agents = detect_agents(Path(sel.path))
            try:
                from raise_cli.cockpit.config import (
                    CockpitConfigStore as ConfigStore,
                )

                state.config_store = ConfigStore(Path(sel.path))
            except Exception:  # noqa: BLE001
                state.config_store = None
            if new_mode == Mode.AGENT_PICKER:
                state.picker_agents = agents
                state.picker_idx = 0
            else:
                state.config_agents = [a for a in agents if a.available]
                state.config_idx = 0
        else:
            state.mode = Mode.LIST
    elif new_mode == Mode.CONFIG and prev_mode in {Mode.SESSIONS}:
        # Tab-switching between CONFIG and SESSIONS: reuse existing config_store
        # but reset cursor position
        state.config_idx = 0
    elif new_mode not in {Mode.AGENT_PICKER, Mode.CONFIG}:
        state.filtered, state.selected_idx = _refilter(
            worktrees, new_query, state.selected_idx
        )


def _handle_picker_key(
    key: str,
    agents: list[DetectedAgent],
    picker_idx: int,
) -> tuple[str, int, DetectedAgent | None]:
    """Dispatch a keypress in AGENT_PICKER mode.

    Args:
        key: Normalized key from _read_key().
        agents: Detected agents list.
        picker_idx: Current highlight index.

    Returns:
        Tuple of (action, new_picker_idx, agent_or_none) where action is one of:
        - "nav":    picker_idx changed, continue in picker
        - "launch": launch the returned DetectedAgent
        - "back":   exit picker back to LIST
        - "noop":   no change
    """
    if key in ("j", "down") and agents:
        return "nav", (picker_idx + 1) % len(agents), None
    if key in ("k", "up") and agents:
        return "nav", (picker_idx - 1) % len(agents), None
    if key == "enter" and agents:
        return "launch", picker_idx, agents[picker_idx]
    if key == "escape":
        return "back", picker_idx, None
    if len(key) == 1:
        match = _picker_handle_key(key, agents)
        if match is not None:
            return "launch", picker_idx, match
    return "noop", picker_idx, None


# ---------------------------------------------------------------------------
# New-worktree creation flow (invoked by 'n' in LIST mode)
# ---------------------------------------------------------------------------


_GitWt = _GitWtNew


def _load_all_worktrees() -> list[Worktree]:
    """Delegate to cockpit.data.load_all_worktrees."""
    return load_all_worktrees()


@dataclass
class _DeleteSafety:
    """Deterministic git-based safety signals for worktree deletion."""

    dirty_files: int  # uncommitted changes (lost on delete)
    unpushed_commits: int  # commits ahead of origin/{branch} — may be lost
    unmerged_commits: int  # commits not yet in merge_target — work would vanish
    remote_exists: bool  # branch exists on origin — is there a backup?

    @property
    def is_safe(self) -> bool:
        """True only when there is nothing that could be lost."""
        return (
            self.dirty_files == 0
            and self.unmerged_commits == 0
            and (self.unpushed_commits == 0 or self.remote_exists)
        )

    @property
    def label(self) -> str:
        if self.dirty_files > 0 or (self.unmerged_commits > 0):
            return "UNSAFE"
        if self.unpushed_commits > 0 and not self.remote_exists:
            return "RISKY"
        return "SAFE"


def _check_delete_safety(
    path: Path, branch: str | None, merge_target: str
) -> _DeleteSafety:
    """Run git checks to assess how safe it is to delete a worktree.

    All checks use subprocess; no AI inference involved.

    Args:
        path: Absolute path to the worktree directory.
        branch: Branch name checked out in this worktree.
        merge_target: The branch work is expected to merge into.

    Returns:
        _DeleteSafety with counts derived directly from git output.
    """

    def _run(args: list[str]) -> str:
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=5)
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:  # noqa: BLE001
            return ""

    g = ["git", "-C", str(path)]

    # 1. Dirty files (uncommitted changes)
    dirty_out = _run(g + ["status", "--short", "--porcelain"])
    dirty = len([ln for ln in dirty_out.splitlines() if ln.strip()])

    # 2. Unpushed commits (commits ahead of origin/branch)
    unpushed = 0
    if branch:
        out = _run(g + ["rev-list", f"origin/{branch}..HEAD", "--count"])
        unpushed = int(out) if out.isdigit() else 0

    # 3. Unmerged commits (commits not yet in merge_target)
    unmerged_out = _run(
        g + ["log", "HEAD", "--not", f"origin/{merge_target}", "--oneline"]
    )
    # Also try local merge_target if origin/<target> is unknown
    if not unmerged_out:
        unmerged_out = _run(g + ["log", "HEAD", "--not", merge_target, "--oneline"])
    unmerged = len([ln for ln in unmerged_out.splitlines() if ln.strip()])

    # 4. Remote branch existence
    remote_check = ""
    if branch:
        remote_check = _run(
            ["git", "-C", str(path), "ls-remote", "--heads", "origin", branch]
        )
    remote_exists = bool(remote_check)

    return _DeleteSafety(
        dirty_files=dirty,
        unpushed_commits=unpushed,
        unmerged_commits=unmerged,
        remote_exists=remote_exists,
    )


def _delete_unregistered_worktree(wt: Worktree) -> None:
    """Delete an unregistered git worktree from disk and remove its branch."""
    repo_root = _main_repo_root()
    path = Path(wt.path)
    merge_target = wt.merge_target or "release/3.1.0"

    print()
    print(f"  Delete unregistered workspace: {wt.worktree_id}")
    print(f"  path:   {path}")
    print(f"  branch: {wt.branch or '(unknown)'}")
    _print_last_commit(path)

    safety = _print_safety_report(path, wt.branch, merge_target)
    if not _confirm_delete(safety):
        print("  Cancelled.")
        input("\n  Press Enter to return to cockpit...")
        return

    _remove_worktree_and_branch(repo_root, path, wt.branch, wt.worktree_id)


def _print_safety_report(
    path: Path, branch: str | None, merge_target: str
) -> _DeleteSafety | None:
    """Print deterministic git safety checks and return the result (or None on error)."""
    print()
    print("  Safety check (git-based, no inference):")
    try:
        safety = _check_delete_safety(path, branch, merge_target)
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        print(f"  (safety check failed: {exc})")
        return None

    def _ok(cond: bool) -> str:
        return "  ✓" if cond else "  ✗"

    print(
        f"{_ok(safety.dirty_files == 0)} dirty files:       {safety.dirty_files} (uncommitted — lost on delete)"
    )
    print(
        f"{_ok(safety.unmerged_commits == 0)} unmerged commits:  {safety.unmerged_commits} (not yet in {merge_target})"
    )
    print(
        f"{_ok(safety.unpushed_commits == 0)} unpushed commits:  {safety.unpushed_commits} (not on origin/{branch or '?'})"
    )
    print(
        f"{_ok(safety.remote_exists)} branch on remote:  {'yes' if safety.remote_exists else 'no'}"
    )

    if safety.label == "SAFE":
        print("\n  Assessment: SAFE — no work will be lost")
    elif safety.label == "RISKY":
        print("\n  Assessment: RISKY — unpushed commits with no remote backup")
    else:
        print("\n  Assessment: UNSAFE — uncommitted or unmerged work will be lost")
    return safety


def _confirm_delete(safety: _DeleteSafety | None) -> bool:
    """Ask for delete confirmation. Returns True if user confirms."""
    print()
    prompt = "  Delete? [y/N]: "
    if safety and safety.label == "UNSAFE":
        prompt = "  UNSAFE — potential data loss. Delete anyway? [y/N]: "
    try:
        return input(prompt).strip().lower() == "y"
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _delete_registered_worktree(wt: Worktree) -> None:
    """Delete a registered worktree: close DB entry + remove from disk + delete branch."""
    repo_root = _main_repo_root()
    rai_cmd = str(Path(sys.executable).parent / "rai")
    path = Path(wt.path)
    merge_target = wt.merge_target or "release/3.1.0"

    print()
    print(f"  Delete registered workspace: {wt.worktree_id}")
    print(f"  path:   {path}")
    print(f"  branch: {wt.branch or '(unknown)'}")
    _print_last_commit(path)

    safety = _print_safety_report(path, wt.branch, merge_target)
    if not _confirm_delete(safety):
        print("  Cancelled.")
        input("\n  Press Enter to return to cockpit...")
        return

    result = subprocess.run(
        [rai_cmd, "worktree", "complete", "--name", wt.worktree_id],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ✗ worktree complete failed: {result.stderr.strip()}", file=sys.stderr)
        input("\n  Press Enter to return to cockpit...")
        return
    _remove_worktree_and_branch(repo_root, path, wt.branch, wt.worktree_id)


def _print_last_commit(path: Path) -> None:
    """Print the last commit for human context."""
    try:
        log = subprocess.run(
            ["git", "-C", str(path), "log", "-1", "--format=%h %s (%cr)"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if log.returncode == 0 and log.stdout.strip():
            print(f"  last:   {log.stdout.strip()}")
    except Exception:  # noqa: BLE001,S110
        pass


def _remove_worktree_and_branch(
    repo_root: Path, path: Path, branch: str | None, worktree_id: str
) -> None:
    """Remove git worktree from disk and delete its branch."""
    r1 = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "remove", "--force", str(path)],
        capture_output=True,
        text=True,
    )
    if r1.returncode != 0:
        print(f"  ✗ worktree remove failed: {r1.stderr.strip()}", file=sys.stderr)
        input("\n  Press Enter to return to cockpit...")
        return

    if branch:
        subprocess.run(
            ["git", "-C", str(repo_root), "branch", "-D", branch],
            capture_output=True,
        )

    print(f"  ✓ {worktree_id} deleted")
    input("\n  Press Enter to return to cockpit...")


def _register_existing_worktree(wt: Worktree) -> None:
    """Delegate to cockpit.worktree_ops.register_existing_worktree."""
    register_existing_worktree(wt)


def _close_orphan_worktree(wt: Worktree) -> None:
    """Delegate to cockpit.worktree_ops.close_orphan_worktree."""
    close_orphan_worktree(wt)


def _slugify(text: str) -> str:
    """Delegate to cockpit.worktree_ops.slugify."""
    return slugify(text)


def _main_repo_root() -> Path:
    """Delegate to cockpit.data.main_repo_root."""
    return main_repo_root()


def _new_worktree_interactive() -> str | None:  # noqa: C901
    """Interactive new-worktree creation flow (runs after Live is stopped).

    Prompts for a name, creates a git worktree branch, registers and
    provisions it via rai CLI.  Returns the new slug on success, None on
    abort or error.  The caller is responsible for stopping Live before
    calling this function.
    """
    repo_root = _main_repo_root()

    repo_name = repo_root.name

    # RAISE-15825 Regla 1: base-branch resolution is delegated to the shared
    # resolver — the same one the rai-worktree-open skill calls — instead of
    # a second, crude implementation (the old _read_merge_target() single-
    # line manifest grep). Prompting for an editable base branch (pre-filled
    # with the resolver's default) is what actually fixes "it always comes
    # from release/3.1.0, I can't choose" — the direct complaint that
    # motivated this story.
    resolved = resolve_worktree_base(repo_root)
    default_base = str(resolved.data["branch"])
    # RAISE-15911: the base-branch prompt was free-text only — the developer
    # had to already know and type the exact branch name. Surface a short
    # numbered list (sibling-worktree branches, then recent local branches)
    # so the common case is a keystroke instead of a memorized name; free
    # text remains the fallback for anything not listed.
    candidates = list_branch_candidates(repo_root)

    print()
    print("  New workspace")
    print("  ─────────────────────────────────────")
    for w in resolved.data.get("warnings", []):
        print(f"  ⚠ {w}")
    if candidates:
        print("  Candidate branches:")
        for i, branch in enumerate(candidates, start=1):
            print(f"    {i}) {branch}")
    try:
        base_input = input(f"  Base branch [{default_base}] (number or name): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if base_input.isdigit():
        index = int(base_input)
        if 1 <= index <= len(candidates):
            base_input = candidates[index - 1]

    if base_input and base_input != default_base:
        resolved = resolve_worktree_base(repo_root, explicit_base=base_input)
        for w in resolved.data.get("warnings", []):
            print(f"  ⚠ {w}")

    merge_target = str(resolved.data["branch"])
    base_ref = str(resolved.data["base_ref"])

    try:
        raw = input("  Name (slug): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if not raw:
        return None

    slug = _slugify(raw)
    if not slug:
        print("  ✗ invalid name", file=sys.stderr)
        return None

    branch = f"feature/{slug}"
    worktree_path = repo_root / ".worktree" / f"{repo_name}-{slug}"

    print()
    print(f"  → worktree  .worktree/{repo_name}-{slug}")
    print(f"  → branch    {branch} → {merge_target}")
    print()

    # git worktree add — handle partial state from a previous failed attempt:
    #   • worktree dir already exists → git step already done, skip it
    #   • branch exists but dir doesn't → checkout existing branch (no -b)
    #   • fresh → base directly on the resolver's `base_ref` — it has already
    #     fetched/reconciled/detected-local-sibling as needed (RAISE-15825
    #     Regla 1); no separate fetch here.
    if worktree_path.exists():
        print("  ✓ worktree already exists (resuming registration)")
    else:
        result = subprocess.run(
            [
                "git",
                "worktree",
                "add",
                str(worktree_path),
                "-b",
                branch,
                base_ref,
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.returncode != 0 and "already exists" in result.stderr:
            # Branch was created in a previous attempt; check it out without -b
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch],
                capture_output=True,
                text=True,
                cwd=repo_root,
            )
        if result.returncode != 0:
            print(result.stdout, end="")
            print(result.stderr, end="", file=sys.stderr)
            print(
                f"  ✗ git worktree add failed (exit {result.returncode})",
                file=sys.stderr,
            )
            input("\n  Press Enter to return to cockpit...")
            return None
        # Show git's own output (e.g. "Preparing worktree…")
        if result.stdout:
            print(result.stdout, end="")

    print("  ✓ worktree ready")
    print("  ◐ registering and provisioning…")

    # Use the rai from the same venv that's running the cockpit.
    # sys.executable is e.g. ".../raise-commons-e14777-cockpit-mvp/.venv/bin/python";
    # the rai script sits next to it and is guaranteed to have all subcommands.
    # Never rely on the PATH rai — it may be an older install without `worktree`.
    rai_cmd = str(Path(sys.executable).parent / "rai")

    # Provisioning now runs by default (S14897.2: --provision removed).
    # register exits 1 if provisioning does not achieve readiness.
    result = subprocess.run(
        [
            rai_cmd,
            "worktree",
            "register",
            "--name",
            slug,
            "--path",
            str(worktree_path.resolve()),
            "--branch",
            branch,
            "--merge-target",
            merge_target,
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        print(f"  ✗ registration failed (exit {result.returncode})", file=sys.stderr)
        # Roll back the git step so git and DB stay in sync.
        # If rollback fails, print the manual commands to avoid leaving the
        # user with a git worktree that has no DB counterpart.
        rb_wt = subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=repo_root,
            capture_output=True,
        )
        rb_br = subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=repo_root,
            capture_output=True,
        )
        if rb_wt.returncode == 0 and rb_br.returncode == 0:
            print("  ✓ git worktree rolled back — no partial state", file=sys.stderr)
        else:
            print("  ✗ rollback incomplete — clean up manually:", file=sys.stderr)
            if rb_wt.returncode != 0:
                print(
                    f"    git worktree remove --force {worktree_path}", file=sys.stderr
                )
            if rb_br.returncode != 0:
                print(f"    git branch -D {branch}", file=sys.stderr)
        input("\n  Press Enter to return to cockpit...")
        return None

    print(f"  ✓ {slug} ready")
    input("\n  Press Enter to return to cockpit...")
    return slug


# ---------------------------------------------------------------------------
# Main TUI loop
# ---------------------------------------------------------------------------


def _find_current_worktree_idx(worktrees: list[Worktree], current_path: Path) -> int:
    """Return index of the worktree that contains current_path, or 0.

    When rai is launched from inside a worktree, pre-selects that entry
    so the user sees their current context highlighted on first paint.
    """
    for i, wt in enumerate(worktrees):
        try:
            current_path.relative_to(Path(wt.path))
            return i
        except ValueError:
            continue
    return 0


def _find_worktree_idx_by_id(worktrees: list[Worktree], target_id: str) -> int:
    """Return index of the worktree whose worktree_id matches target_id, or 0."""
    for i, wt in enumerate(worktrees):
        if wt.worktree_id == target_id:
            return i
    return 0


def _handle_key(  # noqa: C901
    st: _LoopState,
    key: str,
    worktrees: list[Worktree],
    live: Live,
    viewport_rows: int,
) -> bool:
    """Process one keypress, mutating st. Returns True when the loop should exit."""
    # RAISE-15049: DETAIL mode — j/k navigate runs, r launches recovery, Esc/q/i go back
    if st.mode == Mode.DETAIL:
        sel = _selected_worktree(st.filtered, st.selected_idx)
        if key in ("j", "down"):
            # Navigate to next run in DETAIL view
            st.detail_run_idx += 1
            return False
        if key in ("k", "up"):
            # Navigate to previous run
            st.detail_run_idx = max(0, st.detail_run_idx - 1)
            return False
        if key == "r":
            # RAISE-15050 (AC5, §3.4): Recovery launch with ABA-protected force-release.
            if sel is None:
                st.flash_message = "No worktree selected"
                return False
            # Resolve selected run (from pipeline_overview stored in TUI loop state)
            run_id = _detail_run_id(sel, st)
            if not run_id:
                st.flash_message = "No stale/paused run to recover in this view"
                return False
            # Check lease state
            lease_store = _get_lease_store()
            live_lease = (
                lease_store.get_live_or_reap(sel.worktree_id)
                if lease_store is not None
                else None
            )
            live.stop()
            # ABA-protected force-release path (§3.6)
            if live_lease is not None:
                from raise_cli.storage.leases import pid_alive as _pid_alive  # noqa: I001

                print()
                print(f"  ⚠  Worktree '{sel.worktree_id}' has an active lease holder:")
                print(f"     session: {live_lease.session_id}")
                _pid_str = "alive" if _pid_alive(live_lease.pid) else "dead"
                print(f"     pid:     {live_lease.pid} ({_pid_str})")
                print(f"     last heartbeat: {live_lease.heartbeat_at}")
                print()
                print("  This may be a live session OR a shared MCP server.")
                print("  WARNING: if this IS a live session, it will lose its advance")
                print("  token and must re-authorize (run rai pipeline token reissue).")
                print()
                try:
                    confirm = (
                        input("  Force-release and recover? [y/N]: ").strip().lower()
                    )
                except (EOFError, KeyboardInterrupt):
                    print()
                    confirm = ""
                if confirm != "y":
                    print("  Aborted — no changes made.")
                    input("\n  Press Enter to return to cockpit...")
                    st.quit = True
                    return True
                # ABA protection (Sol R2): compare-and-delete with observed heartbeat.
                if lease_store is not None:
                    released = lease_store.release_if_heartbeat_matches(
                        sel.worktree_id,
                        session_id=live_lease.session_id,
                        observed_heartbeat_at=live_lease.heartbeat_at,
                    )
                    if not released:
                        print()
                        print(
                            "  ✗ Lease state changed between display and confirmation"
                        )
                        print("    (ABA race — the holder renewed the lease).")
                        print("    Refresh with 'u' and try again.")
                        input("\n  Press Enter to return to cockpit...")
                        st.quit = True
                        return True
                    print("  ✓ Lease released")

            # Exec recovery agent with RAISE_RECOVERY_RUN_ID (§3.4 step 3)
            agents = detect_agents(Path(sel.path))
            agent = next((a for a in agents if a.available and a.cmd != "bash"), None)
            if agent is None:
                print()
                print(f"  ✗ No available agent found for worktree '{sel.worktree_id}'")
                print(f"    Recovery run_id: {run_id}")
                print("    Start an agent manually with:")
                print(f"      RAISE_RECOVERY_RUN_ID={run_id} claude --cwd {sel.path}")
                input("\n  Press Enter to return to cockpit...")
                st.quit = True
                return True

            launch_id = ""
            if lease_store is not None:
                try:
                    prep = prepare_agent_launch(
                        lease_store, sel.worktree_id, agent, allow_conflict=True
                    )
                    launch_id = prep.launch_id
                except Exception:  # noqa: BLE001,S110
                    pass

            save_last(sel.worktree_id, agent.key)
            exec_agent(
                Path(sel.path),
                agent,
                launch_id=launch_id,
                extra_env={"RAISE_RECOVERY_RUN_ID": run_id},
            )
            return True

        # All other keys (i/esc/q + others) → delegate to _next_state
        new_mode, new_query, quit_ = _next_state(st.mode, st.filter_query, key)
        st.mode = new_mode
        st.filter_query = new_query
        st.quit = quit_
        if new_mode == Mode.LIST:
            st.detail_run_idx = 0  # reset run selection on exit
        return quit_

    if st.mode == Mode.AGENT_PICKER:
        # Config keys: m/e/p cycle model/effort/permissions for highlighted agent
        if key in ("m", "e", "p") and st.config_store is not None and st.picker_agents:
            highlighted = (
                st.picker_agents[st.picker_idx]
                if st.picker_idx < len(st.picker_agents)
                else None
            )
            if highlighted is not None and highlighted.cmd != "bash":
                if key == "m":
                    st.config_store.cycle_model(highlighted.cmd)
                elif key == "e":
                    st.config_store.cycle_effort(highlighted.cmd)
                elif key == "p":
                    st.config_store.toggle_permissions(highlighted.cmd)
                st.config_store.save()
            return False

        action, st.picker_idx, launched = _handle_picker_key(
            key, st.picker_agents, st.picker_idx
        )
        if action == "launch" and launched is not None:
            sel = _selected_worktree(st.filtered, st.selected_idx)
            if sel:
                store = _get_lease_store()
                if store is not None:
                    holder = store.get_live_or_reap(sel.worktree_id)
                    if holder is not None and launched.cmd != "bash":
                        st.flash_message = (
                            f"Active session on this worktree "
                            f"(pid {holder.pid}). "
                            f"Use 'x' to force-launch or close the other session first."
                        )
                        return False
                live.stop()
                launch_id = ""
                if store is not None:
                    try:
                        result = prepare_agent_launch(store, sel.worktree_id, launched)
                        launch_id = result.launch_id
                    except ActiveWorktreeError:
                        pass
                config_args: list[str] = []
                if st.config_store is not None and launched.cmd != "bash":
                    models = st.config_store.available_models(launched.cmd)
                    config_args = st.config_store.get(launched.cmd).to_args(
                        models=models
                    )
                save_last(sel.worktree_id, launched.key)
                exec_agent(
                    Path(sel.path),
                    launched,
                    launch_id=launch_id,
                    config_args=config_args,
                )
                return True
        elif action == "back":
            st.mode = Mode.LIST
        return False

    # SESSIONS tab: j/k/↑↓ navigate rows; x kills ZOMBIE/STALE process
    if st.mode == Mode.SESSIONS:
        n = len(st.sessions_rows)
        if key in ("j", "down", "k", "up"):
            if n:
                if key in ("j", "down"):
                    st.sessions_idx = (st.sessions_idx + 1) % n
                else:
                    st.sessions_idx = (st.sessions_idx - 1) % n
            return False  # swallow nav keys — never leak to worktree list
        if key == "x" and n and 0 <= st.sessions_idx < n:
            row = st.sessions_rows[st.sessions_idx]
            if row.state == "STALE" and row.pid is not None:
                import signal as _signal

                try:
                    os.kill(row.pid, _signal.SIGTERM)
                    st.flash_message = f"SIGTERM sent to pid {row.pid}"
                except ProcessLookupError:
                    st.flash_message = f"pid {row.pid} already gone"
                except PermissionError:
                    st.flash_message = f"permission denied killing pid {row.pid}"
            elif row.state == "ZOMBIE":
                st.flash_message = "ZOMBIE: process already dead — pointer will be reaped on next session start"
            else:
                st.flash_message = "x only kills STALE sessions (live pid)"
            return False

    # CONFIG tab: j/k/↑↓ navigate agent rows; m/e/p cycle field values
    if st.mode == Mode.CONFIG:
        n = len(st.config_agents)
        if key in ("j", "down", "k", "up"):
            if n:
                if key in ("j", "down"):
                    st.config_idx = (st.config_idx + 1) % n
                else:
                    st.config_idx = (st.config_idx - 1) % n
            return (
                False  # always swallow nav keys in CONFIG — never leak to worktree list
            )
        if key in ("m", "e", "p") and st.config_store is not None and n:
            agent = st.config_agents[st.config_idx] if st.config_idx < n else None
            if agent is not None and agent.cmd != "bash":
                if key == "m":
                    st.config_store.cycle_model(agent.cmd)
                elif key == "e":
                    st.config_store.cycle_effort(agent.cmd)
                elif key == "p":
                    st.config_store.toggle_permissions(agent.cmd)
                st.config_store.save()
            return False

    # 'r' in LIST mode: register an unregistered git worktree
    if st.mode == Mode.LIST and key == "r":
        sel = _selected_worktree(st.filtered, st.selected_idx)
        if sel and sel.status == "unregistered":
            live.stop()
            _register_existing_worktree(sel)
            st.new_worktree_slug = sel.worktree_id  # trigger reload
            st.quit = True
            return True

    # 'x' in LIST mode: delete worktree from disk
    if st.mode == Mode.LIST and key == "x":
        sel = _selected_worktree(st.filtered, st.selected_idx)
        if sel and sel.status == "unregistered":
            live.stop()
            _delete_unregistered_worktree(sel)
            st.new_worktree_slug = ""
            st.quit = True
            return True
        if sel and sel.status not in ("orphan",):
            live.stop()
            _delete_registered_worktree(sel)
            st.new_worktree_slug = ""
            st.quit = True
            return True

    # 'd' in LIST mode: remove an orphan DB entry (registered → flash hint)
    if st.mode == Mode.LIST and key == "d":
        sel = _selected_worktree(st.filtered, st.selected_idx)
        if sel and sel.status == "orphan":
            live.stop()
            _close_orphan_worktree(sel)
            st.new_worktree_slug = ""
            st.quit = True
            return True
        if sel and sel.status not in ("unregistered",):
            st.flash_message = "d removes DB entry for orphans only — use x to delete"
            return False

    # 'n' in LIST mode: interactive new-worktree creation, then restart TUI
    if st.mode == Mode.LIST and key == "n":
        live.stop()
        slug = _new_worktree_interactive()
        st.new_worktree_slug = slug  # None = aborted; str = restart with new id
        st.quit = True
        return True

    # RAISE-15049: 'u' in LIST mode: refresh (reload worktrees + pipeline overview)
    if st.mode == Mode.LIST and key == "u":
        # Signal the outer run_cockpit loop to reload by setting new_worktree_slug=""
        # (empty string = reload without pre-select)
        st.new_worktree_slug = ""
        st.quit = True
        return True

    # 'f' in LIST mode: toggle broken-only filter (RAISE-14929)
    if st.mode == Mode.LIST and key == "f":
        st.broken_only = not st.broken_only
        base, st.selected_idx = _refilter(worktrees, st.filter_query, st.selected_idx)
        health = _apply_health_filter(base, st.broken_only)
        st.filtered = health
        if not health:
            st.selected_idx = 0
        elif st.selected_idx >= len(health):
            st.selected_idx = len(health) - 1
        return False

    # 'p' in LIST mode: repair (re-provision) a registered worktree (RAISE-14930)
    if st.mode == Mode.LIST and key == "p":
        sel = _selected_worktree(st.filtered, st.selected_idx)
        if sel and sel.status not in ("unregistered", "orphan"):
            live.stop()
            _repair_worktree_interactive(sel)
            st.new_worktree_slug = ""  # trigger reload
            st.quit = True
            return True

    if not _apply_nav_key(st, key, viewport_rows=viewport_rows):
        _apply_list_key(st, key, worktrees)
        # AC4: re-apply health filter orthogonally after fuzzy filter changes
        if st.broken_only and st.mode in (Mode.LIST, Mode.FILTER):
            health = _apply_health_filter(st.filtered, broken_only=True)
            st.filtered = health
            if not health:
                st.selected_idx = 0
            elif st.selected_idx >= len(health):
                st.selected_idx = len(health) - 1
    return st.quit


def _run_tui(  # noqa: C901
    worktrees: list[Worktree], prefer_id: str | None = None
) -> str | None:
    """Run the interactive TUI list. Blocks until user quits.

    Args:
        worktrees: Open worktrees to display.
        prefer_id: If set, pre-select this worktree ID on first paint
                   (used after 'n' creates a new worktree and the TUI restarts).

    Returns:
        None on clean quit; a worktree slug string when 'n' created a new
        worktree and the caller should reload + restart.
    """
    console = Console()
    current_path = Path.cwd()
    preview_cache: dict[str, PreviewData] = {}
    last_state = load_last()
    last_key = last_state.agent_key if last_state is not None else None

    # RAISE-15049: Load pipeline overview once per TUI load (zero DB hits per keystroke)
    import raise_cli.cockpit.pipeline_view as _pv_run

    try:
        _pipeline_overview = _pv_run.load_pipeline_overview(worktrees)
    except Exception:  # noqa: BLE001
        _pipeline_overview = _pv_run.PipelineOverview()

    filtered_initial = fuzzy_filter(worktrees, "", key=_worktree_id_key)
    if prefer_id is not None:
        initial_idx = _find_worktree_idx_by_id(filtered_initial, prefer_id)
    else:
        initial_idx = _find_current_worktree_idx(filtered_initial, current_path)
    # Scroll viewport so the pre-selected entry is centered.
    # _layout() is a closure defined below, so compute terminal size inline here.
    try:
        _init_rows = os.get_terminal_size().lines
    except OSError:
        _init_rows = 24
    _init_vp = max(4, _init_rows - 3)
    initial_scroll = max(0, initial_idx - _init_vp // 2)

    st = _LoopState(
        mode=Mode.LIST,
        filter_query="",
        selected_idx=initial_idx,
        scroll_offset=initial_scroll,
        filtered=filtered_initial,
        picker_agents=[],
        picker_idx=0,
        pipeline_overview=_pipeline_overview,
    )

    def _layout() -> tuple[int, int, int]:
        """Return (cols, viewport_rows, col_width) from actual terminal size.

        os.get_terminal_size() queries stdout→stdin→stderr in order, which
        gives the real window size even when a parent process set a different
        COLUMNS env var.  Fallback to 80×24 when called from a non-TTY path.
        """
        try:
            ts = os.get_terminal_size()
            cols, rows = ts.columns, ts.lines
        except OSError:
            cols, rows = 80, 24
        # Reserve 3 rows: 1 header + 1 footer + 1 breathing room
        vp = max(4, rows - 3)
        cw = max(20, cols // 2 - 2)
        return cols, vp, cw

    def _make_frame() -> Group:
        cols, vp, cw = _layout()
        sel = _selected_worktree(st.filtered, st.selected_idx)

        # Refresh sessions rows when in SESSIONS mode
        if st.mode == Mode.SESSIONS:
            try:
                from raise_cli.cockpit.sessions import collect_session_rows

                st.sessions_rows = collect_session_rows(current_path)
            except Exception:  # noqa: BLE001
                st.sessions_rows = []

        # RAISE-15049: pass active leases for DETAIL lease display
        _lease_store = _get_lease_store()
        _active_leases: dict[str, Lease] | None = None
        if _lease_store is not None:
            import contextlib as _contextlib

            with _contextlib.suppress(Exception):
                _active_leases = _lease_store.list_live_or_reap()
        return _render_frame(
            worktrees=worktrees,
            filtered=st.filtered,
            selected_idx=st.selected_idx,
            mode=st.mode,
            filter_query=st.filter_query,
            current_path=current_path,
            preview_data=_get_or_fetch_preview(sel, preview_cache, current_path),
            agents=st.picker_agents if st.mode == Mode.AGENT_PICKER else None,
            picker_idx=st.picker_idx,
            last_key=last_key,
            scroll_offset=st.scroll_offset,
            viewport_rows=vp,
            col_width=cw,
            cols=cols,
            preview_cache=preview_cache,
            broken_only=st.broken_only,
            flash_message=st.flash_message,
            config_store=st.config_store,
            config_agents=st.config_agents,
            config_idx=st.config_idx,
            sessions_rows=st.sessions_rows,
            pipeline_overview=_pipeline_overview,
            detail_run_idx=st.detail_run_idx,
            active_leases=_active_leases,
        )

    if not sys.stdin.isatty():
        console.print(_make_frame())
        return None

    fd = sys.stdin.fileno()
    # Clear screen AND move cursor to (0,0) so Live renders from the top.
    # console.clear() only sends \033[2J (clears screen, cursor stays put);
    # without \033[H the TUI renders below a block of blank rows.
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    with Live(_make_frame(), console=console, auto_refresh=False, screen=False) as live:
        while True:
            _, vp, _ = _layout()
            key = _read_key(fd)
            done = _handle_key(st, key, worktrees, live, vp)
            if done:
                return st.new_worktree_slug  # None = quit; str = restart with new id
            live.update(_make_frame(), refresh=True)
            st.flash_message = None


# ---------------------------------------------------------------------------
# Public entry point + direct-mode helpers
# ---------------------------------------------------------------------------


def _load_worktree_store() -> object:
    """Return a SqliteWorktreeStore for the current working directory.

    Extracted for testability (tests can patch this).

    Returns:
        SqliteWorktreeStore instance.
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore

    return SqliteWorktreeStore(Path.cwd())


def _operation_readiness_report(
    result: ProvisionResult, workspace_path: Path
) -> WorkspaceReadinessReport:
    """Return the operation report without degrading to a lossy snapshot."""
    if result.readiness_report is not None:
        return result.readiness_report
    return WorkspaceReadinessReport(
        workspace_path=workspace_path,
        policy_id="git-worktree-v1",
        findings=[
            WorkspaceReadinessFinding(
                code="provision_result_missing_readiness",
                message="Provisioning returned no operation-scoped readiness report",
                severity="required",
            )
        ],
    )


def _maybe_provision(wt: object) -> None:
    """Ensure the worktree is ready via the shared readiness evaluator + provisioner.

    Warm path (evaluator says ready): prints confirmation and returns immediately.
    Cold path: calls WorktreeProvisioner.provision() in-process, then re-evaluates.
    If the workspace is still not ready after provisioning, prints required findings
    and raises SystemExit(1).

    Replaces the previous `.venv/` proxy check and the broken
    `rai worktree provision` subprocess call (that command does not exist).

    Args:
        wt: A Worktree-like object with `.worktree_id` and `.path` attributes.
    """
    # Use duck-typing access so this works with mocks and real Worktree objects.
    wt_id: str = wt.worktree_id  # type: ignore[attr-defined]
    wt_path = Path(wt.path)  # type: ignore[attr-defined]

    policy = git_worktree_readiness_policy()
    report = evaluate_workspace_readiness(wt_path, policy)

    if report.is_ready:
        print("✓ provisioned  [cached]")
        return

    print(f"◐ provisioning {wt_id}...")
    repo_root = _main_repo_root()
    result = WorktreeProvisioner(wt_path, repo_root).provision()
    report = _operation_readiness_report(result, wt_path)
    if not report.is_ready:
        for finding in report.required_findings:
            print(
                f"✗ not-ready: [{finding.code}] {finding.message}",
                file=sys.stderr,
            )
        print("✗ provisioning did not achieve readiness", file=sys.stderr)
        raise SystemExit(1)

    print("✓ provisioned")


def _repair_worktree_interactive(wt: object) -> None:
    """Repair a worktree by calling WorktreeProvisioner in-process, with confirmation.

    Shows a confirmation prompt before any repair action executes.
    Only calls WorktreeProvisioner.provision() when the user explicitly confirms
    with 'y'.  Any other input (including empty/Enter) cancels without mutation.

    Args:
        wt: A Worktree-like object with `.worktree_id` and `.path` attributes.
    """
    wt_id: str = wt.worktree_id  # type: ignore[attr-defined]
    wt_path = Path(wt.path)  # type: ignore[attr-defined]

    print()
    response = input(f"  Repair worktree '{wt_id}'? [y/N]: ").strip().lower()

    if response != "y":
        print("  Repair cancelled.")
        return

    print(f"  ◐ repairing {wt_id}...")
    repo_root = _main_repo_root()
    result = WorktreeProvisioner(wt_path, repo_root).provision()
    report = _operation_readiness_report(result, wt_path)
    if report.is_ready:
        print(f"  ✓ {wt_id} repaired")
    else:
        for finding in report.required_findings:
            print(
                f"  ✗ not-ready: [{finding.code}] {finding.message}",
                file=sys.stderr,
            )
        print("  ✗ repair did not achieve readiness", file=sys.stderr)

    input("\n  Press Enter to return to cockpit...")


def run_cockpit(
    mission: str | None = None,
    agent: str | None = None,
    use_last: bool = False,
) -> None:
    """Launch the workspace cockpit TUI (or direct mode if flags provided).

    Called by `rai` bare invocation from cli/main.py callback.

    Args:
        mission: Worktree/mission ID for direct mode (--mission flag).
        agent: Agent name for direct mode (--agent flag).
        use_last: If True, reuse the last session (--last flag).
    """
    # --last: load saved combo then fall through to mission+agent resolution
    if use_last:
        last = load_last()
        if last is None:
            print(
                "No last session recorded. Run `rai` to launch the cockpit.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        mission = last.worktree_id
        agent = last.agent_key

    if mission and agent:
        _exec_direct(mission, agent)
        return

    # The interactive cockpit needs raw keypress input, which requires
    # tty/termios (Unix-only).  Direct mode above does not, so this check
    # belongs here rather than at module scope (RAISE-15650).
    if not _raw_input_supported():
        print(
            "The interactive workspace cockpit is not available on this "
            "platform (it needs Unix tty/termios; Windows is not supported "
            "yet).\n"
            "\n"
            "Everything else works — use a subcommand instead:\n"
            "  rai --help       list available commands\n"
            "  rai init         set up RaiSE in this project\n"
            "  rai session start\n"
            "\n"
            "To launch an agent without the cockpit:\n"
            "  rai --mission <worktree-id> --agent <agent>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # TUI mode — loop so 'n'/'r'/'d' can modify state and re-enter the cockpit
    prefer_id: str | None = None
    while True:
        worktrees = _load_all_worktrees()
        result_slug = _run_tui(worktrees, prefer_id=prefer_id)
        if result_slug is None:
            break  # clean quit (esc / q)
        # Non-None result: reload and restart.
        # Empty string = reload without pre-select (e.g. orphan closed).
        # Non-empty string = pre-select the new/registered worktree.
        prefer_id = result_slug if result_slug else None


def _exec_direct(mission: str, agent_key: str) -> None:
    """Resolve mission+agent and exec without TUI.

    Args:
        mission: Worktree ID string.
        agent_key: Single-char agent key ("c", "o", "h", "s") or command name.
    """
    from raise_cli.storage.worktrees import WorktreeNotFoundError

    store = _load_worktree_store()

    try:
        wt = store.get_by_name(mission)  # type: ignore[attr-defined]
    except WorktreeNotFoundError:
        print(f"Worktree '{mission}' not found.", file=sys.stderr)
        raise SystemExit(1) from None

    agents = detect_agents(Path(wt.path))  # type: ignore[attr-defined]
    matched = next(
        (a for a in agents if agent_key in (a.key, a.cmd)),
        None,
    )
    if matched is None:
        print(f"Agent '{agent_key}' not found for this worktree.", file=sys.stderr)
        raise SystemExit(1)

    if matched.cmd != "bash":
        lease_store = _get_lease_store()
        if lease_store is not None:
            holder = lease_store.get_live_or_reap(wt.worktree_id)  # type: ignore[attr-defined]
            if holder is not None:
                print(
                    f"Worktree '{mission}' has an active session "
                    f"(pid {holder.pid}). Close it first or use shell.",
                    file=sys.stderr,
                )
                raise SystemExit(1)

    _maybe_provision(wt)
    save_last(wt.worktree_id, matched.key)  # type: ignore[attr-defined]
    exec_agent(Path(wt.path), matched)  # type: ignore[attr-defined]
