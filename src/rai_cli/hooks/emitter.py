"""Event emitter for lifecycle hooks.

Dispatches typed events to registered handlers with error isolation.
Handlers that raise exceptions are logged and skipped — the CLI never
crashes from a handler failure.

Architecture: ADR-039 §4 (Synchronous execution with error isolation)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable

from rai_cli.hooks.events import EmitResult, HookEvent, HookResult

logger = logging.getLogger(__name__)

HandlerFn = Callable[[HookEvent], HookResult]


class EventEmitter:
    """Dispatches lifecycle events to registered handlers.

    Handlers are called in registration order per event name.
    For ``before:`` events, if any handler returns ``abort``, the emit
    result signals that the operation should be aborted.

    Example::

        emitter = EventEmitter()
        emitter.register("session:start", my_handler)
        result = emitter.emit(SessionStartEvent(session_id="SES-1"))
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[HandlerFn]] = defaultdict(list)

    def register(self, event_name: str, handler: HandlerFn) -> None:
        """Register a handler for a specific event name."""
        self._handlers[event_name].append(handler)

    def emit(self, event: HookEvent) -> EmitResult:
        """Dispatch event to all registered handlers.

        For ``before:`` events, if any handler returns ``abort``,
        returns ``EmitResult(aborted=True)``. Remaining handlers
        are still called (all-notify semantics).

        Handler exceptions are caught, logged, and reported in
        ``EmitResult.handler_errors``.
        """
        handlers = self._handlers.get(event.event_name, [])
        errors: list[str] = []
        aborted = False
        abort_message = ""

        for handler in handlers:
            try:
                result = handler(event)
            except Exception as exc:  # noqa: BLE001
                error_msg = f"{type(exc).__name__}: {exc}"
                errors.append(error_msg)
                logger.warning(
                    "Hook handler %s raised %s for event '%s'",
                    getattr(handler, "__name__", repr(handler)),
                    error_msg,
                    event.event_name,
                )
                continue

            if (
                result.status == "abort"
                and event.event_name.startswith("before:")
                and not aborted
            ):
                aborted = True
                abort_message = result.message

        return EmitResult(
            aborted=aborted,
            abort_message=abort_message,
            handler_errors=tuple(errors),
        )
