"""Onboarding DoctorChecks — server connectivity, graph state, cartridge sync.

Three checks that verify a developer has completed the RaiSE onboarding
journey: connected to a server, built the graph, and installed at least
one knowledge cartridge.

All checks require ``--online`` (``requires_online = True``) because they
need either network access or a populated local DB that only exists after
onboarding steps have run.

Architecture: S8916.4, RAISE-9884, ADR-045.
"""

from __future__ import annotations

import sqlite3
from typing import ClassVar

import httpx

from raise_cli.config.server import get_server_credentials
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.graph.backends.sqlite import SQLiteGraphBackend as SqliteGraphBackend
from raise_cli.storage.connection import get_project_db_path, get_project_id

_FIX_HINT_CONNECT = "run: rai connect"
_FIX_HINT_GRAPH_BUILD = "run: rai graph build"
_FIX_HINT_CARTRIDGE = "run: rai cartridge install raise-methodology"


class ServerConnectivityCheck(DoctorCheck):
    """Check that raise-server is configured and reachable.

    WARN (not ERROR) on failure — server being offline or misconfigured
    does not block local workflows.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "server-connectivity"
    category: ClassVar[str] = "onboarding"
    description: ClassVar[str] = "raise-server is configured and reachable"
    requires_online: ClassVar[bool] = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check server credentials exist and /health returns 200."""
        results: list[CheckResult] = []
        creds = get_server_credentials()
        if creds is None:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                "no server configured",
                _FIX_HINT_CONNECT,
            )
            return results

        server_url, api_key = creds
        try:
            response = httpx.get(
                f"{server_url}/health",
                timeout=5.0,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if response.status_code == 200:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.PASS,
                    f"server reachable at {server_url}",
                )
            else:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.WARN,
                    f"server returned HTTP {response.status_code} at {server_url}",
                    _FIX_HINT_CONNECT,
                )
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                str(exc),
                _FIX_HINT_CONNECT,
            )
        return results


class GraphStateCheck(DoctorCheck):
    """Check that the local knowledge graph has been built.

    Queries ``graph_nodes`` in the shared SQLite DB. A missing DB or zero
    rows means ``rai graph build`` has not been run.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "graph-state"
    category: ClassVar[str] = "onboarding"
    description: ClassVar[str] = "local knowledge graph has been built"
    requires_online: ClassVar[bool] = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check that graph_nodes table has rows for the current project."""
        results: list[CheckResult] = []
        db_path = get_project_db_path(context.working_dir)
        if not db_path.is_file():
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                "graph DB not found",
                _FIX_HINT_GRAPH_BUILD,
            )
            return results

        project_id = get_project_id(context.working_dir)
        try:
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            try:
                row = conn.execute(
                    "SELECT COUNT(*) FROM graph_nodes WHERE project_id = ?",
                    (project_id,),
                ).fetchone()
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                f"graph DB unreadable: {exc}",
                _FIX_HINT_GRAPH_BUILD,
            )
            return results

        count = row[0] if row else 0
        if count == 0:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                "graph empty — no nodes indexed for this project",
                _FIX_HINT_GRAPH_BUILD,
            )
        else:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.PASS,
                f"graph populated ({count} nodes)",
            )
        return results


class CartridgeSyncCheck(DoctorCheck):
    """Check that at least one knowledge cartridge is installed and enabled.

    Queries ``cartridge_installations`` via ``SqliteGraphBackend``. Zero
    enabled cartridges means ``rai cartridge install`` has not been run.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "cartridge-sync"
    category: ClassVar[str] = "onboarding"
    description: ClassVar[str] = "at least one knowledge cartridge is installed"
    requires_online: ClassVar[bool] = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check that >= 1 enabled cartridge exists."""
        results: list[CheckResult] = []
        db_path = get_project_db_path(context.working_dir)

        # Guard: SqliteGraphBackend._open() creates the file via sqlite3.connect()
        # if it does not exist, masking "graph not built" as "no cartridges installed".
        # Match GraphStateCheck — warn with the correct fix hint when DB is absent.
        if not db_path.is_file():
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                "graph DB not found — cartridge state unknown",
                _FIX_HINT_GRAPH_BUILD,
            )
            return results

        project_id = get_project_id(context.working_dir)
        try:
            backend = SqliteGraphBackend(project_id=project_id, db_path=db_path)
            installations = backend.list_cartridge_installations()
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                f"could not read cartridge installations: {exc}",
                _FIX_HINT_CARTRIDGE,
            )
            return results

        # Tuple index 2 is status per list_cartridge_installations() contract:
        # (name, source, status, node_count, installed_at, policy)
        enabled = [r for r in installations if r[2] == "enabled"]
        if not enabled:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                "no cartridges installed",
                _FIX_HINT_CARTRIDGE,
            )
        else:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.PASS,
                f"{len(enabled)} cartridge(s) enabled",
            )
        return results
