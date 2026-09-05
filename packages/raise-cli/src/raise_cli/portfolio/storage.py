"""Portfolio storage layer — Layer 0 (component catalog) + Layer 1 (initiative profiles).

Design: design.md D1/D3 (RAISE-15198 e15198-portfolio-impact-model).
Schema: storage/schema.py _apply_v61 (portfolio_components, initiative_profiles, portfolio_deps).

~/.rai/raise.db is shared across projects; every query is scoped by project_id
obtained via get_project_id(). Never re-derive project_id inside queries — use
the cached self._project_id set at __init__ time.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all

_DEFAULT_COMPONENTS: list[dict[str, str]] = [
    {
        "id": "storage",
        "name": "Storage Layer",
        "domain": "infrastructure",
        "description": "SQLite schema + migration",
        "layer": "L0",
    },
    {
        "id": "graph",
        "name": "Graph Backend",
        "domain": "knowledge",
        "description": "Graph nodes/edges + cartridge retrieval",
        "layer": "L0",
    },
    {
        "id": "pipeline",
        "name": "Pipeline Engine",
        "domain": "orchestration",
        "description": "Skill dispatch + phase lifecycle",
        "layer": "L1",
    },
    {
        "id": "backlog",
        "name": "Backlog Adapter",
        "domain": "integration",
        "description": "Jira adapter + transition ownership",
        "layer": "L1",
    },
    {
        "id": "hooks",
        "name": "Hooks System",
        "domain": "orchestration",
        "description": "Event hooks + gate bridge",
        "layer": "L1",
    },
    {
        "id": "skills",
        "name": "Skills Runtime",
        "domain": "execution",
        "description": "SKILL.md execution + lean residues",
        "layer": "L1",
    },
    {
        "id": "gates",
        "name": "Gate System",
        "domain": "governance",
        "description": "Gate checks + portfolio gates",
        "layer": "L2",
    },
    {
        "id": "portfolio",
        "name": "Portfolio Model",
        "domain": "governance",
        "description": "Component catalog + initiative profiles + dependency graph",
        "layer": "L2",
    },
    {
        "id": "sessions",
        "name": "Session Management",
        "domain": "orchestration",
        "description": "Session lifecycle + context bundle",
        "layer": "L1",
    },
    {
        "id": "worktrees",
        "name": "Worktree Management",
        "domain": "infrastructure",
        "description": "Worktree registry + lease enforcement",
        "layer": "L0",
    },
]

# M0 initiative trio — characterized 2026-07-17 for e15198 dogfood
# Extended 2026-07-21 with full 15-initiative seed (optimal repo state)
_M0_INITIATIVE_PROFILES: list[dict[str, object]] = [
    {
        "initiative_key": "RAISE-15025",
        "components_touched": ["pipeline", "backlog", "hooks", "skills"],
        "change_mode": "breaking",
        "contracts_affected": ["skill-transition-contract", "pipeline-phase-contract"],
        "rationale": (
            "Ownership Flip Enforcement: removes direct skill-owned Jira transitions; "
            "pipeline engine now exclusively owns state changes via target_status/transition_mode. "
            "Breaking because all ~28 SKILL.md files that called rai backlog transition must be updated."
        ),
        "created_at": "2026-07-17T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-15165",
        "components_touched": ["portfolio", "storage", "gates"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Portfolio Impact Model: new capability (Layer 0/1/2 + BeforeReadyGate). "
            "New SQLite tables, new portfolio/ module, new gate. No existing contracts changed."
        ),
        "created_at": "2026-07-17T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-14052",
        "components_touched": ["graph", "pipeline", "storage", "backlog"],
        "change_mode": "evolutionary",
        "contracts_affected": [
            "cartridge-extraction-contract",
            "graph-cartridge-schema",
        ],
        "rationale": (
            "Knowledge Cartridge Platform & Marketplace: extends cartridge infrastructure "
            "with marketplace UX, federation, FalkorDB runtime, domain cartridges. "
            "Evolutionary because existing cartridge clients are unaffected; new surfaces added."
        ),
        "created_at": "2026-07-17T00:00:00Z",
    },
    # -- Active initiatives added 2026-07-21 --
    {
        "initiative_key": "RAISE-14674",
        "components_touched": ["sessions", "worktrees", "pipeline"],
        "change_mode": "evolutionary",
        "contracts_affected": [],
        "rationale": (
            "Agent Runtime & Workspace Integrity: workspace cockpit TUI, fleet API, session ledger, "
            "worktree lease enforcement. Evolutionary — extends existing session/worktree contracts "
            "without breaking them."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-14676",
        "components_touched": ["pipeline", "skills", "storage"],
        "change_mode": "evolutionary",
        "contracts_affected": [],
        "rationale": (
            "Delivery & Deploy Reliability: broken-windows remediation, release gates, "
            "reliability scoring, CI hardening. Evolutionary — hardens existing contracts "
            "without adding new surfaces."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-13994",
        "components_touched": ["storage", "backlog", "sessions"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Self-Serve Monetization: raise-admin console, trial provisioning, partner channel, "
            "Stripe billing. Additive — new billing/tenant surfaces, no existing component "
            "contracts changed."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-14566",
        "components_touched": ["sessions", "worktrees", "pipeline"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "SMB / Rai Agent: BYOR daemon, SMB workspace persistence, hosted agent SaaS. "
            "Additive — new local-daemon capability, no existing pipeline/session contracts broken."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-13075",
        "components_touched": ["skills", "pipeline", "sessions"],
        "change_mode": "evolutionary",
        "contracts_affected": ["skill-transition-contract"],
        "rationale": (
            "RaiSE Framework & Planning Methodology: ADR-143 lean pipeline canonical, skill audit, "
            "ShuHaRi developer levels, planning YAML. Evolutionary — refines skill and pipeline "
            "contracts in-place via ADRs."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-14049",
        "components_touched": ["storage", "sessions", "backlog"],
        "change_mode": "breaking",
        "contracts_affected": ["mission-session-contract"],
        "rationale": (
            "Missions & Initiatives como Entidades de Backlog: ADR-130 mission elimination, "
            "mission→initiative rename, Jira entity lifecycle enforcement. Breaking because "
            "mission-keyed storage rows require migration and CLI renames."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-14714",
        "components_touched": ["sessions", "graph", "pipeline"],
        "change_mode": "evolutionary",
        "contracts_affected": [],
        "rationale": (
            "Observación y Reingeniería Unificada: framework reengineering program, event-log "
            "spine, two-velocity model (fast-path / governed-path). Evolutionary — restructures "
            "internals but preserves CLI UX contracts."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-12692",
        "components_touched": ["backlog", "sessions", "worktrees"],
        "change_mode": "evolutionary",
        "contracts_affected": [],
        "rationale": (
            "Work Management: GitLab SCM adapter, notifications, onboarding forge migration. "
            "Evolutionary — extends backlog integration surface without breaking Jira adapter contracts."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-15274",
        "components_touched": ["sessions", "graph"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Session Intelligence: transcript signal extraction, process measurement from sessions. "
            "Additive — new analysis capability on top of existing session and graph contracts."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-10842",
        "components_touched": ["storage"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Migración Infraestructura GCP: QA+prod environment migration Fly.io→GCP. "
            "Additive — infra layer change only; raise-cli gains new DB connection options for GCP."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-15289",
        "components_touched": ["graph", "pipeline"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Raishin Piloto Concierge Canal-first (I-1): marketplace concierge surface. "
            "Additive — Raishin product scope; raise-cli is infrastructure supplier (graph + pipeline)."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
    {
        "initiative_key": "RAISE-15290",
        "components_touched": ["graph", "pipeline"],
        "change_mode": "additive",
        "contracts_affected": [],
        "rationale": (
            "Raishin Web MVP + SaaS Billing (I-2): Raishin marketplace web + billing. "
            "Additive — Raishin product scope; raise-cli provides graph/pipeline infrastructure."
        ),
        "created_at": "2026-07-21T00:00:00Z",
    },
]

VALID_CHANGE_MODES: frozenset[str] = frozenset({"breaking", "additive", "evolutionary"})


class PortfolioComponent(BaseModel):
    """A platform component entry in the catalog (Layer 0)."""

    project_id: str
    id: str
    name: str
    domain: str
    description: str = ""
    layer: str = ""


class InitiativeProfile(BaseModel):
    """An initiative's characterization: components touched, change mode, contracts (Layer 1)."""

    project_id: str
    initiative_key: str
    components_touched: list[str] = []
    change_mode: str = ""
    contracts_affected: list[str] = []
    rationale: str = ""
    created_at: str = ""


