"""CLI commands for worktree-isolated dev stacks.

Provides ``rai dev up`` to orchestrate a full development stack
(PostgreSQL + raise-server + raise-admin) with dynamic ports per worktree.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.dev.compose import (
    generate_compose,
    get_compose_project_name,
    get_worktree_slug,
    write_compose_file,
)
from raise_cli.dev.config import DevConfig
from raise_cli.dev.env import generate_env_content, write_env_file
from raise_cli.dev.ports import allocate_ports
from raise_cli.dev.processes import is_running, kill_process, read_pid, start_process
from raise_cli.dev.reaper import reap_idle
from raise_cli.dev.status import discover_stacks

dev_app = typer.Typer(
    name="dev",
    help="Manage worktree-isolated dev stacks — up, down, status.",
    no_args_is_help=True,
)

console = Console()

_POSTGRES_HEALTH_TIMEOUT = 30
_POSTGRES_HEALTH_INTERVAL = 2


def _check_docker() -> None:
    """Verify Docker is installed and accessible."""
    if shutil.which("docker") is None:
        console.print("[red]Docker is not installed or not in PATH.[/red]")
        console.print("Install Docker: https://docs.docker.com/get-docker/")
        raise typer.Exit(1)


def _check_not_running(worktree_path: Path) -> None:
    """Verify no dev stack is already running for this worktree."""
    for service in ("server", "vite"):
        pid = read_pid(worktree_path, service)
        if pid is not None and is_running(pid):
            console.print(
                f"[red]Stack already running (PID {pid} for {service}).[/red]"
            )
            console.print("Run [bold]rai dev down[/bold] first.")
            raise typer.Exit(1)


def _check_no_containers(worktree_path: Path) -> None:
    """Abort if containers for this worktree's compose project are alive.

    Source of truth: live docker daemon. Docker absent / daemon unreachable
    -> graceful no-op (no container can collide if there is no docker).
    """
    slug = get_worktree_slug(worktree_path)
    project_name = get_compose_project_name(slug)
    try:
        result = subprocess.run(  # noqa: S603, S607
            [
                "docker",
                "ps",
                "--filter",
                f"label=com.docker.compose.project={project_name}",
                "-q",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, PermissionError):
        return  # graceful: no docker -> no container collision
    if result.returncode != 0:
        return  # daemon unreachable -> degrade; native check still applies
    ids = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    if ids:
        console.print(
            f"[red]Container runtime already active for {project_name} "
            f"({len(ids)} container(s): {', '.join(ids)}).[/red]"
        )
        console.print("Run [bold]rai dev down[/bold] first.")
        raise typer.Exit(1)


def _compose_up(worktree_path: Path, project_name: str) -> None:
    """Start PostgreSQL via docker compose."""
    subprocess.run(  # noqa: S603, S607
        [
            "docker",
            "compose",
            "-p",
            project_name,
            "-f",
            "docker-compose.dev.yml",
            "up",
            "-d",
            "--wait",
        ],
        cwd=str(worktree_path),
        check=True,
        capture_output=True,
    )


def _wait_postgres_healthy(
    project_name: str,
    worktree_path: Path,
    timeout: int = _POSTGRES_HEALTH_TIMEOUT,
) -> None:
    """Poll until PostgreSQL is healthy or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = subprocess.run(  # noqa: S603, S607
            [
                "docker",
                "compose",
                "-p",
                project_name,
                "-f",
                "docker-compose.dev.yml",
                "ps",
                "--format",
                "json",
            ],
            cwd=str(worktree_path),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and "healthy" in result.stdout.lower():
            return
        time.sleep(_POSTGRES_HEALTH_INTERVAL)
    console.print("[yellow]Warning: PostgreSQL health check timed out.[/yellow]")


def _get_venv_path(worktree_path: Path) -> Path:
    """Return the isolated venv path for this worktree."""
    return worktree_path / ".venv.dev"


def _install_python_deps(worktree_path: Path) -> None:
    """Run uv sync into a worktree-isolated venv (.venv.dev)."""
    import os

    venv_path = _get_venv_path(worktree_path)
    env = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(venv_path)}
    subprocess.run(  # noqa: S603, S607
        ["uv", "sync"],
        cwd=str(worktree_path),
        env=env,
        check=True,
        capture_output=True,
    )


def _install_frontend_deps(
    worktree_path: Path, package_dir: str = "packages/raise-admin"
) -> None:
    """Run npm ci to install frontend dependencies."""
    admin_dir = worktree_path / package_dir
    if not (admin_dir / "package.json").exists():
        console.print(
            "[yellow]No package.json found in raise-admin — skipping npm.[/yellow]"
        )
        return
    subprocess.run(  # noqa: S603, S607
        ["npm", "ci", "--prefer-offline"],
        cwd=str(admin_dir),
        check=True,
        capture_output=True,
    )


