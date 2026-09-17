"""DDD BC clustering engine — OpenRouter invocation + cohesion evidence.

S16526.3: Assigns Domain-classified symbols to Bounded Contexts using LLM
semantic reasoning combined with cohesion evidence from the CohesionMatrix.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from raise_cli.ddd.cohesion import CohesionMatrix
from raise_cli.ddd.domain_model import BoundedContext
from raise_core.graph.models import SymbolNode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BC_BATCH_SIZE: int = 100
CONFIDENCE_THRESHOLD: float = 0.4
_MAX_ATTEMPTS: int = 3
_RETRY_DELAY_S: float = 2.0
_MAX_WORKERS: int = 4

# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class BCAssignment(BaseModel):
    """LLM-proposed Bounded Context assignment for a single symbol."""

    bc_name: str
    confidence: float
    reasoning: str

    @field_validator("confidence")
    @classmethod
    def _clamp(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class BCMap(BaseModel):
    """Map of symbol_id → BCAssignment covering all input symbols."""

    assignments: dict[str, BCAssignment] = Field(default_factory=dict)

    def get(self, symbol_id: str) -> BCAssignment | None:
        """Return the BCAssignment for symbol_id, or None if absent."""
        return self.assignments.get(symbol_id)

    @property
    def uncertain_ids(self) -> list[str]:
        """Return list of symbol_ids assigned bc_name='uncertain'."""
        return [sid for sid, a in self.assignments.items() if a.bc_name == "uncertain"]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_bounded_contexts(path: Path) -> list[BoundedContext]:
    """Load bounded context definitions from domain-model.yaml.

    Args:
        path: Path to the domain-model.yaml file.

    Returns:
        List of BoundedContext objects.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"domain-model.yaml not found at {path}")

    with path.open() as f:
        data = yaml.safe_load(f)

    bc_list: list[dict[str, Any]] = data.get("bounded_contexts", [])
    return [BoundedContext.model_validate(bc) for bc in bc_list]


def _top_n_neighbors(
    symbol_id: str,
    symbols: list[SymbolNode],
    matrix: CohesionMatrix,
    n: int = 5,
) -> list[tuple[str, float]]:
    """Return the top-N cohesion neighbors for a given symbol.

    Args:
        symbol_id: The target symbol id.
        symbols: All symbols in the batch (used to build id set).
        matrix: CohesionMatrix with pairwise scores.
        n: Maximum number of neighbors to return.

    Returns:
        List of (neighbor_id, score) tuples, sorted descending by score.
    """
    all_ids: set[str] = {sym.id for sym in symbols}
    neighbors: list[tuple[str, float]] = []

    # Key format: "{min_id}::{max_id}" — matches _pair_key() in cohesion.py.
    # If that separator ever changes, this function silently returns no neighbors.
    for key, score in matrix.scores.items():
        parts = key.split("::")
        if len(parts) != 2:
            continue
        a, b = parts
        # Check if this key involves symbol_id
        if a == symbol_id and b != symbol_id and b in all_ids:
            neighbors.append((b, score))
        elif b == symbol_id and a != symbol_id and a in all_ids:
            neighbors.append((a, score))

    neighbors.sort(key=lambda t: t[1], reverse=True)
    return neighbors[:n]


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` fences if present."""
    return re.sub(r"```(?:json)?\s*\n?", "", text).strip()


