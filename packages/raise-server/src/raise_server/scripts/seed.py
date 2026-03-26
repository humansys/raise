"""Seed script — create first client org, admin, license, and API key.

Run: RAI_DATABASE_URL=postgresql+asyncpg://... python -m raise_server.scripts.seed

Uses direct DB inserts (D7) — no API call needed, no chicken-and-egg.
Prints raw API key ONCE. Save it.
"""

from __future__ import annotations

import asyncio
import hashlib
import secrets
import sys
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from raise_server.config import ServerConfig
from raise_server.db.models import ApiKeyRow, Base, LicenseRow, MemberRow, Organization


async def seed(database_url: str) -> None:
    """Insert first client data. Idempotent — skips if org already exists."""
    engine = create_async_engine(database_url)

    async with engine.begin() as conn:
        # Ensure tables exist (in case running without alembic)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        # Check if org already exists
        result = await session.execute(
            select(Organization).where(Organization.slug == "humansys")
        )
        if result.scalar_one_or_none():
            print("Organization 'humansys' already exists — skipping seed.")
            await engine.dispose()
            return

        # 1. Create organization
        org = Organization(name="HumanSys", slug="humansys")
        session.add(org)
        await session.flush()
        print(f"Created organization: HumanSys (humansys) — {org.id}")

        # 2. Create admin member
        admin = MemberRow(
            org_id=org.id,
            email="emilio@humansys.ai",
            name="Emilio",
            role="admin",
        )
        session.add(admin)
        await session.flush()
        print(f"Created admin member: emilio@humansys.ai — {admin.id}")

        # 3. Create license
        lic = LicenseRow(
            org_id=org.id,
            plan="team",
            features=["jira", "confluence", "odoo", "gitlab"],
            seats=10,
            status="active",
            expires_at=datetime(2027, 3, 25, tzinfo=UTC),
        )
        session.add(lic)
        await session.flush()
        print(f"Created license: team, 10 seats, expires 2027-03-25 — {lic.id}")

        # 4. Create API key
        raw_key = "rsk_" + secrets.token_hex(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:12]

        api_key = ApiKeyRow(
            member_id=admin.id,
            org_id=org.id,
            key_hash=key_hash,
            key_prefix=key_prefix,
        )
        session.add(api_key)
        await session.commit()
        print(f"\nAPI Key (SAVE THIS — shown once): {raw_key}")

    await engine.dispose()


def main() -> None:
    """Entry point for `python -m raise_server.scripts.seed`."""
    try:
        config = ServerConfig()  # type: ignore[call-arg]  # pydantic-settings reads env
    except Exception:  # noqa: BLE001
        print("ERROR: Set RAI_DATABASE_URL environment variable.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(seed(config.database_url))


if __name__ == "__main__":
    main()