def _run_migrations(worktree_path: Path, db_url: str) -> None:
    """Run Alembic migrations against the dev database."""
    import os

    server_dir = worktree_path / "packages" / "raise-server"
    if not (server_dir / "alembic.ini").exists():
        console.print("[yellow]No alembic.ini found — skipping migrations.[/yellow]")
        return
    venv_path = _get_venv_path(worktree_path)
    subprocess.run(  # noqa: S603, S607
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=str(server_dir),
        env={
            **os.environ,
            "RAI_DATABASE_URL": db_url,
            "UV_PROJECT_ENVIRONMENT": str(venv_path),
        },
        check=True,
        capture_output=True,
    )


@dev_app.command("up")
def up(
    no_migrate: Annotated[
        bool,
        typer.Option("--no-migrate", help="Skip Alembic migrations."),
    ] = False,
    no_frontend: Annotated[
        bool,
        typer.Option("--no-frontend", help="Don't start Vite dev server."),
    ] = False,
) -> None:
    """Start an isolated dev stack for the current worktree."""
    worktree_path = Path.cwd()

    # Pre-checks
    _check_docker()
    _check_not_running(worktree_path)  # native (existente, sin cambios)
    _check_no_containers(worktree_path)  # container (nuevo)

    # Load dev config
    cfg = DevConfig.load(worktree_path)

    # 1. Allocate ports
    console.print("[bold]\\[1/9][/bold] Allocating ports...", end=" ")
    block = allocate_ports(worktree_path)
    console.print(
        f"base={block.base} "
        f"(postgres={block.postgres}, server={block.server}, vite={block.vite})"
    )

    # 2. Install Python dependencies
    console.print("[bold]\\[2/9][/bold] Installing Python dependencies (uv sync)...")
    _install_python_deps(worktree_path)

    # 3. Generate compose
    console.print("[bold]\\[3/9][/bold] Generating docker-compose.dev.yml...")
    content = generate_compose(worktree_path, block, cfg)
    write_compose_file(worktree_path, content)

    # 4. Start PostgreSQL
    slug = get_worktree_slug(worktree_path)
    project_name = get_compose_project_name(slug)
    console.print(f"[bold]\\[4/9][/bold] Starting PostgreSQL ({cfg.pg_image})...")
    _compose_up(worktree_path, project_name)
    _wait_postgres_healthy(project_name, worktree_path)

    # 5. Migrations
    db_url = f"postgresql+asyncpg://{cfg.pg_user}:{cfg.pg_password}@localhost:{block.postgres}/{cfg.pg_db}"  # pragma: allowlist secret
    if no_migrate:
        console.print("[bold]\\[5/9][/bold] Skipping migrations (--no-migrate).")
    else:
        console.print("[bold]\\[5/9][/bold] Running migrations...")
        _run_migrations(worktree_path, db_url)

    # 6. Start server
    console.print(f"[bold]\\[6/9][/bold] Starting raise-server on :{block.server}...")
    server_cmd = [
        "uv",
        "run",
        "uvicorn",
        cfg.server_module,
        "--host",
        "127.0.0.1",
        "--port",
        str(block.server),
    ]
    if cfg.server_factory:
        server_cmd.insert(4, "--factory")
    venv_path = _get_venv_path(worktree_path)
    start_process(
        server_cmd,
        worktree_path,
        "server",
        env={
            "RAI_DATABASE_URL": db_url,
            "RAI_ENV": "development",
            "RAI_PORT": str(block.server),
            "UV_PROJECT_ENVIRONMENT": str(venv_path),
        },
    )

    # 7. Install frontend dependencies
    if no_frontend:
        console.print("[bold]\\[7/9][/bold] Skipping frontend deps (--no-frontend).")
    else:
        console.print(
            "[bold]\\[7/9][/bold] Installing frontend dependencies (npm ci)..."
        )
        _install_frontend_deps(worktree_path, cfg.frontend_package_dir)

    # 8. Start frontend
    if no_frontend:
        console.print("[bold]\\[8/9][/bold] Skipping frontend (--no-frontend).")
    else:
        console.print(f"[bold]\\[8/9][/bold] Starting raise-admin on :{block.vite}...")
        start_process(
            [
                "npx",
                "vite",
                "--port",
                str(block.vite),
                "--host",
                "127.0.0.1",
            ],
            worktree_path / cfg.frontend_package_dir,
            "vite",
            env={"VITE_API_URL": f"http://localhost:{block.server}"},
        )

    # 9. Write .env.dev
    console.print("[bold]\\[9/9][/bold] Writing .env.dev...")
    env_content = generate_env_content(
        block, no_frontend=no_frontend, venv_path=str(venv_path)
    )
    write_env_file(worktree_path, env_content)

    # Report
    console.print()
    console.print("[bold green]Stack ready:[/bold green]")
    console.print(f"  PostgreSQL: localhost:{block.postgres}")
    console.print(f"  Server:     http://localhost:{block.server}")
    if not no_frontend:
        console.print(f"  Frontend:   http://localhost:{block.vite}")
    console.print(f"  .env.dev:   {worktree_path / '.env.dev'}")


