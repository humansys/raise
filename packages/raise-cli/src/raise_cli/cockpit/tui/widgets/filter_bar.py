"""FilterBar widget — vim-style `/` filter overlay (RAISE-16739, epic D5).

Thin ``Input`` wrapper docked under the ``TopBar`` (D-S5.2): yielded once
in ``CockpitApp.compose()``, hidden by default (``display: none``), shown
full-width when `/` is pressed. Owns no filter state itself (D-S5.1) — it
only renders the query input and a match-count readout; ``CockpitApp``
drives narrowing via ``Input.Changed``/``Input.Submitted`` and calls
``set_count()`` after every re-render.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Input, Static


class FilterBar(Horizontal):
    """Docked, hidden-by-default filter input with a match-count readout."""

    DEFAULT_CSS = """
    FilterBar {
        dock: top;
        height: 1;
        display: none;
        background: $surface_warm;
    }

    FilterBar > Input {
        width: 1fr;
        height: 1;
        border: none;
        padding: 0 1;
        background: $surface_warm;
    }

    FilterBar > #filter-count {
        width: auto;
        padding: 0 1;
        color: $overlay1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_filter", "Cancel", show=False),
    ]

    class Dismissed(Message):
        """Posted when Esc is pressed while the bar (or its input) is focused."""

    def __init__(self) -> None:
        super().__init__()
        self.display = False

    def compose(self) -> ComposeResult:
        """Build the input + match-count readout."""
        yield Input(placeholder="filter…", id="filter-input")
        yield Static("", id="filter-count")

    def show_and_focus(self) -> None:
        """Reveal the bar and focus its input (`/` binding, AC1)."""
        self.display = True
        self.query_one(Input).focus()

    def hide_and_clear(self) -> None:
        """Hide the bar and clear its query text (Esc contract, D-S5.4a)."""
        self.display = False
        self.query_one(Input).value = ""

    def set_count(self, matches: int, total: int) -> None:
        """Update the match-count readout (D-S5.9): ``{matches}/{total}``."""
        self.query_one("#filter-count", Static).update(f"{matches}/{total}")

    @property
    def filter_text(self) -> str:
        """Current filter text (empty string means no filter active)."""
        return self.query_one(Input).value

    def action_dismiss_filter(self) -> None:
        """Esc while the bar/input is focused — let the app clear+hide+refocus."""
        self.post_message(self.Dismissed())
