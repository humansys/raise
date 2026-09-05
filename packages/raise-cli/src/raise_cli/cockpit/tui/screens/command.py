"""Command palette — prefix-autocomplete entry point (RAISE-16712, D-S2.1/D-S2.7).

``CommandPaletteScreen`` follows the decision-only dismiss-result
convention (``CloseConfirmScreen`` precedent): it renders the
prefix-filtered command catalog, moves a selection index with up/down,
and dismisses the chosen command's ``name`` (or ``None`` on Esc) — the
app executes via a dispatch table. This screen never imports services
beyond the pure ``match_commands()`` lookup, and never touches
subprocesses.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from raise_cli.cockpit.tui.services import COMMAND_CATALOG, Command, match_commands
from raise_cli.cockpit.tui.theme import MARKUP_MUTED


def _match_line(cmd: Command, *, selected: bool) -> str:
    marker = ">" if selected else " "
    label = f"{cmd.name:<10} {cmd.description}"
    if not cmd.available:
        label = f"[{MARKUP_MUTED}]{label}[/{MARKUP_MUTED}]"
    return f"{marker} {label}"


class CommandPaletteScreen(ModalScreen[str | None]):
    """Prefix-autocomplete command entry; dismisses the chosen name (D-S2.7)."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("down", "next_match", "Next", show=False),
        Binding("up", "prev_match", "Prev", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._matches: list[Command] = list(COMMAND_CATALOG)
        self._selected = 0

    def compose(self) -> ComposeResult:
        """Build the dialog: title, filter input, live-updating match list."""
        with Vertical(id="dialog"):
            yield Static("Command Palette", id="command-title")
            yield Input(placeholder=":", id="command-input")
            yield Static(self._matches_text(), id="command-matches")

    def _matches_text(self) -> str:
        if not self._matches:
            return "(no matches)"
        return "\n".join(
            _match_line(cmd, selected=index == self._selected)
            for index, cmd in enumerate(self._matches)
        )

    def _refresh_matches_display(self) -> None:
        self.query_one("#command-matches", Static).update(self._matches_text())

    def on_input_changed(self, event: Input.Changed) -> None:
        """Re-filter the catalog on every keystroke and reset the selection."""
        self._matches = match_commands(event.value.strip())
        self._selected = 0
        self._refresh_matches_display()

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        """Enter — dismiss the currently selected match's name."""
        if not self._matches:
            return
        self.dismiss(self._matches[self._selected].name)

    def action_next_match(self) -> None:
        """Down — move the selection toward the end of the match list."""
        if not self._matches:
            return
        self._selected = min(self._selected + 1, len(self._matches) - 1)
        self._refresh_matches_display()

    def action_prev_match(self) -> None:
        """Up — move the selection toward the start of the match list."""
        if not self._matches:
            return
        self._selected = max(self._selected - 1, 0)
        self._refresh_matches_display()

    def action_cancel(self) -> None:
        """Esc — dismiss without a selection."""
        self.dismiss(None)
