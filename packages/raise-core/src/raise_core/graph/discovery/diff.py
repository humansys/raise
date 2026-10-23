"""Schema and node diff/reconcile functions.

Pure data comparison — no LLM dependencies.
Migrated from rai-agent in S2674.6.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

import yaml

from raise_core.graph.discovery.models import (
    DecisionDiff,
    FieldDiff,
    NodeDiffReport,
    ReconcileReport,
    SchemaDiffReport,
    SchemaSpec,
)

logger = logging.getLogger(__name__)


def diff_schemas(
    discovered: SchemaSpec,
    reference_model: Any,
) -> SchemaDiffReport:
    """Compare a discovered SchemaSpec against a reference model's structure.

    The reference_model should have:
    - _node_types: list[str] — known node type names
    - _fields: dict[str, list[str]] — per-type field lists
    """
    ref_types: list[str] = getattr(reference_model, "_node_types", [])
    ref_fields: dict[str, list[str]] = getattr(reference_model, "_fields", {})

    disc_type_names = {nt.name for nt in discovered.node_types}
    ref_type_names = set(ref_types)

    types_both = sorted(disc_type_names & ref_type_names)
    types_only_disc = sorted(disc_type_names - ref_type_names)
    types_only_ref = sorted(ref_type_names - disc_type_names)

    field_diffs: dict[str, FieldDiff] = {}
    for type_name in types_both:
        disc_node = next(nt for nt in discovered.node_types if nt.name == type_name)
        disc_fields = set(disc_node.fields)
        r_fields = set(ref_fields.get(type_name, []))

        field_diffs[type_name] = FieldDiff(
            common=sorted(disc_fields & r_fields),
            only_discovered=sorted(disc_fields - r_fields),
            only_reference=sorted(r_fields - disc_fields),
        )

    return SchemaDiffReport(
        types_both=types_both,
        types_only_discovered=types_only_disc,
        types_only_reference=types_only_ref,
        field_diffs=field_diffs,
    )


def _fuzzy_find_id(target: str, existing_ids: set[str]) -> str | None:
    """Find closest match for a broken target ID."""
    candidates = [
        eid for eid in existing_ids if eid.startswith(target) or target.startswith(eid)
    ]
    if len(candidates) == 1:
        return candidates[0]

    parts = target.split("-", 1)
    if len(parts) == 2:
        suffix = parts[1]
        candidates = [eid for eid in existing_ids if suffix in eid]
        if len(candidates) == 1:
            return candidates[0]

    return None


def _load_node_ids_from_dir(directory: Path) -> dict[str, dict[str, Any]]:
    """Load YAML nodes from a directory (recursively), keyed by 'id' field."""
    nodes: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.rglob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text())
            if isinstance(raw, dict) and "id" in raw:
                nodes[raw["id"]] = raw
        except (yaml.YAMLError, OSError):
            logger.warning("Skipping unreadable YAML %s", path.name)
            continue
    return nodes


def reconcile_extracted(  # noqa: C901
    extracted_dir: Path,
    domain_config: dict[str, Any],  # noqa: ARG001 — preserved for API compat
) -> ReconcileReport:
    """Auto-fix mechanical issues in extracted nodes.

    1. Create missing decision-area nodes (decision-people, etc.)
    2. Fuzzy-match broken refs to existing node IDs
    3. Remove refs that still can't be resolved

    Modifies YAML files in-place. Run after extraction, before curation.
    """
    nodes = _load_node_ids_from_dir(extracted_dir)
    all_ids = set(nodes.keys())
    report = ReconcileReport()

    decision_areas = {"people", "strategy", "execution", "cash"}
    for area in sorted(decision_areas):
        node_id = f"decision-{area}"
        if node_id not in all_ids:
            node_data = {
                "id": node_id,
                "type": "decision",
                "name": f"{area.title()} Decision",
                "name_es": f"Decisión de {area.title()}",
                "decision": area,
                "summary": f"The {area} decision area in Scaling Up — one of the four key decisions every growing company must get right.",
                "difficulty": "beginner",
                "relationships": [],
                "tags": [area, "decision-area", "scaling-up"],
            }
            path = extracted_dir / f"{node_id}.yaml"
            path.write_text(
                yaml.dump(
                    node_data,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            )
            all_ids.add(node_id)
            report.nodes_created.append(node_id)
            logger.info("Created missing decision node: %s", node_id)

    broken_before = 0
    resolved = 0
    removed = 0

    for path in sorted(extracted_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        if not isinstance(raw, dict) or "relationships" not in raw:
            continue

        modified = False
        new_rels: list[dict[str, str]] = []
        rels = cast("list[dict[str, str]]", raw["relationships"])
        for rel in rels:
            if "target" not in rel:
                new_rels.append(rel)
                continue

            target: str = rel["target"]
            if target in all_ids:
                new_rels.append(rel)
                continue

            broken_before += 1

            match = _fuzzy_find_id(target, all_ids)
            if match:
                rel["target"] = match
                new_rels.append(rel)
                resolved += 1
                modified = True
            else:
                removed += 1
                modified = True

        if modified:
            raw["relationships"] = new_rels
            path.write_text(
                yaml.dump(
                    raw, default_flow_style=False, allow_unicode=True, sort_keys=False
                )
            )

    nodes_after = _load_node_ids_from_dir(extracted_dir)
    all_ids_after = set(nodes_after.keys())
    broken_after = 0
    for node_data in nodes_after.values():
        for rel in node_data.get("relationships", []):
            if isinstance(rel, dict) and rel.get("target") not in all_ids_after:
                broken_after += 1

    report.refs_resolved = resolved
    report.refs_removed = removed
    report.total_broken_before = broken_before
    report.total_broken_after = broken_after

    logger.info(
        "Reconciliation: %d created, %d resolved, %d removed, %d→%d broken",
        len(report.nodes_created),
        resolved,
        removed,
        broken_before,
        broken_after,
    )
    return report


def diff_nodes(
    extracted_dir: Path,
    curated_dir: Path,
) -> NodeDiffReport:
    """Compare extracted nodes vs curated nodes by ID."""
    extracted = _load_node_ids_from_dir(extracted_dir)
    curated = _load_node_ids_from_dir(curated_dir)

    ext_ids = set(extracted.keys())
    cur_ids = set(curated.keys())

    both = sorted(ext_ids & cur_ids)
    only_ext = sorted(ext_ids - cur_ids)
    only_cur = sorted(cur_ids - ext_ids)

    total = len(ext_ids | cur_ids)
    overlap_pct = len(both) / total if total > 0 else 0.0

    by_decision: dict[str, DecisionDiff] = {}
    all_nodes = {**extracted, **curated}
    decisions = {
        n.get("decision", "unknown") for n in all_nodes.values() if n.get("decision")
    }

    for decision in sorted(decisions):
        ext_in_dec = {
            nid for nid, n in extracted.items() if n.get("decision") == decision
        }
        cur_in_dec = {
            nid for nid, n in curated.items() if n.get("decision") == decision
        }
        by_decision[decision] = DecisionDiff(
            both=sorted(ext_in_dec & cur_in_dec),
            only_extracted=sorted(ext_in_dec - cur_in_dec),
            only_curated=sorted(cur_in_dec - ext_in_dec),
        )

    return NodeDiffReport(
        nodes_both=both,
        nodes_only_extracted=only_ext,
        nodes_only_curated=only_cur,
        total_extracted=len(ext_ids),
        total_curated=len(cur_ids),
        overlap_pct=overlap_pct,
        by_decision=by_decision,
    )
