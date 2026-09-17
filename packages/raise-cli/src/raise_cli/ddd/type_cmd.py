"""DDD Pass 3 tactical classification command — rai graph ddd type.

Implements the heavy logic for classifying D-layer symbols into tactical DDD
patterns (Entity, ValueObject, DomainService, DomainEvent, AggregateRoot,
Factory, RepositoryInterface) via LLM batch classification.

Architecture (D1):
  - All heavy logic lives here; graph.py is a thin wrapper.
  - graph.py adds @ddd_app.command("type") and calls run_ddd_type().
  - Lazy import of raise_cli.cli.error_handler.cli_error to avoid circular
    imports (same pattern as domain_model.py).

BC source (D2): belongs_to edges in the loaded Graph, not ddd_bc annotation.
Annotation scope (D5): REPO_WIDE — tactical type is symbol semantic, not worktree.
Parallelism (D6): ThreadPoolExecutor(max_workers=4), batch_size=100.
Artifact (D7): work/epics/e16527-ddd-pass3-entity-typing/artifacts/ddd-type-{ts}.json
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from raise_cli.ddd.tactical import TacticalClassification, TacticalType
from raise_cli.ddd.tactical_prompts import build_tactical_classification_prompt
from raise_core.graph.engine import Graph
from raise_core.graph.models import SymbolNode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BATCH_SIZE: int = 100
_MAX_WORKERS: int = 4
_MAX_ATTEMPTS: int = 3
_RETRY_DELAY_S: float = 2.0
_ARTIFACT_EPIC_DIR: str = "work/epics/e16527-ddd-pass3-entity-typing/artifacts"
_STORY_ID: str = "RAISE-16916"

# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class DddTypeReport(BaseModel):
    """Report produced by a single ``rai graph ddd type`` run."""

    d_symbol_count: int
    classified_count: int
    unresolved_count: int
    bc_filter: str | None
    min_confidence: float
    model: str
    by_bc: dict[str, dict[str, int]]
    avg_confidence_by_bc_type: dict[str, dict[str, float]]
    classifications: dict[str, dict[str, Any]]
    artifact_path: Path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_d_annotations(backend: Any) -> dict[str, dict[str, Any]]:
    """Load ddd-namespace annotations filtered to ddd_layer == 'D'.

    Args:
        backend: Graph backend with load_annotations(namespace) method.

    Returns:
        Dict mapping symbol_id -> annotation dict for D-layer symbols only.
    """
    all_annots: dict[str, dict[str, Any]] = backend.load_annotations("ddd")
    return {k: v for k, v in all_annots.items() if v.get("ddd_layer") == "D"}


def _load_bc_map(graph: Graph) -> dict[str, str]:
    """Return symbol_id -> bc_name from belongs_to edges to BC-* nodes.

    BC assignments are written as ``belongs_to`` edges from SymbolNode → BC-{name}
    nodes in the REPO_WIDE partition by ``upsert_bc_assignments()``. This is
    the only authoritative source; ``ddd_bc`` annotation field does not exist
    (Design D2).

    Args:
        graph: Loaded Graph with BC assignment edges.

    Returns:
        Dict mapping symbol_id -> bc_name (with "BC-" prefix stripped).
    """
    result: dict[str, str] = {}
    for src, tgt, edge_data in graph.graph.edges(data=True):
        if str(edge_data.get("type", "")) == "belongs_to" and str(tgt).startswith(
            "BC-"
        ):
            result[str(src)] = str(tgt).removeprefix("BC-")
    return result


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` fences if present."""
    return re.sub(r"```(?:json)?\s*\n?", "", text).strip()


def _parse_tactical_response(text: str) -> list[TacticalClassification]:
    """Parse LLM JSON response into TacticalClassification objects.

    Args:
        text: Raw LLM response (may include markdown fences).

    Returns:
        List of TacticalClassification objects. Skips malformed entries.
        Returns [] on JSON parse failure.
    """
    cleaned = _strip_markdown_fences(text)
    try:
        parsed: object = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse tactical classification response as JSON")
        return []

    if not isinstance(parsed, list):
        logger.warning("Tactical response is not a list: %s", type(parsed))
        return []

    results: list[TacticalClassification] = []
    for item in parsed:
        if not isinstance(item, dict):
            logger.debug("Skipping non-dict entry: %s", item)
            continue
        sym_id = item.get("id")
        if not sym_id or not isinstance(sym_id, str):
            logger.debug("Skipping entry with missing id: %s", item)
            continue
        tactical_type_str = item.get("tactical_type")
        if not tactical_type_str:
            logger.debug("Skipping entry with missing tactical_type: %s", item)
            continue
        try:
            cls = TacticalClassification(
                symbol_id=sym_id,
                tactical_type=TacticalType(str(tactical_type_str)),
                confidence=float(item.get("confidence", 0.0)),
                rationale=str(item.get("rationale", "")),
            )
            results.append(cls)
        except Exception:  # noqa: BLE001
            logger.debug("Skipping malformed tactical entry: %s", item)

    return results


