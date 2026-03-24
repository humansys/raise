# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for daemon __main__ — build_daemon, health endpoint, CLI."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _clean_event_bus() -> Any:  # noqa: PT005
    """Reset the EventBus singleton before each test for isolation."""
    from rai_agent.daemon import events

    original = events._bus
    events._bus = None
    yield
    events._bus = original


class TestBuildDaemon:
    """build_daemon creates all components from DaemonConfig."""

    def test_creates_all_components(self) -> None:
        from rai_agent.daemon.__main__ import (
            DaemonComponents,
            build_daemon,
        )
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
            allowed_user_ids=[42],
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        assert isinstance(components, DaemonComponents)
        assert components.app is not None
        assert components.cron_trigger is not None
        assert components.telegram_trigger is not None
        assert components.dispatcher is not None
        assert components.registry is not None
        assert components.handler is not None

    def test_without_briefing_skips_briefing(self) -> None:
        from rai_agent.daemon.__main__ import build_daemon
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
            briefing_chat_id=None,
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        assert components.briefing_pipeline is None

    def test_with_briefing_creates_briefing(self) -> None:
        from rai_agent.daemon.__main__ import build_daemon
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
            briefing_chat_id=12345,
            briefing_cron="0 9 * * *",
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        assert components.briefing_pipeline is not None


class TestParseArgs:
    """parse_args handles --config, --host, --port."""

    def test_default_args(self) -> None:
        from rai_agent.daemon.__main__ import parse_args

        args = parse_args([])
        assert args.config is None
        assert args.host == "127.0.0.1"
        assert args.port == 8000

    def test_config_flag(self) -> None:
        from rai_agent.daemon.__main__ import parse_args

        args = parse_args(
            ["--config", "/path/to/config.yaml"],
        )
        assert args.config == "/path/to/config.yaml"

    def test_host_flag(self) -> None:
        from rai_agent.daemon.__main__ import parse_args

        args = parse_args(["--host", "0.0.0.0"])
        assert args.host == "0.0.0.0"

    def test_port_flag(self) -> None:
        from rai_agent.daemon.__main__ import parse_args

        args = parse_args(["--port", "9000"])
        assert args.port == 9000


class TestHealthEndpoint:
    """GET /health returns status ok."""

    def test_health_returns_ok(self) -> None:
        from rai_agent.daemon.__main__ import build_daemon
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        from starlette.testclient import TestClient

        client = TestClient(components.app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "triggers" in data
        assert "ws" in data


class TestIntegration:
    """Integration tests — importability and endpoints."""

    def test_module_is_importable(self) -> None:
        from rai_agent.daemon.__main__ import build_daemon, main

        assert callable(build_daemon)
        assert callable(main)

    def test_health_via_testclient(self) -> None:
        from rai_agent.daemon.__main__ import build_daemon
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
            allowed_user_ids=[1],
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        from starlette.testclient import TestClient

        client = TestClient(components.app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_ws_endpoint_exists(self) -> None:
        """Verify the /ws WebSocket route is registered."""
        from rai_agent.daemon.__main__ import build_daemon
        from rai_agent.daemon.config import DaemonConfig

        config = DaemonConfig(
            _skip_env=True,
            telegram_bot_token="test-token",
            anthropic_api_key="test-key",
        )

        with patch(
            "rai_agent.daemon.__main__.load_or_generate_keys",
        ) as mock_keys:
            from rai_agent.daemon.keys import generate_keys

            mock_keys.return_value = generate_keys()
            components = build_daemon(config)

        route_paths: list[Any] = [
            r.path
            for r in components.app.routes  # type: ignore[union-attr]
        ]
        assert "/ws" in route_paths
        assert "/health" in route_paths
