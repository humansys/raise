"""Rai daemon client — CLI and WebSocket client for daemon interaction.

Usage:
    python -m rai_agent.daemon.client run "what is 2+2?"
    python -m rai_agent.daemon.client status
    python -m rai_agent.daemon.client --host 0.0.0.0 --port 9000 stop

Design decisions (S2.10):
  D1: DaemonClient class encapsulates WS connection + auth + run
  D2: CLI uses argparse with subcommands (run/status/stop)
  D3: Status uses urllib.request (no async needed, simple GET)
  D4: Auth follows same Ed25519 challenge-response as server side
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from rai_agent.daemon.protocol import ReqFrame

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )


def _print_content(content: Any) -> None:
    """Extract and print text from assistant message content blocks."""
    if isinstance(content, list):
        for item in cast("list[Any]", content):
            if isinstance(item, dict):
                text = cast("dict[str, Any]", item).get("text")
                if isinstance(text, str):
                    print(text, end="", flush=True)
    elif isinstance(content, str):
        print(content, end="", flush=True)


class DaemonClient:
    """WebSocket client for the Rai daemon.

    Handles connection, Ed25519 challenge-response auth, and command dispatch.
    """

    def __init__(
        self,
        host: str,
        port: int,
        private_key: Ed25519PrivateKey,
    ) -> None:
        self._host = host
        self._port = port
        self._private_key = private_key
        self._ws: Any = None  # websockets client connection

    async def connect(self) -> None:
        """Open a WebSocket connection to the daemon."""
        from websockets.asyncio.client import connect as ws_connect

        url = f"ws://{self._host}:{self._port}/ws"
        self._ws = await ws_connect(url)

    async def authenticate(self) -> None:
        """Perform Ed25519 challenge-response authentication.

        Receives auth_challenge EventFrame, signs nonce, sends auth ReqFrame,
        verifies ResFrame(ok=True).

        Raises:
            ConnectionError: If authentication fails.
        """
        # Receive challenge
        raw = await self._ws.recv()
        frame = json.loads(raw)
        nonce: str = frame["payload"]["nonce"]

        # Sign nonce with private key
        signature = self._private_key.sign(nonce.encode())
        token = base64.b64encode(signature).decode()

        # Send auth request
        req = ReqFrame(
            type="req",
            id=str(uuid4()),
            method="auth",
            params={"token": token},
        )
        await self._ws.send(req.model_dump_json())

        # Verify response
        resp_raw = await self._ws.recv()
        resp: dict[str, Any] = json.loads(resp_raw)
        if not resp.get("ok"):
            error = resp.get("error", "unknown error")
            msg = f"Auth failed: {error}"
            raise ConnectionError(msg)

    async def run(self, prompt: str) -> None:
        """Send a run request and stream assistant messages to stdout.

        Sends ReqFrame(method="run"), receives EventFrames, prints
        assistant_message content. Stops on result event.
        """
        req = ReqFrame(
            type="req",
            id=str(uuid4()),
            method="run",
            params={"prompt": prompt},
        )
        await self._ws.send(req.model_dump_json())

        async for raw in self._ws:
            frame: dict[str, Any] = json.loads(raw)
            if frame["type"] == "event" and frame["event"] == "assistant_message":
                payload: dict[str, Any] = frame.get("payload", {})
                content: Any = payload.get("content", [])
                _print_content(content)
            elif frame["type"] == "event" and frame["event"] == "result":
                print()  # final newline
                break

    async def stop(self) -> None:
        """Send shutdown request to the daemon."""
        req = ReqFrame(
            type="req",
            id=str(uuid4()),
            method="shutdown",
            params={},
        )
        await self._ws.send(req.model_dump_json())

        # Wait for response
        resp_raw = await self._ws.recv()
        resp: dict[str, Any] = json.loads(resp_raw)
        if resp.get("ok"):
            print("Daemon shutting down")
        else:
            print(f"Shutdown failed: {resp.get('error', 'unknown')}", file=sys.stderr)

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None


# ─── CLI ─────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the daemon client.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(description="Rai daemon client")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Daemon host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Daemon port (default: 8000)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a prompt")
    run_parser.add_argument("prompt", help="The prompt to send to the daemon")

    subparsers.add_parser("status", help="Check daemon health")
    subparsers.add_parser("stop", help="Stop the daemon")

    return parser.parse_args(argv)


def status_command(args: argparse.Namespace) -> None:
    """Check daemon health via HTTP GET /health."""
    url = f"http://{args.host}:{args.port}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            print(json.dumps(data, indent=2))
    except urllib.error.URLError as exc:
        print(f"Cannot reach daemon at {url}: {exc}", file=sys.stderr)
        sys.exit(1)


async def run_command(args: argparse.Namespace) -> None:
    """Execute run command: connect, auth, run prompt, close."""
    from rai_agent.daemon.keys import load_or_generate_keys

    keys = load_or_generate_keys()
    client = DaemonClient(host=args.host, port=args.port, private_key=keys.private_key)
    try:
        await client.connect()
        await client.authenticate()
        await client.run(args.prompt)
    finally:
        await client.close()


async def stop_command(args: argparse.Namespace) -> None:
    """Execute stop command: connect, auth, send shutdown, close."""
    from rai_agent.daemon.keys import load_or_generate_keys

    keys = load_or_generate_keys()
    client = DaemonClient(host=args.host, port=args.port, private_key=keys.private_key)
    try:
        await client.connect()
        await client.authenticate()
        await client.stop()
    finally:
        await client.close()


def main() -> None:
    """Entry point for the Rai daemon client."""
    args = parse_args()
    if args.command == "run":
        asyncio.run(run_command(args))
    elif args.command == "status":
        status_command(args)
    elif args.command == "stop":
        asyncio.run(stop_command(args))


if __name__ == "__main__":
    main()
