"""Sessions tab data model and renderer for the cockpit TUI (RAISE-15131 S7).

Provides:
- SessionRow: frozen dataclass representing one row in the Sessions tab.
- collect_session_rows(): join leases + session pointers by worktree_id,
  classify state (LIVE / STALE / ZOMBIE / DETACHED).
- _render_sessions_panel(): Rich Text renderer for the Sessions tab panel.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from rich.style import Style
from rich.text import Text

from raise_cli.cockpit.tokens import (
    AMBER,
    BLUE,
    GREEN,
    PURPLE,
    RED,
    TEXT,
    TEXT_DIM,
)
from raise_cli.session.index import read_all_active_sessions
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.leases import Lease, SqliteLeaseStore
from raise_cli.storage.pause_states import SqlitePauseStore
from raise_cli.storage.worktrees import Worktree

__all__ = ["SessionRow", "collect_session_rows", "_render_sessions_panel"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STALE_H: float = 2.0  # heartbeat age (hours) that crosses LIVE → STALE
ZOMBIE_H: float = 2.0  # session age (hours) that crosses DETACHED → ZOMBIE
ZOMBIE_REAP_H: float = 24.0  # RAISE-16785: auto-delete zombie pointers older than this

STATE_ORDER: dict[str, int] = {
    "LIVE": 0,
    "STALE": 1,
    "DETACHED": 2,
    "ZOMBIE": 3,
}

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
    worktree: Registered/unregistered/orphan Worktree this row belongs to
        (RAISE-16824, S6) — None for session rows with no matching worktree
        (main checkout, stale pointer). Additive/defaulted so every existing
        construction site keeps compiling unchanged.
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
    paused: bool = False
    worktree: Worktree | None = None

    @property
    def rail_key(self) -> str:
        """Rail selection identity (RAISE-16824, D-S6.5): worktree_id, else session_id.

        Fixes the pre-existing session_id=="" collision across lease-only/
        IDLE rows that would otherwise all share the same identity.
        """
        return self.worktree_id or self.session_id


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
    paused_worktrees: set[str] = SqlitePauseStore(project_root).list_paused()

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

    if paused_worktrees:
        rows = [
            replace(r, paused=True) if r.worktree_id in paused_worktrees else r
            for r in rows
        ]

    # RAISE-16785: auto-reap zombie pointers older than ZOMBIE_REAP_H.
    # Prevents indefinite accumulation of orphaned active_sessions rows
    # from crashed/abandoned sessions whose leases were already reaped.
    zombie_ids = [
        r.session_id
        for r in rows
        if r.state == "ZOMBIE" and r.age_hours > ZOMBIE_REAP_H and r.session_id
    ]
    if zombie_ids:
        try:
            conn = get_project_db(project_root)
            pid = get_project_id(project_root)
            placeholders = ",".join("?" for _ in zombie_ids)
            conn.execute(
                f"DELETE FROM active_sessions "  # noqa: S608
                f"WHERE project_id = ? AND session_id IN ({placeholders})",
                [pid, *zombie_ids],
            )
            conn.commit()
        except Exception:  # noqa: BLE001, S110
            pass
        rows = [r for r in rows if r.session_id not in set(zombie_ids)]

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
    panel.append("┌─ sessions ", style=Style(color=PURPLE, bold=True))
    panel.append("─" * 40, style=Style(color=TEXT_DIM))
    panel.append("┐\n", style=Style(color=TEXT_DIM))

    if not rows:
        panel.append("│  ", style=Style(color=TEXT_DIM))
        panel.append("no active sessions", style=Style(color=TEXT_DIM, italic=True))
        panel.append("\n│\n", style=Style(color=TEXT_DIM))
    else:
        # Column headers
        panel.append("│  ", style=Style(color=TEXT_DIM))
        panel.append(f"{'worktree':<20}", style=Style(color=TEXT_DIM, bold=True))
        panel.append(f"{'agent/session':<18}", style=Style(color=TEXT_DIM, bold=True))
        panel.append(f"{'age':>6}", style=Style(color=TEXT_DIM, bold=True))
        panel.append("  ", style=Style(color=TEXT_DIM))
        panel.append(f"{'state':<8}", style=Style(color=TEXT_DIM, bold=True))
        panel.append("\n│  ", style=Style(color=TEXT_DIM))
        panel.append("─" * 55, style=Style(color=TEXT_DIM))
        panel.append("\n", style=Style(color=TEXT_DIM))

        for row in rows:
            state_color = {
                "LIVE": GREEN,
                "STALE": AMBER,
                "ZOMBIE": RED,
                "DETACHED": TEXT_DIM,
            }.get(row.state, TEXT_DIM)

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

            panel.append("│  ", style=Style(color=TEXT_DIM))
            panel.append(f"{wt_label:<20}", style=Style(color=state_color))
            panel.append(f"{name_label:<18}", style=Style(color=TEXT))
            panel.append(f"{age_str:>6}", style=Style(color=TEXT_DIM))
            panel.append("  ", style=Style(color=TEXT_DIM))
            panel.append(f"{row.state:<8}", style=Style(color=state_color, bold=True))
            panel.append("\n", style=Style(color=TEXT_DIM))

    panel.append("│\n│  ", style=Style(color=TEXT_DIM))
    panel.append("x", style=Style(color=BLUE, bold=True))
    panel.append(" kill zombie  ", style=Style(color=TEXT_DIM))
    panel.append("↑↓", style=Style(color=BLUE, bold=True))
    panel.append(" select\n", style=Style(color=TEXT_DIM))
    panel.append("└", style=Style(color=TEXT_DIM))
    panel.append("─" * 51, style=Style(color=TEXT_DIM))
    panel.append("┘\n", style=Style(color=TEXT_DIM))
    return panel