class EpicProfile(BaseModel):
    """An epic's planning-time characterization: components touched and change mode."""

    project_id: str
    epic_key: str
    level: str = "epic"
    components_touched: list[str] = []
    change_mode: str = ""
    created_at: str = ""


class PortfolioDep(BaseModel):
    """A confirmed or declared dependency edge between initiatives/components (Layer 2)."""

    project_id: str
    source: str
    target: str
    type: str  # requires | enables | conflicts | supersedes
    rationale: str = ""
    confirmed_by: str = ""
    confirmed_at: str = ""


def _row_to_component(row: sqlite3.Row) -> PortfolioComponent:
    d: dict[str, object] = dict(row)
    return PortfolioComponent(
        project_id=str(d["project_id"]),
        id=str(d["id"]),
        name=str(d["name"]),
        domain=str(d["domain"]),
        description=str(d.get("description") or ""),
        layer=str(d.get("layer") or ""),
    )


def _row_to_profile(row: sqlite3.Row) -> InitiativeProfile:
    d: dict[str, object] = dict(row)
    components_touched: list[str] = json.loads(str(d.get("components_touched") or "[]"))
    contracts_affected: list[str] = json.loads(str(d.get("contracts_affected") or "[]"))
    return InitiativeProfile(
        project_id=str(d["project_id"]),
        initiative_key=str(d["initiative_key"]),
        components_touched=components_touched,
        change_mode=str(d.get("change_mode") or ""),
        contracts_affected=contracts_affected,
        rationale=str(d.get("rationale") or ""),
        created_at=str(d.get("created_at") or ""),
    )


