"""E2E integration tests for the Rai daemon.

Starts a real uvicorn server on a random port.
Connects with real websockets client (not TestClient stubs).
Validates the full auth → run → disconnect lifecycle.
"""

from __future__ import annotations

import asyncio
import base64
import json
import uuid
from typing import TYPE_CHECKING, Any

import pytest
import uvicorn
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError

from rai_agent.daemon.app import create_app
from rai_agent.daemon.auth import NonceStore
from rai_agent.daemon.connection import make_dispatch
from rai_agent.daemon.protocol import ReqFrame, ResFrame
from rai_agent.daemon.session import InMemorySessionManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# ─── Stub dispatcher ─────────────────────────────────────────────────────────


async def _stub_dispatch(
    req: ReqFrame, send: Any
) -> None:
    res = ResFrame(type="res", id=req.id, ok=True, payload={"method": req.method})
    await send(res.model_dump_json())


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
async def running_daemon() -> AsyncGenerator[tuple[str, Ed25519PrivateKey], None]:
    """Start a real uvicorn daemon on a random port. Yields (ws_url, private_key)."""
    private_key = Ed25519PrivateKey.generate()

    app = create_app(
        session_manager=InMemorySessionManager(),
        nonce_store=NonceStore(),
        public_key=private_key.public_key(),
        dispatch=_stub_dispatch,
        auth_timeout=5.0,
    )

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=0,  # OS assigns a free port
        log_level="warning",
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    serve_task = asyncio.create_task(server.serve())

    # Wait for server to be ready
    while not server.started:
        await asyncio.sleep(0.01)

    port: int = server.servers[0].sockets[0].getsockname()[1]  # type: ignore[index]
    ws_url = f"ws://127.0.0.1:{port}/ws"

    yield ws_url, private_key

    server.should_exit = True
    await serve_task


# ─── Client helper ────────────────────────────────────────────────────────────


async def _authenticate_client(
    ws: Any, private_key: Ed25519PrivateKey
) -> dict[str, Any]:
    """Perform the full auth handshake on a real WS connection."""
    challenge_raw = await ws.recv()
    challenge = json.loads(challenge_raw)
    assert challenge["event"] == "auth_challenge"
    nonce: str = challenge["payload"]["nonce"]

    sig = private_key.sign(nonce.encode())
    token = base64.b64encode(sig).decode()

    auth_req = {
        "type": "req",
        "id": str(uuid.uuid4()),
        "method": "auth",
        "params": {"token": token},
    }
    await ws.send(json.dumps(auth_req))

    auth_res_raw = await ws.recv()
    return json.loads(auth_res_raw)  # type: ignore[no-any-return]


# ─── Tests ────────────────────────────────────────────────────────────────────


async def test_happy_path_auth_and_run(
    running_daemon: tuple[str, Ed25519PrivateKey],
) -> None:
    """Client authenticates and sends a run request — receives a valid response."""
    ws_url, private_key = running_daemon

    async with ws_connect(ws_url) as ws:
        auth_res = await _authenticate_client(ws, private_key)
        assert auth_res["ok"] is True, f"Auth failed: {auth_res}"

        req_id = str(uuid.uuid4())
        run_req = json.dumps({
            "type": "req",
            "id": req_id,
            "method": "run",
            "params": {"prompt": "what is the capital of France?"},
        })
        await ws.send(run_req)

        res_raw = await ws.recv()
        res = json.loads(res_raw)
        assert res["id"] == req_id
        assert res["ok"] is True
        assert res["payload"]["method"] == "run"


async def test_unauthenticated_client_rejected(
    running_daemon: tuple[str, Ed25519PrivateKey],
) -> None:
    """Client that skips auth is disconnected with close code 4401."""
    ws_url, _ = running_daemon

    with pytest.raises(ConnectionClosedError) as exc_info:
        async with ws_connect(ws_url) as ws:
            _challenge = await ws.recv()  # receive challenge but don't respond
            await ws.recv()  # waits for more — daemon closes after timeout

    assert exc_info.value.rcvd.code == 4401  # type: ignore[union-attr]


async def test_two_simultaneous_clients_independent(
    running_daemon: tuple[str, Ed25519PrivateKey],
) -> None:
    """Two simultaneous clients do not interfere with each other."""
    ws_url, private_key = running_daemon

    async with (
        ws_connect(ws_url) as ws1,
        ws_connect(ws_url) as ws2,
    ):
        auth1, auth2 = await asyncio.gather(
            _authenticate_client(ws1, private_key),
            _authenticate_client(ws2, private_key),
        )
        assert auth1["ok"] is True
        assert auth2["ok"] is True

        id1, id2 = str(uuid.uuid4()), str(uuid.uuid4())

        req1 = json.dumps({"type": "req", "id": id1, "method": "ping", "params": {}})
        req2 = json.dumps({"type": "req", "id": id2, "method": "ping", "params": {}})
        await asyncio.gather(ws1.send(req1), ws2.send(req2))

        res1_raw, res2_raw = await asyncio.gather(ws1.recv(), ws2.recv())
        res1 = json.loads(res1_raw)
        res2 = json.loads(res2_raw)

        # Each client receives its own response — no cross-contamination
        assert res1["id"] == id1
        assert res2["id"] == id2


