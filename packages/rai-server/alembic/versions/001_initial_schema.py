"""Initial schema — organizations, api_keys, graph_nodes, graph_edges.

Revision ID: 001
Revises: None
Create Date: 2026-02-25
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- organizations ---
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.func.gen_random_uuid(),
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(63), nullable=False, unique=True, index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # --- api_keys ---
    op.create_table(
        "api_keys",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.func.gen_random_uuid(),
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("key_hash", sa.String(128), nullable=False),
        sa.Column("prefix", sa.String(12), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # --- graph_nodes ---
    op.create_table(
        "graph_nodes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.func.gen_random_uuid(),
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("repo_id", sa.String(255), nullable=False, index=True),
        sa.Column("scope", sa.String(20), nullable=False),
        sa.Column("node_type", sa.String(50), nullable=False, index=True),
        sa.Column("node_id", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("source_file", sa.String(500), nullable=True),
        sa.Column("properties", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("org_id", "repo_id", "node_id", name="uq_node_org_repo_nodeid"),
    )

    # GIN index on graph_nodes.properties
    op.create_index(
        "ix_graph_nodes_properties",
        "graph_nodes",
        ["properties"],
        postgresql_using="gin",
    )

    # --- graph_edges ---
    op.create_table(
        "graph_edges",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.func.gen_random_uuid(),
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("repo_id", sa.String(255), nullable=False),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("graph_nodes.id"),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("graph_nodes.id"),
            nullable=False,
        ),
        sa.Column("edge_type", sa.String(50), nullable=False, index=True),
        sa.Column("weight", sa.Float, server_default="1.0", nullable=False),
        sa.Column("properties", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # GIN index on graph_edges.properties
    op.create_index(
        "ix_graph_edges_properties",
        "graph_edges",
        ["properties"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_table("graph_edges")
    op.drop_table("graph_nodes")
    op.drop_table("api_keys")
    op.drop_table("organizations")
