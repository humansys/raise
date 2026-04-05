"""Per-session FIFO dispatcher for the Rai daemon.

Serializes requests within a session via asyncio queues, isolates sessions
from each other, and applies backpressure when a session queue is full.

No integration with registry or middleware — pure concurrency infrastructure.
S5.5 wires the dispatcher into the Telegram pipeline.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

__all__ = [
    "SessionBusyError",
    "SessionDispatcher",
    "SessionRequest",
]

_log = logging.getLogger(__name__)

_DEFAULT_MAXSIZE = 10
_DEFAULT_IDLE_TIMEOUT = 300.0  # 5 minutes


@dataclass
class SessionRequest:
    """Provider-agnostic request dispatched through the session pipeline.

    Built by provider triggers (Telegram, Google Chat, etc.) with
    their own callbacks. The dispatcher and worker never know which
    provider sent the request.
    """

    session_key: str
    prompt: str
    send: Callable[[str], Awaitable[None]]
    on_complete: Callable[[], Awaitable[None]]
    on_error: Callable[[Exception], Awaitable[None]]
    content_blocks: list[dict[str, Any]] | None = None
    """Multimodal content blocks (images + text) from provider."""
    metadata: dict[str, Any] = field(
        default_factory=lambda: dict[str, Any](),
    )


class SessionBusyError(Exception):
    """Raised when a session queue is full (backpressure signal)."""


class SessionDispatcher:
    """Per-session FIFO dispatcher with lazy workers.

    Each session key gets its own ``asyncio.Queue`` and worker task.
    Workers are created lazily on first dispatch. The handler callable
    is invoked once per request, in FIFO order within a session.
    """

    def __init__(
        self,
        handler: Callable[[SessionRequest], Awaitable[None]] | None = None,
        *,
        maxsize: int = _DEFAULT_MAXSIZE,
        idle_timeout: float = _DEFAULT_IDLE_TIMEOUT,
    ) -> None:
        self._handler = handler
        self._maxsize = maxsize
        self._idle_timeout = idle_timeout
        self._queues: dict[str, asyncio.Queue[SessionRequest]] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}

    def set_handler(
        self,
        handler: Callable[[SessionRequest], Awaitable[None]],
    ) -> None:
        """Set or replace the request handler (deferred wiring)."""
        self._handler = handler

    @property
    def active_session_count(self) -> int:
        """Number of sessions with active workers."""
        return len(self._workers)

    @property
    def active_queue_count(self) -> int:
        """Number of sessions with active queues."""
        return len(self._queues)

    async def dispatch(self, request: SessionRequest) -> None:
        """Enqueue a request, creating queue + worker lazily.

        Raises:
            SessionBusyError: If the session queue is full.
        """
        if self._handler is None:
            msg = "No handler set — call set_handler() before dispatching"
            raise RuntimeError(msg)

        key = request.session_key

        # Get or create queue
        if key not in self._queues:
            self._queues[key] = asyncio.Queue(maxsize=self._maxsize)

        queue = self._queues[key]

        # Enqueue (non-blocking — raises QueueFull if at capacity)
        try:
            queue.put_nowait(request)
        except asyncio.QueueFull:
            raise SessionBusyError(key) from None

        # Create worker if missing or done (AR-Q1: task.done() race guard)
        if key not in self._workers or self._workers[key].done():
            self._workers[key] = asyncio.create_task(
                self._run_worker(key, queue),
            )

    async def _run_worker(
        self,
        key: str,
        queue: asyncio.Queue[SessionRequest],
    ) -> None:
        """Worker loop: process requests from queue in FIFO order."""
        assert self._handler is not None  # guaranteed by dispatch() guard
        handler = self._handler
        try:
            while True:
                request = await asyncio.wait_for(
                    queue.get(),
                    timeout=self._idle_timeout,
                )
                try:
                    await handler(request)
                    await request.on_complete()
                except Exception as exc:  # noqa: BLE001
                    try:
                        await request.on_error(exc)
                    except Exception:  # noqa: BLE001
                        _log.exception(
                            "on_error callback failed for %s",
                            key,
                        )
        except TimeoutError:
            _log.debug("Worker idle timeout for %s", key)
        except asyncio.CancelledError:
            return
        finally:
            # Cleanup: remove queue and worker from dicts
            self._queues.pop(key, None)
            self._workers.pop(key, None)

    async def shutdown(self) -> None:
        """Cancel all workers and clean up."""
        tasks = list(self._workers.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._workers.clear()
        self._queues.clear()
