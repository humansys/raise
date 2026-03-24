"""Internal EventBus for the Rai daemon.

Minimal async event bus — replaces bubus (yanked from PyPI, see RAI-28).
Isolated here: if replaced by NATS/Redis at scale, only this module changes.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)

# ─── BaseEvent ───────────────────────────────────────────────────────────────


class BaseEvent(BaseModel):
    """Base class for all daemon events.

    Extends Pydantic BaseModel — serialization, validation, and
    type safety come for free. The event_type property returns the
    class name, used as the routing key on the bus.
    """

    @property
    def event_type(self) -> str:
        return type(self).__name__


# ─── EventBus ────────────────────────────────────────────────────────────────

Handler = Callable[..., Any]


class EventBus:
    """Minimal async event bus with string-keyed dispatch.

    Supports both sync and async handlers. Handlers are called
    inline in the emitting coroutine's context (no background tasks).
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def on(self, event_name: str, handler: Handler) -> None:
        """Subscribe a handler to an event name."""
        self._handlers[event_name].append(handler)

    def emit(self, event: BaseEvent) -> None:
        """Dispatch an event to all registered handlers.

        Handlers run inline. Async handlers are scheduled as tasks
        on the running event loop. Exceptions are logged, not raised.
        """
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    asyncio.ensure_future(result)
            except Exception:
                _log.exception(
                    "Handler %s failed for %s",
                    getattr(handler, "__name__", repr(handler)),
                    event.event_type,
                )

    @property
    def handlers(self) -> dict[str, list[Handler]]:
        """Expose handlers for testing introspection."""
        return dict(self._handlers)


# ─── Singleton ───────────────────────────────────────────────────────────────

_bus: EventBus | None = None


def get_bus() -> EventBus:
    """Return the daemon-wide EventBus singleton."""
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus


def reset_bus() -> None:
    """Reset the singleton. For testing only."""
    global _bus
    _bus = None
