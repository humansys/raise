"""CLI entry-point resolver for adapters and targets.

PM adapter resolution delegates to the domain-level resolver
(adapters.resolve) and translates AdapterResolutionError into
sys.exit(1) + Rich output for CLI callers.

Docs target resolution remains here (resolve_docs_target) until
a future story extracts it similarly.
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
from raise_cli.adapters.registry import get_doc_targets
from raise_cli.adapters.resolve import LOCAL_PM_ADAPTERS, discover_pm
from raise_cli.adapters.sync import SyncDocsAdapter
from raise_cli.exceptions import AdapterResolutionError
from raise_cli.output.symbols import WARN

logger = logging.getLogger(__name__)

console = Console()
console_err = Console(stderr=True)

# Re-export for backlog.py:427 which imports discover_pm from here
_discover_pm = discover_pm


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
    except FileNotFoundError as exc:
        name = selected or next(iter(entries))
        console.print(
            f"[red]Error:[/red] {group_label} '{name}' config file not found.\n\n"
            f"  {exc}\n\n"
            f"To fix, run:  [bold]rai adapter-setup[/bold]\n"
            f"Or create the config file manually."
        )
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
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


def resolve_adapter(adapter_name: str | None) -> ProjectManagementAdapter:
    """CLI wrapper — delegates to domain resolver, translates errors to sys.exit."""
    from raise_cli.adapters.resolve import resolve_pm_adapter

    _warn_if_implicit_multi_remote(adapter_name)
    _warn_if_filesystem_selected(adapter_name)
    try:
        return resolve_pm_adapter(adapter_name)
    except AdapterResolutionError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)


def _warn_if_filesystem_selected(adapter_name: str | None) -> None:
    """Warn only when the caller explicitly asked for the deprecated adapter.

    ``FilesystemPMAdapter`` is also constructed internally by
    ``_compose_pm_adapters`` on every resolution, so warning from its
    ``__init__`` fires on invocations the user never opted into — and pollutes
    ``--json`` output (RAISE-16940).
    """
    if adapter_name != "filesystem":
        return
    console_err.print(
        f"[yellow]{WARN} -a filesystem is deprecated — use -a local instead. "
        "Will be removed soon.[/yellow]"
    )


def _warn_if_implicit_multi_remote(adapter_name: str | None) -> None:
    """Emit warning when 2+ remotes will be used without explicit selection."""
    if adapter_name is not None:
        return
    entries = _discover_pm()
    remote_names = sorted(n for n in entries if n not in LOCAL_PM_ADAPTERS)
    if len(remote_names) < 2:
        return
    local_names = sorted(n for n in entries if n in LOCAL_PM_ADAPTERS)
    all_names = ", ".join(local_names + remote_names)
    console_err.print(
        f"[yellow]Warning:[/yellow] Writing to {len(local_names) + len(remote_names)} adapters: {all_names}. "
        f"Use -a <name> or -a all to select explicitly."
    )


def get_effective_adapter_name(adapter_name: str | None) -> str:
    """Resolve the effective adapter name string without instantiating.

    Mirrors the name-resolution logic in resolve_adapter() so write
    commands can determine which backlog.yaml section to update.
    """
    if adapter_name == "all":
        raise AdapterResolutionError(
            "'-a all' is not valid for config commands — "
            "use -a <name> to target a specific adapter's config section."
        )
    if adapter_name is not None:
        return adapter_name
    entries = _discover_pm()
    if len(entries) == 1:
        return next(iter(entries))
    if len(entries) == 0:
        return "jira"
    # 2+ entries: exclude local adapters (S16533.3), require exactly 1 remote
    remote_entries = {k: v for k, v in entries.items() if k not in LOCAL_PM_ADAPTERS}
    if len(remote_entries) == 1:
        return next(iter(remote_entries))
    # 2+ remotes or only filesystem — caller must pass -a explicitly
    raise AdapterResolutionError(
        "Multiple PM adapters configured. Use -a to select one explicitly."
    )


def _get_configured_doc_types(project_root: Path | None = None) -> set[str] | None:
    """Return target types declared in docs.yaml, or None if no config found.

    ``project_root`` anchors config resolution to the caller's checkout
    (S15457.2); None preserves the legacy process-CWD resolution.
    """
    from raise_cli.adapters.confluence_config import load_docs_config

    try:
        config = load_docs_config(project_root or Path.cwd())
        return {t.get("type", "") for t in config.targets.values()}
    except FileNotFoundError:
        return None


def _get_default_doc_target_type(project_root: Path | None = None) -> str | None:
    """Return the adapter type configured for docs.yaml's default target."""
    from raise_cli.adapters.confluence_config import load_docs_config

    try:
        config = load_docs_config(project_root or Path.cwd())
        return config.get_target_type()
    except FileNotFoundError:
        return None


def _discover_docs(
    project_root: Path | None = None,
    *,
    apply_config_filter: bool = True,
) -> dict[str, Callable[[], Any]]:
    """Merge YAML and entry point docs targets, filtered by docs.yaml config.

    Only activates EP adapters whose name matches a configured target type.
    filesystem is always included. Falls back to all adapters if no config exists.
    EP wins on name collision with YAML adapters.

    ``apply_config_filter=False`` (RAISE-16657 D1) returns every discovered
    target unfiltered -- used only when the caller names a single target
    explicitly, so an explicit ``--target platform`` is never silently
    dropped just because docs.yaml doesn't mention it. Auto-detect and
    ``--target all`` keep the filter (default True).
    """
    from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

    yaml_entries = discover_yaml_adapters(
        "docs",
        adapters_dir=((project_root / ".raise" / "adapters") if project_root else None),
    )
    ep_entries = get_doc_targets()

    if not apply_config_filter:
        return {**yaml_entries, **ep_entries}

    configured_types = _get_configured_doc_types(project_root)
    if configured_types is None:
        return {**yaml_entries, **ep_entries}

    filtered_ep = {
        name: factory
        for name, factory in ep_entries.items()
        if name == "filesystem" or name in configured_types
    }
    return {**yaml_entries, **filtered_ep}


