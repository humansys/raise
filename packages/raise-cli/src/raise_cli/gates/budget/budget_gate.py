"""BudgetCapGate — blocks when story cost exceeds declared budget cap (S8741.3).

Cap priority (first defined wins):
  1. RAISE_BUDGET_CAP_USD env var  (Jira field or any external override)
  2. fleet.budget_cap_usd in .raise/manifest.yaml
  3. None → fail-open (gate passes)

Cost source: most-recently-modified JSONL in ~/.claude/projects/ for this
working_dir, scanned via scan_single_session(). Fail-open when JSONL absent.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.telemetry.cost_report import CostReport, scan_single_session
from raise_cli.telemetry.session_tokens import find_current_session_jsonl

logger = logging.getLogger(__name__)

_MANIFEST_RELPATH = Path(".raise") / "manifest.yaml"
_ENV_KEY = "RAISE_BUDGET_CAP_USD"


def _read_manifest_cap(working_dir: Path) -> float | None:
    """Return fleet.budget_cap_usd from manifest, or None if absent/invalid."""
    manifest_path = working_dir / _MANIFEST_RELPATH
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        cap = data.get("fleet", {}).get("budget_cap_usd")
        if cap is None:
            return None
        return float(cap)
    except Exception:  # noqa: BLE001
        return None


def _read_cap(working_dir: Path) -> float | None:
    """Resolve effective budget cap: env var → manifest → None."""
    env_val = os.environ.get(_ENV_KEY)
    if env_val is not None:
        try:
            return float(env_val)
        except ValueError:
            logger.debug(
                "RAISE_BUDGET_CAP_USD='%s' is not a valid float — ignoring", env_val
            )

    return _read_manifest_cap(working_dir)


def _read_cost(working_dir: Path) -> float | None:
    """Return total_cost_usd from the current session JSONL, or None if unavailable."""
    try:
        jsonl = find_current_session_jsonl(working_dir)
        if jsonl is None:
            return None
        report: CostReport = scan_single_session(jsonl)
        return report.total_cost_usd
    except Exception:  # noqa: BLE001
        logger.debug("BudgetCapGate: cost scan failed — fail-open", exc_info=True)
        return None


class BudgetCapGate:
    """Gate that blocks when story cost exceeds the declared budget cap.

    Fail-open: when no cap is configured or cost data is unavailable, the gate
    always passes. This prevents CI/CD from being blocked by missing config.
    """

    gate_id: ClassVar[str] = "gate-budget"
    description: ClassVar[str] = "Story cost within declared budget cap"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Evaluate budget cap gate for the current story session."""
        cap = _read_cap(context.working_dir)
        if cap is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No budget cap configured — gate skipped",
            )

        cost = _read_cost(context.working_dir)
        if cost is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="Cost data unavailable — gate skipped (fail-open)",
            )

        if cost > cap:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Cost ${cost:.2f} exceeds budget cap ${cap:.2f}",
                details=(
                    f"Actual: ${cost:.4f}",
                    f"Cap:    ${cap:.4f}",
                    f"Source: {_ENV_KEY if os.environ.get(_ENV_KEY) else 'manifest fleet.budget_cap_usd'}",
                ),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Cost ${cost:.2f} within cap ${cap:.2f}",
        )
