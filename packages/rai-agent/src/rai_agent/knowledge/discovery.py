"""Knowledge schema discovery and diff tools.

Discover ontology schemas from corpora (LLM-based) and compare
discovered vs reference schemas and extracted vs curated node sets.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Prompts ---

DISCOVERY_PROMPT = """\
You are analyzing a book corpus to discover its knowledge structure.

Identify all distinct types of knowledge entities in this text. For each type:
1. Give it a short, lowercase name (e.g. "concept", "tool", "metric")
2. List the fields/attributes that describe entities of this type

Also list the relationship types between entities (e.g. "requires", "belongs_to").

Focus on what the TEXT reveals — do not assume any pre-existing schema.
Analyze the structure, categories, and relationships present in the content.

Return a structured schema specification with:
- node_types: list of (name, fields) for each entity type discovered
- relationship_types: list of relationship type names

TEXT TO ANALYZE:
{corpus_text}
"""


REFINEMENT_PROMPT = """\
You previously analyzed a corpus and discovered these entity types:
{discovered_types}

However, a reference schema for this domain also includes these types that you did NOT discover:
{missing_types}

Re-examine the corpus below. For each missing type, determine if entities of that type
exist in the text. If so, define the type with its fields. If a type genuinely does not
appear in the text, omit it.

Also note any additional relationship types relevant to the newly discovered types.

Return ONLY the newly found types and relationships (do not repeat the previously discovered ones).

