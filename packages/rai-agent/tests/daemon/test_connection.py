"""Tests for FastAPI WS app + connection lifecycle."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from rai_agent.daemon.app import create_app
from rai_agent.daemon.auth import NonceStore
from rai_agent.daemon.protocol import ReqFrame, ResFrame
from rai_agent.daemon.session import InMemorySessionManager

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _sign_token(private_key: Ed25519PrivateKey, nonce: str) -> str:
    return base64.b64encode(private_key.sign(nonce.encode())).decode()


async def _stub_dispatch(req: ReqFrame, send: Callable[[str], Awaitable[None]]) -> None:
    """Stub dispatcher: echoes request id back in a ResFrame."""
    res = ResFrame(type="res", id=req.id, ok=True, payload={"echo": req.method})
    await send(res.model_dump_json())


def _make_app(private_key: Ed25519PrivateKey, auth_timeout: float = 10.0) -> Any:
    return create_app(
        session_manager=InMemorySessionManager(),
        nonce_store=NonceStore(),
        public_key=private_key.public_key(),
        dispatch=_stub_dispatch,
        auth_timeout=auth_timeout,
    )


def _do_auth(ws: Any, private_key: Ed25519PrivateKey) -> dict[str, Any]:
    """Perform the full auth handshake. Returns the auth ResFrame payload."""
    import uuid

    # 1. Receive challenge
    challenge = ws.receive_json()
    assert challenge["event"] == "auth_challenge"
    nonce = challenge["payload"]["nonce"]

    # 2. Send auth req
    ws.send_json(
        {
            "type": "req",
            "id": str(uuid.uuid4()),
            "method": "auth",
            "params": {"token": _sign_token(private_key, nonce)},
        }
    )

    # 3. Receive auth success
    return ws.receive_json()  # type: ignore[no-any-return]


# ─── Connection tests ─────────────────────────────────────────────────────────


class TestConnection:
    def test_unauthenticated_client_gets_closed_4401(self) -> None:
        """Client that doesn't send auth token is disconnected with 4401."""
        private_key = Ed25519PrivateKey.generate()
        app = _make_app(private_key, auth_timeout=0.05)

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:  # noqa: SIM117
                with client.websocket_connect("/ws") as ws:
                    ws.receive_json()  # challenge
                    # Don't send auth — let timeout fire
                    ws.receive_json()  # expects close
            assert exc_info.value.code == 4401

    def test_authenticated_client_receives_stub_response(self) -> None:
        """Authenticated client can send a req and receive a response."""
        import uuid

        private_key = Ed25519PrivateKey.generate()
        app = _make_app(private_key)

        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            auth_res = _do_auth(ws, private_key)
            assert auth_res["ok"] is True

            req_id = str(uuid.uuid4())
            ws.send_json(
                {
                    "type": "req",
                    "id": req_id,
                    "method": "run",
                    "params": {"prompt": "hello"},
                }
            )
            res = ws.receive_json()
            assert res["id"] == req_id
            assert res["ok"] is True

    def test_invalid_token_gets_closed_4401(self) -> None:
        """Client with wrong Ed25519 signature is disconnected with 4401."""
        import uuid

        private_key = Ed25519PrivateKey.generate()
        wrong_key = Ed25519PrivateKey.generate()
        app = _make_app(private_key)

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:  # noqa: SIM117
                with client.websocket_connect("/ws") as ws:
                    challenge = ws.receive_json()
                    nonce = challenge["payload"]["nonce"]
                    ws.send_json(
                        {
                            "type": "req",
                            "id": str(uuid.uuid4()),
                            "method": "auth",
                            "params": {"token": _sign_token(wrong_key, nonce)},
                        }
                    )
                    ws.receive_json()  # expects close
            assert exc_info.value.code == 4401

    def test_session_created_and_removed_on_disconnect(self) -> None:
        """Session is removed from manager after client disconnects."""
        private_key = Ed25519PrivateKey.generate()
        session_manager = InMemorySessionManager()
        app = create_app(
            session_manager=session_manager,
            nonce_store=NonceStore(),
            public_key=private_key.public_key(),
            dispatch=_stub_dispatch,
        )

        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            auth_res = _do_auth(ws, private_key)
            assert auth_res["ok"] is True
            # Session exists while connected
            assert len(session_manager) == 1

        # Session removed after disconnect
        assert len(session_manager) == 0

    def test_loopback_origin_requires_auth(self) -> None:
        """ClawJacked prevention: loopback connection is NOT exempt from auth."""
        private_key = Ed25519PrivateKey.generate()
        app = _make_app(private_key, auth_timeout=0.05)

        # TestClient connects from loopback — still requires auth
        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:  # noqa: SIM117
                with client.websocket_connect("/ws") as ws:
                    ws.receive_json()  # challenge
                    ws.receive_json()  # times out → 4401
            assert exc_info.value.code == 4401
