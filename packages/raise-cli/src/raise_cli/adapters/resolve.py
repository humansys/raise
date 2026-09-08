"""Domain-level adapter resolution — no CLI dependencies (sys.exit, Rich).

Raises AdapterResolutionError on failure instead of calling sys.exit().
CLI layer wraps this to translate errors into user-facing Rich output.
"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from raise_cli.adapters.backlog_config import (
    get_configured_adapters,
    migrate_jira_yaml_if_needed,
)
from raise_cli.adapters.protocols import DocumentationTarget, ProjectManagementAdapter
from raise_cli.adapters.registry import get_doc_targets, get_pm_adapters
from raise_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter
from raise_cli.config.server import get_server_credentials
from raise_cli.exceptions import AdapterResolutionError

logger = logging.getLogger(__name__)

LOCAL_PM_ADAPTERS: frozenset[str] = frozenset({"filesystem", "local"})
"""Entry-point names of the offline PM adapters.

These are always discoverable (no ``backlog.yaml`` section required) and are
excluded when callers count *remote* adapters. Single source of truth: the set
was previously spelled inline in four places as ``("filesystem", "sqlite")``,
and ``sqlite`` was never a registered entry point — the SQLite adapter
registers as ``local`` (see ``pyproject.toml``, ``rai.adapters.pm``). The
mismatch kept it filtered out of every configured project until RAISE-16940.
"""


def discover_pm(project_root: Path | None = None) -> dict[str, Callable[[], Any]]:
    """Merge YAML and entry point PM adapters, gating EP adapters via backlog.yaml.

    YAML-configured adapters (.raise/adapters/*.yaml) are always included —
    they represent explicit user configuration.
    EP-registered adapters (e.g. jira) are only included if backlog.yaml has a
    matching section. filesystem is always included.
    If backlog.yaml doesn't exist, no filtering is applied (backwards compat).
    """
    from raise_cli.adapters.declarative.discovery import discover_yaml_adapters

    root = project_root or Path.cwd()
    migrate_jira_yaml_if_needed(root)
    yaml_entries = discover_yaml_adapters(
        "pm", adapters_dir=root / ".raise" / "adapters"
    )
    ep_entries = get_pm_adapters()
    configured = get_configured_adapters(root)
    if not configured:
        return {**yaml_entries, **ep_entries}
    filtered_ep = {
        name: factory
        for name, factory in ep_entries.items()
        if name in configured or name in LOCAL_PM_ADAPTERS
    }
    return {**yaml_entries, **filtered_ep}


def _discover_pm_for(project_root: Path | None = None) -> dict[str, Callable[[], Any]]:
    """Call discover_pm compatibly with legacy test monkeypatches."""
    if project_root is None:
        return discover_pm()
    return discover_pm(project_root)


def _resolve_entrypoint(
    entries: dict[str, Callable[[], Any]],
    sync_wrapper: type | None,
    async_check_method: str,
    group_label: str,
    selected: str | None,
    project_root: Path | None = None,
) -> Any:
    """Select and instantiate an adapter from discovered entries.

    Raises AdapterResolutionError on all failure paths.
    """
    if selected is not None:
        cls = entries.get(selected)
        if cls is None:
            available = ", ".join(sorted(entries)) if entries else "none"
            raise AdapterResolutionError(
                f"{group_label} '{selected}' not found. Available: {available}"
            )
    elif len(entries) == 0:
        raise AdapterResolutionError(
            f"No {group_label} installed. Install one or register via entry points."
        )
    elif len(entries) == 1:
        cls = next(iter(entries.values()))
    else:
        names = ", ".join(sorted(entries))
        raise AdapterResolutionError(
            f"Multiple {group_label}s found: {names}. "
            f"Use explicit selection to pick one."
        )

    try:
        signature = inspect.signature(cls)
        if project_root is not None and "project_root" in signature.parameters:
            factory = cast("Any", cls)
            instance = factory(project_root=project_root)
        else:
            instance = cls()
    except FileNotFoundError as exc:
        name = selected or next(iter(entries))
        raise AdapterResolutionError(
            f"{group_label} '{name}' config file not found: {exc}\n"
            f"To fix, run: rai adapter-setup"
        ) from exc
    except Exception as exc:
        name = selected or next(iter(entries))
        raise AdapterResolutionError(
            f"Failed to instantiate {group_label} '{name}': {exc}"
        ) from exc

    if sync_wrapper and inspect.iscoroutinefunction(
        getattr(instance, async_check_method, None)
    ):
        instance = sync_wrapper(instance)

    return instance


def _wrap_with_ledger(adapter: Any, project_root: Path | None = None) -> Any:
    """Wrap remote adapter with LedgerAwareAdapter for local→remote key translation."""
    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.ledger_aware import LedgerAwareAdapter
    from raise_cli.adapters.sqlite_pm import SQLitePMAdapter
    from raise_cli.storage.work_items import WorkItemStore

    if isinstance(adapter, (FilesystemPMAdapter, SQLitePMAdapter, LedgerAwareAdapter)):
        return adapter

    root = project_root or Path.cwd()
    wi_store = WorkItemStore(root)
    logger.debug(
        "Wrapping adapter with LedgerAwareAdapter (%d key mappings)",
        len(wi_store.all_jira_mappings()),
    )
    return LedgerAwareAdapter(adapter, wi_store)


def _wrap_with_graph_refresh(adapter: Any, project_root: Path | None = None) -> Any:
    """Wrap adapter with GraphRefreshAdapter for backlog-items cartridge refresh.

    Design DS-2: applied at every resolve_pm_adapter return path, OUTSIDE any
    ledger/composite wrapping, so one refresh fires per logical mutation
    regardless of routing. Idempotent (skips if already wrapped) and skips
    FilesystemPMAdapter (local source-of-truth; no remote-keyed cartridge to
    refresh — same exclusion `_wrap_with_ledger` applies).
    """
    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.graph_refresh import GraphRefreshAdapter
    from raise_cli.adapters.sqlite_pm import SQLitePMAdapter

    if isinstance(adapter, (FilesystemPMAdapter, SQLitePMAdapter, GraphRefreshAdapter)):
        return adapter

    root = project_root or Path.cwd()
    logger.debug("Wrapping adapter with GraphRefreshAdapter (project_root=%s)", root)
    return GraphRefreshAdapter(adapter, root)


def _compose_pm_adapters(
    entries: dict[str, Callable[[], Any]],
    project_root: Path | None = None,
) -> ProjectManagementAdapter:
    """Auto-compose 2+ PM adapters into a CompositeBacklogAdapter."""
    from raise_cli.adapters.composite_pm import CompositeBacklogAdapter
    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.pending_ops import PendingOpsLog
    from raise_cli.adapters.sqlite_pm import SQLitePMAdapter
    from raise_cli.storage.work_items import WorkItemStore

    local_instances: list[Any] = []
    remote_instances: list[Any] = []
    for name, cls in entries.items():
        try:
            signature = inspect.signature(cls)
            if project_root is not None and "project_root" in signature.parameters:
                factory = cast("Any", cls)
                instance = factory(project_root=project_root)
            else:
                instance = cls()
            if inspect.iscoroutinefunction(getattr(instance, "get_issue", None)):
                instance = SyncPMAdapter(instance)
            if isinstance(instance, (FilesystemPMAdapter, SQLitePMAdapter)):
                local_instances.append(instance)
            else:
                remote_instances.append(_wrap_with_ledger(instance, project_root))
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("Skipping PM adapter '%s': %s", name, exc)

    # D-S3.6: SQLitePMAdapter replaces FilesystemPMAdapter when both present.
    has_sqlite = any(isinstance(i, SQLitePMAdapter) for i in local_instances)
    if has_sqlite:
        dropped_fs = [i for i in local_instances if isinstance(i, FilesystemPMAdapter)]
        local_instances = [
            i for i in local_instances if not isinstance(i, FilesystemPMAdapter)
        ]
        # RAISE-16940: dropping the YAML store silently strands a backlog that
        # was never migrated. Warn once per invocation when YAML items exist
        # but work_items is empty — `rai backlog migrate` is the documented,
        # idempotent, non-destructive import.
        if dropped_fs:
            _warn_if_unmigrated_yaml_backlog(project_root, WorkItemStore)

    instances = local_instances + remote_instances

    if not instances:
        raise AdapterResolutionError("All PM adapters failed to initialize.")

    logger.debug(
        "Auto-composing %d PM adapters (local=%d, remote=%d): %s",
        len(instances),
        len(local_instances),
        len(remote_instances),
        ", ".join(entries.keys()),
    )
    root = project_root or Path.cwd()
    wi_store = WorkItemStore(root)
    pending = PendingOpsLog(domain="backlog", project_root=root)
    # Consulta env vars + ~/.rai/server.json (vía get_server_credentials).
    # El código anterior solo leía env vars, ignorando rai connect → server.json.
    server_first = get_server_credentials() is not None
    return CompositeBacklogAdapter(
        instances, wi_store, pending, server_first=server_first
    )


_unmigrated_warned: set[str] = set()


def _warn_if_unmigrated_yaml_backlog(
    project_root: Path | None, work_item_store: Any
) -> None:
    """Warn once per root when a YAML backlog exists but work_items is empty.

    D-S3.6 drops FilesystemPMAdapter whenever SQLite is present, so a project
    whose backlog still lives in ``.raise/backlog/**.yaml`` would read an empty
    store with no explanation. Fail-quiet: any error here must not break
    adapter resolution.
    """
    try:
        root = project_root or Path.cwd()
        if str(root) in _unmigrated_warned:
            return
        backlog_dir = root / ".raise" / "backlog"
        if not backlog_dir.is_dir():
            return
        if not any(backlog_dir.rglob("*.yaml")):
            return
        if work_item_store(root).list_all():
            return
        _unmigrated_warned.add(str(root))
    except Exception:  # noqa: BLE001 — a warning must never break resolution
        return

    logger.warning(
        "Local backlog found in .raise/backlog/ but work_items is empty. "
        "Run 'rai backlog migrate' to import it (idempotent, keeps the files)."
    )


def resolve_pm_adapter(
    adapter_name: str | None,
    project_root: Path | None = None,
) -> ProjectManagementAdapter:
    """Resolve a ProjectManagementAdapter from entry points and YAML configs.

    Raises AdapterResolutionError if resolution fails.
    Pass adapter_name="all" to explicitly composite all configured adapters.

    Args:
        adapter_name: Adapter name or "all" for composite.
        project_root: Project root for config/manifest resolution.
    """
    if adapter_name == "all":
        return _wrap_with_graph_refresh(
            _compose_pm_adapters(_discover_pm_for(project_root), project_root),
            project_root,
        )

    if adapter_name is not None:
        entries = _discover_pm_for(project_root)
        adapter = _resolve_entrypoint(
            entries=entries,
            sync_wrapper=SyncPMAdapter,
            async_check_method="get_issue",
            group_label="PM adapter",
            selected=adapter_name,
            project_root=project_root,
        )
        return _wrap_with_graph_refresh(
            _wrap_with_ledger(adapter, project_root), project_root
        )

    entries = _discover_pm_for(project_root)

    if len(entries) == 0:
        raise AdapterResolutionError(
            "No PM adapter installed. Install one or register via entry points."
        )

    if len(entries) == 1:
        adapter = _resolve_entrypoint(
            entries=entries,
            sync_wrapper=SyncPMAdapter,
            async_check_method="get_issue",
            group_label="PM adapter",
            selected=None,
            project_root=project_root,
        )
        return _wrap_with_graph_refresh(
            _wrap_with_ledger(adapter, project_root), project_root
        )

    return _wrap_with_graph_refresh(
        _compose_pm_adapters(entries, project_root), project_root
    )


def build_docs_composite_for_gate(project_root: Path) -> DocumentationTarget:
    """Build a CompositeDocTarget for gate-layer use without CLI concerns.

    No console output, no sys.exit — raises AdapterResolutionError on failure.
    Used by gate-sync to discover a verifiable docs adapter.

    Architecture: S-AQG.4 (Q1a — gate must not import from cli.commands)
    """
    from raise_cli.adapters.composite_docs import CompositeDocTarget
    from raise_cli.adapters.filesystem_docs import FilesystemDocsTarget
    from raise_cli.adapters.pending_ops import PendingOpsLog

    entries = get_doc_targets()
    if not entries:
        raise AdapterResolutionError(
            "No docs target installed. Install one or register via entry points."
        )

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
        raise AdapterResolutionError("All docs targets failed to initialize.")

    # Consulta env vars + ~/.rai/server.json (vía get_server_credentials).
    # El código anterior solo leía env vars, ignorando rai connect → server.json.
    server_first = get_server_credentials() is not None
    pending_ops = PendingOpsLog(domain="docs", project_root=project_root)
    return CompositeDocTarget(
        instances,
        pending_ops=pending_ops,
        project_root=project_root,
        server_first=server_first,
    )
