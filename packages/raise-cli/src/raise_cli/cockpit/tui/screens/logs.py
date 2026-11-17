"""Read-only session journal viewer modal (RAISE-16739, D-S5.6).

``SessionLogsScreen`` renders the last N journal lines handed to it by the
app (``services.journal_lines()``) and does nothing else — no services, no
subprocesses, flat modal (epic: no stacking). Follows the
``CloseConfirmScreen`` precedent (RAISE-16709): ``#dialog`` container
styled in ``styles.tcss``, ``escape`` dismisses.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class SessionLogsScreen(ModalScreen[None]):
    """Read-only viewer for the last N journal entries of one session."""

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
    ]

    def __init__(self, worktree_id: str, lines: list[str]) -> None:
        super().__init__()
        self._worktree_id = worktree_id
        self._lines = lines

    def compose(self) -> ComposeResult:
        """Build the dialog: title + journal body."""
        with Vertical(id="dialog"):
            yield Static(f"Session Logs: {self._worktree_id}", id="logs-title")
            yield Static(self._body_text(), id="logs-body")

    def _body_text(self) -> str:
        if not self._lines:
            return "(no journal entries)"
        return "\n".join(self._lines)

    def action_close(self) -> None:
        """Esc — dismiss the modal (flat, no return value)."""
        self.dismiss(None)
