"""Textual cockpit TUI — entry point (E1 Foundation).

Launched by `rai --tui`. Complete separation from the Rich Live cockpit
in cockpit/app.py — no imports from that module.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from textual.app import App, ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Resize
from textual.widgets import Input

from raise_cli.cockpit.data import main_repo_root
from raise_cli.cockpit.sessions import SessionRow
from raise_cli.cockpit.tui.screens.command import CommandPaletteScreen
from raise_cli.cockpit.tui.screens.confirm import (
    CloseConfirmScreen,
    CloseDecision,
    CloseMode,
)
from raise_cli.cockpit.tui.screens.help import HelpScreen
from raise_cli.cockpit.tui.screens.logs import SessionLogsScreen
from raise_cli.cockpit.tui.screens.new_session import NewSessionResult, NewSessionScreen
from raise_cli.cockpit.tui.services import (
    AttachOutcome,
    CloseRequest,
    ErrorKind,
    ExpandedDetail,
    HelpContext,
    NewSessionService,
    NewSessionServiceProtocol,
    ProvisionSpec,
    SessionActionsProtocol,
    SessionActionsService,
    SessionCloseService,
    SessionCloseServiceProtocol,
    SessionError,
    SessionInfoProtocol,
    SessionInfoService,
    SourceHealth,
    StepResult,
    apply_filter,
    classify_row,
    diagnose_error_row,
    git_remote_url,
    group_help_bindings,
    merge_worktree_rows,
    sort_rows_attention_first,
)
from raise_cli.cockpit.tui.sources import SqliteSessionSource, SqliteWorktreeDataSource
from raise_cli.cockpit.tui.theme import COPPER_PATINA_DARK
from raise_cli.cockpit.tui.widgets.degraded_banner import DegradedBanner
from raise_cli.cockpit.tui.widgets.detail_panel import DetailPanel
from raise_cli.cockpit.tui.widgets.filter_bar import FilterBar
from raise_cli.cockpit.tui.widgets.recovery_menu import RecoveryMenu
from raise_cli.cockpit.tui.widgets.session_rail import SessionRail
from raise_cli.cockpit.tui.widgets.top_bar import TopBar
from raise_cli.cockpit.types import SessionState
from raise_cli.storage.worktrees import Worktree

_T = TypeVar("_T")

_BREAKPOINT_FULL = 120
_BREAKPOINT_COMPACT = 80
_BREAKPOINT_RAIL = 50


class CockpitApp(App[None]):
    """Session-first cockpit TUI built on Textual."""

    CSS_PATH = "styles.tcss"
    TITLE = "rai"

    # D-S2.5: ':' command palette replaces Textual's built-in ctrl+p provider
    # palette — two coexisting palettes would be UX drift (legacy sweep).
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("n", "new_session", "New"),
        Binding("a", "attach", "Attach"),
        Binding("p", "toggle_pause", "Pause"),
        Binding("x", "close_session", "Close"),
        Binding("slash", "filter", "Filter"),
        Binding("l", "logs", "Logs", show=False),
        Binding("o", "open_mr", "MR", show=False),
        Binding("question_mark", "help", "Help"),
        Binding("colon", "command_palette", "Cmd", show=False),
        Binding("r", "retry_connection", "Retry", show=False),
        Binding("z", "toggle_expand", "Expand"),
        Binding("d", "toggle_density", "Density"),
        Binding("up,k", "expanded_up", "Up", show=False),
        Binding("down,j", "expanded_down", "Down", show=False),
        Binding("escape", "collapse_expanded", "Split view", show=False),
    ]

    def __init__(
        self,
        session_source: SqliteSessionSource | None = None,
        worktree_source: SqliteWorktreeDataSource | None = None,
        new_session_service: NewSessionServiceProtocol | None = None,
        session_actions: SessionActionsProtocol | None = None,
        session_close: SessionCloseServiceProtocol | None = None,
        session_info: SessionInfoProtocol | None = None,
    ) -> None:
        super().__init__()
        self._session_source = session_source or SqliteSessionSource()
        self._worktree_source = worktree_source or SqliteWorktreeDataSource()
        self._new_session_service = new_session_service
        self._session_actions = session_actions
        self._session_close = session_close
        self._session_info = session_info
        self._filter_query: str = ""
        self._all_rows: list[SessionRow] = []
        self._degraded: bool = False
        # Error registry (D-S3.2): keyed by worktree_id. Diagnosed entries
        # are recomputed every refresh; verb-failure entries persist until
        # dismissed, resolved, or their worktree disappears.
        self._session_errors: dict[str, SessionError] = {}
        # Expanded detail view (RAISE-16714, D-S4.1): bool on the app + a
        # Screen CSS class — not a ModalScreen (epic Key Contract 4).
        self._expanded: bool = False

    def compose(self) -> ComposeResult:
        """Build the widget tree."""
        yield TopBar()
        yield FilterBar()
        yield DegradedBanner()
        yield SessionRail()
        with Vertical(id="detail-column"):
            yield DetailPanel()
            yield RecoveryMenu()

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """Custom variables must resolve during startup CSS parse (pre-theme)."""
        return dict(COPPER_PATINA_DARK.variables)

    def on_mount(self) -> None:
        """Activate the Copper & Patina palette, load real data, focus the rail."""
        self.register_theme(COPPER_PATINA_DARK)
        # LATTE registration deferred to H2
        self.theme = "copper-patina-dark"
        self._refresh_rail()
        self.query_one(SessionRail).focus()

    def _has_modal(self) -> bool:
        """True when a modal screen is already on top — block verb dispatch."""
        return len(self.screen_stack) > 1

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Gate expanded-only bindings — inert while collapsed (RAISE-16714, D-S4.2).

        ``up,k``/``down,j``/``escape`` are shared with ``SessionRail``'s own
        bindings; a focused rail always resolves its own binding first
        (innermost wins), so this override only matters when nothing is
        focused (``set_focus(None)`` on expand) or a modal's own binding
        doesn't claim the key first.
        """
        if action in ("expanded_up", "expanded_down", "collapse_expanded"):
            return self._expanded
        return True

    def action_new_session(self) -> None:
        """Open the new-session wizard (RAISE-16707)."""
        if self._has_modal():
            return
        service = self._new_session_service or NewSessionService(main_repo_root())
        existing_ids = {row.worktree_id for row in self._all_rows if row.worktree_id}
        self.push_screen(NewSessionScreen(service, existing_ids), self._on_new_session)

    def _on_new_session(self, result: NewSessionResult | None) -> None:
        """Refresh the rail with the newly provisioned session, or no-op on cancel."""
        if result is None:
            return
        self._refresh_rail(cursor_to=result.slug)
        if result.kept_after_failure:
            self.notify(
                f"worktree kept at {result.worktree_path} — fix manually",
                severity="warning",
            )
            # D-S3.1 continuity: register a rail-level error so the wizard's
            # failure context survives after the modal closes.
            self._session_errors[result.slug] = SessionError(
                kind=ErrorKind.STALE_BASE,
                worktree_id=result.slug,
                what_failed=f"provisioning failed ({result.failure_kind or 'unknown'})",
                whats_safe="worktree kept on disk, nothing rolled back",
                at_risk="worktree not fully registered/leased",
                detail=result.failure_detail,
                diagnosed=False,
            )
            self._sync_recovery_menu(result.slug)
            self.query_one(RecoveryMenu).focus()

    def on_session_rail_selected(self, message: SessionRail.Selected) -> None:
        """Push the selected session's worktree data into the detail panel.

        Also reveals the RecoveryMenu block when the row has a registered
        error (D-S3.4) — no focus steal, the block just renders.
        """
        row = message.row
        detail = self.query_one(DetailPanel)
        worktree = row.worktree
        if worktree is not None:
            detail.set_worktree(
                worktree.worktree_id,
                worktree.branch,
                self._worktree_source.preview(worktree.worktree_id),
            )
        else:
            detail.set_worktree(row.worktree_id or "(main)", "(no worktree)", {})
        self._sync_recovery_menu(row.worktree_id)

    def _sync_recovery_menu(self, worktree_id: str) -> None:
        """Show/hide the RecoveryMenu block for *worktree_id*'s registered error."""
        menu = self.query_one(RecoveryMenu)
        error = self._session_errors.get(worktree_id) if worktree_id else None
        if error is not None:
            menu.show_error(error)
        else:
            menu.hide()

    def on_session_rail_deselected(self, _message: SessionRail.Deselected) -> None:
        """Clear the detail panel and hide the recovery block on deselect."""
        self.query_one(DetailPanel).clear_selection()
        self.query_one(RecoveryMenu).hide()

    def on_session_rail_attach_requested(
        self, message: SessionRail.AttachRequested
    ) -> None:
        """Second Enter on an already-selected row (D-S3.4).

        Routes to the RecoveryMenu when the row has a registered error
        (relaunch is the menu's first action — attach is one Enter away);
        otherwise attaches as before.
        """
        row = message.row
        if row.worktree_id and row.worktree_id in self._session_errors:
            self.query_one(RecoveryMenu).focus()
            return
        self.action_attach()

    def on_recovery_menu_action_chosen(
        self, message: RecoveryMenu.ActionChosen
    ) -> None:
        """Dispatch a committed recovery action to the matching app verb."""
        self.query_one(SessionRail).move_cursor_to(message.worktree_id)
        dispatch: dict[str, Callable[[], None]] = {
            "relaunch": self.action_attach,
            "view_logs": self.action_logs,
            "close": self.action_close_session,
            "retry": lambda: self._retry_failed_verb(message.worktree_id),
            "rebase": lambda: self._start_recovery_rebase(message.worktree_id),
            "dismiss": lambda: self._dismiss_error(message.worktree_id),
        }
        handler = dispatch.get(message.action_id)
        if handler is not None:
            handler()

    def on_recovery_menu_dismissed(self, _message: RecoveryMenu.Dismissed) -> None:
        """Esc on the menu — focus retreats to the rail; block persists (AC5)."""
        self.query_one(SessionRail).focus()

    def _dismiss_error(self, worktree_id: str) -> None:
        """Dismiss action — pop the registry entry and hide the block."""
        self._session_errors.pop(worktree_id, None)
        self.query_one(RecoveryMenu).hide()
        self.query_one(SessionRail).focus()

    def _retry_failed_verb(self, worktree_id: str) -> None:
        """Retry — semantics depend on the registered error's kind (D-S3.5).

        STALE_BASE re-opens the new-session wizard (retry provisioning);
        everything else re-invokes the only rail-level GIT_FAILURE
        producer today, close (D-S3.5's rejected-Rollback note).
        """
        error = self._session_errors.get(worktree_id)
        if error is None:
            return
        if error.kind == ErrorKind.STALE_BASE:
            self.action_new_session()
            return
        self.action_close_session()

    def _find_worktree(self, worktree_id: str) -> Worktree | None:
        """Single lookup helper over ``self._all_rows`` (RAISE-16824, D-S6.7).

        The one entry point that only carries a bare ``worktree_id`` string
        (``RecoveryMenu`` messages) rather than a self-contained
        ``SessionRow`` — every other call site now reads ``row.worktree``
        directly.
        """
        for row in self._all_rows:
            if row.worktree_id == worktree_id and row.worktree is not None:
                return row.worktree
        return None

    def _start_recovery_rebase(self, worktree_id: str) -> None:
        """Rebase onto target — thread-worker execution (D-S3.5/D-S3.6)."""
        worktree = self._find_worktree(worktree_id)
        if worktree is None:
            self.notify("worktree not found — cannot rebase", severity="error")
            return
        spec = ProvisionSpec(
            slug=worktree_id,
            branch=worktree.branch,
            worktree_path=Path(worktree.path),
            merge_target=worktree.merge_target or "release/3.1.0",
            base_ref=worktree.merge_target or "release/3.1.0",
        )
        service = self._new_session_service or NewSessionService(main_repo_root())
        self.notify("◐ rebasing…")
        self.run_worker(
            lambda: self._run_recovery_rebase(service, spec, worktree_id),
            thread=True,
            exclusive=True,
            group="recovery-rebase",
        )

    def _run_recovery_rebase(
        self, service: NewSessionServiceProtocol, spec: ProvisionSpec, worktree_id: str
    ) -> None:
        """Thread-worker body — never touches the UI directly (D-S3.6)."""
        result = service.rebase_worktree(spec)
        self.call_from_thread(self._on_recovery_rebase_complete, worktree_id, result)

    def _on_recovery_rebase_complete(
        self, worktree_id: str, result: StepResult
    ) -> None:
        """Main-thread completion: resolve on success, keep the error on failure."""
        if result.ok:
            self.notify("✓ rebased")
            self._session_errors.pop(worktree_id, None)
        else:
            self.notify(f"✗ rebase failed: {result.detail}", severity="error")
        self._refresh_rail(cursor_to=worktree_id)

    def _source_health(self, source: object) -> SourceHealth:
        """Tolerant health read (D-S3.3): defaults to healthy when absent.

        ``getattr`` + isinstance narrowing keeps E1/E2 fakes (no ``health``
        attribute) passing unchanged — the ``SessionSource``/
        ``WorktreeDataSource`` protocols are not extended.
        """
        health = getattr(source, "health", None)
        return health if isinstance(health, SourceHealth) else SourceHealth()

    def _refresh_rail(self, *, cursor_to: str | None = None) -> None:
        """Reload both data sources and re-render the rail, attention-first sorted.

        Shared by on_mount(), _on_new_session(), action_attach(), and
        action_toggle_pause() — extracted to avoid four copies of the same
        refresh-and-resort block. Filter application lives inside this
        funnel (D-S5.1/gemba 8) so a mid-filter pause/attach/close does not
        silently un-filter the rail.
        """
        self._session_source.refresh()
        self._worktree_source.refresh()
        self._render_rail_from_sources(cursor_to=cursor_to)

    def _render_rail_from_sources(self, *, cursor_to: str | None = None) -> None:
        """Re-derive rows/banner/staleness from the sources' *current* state.

        Shared by ``_refresh_rail()`` (after a synchronous refresh) and
        ``_retry_sources()``'s main-thread completion callback (D-S3.6/
        D-S3.7) — neither path re-fetches here, it only re-renders.
        """
        self._degraded = not (
            self._source_health(self._session_source).ok
            and self._source_health(self._worktree_source).ok
        )
        self._all_rows = sort_rows_attention_first(
            merge_worktree_rows(
                self._worktree_source.list_worktrees(),
                self._session_source.list_sessions(),
            )
        )
        self._rediagnose_errors()
        self._update_banner()
        self._apply_filter_to_rail(cursor_to=cursor_to, stale=self._degraded)

    def _rediagnose_errors(self) -> None:
        """Registry hygiene (D-S3.2): recompute diagnosed entries every refresh.

        Diagnosed (auto) entries are fully replaced by the current
        ERROR-classified rows. Persisted (verb-failure) entries survive
        until their worktree disappears entirely from both sources —
        "live" means either a session row or a registered worktree still
        references that id, so a kept-after-failure worktree (no lease,
        no session row) is not pruned before the user can act on it.
        """
        live_worktree_ids = {
            row.worktree_id for row in self._all_rows if row.worktree_id
        }
        for worktree_id in list(self._session_errors):
            error = self._session_errors[worktree_id]
            if not error.diagnosed and worktree_id not in live_worktree_ids:
                del self._session_errors[worktree_id]

        error_row_ids: set[str] = set()
        for row in self._all_rows:
            if not row.worktree_id:
                continue
            if classify_row(row) == SessionState.ERROR:
                error_row_ids.add(row.worktree_id)
                existing = self._session_errors.get(row.worktree_id)
                if existing is None or existing.diagnosed:
                    self._session_errors[row.worktree_id] = diagnose_error_row(row)

        for worktree_id in list(self._session_errors):
            error = self._session_errors[worktree_id]
            if error.diagnosed and worktree_id not in error_row_ids:
                del self._session_errors[worktree_id]

    def _update_banner(self) -> None:
        """Show/hide the DegradedBanner based on ``self._degraded``."""
        banner = self.query_one(DegradedBanner)
        if not self._degraded:
            banner.hide()
            return
        session_h = self._source_health(self._session_source)
        worktree_h = self._source_health(self._worktree_source)
        candidates = [
            h.last_sync
            for h in (session_h, worktree_h)
            if not h.ok and h.last_sync is not None
        ]
        last_sync = min(candidates) if candidates else None
        banner.show_degraded(last_sync)

    def action_retry_connection(self) -> None:
        """`r` — async re-probe of both sources when degraded (D-S3.7)."""
        if self._has_modal() or not self._degraded:
            return
        self.run_worker(self._retry_sources, thread=True, exclusive=True, group="retry")

    def _retry_sources(self) -> None:
        """Thread-worker body: re-probe both sources, then re-render on the UI thread."""
        self._session_source.refresh()
        self._worktree_source.refresh()
        self.call_from_thread(self._render_rail_from_sources)

    def _apply_filter_to_rail(
        self, *, cursor_to: str | None = None, stale: bool = False
    ) -> None:
        """Re-narrow the cached row set by ``self._filter_query`` — no DB access.

        Called on every FilterBar keystroke (AC1: real-time, <100ms, no
        SQLite hit) as well as from ``_render_rail_from_sources()``.
        """
        rail = self.query_one(SessionRail)
        filtered = apply_filter(self._all_rows, self._filter_query)
        rail.set_rows(filtered, stale=stale)
        self.query_one(FilterBar).set_count(len(filtered), len(self._all_rows))
        if cursor_to is not None:
            rail.move_cursor_to(cursor_to)

    def _clear_filter(self) -> None:
        """Clear the filter query, hide the bar, restore the full list, focus rail."""
        self._filter_query = ""
        self.query_one(FilterBar).hide_and_clear()
        self._apply_filter_to_rail(stale=self._degraded)
        self.query_one(SessionRail).focus()

    def action_filter(self) -> None:
        """`/` — reveal and focus the FilterBar (AC1)."""
        if self._has_modal() or self._expanded:
            return
        self.query_one(FilterBar).show_and_focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Every FilterBar keystroke re-narrows the rail in real time (AC1)."""
        if event.input.id != "filter-input":
            return
        self._filter_query = event.value
        self._apply_filter_to_rail(stale=self._degraded)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter in the FilterBar commits: keep the list, focus rail, cursor 0 (D-S5.5)."""
        if event.input.id != "filter-input":
            return
        rail = self.query_one(SessionRail)
        rail.reset_cursor()
        rail.focus()

    def on_filter_bar_dismissed(self, _message: FilterBar.Dismissed) -> None:
        """Esc while the FilterBar is focused clears+hides+restores (D-S5.4a)."""
        self._clear_filter()

    def on_session_rail_back_requested(
        self, _message: SessionRail.BackRequested
    ) -> None:
        """Esc on the rail with no selection peels the filter layer (D-S5.4c)."""
        if self._filter_query:
            self._clear_filter()

    # -----------------------------------------------------------------
    # Expanded detail view (RAISE-16714, D-S4.1/D-S4.2/D-S4.7)
    # -----------------------------------------------------------------

    def action_toggle_expand(self) -> None:
        """`z` — expand the detail column full-screen, or collapse if already expanded."""
        if self._has_modal():
            return
        if self._expanded:
            self._collapse_expanded()
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None or not row.worktree_id:
            self.notify("no worktree — cannot expand", severity="warning")
            return
        self._expanded = True
        self.screen.add_class("expanded")
        self.query_one(FilterBar).display = False  # inline display, not CSS (gemba 4)
        self.query_one(TopBar).set_hint("z/ESC · split view")
        self._push_expanded_detail(row)
        self.set_focus(None)

    def action_expanded_up(self) -> None:
        """Up/k while expanded — move the rail cursor and re-render (D-S4.7)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        rail.action_cursor_up()
        self._push_expanded_detail(rail.cursor_row)

    def action_expanded_down(self) -> None:
        """Down/j while expanded — move the rail cursor and re-render (D-S4.7)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        rail.action_cursor_down()
        self._push_expanded_detail(rail.cursor_row)

    def action_collapse_expanded(self) -> None:
        """Esc while expanded — return to the split view (D-S4.8)."""
        if self._has_modal():
            return
        self._collapse_expanded()

    def _collapse_expanded(self) -> None:
        """Shared collapse body for both `z` and Esc while expanded (D-S4.7)."""
        self._expanded = False
        self.screen.remove_class("expanded")
        self.query_one(DetailPanel).clear_expanded()  # split content reappears
        self.query_one(TopBar).set_hint(None)
        self.query_one(FilterBar).display = bool(self._filter_query)
        self.query_one(SessionRail).focus()

    def _push_expanded_detail(self, row: SessionRow | None) -> None:
        """Resolve *row*'s worktree and render its expanded report (D-S4.7).

        Rows without a worktree (or a stale worktree_id) render the same
        "(no worktree)" placeholder the split view uses.
        """
        detail = self.query_one(DetailPanel)
        if row is None or not row.worktree_id:
            detail.set_expanded(ExpandedDetail(worktree_id="", branch="(no worktree)"))
            return
        worktree = row.worktree
        if worktree is None:
            detail.set_expanded(
                ExpandedDetail(worktree_id=row.worktree_id, branch="(no worktree)")
            )
            return
        svc = self._session_info or SessionInfoService()
        preview = self._worktree_source.preview(worktree.worktree_id)
        detail.set_expanded(svc.expanded_detail(worktree, preview))

    def action_toggle_density(self) -> None:
        """`d` — flip `Screen.dense`; CSS-only density switch (RAISE-16860, D-S3.1/D-S3.2).

        No mirrored ``self._dense`` bool: ``screen.classes`` is the single
        source of truth — nothing else gates on density.
        """
        if self._has_modal():
            return
        self.screen.toggle_class("dense")

    def action_logs(self) -> None:
        """`l` — open a read-only journal viewer for the cursor row (D-S5.6)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None or not row.session_id:
            self.notify("no session journal for this row", severity="warning")
            return
        worktree = row.worktree
        worktree_path = (
            Path(worktree.path) if worktree is not None else main_repo_root()
        )
        svc = self._session_info or SessionInfoService()
        lines = svc.journal_lines(worktree_path, row.session_id, last_n=50)
        self.push_screen(SessionLogsScreen(row.worktree_id or "(main)", lines))

    def action_open_mr(self) -> None:
        """`o` — open the GitLab MR-list URL for the cursor row's branch (D-S5.7)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None or not row.worktree_id:
            self.notify("no worktree — cannot open MR", severity="warning")
            return
        worktree = row.worktree
        if worktree is None:
            self.notify("no worktree — cannot open MR", severity="warning")
            return
        remote_url = git_remote_url(Path(worktree.path))
        if not remote_url:
            self.notify("no origin remote — cannot open MR", severity="warning")
            return
        svc = self._session_info or SessionInfoService()
        url = svc.mr_url(remote_url, worktree.branch)
        if url is None:
            self.notify("no origin remote — cannot open MR", severity="warning")
            return
        if not svc.open_url(url):
            self.notify("could not open browser", severity="error")

    def action_help(self) -> None:
        """`?` — context-aware keybinding overlay (RAISE-16712, D-S2.2/D-S2.3)."""
        if self._has_modal():
            return
        context = HelpContext.FILTER if self._filter_query else HelpContext.RAIL
        bindings = [
            b for b in (*self.BINDINGS, *SessionRail.BINDINGS) if isinstance(b, Binding)
        ]
        self.push_screen(HelpScreen(group_help_bindings(bindings), context))

    def action_command_palette(self) -> None:
        """`:` — command palette; screen dismisses a name, app executes (D-S2.1)."""
        if self._has_modal():
            return
        self.push_screen(CommandPaletteScreen(), self._on_command)

    def _on_command(self, name: str | None) -> None:
        """Dispatch a command-palette selection to an existing app action (D-S2.4)."""
        if name is None:
            return
        dispatch: dict[str, Callable[[], None]] = {
            "new": self.action_new_session,
            "close": self.action_close_session,
            "clear": self._clear_filter,
            "help": self.action_help,
            "refresh": self._refresh_rail,
            "quit": self.exit,
        }
        handler = dispatch.get(name)
        if handler is None:
            self.notify(f"'{name}' arrives in a later story", severity="warning")
            return
        handler()

    def _suspend_agent(self, fn: Callable[[], _T]) -> _T | None:
        """Suspend the TUI, run *fn*, and resume (D-S3.7 testability seam).

        Translates ``SuspendNotSupported`` (headless/web drivers) into a
        user-facing notify instead of an unhandled exception. Subclassed
        to a no-op in tests so attach wiring is exercisable without a TTY.
        """
        try:
            with self.suspend():
                return fn()
        except SuspendNotSupported:
            self.notify("terminal does not support suspend", severity="error")
            return None

    def action_attach(self) -> None:
        """Attach to the agent for the cursor row's worktree (D3/D7)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None or not row.worktree_id:
            self.notify("no worktree — cannot attach", severity="warning")
            return
        worktree = row.worktree
        if worktree is None:
            self.notify("worktree not found — cannot attach", severity="error")
            self._session_errors[row.worktree_id] = SessionError(
                kind=ErrorKind.GENERIC,
                worktree_id=row.worktree_id,
                what_failed="attach failed — worktree not found",
                whats_safe="session lease/pointer state untouched",
                diagnosed=False,
            )
            self._sync_recovery_menu(row.worktree_id)
            self.query_one(RecoveryMenu).focus()
            return

        svc = self._session_actions or SessionActionsService(main_repo_root())
        worktree_path = Path(worktree.path)
        agent = svc.select_agent(worktree_path)
        if agent is None:
            self.notify("no agent available for this worktree", severity="error")
            return

        outcome = self._suspend_agent(lambda: svc.run_agent(worktree_path, agent))
        if outcome is None:
            return  # suspend not supported — already notified

        if not svc.renew_cockpit_lease(row.worktree_id):
            self.notify(
                "lease not held by cockpit — check session state",
                severity="warning",
            )
        self._refresh_rail(cursor_to=row.worktree_id)
        self._notify_attach_outcome(outcome)

    def _notify_attach_outcome(self, outcome: AttachOutcome) -> None:
        """Surface the attach result — which agent ran, how it exited."""
        if outcome.ok:
            self.notify(outcome.detail or f"{outcome.agent_name} exited")
        else:
            self.notify(outcome.detail or "attach failed", severity="error")

    def action_toggle_pause(self) -> None:
        """Flip the persisted pause flag for the cursor row's worktree (D6)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None:
            return
        if not row.worktree_id:
            self.notify("no worktree — cannot pause", severity="warning")
            return
        svc = self._session_actions or SessionActionsService(main_repo_root())
        svc.toggle_pause(row.worktree_id)
        self._refresh_rail(cursor_to=row.worktree_id)

    def action_close_session(self) -> None:
        """Open the merge-state-aware close confirm modal for the cursor row (D-S4.5)."""
        if self._has_modal():
            return
        rail = self.query_one(SessionRail)
        row = rail.cursor_row
        if row is None or not row.worktree_id:
            self.notify("no worktree — cannot close", severity="warning")
            return
        worktree = row.worktree
        if worktree is None:
            self.notify("worktree not found — cannot close", severity="error")
            return

        svc = self._session_close or SessionCloseService(main_repo_root())
        merge_target = worktree.merge_target or "release/3.1.0"
        safety = svc.check_merge_state(
            Path(worktree.path), worktree.branch, merge_target
        )
        self.push_screen(
            CloseConfirmScreen(
                worktree_id=row.worktree_id,
                branch=worktree.branch,
                merge_target=merge_target,
                safety=safety,
                paused=row.paused,
            ),
            lambda decision: self._on_close_decision(row, worktree, decision),
        )

    def _on_close_decision(
        self, row: SessionRow, worktree: Worktree, decision: CloseDecision | None
    ) -> None:
        """Execute the user's close-modal decision (D-S4.5); no-op on Esc (None)."""
        if decision is None:
            return
        if decision.mode is CloseMode.PAUSE:
            svc = self._session_actions or SessionActionsService(main_repo_root())
            svc.toggle_pause(row.worktree_id)
            self._refresh_rail(cursor_to=row.worktree_id)
            return

        close_svc = self._session_close or SessionCloseService(main_repo_root())
        outcome = close_svc.close_session(
            CloseRequest(
                worktree_id=row.worktree_id,
                session_id=row.session_id,
                path=Path(worktree.path),
                branch=worktree.branch,
            ),
            cleanup=decision.mode is not CloseMode.SOFT,
        )
        if not outcome.ok:
            self.notify(outcome.detail or "close failed", severity="error")
            self._session_errors[row.worktree_id] = SessionError(
                kind=ErrorKind.GIT_FAILURE,
                worktree_id=row.worktree_id,
                what_failed="close failed",
                whats_safe="session state was already cleared (lease/pointer/pause)",
                at_risk="worktree/branch left on disk — see detail for manual cleanup",
                detail=outcome.detail,
                diagnosed=False,
            )
            self._refresh_rail()
            self._sync_recovery_menu(row.worktree_id)
            self.query_one(RecoveryMenu).focus()
            return
        self.query_one(DetailPanel).clear_selection()
        self._refresh_rail()

    def on_resize(self, event: Resize) -> None:
        """Switch responsive tier CSS classes based on terminal width."""
        width = event.size.width
        screen = self.screen
        screen.remove_class("compact", "rail-only", "floor")
        if width >= _BREAKPOINT_FULL:
            pass
        elif width >= _BREAKPOINT_COMPACT:
            screen.add_class("compact")
        elif width >= _BREAKPOINT_RAIL:
            screen.add_class("rail-only")
        else:
            screen.add_class("floor")


def run_cockpit_tui(
    mission: str | None = None,  # noqa: ARG001 — reserved for E2
    agent: str | None = None,  # noqa: ARG001 — reserved for E2
    use_last: bool = False,  # noqa: ARG001 — reserved for E2
) -> None:
    """Launch the Textual cockpit TUI."""
    app = CockpitApp()
    app.run()
