"""Backlog MODEL cartridge generator — discovers project schema via adapter (ADR-111).

Generates a MODEL cartridge (issue types, workflow states, custom fields) for a
Jira project. Follows the same output convention as repo.py:
  output_dir/<cartridge_name>/
      CARTRIDGE.yaml     — manifest with org_id, project_id, schema_version
      instances/
          model.json     — list of node-like dicts (backlog.issue_type, etc.)

SCD Type 2 semantics: valid_from is set at generation time, superseded_at stays
None (the current version on disk is always "active"). History is tracked by
raise-server, not in the YAML file.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import yaml


@runtime_checkable
class BacklogDiscoveryAdapter(Protocol):
    """Minimal discovery protocol satisfied by AsyncProjectManagementAdapter."""

    async def discover_issue_types(self, project_key: str) -> list[Any]:
        """Return issue types available for *project_key*."""
        ...

    async def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[Any]:
        """Return workflow states for *project_key* filtered by *issue_type*."""
        ...

    async def discover_fields(self, project_key: str) -> list[Any]:
        """Return all fields (system + custom) for the Jira instance."""
        ...

    async def discover_fields_for_issue_type(
        self, project_key: str, issue_type_name: str
    ) -> list[Any]:
        """Return fields with allowedValues for a specific issue type (S9939.1)."""
        ...


# ── Node builders ────────────────────────────────────────────────────────────


def _issue_type_node(it: Any, cartridge_name: str, now: str) -> dict[str, Any]:
    return {
        "id": f"backlog.issue_type.{it.id}",
        "type": "backlog.issue_type",
        "content": it.name,
        "source_file": None,
        "created": now,
        "updated_at": None,
        "metadata": {
            "cartridge": cartridge_name,
            "element_type": "issue_type",
            "issue_type_id": it.id,
            "is_subtask": it.subtask,
            "always_on": True,
        },
    }


def _workflow_state_node(ws: Any, cartridge_name: str, now: str) -> dict[str, Any]:
    return {
        "id": f"backlog.workflow_state.{ws.id}",
        "type": "backlog.workflow_state",
        "content": ws.name,
        "source_file": None,
        "created": now,
        "updated_at": None,
        "metadata": {
            "cartridge": cartridge_name,
            "element_type": "workflow_state",
            "status_id": ws.id,
            "status_category": ws.status_category,
            "always_on": True,
        },
    }


def _custom_field_node(
    field: Any,
    cartridge_name: str,
    now: str,
    *,
    belongs_to_issue_types: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": f"backlog.field.{field.id}",
        "type": "backlog.custom_field",
        "content": field.name,
        "source_file": None,
        "created": now,
        "updated_at": None,
        "metadata": {
            "cartridge": cartridge_name,
            "element_type": "custom_field",
            "field_id": field.id,
            "is_custom": field.custom,
            "allowed_values": getattr(field, "allowed_values", []),
            "schema_type": getattr(field, "schema_type", ""),
            "belongs_to_issue_types": sorted(belongs_to_issue_types or []),
        },
    }


async def _collect_field_enrichment(
    adapter: BacklogDiscoveryAdapter,
    project_key: str,
    issue_types: list[Any],
) -> tuple[dict[str, set[str]], dict[str, Any]]:
    """Collect per-issue-type field enrichment (allowed_values, schema_type).

    Returns (field_to_issue_types, enriched_fields) — both keyed by field.id.
    Best-effort: exceptions per issue type are swallowed silently.
    """
    field_to_issue_types: dict[str, set[str]] = {}
    enriched_fields: dict[str, Any] = {}
    for it in issue_types:
        try:
            it_fields = await adapter.discover_fields_for_issue_type(
                project_key, it.name
            )
            for f in it_fields:
                field_to_issue_types.setdefault(f.id, set()).add(it.name)
                if f.id not in enriched_fields:
                    enriched_fields[f.id] = f
        except Exception:  # noqa: S110
            pass
    return field_to_issue_types, enriched_fields


# ── Generator ────────────────────────────────────────────────────────────────


async def generate_backlog_model_cartridge(
    adapter: BacklogDiscoveryAdapter,
    project_key: str,
    output_dir: Path,
    *,
    org_id: str,
    cartridge_name: str | None = None,
) -> Path:
    """Discover and materialise the MODEL cartridge for *project_key*.

    Args:
        adapter: Adapter satisfying BacklogDiscoveryAdapter (e.g. JiraAdapter).
        project_key: Jira project key (e.g. "RAISE").
        output_dir: Parent directory for cartridge output (e.g. ``.raise/cartridges/``).
        org_id: Organisation identifier for multi-tenant boundary (e.g. "humansys").
        cartridge_name: Override the default ``backlog-{org_id}-{project_key}`` name.

    Returns:
        Path to the cartridge directory containing CARTRIDGE.yaml.
    """
    name = cartridge_name or f"backlog-{org_id}-{project_key}".lower()
    cartridge_dir = output_dir / name
    cartridge_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── Discover ──────────────────────────────────────────────────────────────
    issue_types = await adapter.discover_issue_types(project_key)

    seen_state_ids: set[str] = set()
    all_states: list[Any] = []
    for it in issue_types:
        try:
            states = await adapter.discover_statuses(project_key, issue_type=it.name)
            for ws in states:
                if ws.id not in seen_state_ids:
                    seen_state_ids.add(ws.id)
                    all_states.append(ws)
        except Exception:  # noqa: S110
            pass  # best-effort per issue type — don't fail the whole discovery

    all_fields = await adapter.discover_fields(project_key)
    custom_fields = [f for f in all_fields if f.custom]

    # ── Per-issue-type field enrichment (S9939.1) ─────────────────────────────
    field_to_issue_types, enriched_fields = await _collect_field_enrichment(
        adapter, project_key, issue_types
    )

    # ── Build nodes ───────────────────────────────────────────────────────────
    nodes: list[dict[str, Any]] = []
    for it in issue_types:
        nodes.append(_issue_type_node(it, name, now))
    for ws in all_states:
        nodes.append(_workflow_state_node(ws, name, now))
    for field in custom_fields:
        effective_field = enriched_fields.get(field.id, field)
        nodes.append(
            _custom_field_node(
                effective_field,
                name,
                now,
                belongs_to_issue_types=list(field_to_issue_types.get(field.id, set())),
            )
        )

    # schema_version includes allowed_values so option-list changes invalidate the hash
    schema_summary = {
        "issue_types": sorted(
            [
                {"id": n["metadata"]["issue_type_id"], "name": n["content"]}
                for n in nodes
                if n["type"] == "backlog.issue_type"
            ],
            key=lambda x: x["id"],
        ),
        "workflow_states": sorted(
            [
                {"id": n["metadata"]["status_id"], "name": n["content"]}
                for n in nodes
                if n["type"] == "backlog.workflow_state"
            ],
            key=lambda x: x["id"],
        ),
        "custom_fields": sorted(
            [
                {
                    "id": n["metadata"]["field_id"],
                    "name": n["content"],
                    "allowed_values": sorted(n["metadata"].get("allowed_values", [])),
                }
                for n in nodes
                if n["type"] == "backlog.custom_field"
            ],
            key=lambda x: x["id"],
        ),
    }
    schema_version = hashlib.sha256(
        json.dumps(schema_summary, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    # ── Write instances/model.json ────────────────────────────────────────────
    (instances_dir / "model.json").write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # ── Write CARTRIDGE.yaml (read-modify-write to preserve items-facet keys) ─
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    if manifest_path.exists():
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest: dict[str, Any] = raw if isinstance(raw, dict) else {}
    else:
        manifest = {}

    manifest.update(
        {
            "name": name,
            "display_name": f"Backlog Model — {project_key}",
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
                "generator": "raise_core.cartridges.backlog_model:generate_backlog_model_cartridge",
                "refresh": "signal",
            },
        }
    )
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )

    return cartridge_dir
