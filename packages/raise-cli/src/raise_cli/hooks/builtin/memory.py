"""Built-in MemoryMdSyncHook — regenerates MEMORY.md after graph build.

Subscribes to ``graph:build`` and writes MEMORY.md to both the canonical
location (``.raise/rai/memory/MEMORY.md``) and the Claude Code copy
(``~/.claude/projects/{encoded}/memory/MEMORY.md``).

Error isolation: ``handle()`` never raises. Failures are logged and
returned as ``HookResult(status="error")``.

Architecture: S350.3 (MEMORY.md sync hook)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.config.paths import (
    get_claude_memory_path,
    get_framework_dir,
    get_memory_dir,
)
from raise_cli.hooks.events import GraphBuildEvent, HookEvent, HookResult
from raise_cli.onboarding.memory_md import generate_memory_md

logger = logging.getLogger(__name__)


class MemoryMdSyncHook:
    """Regenerate MEMORY.md after graph build.

    Writes to:
    1. Canonical: ``.raise/rai/memory/MEMORY.md``
    2. Claude Code: ``~/.claude/projects/{hash}/memory/MEMORY.md``

    Reads project name and development branch from manifest.yaml.
    Falls back to sensible defaults if manifest is unavailable.

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = ["graph:build"]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        """Generate MEMORY.md and write to canonical + Claude Code paths.

        Never raises — returns ``HookResult(status="error")`` on failure.
        """
        try:
            return self._do_handle(event)
        except Exception as exc:  # noqa: BLE001
            msg = f"{type(exc).__name__}: {exc}"
            logger.warning("MemoryMdSyncHook failed: %s", msg)
            return HookResult(status="error", message=msg)

    def _do_handle(self, event: HookEvent) -> HookResult:
        """Internal handler — may raise, caller catches."""
        assert isinstance(event, (HookEvent, GraphBuildEvent))  # noqa: S101 -- type narrowing for hook dispatch

        project_path = getattr(event, "project_path", None)
        if project_path is None:
            return HookResult(status="error", message="No project_path in event")

        project_path = project_path.resolve()

        # Load manifest for project name and development branch
        project_name, dev_branch = self._load_project_info(project_path)

        # Generate content
        methodology_path = get_framework_dir(project_path) / "methodology.yaml"
        patterns_path = get_memory_dir(project_path) / "patterns.jsonl"

        content = generate_memory_md(
            methodology_path=methodology_path,
            patterns_path=patterns_path,
            project_name=project_name,
            development_branch=dev_branch,
        )

        # Write canonical copy
        canonical = get_memory_dir(project_path) / "MEMORY.md"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_text(content, encoding="utf-8")
        logger.debug("MemoryMdSyncHook wrote canonical MEMORY.md: %s", canonical)

        # Write Claude Code copy
        claude_memory = get_claude_memory_path(project_path)
        claude_memory.parent.mkdir(parents=True, exist_ok=True)
        claude_memory.write_text(content, encoding="utf-8")
        logger.debug("MemoryMdSyncHook wrote Claude Code MEMORY.md: %s", claude_memory)

        return HookResult(status="ok")

    @staticmethod
    def _load_project_info(project_path: Path) -> tuple[str, str]:
        """Load project name and development branch from manifest.

        Returns:
            Tuple of (project_name, development_branch) with defaults.
        """
        project_name = "project"
        dev_branch = "main"

        try:
            from raise_cli.onboarding.manifest import load_manifest

            manifest = load_manifest(Path(str(project_path)))
            if manifest is not None:
                project_name = manifest.project.name
                dev_branch = manifest.branches.development
        except Exception:  # noqa: BLE001
            logger.debug("Could not load manifest, using defaults")

        return project_name, dev_branch
