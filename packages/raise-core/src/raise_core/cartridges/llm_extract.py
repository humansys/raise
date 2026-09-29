"""LLM-powered cartridge extractor — model-agnostic structured extraction.

Uses OpenAI-compatible API with JSON mode + Pydantic validation.
Works with any provider: OpenRouter, OpenAI, Anthropic (via OpenAI compat).
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from raise_core.cartridges.chunker import Chunk, GenericChunker
from raise_core.cartridges.extract import RelationshipSchema, filter_relationships
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL = "google/gemini-2.5-flash-lite"


class _ExtractionResponse(BaseModel):
    """Pydantic validation for LLM JSON output."""

    nodes: list[GraphNode] = Field(default_factory=list)


class LLMExtractor:
    """Cartridge extractor using LLM structured output.

    Implements CartridgeExtractor Protocol via duck typing.
    Uses OpenAI-compatible API with JSON mode, validates with Pydantic.
    """

    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
        heading_level: int = 2,
        max_tokens: int = 4096,
    ) -> None:
        self._explicit_client = client
        self._deferred_model = model
        self._client_resolved: Any | None = client
        self._model_resolved: str | None = model or (_DEFAULT_MODEL if client else None)
        self._chunker = GenericChunker(heading_level=heading_level)
        self._max_tokens = max_tokens

    def _ensure_client(self) -> tuple[Any, str]:
        if self._client_resolved is not None:
            return self._client_resolved, self._model_resolved or _DEFAULT_MODEL
        client, model = _create_default_client(self._deferred_model)
        self._client_resolved = client
        self._model_resolved = model
        return client, model

    def extract(
        self,
        paths: list[Path],
        node_type: str,
        cartridge_name: str,
        *,
        schema: RelationshipSchema | None = None,
        domain_context: str = "",
    ) -> list[GraphNode]:
        """Extract nodes from corpus files using LLM structured output.

        When ``schema`` is provided, the prompt includes a relationship
        schema section (guided extraction) and relationships with types
        outside the schema are filtered from the results.
        """
        if not paths:
            return []

        all_nodes: list[GraphNode] = []
        now = datetime.now(tz=UTC).isoformat()

        for path in paths:
            chunks = self._chunker.split(path)
            for chunk in chunks:
                try:
                    nodes = self._extract_chunk(
                        chunk,
                        node_type,
                        cartridge_name,
                        now,
                        str(path),
                        schema,
                        domain_context,
                    )
                    all_nodes.extend(nodes)
                except Exception:
                    logger.warning(
                        "Extraction failed for chunk '%s' in %s",
                        chunk.heading or "(preamble)",
                        path,
                    )

        return prefix_ids(all_nodes, cartridge_name)

    def _extract_chunk(
        self,
        chunk: Chunk,
        node_type: str,
        cartridge_name: str,
        now: str,
        source_file: str,
        schema: RelationshipSchema | None = None,
        domain_context: str = "",
    ) -> list[GraphNode]:
        """Extract nodes from a single chunk via JSON mode + Pydantic."""
        prompt = build_prompt(chunk, node_type, cartridge_name, schema, domain_context)

        client, model = self._ensure_client()
        output_tokens = max(self._max_tokens, len(chunk.text) * 2)
        response = client.chat.completions.create(
            model=model,
            max_tokens=min(output_tokens, 16384),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content or ""
        if not raw_text.strip():
            return []

        try:
            data = json.loads(_strip_markdown_fences(raw_text))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from LLM for chunk '%s'", chunk.heading)
            return []

        nodes_list = flatten_nodes(data)
        if not nodes_list:
            return []

        return validate_and_enrich(
            nodes_list,
            now,
            source_file,
            node_type,
            cartridge_name,
            chunk.heading,
            schema,
        )


_FENCE_RE = re.compile(r"^```(?:json)?\s*\n(.*?)\n```\s*$", re.DOTALL)


def _strip_markdown_fences(text: str) -> str:
    """Strip markdown code fences (```json ... ```) from LLM output."""
    m = _FENCE_RE.match(text.strip())
    return m.group(1) if m else text


def _normalize_node_type(t: str) -> str:
    """Normalize type name: lowercase, underscores/spaces → hyphens."""
    return re.sub(r"[\s_]+", "-", t.strip().lower()).strip("-")


def validate_and_enrich(
    nodes_list: list[dict[str, Any]],
    now: str,
    source_file: str,
    node_type: str,
    cartridge_name: str,
    heading: str,
    schema: RelationshipSchema | None,
) -> list[GraphNode]:
    """Inject server-side fields, validate via Pydantic, and enrich metadata."""
    for node_dict in nodes_list:
        # Coerce missing OR explicit-null created → now. setdefault alone leaves
        # an explicit `"created": null` (which real Gemini/OpenRouter output
        # returns) in place, failing Pydantic and dropping the whole chunk
        # (SP-project-upgrade gemba: la-aldea-erp + 49bis).
        if not node_dict.get("created"):
            node_dict["created"] = now
        # RAISE-10952: force source_file from the actual path, never trust LLM
        node_dict["source_file"] = source_file

    try:
        parsed = _ExtractionResponse.model_validate({"nodes": nodes_list})
    except ValidationError as exc:
        logger.warning("Pydantic validation failed for chunk '%s': %s", heading, exc)
        return []

    # RAISE-10948/10949/10950: filter nodes whose LLM-assigned type doesn't
    # match the requested node_type, then force canonical type name.
    requested = _normalize_node_type(node_type)
    result: list[GraphNode] = []
    for node in parsed.nodes:
        llm_type = _normalize_node_type(node.type) if node.type else ""
        if llm_type and llm_type != requested:
            continue
        node.type = node_type
        if "cartridge" not in node.metadata:
            node.metadata["cartridge"] = cartridge_name
        if "source_heading" not in node.metadata:
            node.metadata["source_heading"] = heading
        if schema is not None and schema.relationship_types:
            filter_relationships(node, schema)
        result.append(node)

    return result


def flatten_nodes(data: Any) -> list[dict[str, Any]]:
    """Extract a flat list of node dicts from various LLM response shapes."""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict) and "id" in item]

    if not isinstance(data, dict):
        return []

    if "nodes" in data:
        raw = data["nodes"]
        if isinstance(raw, list):
            result: list[dict[str, Any]] = []
            for item in raw:
                if isinstance(item, dict) and "id" in item:
                    nested = item.pop("nodes", None)
                    result.append(item)
                    if isinstance(nested, list):
                        result.extend(
                            n for n in nested if isinstance(n, dict) and "id" in n
                        )
            return result
        return []

    if "id" in data:
        return [data]

    return []


_EXTRACTION_PROMPT = """\
You are a knowledge extraction engine. Extract structured entities from the text below.

