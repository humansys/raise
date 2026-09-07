"""Shared freshness core — RAISE-16049 (graph, RAISE-16998 (backlog mirror).

Evaluated by two consumers:

- ``doctor/checks/project.py`` — maps ``FreshnessReport`` /
  ``BacklogFreshnessReport`` onto the doctor ``CheckResult`` contract.
- ``session/open_service.py`` — maps both onto the session-open
  ``CheckResult`` contract, advisory only (never ``blocked``).

Checkout-scoped throughout (ADR-145 D7): graph freshness is evaluated against
THIS checkout's graph partition, not the repo-wide one.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from raise_cli.config.paths import checkout_scope_id
from raise_cli.project_config.manifest import (
    BacklogStalenessConfig,
    GraphStalenessConfig,
)

logger = logging.getLogger(__name__)

FreshnessTier = Literal["ok", "warn", "critical", "never_built"]


class FreshnessReport(BaseModel):
    """Result of evaluating graph freshness for a single checkout."""

    built_at: datetime | None
    age_days: int | None
    commits_behind: int | None  # None = git unavailable
    tier: FreshnessTier
    thresholds: GraphStalenessConfig


def load_staleness_thresholds(root: Path) -> GraphStalenessConfig:
    """Read ``graph.staleness`` from the manifest, defaults on any absence.

    Fail-open (RAISE-16049 design §1): a missing manifest, a missing/absent
    ``graph`` section, or malformed YAML/schema all collapse to
    ``GraphStalenessConfig()`` defaults — never raises.
    """
    from raise_cli.project_config.manifest import load_manifest

    manifest = load_manifest(root)
    if manifest is None or manifest.graph is None:
        return GraphStalenessConfig()
    return manifest.graph.staleness


def evaluate_graph_freshness(
    root: Path, thresholds: GraphStalenessConfig | None = None
) -> FreshnessReport:
    """Evaluate graph freshness for the checkout rooted at *root*.

    Tier logic uses ``>=`` boundary semantics (matching the pre-existing
    doctor checks):

    - ``built_at is None`` -> ``never_built``
    - ``critical`` if ``age_days >= critical_days`` OR
      ``commits_behind >= critical_commits``
    - ``warn`` if ``age_days >= warn_days`` OR ``commits_behind >= warn_commits``
    - else ``ok``

    ``commits_behind is None`` (git unavailable) evaluates on age alone.
    """
    resolved_thresholds = (
        thresholds if thresholds is not None else load_staleness_thresholds(root)
    )

    built_at = _read_built_at(root)
    if built_at is None:
        return FreshnessReport(
            built_at=None,
            age_days=None,
            commits_behind=None,
            tier="never_built",
            thresholds=resolved_thresholds,
        )

    age_days = (datetime.now(tz=UTC) - built_at).days
    commits_behind = _count_commits_since(root, built_at)

    tier = _compute_tier(age_days, commits_behind, resolved_thresholds)

    return FreshnessReport(
        built_at=built_at,
        age_days=age_days,
        commits_behind=commits_behind,
        tier=tier,
        thresholds=resolved_thresholds,
    )


def _compute_tier(
    age_days: int,
    commits_behind: int | None,
    thresholds: GraphStalenessConfig,
) -> FreshnessTier:
    is_critical = age_days >= thresholds.critical_days or (
        commits_behind is not None and commits_behind >= thresholds.critical_commits
    )
    if is_critical:
        return "critical"
    is_warn = age_days >= thresholds.warn_days or (
        commits_behind is not None and commits_behind >= thresholds.warn_commits
    )
    if is_warn:
        return "warn"
    return "ok"


def _read_built_at(root: Path) -> datetime | None:
    """Read last graph build timestamp FOR THIS CHECKOUT.

    Primary: SQLite MAX(updated_at) from graph_nodes.
    Fallback: graph_builds table MAX(built_at) — explicit build record.

    Both are scoped to ``checkout_id`` (RAISE-15607). Reading them repo-wide
    made doctor report a fresh graph off another worktree's build while the
    local partition was empty — a "fresh" verdict over no evidence at all.
    """
    ts = _read_built_at_sqlite(root)
    if ts is not None:
        return ts
    return _read_built_at_graph_builds(root)


def _read_built_at_sqlite(root: Path) -> datetime | None:
    """Read MAX(updated_at) from THIS checkout's graph_nodes partition."""
    import sqlite3

    from raise_cli.storage.connection import get_project_db_path, get_project_id

    try:
        db_path = get_project_db_path(root)
        if not db_path.is_file():
            return None
        project_id = get_project_id(root)
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT MAX(updated_at) FROM graph_nodes"
                " WHERE project_id = ? AND checkout_id = ?",
                (project_id, checkout_scope_id(root)),
            ).fetchone()
        finally:
            conn.close()
        if row is None or row[0] is None:
            return None
        return datetime.fromisoformat(row[0])
    except Exception:  # noqa: BLE001 — freshness checks must not crash
        return None


