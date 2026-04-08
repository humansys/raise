"""Tests for MemoryMdSyncHook — disabled stub (RAISE-1459)."""

from __future__ import annotations

from pathlib import Path

from raise_cli.hooks.builtin.memory import MemoryMdSyncHook
from raise_cli.hooks.events import GraphBuildEvent, HookResult


class TestMemoryMdSyncHookDisabled:
    """MemoryMdSyncHook is disabled — returns ok without writing files."""

    def test_events_is_graph_build(self) -> None:
        assert MemoryMdSyncHook.events == ["graph:build"]

    def test_handle_returns_ok(self) -> None:
        hook = MemoryMdSyncHook()
        event = GraphBuildEvent(project_path=Path("/tmp/test"))
        result = hook.handle(event)

        assert isinstance(result, HookResult)
        assert result.status == "ok"
        assert "disabled" in result.message

    def test_handle_does_not_write_files(self, tmp_path: Path) -> None:
        hook = MemoryMdSyncHook()
        event = GraphBuildEvent(project_path=tmp_path)
        hook.handle(event)

        # No MEMORY.md should be created anywhere
        memory_md = tmp_path / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert not memory_md.exists()