def _classify_batch(
    symbols: list[dict[str, Any]],
    _bc_map: dict[str, str],
    client: Any,
    model: str,
) -> list[TacticalClassification]:
    """Classify a batch of symbols via one LLM call (with retry).

    Args:
        symbols: List of symbol dicts (id, kind, signature, module, file, line).
        _bc_map: Symbol→BC map (reserved for future context enrichment; unused now).
        client: OpenAI-compatible client (OpenRouter).
        model: Model identifier string.

    Returns:
        List of TacticalClassification objects. Empty on failure.
    """
    if not symbols:
        return []

    prompt = build_tactical_classification_prompt(symbols)
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a DDD tactical classification expert for the "
                            "RaiSE codebase. Follow the heuristics exactly and return "
                            "only the JSON array — no markdown, no explanation."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=32768,
            )
            text: str = response.choices[0].message.content or ""
            results = _parse_tactical_response(text)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            results = []

        if results:
            return results

        if attempt < _MAX_ATTEMPTS:
            logger.warning(
                "Tactical classification (%s) attempt %d/%d returned no results%s — retrying",
                model,
                attempt,
                _MAX_ATTEMPTS,
                f" ({last_exc})" if last_exc else "",
            )
            time.sleep(_RETRY_DELAY_S)

    logger.warning(
        "Tactical classification (%s) failed after %d attempts%s",
        model,
        _MAX_ATTEMPTS,
        f": {last_exc}" if last_exc else "",
    )
    return []


def _persist_results(
    backend: Any,
    results: list[TacticalClassification],
    min_confidence: float,
) -> tuple[int, int]:
    """Write tactical classifications to the ddd_tactical annotation namespace.

    Only results with confidence >= min_confidence are written (Design D5).
    Writes to REPO_WIDE so classifications survive graph rebuilds.

    Args:
        backend: Graph backend with upsert_annotations() method.
        results: All classification results from the LLM.
        min_confidence: Minimum confidence threshold for persistence.

    Returns:
        Tuple of (written_count, skipped_count).
    """
    from raise_cli.graph.backends.sqlite import REPO_WIDE  # noqa: PLC0415

    payload: dict[str, dict[str, Any]] = {}
    skipped: int = 0

    for result in results:
        if result.confidence < min_confidence:
            skipped += 1
            continue
        payload[result.symbol_id] = {
            "ddd_tactical_type": str(result.tactical_type),
            "ddd_tactical_confidence": result.confidence,
            "ddd_tactical_rationale": result.rationale,
        }

    written: int = len(payload)
    if payload:
        backend.upsert_annotations("ddd_tactical", payload, checkout_id=REPO_WIDE)

    return written, skipped


def _write_artifact(
    artifact_data: dict[str, Any],
    project_root: Path,
    output: Path | None,
) -> Path:
    """Write the run artifact JSON and return its path.

    Args:
        artifact_data: Full artifact payload dict.
        project_root: Project root directory.
        output: Override path (if None, uses default under project_root).

    Returns:
        Path where the artifact was written.
    """
    if output is not None:
        artifact_path = output
    else:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        artifact_dir = project_root / _ARTIFACT_EPIC_DIR
        artifact_path = artifact_dir / f"ddd-type-{timestamp}.json"

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(artifact_data, indent=2, default=str), encoding="utf-8"
    )
    return artifact_path


def _run_parallel_classification(
    symbol_dicts: list[dict[str, Any]],
    bc_map: dict[str, str],
    model: str,
    api_key: str,
) -> list[TacticalClassification]:
    """Create OpenRouter client and run batched parallel classification.

    Args:
        symbol_dicts: Symbol dicts ready for the prompt builder.
        bc_map: Symbol→BC map passed through to _classify_batch.
        model: OpenRouter model identifier.
        api_key: OPENROUTER_API_KEY value.

    Returns:
        Flat list of all TacticalClassification results.
    """
    import openai  # noqa: PLC0415

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    batches = [
        symbol_dicts[i : i + _BATCH_SIZE]
        for i in range(0, len(symbol_dicts), _BATCH_SIZE)
    ]
    total_batches = len(batches)
    workers = min(_MAX_WORKERS, total_batches) if total_batches > 0 else 1

    print(
        f"  Classifying {len(symbol_dicts)} D-symbols in {total_batches} batches"
        f" ({workers} parallel workers)",
        file=sys.stderr,
        flush=True,
    )

    indexed: list[tuple[int, list[TacticalClassification]]] = []

    def _run_batch(
        idx: int, batch: list[dict[str, Any]]
    ) -> tuple[int, list[TacticalClassification]]:
        batch_results = _classify_batch(batch, bc_map, client, model)
        print(
            f"  Batch {idx + 1}/{total_batches}"
            f" → {len(batch_results)}/{len(batch)} classified",
            file=sys.stderr,
            flush=True,
        )
        return idx, batch_results

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_run_batch, idx, batch): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            indexed.append(future.result())

    indexed.sort(key=lambda t: t[0])
    return [cls for _, batch_results in indexed for cls in batch_results]


