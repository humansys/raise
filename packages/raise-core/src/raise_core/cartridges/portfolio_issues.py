"""Portfolio Issues cartridge generator (RAISE-15265 S1').

Pure synchronous generator: issues + profiles in, EpicNode/InitiativeNode cartridge on disk out.
No adapter, no asyncio, no raise_cli import. Data injected by the CLI; generator is a pure function.

Design: work/epics/e15265-portfolio-issues-cartridge/design.md (D1-D7, DA-1-DA-4).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Structural constants — must stay stable for schema_version hash invariant (D2).
_VALID_CHANGE_MODES: frozenset[str] = frozenset(
    {"breaking", "additive", "evolutionary"}
)
_NODE_TYPES: list[str] = ["epic", "initiative"]
_METADATA_KEYS: list[str] = sorted(
    [
        "cartridge",
        "change_mode",
        "components_touched",
        "jira_key",
        "jira_status",
        "level",
        "source",
        "summary",
    ]
)


# ── Node helpers ─────────────────────────────────────────────────────────────


def _node_type_for_issue(issue: Any) -> str:
    """Derive node type from issue.issue_type: 'Initiative' → 'initiative', else 'epic'."""
    return "initiative" if str(issue.issue_type).lower() == "initiative" else "epic"


def _profile_key(profile: Any) -> str:
    """Resolve canonical Jira key from EpicProfile (epic_key) or InitiativeProfile (initiative_key)."""
    return str(
        getattr(profile, "epic_key", None) or getattr(profile, "initiative_key", "")
    )


def _profile_node_type(profile: Any) -> str:
    return "epic" if hasattr(profile, "epic_key") else "initiative"


def _content(
    key: str, components: list[str], change_mode: str, status: str | None = None
) -> str:
    """D5: embed literal `components_touched:{c}` tokens so keyword search resolves."""
    parts = [f"key:{key}"]
    for c in components:
        parts.append(f"components_touched:{c}")
    if change_mode:
        parts.append(f"change_mode:{change_mode}")
    if status:
        parts.append(f"status:{status}")
    return " ".join(parts)


def _build_node(
    node_type: str,
    key: str,
    summary: str,
    components: list[str],
    change_mode: str,
    level: str,
    now: str,
    *,
    cartridge: str,
    jira_status: str | None = None,
    source: str = "jira",
) -> dict[str, Any]:
    return {
        "id": f"portfolio.{node_type}.{key}",
        "type": node_type,
        "content": _content(key, components, change_mode, status=jira_status),
        "source_file": None,
        "created": now,
        "updated_at": None,
        "metadata": {
            "cartridge": cartridge,
            "jira_key": key,
            "source": source,
            "components_touched": components,
            "change_mode": change_mode,
            "level": level,
            "jira_status": jira_status,
            "summary": summary,
        },
    }


def _structural_schema_version() -> str:
    """D2: hash structural shape only — node_types, metadata key sets, id/content schemes, vocab.

    Never hashes instance data (ids, statuses, components) so the hash is stable across
    any Jira status change or new epic added. Freshness is carried by valid_from (SCD-2).
    """
    schema_summary: dict[str, Any] = {
        "node_types": _NODE_TYPES,
        "metadata_keys": {
            "epic": _METADATA_KEYS,
            "initiative": _METADATA_KEYS,
        },
        "id_scheme": "portfolio.{type}.{KEY}",
        "content_scheme": "key:{KEY} components_touched:{c}... change_mode:{m} status:{s}",
        "change_mode_vocab": sorted(_VALID_CHANGE_MODES),
    }
    return hashlib.sha256(
        json.dumps(schema_summary, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


# ── Generator ────────────────────────────────────────────────────────────────


def generate_portfolio_issues_cartridge(
    issues: list[Any],
    profiles: list[Any],
    output_dir: Path,
    *,
    org_id: str,
    project_key: str,
    cartridge_name: str | None = None,
    base_nodes: Sequence[Mapping[str, Any]] | None = None,
) -> Path:
    """Generate the portfolio-issues cartridge from injected issues and profiles.

    Pure synchronous function — no adapter, no asyncio, no raise_cli import.
    Attributes read structurally from `issues` (key, summary, status, issue_type)
    and `profiles` (components_touched, change_mode, epic_key|initiative_key, level).

    Args:
        issues: List of IssueSummary-shaped objects from the CLI's adapter search.
        profiles: List of EpicProfile|InitiativeProfile from PortfolioStore.
        output_dir: Parent directory for cartridge output (e.g. `.raise/cartridges/`).
        org_id: Organisation identifier (e.g. "humansys").
        project_key: Jira project key (e.g. "RAISE").
        cartridge_name: Override the default `portfolio-issues-{org_id}-{project_key}` name.
        base_nodes: DA-1 delta seam — prior cartridge nodes for overlay merge.
            Must be None (full snapshot) in M0; non-None raises NotImplementedError
            until RAISE-15272 implements the overlay-merge branch.

    Returns:
        Path to the cartridge directory containing CARTRIDGE.yaml.
    """
    if base_nodes is not None:
        raise NotImplementedError(
            "Delta merge lands in RAISE-15272; pass base_nodes=None for a full snapshot"
        )

    now = datetime.now(UTC).isoformat()
    name = cartridge_name or f"portfolio-issues-{org_id}-{project_key}".lower()

    # D3: index profiles for O(1) lookup; local profile is authoritative for portfolio metadata
    by_key: dict[str, Any] = {_profile_key(p): p for p in profiles}
    covered: set[str] = set()
    nodes: list[dict[str, Any]] = []

    for issue in issues:
        profile = by_key.get(issue.key)
        components = list(getattr(profile, "components_touched", None) or [])
        change_mode = str(getattr(profile, "change_mode", "") or "")
        node_type = _node_type_for_issue(issue)
        level = str(getattr(profile, "level", node_type) or node_type)
        nodes.append(
            _build_node(
                node_type,
                issue.key,
                issue.summary,
                components,
                change_mode,
                level,
                now,
                cartridge=name,
                jira_status=issue.status,
                source="jira",
            )
        )
        if profile is not None:
            covered.add(issue.key)

    # D6: profile-only fallback — every profile key must materialize as a node
    for key, profile in by_key.items():
        if key in covered:
            continue
        nt = _profile_node_type(profile)
        nodes.append(
            _build_node(
                nt,
                key,
                summary="",
                components=list(getattr(profile, "components_touched", None) or []),
                change_mode=str(getattr(profile, "change_mode", "") or ""),
                level=str(getattr(profile, "level", nt) or nt),
                now=now,
                cartridge=name,
                jira_status=None,
                source="profile-only",
            )
        )

    schema_version = _structural_schema_version()
    # DA-1: fetch_mode derived from base_nodes (always "full" in M0)
    fetch_mode = "delta" if base_nodes is not None else "full"

    # ── Write cartridge ───────────────────────────────────────────────────────
    cartridge_dir = output_dir / name
    cartridge_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    (instances_dir / "model.json").write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    manifest: dict[str, Any] = {
        "name": name,
        "display_name": f"Portfolio Issues — {project_key}",
        "version": "1.0.0",
        "org_id": org_id,
        "project_id": project_key,
        "schema_version": schema_version,
        "valid_from": now,
        "superseded_at": None,
        "schema": {
            "module": "raise_core.graph.models",
            "class_name": "GraphNode",
        },
        "source": {
            "type": "derived",
            "authority": "remote",
            "generator": "raise_core.cartridges.portfolio_issues:generate_portfolio_issues_cartridge",
            "refresh": "signal",
        },
        # DA-2: provenance block — ignored by CartridgeManifest (pydantic v2 extra=ignore)
        "generation": {
            "fetch_mode": fetch_mode,
            "last_full_fetch_at": now,
            "last_fetch_at": now,
        },
    }
    (cartridge_dir / "CARTRIDGE.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )

    return cartridge_dir
