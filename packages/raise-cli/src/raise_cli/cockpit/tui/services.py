"""New-session provisioning services (RAISE-16707, epic D5).

Pure business logic extracted from ``cockpit/app.py``'s
``_new_worktree_interactive()`` (lines 1748-1927) — no Rich, no
print/input, no ``cockpit/app.py`` import. All subprocess calls use
``capture_output=True``; output is returned in ``StepResult.detail`` for
inline display by the Textual screen, never written to stdout/stderr
(Textual owns the terminal).

Base-branch resolution is delegated to ``worktree.base_resolver``
(RAISE-15825 Regla 1) — this module never re-implements ``git branch -r``
parsing or manifest-default logic.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import webbrowser
from collections.abc import Collection, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote
from uuid import uuid4

from pydantic import BaseModel
from textual.binding import Binding

from raise_cli.cockpit.agent import DetectedAgent, detect_agents
from raise_cli.cockpit.env import build_exec_env
from raise_cli.cockpit.filter import fuzzy_filter
from raise_cli.cockpit.session_lease import acquire_session_lease, release_session_lease
from raise_cli.cockpit.sessions import SessionRow
from raise_cli.cockpit.types import SessionState, classify_session_state
from raise_cli.cockpit.worktree_ops import slugify
from raise_cli.schemas.journal import JournalEntry
from raise_cli.session.index import clear_active_session
from raise_cli.session.journal import read_journal
from raise_cli.storage.leases import SqliteLeaseStore
from raise_cli.storage.pause_states import SqlitePauseStore
from raise_cli.storage.worktrees import (
    SqliteWorktreeStore,
    Worktree,
    WorktreeNotFoundError,
)
from raise_cli.worktree.base_resolver import (
    list_branch_candidates,
    resolve_worktree_base,
)
from raise_core.workflow.status_sets import TERMINAL_STATUSES

_DETAIL_TAIL_CHARS = 2000


def _tail(text: str) -> str:
    """Trim a subprocess output blob to its last _DETAIL_TAIL_CHARS chars."""
    stripped = text.strip()
    return stripped[-_DETAIL_TAIL_CHARS:]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class NameValidation(BaseModel):
    """Result of validating a raw session-name input."""

    ok: bool
    slug: str = ""
    error: str | None = None


class BranchResolution(BaseModel):
    """Resolved base branch + ref, adapted from ``worktree.base_resolver``."""

    branch: str
    base_ref: str
    source: str
    local_sibling: bool
    warnings: list[str] = []


class ProvisionSpec(BaseModel):
    """Everything needed to provision one new worktree/session."""

    slug: str
    branch: str
    worktree_path: Path
    merge_target: str
    base_ref: str


class StepResult(BaseModel):
    """Outcome of one provisioning step."""

    ok: bool
    detail: str = ""
    resumed: bool = False


class AttachOutcome(BaseModel):
    """Outcome of attaching to (running) an agent subprocess (RAISE-16708)."""

    ok: bool
    exit_code: int = 0
    agent_name: str = ""
    detail: str = ""


class WorktreeCreateResult(BaseModel):
    """Outcome of a full ``NewSessionService.create_session()`` composition."""

    ok: bool
    spec: ProvisionSpec | None = None
    failed_step: str = ""
    detail: str = ""


class FailureKind(StrEnum):
    """Classification of a provisioning-step failure (RAISE-16697)."""

    BAD_BASE_REF = "bad_base_ref"
    STALE_BASE = "stale_base"
    NOT_READY = "not_ready"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------


def validate_session_name(raw: str, existing_ids: Collection[str]) -> NameValidation:
    """Validate + slugify a raw session-name input.

    Empty slug (e.g. all-punctuation input) is an error; a slug already
    present in *existing_ids* (worktree ids) is a duplicate error.
    """
    slug = slugify(raw)
    if not slug:
        return NameValidation(ok=False, error="invalid name")
    if slug in existing_ids:
        return NameValidation(ok=False, error=f"session '{slug}' already exists")
    return NameValidation(ok=True, slug=slug)


# ---------------------------------------------------------------------------
# Base-branch resolution (RAISE-15825 Regla 1 — thin adapters)
# ---------------------------------------------------------------------------


def resolve_base(repo_root: Path, explicit: str = "") -> BranchResolution:
    """Resolve the base branch/ref via the shared resolver."""
    resolved = resolve_worktree_base(repo_root, explicit_base=explicit)
    data = resolved.data
    return BranchResolution(
        branch=str(data["branch"]),
        base_ref=str(data["base_ref"]),
        source=str(data["source"]),
        local_sibling=bool(data["local_sibling"]),
        warnings=list(data.get("warnings", [])),
    )


def branch_candidates(repo_root: Path) -> list[str]:
    """Short list of candidate base branches (sibling worktrees, then recent local)."""
    return list_branch_candidates(repo_root)


def build_spec(repo_root: Path, slug: str, res: BranchResolution) -> ProvisionSpec:
    """Build the concrete provisioning spec for *slug* against *res*."""
    repo_name = repo_root.name
    branch = f"feature/{slug}"
    worktree_path = repo_root / ".worktree" / f"{repo_name}-{slug}"
    return ProvisionSpec(
        slug=slug,
        branch=branch,
        worktree_path=worktree_path,
        merge_target=res.branch,
        base_ref=res.base_ref,
    )


# ---------------------------------------------------------------------------
# Provisioning steps
# ---------------------------------------------------------------------------


def create_worktree(repo_root: Path, spec: ProvisionSpec) -> StepResult:
    """Create the git worktree, resuming a partial-state attempt if present.

    Ports the 3-case logic from ``_new_worktree_interactive()`` verbatim
    (gemba 1.6): worktree dir exists → resume; branch exists without a dir
    → checkout without ``-b``; fresh → ``-b {branch} {base_ref}``.
    """
    if spec.worktree_path.exists():
        return StepResult(
            ok=True,
            detail="worktree already exists (resuming registration)",
            resumed=True,
        )

    result = subprocess.run(
        [
            "git",
            "worktree",
            "add",
            str(spec.worktree_path),
            "-b",
            spec.branch,
            spec.base_ref,
        ],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    if result.returncode != 0 and f"'{spec.branch}'" in result.stderr:
        result = subprocess.run(
            ["git", "worktree", "add", str(spec.worktree_path), spec.branch],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
    if result.returncode != 0:
        return StepResult(ok=False, detail=_tail(result.stderr or result.stdout))
    return StepResult(ok=True, detail=_tail(result.stdout))


def register_worktree(repo_root: Path, spec: ProvisionSpec) -> StepResult:
    """Register + provision the worktree via the venv-local ``rai`` CLI.

    Never relies on the PATH ``rai`` — it may be an older install without
    the ``worktree`` subcommand (mirrors ``_new_worktree_interactive()``).
    """
    rai_cmd = str(Path(sys.executable).parent / "rai")
    result = subprocess.run(
        [
            rai_cmd,
            "worktree",
            "register",
            "--name",
            spec.slug,
            "--path",
            str(spec.worktree_path.resolve()),
            "--branch",
            spec.branch,
            "--merge-target",
            spec.merge_target,
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return StepResult(ok=False, detail=_tail(result.stderr or result.stdout))
    return StepResult(ok=True, detail=_tail(result.stdout))


def acquire_lease(repo_root: Path, spec: ProvisionSpec) -> StepResult:
    """Acquire a cockpit-held session lease so the row surfaces in the rail.

    ``acquire_session_lease()`` never raises — a held-by-other lease is a
    no-op ``ok=True`` (RAISE-16707 SD4: session open is not the place to
    hard-block).
    """
    store = SqliteLeaseStore(repo_root)
    acquired = acquire_session_lease(
        store, spec.slug, session_id=f"cockpit:{spec.slug}"
    )
    if acquired:
        return StepResult(ok=True, detail="lease acquired")
    return StepResult(
        ok=True, detail="worktree already leased by another session — skipped"
    )


def rollback_worktree(repo_root: Path, spec: ProvisionSpec) -> StepResult:
    """Remove the git worktree + branch (ports app.py:1902-1921).

    On partial failure, detail carries the manual cleanup commands instead
    of silently leaving the user without recourse.
    """
    rb_wt = subprocess.run(
        ["git", "worktree", "remove", "--force", str(spec.worktree_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    rb_br = subprocess.run(
        ["git", "branch", "-D", spec.branch],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if rb_wt.returncode == 0 and rb_br.returncode == 0:
        return StepResult(ok=True, detail="git worktree rolled back — no partial state")

    lines = ["rollback incomplete — clean up manually:"]
    if rb_wt.returncode != 0:
        lines.append(f"  git worktree remove --force {spec.worktree_path}")
    if rb_br.returncode != 0:
        lines.append(f"  git branch -D {spec.branch}")
    return StepResult(ok=False, detail="\n".join(lines))


def rebase_worktree(repo_root: Path, spec: ProvisionSpec) -> StepResult:
    """Fetch + rebase the worktree onto the latest merge target (recovery option 1)."""
    fetch = subprocess.run(
        ["git", "-C", str(spec.worktree_path), "fetch", "origin", spec.merge_target],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if fetch.returncode != 0:
        return StepResult(ok=False, detail=_tail(fetch.stderr or fetch.stdout))

    rebase = subprocess.run(
        ["git", "-C", str(spec.worktree_path), "rebase", f"origin/{spec.merge_target}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if rebase.returncode != 0:
        return StepResult(ok=False, detail=_tail(rebase.stderr or rebase.stdout))
    return StepResult(ok=True, detail=_tail(rebase.stdout))


# ---------------------------------------------------------------------------
# Failure classification (RAISE-16697)
# ---------------------------------------------------------------------------

_BAD_BASE_REF_MARKERS = (
    "invalid reference",
    "not a valid object name",
    "unknown revision",
)


def classify_failure(step: str, detail: str) -> FailureKind:
    """Classify a step failure so the screen can compute the right recovery menu.

    *step* gates which patterns apply: ``register`` failures are checked
    against the register-time guards (stale base / not-ready), everything
    else against the worktree-add-time bad-ref patterns (gemba 2 — the two
    failure points produce distinct, non-overlapping symptoms).
    """
    lowered = detail.lower()
    if step == "register_worktree":
        if "commits behind" in lowered:
            return FailureKind.STALE_BASE
        if "not-ready:" in lowered:
            return FailureKind.NOT_READY
        return FailureKind.OTHER
    if any(marker in lowered for marker in _BAD_BASE_REF_MARKERS):
        return FailureKind.BAD_BASE_REF
    return FailureKind.OTHER


# ---------------------------------------------------------------------------
# Service seam
# ---------------------------------------------------------------------------


class NewSessionServiceProtocol(Protocol):
    """Shape the ``NewSessionScreen`` depends on — fakes implement this in tests."""

    def validate_name(
        self, raw: str, existing_ids: Collection[str]
    ) -> NameValidation: ...

    def resolve_base(self, explicit: str = "") -> BranchResolution: ...

    def branch_candidates(self) -> list[str]: ...

    def build_spec(self, slug: str, res: BranchResolution) -> ProvisionSpec: ...

    def create_worktree(self, spec: ProvisionSpec) -> StepResult: ...

    def register_worktree(self, spec: ProvisionSpec) -> StepResult: ...

    def acquire_lease(self, spec: ProvisionSpec) -> StepResult: ...

    def rollback_worktree(self, spec: ProvisionSpec) -> StepResult: ...

    def rebase_worktree(self, spec: ProvisionSpec) -> StepResult: ...


class NewSessionService:
    """Thin class binding ``repo_root`` over the module-level step functions."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    @property
    def repo_root(self) -> Path:
        """Repository root this service operates against."""
        return self._repo_root

    def validate_name(self, raw: str, existing_ids: Collection[str]) -> NameValidation:
        """Validate + slugify a raw session-name input."""
        return validate_session_name(raw, existing_ids)

    def resolve_base(self, explicit: str = "") -> BranchResolution:
        """Resolve the base branch/ref via the shared resolver."""
        return resolve_base(self._repo_root, explicit)

    def branch_candidates(self) -> list[str]:
        """Short list of candidate base branches."""
        return branch_candidates(self._repo_root)

    def build_spec(self, slug: str, res: BranchResolution) -> ProvisionSpec:
        """Build the concrete provisioning spec for *slug* against *res*."""
        return build_spec(self._repo_root, slug, res)

    def create_worktree(self, spec: ProvisionSpec) -> StepResult:
        """Create the git worktree, resuming a partial-state attempt if present."""
        return create_worktree(self._repo_root, spec)

    def register_worktree(self, spec: ProvisionSpec) -> StepResult:
        """Register + provision the worktree via the venv-local ``rai`` CLI."""
        return register_worktree(self._repo_root, spec)

    def acquire_lease(self, spec: ProvisionSpec) -> StepResult:
        """Acquire a cockpit-held session lease so the row surfaces in the rail."""
        return acquire_lease(self._repo_root, spec)

    def rollback_worktree(self, spec: ProvisionSpec) -> StepResult:
        """Remove the git worktree + branch."""
        return rollback_worktree(self._repo_root, spec)

    def rebase_worktree(self, spec: ProvisionSpec) -> StepResult:
        """Fetch + rebase the worktree onto the latest merge target."""
        return rebase_worktree(self._repo_root, spec)

    def create_session(self, name: str, base_branch: str) -> WorktreeCreateResult:
        """Compose the full step sequence — the future concrete behind D1's protocol.

        Not used by ``NewSessionScreen`` (it needs step-granular calls for
        per-step progress UI — SD1); this is the coarse entry point S3 lifts
        the ``SessionLifecycle`` protocol out of.
        """
        validation = self.validate_name(name, ())
        if not validation.ok:
            return WorktreeCreateResult(
                ok=False,
                failed_step="validate_name",
                detail=validation.error or "invalid name",
            )
        resolution = self.resolve_base(base_branch)
        spec = self.build_spec(validation.slug, resolution)

        for step_name, step_fn in (
            ("create_worktree", self.create_worktree),
            ("register_worktree", self.register_worktree),
            ("acquire_lease", self.acquire_lease),
        ):
            step_result = step_fn(spec)
            if not step_result.ok:
                return WorktreeCreateResult(
                    ok=False,
                    spec=spec,
                    failed_step=step_name,
                    detail=step_result.detail,
                )
        return WorktreeCreateResult(ok=True, spec=spec)


