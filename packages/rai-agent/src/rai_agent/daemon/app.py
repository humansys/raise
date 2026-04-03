"""FastAPI app factory for the Rai daemon.

create_app() wires all components together and returns a configured FastAPI app.
The lifespan context manager handles graceful startup/shutdown.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, WebSocket

from rai_agent.daemon.connection import DispatchFn, handle_connection

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    from rai_agent.daemon.auth import NonceStore
    from rai_agent.daemon.session import SessionManager


def create_app(
    session_manager: SessionManager,
    nonce_store: NonceStore,
    public_key: Ed25519PublicKey,
    dispatch: DispatchFn,
    auth_timeout: float = 10.0,
) -> FastAPI:
    """Create and configure the Rai daemon FastAPI application.

    Args:
        session_manager: Backend for session lifecycle tracking.
        nonce_store: Single-use nonce registry for auth challenges.
        public_key: Ed25519 public key for validating client tokens.
        dispatch: Callable that handles ReqFrames and sends responses.
        auth_timeout: Seconds to wait for auth frame after WS upgrade.
    """

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
        yield
        # Sessions are cleaned up in handle_connection's finally block.
        # Future: graceful drain of in-flight sessions here.

    app = FastAPI(lifespan=lifespan, title="Rai Daemon")

    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket) -> None:  # pyright: ignore[reportUnusedFunction]
        await handle_connection(
            websocket,
            session_manager,
            nonce_store,
            public_key,
            dispatch,
            auth_timeout=auth_timeout,
        )

    return app
