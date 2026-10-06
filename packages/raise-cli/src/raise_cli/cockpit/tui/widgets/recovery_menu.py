"""RecoveryMenu widget — focusable non-modal error block + action menu.

Renders the full explain-block (what failed / what's safe / at risk /
last known good / detail) for a ``SessionError`` plus its per-``ErrorKind``
recovery actions (D-S3.4/D-S3.5). Owns navigation state only — the app
executes actions (``ActionChosen``) and owns registry hygiene; this
widget never dispatches to a verb itself.
"""

from __future__ import annotations

from rich.markup import escape
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Static

from raise_cli.cockpit.tui.services import (
    RecoveryAction,
    SessionError,
    recovery_actions,
)


class RecoveryMenu(Static, can_focus=True):
    """Inline red-bordered error block + keyboard-navigable recovery menu."""

    BINDINGS = [
        Binding("up,k", "cursor_up", "Up", show=False),
        Binding("down,j", "cursor_down", "Down", show=False),
        Binding("enter", "choose", "Choose", show=False),
        Binding("escape", "dismiss_menu", "Back", show=False),
    ]

    class ActionChosen(Message):
        """Posted when Enter commits the highlighted recovery action."""

        def __init__(self, action_id: str, worktree_id: str) -> None:
            self.action_id = action_id
            self.worktree_id = worktree_id
            super().__init__()

    class Dismissed(Message):
        """Posted on Esc — the app moves focus back to the rail (D-S3.4).

        The error block is *not* hidden by this message (AC2/AC5 letter):
        only an explicit ``hide()`` call (dismiss/resolve/row-gone) does.
        """

    def __init__(self) -> None:
        super().__init__()
        self._error: SessionError | None = None
        self._actions: list[RecoveryAction] = []
        self._cursor: int = 0

    @property
    def cursor_index(self) -> int:
        """Index of the currently highlighted action."""
        return self._cursor

    @property
    def error(self) -> SessionError | None:
        """The ``SessionError`` currently rendered, or None when hidden."""
        return self._error

    def show_error(self, error: SessionError) -> None:
        """Render *error*'s explain-block + its kind's recovery menu."""
        self._error = error
        self._actions = recovery_actions(error.kind)
        self._cursor = 0
        self.add_class("visible")
        self.refresh()

    def hide(self) -> None:
        """Conceal the block (dismiss/resolve/row-gone — never on Esc alone)."""
        self.remove_class("visible")
        self.refresh()

    def action_cursor_up(self) -> None:
        """Move the highlight up one action, clamped at the first (no wrap)."""
        if not self._actions:
            return
        self._cursor = max(self._cursor - 1, 0)
        self.refresh()

    def action_cursor_down(self) -> None:
        """Move the highlight down one action, clamped at the last (no wrap)."""
        if not self._actions:
            return
        self._cursor = min(self._cursor + 1, len(self._actions) - 1)
        self.refresh()

    def action_choose(self) -> None:
        """Commit the highlighted action — posts ``ActionChosen``, app dispatches."""
        if not self._actions or self._error is None:
            return
        action = self._actions[self._cursor]
        self.post_message(self.ActionChosen(action.action_id, self._error.worktree_id))

    def action_dismiss_menu(self) -> None:
        """Esc — post ``Dismissed``; the block itself stays rendered."""
        self.post_message(self.Dismissed())

    def render(self) -> str:
        """Render the explain-block + action menu, or empty when no error."""
        error = self._error
        if error is None:
            return ""

        lines: list[str] = [f"✗ {escape(error.what_failed)}"]
        if error.whats_safe:
            lines.append(f"safe: {escape(error.whats_safe)}")
        if error.at_risk:
            lines.append(f"at risk: {escape(error.at_risk)}")
        if error.last_good:
            lines.append(f"last known good: {escape(error.last_good)}")
        if error.detail:
            lines.append(escape(error.detail))
        lines.append("")

        for index, action in enumerate(self._actions):
            marker = "▸" if index == self._cursor else " "
            line = f"{marker} {action.label}"
            if index == self._cursor:
                line = f"[reverse]{line}[/reverse]"
            lines.append(line)

        return "\n".join(lines)