# ---------------------------------------------------------------------------
# Session actions — attach + pause/resume (RAISE-16708, epic D3/D6/D7)
# ---------------------------------------------------------------------------

_ATTENTION_ORDER: dict[SessionState, int] = {
    SessionState.BLOCKED: 0,
    SessionState.ERROR: 1,
    SessionState.WORKING: 2,
    SessionState.PAUSED: 3,
    SessionState.IDLE: 4,
    SessionState.DONE: 5,
}


def classify_row(row: SessionRow) -> SessionState:
    """Single classify mapping for the rail (RAISE-16824, D-S6.3).

    Replaces the three byte-identical mirrors (``app.py:_classify_row``,
    ``session_rail.py:_classify_row``, this module's old
    ``_classify_for_sort``) — one function, real input wiring:

    - ``worktree_status`` comes from ``row.worktree.status`` when the row
      carries a worktree (registered/unregistered/orphan all flow through
      unchanged — only ``"closed"`` is special-cased and never reaches the
      rail, ``load_all_worktrees()`` filters it); defaults to ``"open"``
      for rows with no worktree (today's hardcoded value, preserved for
      every pre-existing fixture across the test suite).
    - ``pipeline_phase="none"`` iff the row never had a session
      (``session_id == "" and pid is None``) *and* carries a known
      worktree — the synthetic-IDLE branch (``merge_worktree_rows()``).
      Zombie pointers (a session that lost its lease) and main-checkout
      no-lease rows keep ``pipeline_phase=None`` → ERROR, unchanged.
    """
    never_had_session = (
        row.session_id == "" and row.pid is None and row.worktree is not None
    )
    return classify_session_state(
        worktree_status=row.worktree.status if row.worktree is not None else "open",
        lease_alive=row.pid is not None,
        heartbeat_age_hours=row.heartbeat_age_h,
        pipeline_phase="none" if never_had_session else None,
        paused=row.paused,
    )


