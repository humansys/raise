"""Event emitter for lifecycle hooks.

Dispatches typed events to registered handlers with error isolation.
Handlers that raise exceptions are logged and skipped — the CLI never
crashes from a handler failure.

When a ``HookRegistry`` is provided, discovered hooks are auto-registered
and dispatched in priority order with per-hook timeout enforcement.

Architecture: ADR-039 §4 (Synchronous execution with error isolation)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import TYPE_CHECKING

from raise_cli.hooks.events import EmitResult, HookEvent, HookResult
from raise_cli.hooks.protocol import LifecycleHook

if TYPE_CHECKING:
    from raise_cli.hooks.registry import HookRegistry

logger = logging.getLogger(__name__)

HandlerFn = Callable[[HookEvent], HookResult]


class EventEmitter:
    """Dispatches lifecycle events to registered handlers.

    Handlers are called in registration order per event name.
    For ``before:`` events, if any handler returns ``abort``, the emit
    result signals that the operation should be aborted.

    When ``registry`` is provided, discovered hooks are auto-registered
    and dispatched in priority order with per-hook timeout.

    Example::

        emitter = EventEmitter()
        emitter.register("session:start", my_handler)
        result = emitter.emit(SessionStartEvent(session_id="SES-1"))

    With registry::

        registry = HookRegistry()
        registry.discover()
        emitter = EventEmitter(registry=registry)
        result = emitter.emit(SessionStartEvent(session_id="SES-1"))
    """

    DEFAULT_TIMEOUT: float = 5.0

    def __init__(self, registry: HookRegistry | None = None) -> None:
        self._handlers: dict[str, list[HandlerFn]] = defaultdict(list)
        self._registry = registry

    def register(self, event_name: str, handler: HandlerFn) -> None:
        """Register a handler for a specific event name."""
        self._handlers[event_name].append(handler)

    def emit(self, event: HookEvent) -> EmitResult:
        """Dispatch event to all registered handlers.

        For ``before:`` events, if any handler returns ``abort``,
        returns ``EmitResult(aborted=True)``. Remaining handlers
        are still called (all-notify semantics).

        Handler exceptions and timeouts are caught, logged, and
        reported in ``EmitResult.handler_errors``.
        """
        errors: list[str] = []
        aborted = False
        abort_message = ""

        # Phase 1: Registry hooks (priority-sorted, with timeout)
        if self._registry is not None:
            hooks = self._registry.get_hooks_for_event(event.event_name)
            for hook in hooks:
                result = self._call_hook_with_timeout(hook, event, errors)
                if result is not None:
                    aborted, abort_message = self._check_abort(
                        result, event.event_name, aborted, abort_message
                    )

        # Phase 2: Manual handlers (registration order, no timeout)
        handlers = self._handlers.get(event.event_name, [])
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

            aborted, abort_message = self._check_abort(
                result, event.event_name, aborted, abort_message
            )

        return EmitResult(
            aborted=aborted,
            abort_message=abort_message,
            handler_errors=tuple(errors),
        )

    def _call_hook_with_timeout(
        self,
        hook: LifecycleHook,
        event: HookEvent,
        errors: list[str],
    ) -> HookResult | None:
        """Call a hook's handle() with timeout enforcement.

        Returns the HookResult on success, or None on error/timeout.
        """
        timeout: float = getattr(hook, "timeout", self.DEFAULT_TIMEOUT)
        hook_name = type(hook).__name__

        executor = ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(hook.handle, event)
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            error_msg = f"TimeoutError: {hook_name} exceeded {timeout}s timeout"
            errors.append(error_msg)
            logger.warning(
                "Hook %s timed out after %ss for event '%s'",
                hook_name,
                timeout,
                event.event_name,
            )
            return None
        except Exception as exc:  # noqa: BLE001
            error_msg = f"{type(exc).__name__}: {exc}"
            errors.append(error_msg)
            logger.warning(
                "Hook %s raised %s for event '%s'",
                hook_name,
                error_msg,
                event.event_name,
            )
            return None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    @staticmethod
    def _check_abort(
        result: HookResult,
        event_name: str,
        aborted: bool,
        abort_message: str,
    ) -> tuple[bool, str]:
        """Check if a handler result triggers abort (before: events only)."""
        if (
            result.status == "abort"
            and event_name.startswith("before:")
            and not aborted
        ):
            return True, result.message
        return aborted, abort_message


def create_emitter() -> EventEmitter:
    """Create an EventEmitter with a discovered HookRegistry.

    Convenience factory that avoids repeating registry setup in every
    CLI command. Discovers hooks from ``rai.hooks`` entry points.
    """
    from raise_cli.hooks.registry import HookRegistry

    registry = HookRegistry()
    registry.discover()
    return EventEmitter(registry=registry)