def _build_clustering_prompt(
    symbols: list[SymbolNode],
    matrix: CohesionMatrix,
    bc_defs: list[BoundedContext],
) -> str:
    """Build the BC clustering prompt with BC anchors + cohesion evidence.

    Prompt has 5 sections:
    1. System instruction
    2. BC Anchor Catalog
    3. Cohesion Evidence (per symbol, top-5 neighbors)
    4. Symbols to Classify
    5. Output Schema

    Args:
        symbols: Batch of SymbolNodes to classify.
        matrix: CohesionMatrix for cohesion evidence.
        bc_defs: Bounded context definitions from domain-model.yaml.

    Returns:
        Fully formatted prompt string.
    """
    lines: list[str] = []

    # Section 1: System instruction
    lines.append("You are a DDD BC assignment expert for the RaiSE codebase.")
    lines.append(
        "Assign each symbol to exactly one Bounded Context based on its purpose, "
        "module, and cohesion with neighbors."
    )
    lines.append("")

    # Section 2: BC Anchor Catalog
    lines.append("## Bounded Context Catalog")
    lines.append("")
    for bc in bc_defs:
        lines.append(f"### {bc.name}")
        lines.append(f"Modules: {bc.modules}")
        lines.append(f"Purpose: {bc.description}")
        if bc.terms:
            term_names = [t.get("name", "") for t in bc.terms if t.get("name")]
            if term_names:
                lines.append(f"Key terms: {', '.join(term_names)}")
        lines.append("")

    # Section 3: Cohesion Evidence
    lines.append("## Cohesion Evidence")
    lines.append("")
    for sym in symbols:
        kind = str(sym.metadata.get("kind", "unknown"))
        module = str(sym.metadata.get("module", "unknown"))
        lines.append(f"- {sym.id} [{kind}] module=`{module}`")
        neighbors = _top_n_neighbors(sym.id, symbols, matrix, n=5)
        if neighbors:
            neighbor_str = ", ".join(f"{nid} ({score:.2f})" for nid, score in neighbors)
            lines.append(f"  Top cohesion neighbors: {neighbor_str}")
        lines.append("")

    # Section 4: Symbols to Classify
    lines.append("## Symbols to Classify")
    lines.append("")
    for sym in symbols:
        kind = str(sym.metadata.get("kind", "unknown"))
        module = str(sym.metadata.get("module", "unknown"))
        signature = str(sym.metadata.get("signature", sym.id))
        lines.append(f"- id: {sym.id}")
        lines.append(f"  kind: {kind}")
        lines.append(f"  module: {module}")
        lines.append(f"  signature: {signature}")
        lines.append("")

    # Section 5: Output Schema
    valid_names = [bc.name for bc in bc_defs] + ["shared_kernel", "uncertain"]
    lines.append("## Output Schema")
    lines.append("")
    lines.append(
        "Return a JSON array with one object per symbol. "
        "Do not include any other text outside the JSON."
    )
    lines.append("")
    lines.append("```json")
    lines.append("[")
    lines.append("  {")
    lines.append('    "id": "<symbol id exactly as provided>",')
    lines.append(
        f'    "bc_name": {json.dumps(valid_names[0])} | ... | "uncertain" | "shared_kernel",'
    )
    lines.append('    "confidence": 0.0,')
    lines.append('    "reasoning": "<1-2 sentence explanation>"')
    lines.append("  }")
    lines.append("]")
    lines.append("```")

    return "\n".join(lines)


def _parse_bc_response(
    text: str,
    valid_bc_names: frozenset[str],
) -> list[tuple[str, BCAssignment]]:
    """Parse LLM JSON response into (symbol_id, BCAssignment) pairs.

    Args:
        text: Raw LLM response text (may include markdown fences).
        valid_bc_names: Frozenset of valid bc_name values (BCs + "shared_kernel" + "uncertain").

    Returns:
        List of (symbol_id, BCAssignment) pairs. Skips malformed entries.
        Returns [] on JSON parse failure.
    """
    cleaned = _strip_markdown_fences(text)
    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse BC clustering response as JSON")
        return []

    if not isinstance(parsed, list):
        logger.warning("BC clustering response is not a list: %s", type(parsed))
        return []

    results: list[tuple[str, BCAssignment]] = []
    for item in parsed:
        if not isinstance(item, dict):
            logger.debug("Skipping non-dict BC entry: %s", item)
            continue
        sym_id = item.get("id")
        if not sym_id or not isinstance(sym_id, str):
            logger.debug("Skipping BC entry with missing id: %s", item)
            continue
        bc_name = item.get("bc_name", "uncertain")
        if bc_name not in valid_bc_names:
            logger.warning(
                "Unrecognized bc_name '%s' for symbol '%s' — keeping as-is",
                bc_name,
                sym_id,
            )
        try:
            assignment = BCAssignment(
                bc_name=str(bc_name),
                confidence=float(item.get("confidence", 0.0)),
                reasoning=str(item.get("reasoning", "")),
            )
            results.append((sym_id, assignment))
        except Exception:  # noqa: BLE001
            logger.debug("Skipping malformed BC entry: %s", item)
    return results


