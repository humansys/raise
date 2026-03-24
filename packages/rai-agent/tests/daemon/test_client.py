"""Tests for DaemonClient and CLI argument parsing.

Tests cover:
  - CLI arg parsing (run/status/stop subcommands, host/port overrides)
  - Auth handshake (mock WS)
  - Run streaming (mock WS with EventFrames)
  - Auth failure raises ConnectionError
"""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from uuid import uuid4

if TYPE_CHECKING:
    from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from rai_agent.daemon.protocol import EventFrame, ResFrame

# ─── Mock WS helper ──────────────────────────────────────────────────────────


class MockWebSocket:
    """Mock WebSocket that supports recv() and async iteration.

    recv_frames: frames returned by recv() calls (in order).
    iter_frames: frames yielded by async iteration (async for).
    """

    def __init__(
        self,
        recv_frames: list[str] | None = None,
        iter_frames: list[str] | None = None,
    ) -> None:
        self._recv_frames = recv_frames or []
        self._iter_frames = iter_frames or []
        self._recv_index = 0
        self.sent: list[str] = []

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def recv(self) -> str:
        idx = self._recv_index
        self._recv_index += 1
        return self._recv_frames[idx]

    async def close(self) -> None:
        pass

    def __aiter__(self) -> MockWebSocket:
        self._iter_index = 0
        return self

    async def __anext__(self) -> str:
        if self._iter_index >= len(self._iter_frames):
            raise StopAsyncIteration
        frame = self._iter_frames[self._iter_index]
        self._iter_index += 1
        return frame


# ─── CLI parse_args tests ────────────────────────────────────────────────────


class TestParseArgs:
    """Tests for parse_args()."""

    def test_run_subcommand(self) -> None:
        from rai_agent.daemon.client import parse_args

        args = parse_args(["run", "hello world"])
        assert args.command == "run"
        assert args.prompt == "hello world"

    def test_status_subcommand(self) -> None:
        from rai_agent.daemon.client import parse_args

        args = parse_args(["status"])
        assert args.command == "status"

    def test_stop_subcommand(self) -> None:
        from rai_agent.daemon.client import parse_args

        args = parse_args(["stop"])
        assert args.command == "stop"

    def test_default_host_and_port(self) -> None:
        from rai_agent.daemon.client import parse_args

        args = parse_args(["status"])
        assert args.host == "127.0.0.1"
        assert args.port == 8000

    def test_custom_host_and_port(self) -> None:
        from rai_agent.daemon.client import parse_args

        args = parse_args(["--host", "0.0.0.0", "--port", "9000", "run", "test"])
        assert args.host == "0.0.0.0"
        assert args.port == 9000
        assert args.command == "run"
        assert args.prompt == "test"

    def test_missing_subcommand_raises(self) -> None:
        from rai_agent.daemon.client import parse_args

        with pytest.raises(SystemExit):
            parse_args([])


# ─── DaemonClient tests ─────────────────────────────────────────────────────


def _make_auth_challenge() -> str:
    """Create a serialized auth_challenge EventFrame."""
    nonce = str(uuid4())
    frame = EventFrame(
        type="event",
        event="auth_challenge",
        payload={"nonce": nonce},
        seq=0,
    )
    return frame.model_dump_json()


def _make_auth_success(req_id: str) -> str:
    """Create a serialized auth success ResFrame."""
    return ResFrame(type="res", id=req_id, ok=True).model_dump_json()


def _make_auth_failure(req_id: str) -> str:
    """Create a serialized auth failure ResFrame."""
    return ResFrame(
        type="res", id=req_id, ok=False, error="invalid token"
    ).model_dump_json()


