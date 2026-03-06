"""Built-in JiraSyncHook — auto-sync work lifecycle events to Jira transitions.

Subscribes to ``work:start`` and ``work:close`` events. Maps lifecycle events
to Jira transition IDs via ``lifecycle_mapping`` in ``.raise/jira.yaml``.

Graceful degradation:
- No issue_key on event → skip (debug log)
- No lifecycle_mapping configured → skip (debug log)
- No mapping entry for event type → skip (debug log)
- Adapter unavailable → return error (no crash)

Architecture: E301 S301.6 (Skill Auto-Sync Hooks)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.hooks.events import HookEvent, HookResult, WorkCloseEvent, WorkStartEvent

logger = logging.getLogger(__name__)

_JIRA_YAML_PATH: Path = Path(".raise/jira.yaml")


def _load_lifecycle_mapping() -> dict[str, int] | None:
    """Read lifecycle_mapping from .raise/jira.yaml.

    Returns None if file missing or section absent.
    """
    if not _JIRA_YAML_PATH.exists():
        return None
    data = yaml.safe_load(_JIRA_YAML_PATH.read_text())
    mapping = data.get("workflow", {}).get("lifecycle_mapping")
    if not mapping:
        return None
    return mapping


def _resolve_status_name(transition_id: int) -> str:
    """Reverse-lookup: transition ID → status name from status_mapping.

    Falls back to string of transition_id if not found.
    """
    if not _JIRA_YAML_PATH.exists():
        return str(transition_id)
    data = yaml.safe_load(_JIRA_YAML_PATH.read_text())
    status_mapping: dict[str, int] = data.get("workflow", {}).get("status_mapping", {})
    for name, tid in status_mapping.items():
        if tid == transition_id:
            return name
    return str(transition_id)


class JiraSyncHook:
    """Auto-sync work lifecycle events to Jira transitions.

    Reads ``lifecycle_mapping`` from ``.raise/jira.yaml``::

        workflow:
          lifecycle_mapping:
            story_start: 31   # → In Progress
            story_close: 41   # → Done
            epic_start: 31
            epic_close: 41

    Maps ``work:start`` + ``work_type=story`` → ``story_start`` → transition ID 31
    → adapter.transition_issue(issue_key, "in-progress").

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = ["work:start", "work:close"]
    priority: ClassVar[int] = -10  # after telemetry (priority 0)

    def handle(self, event: HookEvent) -> HookResult:
        """Handle work lifecycle events by triggering Jira transitions.

        Never raises — returns HookResult(status="error") on failure.
        """
        # 1. Type-narrow to work events
        if not isinstance(event, (WorkStartEvent, WorkCloseEvent)):
            return HookResult(status="ok")

        # 2. Skip if no issue key
        if not event.issue_key:
            logger.debug("JiraSyncHook: no issue_key, skipping")
            return HookResult(status="ok")

        # 3. Load lifecycle_mapping
        mapping = _load_lifecycle_mapping()
        if not mapping:
            logger.debug("JiraSyncHook: no lifecycle_mapping configured")
            return HookResult(status="ok")

        # 4. Resolve mapping key: "{work_type}_{action}"
        action = "start" if isinstance(event, WorkStartEvent) else "close"
        mapping_key = f"{event.work_type}_{action}"
        transition_id = mapping.get(mapping_key)
        if transition_id is None:
            logger.debug("JiraSyncHook: no mapping for %s", mapping_key)
            return HookResult(status="ok")

        # 5. Resolve status name from transition ID
        status_name = _resolve_status_name(transition_id)

        # 6. Call adapter
        try:
            from raise_cli.cli.commands._resolve import resolve_adapter

            adapter = resolve_adapter(None)
            adapter.transition_issue(event.issue_key, status_name)
            logger.info(
                "JiraSyncHook: %s → %s (%s)",
                event.issue_key,
                status_name,
                mapping_key,
            )
            return HookResult(status="ok")
        except Exception as exc:  # noqa: BLE001
            msg = f"JiraSyncHook: {type(exc).__name__}: {exc}"
            logger.warning(msg)
            return HookResult(status="error", message=msg)