def _worktree_age_hours(worktree: Worktree, now: datetime) -> float:
    """Hours since *worktree*'s ``created_at`` (D-S6.6) — 0.0 on a bad timestamp."""
    try:
        created = datetime.fromisoformat(worktree.created_at)
    except ValueError:
        return 0.0
    aware = created if created.tzinfo is not None else created.replace(tzinfo=UTC)
    return (now - aware).total_seconds() / 3600.0


def _synthetic_idle_row(worktree: Worktree, now: datetime) -> SessionRow:
    """A worktree with no session row (RAISE-16824, D-S6.6): IDLE, no lease."""
    return SessionRow(
        session_id="",
        name="(idle)",
        worktree_id=worktree.worktree_id,
        started=None,
        age_hours=_worktree_age_hours(worktree, now),
        state="DETACHED",
        pid=None,
        heartbeat_age_h=None,
        join="none",
        worktree=worktree,
    )


def merge_worktree_rows(
    worktrees: list[Worktree], session_rows: list[SessionRow]
) -> list[SessionRow]:
    """Worktree-primary rail rows: every worktree is a row; sessions enrich (D-S6.1).

    Pure — never touches I/O, does not mutate either input. Merge semantics
    (by ``worktree_id``):

    - session row whose ``worktree_id`` matches a worktree → enriched with
      that worktree (``row.worktree``); every matching session row is kept
      (a worktree can carry more than one, e.g. a stray lease-only row).
    - worktree with no matching session row → a synthetic IDLE row.
    - session row with no matching worktree (main checkout, stale pointer)
      → kept as-is, ``worktree=None`` — today's "(main)"/zombie behavior.
    """
    by_id = {wt.worktree_id: wt for wt in worktrees}
    matched_ids: set[str] = set()
    merged: list[SessionRow] = []

    for row in session_rows:
        worktree = by_id.get(row.worktree_id) if row.worktree_id else None
        if worktree is not None:
            matched_ids.add(row.worktree_id)
            merged.append(replace(row, worktree=worktree))
        else:
            merged.append(row)

    now = datetime.now(UTC)
    for worktree in worktrees:
        if worktree.worktree_id in matched_ids:
            continue
        merged.append(_synthetic_idle_row(worktree, now))

    return merged


