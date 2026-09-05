"""Cockpit pipeline overview column and DETAIL view (RAISE-15049).

Implements §1 of cockpit-synthesized-design.md:

- PipelineOverview dataclass: snapshot loaded once per TUI load
- load_pipeline_overview(worktrees): reads pipeline_runs read-only,
  joins runs to worktrees via start_cwd/locked_worktree resolution
- pipeline_cell(runs, lease, now): pure function → Rich Text glyph per §1.3
- render_detail_panel: DETAIL view content per §1.5
- METADATA_VERSION check: v0=legacy, v1=has journal/gate keys
"""

from __future__ import annotations

import contextlib
import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.style import Style
from rich.text import Text

from raise_cli.storage.leases import pid_alive
from raise_core.workflow.status_sets import (
    PAUSED_STATUSES,
    TERMINAL_STATUSES,
)

if TYPE_CHECKING:
    from raise_cli.storage.leases import Lease
    from raise_cli.storage.worktrees import Worktree

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STALE_AFTER: timedelta = timedelta(hours=2)
LEASE_TTL: timedelta = timedelta(minutes=30)

# Pipeline metadata version constant — must match mcp_tools_pipeline.METADATA_VERSION
_METADATA_V1 = 1


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class PipelineOverview:
    """Snapshot of pipeline run state for all worktrees.

    Loaded once per TUI load. Zero DB hits per keystroke; refresh via 'u'.
    """

    runs_by_worktree: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    """worktree_id → list of runs, ordered started_at DESC."""

    unattached_count: int = 0
    """Runs whose cwd/locked_worktree doesn't match any known worktree."""

    loaded_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_current_phase(run: dict[str, Any]) -> str | None:
    """Return the current phase ID from a run dict, or None."""
    phases: list[dict[str, Any]] = run.get("phases", [])
    idx: int = run.get("current_phase_index", 0)
    if phases and 0 <= idx < len(phases):
        return phases[idx].get("id")
    return None


def _last_activity(run: dict[str, Any]) -> datetime | None:
    """Return the latest write timestamp extractable from a run.

    Checks (in order):
    1. awaiting_gate.at (most recent gate stamp)
    2. last hitl_decisions entry's at
    3. started_at

    Sol S6: use per-run timestamps only, NOT lease.heartbeat_at.
    """
    meta: dict[str, Any] = run.get("metadata", {})

    candidates: list[str | None] = []

    # 1. Gate stamp
    gate = meta.get("awaiting_gate", {})
    if isinstance(gate, dict):
        candidates.append(gate.get("at"))

    # 2. Last decision
    decisions: list[dict[str, Any]] = meta.get("hitl_decisions", [])
    if decisions:
        candidates.append(decisions[-1].get("at"))

    # 3. Phase started_at (most recent phase)
    phases: list[dict[str, Any]] = run.get("phases", [])
    idx = run.get("current_phase_index", 0)
    if phases and 0 <= idx < len(phases):
        candidates.append(phases[idx].get("started_at"))

    # 4. Run started_at as final fallback
    candidates.append(run.get("started_at"))

    best: datetime | None = None
    for ts in candidates:
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            if best is None or dt > best:
                best = dt
        except (ValueError, TypeError):
            continue
    return best


def _fmt_age(dt: datetime | None, now: datetime) -> str:
    """Return a compact human-readable age string (e.g. '2h ago')."""
    if dt is None:
        return "?"
    delta = now - dt
    total_s = int(delta.total_seconds())
    if total_s < 0:
        return "just now"
    if total_s < 60:
        return "just now"
    if total_s < 3600:
        return f"{total_s // 60}m ago"
    if total_s < 86400:
        return f"{total_s // 3600}h ago"
    days = total_s // 86400
    if days < 7:
        return f"{days}d ago"
    return f"{days // 7}w ago"


# ---------------------------------------------------------------------------
# Core pure function: pipeline_cell
# ---------------------------------------------------------------------------


