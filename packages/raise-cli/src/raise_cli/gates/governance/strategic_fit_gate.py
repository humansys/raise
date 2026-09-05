"""StrategicFitGate — Initiative Theme must be registered before Validated.

S14559.1 (RAISE-14588), design Decision D1: the mechanical half of
"strategic fit" — the Initiative's parent Theme must exist and be
registered in ``governance/portfolio/strategic-themes.md``
(portfolio-model.md §8) — is a deterministic point-bound governance gate
firing at ``before:initiative:validated``. The YAML layer carries the
separate portfolio go/no-go judgment as a HITL gate on the same phase.

Opt-in: skips silently unless ``project.portfolio_gates.enabled`` is True
in ``.raise/manifest.yaml`` (mirrors ``pm_gates``).

Issue-key resolution follows the ``before:bug:close`` precedent
(``close_sync_gate.py``): ``GateContext`` carries no ``issue_id`` field, so
the subject Initiative is resolved from the git branch via
``_initiative_context.resolve_initiative_key`` — shared with
``ChildEpicsCompleteGate`` (T3) rather than cloned (design DR2 mitigation).

Architecture: RAISE-14588, epic RAISE-14559 (Initiative Flow).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.governance._initiative_context import resolve_initiative_key
from raise_cli.gates.governance._portfolio_config import portfolio_gates_enabled
from raise_cli.gates.models import GateContext, GateResult

_SKIP_ENV = "RAISE_STRATEGIC_FIT_SKIP"
_REGISTRY_PATH = Path("governance/portfolio/strategic-themes.md")


def _theme_registered(registry_text: str, key: str) -> bool:
    """True when ``key`` appears as a registered Theme in the registry text.

    Matches the registry's ``## T{n} — {KEY} · {Name}`` line shape (an
    em-dash immediately preceding the key), so a Theme key mentioned only
    incidentally elsewhere in the document (e.g. in an "Initiatives:" list)
    does not count as a registered Theme.
    """
    return re.search(rf"—\s*{re.escape(key)}\b", registry_text) is not None


class StrategicFitGate:
    """Deterministic point-bound gate: Initiative Theme must be registered.

    Fail-open: portfolio_gates not enabled, no initiative branch context,
    or an adapter error — mirrors every other gate's escape-hatch style.
    Escape hatch: ``RAISE_STRATEGIC_FIT_SKIP=<reason>``.
    """

    gate_id: ClassVar[str] = "gate-strategic-fit"
    description: ClassVar[str] = "Initiative Theme must be registered before Validated"
    workflow_point: ClassVar[str] = "before:initiative:validated"

    def evaluate(self, context: GateContext) -> GateResult:
        """Block Validated when the Initiative has no registered Theme parent."""
        if not portfolio_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="portfolio_gates not configured — skipping",
            )

        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        issue_key = resolve_initiative_key(context.working_dir)
        if not issue_key:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No initiative branch context detected — strategic-fit check not applicable",
            )

        from raise_cli.adapters.resolve import resolve_pm_adapter

        try:
            adapter = resolve_pm_adapter(None, context.working_dir)
            issue = adapter.get_issue(issue_key)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"Could not resolve {issue_key} to verify strategic fit: {exc}. "
                    f"Fail-open — escape hatch: {_SKIP_ENV}=<reason>"
                ),
            )

        parent_key = issue.parent_key
        if not parent_key:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Initiative {issue_key} has no parent Theme registered in "
                    f"{_REGISTRY_PATH}. Every Initiative MUST carry exactly one "
                    "registered Theme (portfolio-model.md §8). Set the Jira "
                    "parent to a Theme from the registry, or ratify a new Theme "
                    "in governance first."
                ),
                details=(f"Escape: {_SKIP_ENV}=<reason>",),
            )

        registry_file = context.working_dir / _REGISTRY_PATH
        registry_text = (
            registry_file.read_text(encoding="utf-8") if registry_file.is_file() else ""
        )
        if not _theme_registered(registry_text, parent_key):
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Initiative {issue_key} has parent {parent_key}, which is "
                    f"not a registered Theme in {_REGISTRY_PATH}. Every "
                    "Initiative MUST carry exactly one registered Theme "
                    f"(portfolio-model.md §8). Ratify {parent_key} as a Theme in "
                    "governance first, or re-parent to a registered Theme."
                ),
                details=(f"Escape: {_SKIP_ENV}=<reason>",),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Initiative {issue_key} parent Theme {parent_key} is registered",
        )
