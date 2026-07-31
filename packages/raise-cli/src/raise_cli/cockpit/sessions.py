"""Sessions tab data model and renderer for the cockpit TUI (RAISE-15131 S7).

Provides:
- SessionRow: frozen dataclass representing one row in the Sessions tab.
- collect_session_rows(): join leases + session pointers by worktree_id,
  classify state (LIVE / STALE / ZOMBIE / DETACHED).
- _render_sessions_panel(): Rich Text renderer for the Sessions tab panel.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from rich.style import Style
from rich.text import Text

from raise_cli.session.index import read_all_active_sessions
from raise_cli.storage.leases import Lease, SqliteLeaseStore

__all__ = ["SessionRow", "collect_session_rows", "_render_sessions_panel"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STALE_H: float = 2.0  # heartbeat age (hours) that crosses LIVE → STALE
ZOMBIE_H: float = 2.0  # session age (hours) that crosses DETACHED → ZOMBIE

STATE_ORDER: dict[str, int] = {
    "LIVE": 0,
    "STALE": 1,
    "DETACHED": 2,
    "ZOMBIE": 3,
}

# ---------------------------------------------------------------------------
# Design tokens (aligned with app.py)
# ---------------------------------------------------------------------------
_BLUE = "#58A6FF"
_GREEN = "#3FB950"
_AMBER = "#D29922"
_RED = "#F85149"
_PURPLE = "#BC8CFF"
_TEXT_BRIGHT = "#F0F6FC"
_TEXT = "#C9D1D9"
_TEXT_DIM = "#8B949E"

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SessionRow:
    """One row in the Sessions tab.

    session_id: RaiSE session ID ("S-E-…") — empty for lease-only rows.
    name: Human-readable session name or "(sin session start)".
    worktree_id: Worktree ID from active_sessions — empty for main-checkout.
    started: Session start time (None for lease-only rows).
    age_hours: Hours since started / lease acquired_at.
    state: LIVE | STALE | ZOMBIE | DETACHED
    pid: Process ID from the lease (None if no live lease).
    heartbeat_age_h: Hours since last heartbeat (None if no lease).
    join: Confidence of the pointer↔lease join.
        "exact"    — session_id matches exactly.
        "worktree" — joined by worktree_id only (IDs differ).
        "none"     — no lease (ZOMBIE/DETACHED).
    """

    session_id: str
    name: str
    worktree_id: str
    started: datetime | None
    age_hours: float
    state: Literal["LIVE", "STALE", "ZOMBIE", "DETACHED"]
    pid: int | None
    heartbeat_age_h: float | None
    join: Literal["exact", "worktree", "none"]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _hours(delta_seconds: float) -> float:
    return delta_seconds / 3600.0


def _fromiso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _age_h(now: datetime, dt: datetime) -> float:
    """Return hours between now and dt, normalising dt to UTC when naive."""
    aware = dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
    return _hours((now - aware).total_seconds())


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def collect_session_rows(project_root: Path) -> list[SessionRow]:
    """Join leases + session pointers by worktree_id, classify state.

    Args:
        project_root: Project root directory (used to scope both the pointer
            table lookup and the lease store).

    Returns:
        Sorted list of SessionRow — LIVE first, ZOMBIE last; newest first
        within each state.
    """
    pointers = read_all_active_sessions(project_root=project_root)
    store = SqliteLeaseStore(project_root)
    leases: Mapping[str, Lease] = store.list_live_or_reap()

    now = datetime.now(UTC)
    rows: list[SessionRow] = []
    claimed: set[str] = set()

    for p in pointers:
        lease: Lease | None = leases.get(p.worktree_id) if p.worktree_id else None
        age_h = _age_h(now, p.started)

        if lease is not None:
            claimed.add(p.worktree_id)
            hb_age_h = _hours((now - _fromiso(lease.heartbeat_at)).total_seconds())
            state: Literal["LIVE", "STALE", "ZOMBIE", "DETACHED"] = (
                "LIVE" if hb_age_h <= STALE_H else "STALE"
            )
            join: Literal["exact", "worktree", "none"] = (
                "exact" if lease.session_id == p.cc_session_id else "worktree"
            )
            rows.append(
                SessionRow(
                    session_id=p.id,
                    name=p.name or "(sin nombre)",
                    worktree_id=p.worktree_id,
                    started=p.started,
                    age_hours=age_h,
                    state=state,
                    pid=lease.pid,
                    heartbeat_age_h=hb_age_h,
                    join=join,
                )
            )
        elif p.worktree_id:
            # Has worktree but no live lease → ZOMBIE
            rows.append(
                SessionRow(
                    session_id=p.id,
                    name=p.name or "(sin nombre)",
                    worktree_id=p.worktree_id,
                    started=p.started,
                    age_hours=age_h,
                    state="ZOMBIE",
                    pid=None,
                    heartbeat_age_h=None,
                    join="none",
                )
            )
        else:
            # No worktree — main checkout or unregistered
            det_state: Literal["LIVE", "STALE", "ZOMBIE", "DETACHED"] = (
                "DETACHED" if age_h <= ZOMBIE_H else "ZOMBIE"
            )
            rows.append(
                SessionRow(
                    session_id=p.id,
                    name=p.name or "(sin nombre)",
                    worktree_id="",
                    started=p.started,
                    age_hours=age_h,
                    state=det_state,
                    pid=None,
                    heartbeat_age_h=None,
                    join="none",
                )
            )

    # Lease-only rows: process launched by cockpit that never ran session start
    for wt_id, lease in leases.items():
        if wt_id in claimed:
            continue
        hb_age_h = _hours((now - _fromiso(lease.heartbeat_at)).total_seconds())
        lo_age_h = _hours((now - _fromiso(lease.acquired_at)).total_seconds())
        lo_state: Literal["LIVE", "STALE", "ZOMBIE", "DETACHED"] = (
            "LIVE" if hb_age_h <= STALE_H else "STALE"
        )
        rows.append(
            SessionRow(
                session_id="",
                name="(sin session start)",
                worktree_id=wt_id,
                started=None,
                age_hours=lo_age_h,
                state=lo_state,
                pid=lease.pid,
                heartbeat_age_h=hb_age_h,
                join="none",
            )
        )

    return sorted(rows, key=lambda r: (STATE_ORDER[r.state], -r.age_hours))


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def _render_sessions_panel(rows: list[SessionRow]) -> Text:
    """Render the Sessions tab panel as a Rich Text block.

    Args:
        rows: List of SessionRow to display (pre-sorted by collect_session_rows).

    Returns:
        Rich Text renderable for the Sessions tab body.
    """
    panel = Text()
    panel.append("┌─ sessions ", style=Style(color=_PURPLE, bold=True))
    panel.append("─" * 40, style=Style(color=_TEXT_DIM))
    panel.append("┐\n", style=Style(color=_TEXT_DIM))

    if not rows:
        panel.append("│  ", style=Style(color=_TEXT_DIM))
        panel.append("no active sessions", style=Style(color=_TEXT_DIM, italic=True))
        panel.append("\n│\n", style=Style(color=_TEXT_DIM))
    else:
        # Column headers
        panel.append("│  ", style=Style(color=_TEXT_DIM))
        panel.append(f"{'worktree':<20}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append(f"{'agent/session':<18}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append(f"{'age':>6}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append("  ", style=Style(color=_TEXT_DIM))
        panel.append(f"{'state':<8}", style=Style(color=_TEXT_DIM, bold=True))
        panel.append("\n│  ", style=Style(color=_TEXT_DIM))
        panel.append("─" * 55, style=Style(color=_TEXT_DIM))
        panel.append("\n", style=Style(color=_TEXT_DIM))

        for row in rows:
            state_color = {
                "LIVE": _GREEN,
                "STALE": _AMBER,
                "ZOMBIE": _RED,
                "DETACHED": _TEXT_DIM,
            }.get(row.state, _TEXT_DIM)

            # worktree column (20 chars)
            wt_label = row.worktree_id if row.worktree_id else "(main)"
            wt_label = wt_label[:19]

            # agent/session column (18 chars)
            name_label = row.name[:17]

            # age column (6 chars)
            if row.age_hours < 1.0:
                age_str = f"{int(row.age_hours * 60)}m"
            else:
                age_str = f"{row.age_hours:.1f}h"

            panel.append("│  ", style=Style(color=_TEXT_DIM))
            panel.append(f"{wt_label:<20}", style=Style(color=state_color))
            panel.append(f"{name_label:<18}", style=Style(color=_TEXT))
            panel.append(f"{age_str:>6}", style=Style(color=_TEXT_DIM))
            panel.append("  ", style=Style(color=_TEXT_DIM))
            panel.append(f"{row.state:<8}", style=Style(color=state_color, bold=True))
            panel.append("\n", style=Style(color=_TEXT_DIM))

    panel.append("│\n│  ", style=Style(color=_TEXT_DIM))
    panel.append("x", style=Style(color=_BLUE, bold=True))
    panel.append(" kill zombie  ", style=Style(color=_TEXT_DIM))
    panel.append("↑↓", style=Style(color=_BLUE, bold=True))
    panel.append(" select\n", style=Style(color=_TEXT_DIM))
    panel.append("└", style=Style(color=_TEXT_DIM))
    panel.append("─" * 51, style=Style(color=_TEXT_DIM))
    panel.append("┘\n", style=Style(color=_TEXT_DIM))
    return panel
