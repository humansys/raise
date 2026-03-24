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
            result = _run(
                bridge.call(
                    ["workitem", "search"],
                    {"--jql": "project = RAI", "--limit": "1"},
                )
            )

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

    def test_unhealthy_when_switch_fails(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            switch_proc = AsyncMock()
            switch_proc.communicate.return_value = (b"", b"switch failed")
            switch_proc.returncode = 1
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=switch_proc)

            bridge = AcliJiraBridge(binary="acli")
            health = _run(bridge.health(site="bad.atlassian.net"))

        assert health.healthy is False
        assert "switch failed" in health.message

    def test_unhealthy_when_not_authenticated(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            proc = AsyncMock()
            proc.communicate.return_value = (b"", b"unauthorized")
            proc.returncode = 1
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=proc)

            bridge = AcliJiraBridge(binary="acli")
            health = _run(bridge.health())

        assert health.healthy is False


# ── Auth switching ─────────────────────────────────────────────────────────


def _make_success_proc() -> AsyncMock:
    """Create a mock subprocess that succeeds with empty JSON."""
    proc = AsyncMock()
    proc.communicate.return_value = (b"[]", b"")
    proc.returncode = 0
    return proc


class TestAuthSwitching:
    """call() runs acli jira auth switch when site differs from cached."""

    def test_switches_site_on_first_call(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            switch_proc = _make_success_proc()
            cmd_proc = _make_success_proc()
            mock_asyncio.create_subprocess_exec = AsyncMock(
                side_effect=[switch_proc, cmd_proc]
            )

            bridge = AcliJiraBridge(binary="acli")
            _run(
                bridge.call(
                    ["workitem", "search"],
                    {"--jql": "x"},
                    site="humansys.atlassian.net",
                )
            )

            calls = mock_asyncio.create_subprocess_exec.call_args_list
            assert len(calls) == 2
            # First call: auth switch
            switch_args = calls[0][0]
            assert "auth" in switch_args
            assert "switch" in switch_args
            assert "humansys.atlassian.net" in switch_args
            # Second call: actual command
            cmd_args = calls[1][0]
            assert "workitem" in cmd_args

    def test_skips_switch_when_same_site(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            switch_proc = _make_success_proc()
            cmd_proc1 = _make_success_proc()
            cmd_proc2 = _make_success_proc()
            mock_asyncio.create_subprocess_exec = AsyncMock(
                side_effect=[switch_proc, cmd_proc1, cmd_proc2]
            )

            bridge = AcliJiraBridge(binary="acli")
            _run(
                bridge.call(
                    ["workitem", "search"],
                    {"--jql": "x"},
                    site="humansys.atlassian.net",
                )
            )
            _run(
                bridge.call(
                    ["workitem", "view", "RAISE-1"],
                    {},
                    site="humansys.atlassian.net",
                )
            )

            # 3 calls total: switch + cmd1 + cmd2 (no second switch)
            assert mock_asyncio.create_subprocess_exec.call_count == 3

    def test_switches_when_site_changes(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            procs = [_make_success_proc() for _ in range(4)]
            mock_asyncio.create_subprocess_exec = AsyncMock(side_effect=procs)

            bridge = AcliJiraBridge(binary="acli")
            _run(
                bridge.call(
                    ["workitem", "search"],
                    {"--jql": "x"},
                    site="humansys.atlassian.net",
                )
            )
            _run(
                bridge.call(
                    ["workitem", "search"],
                    {"--jql": "y"},
                    site="rai-agent.atlassian.net",
                )
            )

            # 4 calls: switch1 + cmd1 + switch2 + cmd2
            assert mock_asyncio.create_subprocess_exec.call_count == 4
            calls = mock_asyncio.create_subprocess_exec.call_args_list
            switch2_args = calls[2][0]
            assert "rai-agent.atlassian.net" in switch2_args

    def test_no_switch_without_site(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            cmd_proc = _make_success_proc()
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=cmd_proc)

            bridge = AcliJiraBridge(binary="acli")
            _run(bridge.call(["workitem", "search"], {"--jql": "x"}))

            # Only 1 call: the command itself (no switch)
            assert mock_asyncio.create_subprocess_exec.call_count == 1

    def test_switch_binary_not_found_raises_bridge_error(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            mock_asyncio.create_subprocess_exec = AsyncMock(
                side_effect=FileNotFoundError("No such file")
            )

            bridge = AcliJiraBridge(binary="nonexistent-acli")
            with pytest.raises(AcliBridgeError, match="not found"):
                _run(
                    bridge.call(
                        ["workitem", "search"],
                        {"--jql": "x"},
                        site="any.atlassian.net",
                    )
                )

    def test_switch_failure_raises(self) -> None:
        with patch("rai_pro.adapters.acli_bridge.asyncio") as mock_asyncio:
            switch_proc = AsyncMock()
            switch_proc.communicate.return_value = (b"", b"switch failed")
            switch_proc.returncode = 1
            mock_asyncio.create_subprocess_exec = AsyncMock(return_value=switch_proc)

            bridge = AcliJiraBridge(binary="acli")
            with pytest.raises(AcliBridgeError, match="switch failed"):
                _run(
                    bridge.call(
                        ["workitem", "search"],
                        {"--jql": "x"},
                        site="bad.atlassian.net",
                    )
                )
