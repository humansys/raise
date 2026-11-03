"""Context-aware keybinding overlay (RAISE-16712, D-S2.1/D-S2.2).

``HelpScreen`` follows the flat read-only convention (``SessionLogsScreen``
precedent): it receives pre-computed content — grouped bindings and the
active ``HelpContext`` — renders, and Esc dismisses ``None``. It never
imports services, touches subprocesses, or stacks on another modal (the
app's ``_has_modal()`` guard enforces the flat-modal invariant before this
screen is ever pushed).
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from raise_cli.cockpit.tui.services import HelpBinding, HelpContext

_GROUP_ORDER: tuple[str, ...] = ("navigation", "lifecycle", "filter", "system")

_GROUP_TITLES: dict[str, str] = {
    "navigation": "Navigation",
    "lifecycle": "Lifecycle",
    "filter": "Filter",
    "system": "System",
}

# RAIL context has no dedicated group of its own — it highlights the
# navigation group (the rail's own cursor/select/back keys), while FILTER
# highlights the filter group (D-S2.2).
_CONTEXT_GROUP: dict[HelpContext, str] = {
    HelpContext.RAIL: "navigation",
    HelpContext.FILTER: "filter",
}

_MODAL_KEYS_TEXT = "Modal keys: Enter confirm   Esc cancel   c/s/p/f close-menu choices"


def _body_text(bindings: list[HelpBinding]) -> str:
    if not bindings:
        return "(none)"
    return "\n".join(f"{b.key:<12} {b.description}" for b in bindings)


class HelpScreen(ModalScreen[None]):
    """Renders all four binding groups plus a static modal-keys section."""

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
    ]

    def __init__(
        self, groups: dict[str, list[HelpBinding]], context: HelpContext
    ) -> None:
        super().__init__()
        self._groups = groups
        self._help_context = context

    def compose(self) -> ComposeResult:
        """Build the dialog: title, one section per group, modal-keys footer."""
        active_group = _CONTEXT_GROUP.get(self._help_context, "navigation")
        with Vertical(id="dialog"):
            yield Static("Help", id="help-title")
            for group_name in _GROUP_ORDER:
                classes = "group-title"
                if group_name == active_group:
                    classes += " active-context"
                yield Static(
                    _GROUP_TITLES[group_name],
                    id=f"group-title-{group_name}",
                    classes=classes,
                )
                yield Static(
                    _body_text(self._groups.get(group_name, [])),
                    id=f"group-body-{group_name}",
                    classes="group-body",
                )
            yield Static(_MODAL_KEYS_TEXT, id="help-modal-keys")

    def action_close(self) -> None:
        """Esc — dismiss the overlay (flat, no return value)."""
        self.dismiss(None)
