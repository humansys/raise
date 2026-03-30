"""Composite documentation target — delegates to multiple targets.

Publishes to ALL targets (e.g. filesystem + Confluence). Reads (get_page,
search, health) delegate to the primary target (first in list).

RAISE-1051 (S1051.7)
"""

from __future__ import annotations

from typing import Any

from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth


class CompositeDocTarget:
    """Delegates to multiple DocumentationTargets.

    - publish: calls all targets that accept the doc_type
    - get_page / search / health: delegate to primary (first) target
    - Primary result comes from first target that publishes
    """

    def __init__(self, targets: list[Any]) -> None:
        self._targets = targets
        self._primary = targets[0]

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        """True if any wrapped target can publish."""
        return any(t.can_publish(doc_type, metadata) for t in self._targets)

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish to all accepting targets. Return primary result."""
        primary_result: PublishResult | None = None
        for target in self._targets:
            if target.can_publish(doc_type, metadata):
                result: PublishResult = target.publish(doc_type, content, metadata)
                if primary_result is None:
                    primary_result = result
        return primary_result or PublishResult(
            success=False, message="No target accepted this doc_type"
        )

    def get_page(self, identifier: str) -> PageContent:
        """Delegate to primary target."""
        return self._primary.get_page(identifier)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Delegate to primary target."""
        return self._primary.search(query, limit=limit)

    def health(self) -> AdapterHealth:
        """Delegate to primary target."""
        return self._primary.health()