def _read_built_at_graph_builds(root: Path) -> datetime | None:
    """Fallback: MAX(built_at) from THIS checkout's graph_builds records."""
    import sqlite3

    from raise_cli.storage.connection import get_project_db_path, get_project_id

    try:
        project_id = get_project_id(root)
        db_path = get_project_db_path(root)
        if not db_path.is_file():
            return None
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT MAX(built_at) FROM graph_builds"
                " WHERE project_id = ? AND checkout_id = ?",
                (project_id, checkout_scope_id(root)),
            ).fetchone()
        finally:
            conn.close()
        if row is None or row[0] is None:
            return None
        return datetime.fromisoformat(row[0])
    except Exception:  # noqa: BLE001 — freshness checks must not crash
        return None


def _count_commits_since(root: Path, since: datetime) -> int | None:
    """Count commits since a given datetime. Returns None on git failure."""
    since_str = since.isoformat()
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"--since={since_str}", "HEAD"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, OSError, ValueError):
        logger.debug("Failed to count commits since %s", since_str)
        return None


# ---------------------------------------------------------------------------
# Backlog mirror freshness — RAISE-16998
# ---------------------------------------------------------------------------

BacklogFreshnessTier = Literal["ok", "stale", "never_synced"]


class BacklogFreshnessReport(BaseModel):
    """Result of evaluating backlog mirror freshness for a project root."""

    last_sync_at: datetime | None
    age_days: int | None
    tier: BacklogFreshnessTier
    thresholds: BacklogStalenessConfig


def load_backlog_staleness_thresholds(root: Path) -> BacklogStalenessConfig:
    """Read ``backlog.staleness`` from the manifest, defaults on any absence.

    Fail-open: a missing manifest, a missing/absent ``backlog`` section, or
    malformed YAML/schema all collapse to ``BacklogStalenessConfig()`` defaults.
    """
    from raise_cli.project_config.manifest import load_manifest

    manifest = load_manifest(root)
    if manifest is None or manifest.backlog is None:
        return BacklogStalenessConfig()
    return manifest.backlog.staleness


def evaluate_backlog_freshness(
    root: Path, thresholds: BacklogStalenessConfig | None = None
) -> BacklogFreshnessReport:
    """Evaluate backlog mirror freshness for the project rooted at *root*.

    Reads ``last_fetch_at`` from the most recent ``backlog-*/CARTRIDGE.yaml``
    under ``.raise/cartridges/``.  Tiers:

    - ``never_synced`` — no backlog cartridge or no ``last_fetch_at``
    - ``stale`` — ``age_days >= stale_days``
    - ``ok`` — synced within threshold
    """
    resolved = (
        thresholds
        if thresholds is not None
        else load_backlog_staleness_thresholds(root)
    )
    last_sync_at = _read_backlog_last_sync(root)

    if last_sync_at is None:
        return BacklogFreshnessReport(
            last_sync_at=None,
            age_days=None,
            tier="never_synced",
            thresholds=resolved,
        )

    age_days = (datetime.now(tz=UTC) - last_sync_at).days
    tier: BacklogFreshnessTier = "stale" if age_days >= resolved.stale_days else "ok"
    return BacklogFreshnessReport(
        last_sync_at=last_sync_at,
        age_days=age_days,
        tier=tier,
        thresholds=resolved,
    )


def _read_backlog_last_sync(root: Path) -> datetime | None:
    """Return the most recent ``last_fetch_at`` across all backlog cartridges.

    Globs ``.raise/cartridges/backlog-*/CARTRIDGE.yaml`` and picks the newest
    ``generation.last_fetch_at``.  Fails open — any read/parse error is
    silently skipped.
    """
    cartridges_dir = root / ".raise" / "cartridges"
    if not cartridges_dir.is_dir():
        return None

    best: datetime | None = None
    for manifest_path in cartridges_dir.glob("backlog-*/CARTRIDGE.yaml"):
        try:
            raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                continue
            generation = raw.get("generation")
            if not isinstance(generation, dict):
                continue
            wm = generation.get("last_fetch_at")
            if wm is None:
                continue
            ts = datetime.fromisoformat(str(wm))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            if best is None or ts > best:
                best = ts
        except Exception:  # noqa: BLE001, S112 — freshness checks must not crash
            logger.debug(
                "Failed to read backlog cartridge %s", manifest_path, exc_info=True
            )
            continue

    return best
