"""Stack discovery and health checks for worktree dev stacks."""

from __future__ import annotations

import socket
import subprocess
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from raise_cli.dev.compose import get_worktree_slug
from raise_cli.dev.ports import PortBlock
from raise_cli.dev.processes import is_running, read_pid

_HEALTH_TIMEOUT_SOCKET = 1
_HEALTH_TIMEOUT_HTTP = 2


@dataclass
class ServiceStatus:
    """Health status of a single service in a dev stack."""

    name: str
    pid: int | None = None
    alive: bool = False
    healthy: bool | None = None


@dataclass
class StackInfo:
    """Aggregated status of a worktree's dev stack."""

    worktree_path: Path
    slug: str
    ports: PortBlock | None = None
    services: dict[str, ServiceStatus] = field(default_factory=dict)


def parse_env_dev(worktree_path: Path) -> PortBlock | None:
    """Parse .env.dev to extract port assignments. Returns None if missing."""
    env_file = worktree_path / ".env.dev"
    if not env_file.exists():
        return None
    values: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip()
    try:
        postgres = int(values["RAI_DEV_POSTGRES_PORT"])
    except (KeyError, ValueError):
        return None
    return PortBlock.from_base(postgres)


def check_service_health(service: str, port: int) -> bool:
    """Probe a service for liveness. Returns True if responsive."""
    if service == "server":
        try:
            with urllib.request.urlopen(  # nosec B310
                f"http://127.0.0.1:{port}/health",
                timeout=_HEALTH_TIMEOUT_HTTP,
            ):
                return True
        except OSError:
            return False
    # postgres and vite: raw TCP connect
    try:
        with socket.create_connection(
            ("127.0.0.1", port), timeout=_HEALTH_TIMEOUT_SOCKET
        ):
            return True
    except OSError:
        return False


def _build_stack_info(worktree_path: Path) -> StackInfo | None:
    """Build StackInfo for a single worktree. Returns None if no dev state."""
    dev_dir = worktree_path / ".raise" / "dev"
    has_pid = dev_dir.exists() and any(dev_dir.glob("*.pid"))
    has_env = (worktree_path / ".env.dev").exists()
    if not has_pid and not has_env:
        return None

    slug = get_worktree_slug(worktree_path)
    ports = parse_env_dev(worktree_path)
    services: dict[str, ServiceStatus] = {}

    for svc_name in ("server", "vite"):
        pid = read_pid(worktree_path, svc_name)
        alive = pid is not None and is_running(pid)
        port = getattr(ports, svc_name, None) if ports else None
        healthy: bool | None = None
        if alive and port:
            healthy = check_service_health(svc_name, port)
        services[svc_name] = ServiceStatus(
            name=svc_name, pid=pid, alive=alive, healthy=healthy
        )

    if ports:
        pg_port = ports.postgres
        pg_healthy = check_service_health("postgres", pg_port)
        services["postgres"] = ServiceStatus(
            name="postgres",
            pid=None,
            alive=pg_healthy,
            healthy=pg_healthy if pg_healthy else None,
        )

    return StackInfo(
        worktree_path=worktree_path,
        slug=slug,
        ports=ports,
        services=services,
    )


def discover_stacks(search_from: Path) -> list[StackInfo]:
    """Discover all worktrees with active dev stacks."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=str(search_from),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Fallback: only check current directory
        info = _build_stack_info(search_from)
        return [info] if info else []

    worktree_paths: list[Path] = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            worktree_paths.append(Path(line.removeprefix("worktree ").strip()))

    stacks: list[StackInfo] = []
    for wt_path in worktree_paths:
        info = _build_stack_info(wt_path)
        if info:
            stacks.append(info)
    return stacks
