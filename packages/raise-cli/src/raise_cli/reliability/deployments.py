"""Deployment-event registration — the configurable production boundary (RAISE-11493).

Without a record of real deploys, "escaped to production" is measured against an
invented boundary (measurement trap 4). ``DeploymentEventStore`` persists deploy
events to an append-only JSONL file under ``.raise/`` (never the SQLite DB — E8204
discipline) and exposes the production boundary the reliability lens needs.

Registering deploys also unlocks the ``per_deployment`` denominator that S11487.2
left as a None+reason slot.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

__all__ = ["DeploymentEvent", "DeploymentEventStore"]

_log = logging.getLogger(__name__)

_STORE_RELPATH = Path(".raise") / "reliability" / "deployments.jsonl"


class DeploymentEvent(BaseModel):
    """One deployment of a ref to an environment."""

    deployed_at: datetime
    """When the deploy happened (UTC recommended)."""

    ref: str
    """Deployed git ref — a commit SHA or tag."""

    environment: str
    """Target environment, e.g. 'prod', 'staging'."""

    version: str | None = None
    """Optional human version label."""

    source: Literal["manual", "ci"] = "manual"
    """How the event was registered."""


class DeploymentEventStore:
    """Append-only JSONL store of deployment events.

    The store is intentionally simple and crash-tolerant: ``register`` appends one
    JSON line; ``list`` reads and skips malformed lines (degrading honestly rather
    than crashing the lens).
    """

    def __init__(self, repo_path: Path, *, prod_environment: str = "prod") -> None:
        """Initialise the store.

        Args:
            repo_path: Repository root; the store lives at
                ``<repo>/.raise/reliability/deployments.jsonl``.
            prod_environment: Which ``environment`` value counts as production.
        """
        self._path = repo_path / _STORE_RELPATH
        self.prod_environment = prod_environment

    @property
    def path(self) -> Path:
        """Absolute path to the JSONL store file."""
        return self._path

    def register(self, event: DeploymentEvent) -> None:
        """Append one deployment event to the store (creates the file/dir if absent)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = event.model_dump_json()
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def list(
        self,
        *,
        environment: str | None = None,
        since: date | None = None,
    ) -> list[DeploymentEvent]:
        """Return stored events, optionally filtered.

        Malformed lines are skipped (logged at debug). Missing file → empty list.

        Args:
            environment: If set, only events for this environment.
            since: If set, only events whose date is >= this date.

        Returns:
            Events in stored (chronological-append) order.
        """
        if not self._path.exists():
            return []

        events: list[DeploymentEvent] = []
        for raw in self._path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                event = DeploymentEvent.model_validate_json(raw)
            except ValueError:
                _log.debug("skipping malformed deployment line: %s", raw[:80])
                continue
            if environment is not None and event.environment != environment:
                continue
            if since is not None and event.deployed_at.date() < since:
                continue
            events.append(event)
        return events

    def prod_deploy_dates(self, *, since: date | None = None) -> list[date]:
        """Convenience: dates of deploys to the production environment."""
        return [
            e.deployed_at.date()
            for e in self.list(environment=self.prod_environment, since=since)
        ]
