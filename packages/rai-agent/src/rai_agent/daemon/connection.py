"""WebSocket connection lifecycle for the Rai daemon.

handle_connection() orchestrates:
  1. Accept WS connection
  2. Authenticate (challenge-response — loopback NOT exempt)
  3. Create session
  4. Run receive_loop + dispatch_loop concurrently via asyncio.TaskGroup
  5. Clean up session on disconnect or error
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from fastapi.websockets import WebSocketDisconnect
from pydantic import ValidationError

from rai_agent.daemon.auth import AuthError, NonceStore, authenticate
from rai_agent.daemon.protocol import ReqFrame, ResFrame
from rai_agent.daemon.runtime import RunConfig

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from fastapi import WebSocket

    from rai_agent.daemon.runtime import RaiAgentRuntime
    from rai_agent.daemon.session import SessionManager

_log = logging.getLogger(__name__)

# Dispatcher: handles a validated ReqFrame and sends responses via send()
DispatchFn = Callable[[ReqFrame, Callable[[str], Awaitable[None]]], Awaitable[None]]


def make_dispatch(
    runtime: RaiAgentRuntime,
    shutdown_callback: Callable[[], None] | None = None,
) -> DispatchFn:
    """Build a DispatchFn backed by a real RaiAgentRuntime.

    Handles:
    - method="run": builds RunConfig from params, calls runtime.run()
    - method="resume": calls runtime.resume() using session_id from params
    - method="shutdown": calls shutdown_callback if provided
    - unknown method: sends ResFrame(ok=False)

    Note: agent_session_id persistence into SessionState is deferred to S2.4
    when SQLiteSessionManager introduces the full session scheme.
    """

    async def dispatch(
        frame: ReqFrame,
        send: Callable[[str], Awaitable[None]],
    ) -> None:
        if frame.method == "shutdown":
            if shutdown_callback is not None:
                shutdown_callback()
                res = ResFrame(type="res", id=frame.id, ok=True)
                await send(res.model_dump_json())
            else:
                err = ResFrame(
                    type="res",
                    id=frame.id,
                    ok=False,
                    error="shutdown not configured",
                )
                await send(err.model_dump_json())
            return

        if frame.method == "run":
            try:
                config = RunConfig(**frame.params)
            except Exception as exc:
                err = ResFrame(
                    type="res", id=frame.id, ok=False, error=f"invalid params: {exc}"
                )
                await send(err.model_dump_json())
                return
            await runtime.run(config, send)

        elif frame.method == "resume":
            try:
                config = RunConfig(**frame.params)
            except Exception as exc:
                err = ResFrame(
                    type="res", id=frame.id, ok=False, error=f"invalid params: {exc}"
                )
                await send(err.model_dump_json())
                return
            session_id = frame.params.get("session_id")
            if not session_id or not isinstance(session_id, str):
                err = ResFrame(
                    type="res",
                    id=frame.id,
                    ok=False,
                    error="resume requires session_id param",
                )
                await send(err.model_dump_json())
                return
            await runtime.resume(config, session_id, send)

        else:
            err = ResFrame(
                type="res",
                id=frame.id,
                ok=False,
                error=f"unknown method: {frame.method}",
            )
            await send(err.model_dump_json())

    return dispatch


async def handle_connection(
    websocket: WebSocket,
    session_manager: SessionManager,
    nonce_store: NonceStore,
    public_key: Ed25519PublicKey,
    dispatch: DispatchFn,
    auth_timeout: float = 10.0,
) -> None:
    """Full connection lifecycle: auth → session → receive/dispatch loops → cleanup.

    SECURITY: authenticate() is called for ALL connections.
    Loopback origin does NOT bypass auth (ClawJacked prevention).
    """
    await websocket.accept()

    try:
        session_key = await authenticate(
            websocket, nonce_store, public_key, auth_timeout
        )
    except AuthError:
        await websocket.close(code=4401)
        return

    session = session_manager.create(session_key)
    # Bounded queue provides backpressure — prevents unbounded memory growth
    queue: asyncio.Queue[ReqFrame | None] = asyncio.Queue(maxsize=256)

    async def receive_loop() -> None:
        """Read frames from WS and enqueue them. Puts None sentinel on disconnect."""
        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    frame = ReqFrame.model_validate_json(raw)
                    await queue.put(frame)
                except ValidationError:
                    pass  # ignore malformed frames silently
        except WebSocketDisconnect:
            # R2: put_nowait avoids blocking if queue is full at disconnect time
            try:
                queue.put_nowait(None)
            except asyncio.QueueFull:
                queue.get_nowait()  # drop one frame to make space for sentinel
                queue.put_nowait(None)

    async def dispatch_loop() -> None:
        """Dequeue frames and dispatch to handler until sentinel received."""
        send = websocket.send_text
        while True:
            frame = await queue.get()
            if frame is None:
                break  # sentinel: connection closed
            await dispatch(frame, send)

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(receive_loop())
            tg.create_task(dispatch_loop())
    except* Exception as eg:
        # WebSocketDisconnect is handled inside receive_loop via sentinel.
        # Anything reaching here is unexpected — log for debugging.
        _log.warning(
            "Unexpected error in connection tasks for %s: %s",
            session.session_key,
            eg,
        )
    finally:
        session_manager.remove(session.session_key)
