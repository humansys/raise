"""Dev stack configuration reader — loads .raise/dev.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_PG_IMAGE = "pgvector/pgvector:0.8.0-pg17-bookworm"
_DEFAULT_PG_USER = "rai"
_DEFAULT_PG_PASSWORD = "dev"  # noqa: S105  # pragma: allowlist secret
_DEFAULT_PG_DB = "rai"
_DEFAULT_SERVER_MODULE = "raise_server.app:create_app"


@dataclass(frozen=True)
class DevConfig:
    """Parsed dev stack configuration."""

    pg_image: str
    pg_user: str
    pg_password: str
    pg_db: str
    server_module: str
    server_factory: bool
    frontend_package_dir: str
    runtime_image_enabled: bool = True

    @classmethod
    def load(cls, worktree_path: Path) -> DevConfig:
        """Load config from .raise/dev.yaml, falling back to defaults."""
        config_file = worktree_path / ".raise" / "dev.yaml"
        raw: dict[str, object] = {}
        if config_file.exists():
            raw = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}

        pg = raw.get("postgres", {})
        if not isinstance(pg, dict):
            pg = {}
        server = raw.get("server", {})
        if not isinstance(server, dict):
            server = {}
        frontend = raw.get("frontend", {})
        if not isinstance(frontend, dict):
            frontend = {}
        runtime = raw.get("runtime", {})
        if not isinstance(runtime, dict):
            runtime = {}

        return cls(
            pg_image=str(pg.get("image", _DEFAULT_PG_IMAGE)),
            pg_user=str(pg.get("user", _DEFAULT_PG_USER)),
            pg_password=str(pg.get("password", _DEFAULT_PG_PASSWORD)),
            pg_db=str(pg.get("db", _DEFAULT_PG_DB)),
            server_module=str(server.get("module", _DEFAULT_SERVER_MODULE)),
            server_factory=bool(server.get("factory", True)),
            frontend_package_dir=str(
                frontend.get("package_dir", "packages/raise-admin")
            ),
            runtime_image_enabled=bool(runtime.get("enabled", True)),
        )
