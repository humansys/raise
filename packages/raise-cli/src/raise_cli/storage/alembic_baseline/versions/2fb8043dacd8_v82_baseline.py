"""v82 baseline — RAISE-19634.

Stamps the raise-cli DB as being at schema version 82 without running any DDL.
Existing databases migrated via the _apply_vXX engine already contain all
tables up to v82; this migration is a no-op that tells Alembic "everything up
to here is already applied".

Revision ID: 2fb8043dacd8
Revises: (none — this is the first Alembic revision for raise-cli)
Create Date: 2026-11-03
"""

from __future__ import annotations

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2fb8043dacd8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """No-op — DB is already at v82 via the _apply_vXX engine."""


def downgrade() -> None:
    """No-op — the baseline cannot be rolled back (v0–v82 use user_version)."""
