"""CLI app for daemon lifecycle — registered as `rai daemon`."""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import time
from pathlib import Path  # noqa: TC003 — used at runtime by typer
from typing import Annotated

import typer

from rai_agent.daemon import pid as pid_mod

app = typer.Typer(
    name="daemon",
    help="Manage the rai-agent daemon lifecycle.",
    no_args_is_help=True,
)

_RAI_DIR = Path(".rai")
_STOP_TIMEOUT = 10  # seconds before SIGKILL


def _pid_path() -> Path:
    """Return the PID file path."""
    return _RAI_DIR / "daemon.pid"


def _log_path() -> Path:
    """Return the log file path."""
    return _RAI_DIR / "daemon.log"


def _wait_for_exit(target_pid: int, timeout: int = _STOP_TIMEOUT) -> bool:
    """Wait for a process to exit, returning True if it exited."""
    for _ in range(timeout * 10):
        if not pid_mod.is_alive(target_pid):
            return True
        time.sleep(0.1)
    return False


def _run_foreground(
    config: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Run daemon in foreground by calling __main__.main() directly."""
    from rai_agent.daemon.__main__ import main

    argv: list[str] = []
    if config:
        argv.extend(["--config", config])
    argv.extend(["--host", host, "--port", str(port)])
    main(argv)


@app.command()
def start(
    config: Annotated[
        str | None,
        typer.Option("--config", "-c", help="Path to YAML config file"),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="Host to bind to"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind to"),
    ] = 8000,
) -> None:
    """Start the daemon in the background."""
    import dotenv

    # Load .env
    dotenv.load_dotenv(".env")

    # Build subprocess environment (PAT-E-001: remove CLAUDECODE)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    # Build command
    cmd = [sys.executable, "-m", "rai_agent.daemon"]
    if config:
        cmd.extend(["--config", config])
    cmd.extend(["--host", host, "--port", str(port)])

    # Ensure log directory exists
    lf = _log_path()
    lf.parent.mkdir(parents=True, exist_ok=True)

    # Launch daemon
    with lf.open("a") as log_fh:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=log_fh,
            stderr=log_fh,
            start_new_session=True,
        )

    # Atomic PID acquisition (R1: eliminates TOCTOU race)
    pf = _pid_path()
    existing = pid_mod.acquire_pid(process.pid, pf)
    if existing is not None:
        # Another instance won the race — kill ours
        process.terminate()
        typer.echo(f"⚠ Daemon already running (PID {existing})")
        return

    typer.echo(f"✓ Daemon started (PID {process.pid})")
    typer.echo(f"  Logs: {lf}")


@app.command()
def stop() -> None:
    """Stop the running daemon."""
    pf = _pid_path()
    existing = pid_mod.read_pid(pf)
    if existing is None:
        typer.echo("○ No daemon running")
        return

    try:
        os.kill(existing, signal.SIGTERM)
    except ProcessLookupError:
        # Process died between read_pid and kill
        typer.echo(f"✓ Daemon already exited (PID {existing})")
        pid_mod.remove(pf)
        return

    if _wait_for_exit(existing):
        typer.echo(f"✓ Daemon stopped (PID {existing})")
    else:
        # SIGKILL fallback
        with contextlib.suppress(ProcessLookupError):
            os.kill(existing, signal.SIGKILL)
        typer.echo(f"✓ Daemon killed (PID {existing})")

    pid_mod.remove(pf)


@app.command()
def restart(
    config: Annotated[
        str | None,
        typer.Option("--config", "-c", help="Path to YAML config file"),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="Host to bind to"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind to"),
    ] = 8000,
) -> None:
    """Restart the daemon (stop + start)."""
    stop()
    start(config=config, host=host, port=port)


@app.command()
def status() -> None:
    """Check if the daemon is running."""
    pf = _pid_path()
    existing = pid_mod.read_pid(pf)
    if existing is not None:
        typer.echo(f"● Daemon running (PID {existing})")
    else:
        typer.echo("○ Daemon not running")


@app.command()
def run(
    config: Annotated[
        str | None,
        typer.Option("--config", "-c", help="Path to YAML config file"),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="Host to bind to"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind to"),
    ] = 8000,
) -> None:
    """Run the daemon in the foreground (Ctrl+C to stop)."""
    _run_foreground(config=config, host=host, port=port)


@app.command()
def logs(
    lines: Annotated[
        int,
        typer.Option("--lines", "-n", help="Number of lines to show"),
    ] = 50,
    follow: Annotated[
        bool,
        typer.Option("--follow", "-f", help="Follow log output"),
    ] = False,
) -> None:
    """View daemon log output."""
    lf = _log_path()
    if not lf.exists():
        typer.echo(f"No log file at {lf}")
        raise typer.Exit(1)

    cmd = ["tail"]
    if follow:
        cmd.append("-f")
    cmd.extend(["-n", str(lines), str(lf)])
    subprocess.run(cmd, check=False)
