"""Session catalog — runtime session discovery and management.

Provides ``SessionCatalog`` for querying active harness sessions across
``CatalogSource`` backends. The local backend (``LocalCatalogSource``) reads
from the ``runtime_sessions`` SQLite table (v70 schema).

Public surface:
    SessionCatalog, LocalCatalogSource, RuntimeSessionRecord,
    CatalogFilter, SessionState, WorktreeScope, ProjectScope, HostScope,
    create_runtime_session, bind_governance_session_id, read_runtime_session_id
"""

from __future__ import annotations

from raise_cli.session.catalog.alias import AliasExhaustedError, generate_alias
from raise_cli.session.catalog.catalog import SessionCatalog
from raise_cli.session.catalog.models import (
    CatalogFilter,
    RuntimeSessionRecord,
    SessionState,
)
from raise_cli.session.catalog.reconcile import (
    PROVISIONING_TIMEOUT_S,
    ReconcileResult,
    reconcile,
)
from raise_cli.session.catalog.runtime import (
    RAI_RUNTIME_SESSION_ID,
    bind_governance_session_id,
    create_runtime_session,
    read_runtime_session_id,
)
from raise_cli.session.catalog.scope import HostScope, ProjectScope, WorktreeScope
from raise_cli.session.catalog.source import LocalCatalogSource

__all__ = [
    "AliasExhaustedError",
    "CatalogFilter",
    "HostScope",
    "LocalCatalogSource",
    "PROVISIONING_TIMEOUT_S",
    "ProjectScope",
    "RAI_RUNTIME_SESSION_ID",
    "ReconcileResult",
    "RuntimeSessionRecord",
    "SessionCatalog",
    "SessionState",
    "WorktreeScope",
    "bind_governance_session_id",
    "create_runtime_session",
    "generate_alias",
    "read_runtime_session_id",
    "reconcile",
]