def sort_rows_attention_first(rows: list[SessionRow]) -> list[SessionRow]:
    """Re-sort *rows* attention-first: BLOCKED, ERROR, WORKING, PAUSED, IDLE, DONE.

    Pure — returns a new list, does not mutate *rows*. Tie-break within a
    state matches ``collect_session_rows()``'s ``STATE_ORDER`` convention:
    ``-age_hours`` ascending.
    """
    return sorted(
        rows,
        key=lambda r: (_ATTENTION_ORDER[classify_row(r)], -r.age_hours),
    )


def select_agent(worktree_path: Path) -> DetectedAgent | None:
    """Return the first available detected agent (claude → codex → hermes → bash).

    ``bash`` is always present and always available (agent.py), so this
    only returns None if ``detect_agents()`` itself returns an empty list —
    unreachable in practice. No picker (E3 scope).
    """
    for agent in detect_agents(worktree_path):
        if agent.available:
            return agent
    return None


def run_agent(worktree_path: Path, agent: DetectedAgent) -> AttachOutcome:
    """Run *agent* to completion in the foreground, inheriting stdio.

    No ``capture_output`` and no ``os.chdir`` — stdio is inherited (the
    caller has already released the terminal via ``app.suspend()``) and
    ``cwd=`` keeps the cockpit's own working directory untouched (D7,
    unlike ``exec_agent()``'s ``os.chdir``).
    """
    launch_id = f"cockpit:{agent.cmd}:{uuid4().hex}"
    env = build_exec_env(
        worktree_path, agent_session_id=launch_id, agent_runtime=agent.cmd
    )
    try:
        result = subprocess.run(
            [agent.cmd, *agent.args], cwd=worktree_path, env=env, check=False
        )
    except FileNotFoundError:
        return AttachOutcome(ok=False, detail=f"agent not found: {agent.cmd}")
    return AttachOutcome(
        ok=True,
        exit_code=result.returncode,
        agent_name=agent.name,
        detail=f"{agent.name} exited ({result.returncode})",
    )


def renew_cockpit_lease(repo_root: Path, worktree_id: str) -> bool:
    """Refresh the cockpit's own lease heartbeat after an attach resumes (D7).

    Only renews when the lease is currently held by *this* process's PID —
    verifying the cockpit never lost lease ownership while the agent
    subprocess ran. Returns False (no hard failure) otherwise so the caller
    can surface a warning without blocking the resumed UI.
    """
    store = SqliteLeaseStore(repo_root)
    lease = store.get(worktree_id)
    if lease is None or lease.pid != os.getpid():
        return False
    return store.renew(worktree_id, session_id=lease.session_id)


def toggle_pause(repo_root: Path, worktree_id: str) -> bool:
    """Flip the persisted pause flag for *worktree_id* and return the new value."""
    return SqlitePauseStore(repo_root).toggle(worktree_id)


class SessionActionsProtocol(Protocol):
    """Shape the Textual app depends on for attach/pause — fakes implement this."""

    def select_agent(self, worktree_path: Path) -> DetectedAgent | None: ...

    def run_agent(self, worktree_path: Path, agent: DetectedAgent) -> AttachOutcome: ...

    def renew_cockpit_lease(self, worktree_id: str) -> bool: ...

    def toggle_pause(self, worktree_id: str) -> bool: ...


class SessionActionsService:
    """Thin class binding ``repo_root`` over the module-level session-action functions."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def select_agent(self, worktree_path: Path) -> DetectedAgent | None:
        """Return the first available detected agent for *worktree_path*."""
        return select_agent(worktree_path)

    def run_agent(self, worktree_path: Path, agent: DetectedAgent) -> AttachOutcome:
        """Run *agent* to completion in the foreground."""
        return run_agent(worktree_path, agent)

    def renew_cockpit_lease(self, worktree_id: str) -> bool:
        """Refresh the cockpit's lease heartbeat for *worktree_id*."""
        return renew_cockpit_lease(self._repo_root, worktree_id)

    def toggle_pause(self, worktree_id: str) -> bool:
        """Flip the persisted pause flag for *worktree_id*."""
        return toggle_pause(self._repo_root, worktree_id)


# ---------------------------------------------------------------------------
# Close flow — merge-state-aware lifecycle cleanup (RAISE-16709, D-S4.1/D-S4.2)
# ---------------------------------------------------------------------------


