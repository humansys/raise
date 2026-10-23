"""Docker Compose template generation for worktree-isolated PostgreSQL."""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.dev.config import DevConfig
from raise_cli.dev.ports import PortBlock


def get_worktree_slug(worktree_path: Path) -> str:
    """Derive a slug from the worktree directory name."""
    return worktree_path.name


def get_compose_project_name(slug: str) -> str:
    """Return the Docker Compose project name for a worktree slug."""
    return f"raise-{slug}"


def generate_compose(worktree_path: Path, block: PortBlock, cfg: DevConfig) -> str:
    """Generate a docker-compose.dev.yml YAML string for this worktree's PostgreSQL."""
    slug = get_worktree_slug(worktree_path)
    compose: dict[str, object] = {
        "services": {
            "postgres": {
                "image": cfg.pg_image,
                "environment": {
                    "POSTGRES_USER": cfg.pg_user,
                    "POSTGRES_DB": cfg.pg_db,
                    "POSTGRES_PASSWORD": cfg.pg_password,
                },
                "ports": [f"{block.postgres}:5432"],
                "volumes": ["pgdata:/var/lib/postgresql/data"],
                "healthcheck": {
                    "test": [
                        "CMD-SHELL",
                        f"pg_isready -U {cfg.pg_user} -d {cfg.pg_db}",
                    ],
                    "interval": "5s",
                    "timeout": "3s",
                    "retries": 5,
                },
            },
        },
        "volumes": {
            "pgdata": {
                "name": f"raise-{slug}-pgdata",
            },
        },
    }
    return yaml.dump(compose, default_flow_style=False, sort_keys=False)


def write_compose_file(worktree_path: Path, content: str) -> Path:
    """Write docker-compose.dev.yml to the worktree root."""
    target = worktree_path / "docker-compose.dev.yml"
    target.write_text(content, encoding="utf-8")
    return target
