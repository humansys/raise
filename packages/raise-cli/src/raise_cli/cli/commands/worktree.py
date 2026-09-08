"""CLI commands for worktree management.

Provides the ``rai worktree`` command group for registering and inspecting
git worktrees. All operations delegate to ``SqliteWorktreeStore`` — this
module is a thin CLI wrapper only.

Architecture: E4325 Parallel Worktrees Skill, S4325.1 / RAISE-4330
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli._agent_session import discover_agent_runtime, discover_agent_session_id
from raise_cli.config.paths import resolve_checkout_root
from raise_cli.output.symbols import CHECK
from raise_cli.project import resolve_project_root
from raise_cli.session.open_service import commits_behind
from raise_cli.storage.worktrees import (
    SqliteWorktreeStore,
    Worktree,
    WorktreeDuplicateError,
    WorktreeNotFoundError,
)
from raise_cli.workspace.readiness import evaluate_workspace_readiness
from raise_cli.worktree.provision import (
    WorktreeProvisioner,
    git_worktree_readiness_policy,
)
from raise_cli.worktree.prune import evaluate_candidate

_log = logging.getLogger(__name__)

worktree_app = typer.Typer(
    name="worktree",
    help="Manage RaiSE git worktrees — register, inspect, and close worktrees.",
    no_args_is_help=True,
)


# PAT-E-1090: force group routing even when only one command is registered
@worktree_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]
    """Internal stub — do not use."""


console = Console()
err_console = Console(stderr=True)

# A worktree correctly based on its merge target is ~0 commits behind it. One
# based on a stale branch (e.g. `main` when the merge target is release/3.1.0) is
# thousands behind — registering it leads to massive conflicts at MR time
# (RAISE-10713). 0 (not a git repo / no remote) never trips this guard.
_STALE_BASE_THRESHOLD = 100

_VALID_FIELDS = (
    "worktree_id",
    "branch",
    "merge_target",
    "stories",
    "status",
    "last_session_id",
    "path",
    "mission_id",
)


def _get_store() -> SqliteWorktreeStore:
    return SqliteWorktreeStore(project=resolve_checkout_root())


def _propagate_worktreeinclude(src_root: Path, dst_path: Path) -> None:
    """Propagate .worktreeinclude entries, printing warnings to console."""
    from raise_cli.worktree.provision import propagate_worktreeinclude

    _count, warnings = propagate_worktreeinclude(src_root, dst_path)
    for w in warnings:
        console.print(f"[yellow]WARN:[/yellow] {w}")


def _git_worktree_paths() -> list[Path]:
    """Return filesystem paths of all active git worktrees."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
    )
    return [
        Path(line.removeprefix("worktree ").strip())
        for line in result.stdout.splitlines()
        if line.startswith("worktree ")
    ]


def _field_value(wt: Worktree, field: str) -> str | None:
    return {
        "worktree_id": wt.worktree_id,
        "branch": wt.branch,
        "merge_target": wt.merge_target,
        "stories": ", ".join(wt.stories),
        "status": wt.status,
        "last_session_id": wt.last_session_id or "",
        "path": wt.path,
        "mission_id": wt.mission_id or "",
    }.get(field)


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def _provision_and_check_readiness(wt_path: Path, src_root: Path) -> None:
    """Run full provisioning and evaluate readiness; exit 1 if still not ready.

    Called by ``register`` on the default (no flags) path. Extracted to keep
    ``register`` below the C901 cyclomatic-complexity limit.

    Raises:
        typer.Exit(code=1): when the workspace has required findings after provisioning.
    """
    provisioner = WorktreeProvisioner(worktree_path=wt_path, repo_root=src_root)
    result = provisioner.provision()

    console.print(
        f"[green]{CHECK}[/green] Provisioned: "
        f"{result.files_propagated} files propagated, "
        f"hermes config {'written' if result.hermes_config_written else 'skipped'}"
    )
    for warning in result.warnings:
        console.print(f"  [yellow]WARN:[/yellow] {warning}")

    introduced_drift = result.introduced_drift
    if introduced_drift:
        for entry in introduced_drift:
            err_console.print(
                f"[red]not-ready:[/red] provision_introduced_git_drift: {entry}"
            )
        err_console.print(
            "[red]Error:[/red] provisioning introduced Git-visible drift."
        )
        raise typer.Exit(code=1)

    # Evaluate readiness after provisioning — exit nonzero if still not ready.
    report = evaluate_workspace_readiness(wt_path, git_worktree_readiness_policy())
    if not report.is_ready:
        for finding in report.required_findings:
            err_console.print(
                f"[red]not-ready:[/red] [{finding.code}] {finding.message}"
            )
        err_console.print(
            "[red]Error:[/red] workspace is not ready after provisioning — "
            "see findings above."
        )
        raise typer.Exit(code=1)


