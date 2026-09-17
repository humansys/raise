"""Check registry with entry point discovery.

Discovers DoctorCheck implementations registered via Python entry points
(``[project.entry-points."rai.doctor.checks"]`` in pyproject.toml).

Architecture: ADR-045, same discovery pattern as gates (ADR-039 S3).
"""

from __future__ import annotations

import inspect
import logging
from importlib.metadata import entry_points
from typing import Any

from raise_cli.doctor.protocol import DoctorCheck

logger = logging.getLogger(__name__)

EP_DOCTOR: str = "rai.doctor.checks"


def _dist_name(ep: Any) -> str:
    """Best-effort extraction of the distribution name for an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


class CheckRegistry:
    """Discovers and manages DoctorCheck implementations.

    Example::

        registry = CheckRegistry()
        registry.discover()

        for check in registry.checks:
            print(f"{check.check_id}: {check.description}")
    """

    def __init__(self) -> None:
        self._checks: list[DoctorCheck] = []

    @property
    def checks(self) -> list[DoctorCheck]:
        """Return a copy of registered checks."""
        return list(self._checks)

    def discover(self) -> None:
        """Load checks from ``rai.doctor.checks`` entry points.

        Skips entry points that fail to load, are not classes, or don't
        conform to the DoctorCheck Protocol.
        """
        for ep in entry_points(group=EP_DOCTOR):
            try:
                loaded: Any = ep.load()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Skipping doctor check '%s' from '%s': %s",
                    ep.name,
                    _dist_name(ep),
                    exc,
                )
                continue

            if not inspect.isclass(loaded):
                logger.warning(
                    "Skipping doctor check '%s': expected a class, got %s",
                    ep.name,
                    type(loaded).__name__,
                )
                continue

            instance = loaded()
            if not isinstance(instance, DoctorCheck):
                logger.warning(
                    "Skipping doctor check '%s': does not conform to DoctorCheck Protocol",
                    ep.name,
                )
                continue

            self._checks.append(instance)
            logger.debug(
                "Loaded doctor check '%s' (category=%s)", ep.name, instance.category
            )

    def register(self, check: DoctorCheck | Any) -> None:
        """Manually register a check instance (useful for testing)."""
        if not isinstance(check, DoctorCheck):
            logger.warning(
                "Skipping manual check registration: %s does not conform to DoctorCheck",
                type(check).__name__,
            )
            return
        self._checks.append(check)

    def get_checks_for_category(self, category: str) -> list[DoctorCheck]:
        """Return checks matching the given category."""
        return [c for c in self._checks if c.category == category]
