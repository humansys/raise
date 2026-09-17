"""DevStackProvisioner — idempotent provisioning for worktree-isolated dev stacks.

S16534.2 (RAISE-16542): Fleet dispatch provisions an isolated dev stack
per story worktree before the agent spawns.  Teardown releases resources
on worktree close.

Design DD1: calls shared library helpers (not subprocess rai dev up).
Design DD2: opt-in gate = .raise/dev.yaml present in the target worktree.
Design DD6: self-heal on unhealthy = teardown + fresh provision.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from raise_cli.dev.compose import (
    generate_compose,
    get_compose_project_name,
    get_worktree_slug,
    write_compose_file,
)
from raise_cli.dev.config import DevConfig
from raise_cli.dev.env import generate_env_content, write_env_file
from raise_cli.dev.envrc import generate_envrc, write_envrc
from raise_cli.dev.ports import PortBlock, allocate_ports
from raise_cli.dev.processes import kill_process, start_process
from raise_cli.dev.runtime_image import extract_deps, should_use_image
from raise_cli.dev.status import check_service_health, parse_env_dev
from raise_cli.storage.port_allocations import SqlitePortAllocationStore

logger = logging.getLogger(__name__)

_POSTGRES_HEALTH_TIMEOUT = 30
_POSTGRES_HEALTH_INTERVAL = 2
_SERVER_HEALTH_TIMEOUT = 15
_SERVER_HEALTH_INTERVAL = 1


# ---------------------------------------------------------------------------
# Exceptions & data
# ---------------------------------------------------------------------------


class DevStackProvisioningError(Exception):
    """Raised when provisioning fails irrecoverably."""


@dataclass(frozen=True)
class DevStackReport:
    """Result of an ``ensure_up`` call."""

    status: Literal["skipped", "already_running", "provisioned"]
    worktree_path: Path
    ports: PortBlock | None = None
    db_url: str | None = None
    detail: str = ""


# ---------------------------------------------------------------------------
# Shared orchestration helpers (moved from cli/commands/dev.py)
#
# console.print warnings become logger.warning — these helpers run in both
# CLI and fleet-dispatch contexts.
# ---------------------------------------------------------------------------


def wait_server_healthy(
    port: int,
    timeout: float = _SERVER_HEALTH_TIMEOUT,
    interval: float = _SERVER_HEALTH_INTERVAL,
) -> None:
    """Poll until the server /health endpoint responds or raise on timeout.

    Mirrors ``wait_postgres_healthy`` but checks the HTTP health endpoint
    via ``check_service_health("server", ...)``.  Raises
    ``DevStackProvisioningError`` when the deadline is exceeded so that
    a dead server never dispatches an agent (MUST-3 rejection semantics).
    """
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if check_service_health("server", port):
            return
        time.sleep(interval)
    raise DevStackProvisioningError(
        f"Server health check timed out after {timeout}s on port {port}"
    )


def compose_up(worktree_path: Path, project_name: str) -> None:
    """Start PostgreSQL via docker compose."""
    subprocess.run(
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


def wait_postgres_healthy(
    project_name: str,
    worktree_path: Path,
    timeout: int = _POSTGRES_HEALTH_TIMEOUT,
) -> None:
    """Poll until PostgreSQL is healthy or timeout."""
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = subprocess.run(
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
    logger.warning("PostgreSQL health check timed out for %s", project_name)


def get_venv_path(worktree_path: Path) -> Path:
    """Return the isolated venv path for this worktree."""
    return worktree_path / ".venv.dev"


def install_python_deps(worktree_path: Path, *, frozen: bool = False) -> None:
    """Run uv sync into a worktree-isolated venv (.venv.dev).

    Args:
        worktree_path: Root of the worktree.
        frozen: If True, pass ``--frozen`` to skip lock-file update (R2/AC2).
            Used after runtime image extraction where third-party deps are
            already present and only workspace editables need linking.
    """
    import os

    venv_path = get_venv_path(worktree_path)
    env = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(venv_path)}
    cmd = ["uv", "sync"]
    if frozen:
        cmd.append("--frozen")
    subprocess.run(
        cmd,
        cwd=str(worktree_path),
        env=env,
        check=True,
        capture_output=True,
    )


def install_frontend_deps(
    worktree_path: Path, package_dir: str = "packages/raise-admin"
) -> None:
    """Run npm ci to install frontend dependencies."""
    admin_dir = worktree_path / package_dir
    if not (admin_dir / "package.json").exists():
        logger.warning("No package.json found in %s -- skipping npm.", package_dir)
        return
    subprocess.run(
        ["npm", "ci", "--prefer-offline"],
        cwd=str(admin_dir),
        check=True,
        capture_output=True,
    )


def run_migrations(worktree_path: Path, db_url: str) -> None:
    """Run Alembic migrations against the dev database."""
    import os

    server_dir = worktree_path / "packages" / "raise-server"
    if not (server_dir / "alembic.ini").exists():
        logger.warning("No alembic.ini found -- skipping migrations.")
        return
    venv_path = get_venv_path(worktree_path)
    subprocess.run(
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


def stop_native_processes(worktree_path: Path) -> int:
    """Kill server and vite processes. Returns count of processes killed."""
    killed = 0
    for service in ("server", "vite"):
        if kill_process(worktree_path, service):
            logger.info("Stopped %s in %s", service, worktree_path)
            killed += 1
    return killed


def compose_down(
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
    subprocess.run(
        cmd,
        cwd=str(worktree_path),
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# DevStackProvisioner
# ---------------------------------------------------------------------------


class DevStackProvisioner:
    """Idempotent provisioner for worktree-isolated dev stacks.

    ``ensure_up`` flow (ProvisioningVerifier pattern — pure check first,
    then side effects):

    1. Gate: ``.raise/dev.yaml`` missing -> ``skipped``
    2. Pure health check: parse_env_dev + check_service_health
    3. Self-heal: unhealthy -> teardown + fresh provision
    4. Provision: allocate_ports -> compose up -> migrations -> server
    5. Return ``provisioned`` with ports + db_url
    """

    def ensure_up(
        self, worktree_path: Path, *, frontend: bool = False
    ) -> DevStackReport:
        """Idempotent, side-effecting. Raises DevStackProvisioningError on failure."""
        # 1. Gate: .raise/dev.yaml missing -> skip
        if not (worktree_path / ".raise" / "dev.yaml").exists():
            return DevStackReport(
                status="skipped",
                worktree_path=worktree_path,
                detail="no .raise/dev.yaml",
            )

        # 2. Pure health check
        ports = parse_env_dev(worktree_path)
        if ports is not None:
            pg_healthy = check_service_health("postgres", ports.postgres)
            srv_healthy = check_service_health("server", ports.server)
            if pg_healthy and srv_healthy:
                cfg = DevConfig.load(worktree_path)
                db_url = (
                    f"postgresql+asyncpg://{cfg.pg_user}:{cfg.pg_password}"
                    f"@localhost:{ports.postgres}/{cfg.pg_db}"
                )
                return DevStackReport(
                    status="already_running",
                    worktree_path=worktree_path,
                    ports=ports,
                    db_url=db_url,
                    detail=f"postgres={ports.postgres}, server={ports.server}",
                )
            # 3. Self-heal: partial/unhealthy -> teardown then provision fresh
            logger.info(
                "Unhealthy stack in %s (pg=%s, srv=%s) -- tearing down for re-provision",
                worktree_path,
                pg_healthy,
                srv_healthy,
            )
            self._teardown_internal(worktree_path, volumes=False)

        # 4. Provision
        try:
            return self._provision(worktree_path, frontend=frontend)
        except DevStackProvisioningError:
            raise
        except subprocess.CalledProcessError as exc:
            stderr_raw = exc.stderr or b""
            stderr_text = (
                stderr_raw.decode(errors="replace").strip()
                if isinstance(stderr_raw, bytes)
                else str(stderr_raw).strip()
            )
            msg = f"{exc}: {stderr_text}" if stderr_text else str(exc)
            raise DevStackProvisioningError(msg) from exc
        except Exception as exc:
            raise DevStackProvisioningError(str(exc)) from exc

    def teardown(self, worktree_path: Path, *, volumes: bool = True) -> None:
        """Stop native processes, compose down, release port claim. Idempotent."""
        self._teardown_internal(worktree_path, volumes=volumes)

    def _teardown_internal(self, worktree_path: Path, *, volumes: bool) -> None:
        """Shared teardown logic for self-heal and explicit teardown."""
        stop_native_processes(worktree_path)
        slug = get_worktree_slug(worktree_path)
        project_name = get_compose_project_name(slug)
        compose_down(worktree_path, project_name, volumes=volumes)
        store = SqlitePortAllocationStore(worktree_path)
        store.release(worktree_path)

    def _provision(self, worktree_path: Path, *, frontend: bool) -> DevStackReport:
        """Full provision sequence -- same as rai dev up (DD1)."""
        cfg = DevConfig.load(worktree_path)

        # 1. Allocate ports
        store = SqlitePortAllocationStore(worktree_path)
        block = allocate_ports(worktree_path, store=store)

        # 2. Python deps -- extract from image or install natively (S16534.4)
        image_used = False
        if cfg.runtime_image_enabled:
            available, tag = should_use_image(worktree_path)
            if available:
                try:
                    extract_deps(tag, worktree_path, cfg.frontend_package_dir)
                    # Fast sync --frozen: workspace editables only (R2)
                    install_python_deps(worktree_path, frozen=True)
                    image_used = True
                except (subprocess.CalledProcessError, OSError, RuntimeError):
                    # C2: extraction failure -> fall back to native install
                    logger.warning(
                        "Runtime image extraction failed (tag=%s), "
                        "falling back to native install.",
                        tag,
                        exc_info=True,
                    )
                    install_python_deps(worktree_path)
            else:
                logger.warning(
                    "Runtime image not found (tag=%s), falling back to native install. "
                    "Run `rai dev build-runtime` to speed up future starts.",
                    tag,
                )
                install_python_deps(worktree_path)
        else:
            install_python_deps(worktree_path)

        # 3. Generate + write compose
        content = generate_compose(worktree_path, block, cfg)
        write_compose_file(worktree_path, content)

        # 4. Start PostgreSQL
        slug = get_worktree_slug(worktree_path)
        project_name = get_compose_project_name(slug)
        compose_up(worktree_path, project_name)
        wait_postgres_healthy(project_name, worktree_path)

        # 5. Migrations
        db_url = (
            f"postgresql+asyncpg://{cfg.pg_user}:{cfg.pg_password}"
            f"@localhost:{block.postgres}/{cfg.pg_db}"
        )
        run_migrations(worktree_path, db_url)

        # 6. Start server
        venv_path = get_venv_path(worktree_path)
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

        # 7. Frontend (DD5: fleet default frontend=False)
        #    If image was used, node_modules already extracted -- skip install.
        if frontend and not image_used:
            install_frontend_deps(worktree_path, cfg.frontend_package_dir)
        if frontend:
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

        # 8. Write .env.dev
        env_content = generate_env_content(
            block,
            no_frontend=not frontend,
            venv_path=str(venv_path),
            db_url=db_url,
        )
        write_env_file(worktree_path, env_content)

        # 9. Write .envrc
        envrc_content = generate_envrc(slug=slug)
        write_envrc(worktree_path, envrc_content)

        # 10. Post-provision health check (C1: poll with deadline, raise on timeout)
        wait_server_healthy(block.server)

        return DevStackReport(
            status="provisioned",
            worktree_path=worktree_path,
            ports=block,
            db_url=db_url,
            detail=f"postgres={block.postgres}, server={block.server}",
        )
