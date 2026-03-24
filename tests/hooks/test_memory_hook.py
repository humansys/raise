"""Tests for MemoryMdSyncHook — regenerates MEMORY.md after graph build."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.hooks.builtin.memory import MemoryMdSyncHook
from raise_cli.hooks.events import GraphBuildEvent, HookResult


class TestMemoryMdSyncHookAttributes:
    """MemoryMdSyncHook class-level attributes."""

    def test_events_is_graph_build(self) -> None:
        assert MemoryMdSyncHook.events == ["graph:build"]

    def test_priority_is_zero(self) -> None:
        assert MemoryMdSyncHook.priority == 0


class TestMemoryMdSyncHookHandle:
    """MemoryMdSyncHook.handle() behavior."""

    @pytest.fixture
    def hook(self) -> MemoryMdSyncHook:
        return MemoryMdSyncHook()

    @pytest.fixture
    def project_dir(self, tmp_path: Path) -> Path:
        """Create a minimal project directory with manifest and framework files."""
        # .raise/manifest.yaml
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        (raise_dir / "manifest.yaml").write_text(
            "project:\n"
            "  name: test-project\n"
            "  project_type: brownfield\n"
            "branches:\n"
            "  development: dev\n"
            "  main: main\n",
            encoding="utf-8",
        )

        # .raise/rai/framework/methodology.yaml (minimal)
        framework_dir = raise_dir / "rai" / "framework"
        framework_dir.mkdir(parents=True)
        (framework_dir / "methodology.yaml").write_text(
            "principles:\n  core:\n    - name: TDD\n      rule: always\n",
            encoding="utf-8",
        )

        # .raise/rai/memory/ (empty patterns)
        memory_dir = raise_dir / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        return tmp_path

    def test_generates_canonical_memory_md(
        self, hook: MemoryMdSyncHook, project_dir: Path
    ) -> None:
        event = GraphBuildEvent(project_path=project_dir, node_count=5, edge_count=3)
        result = hook.handle(event)

        assert result.status == "ok"

        canonical = project_dir / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.exists()
        content = canonical.read_text(encoding="utf-8")
        assert "test-project" in content

    def test_writes_claude_code_copy(
        self, hook: MemoryMdSyncHook, project_dir: Path
    ) -> None:
        event = GraphBuildEvent(project_path=project_dir, node_count=5, edge_count=3)

        with patch(
            "raise_cli.hooks.builtin.memory.get_claude_memory_path"
        ) as mock_path:
            claude_memory = project_dir / ".claude" / "memory" / "MEMORY.md"
            mock_path.return_value = claude_memory

            result = hook.handle(event)

        assert result.status == "ok"
        assert claude_memory.exists()

        canonical = project_dir / ".raise" / "rai" / "memory" / "MEMORY.md"
        assert canonical.read_text(encoding="utf-8") == claude_memory.read_text(
            encoding="utf-8"
        )

    def test_returns_error_on_generation_failure(self, hook: MemoryMdSyncHook) -> None:
        event = GraphBuildEvent(project_path=Path("/nonexistent/path"))

        with patch(
            "raise_cli.hooks.builtin.memory.generate_memory_md",
            side_effect=Exception("boom"),
        ):
            result = hook.handle(event)

        assert result.status == "error"
        assert "boom" in result.message

    def test_never_raises(self, hook: MemoryMdSyncHook) -> None:
        """Even if everything goes wrong, handle() returns HookResult, not exception."""
        event = GraphBuildEvent(project_path=Path("/nonexistent/path"))

        with patch(
            "raise_cli.hooks.builtin.memory.generate_memory_md",
            side_effect=RuntimeError("catastrophic"),
        ):
            result = hook.handle(event)

        assert isinstance(result, HookResult)
        assert result.status == "error"
