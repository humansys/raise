"""Composite documentation target — delegates to multiple targets.

Publishes to ALL targets (e.g. filesystem + Confluence). Reads (get_page,
search, health) delegate to the remote target (last in list — typically Confluence).

Filesystem is first for durability: local copy always saved.
Result prefers last successful publish (remote URL over local path).
If remote fails, returns success with warning (local copy is the guarantee).

RAISE-1051 (S1051.7)
"""

from __future__ import annotations

import logging
from typing import Any

from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth

logger = logging.getLogger(__name__)


class CompositeDocTarget:
    """Delegates to multiple DocumentationTargets.

    - publish: calls all targets; returns last successful result (remote preferred)
    - get_page / search / health: delegate to remote (last) target
    - Filesystem first for durability, Confluence last for the URL
    """

    def __init__(self, targets: list[Any]) -> None:
        self._targets = targets
        self._remote = targets[-1]  # last target = remote (Confluence)

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        """True if any wrapped target can publish."""
        return any(t.can_publish(doc_type, metadata) for t in self._targets)

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish to all accepting targets. Return best result.

        Prefers last successful result (remote URL). If remote fails but
        local succeeded, returns success with sync-pending warning.
        """
        results: list[PublishResult] = []
        failures: list[str] = []

        for target in self._targets:
            if target.can_publish(doc_type, metadata):
                try:
                    result: PublishResult = target.publish(doc_type, content, metadata)
                    results.append(result)
                    if not result.success:
                        failures.append(result.message)
                except Exception as exc:
                    logger.warning("Composite publish failed on %s: %s", type(target).__name__, exc)
                    failures.append(str(exc))

        if not results:
            return PublishResult(
                success=False, message="No target accepted this doc_type"
            )

        # Prefer last successful result (remote URL over local path)
        successful = [r for r in results if r.success]
        if successful:
            best = successful[-1]  # last success = remote if available
            if failures:
                return PublishResult(
                    success=True,
                    url=best.url,
                    message=f"{best.message} (sync pending: {'; '.join(failures)})",
                )
            return best

        # All failed — return first failure
        return results[0]

    def get_page(self, identifier: str) -> PageContent:
        """Delegate to remote (last) target."""
        return self._remote.get_page(identifier)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Delegate to remote (last) target."""
        return self._remote.search(query, limit=limit)

    def health(self) -> AdapterHealth:
        """Delegate to remote (last) target."""
        return self._remote.health()
