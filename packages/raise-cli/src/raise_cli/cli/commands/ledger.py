"""CLI commands for the session ledger — cross-project self-surfacing store.

`ledger` is the live/canonical surface replacing `rai session journal`
(deprecated, RAISE-1433) for cross-project state: independent of the
fragile session-binding (path-equality across worktrees), persisted to the
global ``~/.rai/raise.db`` (RAISE-13146, O2).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.cli.error_handler import cli_error
from raise_cli.schemas.session_ledger import LedgerEntry, LedgerKind
from raise_cli.session.ledger import read_entries, render_sections, upsert_entry
from raise_cli.storage.connection import get_project_id

ledger_app = typer.Typer(
    name="ledger",
    help="Session ledger — cross-project self-surfacing store",
    no_args_is_help=True,
)


def _resolve_session_id() -> str:
    """Resolve session_id in-process — never via profile.active_sessions.

    Raises:
        typer.Exit: If the session id is not resolvable (fail-loud, AC7).
    """
    session_id = discover_agent_session_id()
    if not session_id:
        cli_error(
            "Could not resolve agent session_id — neither RAISE_AGENT_SESSION_ID, "
            "RAISE_CC_SESSION_ID, nor CLAUDE_CODE_SSE_PORT + matching "
            ".raise/rai/sessions/*/cc.port are available."
        )
        raise typer.Exit(1)
    return session_id


def _parse_fields(pairs: list[str]) -> dict[str, str]:
    """Parse repeated `-f key=value` pairs into a dict."""
    fields: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            cli_error(f"Invalid -f value (expected key=value): {pair!r}")
            raise typer.Exit(1)
        key, _, value = pair.partition("=")
        fields[key] = value
    return fields


@ledger_app.command()
def add(
    kind: Annotated[
        LedgerKind,
        typer.Option("--kind", help="Ledger section kind"),
    ],
    key: Annotated[
        str,
        typer.Option("--key", help="Natural key (upsert key within the session)"),
    ],
    fields: Annotated[
        list[str],
        typer.Option("-f", help="key=value field (repeatable)"),
    ] = [],  # noqa: B006
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project path"),
    ] = ".",
) -> None:
    """Upsert an entry in the session ledger.

    Examples:
        $ rai session ledger add --kind issue --key RAISE-13146 -f jira=RAISE -f status="In Progress"
        $ rai session ledger add --kind branch --key "raise-gtm:chore/x" -f repo=raise-gtm -f target=main
    """
    session_id = _resolve_session_id()
    project_path = Path(project).resolve()
    fields_dict = _parse_fields(fields)

    entry = LedgerEntry(
        session_id=session_id,
        kind=kind,
        natural_key=key,
        timestamp=datetime.now(UTC),
        project_id=get_project_id(project_path),
        fields=fields_dict,
    )
    upsert_entry(entry, project_path)
    typer.echo(f"Ledger upserted: {kind.value}:{key}")


@ledger_app.command()
def show(
    kind: Annotated[
        LedgerKind | None,
        typer.Option("--kind", help="Filter to a single kind"),
    ] = None,
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project path"),
    ] = ".",
    session: Annotated[
        str | None,
        typer.Option(
            "--session",
            help="Show a specific session's ledger (exact; no cross-session fallback)",
        ),
    ] = None,
) -> None:
    """Show the session ledger for the current (or an explicit) session.

    With ``--session X`` shows exactly X's entries — parity with
    ``rai session context --session`` for cross-session recovery (RAISE-13341).

    Examples:
        $ rai session ledger show
        $ rai session ledger show --kind friction
        $ rai session ledger show --session cc-uuid-x
    """
    session_id = session if session else _resolve_session_id()
    project_path = Path(project).resolve()

    entries = read_entries(session_id, project_path, kind=kind)
    if not entries:
        typer.echo("Ledger is empty.")
        return
    typer.echo(render_sections(entries))
