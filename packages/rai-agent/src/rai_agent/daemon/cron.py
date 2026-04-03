"""Cron-based scheduling for the Rai daemon.

ScheduledRunEvent is emitted on the EventBus when a cron schedule fires.
CronTrigger wraps APScheduler v4 (AsyncScheduler) and satisfies RaiTrigger.

Design decisions (S2.4):
  D1: APScheduler v4 (AsyncScheduler) — async-native, built-in SQLite data store
  D2: CronTrigger (ours) wraps APSCronTrigger (APScheduler's) — no namespace collision
  D3: Flat daemon/cron.py — YAGNI, one trigger type doesn't justify a subpackage
  D4: ScheduledRunEvent extends bubus.BaseEvent — required by EventBus.emit()
  D6: RaiTrigger Protocol in triggers.py — start()/stop() for lifecycle
"""

from __future__ import annotations

from datetime import UTC, datetime

from apscheduler import AsyncScheduler, ConflictPolicy  # type: ignore[import-untyped]
from apscheduler.datastores.sqlalchemy import (
    SQLAlchemyDataStore,  # type: ignore[import-untyped]
)
from apscheduler.triggers.cron import (
    CronTrigger as APSCronTrigger,  # type: ignore[import-untyped]
)

from rai_agent.daemon.events import BaseEvent, get_bus
from rai_agent.daemon.runtime import (
    RunConfig,  # noqa: TCH001 — Pydantic needs at runtime
)

# ─── Event Model ──────────────────────────────────────────────────────────────


class ScheduledRunEvent(BaseEvent):  # type: ignore[misc]
    """Emitted on EventBus when a cron schedule fires.

    Deviation from design: extends bubus.BaseEvent (not plain BaseModel)
    because EventBus.emit() requires BaseEvent subclasses. BaseEvent itself
    extends Pydantic BaseModel, so serialization works identically.
    """

    job_id: str
    run_config: RunConfig
    scheduled_at: datetime


# ─── Module-level fire handler ────────────────────────────────────────────────

# APScheduler serializes callable + args for persistence in SQLite.
# Bound methods aren't picklable, so we use a module-level function.
# RunConfig is serialized as JSON string in the args — APScheduler persists
# it automatically, so jobs survive process restarts without a separate store.


async def _fire_handler(job_id: str, run_config_json: str) -> None:
    """Module-level handler called by APScheduler when a cron schedule fires.

    Args:
        job_id: The schedule identifier.
        run_config_json: RunConfig serialized as JSON (persisted by APScheduler).
    """
    import logging

    _log = logging.getLogger(__name__)

    try:
        run_config = RunConfig.model_validate_json(run_config_json)
    except Exception:
        _log.warning("Failed to deserialize RunConfig for job %s", job_id)
        return

    event = ScheduledRunEvent(
        job_id=job_id,
        run_config=run_config,
        scheduled_at=datetime.now(tz=UTC),
    )
    get_bus().emit(event)


# ─── CronTrigger ──────────────────────────────────────────────────────────────


class CronTrigger:
    """APScheduler v4 wrapper that emits ScheduledRunEvent on the EventBus.

    Implements RaiTrigger Protocol (start/stop lifecycle).
    Jobs persist in SQLite via APScheduler's built-in SQLAlchemyDataStore.
    RunConfig is serialized into APScheduler's args, so both the schedule
    and its payload survive process restarts.
    """

    def __init__(self, db_url: str) -> None:
        data_store = SQLAlchemyDataStore(engine_or_url=db_url)
        self._scheduler = AsyncScheduler(data_store=data_store)

    async def start(self) -> None:
        """Start the APScheduler async context."""
        await self._scheduler.__aenter__()

    async def stop(self) -> None:
        """Stop the APScheduler async context."""
        await self._scheduler.__aexit__(None, None, None)

    async def add_job(self, job_id: str, cron_expr: str, run_config: RunConfig) -> None:
        """Register a cron schedule.

        Args:
            job_id: Unique identifier for the schedule.
            cron_expr: Crontab expression (e.g. "0 7 * * *").
            run_config: RunConfig to dispatch when the schedule fires.
        """
        await self._scheduler.add_schedule(
            _fire_handler,
            APSCronTrigger.from_crontab(cron_expr),
            id=job_id,
            args=[job_id, run_config.model_dump_json()],
            conflict_policy=ConflictPolicy.replace,
        )

    async def remove_job(self, job_id: str) -> None:
        """Remove a previously registered schedule."""
        await self._scheduler.remove_schedule(job_id)
