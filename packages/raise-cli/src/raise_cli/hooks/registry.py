"""Hook registry with entry point discovery.

Discovers LifecycleHook implementations registered via Python entry points
(``[project.entry-points."rai.hooks"]`` in pyproject.toml). Validates
Protocol conformance before accepting hooks.

Architecture: ADR-039 §3 (Entry point discovery via stevedore)
"""

from __future__ import annotations

import inspect
import logging
from importlib.metadata import entry_points
from typing import Any

from raise_cli.hooks.protocol import LifecycleHook

logger = logging.getLogger(__name__)

EP_HOOKS: str = "rai.hooks"


def _dist_name(ep: Any) -> str:
    """Best-effort extraction of the distribution name for an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


class HookRegistry:
    """Discovers and manages LifecycleHook implementations.

    Example::

        registry = HookRegistry()
        registry.discover()  # loads from rai.hooks entry points

        for hook in registry.hooks:
            print(f"{hook.__class__.__name__}: priority={hook.priority}")

        handlers = registry.get_hooks_for_event("session:start")
    """

    def __init__(self) -> None:
        self._hooks: list[LifecycleHook] = []

    @property
    def hooks(self) -> list[LifecycleHook]:
        """Return a copy of registered hooks."""
        return list(self._hooks)

    def discover(self) -> None:
        """Load hooks from ``rai.hooks`` entry points.

        Skips entry points that:
        - Fail to load (ImportError, etc.)
        - Are not classes
        - Don't conform to the LifecycleHook Protocol
        """
        for ep in entry_points(group=EP_HOOKS):
            try:
                loaded: Any = ep.load()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Skipping hook entry point '%s' from '%s': %s",
                    ep.name,
                    _dist_name(ep),
                    exc,
                )
                continue

            if not inspect.isclass(loaded):
                logger.warning(
                    "Skipping hook entry point '%s' from '%s': expected a class, got %s",
                    ep.name,
                    _dist_name(ep),
                    type(loaded).__name__,
                )
                continue

            instance = loaded()
            if not isinstance(instance, LifecycleHook):
                logger.warning(
                    "Skipping hook entry point '%s' from '%s': "
                    "does not conform to LifecycleHook Protocol",
                    ep.name,
                    _dist_name(ep),
                )
                continue

            self._hooks.append(instance)
            logger.debug(
                "Loaded hook '%s' (priority=%d, events=%s)",
                ep.name,
                instance.priority,
                instance.events,
            )

    def register(self, hook: LifecycleHook | Any) -> None:
        """Manually register a hook instance (useful for testing).

        Silently skips non-compliant objects.
        """
        if not isinstance(hook, LifecycleHook):
            logger.warning(
                "Skipping manual hook registration: %s does not conform to LifecycleHook Protocol",
                type(hook).__name__,
            )
            return
        self._hooks.append(hook)

    def get_hooks_for_event(self, event_name: str) -> list[LifecycleHook]:
        """Return hooks subscribed to ``event_name``, sorted by priority (highest first)."""
        matching = [h for h in self._hooks if event_name in h.events]
        return sorted(matching, key=lambda h: h.priority, reverse=True)