class CloseSafety(BaseModel):
    """Deterministic git-based safety signals for closing a worktree.

    Port of ``cockpit/app.py``'s ``_DeleteSafety`` (gemba 2) with a local
    tracking-ref probe instead of ``ls-remote`` (gemba 3, no network on the
    Textual main thread) and an explicit ``checked`` flag: any
    subprocess-level failure sets ``checked=False``, which the UI treats as
    unmerged/UNSAFE (fail-safe).
    """

    checked: bool = True
    dirty_files: int = 0
    unpushed_commits: int = 0
    unmerged_commits: int = 0
    remote_exists: bool = False

    @property
    def merged(self) -> bool:
        """True when git ran and there is nothing unmerged into the target."""
        return self.checked and self.unmerged_commits == 0

    @property
    def label(self) -> str:
        """SAFE | RISKY | UNSAFE, matching ``_DeleteSafety.label`` semantics."""
        if not self.checked:
            return "UNSAFE"
        if self.dirty_files > 0 or self.unmerged_commits > 0:
            return "UNSAFE"
        if self.unpushed_commits > 0 and not self.remote_exists:
            return "RISKY"
        return "SAFE"


def _run_git_capture(args: list[str]) -> str:
    """Run a git subprocess, returning stripped stdout or "" on any failure."""
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001 — fail-safe, caller treats "" as unknown
        return ""


def check_merge_state(path: Path, branch: str | None, merge_target: str) -> CloseSafety:
    """Assess how safe it is to close (soft-close or cleanup) a worktree.

    Local-only (gemba 3): the remote-existence check is a tracking-ref
    probe (``refs/remotes/origin/<branch>``), never ``git ls-remote``. All
    four checks are subprocess-git against *path*; a nonexistent path (or
    any other subprocess-level failure) yields ``checked=False`` rather
    than raising.
    """
    if not path.exists():
        return CloseSafety(checked=False)

    g = ["git", "-C", str(path)]

    dirty_out = _run_git_capture([*g, "status", "--short", "--porcelain"])
    dirty = len([ln for ln in dirty_out.splitlines() if ln.strip()])

    unpushed = 0
    if branch:
        out = _run_git_capture([*g, "rev-list", f"origin/{branch}..HEAD", "--count"])
        unpushed = int(out) if out.isdigit() else 0

    unmerged_out = _run_git_capture(
        [*g, "log", "HEAD", "--not", f"origin/{merge_target}", "--oneline"]
    )
    if not unmerged_out:
        unmerged_out = _run_git_capture(
            [*g, "log", "HEAD", "--not", merge_target, "--oneline"]
        )
    unmerged = len([ln for ln in unmerged_out.splitlines() if ln.strip()])

    remote_exists = False
    if branch:
        ref_out = _run_git_capture(
            [*g, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branch}"]
        )
        remote_exists = bool(ref_out)

    return CloseSafety(
        checked=True,
        dirty_files=dirty,
        unpushed_commits=unpushed,
        unmerged_commits=unmerged,
        remote_exists=remote_exists,
    )


def validate_force_close_name(typed: str, worktree_id: str) -> bool:
    """Strip-only, case-sensitive match of a typed confirmation against worktree_id."""
    return typed.strip() == worktree_id


class CloseRequest(BaseModel):
    """Everything ``close_session`` needs to tear down one worktree/session."""

    worktree_id: str
    session_id: str = ""
    path: Path
    branch: str | None = None


class CloseOutcome(BaseModel):
    """Outcome of a ``close_session`` call — one flag per PAT-T-442 step."""

    ok: bool
    detail: str = ""
    lease_released: bool = False
    pointer_cleared: bool = False
    pause_cleared: bool = False
    db_closed: bool = False
    worktree_removed: bool = False
    branch_deleted: bool = False


def close_session(repo_root: Path, req: CloseRequest, *, cleanup: bool) -> CloseOutcome:
    """Close *req*'s session, state-first then disk-last (PAT-T-442, D-S4.2).

    Steps 1-4 always run (soft close); step 5 (worktree + branch removal)
    only when ``cleanup=True``. A failed ``git worktree remove`` reports
    ``ok=False`` with manual-cleanup commands in ``detail`` — the state
    steps have already committed, so the row still leaves the rail
    regardless (gemba 5, risk table).
    """
    lease_released = False
    lease_store = SqliteLeaseStore(repo_root)
    lease = lease_store.get(req.worktree_id)
    if lease is not None:
        lease_released = release_session_lease(
            lease_store, req.worktree_id, lease.session_id
        )

    pointer_cleared = False
    if req.session_id:
        clear_active_session(session_id=req.session_id, project_root=repo_root)
        pointer_cleared = True

    SqlitePauseStore(repo_root).clear(req.worktree_id)
    pause_cleared = True

    db_closed = False
    try:
        SqliteWorktreeStore(repo_root).complete(req.worktree_id)
        db_closed = True
    except WorktreeNotFoundError:
        db_closed = False

    if not cleanup:
        return CloseOutcome(
            ok=True,
            lease_released=lease_released,
            pointer_cleared=pointer_cleared,
            pause_cleared=pause_cleared,
            db_closed=db_closed,
        )

    rm_wt = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "remove", "--force", str(req.path)],
        capture_output=True,
        text=True,
    )
    if rm_wt.returncode != 0:
        detail = (
            "worktree removal failed — clean up manually:\n"
            f"  git worktree remove --force {req.path}"
        )
        if req.branch:
            detail += f"\n  git branch -D {req.branch}"
        return CloseOutcome(
            ok=False,
            detail=detail,
            lease_released=lease_released,
            pointer_cleared=pointer_cleared,
            pause_cleared=pause_cleared,
            db_closed=db_closed,
        )

    branch_deleted = False
    if req.branch:
        rm_branch = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "-D", req.branch],
            capture_output=True,
            text=True,
        )
        branch_deleted = rm_branch.returncode == 0

    return CloseOutcome(
        ok=True,
        lease_released=lease_released,
        pointer_cleared=pointer_cleared,
        pause_cleared=pause_cleared,
        db_closed=db_closed,
        worktree_removed=True,
        branch_deleted=branch_deleted,
    )


