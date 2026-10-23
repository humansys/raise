"""TacticalDriftGate — advisory drift check before story close.

Compares current ``ddd_tactical`` annotations in the graph against the
ratified ground-truth YAML (``gt_tactical.yaml``) and emits advisory
warnings for any mismatches.

Gate is NON-BLOCKING (advisory=True) — reclassifications after LLM re-runs
may be improvements, not regressions. Use ``--strict-drift`` if blocking
is required.

Registered via ``pyproject.toml [project.entry-points."rai.gates"]``:
    ddd-tactical-drift = "raise_cli.gates.ddd.tactical_drift_gate:TacticalDriftGate"

RAISE-16918: D5.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, ClassVar

from raise_cli.ddd.tactical_validation import (
    AUTHORITY_SCORES,
    DriftEntry,
    load_gt,
)
from raise_cli.gates.drift._base import DriftGate
from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_GATE_ID = "ddd-tactical-drift"

# GT file discovery — relative to project root (working_dir)
_GT_CANDIDATES = [
    "packages/raise-cli/tests/ddd/gt_tactical.yaml",
    "tests/ddd/gt_tactical.yaml",
]


# ---------------------------------------------------------------------------
# Module-level helpers — extracted so tests can patch them cleanly
# ---------------------------------------------------------------------------


def _discover_gt_path(working_dir: Path) -> Path | None:
    """Search for gt_tactical.yaml relative to *working_dir*.

    Returns the first existing path or ``None`` if not found.
    """
    for rel in _GT_CANDIDATES:
        candidate = working_dir / rel
        if candidate.exists():
            return candidate
    return None


def _load_annotations(working_dir: Path) -> dict[str, dict[str, Any]]:
    """Load ``ddd_tactical`` annotations from the active graph backend.

    Raises any exception if the backend is unavailable — callers handle it.
    """
    from raise_cli.graph.backends import get_active_backend

    backend = get_active_backend(working_dir, explicit_path=False)
    graph = backend.load()
    # Load all annotations keyed by symbol_id
    annotations: dict[str, dict[str, Any]] = {}
    if hasattr(graph, "annotations"):
        raw = graph.annotations  # type: ignore[union-attr]
        annotations = {
            sid: ann
            for sid, ann in raw.items()
            if "ddd_tactical" in ann or any(k.startswith("ddd_tactical") for k in ann)
        }
    # Fallback: try backend.load_annotations if present
    if not annotations and hasattr(backend, "load_annotations"):
        raw_anns: dict[str, Any] = backend.load_annotations("ddd_tactical")  # type: ignore[union-attr]
        for symbol_id, ann in raw_anns.items():
            annotations[symbol_id] = (
                ann if isinstance(ann, dict) else {"ddd_tactical_type": ann}
            )
    return annotations


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


# duplicate_approved: drift-gate — TacticalDriftGate specializes DriftGate for DDD tactical type monitoring; not a duplicate
class TacticalDriftGate(DriftGate):
    """Advisory gate: detect tactical type drift vs ratified GT.

    Wired into the ``before:story:close`` workflow point. Emits advisory
    warnings for any GT symbols whose current annotation differs from the
    ratified expected type. Non-blocking by design.
    """

    gate_id: ClassVar[str] = _GATE_ID
    description: ClassVar[str] = "Detect tactical type regressions vs ratified GT"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run the drift check.

        Args:
            context: Gate evaluation context.  ``context.working_dir`` is used
                as the project root for path resolution.

        Returns:
            - ``skipped=True`` when no backend is available.
            - ``advisory=True`` when drift is detected (still ``passed=True``).
            - Clean pass when no drift.
        """
        working_dir = context.working_dir

        # ------------------------------------------------------------------
        # 1. Load annotations — skip if backend unavailable
        # ------------------------------------------------------------------
        try:
            annotations = _load_annotations(working_dir)
        except Exception as exc:  # noqa: BLE001
            logger.debug("TacticalDriftGate: backend unavailable — %s", exc)
            return GateResult(
                passed=True,
                gate_id=_GATE_ID,
                message="Skipped: graph backend unavailable — run 'rai graph build' first.",
                skipped=True,
            )

        # ------------------------------------------------------------------
        # 2. Discover GT file
        # ------------------------------------------------------------------
        gt_path = _discover_gt_path(working_dir)
        if gt_path is None:
            logger.debug("TacticalDriftGate: gt_tactical.yaml not found — skipping.")
            return GateResult(
                passed=True,
                gate_id=_GATE_ID,
                message="Skipped: gt_tactical.yaml not found (run 'rai ddd validate' to locate).",
                skipped=True,
            )

        # ------------------------------------------------------------------
        # 3. Load GT and compare
        # ------------------------------------------------------------------
        try:
            gt_entries = load_gt(gt_path)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=_GATE_ID,
                message=f"Failed to load gt_tactical.yaml: {exc}",
            )

        drift_entries: list[DriftEntry] = []
        for entry in gt_entries:
            ann = annotations.get(entry.symbol_id)
            if ann is None:
                continue  # symbol not yet classified — not a regression
            current_type = ann.get("ddd_tactical_type") or ann.get(entry.symbol_id)
            if current_type and current_type != entry.expected_type:
                drift_entries.append(
                    DriftEntry(
                        symbol_id=entry.symbol_id,
                        gt_type=entry.expected_type,
                        gt_source=entry.source,
                        current_type=str(current_type),
                        authority_score=AUTHORITY_SCORES.get(entry.source, 0),
                    )
                )

        # ------------------------------------------------------------------
        # 4. Sort by authority score descending (ratified first)
        # ------------------------------------------------------------------
        drift_entries.sort(key=lambda d: d.authority_score, reverse=True)

        if not drift_entries:
            return GateResult(
                passed=True,
                gate_id=_GATE_ID,
                message="No tactical type drift detected.",
            )

        # ------------------------------------------------------------------
        # 5. Advisory result
        # ------------------------------------------------------------------
        detail_lines = tuple(
            f"{d.symbol_id}: expected={d.gt_type} current={d.current_type} "
            f"[source={d.gt_source}, authority={d.authority_score}]"
            for d in drift_entries
        )
        summary = (
            f"{len(drift_entries)} tactical type drift(s) detected "
            f"(advisory — non-blocking). "
            f"Review: entity→value_object and other reclassifications may "
            f"be improvements; update gt_tactical.yaml to ratify."
        )
        # Build a message that contains the first drift's types for test assertions
        first = drift_entries[0]
        msg = (
            f"{len(drift_entries)} drift(s) detected. "
            f"Example: {first.symbol_id} expected={first.gt_type} "
            f"current={first.current_type} [source={first.gt_source}]. "
            f"{summary}"
        )
        return GateResult(
            passed=True,
            gate_id=_GATE_ID,
            message=msg,
            details=detail_lines,
            advisory=True,
        )
