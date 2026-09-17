"""DegradedBanner widget — staleness banner for a degraded data source.

Docked top (below FilterBar), hidden by default; shown when either the
session or worktree source reports unhealthy (D-S3.7). Owns no health
state itself — ``CockpitApp`` decides *when* to show/hide and supplies
``last_sync``; this widget only formats and renders the text.
"""

from __future__ import annotations

from datetime import UTC, datetime

from textual.widgets import Static

from raise_cli.cockpit.tui.services import format_last_sync


class DegradedBanner(Static):
    """Single-line banner: ``DB degraded — last sync: {age} · [r] retry``."""

    def __init__(self) -> None:
        super().__init__()
        self._text: str = ""

    def show_degraded(
        self, last_sync: datetime | None, *, now: datetime | None = None
    ) -> None:
        """Reveal the banner with an age fragment computed from *last_sync*."""
        age = format_last_sync(last_sync, now or datetime.now(UTC))
        self._text = f"DB degraded — last sync: {age} · \\[r] retry"
        self.add_class("visible")
        self.refresh()

    def hide(self) -> None:
        """Hide the banner (both sources healthy again)."""
        self.remove_class("visible")
        self.refresh()

    def render(self) -> str:
        """Render the current banner text (empty when never shown)."""
        return self._text
