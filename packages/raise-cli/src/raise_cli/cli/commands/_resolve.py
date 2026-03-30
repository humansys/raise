"""Generic entry-point resolver for adapters and targets.

Parametrized auto-detect logic:
- 1 registered → auto-select
- 0 registered → error with install guidance
- 2+ registered → error listing names, request flag
- flag → select by name (override)

Auto-wraps async implementations with the provided sync wrapper.

Replaces ``_adapter_resolve.py`` (S301.4, D7 — DRY).
"""

from __future__ import annotations

import inspect
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rich.console import Console

from raise_cli.adapters.protocols import DocumentationTarget, ProjectManagementAdapter
from raise_cli.adapters.registry import get_doc_targets, get_pm_adapters
from raise_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter
from raise_cli.onboarding.manifest import load_manifest

logger = logging.getLogger(__name__)

console = Console()


def resolve_entrypoint(
    discover: Callable[[], dict[str, Callable[[], Any]]],
    sync_wrapper: type | None,
    async_check_method: str,
    group_label: str,
    flag_name: str,
    selected: str | None,
) -> Any:
    """Resolve and instantiate an adapter/target from entry points and YAML configs.

    Args:
        discover: Function returning {name: factory} from entry points and/or YAML.
        sync_wrapper: Wrapper class for async→sync bridging (or None).
        async_check_method: Method name to check for async (e.g., "get_issue").
        group_label: Human label for error messages (e.g., "PM adapter").
        flag_name: CLI flag name for error messages (e.g., "--adapter").
        selected: Explicit selection by name, or None for auto-detect.

    Returns:
        An instantiated adapter/target, wrapped if async.

    Raises:
        SystemExit: If resolution fails.
    """
    entries = discover()

    if selected is not None:
        cls = entries.get(selected)
        if cls is None:
            available = ", ".join(sorted(entries)) if entries else "none"
            console.print(
                f"[red]Error:[/red] {group_label} '{selected}' not found. "
                f"Available: {available}"
            )
            sys.exit(1)
    elif len(entries) == 0:
        console.print(
            f"[red]Error:[/red] No {group_label} installed.\n"
            f"Install one or register via entry points. Use {flag_name} to select."
        )
        sys.exit(1)
    elif len(entries) == 1:
        cls = next(iter(entries.values()))
    else:
        names = ", ".join(sorted(entries))
        console.print(
            f"[red]Error:[/red] Multiple {group_label}s found: {names}.\n"
            f"Use {flag_name} <name> to select."
        )
        sys.exit(1)

    try:
        instance = cls()
    except Exception as exc:
        name = selected or next(iter(entries))
        console.print(
            f"[red]Error:[/red] Failed to instantiate {group_label} '{name}': {exc}"
        )
        sys.exit(1)

    # Auto-wrap async implementations for sync CLI consumption
    if sync_wrapper and inspect.iscoroutinefunction(
        getattr(instance, async_check_method, None)
    ):
        instance = sync_wrapper(instance)

    return instance


def _discover_pm() -> dict[str, Callable[[], Any]]:
    """Merge YAML and entry point PM adapters. EP wins on name collision."""
    from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

    return {**discover_yaml_adapters("pm"), **get_pm_adapters()}


def _discover_docs() -> dict[str, Callable[[], Any]]:
    """Merge YAML and entry point docs targets. EP wins on name collision."""
    from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

    return {**discover_yaml_adapters("docs"), **get_doc_targets()}


def resolve_adapter(adapter_name: str | None) -> ProjectManagementAdapter:
    """Resolve a ProjectManagementAdapter from entry points and YAML configs.

    Resolution priority:
    1. Explicit adapter_name (from -a/--adapter flag) → use it
    2. Manifest backlog.adapter_default → use it
    3. Auto-detect (single adapter) or error (0 / 2+)
    """
    effective = adapter_name

    if effective is None:
        manifest = load_manifest(Path.cwd())
        if manifest and manifest.backlog and manifest.backlog.adapter_default:
            effective = manifest.backlog.adapter_default
            logger.debug("Using manifest default adapter: %s", effective)

    return resolve_entrypoint(
        discover=_discover_pm,
        sync_wrapper=SyncPMAdapter,
        async_check_method="get_issue",
        group_label="PM adapter",
        flag_name="--adapter",
        selected=effective,
    )


def resolve_docs_target(target_name: str | None) -> DocumentationTarget:
    """Resolve a DocumentationTarget from entry points and YAML configs.

    Unlike PM adapters, docs targets auto-compose when multiple are found:
    2+ targets without --target flag → CompositeDocTarget wrapping all.
    With --target flag → single target selected (no composition).
    """
    if target_name is not None:
        # Explicit selection — delegate to standard resolver (single target)
        return resolve_entrypoint(
            discover=_discover_docs,
            sync_wrapper=SyncDocsAdapter,
            async_check_method="get_page",
            group_label="docs target",
            flag_name="--target",
            selected=target_name,
        )

    entries = _discover_docs()

    if len(entries) == 0:
        console.print(
            "[red]Error:[/red] No docs target installed.\n"
            "Install one or register via entry points. Use --target to select."
        )
        sys.exit(1)

    if len(entries) == 1:
        return resolve_entrypoint(
            discover=_discover_docs,
            sync_wrapper=SyncDocsAdapter,
            async_check_method="get_page",
            group_label="docs target",
            flag_name="--target",
            selected=None,
        )

    # 2+ targets — auto-compose into CompositeDocTarget
    from raise_cli.adapters.composite_docs import CompositeDocTarget

    instances: list[Any] = []
    for name, cls in entries.items():
        try:
            instance = cls()
            if inspect.iscoroutinefunction(getattr(instance, "get_page", None)):
                instance = SyncDocsAdapter(instance)
            instances.append(instance)
        except Exception as exc:
            logger.warning("Skipping docs target '%s': %s", name, exc)

    if not instances:
        console.print("[red]Error:[/red] All docs targets failed to initialize.")
        sys.exit(1)

    logger.debug(
        "Auto-composing %d docs targets: %s",
        len(instances),
        ", ".join(entries.keys()),
    )
    return CompositeDocTarget(instances)
