"""Tests for AcliJiraBridge — subprocess wrapper around ACLI."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from rai_pro.adapters.acli_bridge import AcliBridgeError, AcliJiraBridge


def _run(coro: Any) -> Any:
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# ── Success path ────────────────────────────────────────────────────────────


class TestCallSuccess:
    """call() returns parsed JSON on success."""

    def test_search_returns_parsed_json(self) -> None:
        expected = [{"key": "RAI-1", "fields": {"summary": "Test"}}]
        stdout = json.dumps(expected).encode()

        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (stdout, b"")
            proc.returncode = 0
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            result = _run(bridge.call(
                ["workitem", "search"],
                {"--jql": "project = RAI", "--limit": "1"},
            ))

        assert result == expected

    def test_call_passes_json_flag(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (b"[]", b"")
            proc.returncode = 0
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            _run(bridge.call(["workitem", "search"], {"--jql": "project = RAI"}))

            args = mock_asyncio.create_subprocess_exec.call_args
            cmd_args = args[0]
            assert "--json" in cmd_args


# ── Error paths ─────────────────────────────────────────────────────────────


class TestCallErrors:
    """call() raises AcliBridgeError on failures."""

    def test_nonzero_exit_raises(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (b"", b"Error: bad query")
            proc.returncode = 1
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            with pytest.raises(AcliBridgeError, match="bad query"):
                _run(bridge.call(["workitem", "search"], {"--jql": "bad"}))

    def test_invalid_json_raises(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (b"not json", b"")
            proc.returncode = 0
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            with pytest.raises(AcliBridgeError, match="JSON"):
                _run(bridge.call(["workitem", "search"], {}))

    def test_binary_not_found_raises(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            mock_asyncio.create_subprocess_exec = AsyncMock(
                side_effect=FileNotFoundError("No such file")
            )

            bridge = AcliJiraBridge(binary="nonexistent-acli")
            with pytest.raises(AcliBridgeError, match="not found"):
                _run(bridge.call(["workitem", "search"], {}))


# ── Health ──────────────────────────────────────────────────────────────────


class TestHealth:
    """health() returns AdapterHealth."""

    def test_healthy_when_authenticated(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (
                b"Authenticated\n  Site: test.atlassian.net",
                b"",
            )
            proc.returncode = 0
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            health = _run(bridge.health())

        assert health.healthy is True
        assert health.name == "jira-acli"
        assert health.latency_ms is not None

    def test_unhealthy_when_not_authenticated(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (b"", b"unauthorized")
            proc.returncode = 1
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            health = _run(bridge.health())

        assert health.healthy is False