def _cluster_batch(
    symbols: list[SymbolNode],
    matrix: CohesionMatrix,
    bc_defs: list[BoundedContext],
    client: Any,
    model: str,
) -> list[tuple[str, BCAssignment]]:
    """Assign a batch of symbols to BCs via one LLM call with retry.

    Args:
        symbols: Batch of SymbolNodes to cluster.
        matrix: CohesionMatrix for cohesion evidence.
        bc_defs: Bounded context definitions.
        client: OpenAI-compatible client (OpenRouter).
        model: Model identifier string.

    Returns:
        List of (symbol_id, BCAssignment) pairs. May be empty on failure.
    """
    if not symbols:
        return []

    valid_bc_names: frozenset[str] = frozenset(
        [bc.name for bc in bc_defs] + ["shared_kernel", "uncertain"]
    )
    prompt = _build_clustering_prompt(symbols, matrix, bc_defs)
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a DDD BC assignment expert for the RaiSE codebase.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=32768,
            )
            text = response.choices[0].message.content or ""
            results = _parse_bc_response(text, valid_bc_names)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            results = []

        if results:
            return results

        if attempt < _MAX_ATTEMPTS:
            logger.warning(
                "BC clustering (%s) batch attempt %d/%d returned no results%s -- retrying",
                model,
                attempt,
                _MAX_ATTEMPTS,
                f" ({last_exc})" if last_exc else "",
            )
            time.sleep(_RETRY_DELAY_S)

    logger.warning(
        "BC clustering (%s) failed after %d attempts%s",
        model,
        _MAX_ATTEMPTS,
        f": {last_exc}" if last_exc else "",
    )
    return []


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def cluster_symbols(
    symbols: list[SymbolNode],
    cohesion_matrix: CohesionMatrix,
    domain_model_path: Path,
    *,
    model: str = "google/gemini-3.7-flash",
    batch_size: int = BC_BATCH_SIZE,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> BCMap:
    """Assign each Domain symbol to a Bounded Context using LLM + cohesion evidence.

    Symbols with LLM confidence below `confidence_threshold` are assigned
    bc_name="uncertain". The bc_name answer set is loaded from `domain_model_path`.

    Args:
        symbols: Domain-classified SymbolNodes to cluster.
        cohesion_matrix: Pairwise cohesion scores from S16526.2.
        domain_model_path: Path to .raise/domain-model.yaml.
        model: OpenRouter model identifier.
        batch_size: Number of symbols per LLM batch (default 100).
        confidence_threshold: Minimum confidence to accept a bc_name (default 0.4).

    Returns:
        BCMap mapping every input symbol_id to a BCAssignment.
    """
    if not symbols:
        return BCMap()

    bc_defs = _load_bounded_contexts(domain_model_path)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set — BC clustering unavailable")
        return BCMap()

    import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    batches = [symbols[i : i + batch_size] for i in range(0, len(symbols), batch_size)]
    total_batches = len(batches)
    workers = min(_MAX_WORKERS, total_batches)
    print(
        f"  Clustering {len(symbols)} symbols in {total_batches} batches"
        f" ({workers} parallel workers)",
        file=sys.stderr,
        flush=True,
    )

    indexed_results: list[tuple[int, list[tuple[str, BCAssignment]]]] = []

    def _run(
        idx: int, batch: list[SymbolNode]
    ) -> tuple[int, list[tuple[str, BCAssignment]]]:
        results = _cluster_batch(batch, cohesion_matrix, bc_defs, client, model)
        print(
            f"  Batch {idx + 1}/{total_batches} → {len(results)}/{len(batch)} assigned",
            file=sys.stderr,
            flush=True,
        )
        return idx, results

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_run, idx, batch): idx for idx, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            indexed_results.append(future.result())

    indexed_results.sort(key=lambda t: t[0])

    # Collect all (symbol_id, BCAssignment) pairs
    raw_assignments: dict[str, BCAssignment] = {
        sym_id: assignment
        for _, batch_results in indexed_results
        for sym_id, assignment in batch_results
    }

    # Post-process: apply confidence threshold + fill missing
    input_ids = {sym.id for sym in symbols}
    final_assignments: dict[str, BCAssignment] = {}

    for sym_id in input_ids:
        if sym_id not in raw_assignments:
            # Missing from LLM response
            final_assignments[sym_id] = BCAssignment(
                bc_name="uncertain",
                confidence=0.0,
                reasoning="Not returned by LLM",
            )
        else:
            a = raw_assignments[sym_id]
            if a.confidence < confidence_threshold:
                final_assignments[sym_id] = BCAssignment(
                    bc_name="uncertain",
                    confidence=a.confidence,
                    reasoning=a.reasoning,
                )
            else:
                final_assignments[sym_id] = a

    return BCMap(assignments=final_assignments)
