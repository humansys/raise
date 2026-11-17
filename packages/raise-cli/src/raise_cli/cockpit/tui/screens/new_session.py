"""New Session wizard — 3-step ModalScreen with RAISE-16697 failure recovery.

Step 1 (name) -> Step 2 (base branch) -> Step 3 (provisioning). Provisioning
runs as an async worker that awaits thread-workers for each blocking git/rai
call (SD5) — this keeps the screen's own message queue free to handle Esc
mid-provisioning (cooperative cancel, checked between steps only; a running
subprocess is never killed mid-flight).
"""

from __future__ import annotations

from collections.abc import Collection
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import ContentSwitcher, Input, Label, ListItem, ListView, Static

from raise_cli.cockpit.tui.services import (
    BranchResolution,
    FailureKind,
    NewSessionServiceProtocol,
    ProvisionSpec,
    StepResult,
    classify_failure,
)

if TYPE_CHECKING:
    from textual.worker import Worker

_STEP_LABELS: tuple[str, ...] = (
    "resolving base ref",
    "creating worktree",
    "registering + provisioning",
    "activating session",
)
_STEP_NAMES: tuple[str, ...] = (
    "resolve_base",
    "create_worktree",
    "register_worktree",
    "acquire_lease",
)
_MARK_PENDING = "…"
_MARK_RUNNING = "◐"
_MARK_DONE = "✓"
_MARK_FAILED = "✗"


class NewSessionResult(BaseModel):
    """Outcome returned by ``NewSessionScreen.dismiss()`` on success or keep."""

    slug: str
    worktree_path: Path
    branch: str
    merge_target: str
    kept_after_failure: bool = False
    # Additive continuity fields (RAISE-16713, D-S3.1): populated only when
    # kept_after_failure=True so the app can register a rail-level
    # SessionError — the wizard menu itself is unchanged (E2, RAISE-16697).
    failure_kind: str = ""
    failure_detail: str = ""


class _Step3Mode(StrEnum):
    """Sub-state of the provisioning step — drives Esc/recovery-key semantics."""

    IDLE = "idle"
    RUNNING = "running"
    CONFIRM_CANCEL = "confirm_cancel"
    RECOVERY = "recovery"


