"""SuppressionRatchetGate — F3 blocking total-suppression ratchet (RAISE-15491).

Counts ``noqa`` + ``type: ignore`` suppression comments across production
source (``packages/*/src/**/*.py``) and fails when the count exceeds a
persisted baseline plus a configurable delta. Bootstraps on first run.

Distinct from the advisory ``drift-linter-suppression`` gate, which only
detects ``noqa: C901`` *clustering*. This gate bounds TOTAL suppression
growth so sessions cannot escape gate failures by accumulating suppressions.

The counter is line-based (design D4), so these docstrings deliberately omit
the literal ``#`` prefix — a gate must not count its own documentation as a
suppression.

Reuses ``scoped_rglob`` + ``is_excluded`` from ``gates.drift._base`` rather
than reimplementing the file walk (RAISE-15491 AC8 / drift risk AG2).

Architecture: ADR-039 §5 (Built-in gates).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.drift._base import is_excluded, scoped_rglob
from raise_cli.gates.models import GateContext, GateResult

# A line carrying either marker counts once (a line with both counts once too).
_SUPPRESSION_RE = re.compile(r"#\s*noqa|#\s*type:\s*ignore")
_BASELINE_REL = Path(".raise") / "suppression-baseline.txt"
_MANIFEST_REL = Path(".raise") / "manifest.yaml"
_DELTA_KEY = "suppression_ratchet_delta"
_DEFAULT_DELTA = 2


def _count_suppressions(working_dir: Path) -> int:
    """Count suppression-marker lines across ``packages/*/src`` .py files.

    Scoped to production source (matches ``code.root_glob``) so conformance-test
    fixtures that embed literal ``noqa`` strings are not counted.
    """
    count = 0
    for pkg_src in sorted(working_dir.glob("packages/*/src")):
        if not pkg_src.is_dir():
            continue
        for path in scoped_rglob(pkg_src, "*.py", None):
            if is_excluded(path, pkg_src):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                if _SUPPRESSION_RE.search(line):
                    count += 1
    return count


def _read_delta(working_dir: Path) -> int:
    """Read ``suppression_ratchet_delta`` from the raw manifest; default 2.

    Uses ``yaml.safe_load`` directly (per design D5) to avoid touching the
    ``ProjectInfo`` pydantic model for a single optional integer.
    """
    manifest_path = working_dir / _MANIFEST_REL
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except OSError:
        return _DEFAULT_DELTA
    if not isinstance(data, dict):
        return _DEFAULT_DELTA
    try:
        return int(data.get(_DELTA_KEY, _DEFAULT_DELTA))
    except (TypeError, ValueError):
        return _DEFAULT_DELTA


class SuppressionRatchetGate:
    """Blocking gate: total suppressions must stay within ``baseline + delta``.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "suppression-ratchet"
    description: ClassVar[str] = "Suppression count within ratchet"
    workflow_point: ClassVar[str] = "before:release:publish"
    is_blocker: ClassVar[bool] = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Count suppressions, compare to baseline+delta, bootstrap on absent."""
        working_dir = context.working_dir
        count = _count_suppressions(working_dir)
        baseline_path = working_dir / _BASELINE_REL
        if not baseline_path.exists():
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            baseline_path.write_text(f"{count}\n", encoding="utf-8")
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Baseline bootstrapped: {count}",
            )
        baseline = int(baseline_path.read_text(encoding="utf-8").strip())
        threshold = baseline + _read_delta(working_dir)
        if count > threshold:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Suppression count {count} exceeds ratchet threshold "
                    f"{threshold}. Remove suppressions or justify each with a "
                    "comment."
                ),
            )
        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Suppressions {count} <= {threshold}",
        )
