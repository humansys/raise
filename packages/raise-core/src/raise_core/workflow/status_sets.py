"""Shared run-status frozensets — single source of truth for active pipeline run detection.

RAISE-15049: Added PAUSED_RUN_STATUSES and expanded TERMINAL_RUN_STATUSES to cover
all spelling variants used across MCP tools and engine. Design aliases (ACTIVE_STATUSES,
PAUSED_STATUSES, TERMINAL_STATUSES) exported for cockpit pipeline_view.py.
"""

from __future__ import annotations

ACTIVE_RUN_STATUSES: frozenset[str] = frozenset({"started", "running", "pending"})
"""Statuses that indicate a pipeline run is active (not yet terminal).

RAISE-15795: write sites were normalized to emit "running" only ("started" is
no longer written by current code). "started" is retained here as a
tolerant-read backward-compat value for runs written by pre-normalization
code during the cross-worktree transition period; do not remove it without
a follow-up cleanup story.

- "started": legacy MCP-initiated runs (backward compat only, no longer written)
- "running": canonical active status (RunStatus.RUNNING = "running")
- "pending": Queued but not yet dispatched
"""

PAUSED_RUN_STATUSES: frozenset[str] = frozenset({"paused", "paused_hitl"})
"""Statuses that indicate a pipeline run is paused awaiting human input.

- "paused": Explicit pause via pipeline_pause tool
- "paused_hitl": Paused at an HITL gate pending approval
"""

TERMINAL_RUN_STATUSES: frozenset[str] = frozenset(
    {"complete", "completed", "cancelled", "canceled", "failed"}
)
"""Statuses that indicate a pipeline run has ended.

Includes both spelling variants ("cancelled"/"canceled", "complete"/"completed")
that appear across MCP tools, engine, and external adapters.
"""

# Design-name aliases (§1.3 of cockpit-synthesized-design.md)
# Preferred names for new code — use these in cockpit/pipeline_view.py.
ACTIVE_STATUSES: frozenset[str] = ACTIVE_RUN_STATUSES
PAUSED_STATUSES: frozenset[str] = PAUSED_RUN_STATUSES
TERMINAL_STATUSES: frozenset[str] = TERMINAL_RUN_STATUSES