class BranchListView(ListView):
    """ListView with j/k navigation, matching the rail's vim-style bindings."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]


class NewSessionScreen(ModalScreen[NewSessionResult | None]):
    """3-step new-session wizard with RAISE-16697 failure recovery."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("b", "recovery_choose_branch", "Choose branch", show=False),
        Binding("t", "recovery_retry", "Retry", show=False),
        Binding("e", "recovery_rebase", "Rebase & retry", show=False),
        Binding("k", "recovery_keep", "Keep worktree", show=False),
        Binding("r", "recovery_rollback", "Rollback", show=False),
    ]

    def __init__(
        self,
        service: NewSessionServiceProtocol,
        existing_ids: Collection[str] | None = None,
    ) -> None:
        super().__init__()
        self._service = service
        self._existing_ids: set[str] = set(existing_ids or ())

        self._step: int = 1
        self._slug: str = ""
        self._default_resolution: BranchResolution | None = None
        self._selected_branch: str | None = None
        self._branch_options: list[str] = []
        self._resolution: BranchResolution | None = None
        self._spec: ProvisionSpec | None = None

        self._step3_mode: _Step3Mode = _Step3Mode.IDLE
        self._step_marks: list[str] = [_MARK_PENDING] * len(_STEP_NAMES)
        self._cancel_requested: bool = False
        self._worktree_created_this_run: bool = False
        self._failure_kind: FailureKind | None = None
        self._failure_detail: str = ""

        self._resolve_worker: Worker[BranchResolution] | None = None

    # -- composition ---------------------------------------------------

    def compose(self) -> ComposeResult:
        """Build the modal's dialog + step ContentSwitcher."""
        with Vertical(id="dialog"):
            yield Static(self._title_text(), id="wizard-title")
            with ContentSwitcher(initial="step-name", id="wizard-switcher"):
                with Vertical(id="step-name"):
                    yield Static("Enter session name, Esc to cancel", id="name-hint")
                    yield Input(placeholder="e.g., feature-auth", id="name-input")
                    yield Static("", id="name-error")
                    yield Static("", id="name-preview")
                with Vertical(id="step-branch"):
                    yield Static("", id="branch-status")
                    yield BranchListView(id="branch-list")
                with Vertical(id="step-provision"):
                    yield Static("", id="provision-body")

    def on_mount(self) -> None:
        """Focus the name input and kick off the background base resolution."""
        self._resolve_worker = self.run_worker(
            self._service.resolve_base, thread=True, name="resolve-default"
        )
        self.query_one("#name-input", Input).focus()

    # -- step 1: name ----------------------------------------------------

    def on_input_changed(self, event: Input.Changed) -> None:
        """Live slug preview as the user types the session name."""
        if event.input.id != "name-input":
            return
        validation = self._service.validate_name(event.value, set())
        preview = f"→ feature/{validation.slug}" if validation.slug else ""
        self.query_one("#name-preview", Static).update(preview)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Validate the name on Enter; advance to step 2 or show an inline error."""
        if event.input.id != "name-input":
            return
        validation = self._service.validate_name(event.value, self._existing_ids)
        if not validation.ok:
            self.query_one("#name-error", Static).update(
                validation.error or "invalid name"
            )
            return
        self._slug = validation.slug
        self.query_one("#name-error", Static).update("")
        await self._enter_branch_step()

    # -- step 2: base branch ----------------------------------------------

    async def _enter_branch_step(self) -> None:
        self._step = 2
        self._switch_step()
        status = self.query_one("#branch-status", Static)
        worker = self._resolve_worker
        if worker is not None and not worker.is_finished:
            status.update("resolving default…")
        if worker is not None:
            self._default_resolution = await worker.wait()
        await self._populate_branch_list()

    async def _populate_branch_list(self) -> None:
        default_branch = (
            self._default_resolution.branch if self._default_resolution else ""
        )
        candidates = self._service.branch_candidates()
        options: list[str] = []
        seen: set[str] = set()
        for branch in (default_branch, *candidates):
            if not branch or branch in seen:
                continue
            seen.add(branch)
            options.append(branch)
        self._branch_options = options

        list_view = self.query_one("#branch-list", BranchListView)
        await list_view.clear()
        await list_view.extend(ListItem(Label(branch)) for branch in options)
        list_view.index = 0 if options else None

        warnings = self._default_resolution.warnings if self._default_resolution else []
        self.query_one("#branch-status", Static).update("\n".join(warnings))
        list_view.focus()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Advance to provisioning with the highlighted branch."""
        if event.list_view.id != "branch-list":
            return
        index = event.list_view.index
        if index is not None and 0 <= index < len(self._branch_options):
            self._selected_branch = self._branch_options[index]
        await self._enter_provision_step()

    # -- step 3: provisioning ---------------------------------------------

    async def _enter_provision_step(self) -> None:
        self._step = 3
        self._switch_step()
        self.run_worker(self._run_provisioning, exclusive=True, group="provision")

    async def _run_provisioning(self) -> None:
        self._step3_mode = _Step3Mode.RUNNING
        self._cancel_requested = False
        self._step_marks = [_MARK_PENDING] * len(_STEP_NAMES)
        self._render_provision()

        for idx, step_name in enumerate(_STEP_NAMES):
            if self._cancel_requested:
                await self._cancel_and_dismiss()
                return
            self._step3_mode = _Step3Mode.RUNNING
            self._step_marks[idx] = _MARK_RUNNING
            self._render_provision()

            result = await self._exec_step(step_name)

            if self._cancel_requested:
                await self._cancel_and_dismiss()
                return
            if not result.ok:
                self._step_marks[idx] = _MARK_FAILED
                self._render_provision()
                self._enter_recovery(step_name, result.detail)
                return
            self._step_marks[idx] = _MARK_DONE
            self._render_provision()

        self._step3_mode = _Step3Mode.IDLE
        self.dismiss(self._build_result())

    async def _exec_step(self, step_name: str) -> StepResult:
        if step_name == "resolve_base":
            return await self._step_resolve_base()

        spec = self._spec
        if spec is None:
            raise RuntimeError("spec must be built by the resolve_base step")

        if step_name == "create_worktree":
            worker = self.run_worker(
                lambda: self._service.create_worktree(spec),
                thread=True,
                exclusive=True,
                group="provision-work",
            )
            result = await worker.wait()
            if result.ok and not result.resumed:
                self._worktree_created_this_run = True
            return result
        if step_name == "register_worktree":
            worker = self.run_worker(
                lambda: self._service.register_worktree(spec),
                thread=True,
                exclusive=True,
                group="provision-work",
            )
            return await worker.wait()
        if step_name == "acquire_lease":
            worker = self.run_worker(
                lambda: self._service.acquire_lease(spec),
                thread=True,
                exclusive=True,
                group="provision-work",
            )
            return await worker.wait()
        raise ValueError(f"unknown provisioning step: {step_name}")

    async def _step_resolve_base(self) -> StepResult:
        default_branch = (
            self._default_resolution.branch if self._default_resolution else ""
        )
        branch = self._selected_branch
        if branch and branch != default_branch:
            worker = self.run_worker(
                lambda: self._service.resolve_base(branch),
                thread=True,
                exclusive=True,
                group="provision-work",
            )
            resolution = await worker.wait()
        else:
            if self._default_resolution is None:
                raise RuntimeError("default resolution must be cached")
            resolution = self._default_resolution
        self._resolution = resolution
        self._spec = self._service.build_spec(self._slug, resolution)
        return StepResult(ok=True, detail=f"base: {resolution.base_ref}")

    def _build_result(self, *, kept_after_failure: bool = False) -> NewSessionResult:
        spec = self._spec
        if spec is None:
            raise RuntimeError("spec must exist before building a result")
        return NewSessionResult(
            slug=spec.slug,
            worktree_path=spec.worktree_path,
            branch=spec.branch,
            merge_target=spec.merge_target,
            kept_after_failure=kept_after_failure,
            failure_kind=(
                self._failure_kind.value
                if kept_after_failure and self._failure_kind is not None
                else ""
            ),
            failure_detail=self._failure_detail if kept_after_failure else "",
        )

    async def _cancel_and_dismiss(self) -> None:
        spec = self._spec
        if self._worktree_created_this_run and spec is not None:
            worker = self.run_worker(
                lambda: self._service.rollback_worktree(spec),
                thread=True,
                exclusive=True,
                group="provision-work",
            )
            await worker.wait()
        self.dismiss(None)

    # -- recovery (RAISE-16697) --------------------------------------------

    def _enter_recovery(self, step_name: str, detail: str) -> None:
        self._step3_mode = _Step3Mode.RECOVERY
        self._failure_kind = classify_failure(step_name, detail)
        self._failure_detail = detail
        self._render_provision()

    def action_recovery_choose_branch(self) -> None:
        """[b] Choose another branch — BAD_BASE_REF only, nothing on disk yet."""
        if (
            self._step3_mode != _Step3Mode.RECOVERY
            or self._failure_kind != FailureKind.BAD_BASE_REF
        ):
            return
        self.run_worker(self._back_to_branch_step, exclusive=True, group="provision")

    def action_recovery_retry(self) -> None:
        """[t] Retry as-is — re-run the full sequence (transient failures)."""
        if self._step3_mode != _Step3Mode.RECOVERY:
            return
        self.run_worker(self._run_provisioning, exclusive=True, group="provision")

    def action_recovery_rebase(self) -> None:
        """[e] Rebase and retry — STALE_BASE/NOT_READY/OTHER only."""
        if (
            self._step3_mode != _Step3Mode.RECOVERY
            or self._failure_kind == FailureKind.BAD_BASE_REF
        ):
            return
        self.run_worker(self._rebase_and_retry, exclusive=True, group="provision")

    def action_recovery_keep(self) -> None:
        """[k] Keep worktree — non-destructive exit, STALE_BASE/NOT_READY/OTHER only."""
        if (
            self._step3_mode != _Step3Mode.RECOVERY
            or self._failure_kind == FailureKind.BAD_BASE_REF
        ):
            return
        self.dismiss(self._build_result(kept_after_failure=True))

    def action_recovery_rollback(self) -> None:
        """[r] Rollback and choose another branch — STALE_BASE/NOT_READY/OTHER only."""
        if (
            self._step3_mode != _Step3Mode.RECOVERY
            or self._failure_kind == FailureKind.BAD_BASE_REF
        ):
            return
        self.run_worker(self._rollback_and_return, exclusive=True, group="provision")

    async def _rebase_and_retry(self) -> None:
        spec = self._spec
        if spec is None:
            raise RuntimeError("spec must exist to rebase")
        worker = self.run_worker(
            lambda: self._service.rebase_worktree(spec),
            thread=True,
            exclusive=True,
            group="provision-work",
        )
        result = await worker.wait()
        if not result.ok:
            self._failure_detail = result.detail
            self._render_provision()
            return
        await self._run_provisioning()

    async def _rollback_and_return(self) -> None:
        spec = self._spec
        if spec is None:
            raise RuntimeError("spec must exist to roll back")
        worker = self.run_worker(
            lambda: self._service.rollback_worktree(spec),
            thread=True,
            exclusive=True,
            group="provision-work",
        )
        await worker.wait()
        self._worktree_created_this_run = False
        self._step3_mode = _Step3Mode.IDLE
        self._failure_kind = None
        await self._back_to_branch_step()

    async def _back_to_branch_step(self) -> None:
        self._step = 2
        self._switch_step()
        await self._populate_branch_list()

    # -- Esc / cancel -------------------------------------------------------

    def action_cancel(self) -> None:
        """Esc — behaviour depends on which step/sub-state is active."""
        if self._step == 3:
            if self._step3_mode == _Step3Mode.RECOVERY:
                if self._failure_kind == FailureKind.BAD_BASE_REF:
                    self.dismiss(None)
                else:
                    self.action_recovery_keep()
                return
            if self._step3_mode == _Step3Mode.RUNNING:
                self._step3_mode = _Step3Mode.CONFIRM_CANCEL
                self._render_provision()
                return
            if self._step3_mode == _Step3Mode.CONFIRM_CANCEL:
                self._cancel_requested = True
                return
        self.dismiss(None)

    # -- rendering helpers ----------------------------------------------

    def _title_text(self) -> str:
        return f"New Session — step {self._step}/3"

    def _switch_step(self) -> None:
        switcher = self.query_one("#wizard-switcher", ContentSwitcher)
        switcher.current = {1: "step-name", 2: "step-branch", 3: "step-provision"}[
            self._step
        ]
        self.query_one("#wizard-title", Static).update(self._title_text())

    def _render_provision(self) -> None:
        lines: list[str] = [
            f"{mark} {label}"
            for mark, label in zip(self._step_marks, _STEP_LABELS, strict=True)
        ]
        if self._step3_mode == _Step3Mode.CONFIRM_CANCEL:
            lines.append("")
            lines.append("provisioning in progress — press Esc again to cancel")
        elif self._step3_mode == _Step3Mode.RECOVERY:
            lines.append("")
            lines.append(self._failure_detail)
            lines.append("")
            if self._failure_kind == FailureKind.BAD_BASE_REF:
                lines.append(
                    "[b] Choose another branch   [t] Retry as-is   [Esc] Cancel wizard"
                )
            else:
                lines.append(
                    "[e] Rebase and retry   [t] Retry as-is   "
                    "[k] Keep worktree   [r] Rollback and choose another branch"
                )
        self.query_one("#provision-body", Static).update("\n".join(lines))