def _enforce_stale_base_guard(path: str, merge_target: str) -> None:
    """Refuse to register a worktree based on a stale branch (RAISE-10713).

    The development branch must be the base — a worktree cut from main while
    the merge target is release/3.1.0 is thousands of commits behind and
    produces massive conflicts at MR time. Raises ``typer.Exit(1)`` to block
    registration; returns normally (possibly after printing a WARN) otherwise.
    """
    # Fetch before measuring so origin/<merge_target> is current (RAISE-13753).
    # Failure is non-blocking — treat as INDETERMINATE, same as no-network.
    subprocess.run(
        ["git", "fetch", "origin", merge_target],
        capture_output=True,
        cwd=path,
    )
    behind = commits_behind(Path(path), f"origin/{merge_target}")
    # RAISE-14279: None is INDETERMINATE (ref/git unavailable), not "0 commits
    # behind". Fresh worktrees before the first `git fetch` are a legitimate
    # case — fail loud (visible warning), never fail closed.
    if behind is None:
        console.print(
            f"[yellow]WARN:[/yellow] could not evaluate commits-behind "
            f"'{merge_target}' (git unavailable or ref not fetched yet) — "
            "skipping the stale-base check."
        )
        return
    if behind > _STALE_BASE_THRESHOLD:
        err_console.print(
            f"[red]Error:[/red] worktree base is {behind} commits behind "
            f"'{merge_target}' — it looks based on a stale branch (e.g. 'main'). "
            f"Rebase the worktree onto the development branch before registering."
        )
        raise typer.Exit(code=1)


