"""E2E test fixtures — real PostgreSQL via docker compose.

All tests in this directory require `@pytest.mark.e2e` and a running PG.
Skip with: `pytest -m 'not e2e'`
Run only E2E: `pytest tests/e2e/ -m e2e`

Strategy: Seed data via standalone engine, then create a SEPARATE app engine
for the FastAPI app (httpx ASGITransport doesn't trigger lifespan).
"""

from __future__ import annotations

import hashlib
import os
import secrets
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from raise_server.app import create_app
from raise_server.config import ServerConfig
from raise_server.db.models import ApiKeyRow, Base, LicenseRow, MemberRow, Organization
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

_DEFAULT_DB_URL = "postgresql+asyncpg://rai:rai_dev@localhost:5432/rai"


def _db_url() -> str:
    return os.environ.get("RAI_DATABASE_URL", _DEFAULT_DB_URL)


def _pg_available() -> bool:
    """Check if PG is reachable."""
    try:
        import asyncio

        async def _check() -> bool:
            engine = create_async_engine(_db_url())
            try:
                async with engine.connect() as conn:
                    from sqlalchemy import text

                    await conn.execute(text("SELECT 1"))
                return True
            except Exception:  # noqa: BLE001
                return False
            finally:
                await engine.dispose()

        return asyncio.run(_check())
    except Exception:  # noqa: BLE001
        return False


_pg_ok = _pg_available()
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not _pg_ok, reason="PostgreSQL not available"),
]


@pytest_asyncio.fixture(scope="module")
async def seed_data() -> AsyncGenerator[dict[str, str], None]:
    """Create tables, seed first client, yield IDs + raw key, then drop tables."""
    engine = create_async_engine(_db_url())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        org = Organization(name="HumanSys", slug="humansys")
        session.add(org)
        await session.flush()

        admin = MemberRow(
            org_id=org.id, email="emilio@humansys.ai", name="Emilio", role="admin"
        )
        session.add(admin)
        await session.flush()

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

        raw_key = "rsk_" + secrets.token_hex(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = ApiKeyRow(
            member_id=admin.id,
            org_id=org.id,
            key_hash=key_hash,
            key_prefix=raw_key[:12],
        )
        session.add(api_key)
        await session.commit()

        data: dict[str, str] = {
            "org_id": str(org.id),
            "admin_id": str(admin.id),
            "license_id": str(lic.id),
            "api_key_id": str(api_key.id),
            "raw_key": raw_key,
        }

    await engine.dispose()
    yield data

    # Teardown
    engine = create_async_engine(_db_url())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def client(seed_data: dict[str, str]) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX AsyncClient with app engine set up manually (no lifespan)."""
    config = ServerConfig(database_url=_db_url())  # type: ignore[call-arg]
    app = create_app(config)

    # ASGITransport doesn't trigger lifespan, so set up engine manually.
    # NullPool: each request gets a fresh connection — avoids asyncpg stale
    # connection issues where last_used_at commit leaves pool connections dirty.
    app_engine = create_async_engine(_db_url(), poolclass=NullPool)
    app.state.engine = app_engine
    app.state.session_factory = async_sessionmaker(app_engine, expire_on_commit=False)

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await app_engine.dispose()
