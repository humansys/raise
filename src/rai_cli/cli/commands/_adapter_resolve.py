"""Resolve a ProjectManagementAdapter from entry point registry.

Auto-detect logic (D3):
- 1 registered → auto-select
- 0 registered → error with install guidance
- 2+ registered → error listing names, request --adapter flag
- --adapter flag → select by name (override)

Instantiation (AR3): no-arg constructor. Config injection is the adapter's
responsibility (e.g., JiraAdapter reads env vars in __init__).
"""

from __future__ import annotations

import sys

from rich.console import Console

from rai_cli.adapters.protocols import ProjectManagementAdapter
from rai_cli.adapters.registry import get_pm_adapters

console = Console()


def resolve_adapter(adapter_name: str | None) -> ProjectManagementAdapter:
    """Resolve and instantiate a PM adapter.

    Args:
        adapter_name: Explicit adapter name (from --adapter flag), or None for auto-detect.

    Returns:
        An instantiated ProjectManagementAdapter.

    Raises:
        SystemExit: If no adapter found, multiple without flag, or instantiation fails.
    """
    adapters = get_pm_adapters()

    if adapter_name is not None:
        # Explicit selection
        cls = adapters.get(adapter_name)
        if cls is None:
            available = ", ".join(sorted(adapters)) if adapters else "none"
            console.print(
                f"[red]Error:[/red] Adapter '{adapter_name}' not found. "
                f"Available: {available}"
            )
            sys.exit(1)
    elif len(adapters) == 0:
        console.print(
            "[red]Error:[/red] No PM adapter installed.\n"
            "Install rai-pro or register one via entry points in group 'rai.adapters.pm'."
        )
        sys.exit(1)
    elif len(adapters) == 1:
        cls = next(iter(adapters.values()))
    else:
        names = ", ".join(sorted(adapters))
        console.print(
            f"[red]Error:[/red] Multiple PM adapters found: {names}.\n"
            "Use --adapter <name> to select."
        )
        sys.exit(1)

    try:
        instance = cls()
    except Exception as exc:
        console.print(
            f"[red]Error:[/red] Failed to instantiate adapter '{adapter_name or next(iter(adapters))}': {exc}"
        )
        sys.exit(1)

    return instance  # type: ignore[return-value]