def pipeline_cell(  # noqa: C901
    runs: list[dict[str, Any]],
    lease: Lease | None,
    now: datetime,
) -> Text:
    """Compute the pipeline status cell glyph for a worktree.

    Pure function — no I/O, injected clock. Follows §1.3 of synthesized design.

    Args:
        runs: Runs for this worktree, ordered started_at DESC. May be empty.
        lease: Active worktree lease, or None when no session holds it.
        now: Current datetime (UTC, tz-aware) for age calculations.

    Returns:
        Rich Text with a colored status glyph.
    """
    # Find newest non-terminal run (active candidate)
    active: dict[str, Any] | None = None
    for r in runs:
        if r.get("status") not in TERMINAL_STATUSES:
            active = r
            break

    if active is None:
        # Sol W1: check for failed runs before returning blank
        for r in runs:
            if r.get("status") == "failed":
                return Text("✗ failed", style=Style(color="#F85149"))
        return Text("")

    phase = _get_current_phase(active) or "?"
    last_act = _last_activity(active)
    age = (now - last_act) if last_act else timedelta(0)

    # 1. Explicit pause (status-level)
    if active.get("status") in PAUSED_STATUSES:
        return Text(f"⏸ {phase} (paused)", style=Style(color="#D29922"))

    # 2. Awaiting gate — Sol S7: phase-match predicate
    meta: dict[str, Any] = active.get("metadata", {})
    gate = meta.get("awaiting_gate", {})
    if isinstance(gate, dict) and gate:
        gate_phase = gate.get("phase")
        if gate_phase and gate_phase == phase:
            return Text(f"⏸ {phase} (gate)", style=Style(color="#D29922"))

    # 3. Dead PID → definite orphan
    if lease is not None and not pid_alive(lease.pid):
        age_str = _fmt_age(last_act, now)
        return Text(f"⚠ {phase} · {age_str}", style=Style(color="#D29922"))

    # 4. Stale (no write for >= 2h)
    if age >= STALE_AFTER:
        age_str = _fmt_age(last_act, now)
        return Text(f"⚠ {phase} · {age_str}", style=Style(color="#D29922"))

    # 5. Active — show age if >= LEASE_TTL
    if age >= LEASE_TTL:
        age_str = _fmt_age(last_act, now)
        return Text(f"▶ {phase} · {age_str}", style=Style(color="#3FB950"))

    return Text(f"▶ {phase}", style=Style(color="#3FB950"))


# ---------------------------------------------------------------------------
# Run store read-only access
# ---------------------------------------------------------------------------


def _get_db_path() -> Path:
    """Return the path to the global raise.db."""
    from raise_cli.config.paths import get_global_rai_dir

    return get_global_rai_dir() / "raise.db"


@contextmanager
def _open_run_store_ro() -> Generator[sqlite3.Connection | None, None, None]:
    """Open the pipeline_runs DB in read-only mode for the cockpit loader.

    Uses SQLite URI mode (?mode=ro) so no DDL/migrations can fire.
    Falls back gracefully when the DB doesn't exist yet.

    Yields:
        sqlite3.Connection in read-only mode, or None when DB is unavailable.
    """
    db_path = _get_db_path()
    if not db_path.exists():
        yield None
        return

    uri = f"file:{db_path}?mode=ro"
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.OperationalError:
        # DB locked or unavailable — cockpit degrades gracefully
        yield None
    finally:
        if conn is not None:
            with contextlib.suppress(Exception):
                conn.close()


def _query_all_runs(
    conn: sqlite3.Connection,
    project_id: str,
) -> list[dict[str, Any]]:
    """Query all runs for this project, newest first.

    Args:
        conn: Read-only SQLite connection.
        project_id: Project discriminator from get_project_id().

    Returns:
        List of run dicts with parsed phases/metadata.
    """
    try:
        rows = conn.execute(
            "SELECT run_id, pipeline_name, issue_id, current_phase_index, "
            "status, phases, started_at, completed_at, metadata "
            "FROM pipeline_runs "
            "WHERE project_id = ? "
            "ORDER BY started_at DESC",
            (project_id,),
        ).fetchall()
    except sqlite3.OperationalError:
        # Table may not exist in very early setups
        return []

    result: list[dict[str, Any]] = []
    for row in rows:
        d = dict(row)
        d["phases"] = json.loads(d.get("phases") or "[]") or []
        d["metadata"] = json.loads(d.get("metadata") or "{}") or {}
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# Overview loader
# ---------------------------------------------------------------------------


def load_pipeline_overview(worktrees: list[Worktree]) -> PipelineOverview:
    """Load pipeline run snapshot for all worktrees.

    Opens the global raise.db in read-only mode. Joins runs to worktrees
    via resolved(start_cwd or locked_worktree) == resolved(worktree.path).
    Falls back gracefully if the DB is unavailable.

    Args:
        worktrees: List of worktrees from _load_all_worktrees().

    Returns:
        PipelineOverview snapshot with runs grouped by worktree_id.
    """
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_id

    overview = PipelineOverview()

    # Pre-populate all worktrees with empty run lists
    wt_by_resolved: dict[Path, str] = {}
    for wt in worktrees:
        overview.runs_by_worktree[wt.worktree_id] = []
        with contextlib.suppress(Exception):
            resolved = Path(wt.path).resolve()
            wt_by_resolved[resolved] = wt.worktree_id

    try:
        root = resolve_checkout_root()
        project_id = get_project_id(root)
    except Exception:  # noqa: BLE001
        return overview

    with _open_run_store_ro() as conn:
        if conn is None:
            return overview

        runs = _query_all_runs(conn, project_id)

    for run in runs:
        meta: dict[str, Any] = run.get("metadata", {})
        run_cwd = meta.get("start_cwd") or meta.get("locked_worktree") or ""

        matched_id: str | None = None
        if run_cwd:
            with contextlib.suppress(Exception):
                resolved_cwd = Path(run_cwd).resolve()
                matched_id = wt_by_resolved.get(resolved_cwd)

        if matched_id is not None:
            overview.runs_by_worktree[matched_id].append(run)
        else:
            overview.unattached_count += 1

    return overview


