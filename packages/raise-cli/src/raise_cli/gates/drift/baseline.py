"""Drift baseline — freezes existing advisory violations, gates new ones.

RAISE-14280 (S14262.5, ADR-130): advisory drift gates never flip ``passed``
locally (see ``_base.advisory()``) — the ramp is WARN-first, not
block-first, so in-flight sessions do not break under ~4,300 pre-existing
violations surfaced once RAISE-14279 revived the graph-backed guards. The
committed ``governance/drift-baseline.json`` is the frozen snapshot of that
stock: any violation string it lists is "known" and stays advisory even in
``--strict-drift`` mode; anything else is new drift and blocks (CI locus,
ADR-130 — the agent does not control CI).

Fingerprint = the violation string ``advisory()`` already builds (symbol +
module identity per gate, e.g. ``"AG1: <signature> fans out to N modules:
..."`` or ``"<signature> [<module>]"``). No line numbers are involved, so a
reformat/reflow of a file does not drift the baseline — only a genuine
symbol/module change does. See ``scripts/generate_drift_baseline.py`` for
how the baseline file is (re)generated.
"""

from __future__ import annotations

import dataclasses
import json
import logging
from collections.abc import Mapping
from pathlib import Path

from raise_cli.gates.models import GateResult

logger = logging.getLogger(__name__)

BASELINE_REL_PATH = Path("governance") / "drift-baseline.json"

Baseline = Mapping[str, frozenset[str]]


def load_baseline(working_dir: Path) -> Baseline:
    """Load the committed drift baseline, or an empty one if absent/corrupt.

    Fail-loud, not fail-open: an absent or malformed baseline means every
    live advisory violation is treated as "new" under ``--strict-drift`` —
    it does NOT silently disable strict mode. A missing committed baseline
    in CI is a real config error and should surface as gate failures, not
    pass quietly.
    """
    path = working_dir / BASELINE_REL_PATH
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        violations = raw.get("violations", {})
        return {
            gate_id: frozenset(fingerprints)
            for gate_id, fingerprints in violations.items()
        }
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        logger.warning(
            "drift baseline unreadable at %s (%s) — treating as empty; "
            "every live advisory violation counts as NEW under --strict-drift",
            path,
            exc,
        )
        return {}


def apply_strict_drift(result: GateResult, baseline: Baseline) -> GateResult:
    """Turn a non-baselined advisory violation into a hard failure.

    No-op for non-advisory results and for advisory results with no current
    violations (``result.details`` empty means ``advisory()`` returned the
    clean-pass branch). Violations present in the baseline for this
    ``gate_id`` stay advisory/non-blocking; anything else flips ``passed``
    to False so ``rai gate check --strict-drift`` exits 1 (RAISE-14280).
    """
    if not result.advisory or not result.details:
        return result

    known = baseline.get(result.gate_id, frozenset())
    new_violations = [d for d in result.details if d not in known]

    if not new_violations:
        return result

    baselined_count = len(result.details) - len(new_violations)
    message = (
        f"⚠ DRIFT: {len(new_violations)} NEW violation(s) not in baseline "
        f"({baselined_count} known — frozen in {BASELINE_REL_PATH})"
    )
    logger.warning("%s: %s", result.gate_id, message)
    return dataclasses.replace(result, passed=False, message=message)