@worktree_app.command("register")
def register(
    name: Annotated[str, typer.Option("--name", help="Worktree identifier (slug)")],
    path: Annotated[
        str, typer.Option("--path", help="Filesystem path of the worktree")
    ],
    branch: Annotated[
        str, typer.Option("--branch", help="Git branch checked out in this worktree")
    ],
    merge_target: Annotated[
        str, typer.Option("--merge-target", help="Branch this worktree merges into")
    ],
    stories: Annotated[
        str | None,
        typer.Option(
            "--stories", help="Comma-separated Jira keys (e.g. RAISE-4330,RAISE-4331)"
        ),
    ] = None,
    mission: Annotated[
        str | None,
        typer.Option("--mission", help="Mission ID to bind this worktree to"),
    ] = None,
    update: Annotated[
        bool, typer.Option("--update", help="Update an existing registration")
    ] = False,
    propagate: Annotated[
        bool,
        typer.Option(
            "--propagate",
            help="Propagate .worktreeinclude entries. Only meaningful with --no-provision; full provisioning already includes propagation.",
        ),
    ] = False,
    no_provision: Annotated[
        bool,
        typer.Option(
            "--no-provision",
            help="Skip provisioning — register metadata only (recovery/escape hatch)",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview provisioning without writing files",
        ),
    ] = False,
) -> None:
    """Register a worktree with its merge target and associated stories.

    Provisioning runs by default: generates .hermes/config.yaml, .mcp.json,
    propagates .worktreeinclude files, and syncs skills. Pass --no-provision to
    register metadata only (recovery/escape hatch). Exit code is nonzero when
    provisioning completes but the workspace is still not ready.
    """
    store = _get_store()
    story_list = [s.strip() for s in stories.split(",") if s.strip()] if stories else []

    # Skip on --update (re-registration of a known worktree).
    if not update:
        _enforce_stale_base_guard(path, merge_target)

    # Best-effort agent attribution: never block provisioning on discovery errors.
    _agent_id: str = ""
    _harness: str = ""
    try:
        _agent_id = discover_agent_session_id() or ""
        _harness = discover_agent_runtime()
    except Exception as _exc:  # noqa: BLE001
        _log.debug("Agent attribution discovery failed (non-blocking): %s", _exc)

    def _do_register() -> Worktree:
        try:
            return store.register(
                name,
                path,
                branch,
                merge_target,
                story_list,
                mission_id=mission or "",
                update=update,
                agent_id=_agent_id,
                harness=_harness,
            )
        except WorktreeDuplicateError as e:
            err_console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1) from None

    wt_path = Path(path)

    if no_provision:
        wt = _do_register()
        if propagate:
            # --no-provision + --propagate: metadata-only registration + selective
            # file propagation. Full provisioning (config generation, venv, etc.) is
            # skipped — this is the escape-hatch path for recovery workflows.
            src_root = resolve_project_root()
            _propagate_worktreeinclude(src_root, wt_path)
        # --no-provision alone: pure metadata registration, nothing else to do.
    elif dry_run:
        wt = _do_register()
        provisioner = WorktreeProvisioner(
            worktree_path=wt_path, repo_root=resolve_project_root()
        )
        provisioner.provision(dry_run=True)
        console.print("[yellow]Dry run[/yellow] — no files written.")
    else:
        # Default: full provisioning + readiness check BEFORE registering
        # (RAISE-15910) — a provisioning failure must not leave an orphaned
        # DB row once the caller rolls back the git worktree itself.
        # --propagate is orthogonal: propagation is already included inside
        # _provision_and_check_readiness (WorktreeProvisioner.provision()),
        # so no separate step is needed here.
        _provision_and_check_readiness(wt_path, resolve_project_root())
        wt = _do_register()

    console.print(f"[green]{CHECK}[/green] Worktree '{wt.worktree_id}' registered.")
    console.print(f"  path:         {wt.path}")
    console.print(f"  branch:       {wt.branch}")
    console.print(f"  merge_target: {wt.merge_target}")
    if wt.stories:
        console.print(f"  stories:      {', '.join(wt.stories)}")
    if wt.mission_id:
        console.print(f"  mission_id:   {wt.mission_id}")


# ---------------------------------------------------------------------------
# resolve-base
# ---------------------------------------------------------------------------