class TestDaemonClientAuth:
    """Tests for DaemonClient.authenticate()."""

    async def test_auth_handshake_success(self) -> None:
        """Client signs challenge nonce and receives ok=True."""
        from rai_agent.daemon.client import DaemonClient

        private_key = Ed25519PrivateKey.generate()
        client = DaemonClient(host="127.0.0.1", port=8000, private_key=private_key)

        # Build mock WS that simulates auth challenge/response
        mock_ws = AsyncMock()
        challenge_json = _make_auth_challenge()
        challenge_data = json.loads(challenge_json)
        nonce = challenge_data["payload"]["nonce"]

        # recv() returns challenge first, then auth success
        # We need to capture the auth request to extract the id
        sent_frames: list[str] = []

        async def mock_send(data: str) -> None:
            sent_frames.append(data)

        mock_ws.send = mock_send

        call_count = 0

        async def mock_recv() -> str:
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return challenge_json
            # Parse the sent auth request to get the id
            auth_req = json.loads(sent_frames[0])
            return _make_auth_success(auth_req["id"])

        mock_ws.recv = mock_recv

        client._ws = mock_ws  # type: ignore[assignment]
        await client.authenticate()

        # Verify we sent an auth request
        assert len(sent_frames) == 1
        auth_req = json.loads(sent_frames[0])
        assert auth_req["method"] == "auth"
        assert "token" in auth_req["params"]

        # Verify the signature is valid
        sig = base64.b64decode(auth_req["params"]["token"])
        # Should not raise
        private_key.public_key().verify(sig, nonce.encode())

    async def test_auth_failure_raises(self) -> None:
        """Client raises ConnectionError when auth response has ok=False."""
        from rai_agent.daemon.client import DaemonClient

        private_key = Ed25519PrivateKey.generate()
        client = DaemonClient(host="127.0.0.1", port=8000, private_key=private_key)

        mock_ws = AsyncMock()
        challenge_json = _make_auth_challenge()

        sent_frames: list[str] = []

        async def mock_send(data: str) -> None:
            sent_frames.append(data)

        mock_ws.send = mock_send

        call_count = 0

        async def mock_recv() -> str:
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return challenge_json
            auth_req = json.loads(sent_frames[0])
            return _make_auth_failure(auth_req["id"])

        mock_ws.recv = mock_recv

        client._ws = mock_ws  # type: ignore[assignment]

        with pytest.raises(ConnectionError, match="Auth failed"):
            await client.authenticate()


