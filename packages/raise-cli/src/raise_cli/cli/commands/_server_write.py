"""Shared server-write confirmation gate (RAISE-9821).

Echoes the resolved write target (org + url) and asks for confirmation before
any command writes to raise-server, so data never silently lands in the wrong
org after server.json changes between operations. ``--yes``/``-y`` skips the
prompt (CI/scripts) but STILL echoes the target.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from raise_cli.config.org_binding import get_bound_org
from raise_cli.config.server import ServerTarget, get_server_target

console = Console()


def confirm_server_write(
    action: str,
    *,
    yes: bool,
    project_root: Path | None = None,
    allow_org_mismatch: bool = False,
) -> ServerTarget:
    """Echo the target org/url and confirm before a server write.

    Exits(1) when the server is unconfigured or the user declines. Returns the
    ``ServerTarget`` so callers reuse the exact credentials that were echoed —
    the echoed target and the write target can never diverge.

    When ``project_root`` is given and the project is bound to an org whose id
    does not match the active target, the write is refused (RAISE-9823) unless
    ``allow_org_mismatch`` is set. This is the structural net for the cross-org
    contamination incident (RAISE-11075): server.json switching to another org's
    key must not silently land data in the wrong org.
    """
    target = get_server_target()
    if target is None:
        console.print(
            "[red]Error:[/red] Server not configured — run 'rai connect <org>' "
            "or set RAISE_SERVER_URL + RAISE_API_KEY."
        )
        raise typer.Exit(1)
    if project_root is not None and not allow_org_mismatch:
        bound = get_bound_org(project_root)
        if bound is not None:
            bound_name, bound_id = bound
            if target.org_id and bound_id != target.org_id:
                active = target.org_name or "(unknown org)"
                console.print(
                    f"[red]✗[/red] Project bound to '{bound_name}' but active org "
                    f"is '{active}'. Run 'rai connect' to switch org, or pass "
                    f"--allow-org-mismatch to override."
                )
                raise typer.Exit(1)
    org = target.org_name or "(unknown org)"
    short_id = target.org_id[:8] if target.org_id else ""
    suffix = f" ({short_id})" if short_id else ""
    console.print(f"→ Target: org '{org}'{suffix} @ {target.server_url}")
    if not yes and not typer.confirm(f"Continue with {action}?", default=False):
        console.print("Aborted.")
        raise typer.Exit(1)
    return target