@worktree_app.command("resolve-base")
def resolve_base(
    base: Annotated[
        str,
        typer.Option(
            "--base",
            help="Explicit base branch; omit to resolve from the manifest default",
        ),
    ] = "",
    work_type: Annotated[
        str,
        typer.Option(
            "--work-type",
            help="story | bugfix | feature | epic — selects the release-line routing rule",
        ),
    ] = "story",
    fix_version: Annotated[
        str | None,
        typer.Option(
            "--fix-version",
            help="Target a specific fix_versions[] entry across release_lines[]",
        ),
    ] = None,
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="human | json")
    ] = "human",
) -> None:
    """Resolve the base branch/ref for a new worktree — RAISE-15825 Regla 1.

    Single source of truth for base-branch resolution, called by the
    rai-worktree-open and rai-bugfix-start skills, and the cockpit's ``n``
    (new worktree) flow, so none re-implement fetch/resolve/sibling-detection
    logic inline:

    1. Explicit ``--base`` — used verbatim, no resolution.
    2. No ``--base`` — resolved via ``resolve_target()`` (RAISE-17066):
       env override > ``--fix-version`` mapping > ``--work-type`` default >
       FAIL LOUD. The target is declared in ``.raise/manifest.yaml``
       (``branches.release_lines[]`` / ``branches.development``), never
       inferred from ``origin/release/*``.
    3. If the resolved branch is currently checked out in a sibling
       worktree (possibly local-only/unpushed), bases directly off that
       local branch — no remote fetch, which could silently drop the
       sibling's unpushed commits.

    Exits 1 when the target is ambiguous (``status: blocked``) — e.g. an
    unknown ``--fix-version``. Otherwise never exits non-zero: worst case
    for a resolvable target is a warning (rule 4 — divergence at
    worktree-creation time is never a hard block).
    """
    from raise_cli.worktree.base_resolver import resolve_worktree_base

    project_path = Path(project).resolve()
    result = resolve_worktree_base(
        project_path, explicit_base=base, work_type=work_type, fix_version=fix_version
    )
    if output_format == "json":
        print(result.model_dump_json())
        if result.status == "blocked":
            raise typer.Exit(1)
        return
    if result.status == "blocked":
        console.print(f"[red]ERROR:[/red] {result.data['warnings'][0]}")
        raise typer.Exit(1)
    console.print(f"branch:        {result.data['branch']}")
    console.print(f"base_ref:      {result.data['base_ref']}")
    console.print(f"source:        {result.data['source']}")
    console.print(f"local_sibling: {result.data['local_sibling']}")
    for w in result.data.get("warnings", []):
        console.print(f"[yellow]WARN:[/yellow] {w}")


# ---------------------------------------------------------------------------
# context
# ---------------------------------------------------------------------------


@worktree_app.command("context")
def context(
    name: Annotated[
        str | None,
        typer.Option("--name", help="Worktree ID (default: auto-detect from CWD)"),
    ] = None,
    field: Annotated[
        str | None,
        typer.Option(
            "--field",
            help=f"Print a single field for scripting. Valid: {', '.join(_VALID_FIELDS)}",
        ),
    ] = None,
) -> None:
    """Show worktree context: branch, merge_target, stories, status.

    Without --name, resolves the current working directory against registered worktrees.
    Use --field <name> for single-value output suitable for shell scripts.
    """
    store = _get_store()
    try:
        wt = (
            store.get_by_name(name)
            if name
            else store.get_by_path(str(resolve_checkout_root()))
        )
    except WorktreeNotFoundError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    if field:
        value = _field_value(wt, field)
        if value is None:
            err_console.print(
                f"[red]Error:[/red] Unknown field '{field}'. "
                f"Valid: {', '.join(_VALID_FIELDS)}"
            )
            raise typer.Exit(code=1)
        print(value)
        return

    console.print(f"worktree_id:   {wt.worktree_id}")
    console.print(f"branch:        {wt.branch}")
    console.print(f"merge_target:  {wt.merge_target}")
    console.print(f"stories:       {', '.join(wt.stories) or '(none)'}")
    console.print(f"status:        {wt.status}")
    console.print(f"last_session:  {wt.last_session_id or '(none)'}")
    console.print(f"path:          {wt.path}")
    console.print(f"mission_id:    {wt.mission_id or '(none)'}")


# ---------------------------------------------------------------------------
# complete
# ---------------------------------------------------------------------------