class SessionCloseServiceProtocol(Protocol):
    """Shape the close flow depends on — fakes implement this in tests."""

    def check_merge_state(
        self, path: Path, branch: str | None, merge_target: str
    ) -> CloseSafety: ...

    def close_session(self, req: CloseRequest, *, cleanup: bool) -> CloseOutcome: ...


class SessionCloseService:
    """Thin class binding ``repo_root`` over the module-level close functions."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def check_merge_state(
        self, path: Path, branch: str | None, merge_target: str
    ) -> CloseSafety:
        """Assess how safe it is to close *path*'s worktree."""
        return check_merge_state(path, branch, merge_target)

    def close_session(self, req: CloseRequest, *, cleanup: bool) -> CloseOutcome:
        """Close *req*'s session, state-first then disk-last."""
        return close_session(self._repo_root, req, cleanup=cleanup)


# ---------------------------------------------------------------------------
# Filter mode + verb-on-selection (RAISE-16739, epic D5, D-S5.1/D-S5.3/D-S5.7)
# ---------------------------------------------------------------------------


def apply_filter(rows: list[SessionRow], query: str) -> list[SessionRow]:
    """Narrow *rows* by the rail label (D-S5.3); empty query returns rows unchanged.

    Reuses ``fuzzy_filter()`` verbatim (epic constraint) — never reimplemented.
    """
    return fuzzy_filter(rows, query, key=lambda r: r.worktree_id or r.name)


def _format_journal_line(entry: JournalEntry) -> str:
    """One compact line per journal entry: ``TIMESTAMP  TYPE  content``."""
    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M")
    entry_type = entry.entry_type.value.upper()
    return f"{timestamp}  {entry_type:<10} {entry.content}"


def journal_lines(worktree_path: Path, session_id: str, last_n: int = 50) -> list[str]:
    """Last *last_n* journal entries for *session_id*, oldest first, one per line.

    Returns [] when the session has no entries (screen shows a placeholder).
    """
    entries = read_journal(worktree_path, session_id, last_n=last_n)
    return [_format_journal_line(entry) for entry in entries]


_SSH_REMOTE_RE = re.compile(r"^[\w.-]+@([\w.-]+):(.+?)(\.git)?$")


def _normalize_gitlab_base(remote_url: str) -> str | None:
    """Normalize a git remote URL (ssh or https form) to its https base URL."""
    remote_url = remote_url.strip()
    if not remote_url:
        return None
    ssh_match = _SSH_REMOTE_RE.match(remote_url)
    if ssh_match:
        host, path = ssh_match.group(1), ssh_match.group(2)
        return f"https://{host}/{path}"
    if remote_url.startswith(("http://", "https://")):
        return remote_url.removesuffix(".git")
    return None


def mr_url(remote_url: str, branch: str) -> str | None:
    """GitLab MR-list URL for *branch*, or None when *remote_url* is unparseable.

    Built offline (no ``glab``, no network) — D-S5.7. ``source_branch`` is
    quoted with the default ``quote()`` safe set (keeps ``/`` readable).
    """
    base = _normalize_gitlab_base(remote_url)
    if base is None:
        return None
    return f"{base}/-/merge_requests?scope=all&state=all&source_branch={quote(branch)}"


def git_remote_url(worktree_path: Path, remote: str = "origin") -> str | None:
    """Read *remote*'s URL for *worktree_path* via git; None on any failure.

    Reuses ``_run_git_capture`` (5s timeout, fail-safe — gemba 3/D-S4.1
    precedent), never ``git ls-remote`` (no network on the Textual main
    thread).
    """
    out = _run_git_capture(
        ["git", "-C", str(worktree_path), "remote", "get-url", remote]
    )
    return out or None


# ---------------------------------------------------------------------------
# Expanded detail view (RAISE-16714, D-S4.3)
# ---------------------------------------------------------------------------


class PhaseEntry(BaseModel):
    """One phase's id + status in a pipeline run's track (RAISE-16714)."""

    id: str
    status: str  # pending|running|passed|failed|skipped|cancelled|done


class ExpandedDetail(BaseModel):
    """Full-screen situation report for the expanded view (RAISE-16714, D-S4.3)."""

    worktree_id: str
    branch: str
    merge_target: str = ""
    dirty_count: int = 0
    behind_count: int = 0
    path_exists: bool = True
    commits: list[str] = []
    mr_url: str | None = None
    pipeline_name: str = ""
    run_status: str = ""
    issue_id: str = ""
    phases: list[PhaseEntry] = []


def normalize_phases(run: dict[str, Any]) -> list[PhaseEntry]:
    """Shape-tolerant (engine dict / API list — gemba 2); unknown shapes → [].

    Engine-written runs persist ``phases`` as a dict keyed by phase id
    (insertion-ordered, i.e. pipeline order); API-written runs persist a
    list of ``{"id", "status"}`` entries. Anything else degrades to an
    empty track rather than raising.
    """
    raw = run.get("phases")
    if isinstance(raw, dict):
        return [
            PhaseEntry(id=pid, status=str((p or {}).get("status", "pending")))
            for pid, p in raw.items()
            if isinstance(p, dict)
        ]
    if isinstance(raw, list):
        return [
            PhaseEntry(id=str(p.get("id", "?")), status=str(p.get("status", "pending")))
            for p in raw
            if isinstance(p, dict)
        ]
    return []


_PHASE_GLYPHS: dict[str, str] = {
    "passed": "◆",
    "done": "◆",
    "running": "◐",
    "pending": "◇",
    "skipped": "◇",
    "failed": "✗",
    "cancelled": "✗",
}


