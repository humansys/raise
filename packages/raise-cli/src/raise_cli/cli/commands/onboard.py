"""CLI command: rai onboard — unified developer onboarding orchestrator.

Two paths:
  1. OIT web-first: --from-oit-token oit_xxx
     Exchange token → save ~/.rai/server.json → rai init (if slug) → bootstrap
     → emit transcript (Detected/Action/Next)
  2. Local-first OSS: (no token)
     Router: observe → decide → execute → re-observe → render transcript
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import httpx
import typer
from rich.console import Console

from raise_cli.cli.commands.connect import (
    _get_server_credentials_path,  # pyright: ignore[reportPrivateUsage]
    _save_credentials,  # pyright: ignore[reportPrivateUsage]
    bootstrap_after_connect,
)
from raise_cli.compat import get_self_invocation
from raise_cli.onboarding.router import (
    OnboardDecision,
    RepositorySignals,
    RouteKind,
    decide_route,
    observe_repository,
)

console = Console()
_DEFAULT_SERVER = "https://api.raise.sh"
_OIT_EXCHANGE_PATH = "/api/v2/auth/oit/exchange"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _stdin_is_tty() -> bool:
    """Return True when stdin is an interactive terminal."""
    return sys.stdin.isatty()


def _manifest_exists() -> bool:
    """Return True when .raise/manifest.yaml exists in the current directory."""
    return (Path.cwd() / ".raise" / "manifest.yaml").exists()


def _exchange_oit(server: str, token: str) -> dict[str, object]:
    """POST /api/v2/auth/oit/exchange. Raises typer.Exit on failure."""
    url = f"{server.rstrip('/')}{_OIT_EXCHANGE_PATH}"
    try:
        resp = httpx.post(url, json={"token": token}, timeout=30)
    except httpx.RequestError as exc:
        console.print(f"[red]Network error during OIT exchange:[/red] {exc}")
        raise typer.Exit(1) from None

    if resp.status_code == 410:
        console.print(
            "[red]Token expired or already used.[/red]\n"
            "Request a new magic link from [bold]raise.sh/onboard[/bold]"
        )
        raise typer.Exit(1)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        console.print(f"[red]OIT exchange failed ({resp.status_code}):[/red] {exc}")
        raise typer.Exit(1) from None

    return resp.json()  # type: ignore[no-any-return]


def _check_credential_overwrite(force: bool) -> None:
    """If ~/.rai/server.json exists, warn and prompt (or error in non-TTY).

    Raises typer.Exit(1) when user declines or is in non-TTY without --force.
    """
    import json

    creds_path = _get_server_credentials_path()
    if not creds_path.exists():
        return

    if force:
        return

    if not _stdin_is_tty():
        console.print(
            "[red]Existing credentials found in ~/.rai/server.json.[/red]\n"
            "Cannot overwrite in non-interactive mode.\n"
            "Use [bold]--force[/bold] to overwrite, or run [bold]rai connect[/bold] "
            "to update credentials interactively."
        )
        raise typer.Exit(1)

    # TTY: interactive confirm
    try:
        existing = json.loads(creds_path.read_text(encoding="utf-8"))
        org_name = existing.get("org_name", creds_path)
    except (OSError, json.JSONDecodeError):
        org_name = str(creds_path)

    confirmed = typer.confirm(
        f"Overwrite existing credentials for '{org_name}'?",
        default=False,
    )
    if not confirmed:
        console.print("[dim]Aborted — existing credentials kept.[/dim]")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Transcript renderer
# ---------------------------------------------------------------------------


def _render_transcript(detected: str, action: str, next_step: str) -> None:
    """Emit a single Detected/Action/Next transcript.

    Uses soft_wrap to avoid breaking paths or commands at terminal width.
    """
    console.print(f"Detected: {detected}", soft_wrap=True)
    console.print(f"Action:   {action}", soft_wrap=True)
    console.print(f"Next:     {next_step}", soft_wrap=True)


# ---------------------------------------------------------------------------
# Local path executor (router-based)
# ---------------------------------------------------------------------------


def _execute_local_path(project_root: Path) -> None:
    """Execute the router-based local onboarding path.

    Observe → decide → (execute child) → (re-observe postcondition) → render.
    Never trusts child exit code alone; postcondition verified from re-observed signals.
    """
    signals: RepositorySignals = observe_repository(project_root)
    decision: OnboardDecision = decide_route(signals)

    final_action = decision.action
    final_next = decision.next_step
    final_exit_code = decision.exit_code

    if decision.operation is not None:
        prefix = get_self_invocation()
        argv = prefix + list(decision.operation)
        result = subprocess.run(
            argv,
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            shell=False,
            check=False,
        )

        if result.returncode != 0:
            op_str = "rai " + " ".join(decision.operation)
            final_action = f"{op_str} failed (exit {result.returncode})"
            final_next = shlex.join(argv)
            final_exit_code = 1
            # Surface subprocess output so CI logs show the actual failure reason.
            for _stream in (result.stdout, result.stderr):
                if _stream:
                    console.print(_stream.decode("utf-8", errors="replace"))
        else:
            # Postcondition verification via re-observation — zero exit is not enough.
            # Re-observe uses the same mocked observe_repository in tests, making
            # postcondition verifiable without filesystem state.
            post_signals: RepositorySignals = observe_repository(project_root)
            postcondition_ok: bool
            if decision.route in (RouteKind.BROWNFIELD, RouteKind.GREENFIELD):
                postcondition_ok = post_signals.manifest_valid
            elif decision.route == RouteKind.UPGRADE:
                postcondition_ok = post_signals.skill_manifest_current
            else:
                postcondition_ok = True

            if not postcondition_ok:
                op_str = "rai " + " ".join(decision.operation)
                final_action = f"{op_str} completed but postcondition not met"
                final_next = shlex.join(argv)
                final_exit_code = 1
            elif decision.route == RouteKind.UPGRADE:
                # Re-observe to determine next step (grounding vs. ready)
                post_decision = decide_route(post_signals)
                final_next = post_decision.next_step

    _render_transcript(decision.detected, final_action, final_next)

    if final_exit_code != 0:
        raise typer.Exit(final_exit_code)


# ---------------------------------------------------------------------------
# OIT path
# ---------------------------------------------------------------------------


def _run_oit_path(token: str, server: str, no_bootstrap: bool, force: bool) -> None:
    """Execute the web-first OIT onboarding path."""
    _check_credential_overwrite(force)

    console.print(f"Exchanging OIT token with [bold]{server}[/bold]...")
    payload = _exchange_oit(server, token)

    api_key = str(payload.get("api_key", ""))
    server_url = str(payload.get("server_url", server))
    org_id = str(payload.get("org_id", ""))
    org_name = str(payload.get("org_name", ""))
    project_slug: str | None = payload.get("project_slug")  # type: ignore[assignment]
    if project_slug is not None:
        project_slug = str(project_slug)

    creds: dict[str, object] = {
        "server_url": server_url,
        "api_key": api_key,
        "org_id": org_id,
        "org_name": org_name,
    }
    _save_credentials(creds)
    console.print(f"[green]✓ Connected to {org_name}[/green]")

    # OIT scoped init — use strict self-invocation (RAISE-16346)
    oit_init_ran = False
    oit_init_failed = False
    if project_slug and not _manifest_exists():
        console.print(f"[dim]Initializing project '{project_slug}'...[/dim]")
        prefix = get_self_invocation()
        argv = prefix + ["init", "--slug", project_slug]
        result = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            shell=False,
            check=False,
        )
        oit_init_ran = True
        if result.returncode != 0:
            oit_init_failed = True

    bootstrap_after_connect(server_url, api_key, no_bootstrap=no_bootstrap)

    console.print()
    if project_slug is None:
        # No repository scoped in this token — direct user to run rai onboard inside repo
        _render_transcript(
            detected="organization connected; repository not scoped",
            action="no-op",
            next_step="enter the repository and run rai onboard",
        )
    elif oit_init_failed:
        # Scoped but init failed — show failure transcript
        prefix = get_self_invocation()
        rerun = shlex.join(prefix + ["init", "--slug", str(project_slug)])
        _render_transcript(
            detected=f"organization connected; project '{project_slug}' scope",
            action=f"rai init --slug {project_slug} failed",
            next_step=rerun,
        )
        raise typer.Exit(1)
    else:
        # Scoped — init ran, or manifest already existed (truthful no-op).
        # Re-observe to determine the real next step in either case.
        project_root = Path.cwd()
        signals = observe_repository(project_root)
        post_decision = decide_route(signals)

        # Truthful action: only claim "ran rai init" when it actually ran.
        if oit_init_ran:
            action = f"ran rai init --slug {project_slug}"
            detected = f"organization connected; project '{project_slug}' initialized"
        else:
            action = "project already initialized"
            detected = f"organization connected; project '{project_slug}' scope"

        # Never surface UPGRADE's next_step (/rai-session-start) without executing
        # the upgrade.  Surface the pending operation instead.
        if post_decision.route == RouteKind.UPGRADE:
            next_step = "rai upgrade"
        else:
            next_step = post_decision.next_step

        _render_transcript(detected=detected, action=action, next_step=next_step)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


def onboard_command(
    from_oit_token: Annotated[
        str | None,
        typer.Option(
            "--from-oit-token",
            help=(
                "One-time invitation token (oit_xxx) from raise.sh/onboard. "
                "Exchanges token for credentials, runs init if scoped, then bootstraps."
            ),
            metavar="TOKEN",
        ),
    ] = None,
    server: Annotated[
        str,
        typer.Option(
            "--server",
            "-s",
            help="RaiSE server URL (default: https://api.raise.sh)",
        ),
    ] = _DEFAULT_SERVER,
    no_bootstrap: Annotated[
        bool,
        typer.Option(
            "--no-bootstrap",
            help="Skip team knowledge sync after connect (useful in CI).",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help=(
                "Overwrite existing credentials without prompting. "
                "Required in non-TTY when --from-oit-token is used and "
                "~/.rai/server.json already exists."
            ),
        ),
    ] = False,
) -> None:
    r"""Unified developer onboarding — sets up RaiSE from zero to working session.

    Two modes:

    \b
    OIT (invitation) path — pass --from-oit-token:
      1. Exchange OIT for credentials
      2. Save ~/.rai/server.json
      3. Run rai init (if project scoped in token)
      4. Sync team knowledge

    \b
    Local-first (OSS) path — no token:
      1. Observe repository state (legacy scan, manifest, skill manifest, grounding)
      2. Route deterministically to exactly one action
      3. Execute action (if any) via strict self-invocation
      4. Re-observe postcondition; emit Detected/Action/Next transcript
    """
    if from_oit_token:
        _run_oit_path(from_oit_token, server, no_bootstrap, force)
    else:
        _execute_local_path(Path.cwd())
