"""Main CLI application entry point."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Annotated, Literal

# Force UTF-8 stdio on Windows so rich can render box-drawing/check characters
# (✓, ─, etc.) without UnicodeEncodeError under cp1252. Equivalent to setting
# PYTHONUTF8=1 but applied at runtime so users don't have to configure env vars.
# Fixes RAISE-3743 (rai graph build exit 1 on ✓) and RAISE-3745 (rai adapter
# setup jira crash on preview ─). No-op on non-Windows.
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

import typer
from rich.console import Console

from raise_cli import __version__
from raise_cli.cartridges.cli import app as cartridge_app
from raise_cli.cli.commands.adapters import adapters_app
from raise_cli.cli.commands.auth import auth_app
from raise_cli.cli.commands.backlog import backlog_app
from raise_cli.cli.commands.base import base_app
from raise_cli.cli.commands.bot import bot_app
from raise_cli.cli.commands.connect import (
    connect_app,
    connect_command,
    load_cli_env,
    load_server_credentials,
)
from raise_cli.cli.commands.db import db_app
from raise_cli.cli.commands.dev import dev_app
from raise_cli.cli.commands.discover import discover_app
from raise_cli.cli.commands.distillation import distillation_app
from raise_cli.cli.commands.docs import docs_app
from raise_cli.cli.commands.doctor import doctor_app
from raise_cli.cli.commands.drift import drift_app
from raise_cli.cli.commands.fleet import fleet_app
from raise_cli.cli.commands.gate import gate_app
from raise_cli.cli.commands.governance import governance_app
from raise_cli.cli.commands.graph import graph_app
from raise_cli.cli.commands.impact import impact_app
from raise_cli.cli.commands.info import info_command
from raise_cli.cli.commands.init import init_command, purge_command, upgrade_command
from raise_cli.cli.commands.learn import learn_app
from raise_cli.cli.commands.manifest import manifest_app
from raise_cli.cli.commands.mcp import mcp_app
from raise_cli.cli.commands.memory import memory_app
from raise_cli.cli.commands.onboard import onboard_command
from raise_cli.cli.commands.pattern import pattern_app
from raise_cli.cli.commands.pipeline import pipeline_app
from raise_cli.cli.commands.portfolio import portfolio_app
from raise_cli.cli.commands.profile import profile_app
from raise_cli.cli.commands.project import project_app
from raise_cli.cli.commands.quality import quality_app
from raise_cli.cli.commands.release import release_app
from raise_cli.cli.commands.reliability import reliability_app
from raise_cli.cli.commands.repo import repo_app
from raise_cli.cli.commands.schema import schema_app
from raise_cli.cli.commands.scm import scm_app
from raise_cli.cli.commands.self_update import self_update_command
from raise_cli.cli.commands.session import session_app
from raise_cli.cli.commands.signal import signal_app
from raise_cli.cli.commands.skill import skill_app
from raise_cli.cli.commands.story import story_app
from raise_cli.cli.commands.telemetry import telemetry_app
from raise_cli.cli.commands.whoami import whoami_command
from raise_cli.cli.commands.worktree import worktree_app
from raise_cli.cli.extensions import discover_cli_extensions
from raise_cli.config import RaiSettings
from raise_cli.eval.cli import eval_app

# Module-level state for error handling
_current_output_format: Literal["human", "json", "table"] = "human"


def get_output_format() -> Literal["human", "json", "table"]:
    """Get the current output format.

    Returns:
        The output format string ("human", "json", or "table").
    """
    return _current_output_format


app = typer.Typer(
    name="rai",
    help="RaiSE CLI - Reliable AI Software Engineering",
    no_args_is_help=False,
    add_completion=False,
)

# Register command groups
app.add_typer(adapters_app, name="adapter")
app.add_typer(auth_app, name="auth")
app.add_typer(backlog_app, name="backlog")
app.add_typer(bot_app, name="bot")
app.add_typer(cartridge_app, name="cartridge")
app.add_typer(db_app, name="db")
app.add_typer(dev_app, name="dev")
app.add_typer(base_app, name="base")
app.add_typer(discover_app, name="discover")
app.add_typer(distillation_app, name="distillation")
app.add_typer(docs_app, name="docs")
app.add_typer(drift_app, name="drift")
app.add_typer(doctor_app, name="doctor")
app.add_typer(eval_app, name="eval")
# RAISE-15618: excluded from the 3.1 pitch, so excluded from `rai --help`.
# hidden=True CONCEALS ONLY — the code ships in the wheel and `rai fleet ...`
# stays fully invocable for internal team use. Removing it from the
# distribution is a product decision and is out of scope here.
app.add_typer(fleet_app, name="fleet", hidden=True)
app.add_typer(gate_app, name="gate")
app.add_typer(governance_app, name="governance")
app.add_typer(graph_app, name="graph")
app.add_typer(impact_app, name="impact")
app.add_typer(learn_app, name="learn")
app.add_typer(manifest_app, name="manifest")
app.add_typer(mcp_app, name="mcp")
app.add_typer(memory_app, name="memory")
app.add_typer(worktree_app, name="worktree")
app.add_typer(pattern_app, name="pattern")
app.add_typer(pipeline_app, name="pipeline")
# RAISE-15618: hidden for the same reason as `fleet` above — concealment, not
# removal. `rai portfolio ...` still works when invoked by name.
app.add_typer(portfolio_app, name="portfolio", hidden=True)
app.add_typer(profile_app, name="profile")
app.add_typer(project_app, name="project")
app.add_typer(quality_app, name="quality")
app.add_typer(reliability_app, name="reliability")
app.add_typer(release_app, name="release")
app.add_typer(repo_app, name="repo")
app.add_typer(scm_app, name="scm")
app.add_typer(schema_app, name="schema")
app.add_typer(session_app, name="session")
app.add_typer(signal_app, name="signal")
app.add_typer(story_app, name="story")
app.add_typer(skill_app, name="skill")
app.add_typer(telemetry_app, name="telemetry")

# Register standalone commands
app.command("info")(info_command)
connect_app.callback(invoke_without_command=True)(connect_command)
app.add_typer(connect_app, name="connect")
app.command("init")(init_command)
app.command("onboard")(onboard_command)
app.command("purge")(purge_command)
app.command("self-update")(self_update_command)
app.command("upgrade")(upgrade_command)
app.command("whoami")(whoami_command)

# Register CLI extensions from external packages
discover_cli_extensions(app)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""

    human = "human"
    json = "json"
    table = "table"


def version_callback(value: bool) -> None:  # noqa: ARG001
    """Print version and exit."""
    if value:
        console.print(f"raise-cli version {__version__}")
        raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[  # noqa: ARG001
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
    format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format (human, json, table)",
        ),
    ] = OutputFormat.human,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Increase verbosity (-v, -vv, -vvv)",
        ),
    ] = 0,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress non-error output",
        ),
    ] = False,
    mission: Annotated[
        str | None,
        typer.Option(
            "--mission",
            hidden=True,
            help="[cockpit] direct-mode: open this worktree/mission",
        ),
    ] = None,
    agent: Annotated[
        str | None,
        typer.Option(
            "--agent",
            hidden=True,
            help="[cockpit] direct-mode: use this agent",
        ),
    ] = None,
    last: Annotated[
        bool,
        typer.Option(
            "--last",
            hidden=True,
            help="[cockpit] direct-mode: relaunch last session",
        ),
    ] = False,
) -> None:
    """RaiSE CLI - Reliable AI Software Engineering governance framework.

    Global options apply to all commands and control output format and verbosity.
    """
    load_cli_env()
    load_server_credentials()

    global _current_output_format  # noqa: PLW0603
    _current_output_format = format.value  # type: ignore[assignment]

    # Calculate verbosity from flags
    verbosity = -1 if quiet else min(verbose, 3)

    # Create settings with CLI overrides (highest priority)
    settings = RaiSettings(
        output_format=format.value,  # type: ignore[arg-type]
        verbosity=verbosity,
    )

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings

    # Backward compatibility: keep individual values in ctx.obj
    # (Can be removed once all commands migrate to using settings)
    ctx.obj["format"] = format.value
    ctx.obj["verbosity"] = verbosity
    ctx.obj["quiet"] = quiet

    # Bare `rai` (no subcommand) → launch workspace cockpit
    if ctx.invoked_subcommand is None:
        from raise_cli.cockpit.app import run_cockpit

        run_cockpit(mission=mission, agent=agent, use_last=last)


if __name__ == "__main__":
    app()
