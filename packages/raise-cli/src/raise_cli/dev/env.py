"""Environment file generation for worktree dev stacks."""

from __future__ import annotations

from pathlib import Path

from raise_cli.dev.ports import PortBlock


def generate_env_content(
    block: PortBlock, *, no_frontend: bool = False, venv_path: str = ".venv.dev"
) -> str:
    """Generate .env.dev content with all port assignments and URLs."""
    lines = [
        f"RAI_DEV_POSTGRES_PORT={block.postgres}",
        f"RAI_DEV_SERVER_PORT={block.server}",
        f"RAI_DEV_DB_URL=postgresql+asyncpg://rai:dev@localhost:{block.postgres}/rai",  # pragma: allowlist secret
        f"UV_PROJECT_ENVIRONMENT={venv_path}",
    ]
    if not no_frontend:
        lines.extend(
            [
                f"RAI_DEV_VITE_PORT={block.vite}",
                f"VITE_API_URL=http://localhost:{block.server}",
            ]
        )
    return "\n".join(lines) + "\n"


def write_env_file(worktree_path: Path, content: str) -> Path:
    """Write .env.dev to the worktree root."""
    target = worktree_path / ".env.dev"
    target.write_text(content, encoding="utf-8")
    return target