def _row_to_epic_profile(row: sqlite3.Row) -> EpicProfile:
    d: dict[str, object] = dict(row)
    components_touched: list[str] = json.loads(str(d.get("components_touched") or "[]"))
    return EpicProfile(
        project_id=str(d["project_id"]),
        epic_key=str(d["epic_key"]),
        level=str(d.get("level") or "epic"),
        components_touched=components_touched,
        change_mode=str(d.get("change_mode") or ""),
        created_at=str(d.get("created_at") or ""),
    )


def _row_to_dep(row: sqlite3.Row) -> PortfolioDep:
    d: dict[str, object] = dict(row)
    return PortfolioDep(
        project_id=str(d["project_id"]),
        source=str(d["source"]),
        target=str(d["target"]),
        type=str(d["type"]),
        rationale=str(d.get("rationale") or ""),
        confirmed_by=str(d.get("confirmed_by") or ""),
        confirmed_at=str(d.get("confirmed_at") or ""),
    )


class PortfolioStore:
    """CRUD access to portfolio_components and initiative_profiles.

    All queries are scoped by project_id (get_project_id at __init__ time).
    portfolio_deps table is created by schema v61 but populated in S2.
    """

    def __init__(self, project: Path) -> None:
        self._project = project
        self._project_id = get_project_id(project)
        self._conn = get_project_db(project)
        self._conn.row_factory = sqlite3.Row
        create_all(self._conn)

    # ------------------------------------------------------------------
    # Layer 0 — Component Catalog
    # ------------------------------------------------------------------

    def create_component(
        self,
        id: str,
        name: str,
        domain: str,
        description: str = "",
        layer: str = "",
    ) -> PortfolioComponent:
        """Insert a component; silently ignores duplicate (project_id, id)."""
        self._conn.execute(
            "INSERT OR IGNORE INTO portfolio_components"
            " (project_id, id, name, domain, description, layer)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (self._project_id, id, name, domain, description, layer),
        )
        self._conn.commit()
        return PortfolioComponent(
            project_id=self._project_id,
            id=id,
            name=name,
            domain=domain,
            description=description,
            layer=layer,
        )

    def get_component(self, id: str) -> PortfolioComponent | None:
        """Return component by id scoped to this project, or None."""
        row = self._conn.execute(
            "SELECT * FROM portfolio_components WHERE project_id = ? AND id = ?",
            (self._project_id, id),
        ).fetchone()
        return _row_to_component(row) if row is not None else None

    def list_components(self) -> list[PortfolioComponent]:
        """Return all components for this project."""
        rows = self._conn.execute(
            "SELECT * FROM portfolio_components WHERE project_id = ? ORDER BY id",
            (self._project_id,),
        ).fetchall()
        return [_row_to_component(r) for r in rows]

    def sync_manifest_catalog(self, component_paths: dict[str, list[str]]) -> int:
        """Upsert manifest component_paths keys into portfolio_components. Idempotent.

        Each key in component_paths becomes a row with id=name=key; domain/description/layer
        are left empty (manifest carries path prefixes, not rich metadata). Returns the count
        of components synced. Skips silently when component_paths is empty.
        """
        if not component_paths:
            return 0
        for name in component_paths:
            self._conn.execute(
                "INSERT OR IGNORE INTO portfolio_components"
                " (project_id, id, name, domain, description, layer)"
                " VALUES (?, ?, ?, '', '', '')",
                (self._project_id, name, name),
            )
        self._conn.commit()
        return len(component_paths)

    def get_valid_component_names(self) -> frozenset[str]:
        """Return the set of valid component ids for this project (empty = no catalog)."""
        rows = self._conn.execute(
            "SELECT id FROM portfolio_components WHERE project_id = ?",
            (self._project_id,),
        ).fetchall()
        return frozenset(r[0] for r in rows)

    def seed_default_components(self) -> None:
        """Seed the default RaiSE platform component catalog. Idempotent."""
        for comp in _DEFAULT_COMPONENTS:
            self._conn.execute(
                "INSERT OR IGNORE INTO portfolio_components"
                " (project_id, id, name, domain, description, layer)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    self._project_id,
                    comp["id"],
                    comp["name"],
                    comp["domain"],
                    comp["description"],
                    comp["layer"],
                ),
            )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Layer 1 — Initiative Profiles
    # ------------------------------------------------------------------

    def create_initiative_profile(
        self,
        initiative_key: str,
        components_touched: list[str],
        change_mode: str,
        contracts_affected: list[str],
        rationale: str,
        created_at: str = "",
    ) -> InitiativeProfile:
        """Insert or replace an initiative profile."""
        if change_mode not in VALID_CHANGE_MODES:
            raise ValueError(
                f"change_mode must be one of {sorted(VALID_CHANGE_MODES)}, got {change_mode!r}"
            )
        self._conn.execute(
            "INSERT OR REPLACE INTO initiative_profiles"
            " (project_id, initiative_key, components_touched, change_mode,"
            "  contracts_affected, rationale, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self._project_id,
                initiative_key,
                json.dumps(components_touched),
                change_mode,
                json.dumps(contracts_affected),
                rationale,
                created_at,
            ),
        )
        self._conn.commit()
        return InitiativeProfile(
            project_id=self._project_id,
            initiative_key=initiative_key,
            components_touched=components_touched,
            change_mode=change_mode,
            contracts_affected=contracts_affected,
            rationale=rationale,
            created_at=created_at,
        )

    def get_initiative_profile(self, initiative_key: str) -> InitiativeProfile | None:
        """Return initiative profile by key scoped to this project, or None."""
        row = self._conn.execute(
            "SELECT * FROM initiative_profiles"
            " WHERE project_id = ? AND initiative_key = ?",
            (self._project_id, initiative_key),
        ).fetchone()
        return _row_to_profile(row) if row is not None else None

    def list_initiative_profiles(self) -> list[InitiativeProfile]:
        """Return all initiative profiles for this project."""
        rows = self._conn.execute(
            "SELECT * FROM initiative_profiles WHERE project_id = ? ORDER BY initiative_key",
            (self._project_id,),
        ).fetchall()
        return [_row_to_profile(r) for r in rows]

    def seed_m0_initiative_profiles(self) -> None:
        """Seed the 3 M0 initiative profiles (breaking/additive/evolutionary). Idempotent."""
        for entry in _M0_INITIATIVE_PROFILES:
            self._conn.execute(
                "INSERT OR IGNORE INTO initiative_profiles"
                " (project_id, initiative_key, components_touched, change_mode,"
                "  contracts_affected, rationale, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    self._project_id,
                    str(entry["initiative_key"]),
                    json.dumps(entry["components_touched"]),
                    str(entry["change_mode"]),
                    json.dumps(entry["contracts_affected"]),
                    str(entry["rationale"]),
                    str(entry["created_at"]),
                ),
            )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Layer 1b — Epic Profiles (planning-time capture)
    # ------------------------------------------------------------------

    def create_epic_profile(
        self,
        epic_key: str,
        components_touched: list[str],
        change_mode: str,
        level: str = "epic",
        created_at: str = "",
    ) -> EpicProfile:
        """Insert or replace an epic profile."""
        if change_mode not in VALID_CHANGE_MODES:
            raise ValueError(
                f"change_mode must be one of {sorted(VALID_CHANGE_MODES)}, got {change_mode!r}"
            )
        self._conn.execute(
            "INSERT OR REPLACE INTO epic_profiles"
            " (project_id, epic_key, level, components_touched, change_mode, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                self._project_id,
                epic_key,
                level,
                json.dumps(components_touched),
                change_mode,
                created_at,
            ),
        )
        self._conn.commit()
        return EpicProfile(
            project_id=self._project_id,
            epic_key=epic_key,
            level=level,
            components_touched=components_touched,
            change_mode=change_mode,
            created_at=created_at,
        )

    def get_epic_profile(self, epic_key: str) -> EpicProfile | None:
        """Return epic profile by key scoped to this project, or None."""
        row = self._conn.execute(
            "SELECT * FROM epic_profiles WHERE project_id = ? AND epic_key = ?",
            (self._project_id, epic_key),
        ).fetchone()
        return _row_to_epic_profile(row) if row is not None else None

    def list_epic_profiles(self) -> list[EpicProfile]:
        """Return all epic profiles for this project."""
        rows = self._conn.execute(
            "SELECT * FROM epic_profiles WHERE project_id = ? ORDER BY epic_key",
            (self._project_id,),
        ).fetchall()
        return [_row_to_epic_profile(r) for r in rows]

    # ------------------------------------------------------------------
    # Layer 2 — Confirmed/Declared Dependency Edges
    # ------------------------------------------------------------------

    _PROMOTE_TYPES = ("requires", "conflicts")
    _DECLARE_TYPES = ("enables", "supersedes")

    def _upsert_dep(
        self,
        source: str,
        target: str,
        edge_type: str,
        rationale: str,
        confirmed_by: str,
        confirmed_at: str,
    ) -> PortfolioDep:
        self._conn.execute(
            "INSERT OR REPLACE INTO portfolio_deps"
            " (project_id, source, target, type, rationale, confirmed_by, confirmed_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self._project_id,
                source,
                target,
                edge_type,
                rationale,
                confirmed_by,
                confirmed_at,
            ),
        )
        self._conn.commit()
        return PortfolioDep(
            project_id=self._project_id,
            source=source,
            target=target,
            type=edge_type,
            rationale=rationale,
            confirmed_by=confirmed_by,
            confirmed_at=confirmed_at,
        )

    def promote_to_confirmed(
        self,
        source: str,
        target: str,
        edge_type: str,
        rationale: str,
        confirmed_by: str = "",
        confirmed_at: str = "",
    ) -> PortfolioDep:
        """Promote an advisory edge to a confirmed edge (requires | conflicts).

        Requires a non-empty rationale — human judgment is what distinguishes
        a confirmed edge from a derived advisory one.
        """
        if not rationale:
            raise ValueError("promote_to_confirmed requires a non-empty rationale")
        if edge_type not in self._PROMOTE_TYPES:
            raise ValueError(
                f"promote_to_confirmed edge_type must be one of {self._PROMOTE_TYPES},"
                f" got {edge_type!r}"
            )
        return self._upsert_dep(
            source, target, edge_type, rationale, confirmed_by, confirmed_at
        )

    def declare_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        rationale: str,
        confirmed_by: str = "",
        confirmed_at: str = "",
    ) -> PortfolioDep:
        """Declare a human-asserted edge (enables | supersedes).

        Requires a non-empty rationale.
        """
        if not rationale:
            raise ValueError("declare_edge requires a non-empty rationale")
        if edge_type not in self._DECLARE_TYPES:
            raise ValueError(
                f"declare_edge edge_type must be one of {self._DECLARE_TYPES},"
                f" got {edge_type!r}"
            )
        return self._upsert_dep(
            source, target, edge_type, rationale, confirmed_by, confirmed_at
        )

    def get_dep(self, source: str, target: str, edge_type: str) -> PortfolioDep | None:
        """Return a dependency edge by (source, target, type) scoped to this project."""
        row = self._conn.execute(
            "SELECT * FROM portfolio_deps"
            " WHERE project_id = ? AND source = ? AND target = ? AND type = ?",
            (self._project_id, source, target, edge_type),
        ).fetchone()
        return _row_to_dep(row) if row is not None else None

    def list_deps(self) -> list[PortfolioDep]:
        """Return all confirmed/declared dependency edges for this project."""
        rows = self._conn.execute(
            "SELECT * FROM portfolio_deps WHERE project_id = ? ORDER BY source, target, type",
            (self._project_id,),
        ).fetchall()
        return [_row_to_dep(r) for r in rows]

    def list_deps_for(self, source: str) -> list[PortfolioDep]:
        """Return dependency edges where source matches, scoped to this project."""
        rows = self._conn.execute(
            "SELECT * FROM portfolio_deps"
            " WHERE project_id = ? AND source = ? ORDER BY target, type",
            (self._project_id, source),
        ).fetchall()
        return [_row_to_dep(r) for r in rows]
