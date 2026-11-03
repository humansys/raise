"""SessionCatalog — orchestrates queries across CatalogSource backends."""

from __future__ import annotations

import logging

from raise_cli.session.catalog.models import CatalogFilter, RuntimeSessionRecord
from raise_cli.session.catalog.source import CatalogSource

logger = logging.getLogger(__name__)


class SessionCatalog:
    """Query runtime sessions across one or more ``CatalogSource`` backends.

    Sources are queried concurrently in S3 (network discovery). For S1,
    a single ``LocalCatalogSource`` is sufficient.
    """

    def __init__(self, sources: list[CatalogSource]) -> None:
        self._sources = sources

    def query(
        self,
        filters: CatalogFilter,
        *,
        timeout_s: float = 5.0,
    ) -> list[RuntimeSessionRecord]:
        """Query all sources and return a merged, deduplicated record list."""
        records: list[RuntimeSessionRecord] = []
        seen: set[str] = set()

        for source in self._sources:
            try:
                result = source.query(filters, timeout_s=timeout_s)
                if result.error:
                    logger.warning(
                        "CatalogSource %s returned error: %s",
                        source.source_id,
                        result.error,
                    )
                    continue
                for rec in result.records:
                    key = f"{source.source_id}:{rec.session_id}"
                    if key not in seen:
                        seen.add(key)
                        records.append(rec)
            except Exception as exc:  # noqa: BLE001 — catalog sources are fail-open
                logger.warning("CatalogSource %s failed: %s", source.source_id, exc)

        return records