def _stop_native_processes(worktree_path: Path) -> int:
    """Kill server and vite processes. Returns count of processes killed."""
    killed = 0
    for service in ("server", "vite"):
        if kill_process(worktree_path, service):
            console.print(f"  Stopped {service}")
            killed += 1
    return killed


def _compose_down(
    worktree_path: Path, project_name: str, *, volumes: bool = False
) -> None:
    """Stop PostgreSQL via docker compose."""
    cmd = [
        "docker",
        "compose",
        "-p",
        project_name,
        "-f",
        "docker-compose.dev.yml",
        "down",
    ]
    if volumes:
        cmd.append("-v")
    subprocess.run(  # noqa: S603, S607
        cmd,
        cwd=str(worktree_path),
        capture_output=True,
    )


@dev_app.command("down")
def down(
    volumes: Annotated[
        bool,
        typer.Option("--volumes", help="Remove PostgreSQL data volume."),
    ] = False,
) -> None:
    """Stop the dev stack for the current worktree."""
    worktree_path = Path.cwd()

    console.print("[bold]Stopping dev stack...[/bold]")

    # Kill native processes
    killed = _stop_native_processes(worktree_path)

    # Stop Docker containers
    slug = get_worktree_slug(worktree_path)
    project_name = get_compose_project_name(slug)
    _compose_down(worktree_path, project_name, volumes=volumes)
    console.print(f"  Stopped PostgreSQL ({project_name})")

    if volumes:
        console.print("  [yellow]Volume data removed.[/yellow]")

    if killed == 0:
        console.print("[dim]No native processes were running.[/dim]")

    console.print("[bold green]Stack stopped.[/bold green]")


def _health_indicator(healthy: bool | None, alive: bool) -> str:
    """Return a Rich-formatted health indicator."""
    if healthy is True:
        return "[green]UP[/green]"
    if alive and healthy is False:
        return "[yellow]UNHEALTHY[/yellow]"
    if alive:
        return "[yellow]ALIVE[/yellow]"
    return "[red]DOWN[/red]"


@dev_app.command("status")
def status() -> None:
    """Show status of all active dev stacks across worktrees."""
    from rich.table import Table

    worktree_path = Path.cwd()
    stacks = discover_stacks(worktree_path)

    if not stacks:
        console.print("[dim]No active dev stacks found.[/dim]")
        return

    table = Table(title="Dev Stacks")
    table.add_column("Worktree", style="bold")
    table.add_column("Slug")
    table.add_column("Postgres")
    table.add_column("Server")
    table.add_column("Vite")
    table.add_column("Status")

    for stack in stacks:
        pg = stack.services.get("postgres")
        srv = stack.services.get("server")
        vite = stack.services.get("vite")

        pg_port = str(stack.ports.postgres) if stack.ports else "?"
        srv_port = str(stack.ports.server) if stack.ports else "?"
        vite_port = str(stack.ports.vite) if stack.ports else "?"

        pg_status = _health_indicator(pg.healthy, pg.alive) if pg else "[dim]—[/dim]"
        srv_status = (
            _health_indicator(srv.healthy, srv.alive) if srv else "[dim]—[/dim]"
        )
        vite_status = (
            _health_indicator(vite.healthy, vite.alive) if vite else "[dim]—[/dim]"
        )

        # Detect orphans: PID file exists but process dead
        orphan_services = [
            s.name for s in stack.services.values() if s.pid is not None and not s.alive
        ]
        overall = (
            "[yellow]ORPHAN[/yellow]"
            if orphan_services
            else "[green]RUNNING[/green]"
            if any(s.alive for s in stack.services.values())
            else "[red]STOPPED[/red]"
        )

        table.add_row(
            str(stack.worktree_path),
            stack.slug,
            f"{pg_port} {pg_status}",
            f"{srv_port} {srv_status}",
            f"{vite_port} {vite_status}",
            overall,
        )

    console.print(table)


@dev_app.command("reap")
def reap(
    max_age_minutes: Annotated[
        int,
        typer.Option(
            "--max-age",
            help="Edad máxima en minutos antes de reapear (default: 30).",
        ),
    ] = 30,
) -> None:
    """Force-remove orphan raise-runner containers idle beyond max_age."""
    from datetime import timedelta

    reaped = reap_idle(timedelta(minutes=max_age_minutes))
    if not reaped:
        console.print("docker no disponible o sin containers raise-runner idle.")
    else:
        console.print(
            f"Reapeados {len(reaped)} containers raise-runner idle"
            f" (> {max_age_minutes}m)."
        )
