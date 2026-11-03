"""Close-confirmation modal — decision-only (RAISE-16709, D-S4.4).

``CloseConfirmScreen`` renders the merge-safety report and a merge-state-
aware menu, then dismisses a ``CloseDecision | None``. It never touches
services or subprocesses — the app executes the decision (mirrors the
dismiss-result convention of ``NewSessionScreen``, unlike that screen it
has no per-step progress to show, so it does not need to own execution).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from raise_cli.cockpit.tui.services import CloseSafety, validate_force_close_name


class CloseMode(StrEnum):
    """The action the user chose in the close-confirm modal."""

    CLEANUP = "cleanup"
    SOFT = "soft"
    PAUSE = "pause"
    FORCE_CLEANUP = "force_cleanup"


class CloseDecision(BaseModel):
    """Result dismissed by ``CloseConfirmScreen`` — decision only, no execution."""

    mode: CloseMode


class _ConfirmMode(StrEnum):
    """Sub-state of the modal — drives Esc/key semantics (_Step3Mode precedent)."""

    MENU = "menu"
    NAME_ENTRY = "name_entry"


def _variant(safety: CloseSafety, *, paused: bool) -> str:
    """Paused > merged > unmerged (paused changes the default, not the safety bar)."""
    if paused:
        return "paused"
    if safety.merged:
        return "merged"
    return "unmerged"


class CloseConfirmScreen(ModalScreen[CloseDecision | None]):
    """Merge-state-aware close menu; a destructive choice while unmerged name-gates."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("c", "choose_cleanup", "Cleanup", show=False),
        Binding("s", "choose_soft", "Soft close", show=False),
        Binding("p", "choose_pause", "Pause", show=False),
        Binding("f", "choose_force", "Force close", show=False),
    ]

    def __init__(
        self,
        worktree_id: str,
        branch: str,
        merge_target: str,
        safety: CloseSafety,
        paused: bool,
    ) -> None:
        super().__init__()
        self._worktree_id = worktree_id
        self._branch = branch
        self._merge_target = merge_target
        self._safety = safety
        self._paused = paused
        self._variant = _variant(safety, paused=paused)
        self._mode = _ConfirmMode.MENU
        self._name_error = ""

    # -- composition ---------------------------------------------------

    def compose(self) -> ComposeResult:
        """Build the dialog: title, safety report, menu, hidden name-entry."""
        with Vertical(id="dialog"):
            yield Static(f"Close Session: {self._worktree_id}", id="close-title")
            yield Static(self._safety_text(), id="close-safety")
            yield Static(self._menu_text(), id="close-menu")
            yield Static("", id="close-name-error")
            yield Input(
                placeholder="type worktree id to confirm", id="force-close-name"
            )

    def on_mount(self) -> None:
        """Hide + defocus the name-entry input until it is actually needed.

        ``can_focus=False`` matters as much as ``display=False``: Textual
        auto-focuses the sole focusable widget on screen mount, and a
        focused ``Input`` swallows the menu's letter-key bindings as typed
        text instead of dispatching ``action_choose_*`` (D-S4.4 menu keys).
        """
        name_input = self.query_one("#force-close-name", Input)
        name_input.display = False
        name_input.can_focus = False

    # -- rendering -------------------------------------------------------

    def _safety_text(self) -> str:
        if not self._safety.checked:
            return f"branch: {self._branch}  ->  {self._merge_target}\nmerge state: UNKNOWN (git check failed)"
        return (
            f"branch: {self._branch}  ->  {self._merge_target}\n"
            f"{self._safety.label}: dirty={self._safety.dirty_files} "
            f"unpushed={self._safety.unpushed_commits} "
            f"unmerged={self._safety.unmerged_commits} "
            f"remote={'yes' if self._safety.remote_exists else 'no'}"
        )

    def _menu_text(self) -> str:
        if self._variant == "merged":
            return (
                "[c] Cleanup: delete worktree + branch   [s] Soft close   [Esc] Cancel"
            )
        if self._variant == "paused":
            return (
                "[s] Soft close   [c] Cleanup: delete worktree + branch   [Esc] Cancel"
            )
        return "[p] Pause   [f] Force close (unmerged work)   [Esc] Cancel"

    def _enter_name_gate(self) -> None:
        self._mode = _ConfirmMode.NAME_ENTRY
        self._name_error = ""
        self.query_one("#close-name-error", Static).update("")
        name_input = self.query_one("#force-close-name", Input)
        name_input.display = True
        name_input.can_focus = True
        name_input.value = ""
        name_input.focus()

    def _back_to_menu(self) -> None:
        self._mode = _ConfirmMode.MENU
        self._name_error = ""
        self.query_one("#close-name-error", Static).update("")
        name_input = self.query_one("#force-close-name", Input)
        name_input.display = False
        name_input.can_focus = False

    # -- key handlers ------------------------------------------------------

    def action_choose_cleanup(self) -> None:
        """[c] Cleanup — merged/paused variants; unmerged branches name-gate first."""
        if self._mode != _ConfirmMode.MENU or self._variant not in (
            "merged",
            "paused",
        ):
            return
        if not self._safety.merged:
            self._enter_name_gate()
            return
        self.dismiss(CloseDecision(mode=CloseMode.CLEANUP))

    def action_choose_soft(self) -> None:
        """[s] Soft close — merged/paused variants only."""
        if self._mode != _ConfirmMode.MENU or self._variant not in (
            "merged",
            "paused",
        ):
            return
        self.dismiss(CloseDecision(mode=CloseMode.SOFT))

    def action_choose_pause(self) -> None:
        """[p] Pause — unmerged variant only."""
        if self._mode != _ConfirmMode.MENU or self._variant != "unmerged":
            return
        self.dismiss(CloseDecision(mode=CloseMode.PAUSE))

    def action_choose_force(self) -> None:
        """[f] Force close — unmerged variant only; always name-gated."""
        if self._mode != _ConfirmMode.MENU or self._variant != "unmerged":
            return
        self._enter_name_gate()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Validate the typed worktree id on Enter in the name-entry sub-state."""
        if (
            event.input.id != "force-close-name"
            or self._mode != _ConfirmMode.NAME_ENTRY
        ):
            return
        if validate_force_close_name(event.value, self._worktree_id):
            self.dismiss(CloseDecision(mode=CloseMode.FORCE_CLEANUP))
            return
        self.query_one("#close-name-error", Static).update(
            "worktree id does not match — try again"
        )

    # -- Esc / cancel -------------------------------------------------------

    def action_cancel(self) -> None:
        """Esc — name-entry returns to the menu; menu cancels the whole modal."""
        if self._mode == _ConfirmMode.NAME_ENTRY:
            self._back_to_menu()
            return
        self.dismiss(None)
