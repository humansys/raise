"""CLI commands: rai scm — local git/MR operations (RAISE-16772/3, RAISE-16777).

Every command here is local and git-only. The group used to carry a second
half — ``repos``/``branches``/``disconnect``/``create-pr``/``get-pr``, which
proxied through raise-server — and RAISE-16777 removed it: the ``ScmAdapter``
Protocol in ``raise_cli.scm`` replaces that path rather than coexisting with it
(epic D1). Nothing in this module may import ``raise_cli.adapters`` again;
``tests/cli/commands/test_scm.py`` enforces that over the parsed import graph.

``create-mr`` is the skill→adapter bridge (D-S3-2). Skills speak bash and the
adapter is Python; this command is the seam. It prints the MR URL and nothing
else on stdout, because the skill runs ``MR_URL=$(rai scm create-mr …)``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.config.paths import resolve_checkout_root
from raise_cli.scm import (
    DEFAULT_CI_POLL_INTERVAL_SECONDS,
    DEFAULT_CI_TIMEOUT_SECONDS,
    ScmAdapter,
    ScmConfigError,
    ScmError,
    from_manifest,
    wait_for_ci_status,
)
from raise_cli.scm.conflict_rules import (
    CONFIG_RELATIVE_PATH,
    ConflictConfigError,
    GitStateError,
    ResolutionReport,
    load_config,
    resolve_conflicts,
)
from raise_cli.scm.gitlab_adapter import GitLabAdapter
from raise_cli.scm.governance import append_governance_block, resolve_worktree
from raise_cli.session.resolver import resolve_session_id_optional

console = Console()
# Notices, warnings, and errors go here so stdout carries the MR URL alone.
err_console = Console(stderr=True)
scm_app = typer.Typer(help="Local SCM operations (conflict resolution, MRs).")

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_CONFLICTS_REMAIN = 2
# Distinct from EXIT_CONFIG_ERROR so a caller can tell "the tool broke" from
# "the tool worked and the answer was no". rai-mr-merge branches on this.
EXIT_CI_FAILED = 3


_UNRESOLVED_LABEL = {
    "no_matching_rule": "no matching rule",
    "union_not_implemented": (
        "strategy 'union' is not implemented — left for manual resolution"
    ),
    "checkout_failed": "git could not check out the requested side",
}


def _print_report(report: ResolutionReport) -> None:
    """Print one file per line, path first.

    The path leads and the rule/reason go on a continuation line so that rich's
    soft-wrapping at 80 columns cannot split a path across lines — these lines
    are read by humans mid-merge and, in tests, grepped for the path.
    """
    prefix = "Would resolve" if report.dry_run else "Resolved"
    for entry in report.resolved:
        console.print(f"[green]{prefix}[/green] ({entry.rule.strategy}): {entry.path}")
        detail = f"matched {entry.rule.pattern}"
        if entry.rule.reason:
            detail = f"{detail} — {entry.rule.reason}"
        console.print(f"  [dim]{detail}[/dim]")

    for unresolved in report.unresolved:
        console.print(f"[yellow]Unresolved[/yellow]: {unresolved.path}")
        console.print(f"  [dim]{_UNRESOLVED_LABEL[unresolved.reason]}[/dim]")


@scm_app.command("resolve-conflicts")
def resolve_conflicts_command(
    project: Annotated[
        Path | None,
        typer.Option(
            "--project", "-p", help="Repository root (default: this checkout)"
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Report what would be resolved, change nothing"),
    ] = False,
) -> None:
    """Auto-resolve merge conflicts declared in .raise/conflict-resolution.yaml.

    Run after a conflicted ``git merge origin/{target}`` on the source branch.
    Strategies are relative to that direction — a rebase inverts them and every
    resolution would be exactly wrong.

    Exit codes (rai-mr-create Step 2 branches on these):
      0  all conflicts resolved, none present, or no policy file
      1  the policy file exists but is invalid
      2  conflicts remain — resolve manually, `git add`, then commit
    """
    repo_root = (project or resolve_checkout_root()).resolve()
    config_path = repo_root / CONFIG_RELATIVE_PATH

    if not config_path.is_file():
        # Deliberately outranks the exit-2 rule: with no policy the command was
        # asked to do nothing, and any conflicts present belong to the developer
        # exactly as they did before this command existed (design D6).
        console.print(f"[dim]No {config_path} — nothing to auto-resolve.[/dim]")
        raise typer.Exit(EXIT_OK)

    try:
        config = load_config(repo_root)
        report = resolve_conflicts(repo_root=repo_root, config=config, dry_run=dry_run)
    except ConflictConfigError as exc:
        console.print(f"[red]ERROR {exc}[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR) from None
    except GitStateError as exc:
        console.print(f"[red]ERROR {exc}[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR) from None

    _print_report(report)

    resolved_count = len(report.resolved)
    remaining = len(report.unresolved)
    if not report.resolved and not report.unresolved:
        # The common Step 2 outcome: the merge was clean. Reporting it as
        # "all 0 conflicts resolved" reads like the command did something.
        console.print("[dim]No conflicts to resolve.[/dim]")
        raise typer.Exit(EXIT_OK)

    if report.all_resolved:
        console.print(
            f"[green]All conflicts resolved[/green] "
            f"({resolved_count} auto, 0 remaining)."
        )
        raise typer.Exit(EXIT_OK)

    console.print(
        f"[yellow]{resolved_count} auto-resolved, {remaining} remaining[/yellow] — "
        "resolve manually, then `git add` and commit."
    )
    raise typer.Exit(EXIT_CONFLICTS_REMAIN)


def _resolve_adapter(repo_root: Path) -> ScmAdapter:
    """Pick the provider adapter, falling back to GitLab when none is configured.

    D-S3-4: the library refuses to guess, but this repository (and every other
    one predating ``branches.scm``) has no provider configured and the shipped
    skill has always defaulted to GitLab. Failing here would break the flow this
    epic exists to improve, so the default lives at the edge — announced, on
    stderr, never silent. ``create-mr`` and ``merge-mr`` share this so the
    fallback is one decision rather than two that can drift.
    """
    try:
        return from_manifest(repo_root)
    except ScmConfigError as exc:
        err_console.print(f"[yellow]{exc}[/yellow]")
        err_console.print("[yellow]Defaulting to GitLab (shipped behaviour).[/yellow]")
        return GitLabAdapter()


@scm_app.command("create-mr")
def create_mr_command(
    title: Annotated[str, typer.Option("--title", help="Merge request title")],
    source: Annotated[str, typer.Option("--source", help="Source branch")],
    target: Annotated[str, typer.Option("--target", help="Target branch")],
    description: Annotated[
        str, typer.Option("--description", help="MR description (markdown)")
    ] = "",
    description_file: Annotated[
        Path | None,
        typer.Option("--description-file", help="Read the description from a file"),
    ] = None,
    harness: Annotated[
        str,
        typer.Option("--harness", help="Agent runtime, recorded in the rai metadata"),
    ] = "",
    session: Annotated[
        str | None,
        typer.Option("--session", help="Session id (default: $RAI_SESSION_ID)"),
    ] = None,
    project: Annotated[
        Path | None,
        typer.Option(
            "--project", "-p", help="Repository root (default: this checkout)"
        ),
    ] = None,
) -> None:
    """Create a merge request through the configured SCM adapter.

    Prints the MR URL — and only the MR URL — on stdout, so ``rai-mr-create``
    can capture it with ``MR_URL=$(rai scm create-mr …)``. Notices and errors go
    to stderr.

    The ``<!-- rai: … -->`` governance block (RAISE-15009) is appended here
    rather than by the caller. There is deliberately no flag to suppress it:
    before S3 it was bash in ten synced copies of a skill and could be skipped
    by forgetting a step, which is the gap D-S3-3 closes.
    """
    repo_root = (project or resolve_checkout_root()).resolve()

    if description_file is not None:
        try:
            description = description_file.read_text(encoding="utf-8")
        except OSError as exc:
            err_console.print(f"[red]ERROR cannot read {description_file}: {exc}[/red]")
            raise typer.Exit(EXIT_CONFIG_ERROR) from None

    adapter = _resolve_adapter(repo_root)

    full_description = append_governance_block(
        description,
        worktree=resolve_worktree(repo_root),
        harness=harness,
        session=resolve_session_id_optional(session, os.environ.get("RAI_SESSION_ID"))
        or "",
    )

    try:
        mr_url = adapter.create_mr(
            title=title,
            description=full_description,
            source_branch=source,
            target_branch=target,
        )
    except ScmError as exc:
        err_console.print(f"[red]ERROR {exc}[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR) from None

    # Bare print, not console.print: rich wraps long lines, and a wrapped URL
    # is a broken URL once the skill captures it.
    print(mr_url)


@scm_app.command("merge-mr")
def merge_mr_command(
    mr_url: Annotated[str, typer.Option("--mr-url", help="MR/PR URL to merge")],
    delete_source_branch: Annotated[
        bool,
        typer.Option(
            "--delete-source-branch/--no-delete-source-branch",
            help="Delete the source branch after merging (default: delete)",
        ),
    ] = True,
    no_ci_override: Annotated[
        bool,
        typer.Option(
            "--no-ci-override",
            help="Skip CI polling entirely (for repositories with no CI configured)",
        ),
    ] = False,
    poll_timeout: Annotated[
        int,
        typer.Option("--poll-timeout", help="Give up waiting for CI after N seconds"),
    ] = int(DEFAULT_CI_TIMEOUT_SECONDS),
    poll_interval: Annotated[
        int,
        typer.Option("--poll-interval", help="Seconds between CI status reads"),
    ] = int(DEFAULT_CI_POLL_INTERVAL_SECONDS),
    project: Annotated[
        Path | None,
        typer.Option(
            "--project", "-p", help="Repository root (default: this checkout)"
        ),
    ] = None,
) -> None:
    """Wait for CI to pass, then merge the merge request.

    The gate is fail-closed: anything other than a ``success`` verdict — a red
    pipeline, a cancelled one, or a timeout — blocks the merge. ``merge_mr()``
    is not reached, so there is no window in which a half-checked branch lands.

    ``--no-ci-override`` is the one bypass, and it is a *bypass*, not a smarter
    reading of CI: it skips the poll altogether. The Protocol reports "no CI
    configured" and "CI ran and failed" as the same ``failed`` (D-S4-3), so the
    only honest way to merge a CI-less repository is an explicit human opt-in.

    stdout stays empty; every message goes to stderr, mirroring ``create-mr``.

    Exit codes: 0 merged, 1 adapter/config error, 3 CI gate refused.
    """
    repo_root = (project or resolve_checkout_root()).resolve()
    adapter = _resolve_adapter(repo_root)

    if not no_ci_override:
        err_console.print(f"[dim]Waiting for CI on {mr_url}…[/dim]")
        status = wait_for_ci_status(
            adapter,
            mr_url=mr_url,
            timeout_seconds=float(poll_timeout),
            poll_interval_seconds=float(poll_interval),
        )
        if status != "success":
            err_console.print(
                f"[red]CI gate refused — status: {status}. Merge blocked.[/red]"
            )
            raise typer.Exit(EXIT_CI_FAILED)
        err_console.print("[green]CI passed.[/green]")

    try:
        adapter.merge_mr(mr_url=mr_url, delete_source_branch=delete_source_branch)
    except ScmError as exc:
        err_console.print(f"[red]ERROR {exc}[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR) from None

    err_console.print(f"[green]Merged.[/green] {mr_url}")