## Rules
- Extract ONLY entities of type "{node_type}" — skip everything else
- Each entity must be a distinct instance of "{node_type}"
- Use the ORIGINAL wording from the text — do not paraphrase or rewrite
- For content: quote or tightly summarize the source (1-3 sentences max)
- Set the "type" field to exactly "{node_type}" for every node
- Include relationships when entities reference each other
- If the text contains NO entities of type "{node_type}", return {{"nodes": []}}
- For markdown tables: each row with an ID column is one entity
- SKIP these entirely — return NO nodes for them:
  - Version history / changelog entries (dates + "Added X" / "Changed Y")
  - Approval records (who approved what)
  - YAML/config code blocks (pre-commit config, pyproject.toml snippets)
  - Boilerplate headers, frontmatter, table-of-contents
  If the ENTIRE section is one of these, return {{"nodes": []}}

## Output format
Return a JSON object with a "nodes" array. Each node is a FLAT object (no nesting):
```json
{{
  "nodes": [
    {{
      "id": "kebab-case-id",
      "type": "guardrail",
      "content": "Original text or tight summary from source",
      "source_file": null,
      "created": "2026-01-01T00:00:00+00:00",
      "metadata": {{
        "level": "MUST",
        "category": "code-quality",
        "verification": "how to verify",
        "relationships": [{{"target": "other-id", "type": "implements"}}]
      }}
    }}
  ]
}}
```

## Table Extraction Rules
For markdown tables, treat EACH data row as one individual node:
- Column headers become metadata keys (lowercase, kebab-case, e.g. "Guardrail ID" → "guardrail-id")
- If an ID or Name column exists: use its value (kebab-cased) as the node `id`
- If no ID column: generate `id` from the first column value (kebab-case)
- `content` = the most descriptive column value (description, purpose, or summary)

Table with ID column — given:
```
| ID       | Category     | Description            | Verification        |
|----------|------------- |------------------------|---------------------|
| CODE-001 | code-quality | Type hints on all code | pyright --strict    |
```
Output:
```json
{{"id": "code-001", "type": "guardrail", "content": "Type hints on all code",
  "metadata": {{"id": "CODE-001", "category": "code-quality", "verification": "pyright --strict"}}}}
```

