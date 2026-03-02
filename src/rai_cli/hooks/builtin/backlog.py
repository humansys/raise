"""Built-in BacklogHook — syncs Jira state on work lifecycle events.

Listens to ``work:lifecycle`` events (fired by ``rai signal emit-work``)
and calls the ProjectManagementAdapter to create/transition Jira issues.

Error isolation: ``handle()`` never raises. Adapter or config failures are
logged and returned as ``HookResult(status="error")``.

Architecture: ADR-039 §5 (Built-in hooks), S325.4
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, ClassVar

import yaml

from rai_cli.adapters.models import IssueSpec
from rai_cli.hooks.events import HookEvent, HookResult, WorkLifecycleEvent

logger = logging.getLogger(__name__)

# Events that trigger backlog actions
_ACTIONABLE_EVENTS = frozenset({"start", "complete"})

# Map (work_type, event) → lifecycle_mapping key
_LIFECYCLE_KEY_MAP: dict[tuple[str, str], str] = {
    ("story", "start"): "story_start",
    ("story", "complete"): "story_close",
    ("epic", "start"): "epic_start",
    ("epic", "complete"): "epic_close",
}

# Map lifecycle_mapping key → target status for rai backlog transition
_STATUS_MAP: dict[str, str] = {
    "story_start": "in-progress",
    "story_close": "done",
    "epic_start": "in-progress",
    "epic_close": "done",
}


class _JiraConfig:
    """Parsed jira.yaml config relevant to BacklogHook."""

    __slots__ = ("project_key", "lifecycle_mapping")

    def __init__(self, project_key: str, lifecycle_mapping: dict[str, int]) -> None:
        self.project_key = project_key
        self.lifecycle_mapping = lifecycle_mapping


def _load_jira_config(project_root: Path) -> _JiraConfig | None:
    """Load project key and lifecycle_mapping from .raise/jira.yaml.

    Returns None if file missing, unparseable, or missing required sections.
    """
    config_path = project_root / ".raise" / "jira.yaml"
    if not config_path.exists():
        return None
    try:
        with open(config_path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        workflow = data.get("workflow", {})
        mapping: dict[str, int] | None = workflow.get("lifecycle_mapping")
        if mapping is None:
            return None
        projects = data.get("projects", {})
        project_key = next(iter(projects), None) if projects else None
        if project_key is None:
            return None
        return _JiraConfig(project_key=project_key, lifecycle_mapping=mapping)
    except Exception:  # noqa: BLE001
        logger.warning("Failed to parse .raise/jira.yaml")
        return None


def _resolve_jira_key(
    adapter: Any, work_id: str, project_key: str
) -> str | None:
    """Search for Jira issue by work_id in summary.

    Returns the issue key if found, None otherwise.
    """
    query = f'project = "{project_key}" AND summary ~ "{work_id}"'
    results = adapter.search(query, limit=1)
    if results:
        return results[0].key
    return None


def resolve_adapter() -> Any:
    """Resolve ProjectManagementAdapter. Separated for testability."""
    from rai_cli.cli.commands._resolve import (
        resolve_adapter as _resolve,
    )

    return _resolve("jira")


class BacklogHook:
    """Syncs Jira state on work lifecycle events.

    Subscribes to ``work:lifecycle`` events and maps them to
    ``rai backlog`` actions using ``.raise/jira.yaml`` lifecycle_mapping.

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = ["work:lifecycle"]
    priority: ClassVar[int] = 0
    timeout: ClassVar[float] = 30.0  # MCP bridge cold start needs >5s

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path(".")

    def handle(self, event: HookEvent) -> HookResult:
        """Handle a work lifecycle event by syncing Jira.

        Never raises — returns HookResult with status and message.
        """
        if not isinstance(event, WorkLifecycleEvent):
            return HookResult(status="ok")

        # Only act on start/complete
        if event.event not in _ACTIONABLE_EVENTS:
            return HookResult(status="ok")

        # Load jira config
        config = _load_jira_config(self._project_root)
        if config is None:
            return HookResult(status="error", message="no jira.yaml or lifecycle_mapping")

        # Determine lifecycle key
        lifecycle_key = _LIFECYCLE_KEY_MAP.get((event.work_type, event.event))
        if lifecycle_key is None:
            return HookResult(status="ok")

        # Resolve adapter
        try:
            adapter = resolve_adapter()
        except Exception as exc:  # noqa: BLE001
            return HookResult(status="error", message=f"adapter unavailable: {exc}")

        # Resolve Jira key
        try:
            jira_key = _resolve_jira_key(adapter, event.work_id, config.project_key)
        except Exception as exc:  # noqa: BLE001
            return HookResult(status="error", message=f"search failed: {exc}")

        target_status = _STATUS_MAP[lifecycle_key]

        # Handle start: create if missing, then transition
        if event.event == "start":
            if jira_key is None:
                try:
                    issue_type = "Epic" if event.work_type == "epic" else "Story"
                    spec = IssueSpec(
                        summary=f"{event.work_id}",
                        issue_type=issue_type,
                    )
                    ref = adapter.create_issue(config.project_key, spec)
                    jira_key = ref.key
                except Exception as exc:  # noqa: BLE001
                    return HookResult(status="error", message=f"create failed: {exc}")

            try:
                adapter.transition_issue(jira_key, target_status)
            except Exception as exc:  # noqa: BLE001
                return HookResult(status="error", message=f"transition failed: {exc}")

            return HookResult(status="ok")

        # Handle complete: transition existing issue
        if event.event == "complete":
            if jira_key is None:
                return HookResult(status="error", message=f"no Jira issue found for {event.work_id}")

            try:
                adapter.transition_issue(jira_key, target_status)
            except Exception as exc:  # noqa: BLE001
                return HookResult(status="error", message=f"transition failed: {exc}")

            return HookResult(status="ok")

        return HookResult(status="ok")