async def test_clean_disconnect_no_leak(
    running_daemon: tuple[str, Ed25519PrivateKey],
) -> None:
    """Client disconnects cleanly — no exception propagates to caller."""
    ws_url, private_key = running_daemon

    async with ws_connect(ws_url) as ws:
        auth_res = await _authenticate_client(ws, private_key)
        assert auth_res["ok"] is True
    # Context exit = clean disconnect, no exception raised


# ─── make_dispatch integration tests ─────────────────────────────────────────


async def _async_sdk_messages(items: list[Any]):  # type: ignore[return]
    """Async generator that yields SDK messages from a list."""
    for item in items:
        yield item


@pytest.fixture
async def running_daemon_with_runtime() -> AsyncGenerator[
    tuple[str, Ed25519PrivateKey], None
]:
    """Daemon fixture using make_dispatch with SDK mocked at the query level."""
    from unittest.mock import patch

    from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

    sdk_messages: list[Any] = [
        AssistantMessage(content=[TextBlock(text="Paris")], model="claude-3-5-sonnet"),
        ResultMessage(
            subtype="success",
            duration_ms=100,
            duration_api_ms=80,
            is_error=False,
            num_turns=1,
            session_id="ses-integration-test",
            stop_reason="end_turn",
            total_cost_usd=0.001,
        ),
    ]

    private_key = Ed25519PrivateKey.generate()
    session_manager = InMemorySessionManager()

    with patch("rai_agent.daemon.runtime.query") as mock_query:
        def _sdk_gen(**_kw: Any):  # type: ignore[return]
            return _async_sdk_messages(sdk_messages)

        mock_query.side_effect = _sdk_gen

        from rai_agent.daemon.runtime import ClaudeRuntime

        dispatch = make_dispatch(ClaudeRuntime())

        app = create_app(
            session_manager=session_manager,
            nonce_store=NonceStore(),
            public_key=private_key.public_key(),
            dispatch=dispatch,
            auth_timeout=5.0,
        )

        config = uvicorn.Config(
            app, host="127.0.0.1", port=0, log_level="warning", loop="asyncio"
        )
        server = uvicorn.Server(config)
        serve_task = asyncio.create_task(server.serve())

        while not server.started:
            await asyncio.sleep(0.01)

        port: int = server.servers[0].sockets[0].getsockname()[1]  # type: ignore[index]
        ws_url = f"ws://127.0.0.1:{port}/ws"

        yield ws_url, private_key

        server.should_exit = True
        await serve_task


async def test_real_dispatch_run_streams_event_frames(
    running_daemon_with_runtime: tuple[str, Ed25519PrivateKey],
) -> None:
    """make_dispatch: run method → EventFrames streamed to client."""
    ws_url, private_key = running_daemon_with_runtime

    async with ws_connect(ws_url) as ws:
        auth_res = await _authenticate_client(ws, private_key)
        assert auth_res["ok"] is True

        await ws.send(json.dumps({
            "type": "req",
            "id": str(uuid.uuid4()),
            "method": "run",
            "params": {"prompt": "capital of France?"},
        }))

        frames: list[dict[str, Any]] = []
        for _ in range(2):  # AssistantMessage + ResultMessage
            frames.append(json.loads(await ws.recv()))

        assert frames[0]["type"] == "event"
        assert frames[0]["event"] == "assistant_message"
        assert frames[1]["type"] == "event"
        assert frames[1]["event"] == "result"
        assert frames[1]["payload"]["session_id"] == "ses-integration-test"


async def test_real_dispatch_unknown_method_returns_error(
    running_daemon_with_runtime: tuple[str, Ed25519PrivateKey],
) -> None:
    """make_dispatch: unknown method → ResFrame(ok=False)."""
    ws_url, private_key = running_daemon_with_runtime

    async with ws_connect(ws_url) as ws:
        auth_res = await _authenticate_client(ws, private_key)
        assert auth_res["ok"] is True

        req_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "type": "req",
            "id": req_id,
            "method": "explode",
            "params": {},
        }))

        res = json.loads(await ws.recv())
        assert res["id"] == req_id
        assert res["ok"] is False
        assert "explode" in res["error"]