Table without ID column — given:
```
| Layer    | Technology   |
|----------|------------- |
| Language | Python 3.12+ |
```
Output (id from first column):
```json
{{"id": "layer-language", "type": "component", "content": "Python 3.12+",
  "metadata": {{"layer": "Language", "technology": "Python 3.12+"}}}}
```

## Example
Given table row: "| `MUST-CODE-001` | MUST | Type hints on all code | `pyright --strict` passes | Solution Vision §Stack |"
Output:
```json
{{
  "id": "must-code-001",
  "type": "guardrail",
  "content": "Type hints on all code. All Python code must have complete type annotations.",
  "source_file": null,
  "created": "2026-01-01T00:00:00+00:00",
  "metadata": {{
    "level": "MUST",
    "category": "code-quality",
    "verification": "pyright --strict passes",
    "derived_from": "Solution Vision §Stack",
    "relationships": [{{"target": "type-safety-first", "type": "implements"}}]
  }}
}}
```

## Text to extract from{heading_ctx}:

{text}"""


_SCHEMA_SECTION = """\
## Relationship Schema
Extract relationships between entities using ONLY these types:
{type_lines}

For each entity, include a "relationships" array in metadata with
{{"target": "kebab-case-id", "type": "<type-from-above>"}}.
Only include relationships where both entities exist in this section.

"""


_DOMAIN_SECTION = """\
## Domain Context
This cartridge covers: {domain_context}
Adapt entity types and relationships to this domain — the default types \
(concept, practice, guardrail, etc.) are suggestions, not constraints.

"""


def build_prompt(
    chunk: Chunk,
    node_type: str,
    cartridge_name: str,
    schema: RelationshipSchema | None = None,
    domain_context: str = "",
) -> str:
    """Build the extraction prompt for a chunk.

    Shared by the API extractor and the agent-native extractor so both hand the
    model the exact same instruction. Injects the relationship-schema and
    domain-context sections when provided.
    """
    heading_ctx = f" (section: {chunk.heading})" if chunk.heading else ""
    prompt = _EXTRACTION_PROMPT.format(
        heading_ctx=heading_ctx,
        text=chunk.text,
        node_type=node_type,
        cartridge_name=cartridge_name,
    )
    marker = "## Text to extract from"
    injections = ""
    if schema is not None and schema.relationship_types:
        type_lines = "\n".join(
            f"- {rt.type}: {rt.description}" if rt.description else f"- {rt.type}"
            for rt in schema.relationship_types
        )
        injections += _SCHEMA_SECTION.format(type_lines=type_lines)
    if domain_context:
        injections += _DOMAIN_SECTION.format(domain_context=domain_context)
    if injections:
        prompt = prompt.replace(marker, injections + marker, 1)
    return prompt


def prefix_ids(nodes: list[GraphNode], cartridge_name: str) -> list[GraphNode]:
    """Ensure all node IDs have the cartridge prefix."""
    prefix = f"kc-{cartridge_name}-"
    result: list[GraphNode] = []
    for node in nodes:
        if not node.id.startswith(prefix):
            node = node.model_copy(update={"id": f"{prefix}{node.id}"})
        result.append(node)
    return result


def _create_default_client(model: str | None = None) -> tuple[Any, str]:
    """Create OpenAI-compatible client from environment.

    Detection order:
    1. OPENROUTER_API_KEY → OpenRouter
    2. OPENAI_API_KEY + OPENAI_BASE_URL → custom endpoint
    3. OPENAI_API_KEY → OpenAI direct
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        msg = "LLMExtractor requires 'openai'. Install with: pip install openai"
        raise ImportError(msg) from exc

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        return (
            OpenAI(base_url=_OPENROUTER_BASE_URL, api_key=openrouter_key),
            model or _DEFAULT_MODEL,
        )

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        base_url = os.environ.get("OPENAI_BASE_URL")
        return OpenAI(api_key=openai_key, base_url=base_url), model or "gpt-4o-mini"

    msg = (
        "LLMExtractor requires an API key. Set one of:\n"
        "  OPENROUTER_API_KEY (recommended — supports 200+ models)\n"
        "  OPENAI_API_KEY [+ OPENAI_BASE_URL]"
    )
    raise ValueError(msg)


__all__ = [
    "LLMExtractor",
    "build_prompt",
    "flatten_nodes",
    "prefix_ids",
    "validate_and_enrich",
]
