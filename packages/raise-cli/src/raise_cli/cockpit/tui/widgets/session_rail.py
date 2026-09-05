"""Session Rail widget — list of sessions with V2 state glyphs."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from rich.markup import escape
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Static

from raise_cli.cockpit.tokens import (
    GLYPH_BLOCKED,
    GLYPH_DONE,
    GLYPH_ERROR,
    GLYPH_IDLE,
    GLYPH_PAUSED,
    GLYPH_WORKING,
)
from raise_cli.cockpit.tui.services import classify_row
from raise_cli.cockpit.tui.theme import (
    MARKUP_BLOCKED,
    MARKUP_COPPER,
    MARKUP_DONE,
    MARKUP_ERROR,
    MARKUP_IDLE,
    MARKUP_MUTED,
    MARKUP_PAUSED,
    MARKUP_SELECTION_WASH,
    MARKUP_WORKING,
)
from raise_cli.cockpit.types import SessionState

if TYPE_CHECKING:
    from raise_cli.cockpit.sessions import SessionRow
    from raise_cli.storage.worktrees import Worktree


def _use_unicode() -> bool:
    """Mirror tokens._use_unicode() locally (that helper is module-private)."""
    if os.environ.get("RAI_ASCII", "") == "1":
        return False
    try:
        return sys.stdout.encoding.lower().startswith("utf")
    except (AttributeError, LookupError):
        return False


_SELECTED_GLYPH: str = "▸" if _use_unicode() else ">"

_STATE_GLYPHS: dict[SessionState, str] = {
    SessionState.WORKING: GLYPH_WORKING,
    SessionState.PAUSED: GLYPH_PAUSED,
    SessionState.BLOCKED: GLYPH_BLOCKED,
    SessionState.DONE: GLYPH_DONE,
    SessionState.ERROR: GLYPH_ERROR,
    SessionState.IDLE: GLYPH_IDLE,
}

_STATE_COLORS: dict[SessionState, str] = {
    SessionState.WORKING: MARKUP_WORKING,
    SessionState.PAUSED: MARKUP_PAUSED,
    SessionState.BLOCKED: MARKUP_BLOCKED,
    SessionState.DONE: MARKUP_DONE,
    SessionState.ERROR: MARKUP_ERROR,
    SessionState.IDLE: MARKUP_IDLE,
}


class SessionRail(Static, can_focus=True):
    """Session list with V2 state glyphs and keyboard navigation."""

    DEFAULT_CSS = """
    SessionRail {
        padding: 1 2;
        color: $foreground;
    }
    """

    BINDINGS = [
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("escape", "deselect", "Back", show=False),
    ]

    class Selected(Message):
        """Posted when the user commits a selection with Enter."""

        def __init__(self, row: SessionRow) -> None:
            self.row = row
            super().__init__()

    class Deselected(Message):
        """Posted when the user clears a selection with Escape."""

    class AttachRequested(Message):
        """Posted when Enter is pressed on an already-selected row (D-S3.4)."""

        def __init__(self, row: SessionRow) -> None:
            self.row = row
            super().__init__()

    class BackRequested(Message):
        """Posted from the Esc no-op branch when there is no selection to clear.

        Additive (RAISE-16739, D-S5.4c) — the app uses this to peel the
        filter layer once selection has already been cleared.
        """

    def __init__(self) -> None:
        super().__init__(classes="section")
        self.border_title = "Sessions"
        self._rows: list[SessionRow] = []
        self._cursor: int = 0
        self._selected_id: str | None = None
        self._stale: bool = False

    def set_rows(self, rows: list[SessionRow], stale: bool = False) -> None:
        """Update the session rows, clamp cursor, and preserve selection.

        ``stale=True`` (D-S3.7, additive) dims every row — the rail is
        rendering cached data because a source is currently degraded.
        """
        self._rows = rows
        self._stale = stale
        if rows:
            self._cursor = min(self._cursor, len(rows) - 1)
        else:
            self._cursor = 0
        if self._selected_id is not None and not any(
            row.rail_key == self._selected_id for row in rows
        ):
            self._selected_id = None
            self.remove_class("selected")
            self.post_message(self.Deselected())
        self.refresh()

    @property
    def cursor_row(self) -> SessionRow | None:
        """Return the row currently under the cursor, or None when empty."""
        if not self._rows:
            return None
        return self._rows[self._cursor]

    def move_cursor_to(self, worktree_id: str) -> None:
        """Move the cursor to the first row matching worktree_id (RAISE-16707).

        No-op when no row matches — additive method, does not touch
        render()'s contract (epic D2 / E1 tests).
        """
        for index, row in enumerate(self._rows):
            if row.worktree_id == worktree_id:
                self._cursor = index
                self.refresh()
                return

    def reset_cursor(self) -> None:
        """Move the cursor to row 0 (RAISE-16739, D-S5.5 Enter-commit contract).

        No-op when empty — additive method, does not touch render()'s
        contract (epic D2 / E1 tests).
        """
        if not self._rows:
            return
        self._cursor = 0
        self.refresh()

    def action_cursor_down(self) -> None:
        """Move the cursor down one row, clamped at the last row (no wrap)."""
        if not self._rows:
            return
        self._cursor = min(self._cursor + 1, len(self._rows) - 1)
        self.refresh()

    def action_cursor_up(self) -> None:
        """Move the cursor up one row, clamped at the first row (no wrap)."""
        if not self._rows:
            return
        self._cursor = max(self._cursor - 1, 0)
        self.refresh()

    def action_select(self) -> None:
        """Commit the cursor row as the selection and notify the app.

        D-S3.4: Enter on a row that is already the current selection
        escalates to an attach request instead of re-posting Selected —
        first Enter still selects (S1 contract), second Enter attaches.
        """
        if not self._rows:
            return
        row = self._rows[self._cursor]
        if row.rail_key and row.rail_key == self._selected_id:
            self.post_message(self.AttachRequested(row))
            return
        self._selected_id = row.rail_key
        self.add_class("selected")
        self.refresh()
        self.post_message(self.Selected(row))

    def action_deselect(self) -> None:
        """Clear the current selection and notify the app.

        No selection to clear → post ``BackRequested`` instead (D-S5.4c):
        the app peels the filter layer if one is active, else ignores.
        """
        if self._selected_id is None:
            self.post_message(self.BackRequested())
            return
        self._selected_id = None
        self.remove_class("selected")
        self.refresh()
        self.post_message(self.Deselected())

    def render(self) -> str:
        """Render session list with state glyphs, cursor, and selection."""
        if not self._rows:
            return "(no active sessions)"

        lines: list[str] = []
        for index, row in enumerate(self._rows):
            state = classify_row(row)
            glyph = _STATE_GLYPHS.get(state, GLYPH_IDLE)
            color = _STATE_COLORS.get(state, MARKUP_MUTED)
            raw_label = row.worktree_id if row.worktree_id else "(main)"
            tag = _status_tag(row.worktree)
            budget = 25 - len(tag)
            wt_label = escape(raw_label[:budget] + tag)
            age = _format_age(row.age_hours)
            is_selected = row.rail_key == self._selected_id
            marker = (
                f"[{MARKUP_COPPER}]{_SELECTED_GLYPH}[/{MARKUP_COPPER}]"
                if is_selected
                else " "
            )
            line = f"{marker}[{color}]{glyph}[/{color}] {wt_label:<25} {age:>6}  {state.value}"
            if self._stale:
                line = f"[italic {MARKUP_MUTED}]{line}[/italic {MARKUP_MUTED}]"
            if is_selected:
                line = (
                    f"[on {MARKUP_SELECTION_WASH}]{line}[/on {MARKUP_SELECTION_WASH}]"
                )
            if index == self._cursor:
                line = f"[reverse]{line}[/reverse]"
            lines.append(line)

        return "\n".join(lines)


def _status_tag(worktree: Worktree | None) -> str:
    """Visible status suffix for unregistered/orphan rows (D-S6.4) — else "".

    A status tag, not a new SessionState member: orphan/unregistered rows
    still classify IDLE (or WORKING with a live lease) — the tag is purely
    cosmetic, keeping ``_rediagnose_errors()`` immune to registry noise.
    """
    if worktree is None:
        return ""
    if worktree.status == "unregistered":
        return " ·unreg"
    if worktree.status == "orphan":
        return " ·orphan"
    return ""


def _format_age(hours: float) -> str:
    """Format age as human-readable string."""
    if hours < 1.0:
        return f"{int(hours * 60)}m"
    return f"{hours:.1f}h"
