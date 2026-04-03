"""Trigger protocols for the Rai daemon (ADR-003).

RaiTrigger defines the lifecycle contract for all trigger sources.
Implementations: CronTrigger (S2.4), TelegramTrigger (S2.5).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class RaiTrigger(Protocol):
    """Lifecycle contract for trigger sources (ADR-003).

    Implementations: CronTrigger (S2.4), TelegramTrigger (future S2.5).
    """

    async def start(self) -> None: ...
    async def stop(self) -> None: ...