@worktree_app.command("complete")
def complete(
    name: Annotated[str, typer.Option("--name", help="Worktree ID to mark as closed")],
) -> None:
    """Mark a worktree as complete (status → closed)."""
    store = _get_store()
    try:
        wt = store.complete(name)
    except WorktreeNotFoundError:
        if any(name in str(p) for p in _git_worktree_paths()):
            console.print(
                f"[yellow]WARN:[/yellow] Worktree '{name}' is not registered in RaiSE"
                " — already effectively closed."
            )
            raise typer.Exit(code=0) from None
        err_console.print(f"[red]Error:[/red] Worktree '{name}' not found.")
        raise typer.Exit(code=1) from None
    console.print(
        f"[green]{CHECK}[/green] Worktree '{wt.worktree_id}' marked as closed."
    )


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@worktree_app.command("list")
def list_worktrees(
    all_worktrees: Annotated[
        bool,
        typer.Option("--all", help="Include closed worktrees"),
    ] = False,
) -> None:
    """List worktrees for the current project."""
    store = _get_store()
    worktrees = store.list_worktrees(include_closed=all_worktrees)

    if not worktrees:
        suffix = "" if all_worktrees else " (use --all to include closed)"
        console.print(f"No worktrees found{suffix}.")
        return

    table = Table(show_header=True)
    table.add_column("NAME", style="bold")
    table.add_column("BRANCH")
    table.add_column("MERGE TARGET")
    table.add_column("STORIES")
    table.add_column("STATUS")

    for wt in worktrees:
        table.add_row(
            wt.worktree_id,
            wt.branch,
            wt.merge_target,
            ", ".join(wt.stories) or "(none)",
            wt.status,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# prune
# ---------------------------------------------------------------------------


@worktree_app.command("prune")
def prune(
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            help="Execute deletions. Without this flag, prune only previews "
            "candidates and makes no changes (dry-run).",
        ),
    ] = False,
) -> None:
    """Delete merged/stale worktrees and their branches.

    A worktree is only pruned when its branch is merged into its registered
    merge_target, its tree is clean (no uncommitted changes, no stashes),
    and it has no unpushed commits. The worktree currently running this
    command is never a candidate. Dry-run by default — pass --yes to
    actually run `git worktree remove` / `git branch -d` and close the
    RaiSE registration.
    """
    store = _get_store()
    repo = resolve_project_root()
    current_path = Path.cwd()

    worktrees = store.list_worktrees()
    if not worktrees:
        console.print("No open worktrees found.")
        return

    decisions = [
        (wt, evaluate_candidate(wt, repo=repo, current_path=current_path))
        for wt in worktrees
    ]

    table = Table(show_header=True)
    table.add_column("NAME", style="bold")
    table.add_column("BRANCH")
    table.add_column("DECISION")
    table.add_column("REASON")
    for wt, decision in decisions:
        if decision.safe:
            table.add_row(wt.worktree_id, wt.branch, "[green]PRUNE[/green]", "")
        else:
            table.add_row(
                wt.worktree_id,
                wt.branch,
                "[yellow]SKIP[/yellow]",
                "; ".join(decision.reasons),
            )
    console.print(table)

    safe_candidates = [wt for wt, decision in decisions if decision.safe]

    if not yes:
        if safe_candidates:
            console.print(
                f"\n[yellow]Dry run[/yellow] — {len(safe_candidates)} "
                "candidate(s) would be pruned. Re-run with --yes to execute."
            )
        else:
            console.print(
                "\n[yellow]Dry run[/yellow] — no candidates are safe to prune."
            )
        return

    for wt in safe_candidates:
        # Order matters: git worktree remove -> git branch -d -> store.complete().
        # If remove fails, skip the rest for this candidate entirely so the DB
        # never says "closed" while the directory still exists (RAISE-11104 AR Q4).
        remove = subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", wt.path],
            capture_output=True,
            text=True,
        )
        if remove.returncode != 0:
            err_console.print(
                f"[red]Error:[/red] failed to remove worktree "
                f"'{wt.worktree_id}': {remove.stderr.strip()}"
            )
            continue

        branch_del = subprocess.run(
            ["git", "-C", str(repo), "branch", "-d", wt.branch],
            capture_output=True,
            text=True,
        )
        if branch_del.returncode != 0:
            err_console.print(
                f"[red]Error:[/red] worktree '{wt.worktree_id}' removed but "
                f"failed to delete branch '{wt.branch}': {branch_del.stderr.strip()}"
            )
            continue

        store.complete(wt.worktree_id)
        console.print(
            f"[green]{CHECK}[/green] Pruned '{wt.worktree_id}' "
            f"(branch '{wt.branch}' deleted)."
        )