# ---------------------------------------------------------------------------
# DETAIL view renderer
# ---------------------------------------------------------------------------

_BLUE = "#58A6FF"
_GREEN = "#3FB950"
_AMBER = "#D29922"
_RED = "#F85149"
_PURPLE = "#BC8CFF"
_TEXT_BRIGHT = "#F0F6FC"
_TEXT = "#C9D1D9"
_TEXT_DIM = "#8B949E"


def _run_glyph(run: dict[str, Any], now: datetime) -> tuple[str, str]:
    """Return (glyph, style_color) for a run in the DETAIL run list."""
    status = run.get("status", "")
    if status in TERMINAL_STATUSES:
        if status == "failed":
            return "✗", _RED
        if status in ("cancelled", "canceled"):
            return "✗", _TEXT_DIM
        return "✓", _GREEN
    if status in PAUSED_STATUSES:
        return "⏸", _AMBER

    last_act = _last_activity(run)
    age = (now - last_act) if last_act else timedelta(0)

    if age >= STALE_AFTER:
        return "⚠", _AMBER
    return "▶", _GREEN


def render_detail_panel(  # noqa: C901
    worktree: Worktree,
    runs: list[dict[str, Any]],
    lease: Lease | None,
    now: datetime,
    selected_run_idx: int = 0,
    col_width: int = 60,
) -> Text:
    """Render the full DETAIL panel for a worktree's pipeline state.

    Follows §1.5 of cockpit-synthesized-design.md.

    Args:
        worktree: The worktree being inspected.
        runs: All runs for this worktree, newest first.
        lease: Active lease or None.
        now: Current UTC datetime.
        selected_run_idx: Index of selected run (j/k navigation).
        col_width: Max character width per line.

    Returns:
        Rich Text renderable for the DETAIL panel.
    """
    # Clamp index so j-navigation never hides the cursor past the last run (R1).
    if runs:
        selected_run_idx = min(selected_run_idx, len(runs) - 1)

    panel = Text()

    # --- Header ---
    issue_ids = sorted({r.get("issue_id", "") for r in runs if r.get("issue_id")})
    issue_hint = issue_ids[0] if issue_ids else "—"
    branch = worktree.branch or "—"
    header = f" {worktree.worktree_id} · {issue_hint} · {branch}"
    if len(header) > col_width:
        header = header[: col_width - 1] + "…"
    panel.append(header + "\n", style=Style(color=_TEXT_BRIGHT, bold=True))
    panel.append(
        " " + "─" * min(col_width - 2, 60) + "\n", style=Style(color=_TEXT_DIM)
    )

    # --- Runs section ---
    panel.append(" Runs\n", style=Style(color=_TEXT, bold=True))

    if not runs:
        panel.append("   (no pipeline runs)\n", style=Style(color=_TEXT_DIM))
    else:
        for i, run in enumerate(runs):
            selected = i == selected_run_idx
            cursor = "›" if selected else " "
            glyph, glyph_color = _run_glyph(run, now)

            pipeline_name = run.get("pipeline_name", "?")
            issue_id = run.get("issue_id", "?")
            phase = _get_current_phase(run) or run.get("status", "?")
            phases = run.get("phases", [])
            n_phases = len(phases)
            idx = run.get("current_phase_index", 0)
            phase_counter = f"({idx + 1}/{n_phases})" if n_phases > 1 else ""

            last_act = _last_activity(run)
            age_str = _fmt_age(last_act, now)

            row = Text()
            row.append(
                f" {cursor} ",
                style=Style(color=_BLUE, bold=True)
                if selected
                else Style(color=_TEXT_DIM),
            )
            row.append(glyph + " ", style=Style(color=glyph_color, bold=True))
            row.append(f"{pipeline_name:<8}", style=Style(color=_TEXT))
            row.append(f"  {issue_id:<14}", style=Style(color=_BLUE))
            row.append(
                f"  {phase}", style=Style(color=_TEXT_BRIGHT if selected else _TEXT)
            )
            if phase_counter:
                row.append(f" {phase_counter}", style=Style(color=_TEXT_DIM))
            row.append(f"   {age_str}", style=Style(color=_TEXT_DIM))

            # Hard truncate
            plain = row.plain
            if len(plain) > col_width:
                row.truncate(col_width - 1, overflow="ellipsis")

            panel.append_text(row)
            panel.append("\n")

    panel.append("\n")

    # --- Decisions section (for selected run) ---
    selected_run: dict[str, Any] | None = (
        runs[selected_run_idx] if runs and 0 <= selected_run_idx < len(runs) else None
    )
    if selected_run is not None:
        sel_issue = selected_run.get("issue_id", "?")
        panel.append(f" Decisions ({sel_issue})\n", style=Style(color=_TEXT, bold=True))

        meta = selected_run.get("metadata", {})
        meta_v = meta.get("_v", 0)
        decisions: list[dict[str, Any]] = meta.get("hitl_decisions", [])

        if meta_v < _METADATA_V1 or not decisions:
            panel.append("   (no decisions recorded)\n", style=Style(color=_TEXT_DIM))
        else:
            for dec in decisions:
                phase_label = dec.get("phase", "?")
                decision_text = dec.get("decision", "?")
                source = dec.get("source", "?")
                at = dec.get("at", "")
                age_str = ""
                if at:
                    try:
                        dt = datetime.fromisoformat(at)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=UTC)
                        age_str = _fmt_age(dt, now)
                    except (ValueError, TypeError):
                        pass

                # Truncate decision text
                max_dec = max(20, col_width - 40)
                if len(decision_text) > max_dec:
                    decision_text = decision_text[: max_dec - 1] + "…"

                dec_line = Text()
                dec_line.append("   • ", style=Style(color=_TEXT_DIM))
                dec_line.append(f"{phase_label:<10}", style=Style(color=_BLUE))
                dec_line.append(f'  "{decision_text}"', style=Style(color=_TEXT))
                dec_line.append(f"  ({source}", style=Style(color=_TEXT_DIM))
                if age_str:
                    dec_line.append(f", {age_str}", style=Style(color=_TEXT_DIM))
                dec_line.append(")", style=Style(color=_TEXT_DIM))

                plain = dec_line.plain
                if len(plain) > col_width:
                    dec_line.truncate(col_width - 1, overflow="ellipsis")

                panel.append_text(dec_line)
                panel.append("\n")

        panel.append("\n")

    # --- Lease section ---
    panel.append(" Lease: ", style=Style(color=_TEXT, bold=True))
    if lease is None:
        panel.append("(no active lease)\n", style=Style(color=_TEXT_DIM))
    else:
        alive = pid_alive(lease.pid)
        pid_status = "alive" if alive else "dead"
        pid_color = _GREEN if alive else _RED

        hb_str = ""
        try:
            hb_dt = datetime.fromisoformat(lease.heartbeat_at)
            if hb_dt.tzinfo is None:
                hb_dt = hb_dt.replace(tzinfo=UTC)
            hb_age = _fmt_age(hb_dt, now)
            expired = (now - hb_dt) > STALE_AFTER
            hb_str = f"{hb_age} ({'expired' if expired else 'ok'})"
        except (ValueError, TypeError):
            hb_str = "?"

        sess_short = (
            lease.session_id[:8] + "…"
            if len(lease.session_id) > 8
            else lease.session_id
        )

        lease_line = Text()
        lease_line.append(f"session {sess_short} · ", style=Style(color=_TEXT_DIM))
        lease_line.append(f"pid {lease.pid}", style=Style(color=_TEXT))
        lease_line.append(f" ({pid_status})", style=Style(color=pid_color))
        lease_line.append(f" · heartbeat {hb_str}\n", style=Style(color=_TEXT_DIM))
        panel.append_text(lease_line)

    panel.append("\n")

    # --- Keymap ---
    run_id_hint = ""
    if selected_run is not None:
        run_id_hint = selected_run.get("run_id", "")

    panel.append(
        " [r] resume   [j/k] select run   [esc] back\n", style=Style(color=_TEXT_DIM)
    )
    if run_id_hint:
        panel.append(
            f" cancel: rai pipeline cancel {run_id_hint}\n",
            style=Style(color=_TEXT_DIM, dim=True),
        )

    # --- Unattached footer --- (shown on LIST view footer, not DETAIL)
    return panel


def render_unattached_footer(unattached_count: int) -> str:
    """Return the unattached-runs footer string for the LIST view.

    Args:
        unattached_count: Number of runs not joined to any known worktree.

    Returns:
        Footer string. Always non-empty; includes unattached count only when > 0.
    """
    if unattached_count == 0:
        return "Showing local runs only. Use 'rai pipeline runs --all' for server-side."
    return (
        f"Showing local runs only. {unattached_count} unattached run(s). "
        "Use 'rai pipeline runs --all' for server-side."
    )