def _compose_docs_targets(
    entries: dict[str, Callable[[], Any]],
    require_local: bool,
    project_root: Path | None = None,
) -> DocumentationTarget:
    """Instantiate all docs targets for an explicit multi-target operation."""
    from raise_cli.adapters.composite_docs import CompositeDocTarget
    from raise_cli.adapters.filesystem_docs import FilesystemDocsTarget
    from raise_cli.adapters.pending_ops import PendingOpsLog

    local_instances: list[Any] = []
    remote_instances: list[Any] = []
    for name, cls in entries.items():
        try:
            instance = cls()
            if inspect.iscoroutinefunction(getattr(instance, "get_page", None)):
                instance = SyncDocsAdapter(instance)
            if isinstance(instance, FilesystemDocsTarget):
                local_instances.append(instance)
            else:
                remote_instances.append(instance)
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("Skipping docs target '%s': %s", name, exc)

    instances = local_instances + remote_instances
    if not instances:
        console.print("[red]Error:[/red] All docs targets failed to initialize.")
        sys.exit(1)

    logger.debug(
        "Composing %d explicit docs targets (local=%d, remote=%d): %s",
        len(instances),
        len(local_instances),
        len(remote_instances),
        ", ".join(entries.keys()),
    )
    root = project_root or Path.cwd()
    return CompositeDocTarget(
        instances,
        pending_ops=PendingOpsLog(domain="docs", project_root=root),
        project_root=root,
        require_local=require_local,
    )


def _compose_docs_target_with_local(
    entries: dict[str, Callable[[], Any]],
    target_name: str,
    project_root: Path | None = None,
) -> DocumentationTarget:
    """Compose the selected docs target with the mandatory local writer."""
    from raise_cli.adapters.filesystem_docs import FilesystemDocsTarget

    selected = entries[target_name]
    local = entries.get("filesystem", FilesystemDocsTarget)
    selected_entries = {"filesystem": local}
    if target_name != "filesystem":
        selected_entries[target_name] = selected
    return _compose_docs_targets(
        selected_entries, require_local=True, project_root=project_root
    )


def resolve_docs_target(
    target_name: str | None,
    require_local: bool = False,
    project_root: Path | None = None,
) -> DocumentationTarget:
    """Resolve a DocumentationTarget from entry points and YAML configs.

    An omitted target selects the adapter type for docs.yaml's default target.
    Use ``--target all`` to compose every discovered target explicitly.

    ``project_root`` anchors docs.yaml/YAML-adapter resolution to the
    caller's checkout (S15457.2); None preserves the legacy process-CWD
    resolution for CLI callers.
    """
    if target_name == "all":
        entries = _discover_docs(project_root)
        return _compose_docs_targets(entries, require_local, project_root)

    if target_name is not None:
        # Explicit single-target selection bypasses docs.yaml's type filter
        # (RAISE-16657 D1) -- only auto-detect and --target all keep it.
        entries = _discover_docs(project_root, apply_config_filter=False)
        if require_local and target_name in entries:
            return _compose_docs_target_with_local(entries, target_name, project_root)
        return resolve_entrypoint(
            discover=lambda: _discover_docs(project_root, apply_config_filter=False),
            sync_wrapper=SyncDocsAdapter,
            async_check_method="get_page",
            group_label="docs target",
            flag_name="--target",
            selected=target_name,
        )

    entries = _discover_docs(project_root)

    if len(entries) == 0:
        console.print(
            "[red]Error:[/red] No docs target installed.\n"
            "Install one or register via entry points. Use --target to select."
        )
        sys.exit(1)

    default_type = _get_default_doc_target_type(project_root)
    if default_type is not None:
        if default_type not in entries:
            available = ", ".join(sorted(entries))
            console.print(
                "[red]Error:[/red] Configured default docs target type "
                f"'{default_type}' is not installed. Available: {available}"
            )
            sys.exit(1)
        if require_local:
            return _compose_docs_target_with_local(entries, default_type, project_root)
        return resolve_entrypoint(
            discover=lambda: _discover_docs(project_root),
            sync_wrapper=SyncDocsAdapter,
            async_check_method="get_page",
            group_label="docs target",
            flag_name="--target",
            selected=default_type,
        )

    if len(entries) == 1:
        if require_local:
            return _compose_docs_target_with_local(
                entries, next(iter(entries)), project_root
            )
        return resolve_entrypoint(
            discover=lambda: _discover_docs(project_root),
            sync_wrapper=SyncDocsAdapter,
            async_check_method="get_page",
            group_label="docs target",
            flag_name="--target",
            selected=None,
        )

    names = ", ".join(sorted(entries))
    console.print(
        f"[red]Error:[/red] Multiple docs targets found: {names}.\n"
        "Use --target <name>, --target all, or configure default_target in docs.yaml."
    )
    sys.exit(1)
