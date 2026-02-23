"""Output formatters for adapter commands."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console


def format_list_human(
    tier: str,
    groups: list[dict[str, Any]],
    console: Console,
) -> None:
    """Display adapter list grouped by entry point group.

    Args:
        tier: Current tier level.
        groups: List of dicts with group, protocol_name, adapters keys.
        console: Rich console for output.
    """
    console.print(f"Tier: {tier}\n")

    for group_info in groups:
        header = f"{group_info['group']} ({group_info['protocol_name']})"
        console.print(f"[bold]{header}[/bold]")

        adapters = group_info["adapters"]
        if not adapters:
            console.print("  [dim](none)[/dim]")
        else:
            for adapter in adapters:
                console.print(f"  {adapter['name']:<20s}{adapter['package']}")

        console.print()


def format_list_json(tier: str, groups: list[dict[str, Any]]) -> str:
    """Format adapter list as JSON.

    Args:
        tier: Current tier level.
        groups: List of dicts with group, protocol_name, adapters keys.

    Returns:
        JSON string.
    """
    return json.dumps({"tier": tier, "groups": groups}, indent=2)


def format_check_human(
    results: list[dict[str, Any]],
    console: Console,
) -> None:
    """Display adapter check results with pass/fail indicators.

    Args:
        results: List of dicts with group, name, protocol_name, compliant, error keys.
        console: Rich console for output.
    """
    if not results:
        console.print("No adapters registered.")
        return

    console.print("Checking adapters...\n")

    current_group = ""
    for r in results:
        if r["group"] != current_group:
            current_group = r["group"]
            console.print(f"[bold]{current_group}[/bold]")

        if r["compliant"]:
            console.print(
                f"  [green]\u2713[/green] {r['name']:<20s}{r['protocol_name']} compliant"
            )
        else:
            console.print(
                f"  [red]\u2717[/red] {r['name']:<20s}{r['error']}"
            )

    passed = sum(1 for r in results if r["compliant"])
    total = len(results)
    console.print()
    if passed == total:
        console.print(f"[green]All {total} adapters passed.[/green]")
    else:
        failed = total - passed
        console.print(f"[red]{failed} of {total} adapters failed.[/red]")


def format_check_json(results: list[dict[str, Any]]) -> str:
    """Format adapter check results as JSON.

    Args:
        results: List of dicts with group, name, protocol_name, compliant, error keys.

    Returns:
        JSON string.
    """
    passed = sum(1 for r in results if r["compliant"])
    return json.dumps(
        {
            "results": results,
            "total": len(results),
            "passed": passed,
            "all_passed": passed == len(results),
        },
        indent=2,
    )
