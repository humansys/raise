"""Built-in MemoryMdSyncHook — DISABLED.

Previously regenerated MEMORY.md after graph build. Disabled because
MEMORY.md is owned by Claude Code's auto-memory system (see RAISE-1459).

CLAUDE.md (user-managed) is the correct place for always-on context.
MEMORY.md and memory/*.md are Claude-managed auto-memory files.

Architecture: E1132 Wave 4, CC source memoryFileDetection.ts:127-131.
"""

from __future__ import annotations

import logging
from typing import ClassVar

from raise_cli.hooks.events import HookEvent, HookResult

logger = logging.getLogger(__name__)


class MemoryMdSyncHook:
    """DISABLED — MEMORY.md is owned by Claude auto-memory.

    Kept as a stub to avoid import errors from any code that references
    this class. The entry point has been removed from pyproject.toml
    so this hook is never discovered or invoked by the hook system.

    See: RAISE-1459, E1132 Wave 4 (CC reverse engineering)
    """

    events: ClassVar[list[str]] = ["graph:build"]
    priority: ClassVar[int] = 0

    def handle(self, event: HookEvent) -> HookResult:
        """No-op. Returns ok without writing any files."""
        logger.debug("MemoryMdSyncHook disabled (RAISE-1459)")
        return HookResult(status="ok", message="disabled — MEMORY.md owned by Claude auto-memory")
