"""Alembic environment for raise-cli SQLite migrations — RAISE-19634.

Designed for programmatic invocation (no alembic.ini required at runtime):
  cfg = Config()
  cfg.set_main_option("script_location", str(Path(__file__).parent))
  cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
  alembic.command.stamp(cfg, revision)

The offline/online split follows Alembic convention; target_metadata is None
because raise-cli does not use SQLAlchemy ORM models — it owns its DDL via the
_apply_vXX engine in storage/schema.py.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No ORM metadata — raise-cli owns its DDL via the hand-rolled migration engine.
target_metadata = None


def run_migrations_offline() -> None:
    """Generate SQL without a DB connection (offline mode)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection (online mode)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
