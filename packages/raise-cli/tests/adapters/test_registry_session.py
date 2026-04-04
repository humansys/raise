"""Tests for session protocol discovery via entry points."""

from __future__ import annotations

from raise_cli.adapters.registry import (
    get_session_registries,
    get_state_derivers,
    get_workstream_monitors,
)
from raise_cli.session.derive import GitStateDeriver
from raise_cli.session.registry import LocalSessionRegistry


class TestSessionRegistryDiscovery:
    """Verify session protocol entry points are discoverable."""

    def test_git_state_deriver_discovered(self) -> None:
        derivers = get_state_derivers()
        assert "git" in derivers
        assert derivers["git"] is GitStateDeriver

    def test_local_session_registry_discovered(self) -> None:
        registries = get_session_registries()
        assert "local" in registries
        assert registries["local"] is LocalSessionRegistry

    def test_workstream_monitors_empty_for_now(self) -> None:
        monitors = get_workstream_monitors()
        # No implementations registered yet (S1248.4)
        assert isinstance(monitors, dict)