def phase_glyph(status: str) -> str:
    """Pure glyph map for a phase status; unknown statuses fall to pending's ◇."""
    return _PHASE_GLYPHS.get(status, "◇")


def recent_commits(path: Path, n: int = 8) -> list[str]:
    """Last *n* commits as 'sha7 · message' strings — expanded view's own fetch.

    ``preview()``'s cached commits are capped at 3 (gemba 3); the expanded
    view wants ≥5 (target 8), so it fetches independently via the same
    fail-safe ``_run_git_capture`` helper.
    """
    out = _run_git_capture(["git", "-C", str(path), "log", "--oneline", f"-{n}"])
    return [
        f"{sha[:7]} · {rest}"
        for sha, _, rest in (ln.partition(" ") for ln in out.splitlines() if ln.strip())
    ]


def _select_run(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Newest non-terminal run, else the newest run, else None.

    *runs* is expected newest-first (``load_pipeline_overview()``'s
    ``started_at DESC`` ordering) — no re-sorting here.
    """
    for run in runs:
        if str(run.get("status", "")) not in TERMINAL_STATUSES:
            return run
    return runs[0] if runs else None


def build_expanded_detail(
    worktree: Worktree,
    preview: dict[str, object],
    runs: list[dict[str, Any]],
    remote_url: str | None,
) -> ExpandedDetail:
    """Pure composition of worktree + preview + pipeline-run data (D-S4.3).

    Never touches the filesystem or a database — all I/O happens in the
    caller (``SessionInfoService.expanded_detail()``).
    """
    run = _select_run(runs)
    dirty = preview.get("dirty_count", 0)
    behind = preview.get("behind_count", 0)
    path_exists = preview.get("path_exists", True)
    commits_raw = preview.get("commits", [])
    commits = list(commits_raw) if isinstance(commits_raw, list) else []
    return ExpandedDetail(
        worktree_id=worktree.worktree_id,
        branch=worktree.branch,
        merge_target=worktree.merge_target,
        dirty_count=dirty if isinstance(dirty, int) else 0,
        behind_count=behind if isinstance(behind, int) else 0,
        path_exists=path_exists if isinstance(path_exists, bool) else True,
        commits=commits,
        mr_url=mr_url(remote_url, worktree.branch) if remote_url else None,
        pipeline_name=str(run.get("pipeline_name", "")) if run else "",
        run_status=str(run.get("status", "")) if run else "",
        issue_id=str(run.get("issue_id", "")) if run else "",
        phases=normalize_phases(run) if run else [],
    )


class SessionInfoProtocol(Protocol):
    """Shape the Textual app depends on for `l`/`o`/`z` verbs — fakes implement this.

    Kept separate from ``SessionActionsProtocol`` (read-only info vs
    lifecycle mutation — D-S5.8, mirrors epic D1's SRP split).
    """

    def journal_lines(
        self, worktree_path: Path, session_id: str, last_n: int = 50
    ) -> list[str]: ...

    def mr_url(self, remote_url: str, branch: str) -> str | None: ...

    def open_url(self, url: str) -> bool: ...

    def expanded_detail(
        self, worktree: Worktree, preview: dict[str, object]
    ) -> ExpandedDetail: ...


class SessionInfoService:
    """Concrete ``SessionInfoProtocol`` — wraps journal/MR/browser primitives."""

    def journal_lines(
        self, worktree_path: Path, session_id: str, last_n: int = 50
    ) -> list[str]:
        """Last *last_n* journal entries for *session_id*, formatted one per line."""
        return journal_lines(worktree_path, session_id, last_n)

    def mr_url(self, remote_url: str, branch: str) -> str | None:
        """GitLab MR-list URL for *branch*, or None when unparseable."""
        return mr_url(remote_url, branch)

    def open_url(self, url: str) -> bool:
        """Open *url* in the default browser; False on any failure (fail-safe)."""
        try:
            return bool(webbrowser.open(url))
        except Exception:  # noqa: BLE001 — fail-safe, caller notifies
            return False

    def expanded_detail(
        self, worktree: Worktree, preview: dict[str, object]
    ) -> ExpandedDetail:
        """Assemble the expanded-view report for *worktree* (RAISE-16714, D-S4.3).

        Reads pipeline runs (read-only sqlite, fail-safe), a fresh 8-commit
        git log, and the origin remote — then delegates to the pure
        builder. Never raises: each read degrades independently.
        """
        from raise_cli.cockpit.pipeline_view import load_pipeline_overview

        path = Path(worktree.path)
        overview = load_pipeline_overview([worktree])
        runs = overview.runs_by_worktree.get(worktree.worktree_id, [])
        merged_preview = {**preview, "commits": recent_commits(path)}
        remote_url = git_remote_url(path)
        return build_expanded_detail(worktree, merged_preview, runs, remote_url)


# ---------------------------------------------------------------------------
# Help overlay + command palette (RAISE-16712, D-S2.3/D-S2.4)
# ---------------------------------------------------------------------------


class HelpContext(StrEnum):
    """Which group the app-computed context should highlight in HelpScreen."""

    RAIL = "rail"
    FILTER = "filter"


class HelpBinding(BaseModel):
    """One rendered row in a HelpScreen group — key + human description."""

    key: str
    description: str


_ACTION_GROUPS: dict[str, str] = {
    "cursor_down": "navigation",
    "cursor_up": "navigation",
    "select": "navigation",
    "deselect": "navigation",
    "new_session": "lifecycle",
    "attach": "lifecycle",
    "toggle_pause": "lifecycle",
    "close_session": "lifecycle",
    "filter": "filter",
    # everything else falls to "system"
}


def group_help_bindings(
    bindings: Sequence[Binding],
) -> dict[str, list[HelpBinding]]:
    """Group live Binding objects by intent; unknown actions fall to system (D-S2.3)."""
    groups: dict[str, list[HelpBinding]] = {
        "navigation": [],
        "lifecycle": [],
        "filter": [],
        "system": [],
    }
    for binding in bindings:
        group = _ACTION_GROUPS.get(binding.action, "system")
        groups[group].append(
            HelpBinding(key=binding.key, description=binding.description)
        )
    return groups


class Command(BaseModel):
    """One entry in the command-palette catalog (D-S2.4)."""

    name: str
    group: str
    description: str
    available: bool = True


COMMAND_CATALOG: list[Command] = [
    Command(
        name="go", group="navigation", description="Go to session", available=False
    ),
    Command(
        name="list", group="navigation", description="List sessions", available=False
    ),
    Command(name="new", group="lifecycle", description="Create new session"),
    Command(name="close", group="lifecycle", description="Close session"),
    Command(
        name="rebase", group="lifecycle", description="Rebase session", available=False
    ),
    Command(name="clear", group="filter", description="Clear filter"),
    Command(name="apply", group="filter", description="Apply filter", available=False),
    Command(name="help", group="system", description="Show help"),
    Command(name="refresh", group="system", description="Refresh sessions"),
    Command(name="quit", group="system", description="Quit cockpit"),
]


def match_commands(prefix: str) -> list[Command]:
    """Prefix match on command name; empty prefix returns the full catalog (D-S2.7)."""
    return [c for c in COMMAND_CATALOG if c.name.startswith(prefix)]


# ---------------------------------------------------------------------------
# Error recovery + resilience (RAISE-16713, epic D-S3.2/D-S3.3/D-S3.5)
# ---------------------------------------------------------------------------


class ErrorKind(StrEnum):
    """Classification of a rail-level or verb-failure error (D-S3.5)."""

    AGENT_CRASH = "agent_crash"
    GIT_FAILURE = "git_failure"
    STALE_BASE = "stale_base"
    DB_UNAVAILABLE = "db_unavailable"
    GENERIC = "generic"


class SessionError(BaseModel):
    """Explanation of a rail-level error, registered on ``CockpitApp`` (D-S3.2).

    ``diagnosed=True`` entries are recomputed every ``_refresh_rail()``
    (auto-diagnosed ERROR rows); ``diagnosed=False`` entries are verb
    failures that persist until dismissed, resolved, or their row
    disappears.
    """

    kind: ErrorKind
    worktree_id: str
    what_failed: str
    whats_safe: str = ""
    at_risk: str = ""
    last_good: str = ""
    detail: str = ""
    diagnosed: bool = False


class RecoveryAction(BaseModel):
    """One menu entry in a ``RecoveryMenu`` — action id + human label."""

    action_id: (
        str  # "relaunch" | "view_logs" | "close" | "retry" | "rebase" | "dismiss"
    )
    label: str


_RECOVERY_CATALOG: dict[ErrorKind, list[RecoveryAction]] = {
    ErrorKind.AGENT_CRASH: [
        RecoveryAction(action_id="relaunch", label="Relaunch agent"),
        RecoveryAction(action_id="view_logs", label="View logs"),
        RecoveryAction(action_id="close", label="Close session"),
        RecoveryAction(action_id="dismiss", label="Dismiss"),
    ],
    ErrorKind.GIT_FAILURE: [
        RecoveryAction(action_id="retry", label="Retry"),
        RecoveryAction(action_id="view_logs", label="View logs"),
        RecoveryAction(action_id="dismiss", label="Dismiss"),
    ],
    ErrorKind.STALE_BASE: [
        RecoveryAction(action_id="rebase", label="Rebase onto target"),
        RecoveryAction(action_id="retry", label="Retry provisioning"),
        RecoveryAction(action_id="dismiss", label="Dismiss"),
    ],
    ErrorKind.GENERIC: [
        RecoveryAction(action_id="view_logs", label="View logs"),
        RecoveryAction(action_id="dismiss", label="Dismiss"),
    ],
}


def recovery_actions(kind: ErrorKind) -> list[RecoveryAction]:
    """Menu for *kind*; DB_UNAVAILABLE is banner-only (D-S3.5) — falls to GENERIC.

    Returns a fresh copy so caller-side mutation never leaks into the
    shared catalog.
    """
    return list(_RECOVERY_CATALOG.get(kind, _RECOVERY_CATALOG[ErrorKind.GENERIC]))


def diagnose_error_row(row: SessionRow) -> SessionError:
    """Explain an ERROR-classified rail row (orphaned session) — pure."""
    return SessionError(
        kind=ErrorKind.AGENT_CRASH,
        worktree_id=row.worktree_id,
        what_failed="no live lease — agent or session process lost",
        whats_safe="worktree and branch intact on disk",
        at_risk="in-flight agent work since last heartbeat",
        last_good=(
            f"last heartbeat {row.heartbeat_age_h:.1f}h ago"
            if row.heartbeat_age_h is not None
            else "no heartbeat recorded"
        ),
        diagnosed=True,
    )


class SourceHealth(BaseModel):
    """Health signal exposed by a data source after ``refresh()`` (D-S3.3).

    Defaults to healthy so the app's tolerant ``_source_health()`` read
    stays fail-open for fakes/sources that predate this story.
    """

    ok: bool = True
    last_sync: datetime | None = None
    error: str = ""


def format_last_sync(last_sync: datetime | None, now: datetime) -> str:
    """Format a DegradedBanner age fragment: never / 45s ago / 2m ago / 1.5h ago."""
    if last_sync is None:
        return "never"
    aware = last_sync if last_sync.tzinfo is not None else last_sync.replace(tzinfo=UTC)
    seconds = max(0, (now - aware).total_seconds())
    if seconds < 60:
        return f"{int(seconds)}s ago"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)}m ago"
    hours = minutes / 60
    return f"{hours:.1f}h ago"
