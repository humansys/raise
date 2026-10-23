"""Business rules LLM derivation for PMO cartridges (S9939.2, ADR-111).

Reads a MODEL cartridge (model.json) and calls an LLM client to derive
business rules for custom fields grouped by issue type. Produces
instances/rules.json with SCD Type-2-compatible nodes.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import yaml
from pydantic import BaseModel


class BusinessRuleEnrichmentError(RuntimeError):
    """Raised when enrichment fails for ALL candidate issue types.

    Distinguishes a total wipe-out (e.g. the LLM client is unavailable — missing
    API key, auth/network error) from a legitimate empty result (no qualifying
    fields). Without this, every LLM call silently fails, an empty rules.json is
    written, and the CLI reports success (RAISE-10012).
    """


class FieldSummary(BaseModel, frozen=True):
    """Compact view of a custom field passed to the LLM client."""

    field_id: str
    name: str
    schema_type: str
    allowed_values: list[str]
    belongs_to_issue_types: list[str]


class BusinessRuleProposal(BaseModel, frozen=True):
    """A single business rule proposed by the LLM client for a field."""

    field_id: str
    rule_text: str


@runtime_checkable
class BacklogEnrichmentClient(Protocol):
    """Protocol for LLM clients that derive business rules from field metadata."""

    async def derive_business_rules(
        self, issue_type: str, fields: list[FieldSummary]
    ) -> list[BusinessRuleProposal]:
        """Derive business rules for fields of a given issue type."""
        ...


# ── Helpers ──────────────────────────────────────────────────────────────────


def _issue_type_slug(issue_type: str) -> str:
    """Convert issue type name to URL-safe slug (e.g. 'Story Points' → 'story-points')."""
    return issue_type.lower().replace(" ", "-")


def _should_include_field(node_meta: dict[str, Any]) -> bool:
    """Include fields with allowed_values OR non-trivial schema_type."""
    allowed = node_meta.get("allowed_values", [])
    schema_type = node_meta.get("schema_type", "")
    return bool(allowed) or schema_type not in ("", "string", "number", "date")


def _rules_up_to_date(rules_path: Path, schema_version: str) -> bool:
    """Return True if rules.json is a non-empty flat list stamped with current schema_version.

    Corrupt or otherwise unreadable files return False so the generator re-runs (AR2-fix).
    """
    if not rules_path.exists():
        return False
    try:
        existing: object = json.loads(rules_path.read_text(encoding="utf-8"))
        return (
            isinstance(existing, list)
            and bool(existing)
            and isinstance(existing[0], dict)
            and existing[0].get("metadata", {}).get("schema_version") == schema_version
        )
    except Exception:
        return False  # corrupt file → regenerate


# ── Main entry point ──────────────────────────────────────────────────────────


async def enrich_cartridge_with_business_rules(
    cartridge_dir: Path,
    llm_client: BacklogEnrichmentClient,
) -> Path:
    """Derive business rules from a MODEL cartridge and write rules.json.

    Args:
        cartridge_dir: Root directory of the cartridge (contains CARTRIDGE.yaml).
        llm_client: Protocol implementor that calls the LLM.

    Returns:
        The cartridge_dir (for chaining).
    """
    # 1. Read CARTRIDGE.yaml
    manifest = yaml.safe_load(
        (cartridge_dir / "CARTRIDGE.yaml").read_text(encoding="utf-8")
    )
    schema_version: str = manifest["schema_version"]
    cartridge_name: str = manifest["name"]

    # 2. Idempotency check — rules.json is a flat list; schema_version lives in each node's
    #    metadata. Corrupt or empty files regenerate rather than hard-failing (AR2-fix, AR5-fix).
    rules_path = cartridge_dir / "instances" / "rules.json"
    if _rules_up_to_date(rules_path, schema_version):
        return cartridge_dir

    # 3. Read model.json
    model_path = cartridge_dir / "instances" / "model.json"
    nodes: list[dict[str, Any]] = json.loads(model_path.read_text(encoding="utf-8"))

    # 4. Group custom fields by issue_type
    issue_type_fields: dict[str, list[FieldSummary]] = {}
    for node in nodes:
        if node.get("type") != "backlog.custom_field":
            continue
        meta = node.get("metadata", {})
        if not _should_include_field(meta):
            continue
        for it_name in meta.get("belongs_to_issue_types", []):
            summary = FieldSummary(
                field_id=meta["field_id"],
                name=node["content"],
                schema_type=meta.get("schema_type", ""),
                allowed_values=meta.get("allowed_values", []),
                belongs_to_issue_types=meta.get("belongs_to_issue_types", []),
            )
            issue_type_fields.setdefault(it_name, []).append(summary)

    # 5. Call LLM per issue_type. Per-type failures are best-effort (one bad type
    #    must not tumble the rest), but a TOTAL wipe-out fails loud below.
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_rules: list[dict[str, Any]] = []
    failures = 0
    last_error: Exception | None = None
    for issue_type, fields in issue_type_fields.items():
        try:
            proposals = await llm_client.derive_business_rules(issue_type, fields)
            for p in proposals:
                node_id = f"backlog.rule.{_issue_type_slug(issue_type)}.{p.field_id}"
                all_rules.append(
                    {
                        "id": node_id,
                        "type": "backlog.business_rule",
                        "content": p.rule_text,
                        "source_file": None,
                        "created": now,
                        "updated_at": None,
                        "metadata": {
                            "cartridge": cartridge_name,
                            "issue_type": issue_type,
                            "field_id": p.field_id,
                            "schema_version": schema_version,
                        },
                    }
                )
        except Exception as exc:
            failures += 1
            last_error = exc

    # 5b. Distinguish '0 rules because nothing qualified' (handled by step 4 leaving
    #     issue_type_fields empty) from '0 rules because every LLM call failed'. The
    #     latter must not masquerade as success with an empty rules.json (RAISE-10012).
    if issue_type_fields and failures == len(issue_type_fields):
        raise BusinessRuleEnrichmentError(
            f"Business rule enrichment failed for all {failures} candidate issue "
            f"type(s) in cartridge '{cartridge_name}': {last_error}. rules.json not "
            f"written — the LLM client is likely unavailable (check ANTHROPIC_API_KEY)."
        ) from last_error

    # 6. Write rules.json — flat list (consistent with model.json and ingest expectations).
    #    schema_version is in each node's metadata; idempotency reads it from there.
    rules_path.write_text(
        json.dumps(all_rules, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return cartridge_dir