class TestDaemonClientRun:
    """Tests for DaemonClient.run() streaming."""

    async def test_run_streams_assistant_messages(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """run() prints assistant_message content to stdout."""
        from rai_agent.daemon.client import DaemonClient

        private_key = Ed25519PrivateKey.generate()
        client = DaemonClient(host="127.0.0.1", port=8000, private_key=private_key)

        # Build event frames the daemon would send
        msg_frame = EventFrame(
            type="event",
            event="assistant_message",
            payload={"content": [{"text": "Hello, world!"}]},
            seq=1,
        )
        result_frame = EventFrame(
            type="event",
            event="result",
            payload={"session_id": "ses-123"},
            seq=2,
        )

        frames = [msg_frame.model_dump_json(), result_frame.model_dump_json()]
        mock_ws = MockWebSocket(iter_frames=frames)

        client._ws = mock_ws  # type: ignore[assignment]
        await client.run("test prompt")

        # Verify the run request was sent
        assert len(mock_ws.sent) == 1
        req = json.loads(mock_ws.sent[0])
        assert req["method"] == "run"
        assert req["params"]["prompt"] == "test prompt"

        # Verify output was printed
        captured = capsys.readouterr()
        assert "Hello, world!" in captured.out

    async def test_run_handles_multiple_messages(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """run() handles multiple assistant_message events before result."""
        from rai_agent.daemon.client import DaemonClient

        private_key = Ed25519PrivateKey.generate()
        client = DaemonClient(host="127.0.0.1", port=8000, private_key=private_key)

        msg1 = EventFrame(
            type="event",
            event="assistant_message",
            payload={"content": [{"text": "Part 1"}]},
            seq=1,
        )
        msg2 = EventFrame(
            type="event",
            event="assistant_message",
            payload={"content": [{"text": "Part 2"}]},
            seq=2,
        )
        result = EventFrame(
            type="event",
            event="result",
            payload={"session_id": "ses-456"},
            seq=3,
        )

        all_frames = [
            msg1.model_dump_json(),
            msg2.model_dump_json(),
            result.model_dump_json(),
        ]

        mock_ws = MockWebSocket(iter_frames=all_frames)

        client._ws = mock_ws  # type: ignore[assignment]
        await client.run("multi part")

        captured = capsys.readouterr()
        assert "Part 1" in captured.out
        assert "Part 2" in captured.out


# ─── Status tests ────────────────────────────────────────────────────────────


class TestStatus:
    """Tests for status_command() HTTP health check."""

    def test_status_prints_health_json(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """status_command() prints JSON from /health endpoint."""
        import argparse
        from unittest.mock import MagicMock, patch

        from rai_agent.daemon.client import status_command

        health_data = b'{"status": "ok", "ws": "listening"}'

        # MagicMock supports __enter__/__exit__ natively
        mock_resp = MagicMock()
        mock_resp.read.return_value = health_data
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        args = argparse.Namespace(host="127.0.0.1", port=8000)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            status_command(args)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["status"] == "ok"


# ─── Stop tests ──────────────────────────────────────────────────────────────


class TestDaemonClientStop:
    """Tests for DaemonClient.stop()."""

    async def test_stop_sends_shutdown_method(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """stop() sends ReqFrame with method=shutdown and prints confirmation."""
        from rai_agent.daemon.client import DaemonClient

        private_key = Ed25519PrivateKey.generate()
        client = DaemonClient(host="127.0.0.1", port=8000, private_key=private_key)

        # Mock WS: first recv is the shutdown success response
        shutdown_resp = ResFrame(type="res", id="any", ok=True).model_dump_json()
        mock_ws = MockWebSocket(recv_frames=[shutdown_resp])

        client._ws = mock_ws  # type: ignore[assignment]
        await client.stop()

        # Verify shutdown request was sent
        assert len(mock_ws.sent) == 1
        req = json.loads(mock_ws.sent[0])
        assert req["method"] == "shutdown"

        captured = capsys.readouterr()
        assert "shutting down" in captured.out.lower()


# ─── Shutdown dispatch tests ─────────────────────────────────────────────────


class TestShutdownDispatch:
    """Tests for shutdown method handling in make_dispatch."""

    async def test_shutdown_method_calls_callback(self) -> None:
        """Dispatch handles method=shutdown by calling the shutdown callback."""
        from rai_agent.daemon.connection import make_dispatch
        from rai_agent.daemon.protocol import ReqFrame

        shutdown_called = False

        def on_shutdown() -> None:
            nonlocal shutdown_called
            shutdown_called = True

        # Create a stub runtime
        runtime = AsyncMock()
        dispatch = make_dispatch(runtime, shutdown_callback=on_shutdown)

        req = ReqFrame(type="req", id="test-id", method="shutdown", params={})
        sent: list[str] = []

        async def mock_send(data: str) -> None:
            sent.append(data)

        await dispatch(req, mock_send)

        assert shutdown_called
        assert len(sent) == 1
        resp = json.loads(sent[0])
        assert resp["ok"] is True

    async def test_shutdown_without_callback_returns_error(self) -> None:
        """Dispatch returns error when shutdown is called without callback."""
        from rai_agent.daemon.connection import make_dispatch
        from rai_agent.daemon.protocol import ReqFrame

        runtime = AsyncMock()
        dispatch = make_dispatch(runtime)

        req = ReqFrame(type="req", id="test-id", method="shutdown", params={})
        sent: list[str] = []

        async def mock_send(data: str) -> None:
            sent.append(data)

        await dispatch(req, mock_send)

        # Without callback, shutdown is an unknown method
        assert len(sent) == 1
        resp = json.loads(sent[0])
        assert resp["ok"] is False


# ─── Integration tests ──────────────────────────────────────────────────────


class TestClientIntegration:
    """Integration tests using real daemon components.

    Uses real FastAPI app with stub dispatcher, real WS connections,
    and real DaemonClient.
    """

    async def test_client_auth_and_run_e2e(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Full flow: connect → auth → run → receive events → close."""
        import asyncio

        import uvicorn
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        from rai_agent.daemon.app import create_app
        from rai_agent.daemon.auth import NonceStore
        from rai_agent.daemon.client import DaemonClient
        from rai_agent.daemon.protocol import EventFrame, ReqFrame
        from rai_agent.daemon.session import InMemorySessionManager

        private_key = Ed25519PrivateKey.generate()

        # Stub dispatcher that sends assistant_message + result events
        async def stub_dispatch(
            req: ReqFrame,
            send: Any,
        ) -> None:
            if req.method == "run":
                msg = EventFrame(
                    type="event",
                    event="assistant_message",
                    payload={"content": [{"text": "42"}]},
                    seq=1,
                )
                await send(msg.model_dump_json())
                result_ev = EventFrame(
                    type="event",
                    event="result",
                    payload={"session_id": "ses-e2e"},
                    seq=2,
                )
                await send(result_ev.model_dump_json())

        app = create_app(
            session_manager=InMemorySessionManager(),
            nonce_store=NonceStore(),
            public_key=private_key.public_key(),
            dispatch=stub_dispatch,
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

        client = DaemonClient(host="127.0.0.1", port=port, private_key=private_key)

        try:
            await client.connect()
            await client.authenticate()
            await client.run("what is the answer?")

            captured = capsys.readouterr()
            assert "42" in captured.out
        finally:
            await client.close()
            server.should_exit = True
            await serve_task

    async def test_client_status_e2e(self) -> None:
        """Status command hits /health endpoint on real server."""
        import asyncio

        import uvicorn
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        from rai_agent.daemon.app import create_app
        from rai_agent.daemon.auth import NonceStore
        from rai_agent.daemon.session import InMemorySessionManager

        private_key = Ed25519PrivateKey.generate()

        async def stub_dispatch(req: Any, send: Any) -> None:
            pass

        app = create_app(
            session_manager=InMemorySessionManager(),
            nonce_store=NonceStore(),
            public_key=private_key.public_key(),
            dispatch=stub_dispatch,
            auth_timeout=5.0,
        )

        @app.get("/health")
        async def health() -> dict[str, str]:  # pyright: ignore[reportUnusedFunction]
            return {"status": "ok"}

        config = uvicorn.Config(
            app, host="127.0.0.1", port=0, log_level="warning", loop="asyncio"
        )
        server = uvicorn.Server(config)
        serve_task = asyncio.create_task(server.serve())

        while not server.started:
            await asyncio.sleep(0.01)

        port: int = server.servers[0].sockets[0].getsockname()[1]  # type: ignore[index]

        # Run sync urllib in a thread to avoid blocking the event loop
        import urllib.request

        url = f"http://127.0.0.1:{port}/health"
        try:

            def _fetch() -> dict[str, str]:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    return json.loads(resp.read().decode())  # type: ignore[no-any-return]

            data = await asyncio.to_thread(_fetch)
            assert data["status"] == "ok"
        finally:
            server.should_exit = True
            await serve_task

    async def test_client_shutdown_e2e(self) -> None:
        """Stop command sends shutdown to real daemon and gets ok response."""
        import asyncio

        import uvicorn
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        from rai_agent.daemon.app import create_app
        from rai_agent.daemon.auth import NonceStore
        from rai_agent.daemon.client import DaemonClient
        from rai_agent.daemon.connection import make_dispatch
        from rai_agent.daemon.session import InMemorySessionManager

        private_key = Ed25519PrivateKey.generate()
        shutdown_called = False

        def on_shutdown() -> None:
            nonlocal shutdown_called
            shutdown_called = True

        # Use a stub runtime
        runtime = AsyncMock()
        dispatch = make_dispatch(runtime, shutdown_callback=on_shutdown)

        app = create_app(
            session_manager=InMemorySessionManager(),
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

        client = DaemonClient(host="127.0.0.1", port=port, private_key=private_key)

        try:
            await client.connect()
            await client.authenticate()
            await client.stop()
            assert shutdown_called
        finally:
            await client.close()
            server.should_exit = True
            await serve_task