def _symbol_to_dict(node: SymbolNode) -> dict[str, Any]:
    """Convert a SymbolNode to the dict format expected by the prompt builder.

    Args:
        node: SymbolNode from the graph.

    Returns:
        Dict with id, kind, signature, module, file, line keys.
    """
    return {
        "id": node.id,
        "kind": str(node.metadata.get("kind", "unknown")),
        "signature": str(node.metadata.get("signature", node.id)),
        "module": str(node.metadata.get("module", "unknown")),
        "file": str(node.metadata.get("file", "")),
        "line": int(node.metadata.get("line", 0)),
    }


def _print_summary_table(report: DddTypeReport) -> None:
    """Print a Rich table summarising the classification run to stdout.

    Args:
        report: Completed DddTypeReport.
    """
    try:
        from rich.console import Console  # noqa: PLC0415
        from rich.table import Table  # noqa: PLC0415
    except ImportError:
        print(
            f"ddd type: {report.classified_count}/{report.d_symbol_count} classified",
            file=sys.stderr,
        )
        return

    console = Console()
    console.print(
        f"\n[green]ddd type[/green]: "
        f"{report.classified_count}/{report.d_symbol_count} classified "
        f"(min_confidence={report.min_confidence}, model={report.model})"
    )

    if report.by_bc:
        table = Table(title="Tactical Types by BC")
        table.add_column("BC", style="cyan")
        table.add_column("tactical_type", style="green")
        table.add_column("count", justify="right")
        table.add_column("avg_confidence", justify="right")

        for bc_name, type_counts in sorted(report.by_bc.items()):
            for ttype, count in sorted(type_counts.items()):
                avg_conf = report.avg_confidence_by_bc_type.get(bc_name, {}).get(
                    ttype, 0.0
                )
                table.add_row(bc_name, ttype, str(count), f"{avg_conf:.2f}")

        console.print(table)

    if report.artifact_path:
        console.print(f"[dim]Artifact: {report.artifact_path}[/dim]")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_ddd_type(
    backend: Any,
    graph: Graph,
    *,
    bc_filter: str | None,
    min_confidence: float,
    force: bool,
    model: str,
    project_root: Path,
    output: Path | None,
) -> DddTypeReport:
    """Run Pass 3 tactical DDD classification.

    Loads D-layer symbols from the graph, classifies each into a tactical DDD
    pattern (Entity, ValueObject, DomainService, DomainEvent, AggregateRoot,
    Factory, RepositoryInterface) using an LLM, and persists results via
    upsert_annotations() in the ``ddd_tactical`` namespace.

    Pre-flight (D3):
        If no D-layer symbols are found and ``force`` is False, exits with an
        error message. Use ``force=True`` to run with 0 symbols (no-op).

    BC source (D2):
        BC assignments are loaded from ``belongs_to`` graph edges (BC-* nodes),
        not from annotations. This is the authoritative post-``assign-bcs`` source.

    Args:
        backend: Active graph backend (must support load_annotations/upsert_annotations).
        graph: Loaded Graph with BC assignment edges.
        bc_filter: If set, classify only symbols assigned to this BC.
        min_confidence: Minimum LLM confidence threshold for persistence (D5).
        force: Bypass pre-flight empty-symbols check.
        model: OpenRouter model identifier (default moonshotai/kimi-k2, D4).
        project_root: Project root for artifact output path.
        output: Override artifact path (None → default under project_root).

    Returns:
        DddTypeReport with classification results and artifact path.
    """
    from raise_cli.cli.error_handler import cli_error  # noqa: PLC0415

    # Step 1: Load D-layer annotations
    d_annots = _load_d_annotations(backend)

    # Step 2: Pre-flight — error if no D symbols and --force not set (D3)
    if not d_annots and not force:
        cli_error(
            "No D-layer symbols found in the graph",
            hint=(
                "Run 'rai graph classify' first to classify symbols into D/I layers, "
                "then 'rai graph assign-bcs' before running 'rai graph ddd type'."
            ),
            exit_code=3,
        )
        # Unreachable — cli_error raises typer.Exit; satisfies pyright
        return DddTypeReport(
            d_symbol_count=0,
            classified_count=0,
            unresolved_count=0,
            bc_filter=bc_filter,
            min_confidence=min_confidence,
            model=model,
            by_bc={},
            avg_confidence_by_bc_type={},
            classifications={},
            artifact_path=Path("/dev/null"),
        )

    # Step 3: Build BC map from graph edges
    bc_map = _load_bc_map(graph)

    # Step 4: Build SymbolNode map
    symbol_map: dict[str, SymbolNode] = {
        n.id: n for n in graph.iter_concepts() if isinstance(n, SymbolNode)
    }

    # Step 5: Intersect D-annotations with graph symbols; apply bc_filter
    target_ids = set(d_annots.keys()) & set(symbol_map.keys())
    stale_count = len(d_annots) - len(target_ids)
    if stale_count > 0:
        logger.debug(
            "%d stale D-annotation IDs absent from graph (skipped)", stale_count
        )

    if bc_filter is not None:
        target_ids = {sid for sid in target_ids if bc_map.get(sid) == bc_filter}
        logger.debug("BC filter '%s' → %d target symbols", bc_filter, len(target_ids))

    # Step 6: Build prompt-compatible symbol dicts
    symbol_dicts = [_symbol_to_dict(symbol_map[sid]) for sid in sorted(target_ids)]

    # Step 7: LLM classification (skip if nothing to classify)
    all_classifications: list[TacticalClassification] = []

    if symbol_dicts:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            cli_error(
                "OPENROUTER_API_KEY environment variable not set",
                hint="Export OPENROUTER_API_KEY before running 'rai graph ddd type'.",
                exit_code=3,
            )
            return DddTypeReport(  # unreachable — cli_error raises typer.Exit
                d_symbol_count=len(d_annots),
                classified_count=0,
                unresolved_count=len(target_ids),
                bc_filter=bc_filter,
                min_confidence=min_confidence,
                model=model,
                by_bc={},
                avg_confidence_by_bc_type={},
                classifications={},
                artifact_path=Path("/dev/null"),
            )

        all_classifications = _run_parallel_classification(
            symbol_dicts, bc_map, model, api_key
        )

    # Step 8: Persist (filter by min_confidence)
    written, skipped = _persist_results(backend, all_classifications, min_confidence)

    # Step 9: Build summary statistics
    classified_map: dict[str, TacticalClassification] = {
        c.symbol_id: c for c in all_classifications if c.confidence >= min_confidence
    }

    by_bc: dict[str, dict[str, int]] = {}
    confidence_sums: dict[str, dict[str, float]] = {}
    confidence_counts: dict[str, dict[str, int]] = {}

    for cls in classified_map.values():
        bc = bc_map.get(cls.symbol_id, "unassigned")
        ttype = str(cls.tactical_type)
        if bc not in by_bc:
            by_bc[bc] = {}
        by_bc[bc][ttype] = by_bc[bc].get(ttype, 0) + 1
        if bc not in confidence_sums:
            confidence_sums[bc] = {}
            confidence_counts[bc] = {}
        confidence_sums[bc][ttype] = (
            confidence_sums[bc].get(ttype, 0.0) + cls.confidence
        )
        confidence_counts[bc][ttype] = confidence_counts[bc].get(ttype, 0) + 1

    avg_confidence_by_bc_type: dict[str, dict[str, float]] = {
        bc: {
            ttype: confidence_sums[bc][ttype] / confidence_counts[bc][ttype]
            for ttype in ttypes
        }
        for bc, ttypes in by_bc.items()
    }

    classifications_payload: dict[str, dict[str, Any]] = {
        cls.symbol_id: {
            "tactical_type": str(cls.tactical_type),
            "confidence": cls.confidence,
            "rationale": cls.rationale,
        }
        for cls in all_classifications
    }

    # Step 10: Write artifact
    unresolved_count = skipped + max(0, len(target_ids) - len(all_classifications))
    artifact_data: dict[str, Any] = {
        "run_at": datetime.now(UTC).isoformat(),
        "story_id": _STORY_ID,
        "d_symbol_count": len(d_annots),
        "classified_count": written,
        "unresolved_count": unresolved_count,
        "bc_filter": bc_filter,
        "min_confidence": min_confidence,
        "model": model,
        "by_bc": by_bc,
        "classifications": classifications_payload,
    }
    artifact_path = _write_artifact(artifact_data, project_root, output)

    report = DddTypeReport(
        d_symbol_count=len(d_annots),
        classified_count=written,
        unresolved_count=unresolved_count,
        bc_filter=bc_filter,
        min_confidence=min_confidence,
        model=model,
        by_bc=by_bc,
        avg_confidence_by_bc_type=avg_confidence_by_bc_type,
        classifications=classifications_payload,
        artifact_path=artifact_path,
    )

    _print_summary_table(report)
    return report
