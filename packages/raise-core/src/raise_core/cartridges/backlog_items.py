"""Backlog Items cartridge generator (RAISE-16401 S16397.2).

Pure synchronous generator: backlog issues in, granular-type STATE nodes on disk
out. No adapter, no asyncio, no raise_cli import. Data injected by the caller
(CLI or refresh trigger); this module is a pure function.

Co-locates with the existing MODEL cartridge written by backlog_model.py in the
same `backlog-{org_id}-{project_key}` directory: this module never writes
`instances/model.json` and merge-preserves any existing `CARTRIDGE.yaml`
instead of overwriting it (ADR-111 split; see design D-S2.1).

Echo-loop safety (RAISE-13584 pattern): the backlog cartridge manifest carries
no `corpus` key, so no extraction pass ever scans this directory; discovery
scanning is language-glob driven and does not touch `.raise/cartridges/`.
`instances/items.json` is picked up only via `iter_instance_files()` node-list
ingestion. Do not add this cartridge directory as a scan target.

Design: work/stories/s16397.2/design.md (D-S2.1..D-S2.6).
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_METADATA_KEYS: list[str] = sorted(
    [
        "assignee",
        "cartridge",
        "custom_fields",
        "fix_versions",
        "issue_type",
        "key",
        "status",
        "labels",
        "parent",
        "priority",
        "status_category",
        "summary",
    ]
)


# ── Node helpers ─────────────────────────────────────────────────────────────


def _node_type_for_issue(issue: Any) -> str:
    """Derive the short node type from issue.issue_type.

    Returns the normalized type (e.g. "story", "research-item"); callers
    prefix with "backlog.".  Any issue_type is accepted — lowercased and
    spaces replaced with hyphens (RAISE-16727).
    """
    return str(issue.issue_type).lower().replace(" ", "-")


def _content(
    key: str,
    status: str,
    summary: str,
    *,
    issue_type: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    parent: str | None = None,
    assignee: str | None = None,
) -> str:
    """D5-style literal tokens so keyword search resolves rich fields (RAISE-16728)."""
    parts = [f"key:{key}", f"status:{status}"]
    if issue_type:
        parts.append(f"type:{issue_type}")
    if priority:
        parts.append(f"priority:{priority}")
    if labels:
        parts.append(f"labels:{','.join(labels)}")
    parts.append(f"summary:{summary}")
    if parent:
        parts.append(f"parent:{parent}")
    if assignee:
        parts.append(f"assignee:{assignee}")
    return " ".join(parts)


def build_backlog_item_node(
    issue: Any, *, cartridge_name: str, now: str | None = None
) -> dict[str, Any]:
    """Build a single backlog-item node dict from an issue-shaped object.

    Public — single source of truth for the node schema (epic §Key Contracts,
    design §4.2). Used both by ``generate_backlog_items_cartridge`` (full
    rebuild) and by ``GraphRefreshAdapter`` (single-node hot-path refresh,
    S16397.3). Never duplicate this schema elsewhere.

    Duck-types the parent/timestamp fields defensively: the real
    ``IssueDetail`` (from raise-cli's ``get_issue()``) carries ``parent_key``
    and ``updated``, NOT ``parent``/``updated_at`` — but this module's own
    fixtures (and any other issue-shaped object) may only carry the latter.
    Real-shape field names take precedence when both are present (S16397.3
    regression — PAT-E-954: adapter contract tests must validate the real
    I/O-boundary shape, not just a fixture shaped to match the code).

    Args:
        issue: Issue-shaped object (key, summary, status, issue_type
            required; parent_key/parent and updated/updated_at optional).
        cartridge_name: Cartridge directory name (stored in node metadata).
        now: ISO 8601 timestamp for the node's ``created`` field. Callers
            generating a full batch should compute this once and pass it
            through so every node in the batch shares one timestamp;
            defaults to the current time for single-node hot-path refreshes.

    Returns:
        Node dict ready for ``items.json`` (and ``GraphNode(**node)``).
    """
    short_type = _node_type_for_issue(issue)
    created = now if now is not None else datetime.now(UTC).isoformat()
    parent = getattr(issue, "parent_key", None) or getattr(issue, "parent", None)
    updated = getattr(issue, "updated", None) or getattr(issue, "updated_at", None)
    assignee = getattr(issue, "assignee", None)
    priority = getattr(issue, "priority", None)
    labels = getattr(issue, "labels", None) or []
    fix_versions = [str(v) for v in (getattr(issue, "fix_versions", None) or [])]
    status_category = str(getattr(issue, "status_category", "") or "")
    custom_fields = dict(getattr(issue, "metadata", None) or {})
    return {
        "id": f"backlog.{short_type}.{issue.key}",
        "type": f"backlog.{short_type}",
        "content": _content(
            issue.key,
            issue.status,
            issue.summary,
            issue_type=str(issue.issue_type),
            priority=str(priority) if priority else None,
            labels=[str(lbl) for lbl in labels] if labels else None,
            parent=parent,
            assignee=str(assignee) if assignee else None,
        ),
        "source_file": None,
        "created": created,
        "updated_at": updated,
        "metadata": {
            "cartridge": cartridge_name,
            "key": str(issue.key),
            "status": str(issue.status),
            "parent": parent,
            "summary": str(issue.summary),
            "issue_type": str(issue.issue_type),
            "assignee": str(assignee) if assignee else None,
            "priority": str(priority) if priority else None,
            "labels": [str(lbl) for lbl in labels] if labels else [],
            "fix_versions": fix_versions,
            "status_category": status_category,
            "custom_fields": custom_fields,
        },
    }


def _structural_schema_version() -> str:
    """D2: hash structural shape only — metadata key sets, id/content schemes.

    Node types are dynamic (RAISE-16727) so the hash captures structural
    contracts (metadata keys, id scheme, content scheme) but NOT the type
    vocabulary.  Never hashes instance data, so the hash is stable across
    any status change, summary edit, new issue, or new issue type.
    """
    schema_summary: dict[str, Any] = {
        "metadata_keys": _METADATA_KEYS,
        "id_scheme": "backlog.{type}.{KEY}",
        "content_scheme": "key:{KEY} status:{s} type:{t} priority:{p} labels:{l} summary:{summary} parent:{parent} assignee:{a}",
        "type_normalization": "lowercase-hyphenated",
    }
    return hashlib.sha256(
        json.dumps(schema_summary, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


# ── Manifest merge (D-S2.1) ─────────────────────────────────────────────────


def _write_manifest(
    cartridge_dir: Path,
    *,
    name: str,
    org_id: str,
    project_key: str,
    items_schema_version: str,
    now: str,
    incremental: bool = False,
) -> None:
    """Read-modify-write CARTRIDGE.yaml, preserving any existing MODEL keys.

    If the manifest already exists (normal case — MODEL cartridge generated
    first), every existing key is preserved untouched and only the two
    items-facet keys are set/replaced. If missing, a full manifest is written
    in the backlog_model shape (superseded later if backlog_model runs).

    When *incremental* is True, ``last_full_fetch_at`` is preserved from the
    existing manifest (RAISE-16444).
    """
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"

    old_generation: dict[str, Any] = {}
    if manifest_path.exists():
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        existing: dict[str, Any] = raw if isinstance(raw, dict) else {}
        gen = existing.get("generation")
        old_generation = gen if isinstance(gen, dict) else {}
    else:
        existing = {}

    if incremental:
        generation: dict[str, Any] = {
            "fetch_mode": "incremental",
            "last_full_fetch_at": old_generation.get("last_full_fetch_at", now),
            "last_fetch_at": now,
        }
    else:
        generation = {
            "fetch_mode": "full",
            "last_full_fetch_at": now,
            "last_fetch_at": now,
        }

    if existing:
        manifest: dict[str, Any] = existing
        manifest["items_schema_version"] = items_schema_version
        manifest["generation"] = generation
    else:
        manifest = {
            "name": name,
            "display_name": f"Backlog Items — {project_key}",
            "version": "1.0.0",
            "org_id": org_id,
            "project_id": project_key,
            "schema_version": items_schema_version,
            "valid_from": now,
            "superseded_at": None,
            "schema": {
                "module": "raise_core.graph.models",
                "class_name": "GraphNode",
            },
            "source": {
                "type": "derived",
                "authority": "remote",
                "generator": "raise_core.cartridges.backlog_items:generate_backlog_items_cartridge",
                "refresh": "signal",
            },
            "items_schema_version": items_schema_version,
            "generation": generation,
        }

    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


# ── Generator ────────────────────────────────────────────────────────────────


def generate_backlog_items_cartridge(
    issues: list[Any],
    output_dir: Path,
    *,
    org_id: str,
    project_key: str,
    cartridge_name: str | None = None,
    merge_existing: bool = False,
) -> Path:
    """Generate the backlog-items STATE facet from injected issues.

    Pure synchronous function — no adapter, no asyncio, no raise_cli import.
    Attributes read structurally from issues: key, summary, status,
    issue_type, parent (optional), updated_at (optional).

    Args:
        issues: List of issue-shaped objects (any object with key, summary,
            status, issue_type attributes; parent/updated_at optional).
        output_dir: Parent directory for cartridge output (e.g. `.raise/cartridges/`).
        org_id: Organisation identifier (e.g. "humansys").
        project_key: Jira project key (e.g. "RAISE").
        cartridge_name: Override the default `backlog-{org_id}-{project_key}` name
            — byte-identical to backlog_model.py's naming so both facets co-locate.
        merge_existing: When True, merge new nodes into existing items.json by id
            instead of replacing it (RAISE-16444 incremental sync).

    Returns:
        Path to the cartridge directory containing CARTRIDGE.yaml.
    """
    now = datetime.now(UTC).isoformat()
    name = cartridge_name or f"backlog-{org_id}-{project_key}".lower()

    new_nodes: list[dict[str, Any]] = [
        build_backlog_item_node(issue, cartridge_name=name, now=now) for issue in issues
    ]

    cartridge_dir = output_dir / name
    cartridge_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    items_path = instances_dir / "items.json"
    if merge_existing and items_path.exists():
        existing_nodes: list[dict[str, Any]] = json.loads(
            items_path.read_text(encoding="utf-8")
        )
        merged = {n["id"]: n for n in existing_nodes}
        for n in new_nodes:
            merged[n["id"]] = n
        nodes = list(merged.values())
    else:
        nodes = new_nodes

    items_path.write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    items_schema_version = _structural_schema_version()
    _write_manifest(
        cartridge_dir,
        name=name,
        org_id=org_id,
        project_key=project_key,
        items_schema_version=items_schema_version,
        now=now,
        incremental=merge_existing,
    )

    return cartridge_dir