TEXT TO ANALYZE:
{corpus_text}
"""


# --- Models ---


class NodeTypeSpec(BaseModel):
    """A discovered node type with its fields."""

    name: str = Field(..., description="Node type name (e.g. 'concept', 'tool')")
    fields: list[str] = Field(
        default_factory=list, description="Field names for this type"
    )


class SchemaSpec(BaseModel):
    """Schema discovered from a corpus — types, fields, relationships."""

    node_types: list[NodeTypeSpec] = Field(
        default_factory=lambda: list[NodeTypeSpec]()
    )
    relationship_types: list[str] = Field(default_factory=list)


class FieldDiff(BaseModel):
    """Per-type field comparison between discovered and reference."""

    common: list[str] = Field(default_factory=list)
    only_discovered: list[str] = Field(default_factory=list)
    only_reference: list[str] = Field(default_factory=list)


class SchemaDiffReport(BaseModel):
    """Comparison of discovered schema spec vs a reference Pydantic model."""

    types_both: list[str] = Field(default_factory=list)
    types_only_discovered: list[str] = Field(default_factory=list)
    types_only_reference: list[str] = Field(default_factory=list)
    field_diffs: dict[str, FieldDiff] = Field(default_factory=dict)


class DecisionDiff(BaseModel):
    """Per-decision-area breakdown for content diff."""

    both: list[str] = Field(default_factory=list)
    only_extracted: list[str] = Field(default_factory=list)
    only_curated: list[str] = Field(default_factory=list)


class NodeDiffReport(BaseModel):
    """Comparison of extracted nodes vs curated nodes by ID."""

    nodes_both: list[str] = Field(default_factory=list)
    nodes_only_extracted: list[str] = Field(default_factory=list)
    nodes_only_curated: list[str] = Field(default_factory=list)
    total_extracted: int = 0
    total_curated: int = 0
    overlap_pct: float = 0.0
    by_decision: dict[str, DecisionDiff] = Field(default_factory=dict)


# --- Diff functions ---


def diff_schemas(
    discovered: SchemaSpec,
    reference_model: Any,
) -> SchemaDiffReport:
    """Compare a discovered SchemaSpec against a reference model's structure.

    The reference_model should have:
    - _node_types: list[str] — known node type names
    - _fields: dict[str, list[str]] — per-type field lists

    For real usage with OntologyNode, extract these from the Pydantic model
    and its Literal type annotation.
    """
    # Extract reference type names and fields
    ref_types: list[str] = getattr(reference_model, "_node_types", [])
    ref_fields: dict[str, list[str]] = getattr(reference_model, "_fields", {})

    disc_type_names = {nt.name for nt in discovered.node_types}
    ref_type_names = set(ref_types)

    types_both = sorted(disc_type_names & ref_type_names)
    types_only_disc = sorted(disc_type_names - ref_type_names)
    types_only_ref = sorted(ref_type_names - disc_type_names)

    # Field-level diff for overlapping types
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


def discover_schema(
    corpus_path: Path,
    model: str = "claude-sonnet-4-20250514",
    client: Any | None = None,
) -> SchemaSpec:
    """Discover ontology schema from a corpus using LLM analysis.

    Uses the Claude Agent SDK for inference (see Confluence: Inference Mechanism).
    Reads the corpus, sends it with a zero-knowledge prompt, returns SchemaSpec.

    Args:
        corpus_path: Path to the markdown corpus file.
        model: Claude model ID for the LLM call.
        client: Optional mock client factory (for testing).
    """
    corpus_text = corpus_path.read_text()
    if not corpus_text.strip():
        msg = f"Empty corpus at {corpus_path}"
        raise ValueError(msg)

    prompt = DISCOVERY_PROMPT.replace("{corpus_text}", corpus_text)

    from rai_agent.inference import invoke_structured

    result = invoke_structured(
        prompt=prompt,
        response_model=SchemaSpec,
        model=model,
        _client_factory=client,
    )

    logger.info(
        "Discovered %d node types, %d relationship types",
        len(result.node_types),
        len(result.relationship_types),
    )
    return result


def refine_schema(
    *,
    initial_schema: SchemaSpec,
    missing_types: list[str],
    corpus_path: Path,
    model: str = "claude-sonnet-4-20250514",
    client: Any | None = None,
) -> SchemaSpec:
    """Refine a discovered schema by searching for missing reference types.

    If missing_types is empty, returns initial_schema unchanged (no LLM call).
    Otherwise, sends a targeted prompt asking the LLM to look for the specific
    missing types in the corpus, then merges results with the initial schema.
    """
    if not missing_types:
        return initial_schema

    corpus_text = corpus_path.read_text()
    discovered_names = ", ".join(nt.name for nt in initial_schema.node_types)
    missing_names = ", ".join(missing_types)

    prompt = (
        REFINEMENT_PROMPT
        .replace("{discovered_types}", discovered_names)
        .replace("{missing_types}", missing_names)
        .replace("{corpus_text}", corpus_text)
    )

    from rai_agent.inference import invoke_structured

    refinement = invoke_structured(
        prompt=prompt,
        response_model=SchemaSpec,
        model=model,
        _client_factory=client,
    )

    # Merge: keep all initial types + add newly found types
    existing_names = {nt.name for nt in initial_schema.node_types}
    merged_types = list(initial_schema.node_types)
    for nt in refinement.node_types:
        if nt.name not in existing_names:
            merged_types.append(nt)
            existing_names.add(nt.name)

    # Merge relationship types (deduplicate)
    all_rels = set(initial_schema.relationship_types)
    all_rels.update(refinement.relationship_types)

    merged = SchemaSpec(
        node_types=merged_types,
        relationship_types=sorted(all_rels),
    )

    logger.info(
        "Refinement added %d types, %d relationships",
        len(merged.node_types) - len(initial_schema.node_types),
        len(merged.relationship_types) - len(initial_schema.relationship_types),
    )
    return merged


# --- Reconciliation ---


class ReconcileReport(BaseModel):
    """Report from reconcile_extracted: what was fixed."""

    nodes_created: list[str] = Field(default_factory=list)
    refs_resolved: int = 0
    refs_removed: int = 0
    total_broken_before: int = 0
    total_broken_after: int = 0


def reconcile_extracted(
    extracted_dir: Path,
    domain_config: dict[str, Any],
) -> ReconcileReport:
    """Auto-fix mechanical issues in extracted nodes.

    1. Create missing decision-area nodes (decision-people, etc.)
    2. Fuzzy-match broken refs to existing node IDs
    3. Remove refs that still can't be resolved

    Modifies YAML files in-place. Run after extraction, before curation.
    """
    # Load all nodes
    nodes = _load_node_ids_from_dir(extracted_dir)
    all_ids = set(nodes.keys())
    report = ReconcileReport()

    # Step 1: Create missing decision nodes
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
            path.write_text(yaml.dump(node_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
            all_ids.add(node_id)
            report.nodes_created.append(node_id)
            logger.info("Created missing decision node: %s", node_id)

    # Step 2: Count broken refs and try fuzzy resolution
    broken_before = 0
    resolved = 0
    removed = 0

    for path in sorted(extracted_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        if not isinstance(raw, dict) or "relationships" not in raw:
            continue

        modified = False
        new_rels = []
        for rel in raw["relationships"]:
            if not isinstance(rel, dict) or "target" not in rel:
                new_rels.append(rel)
                continue

            target = rel["target"]
            if target in all_ids:
                new_rels.append(rel)
                continue

            broken_before += 1

            # Try fuzzy match: find closest existing ID
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
            path.write_text(yaml.dump(raw, default_flow_style=False, allow_unicode=True, sort_keys=False))

    # Count remaining broken
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
        len(report.nodes_created), resolved, removed, broken_before, broken_after,
    )
    return report


def _fuzzy_find_id(target: str, existing_ids: set[str]) -> str | None:
    """Find closest match for a broken target ID.

    Strategy: check if target is a prefix/suffix of an existing ID,
    or if an existing ID is a prefix of the target.
    """
    # Exact prefix match (e.g. "concept-employee-engagement" matches
    # "concept-employee-engagement-survey")
    candidates = [eid for eid in existing_ids if eid.startswith(target) or target.startswith(eid)]
    if len(candidates) == 1:
        return candidates[0]

    # Strip type prefix and try again (e.g. "debt-service-capability" → look for "*-debt-service-*")
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


def diff_nodes(
    extracted_dir: Path,
    curated_dir: Path,
) -> NodeDiffReport:
    """Compare extracted nodes vs curated nodes by ID.

    Loads YAML files recursively from both directories.
    """
    extracted = _load_node_ids_from_dir(extracted_dir)
    curated = _load_node_ids_from_dir(curated_dir)

    ext_ids = set(extracted.keys())
    cur_ids = set(curated.keys())

    both = sorted(ext_ids & cur_ids)
    only_ext = sorted(ext_ids - cur_ids)
    only_cur = sorted(cur_ids - ext_ids)

    total = len(ext_ids | cur_ids)
    overlap_pct = len(both) / total if total > 0 else 0.0

    # By-decision breakdown
    by_decision: dict[str, DecisionDiff] = {}
    all_nodes = {**extracted, **curated}
    decisions = {
        n.get("decision", "unknown")
        for n in all_nodes.values()
        if n.get("decision")
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
