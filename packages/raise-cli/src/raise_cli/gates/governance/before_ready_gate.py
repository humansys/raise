"""BeforeReadyGate — Initiative profile must be complete before Validated.

Fires at before:initiative:validated. MVP checks:
  (a) initiative_profiles row exists for this initiative key
  (b) required fields populated: components_touched non-empty, change_mode valid, rationale non-empty

Soft checks (activate automatically when portfolio_deps has data):
  (c) no unresolved requires edges (confirmed requires edges whose targets are not in any profile)
  (d) no cycles in confirmed edges (DependencyGraph.toposort())

Opt-in: project.portfolio_gates.enabled in .raise/manifest.yaml
Fail-open: portfolio_gates not configured, no initiative key, or any unexpected error.
Escape hatch: RAISE_BEFORE_READY_SKIP=<reason>
Initiative key resolution: env var RAISE_PORTFOLIO_GATE_INITIATIVE_KEY takes precedence,
falls back to resolve_initiative_key() (branch regex initiative/RAISE-xxx/).

Architecture: RAISE-15208 (S4 of e15198-portfolio-impact-model).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from raise_cli.gates.governance._initiative_context import resolve_initiative_key
from raise_cli.gates.governance._portfolio_config import portfolio_gates_enabled
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.portfolio.storage import VALID_CHANGE_MODES

if TYPE_CHECKING:
    from raise_cli.portfolio.storage import InitiativeProfile, PortfolioStore

_SKIP_ENV = "RAISE_BEFORE_READY_SKIP"
_KEY_ENV = "RAISE_PORTFOLIO_GATE_INITIATIVE_KEY"  # override for dogfood/testing


def _check_required_fields(profile: InitiativeProfile, key: str) -> GateResult | None:
    """Check (b): required fields populated. Returns a failing GateResult or None."""
    errors: list[str] = []
    if not profile.components_touched:
        errors.append(f"{key}: components_touched is empty")
    if profile.change_mode not in VALID_CHANGE_MODES:
        errors.append(
            f"{key}: change_mode {profile.change_mode!r} is not valid "
            f"(must be one of {sorted(VALID_CHANGE_MODES)})"
        )
    if not profile.rationale.strip():
        errors.append(f"{key}: rationale is empty")
    if not errors:
        return None
    return GateResult(
        passed=False,
        gate_id="gate-before-ready",
        message="; ".join(errors),
        details=(f"Escape: {_SKIP_ENV}=<reason>",),
    )


def _collect_soft_warnings(store: PortfolioStore, key: str) -> list[str]:
    """Soft checks (c) and (d): return warning strings; never raise."""
    warnings: list[str] = []

    try:
        deps_from_key = store.list_deps_for(key)
        requires_deps = [d for d in deps_from_key if d.type == "requires"]
        if requires_deps:
            profiled_keys = {p.initiative_key for p in store.list_initiative_profiles()}
            unresolved = sorted(
                d.target for d in requires_deps if d.target not in profiled_keys
            )
            if unresolved:
                warnings.append(
                    f"{key} has unresolved requires edges to: "
                    f"{', '.join(unresolved)} (targets have no profile)"
                )
    except Exception:  # noqa: BLE001, S110
        pass

    try:
        from raise_cli.portfolio.dependency.graph import DependencyGraph

        topo = DependencyGraph(store.list_deps()).toposort()
        if topo.has_cycle:
            warnings.append(
                f"Portfolio has a confirmed dependency cycle "
                f"(portfolio-wide, may not involve {key}): "
                f"{' -> '.join(topo.cycle)}"
            )
    except Exception:  # noqa: BLE001, S110
        pass

    return warnings


class BeforeReadyGate:
    """Deterministic point-bound gate: Initiative profile must be complete.

    Fail-open: portfolio_gates not enabled, no initiative branch context,
    or an adapter error — mirrors every other gate's escape-hatch style.
    Escape hatch: ``RAISE_BEFORE_READY_SKIP=<reason>``.
    """

    gate_id: ClassVar[str] = "gate-before-ready"
    description: ClassVar[str] = "Initiative profile must be complete before Validated"
    workflow_point: ClassVar[str] = "before:initiative:validated"

    def evaluate(self, context: GateContext) -> GateResult:
        """Block Validated when the Initiative profile is missing or incomplete."""
        # 1. opt-in check (fail-open)
        if not portfolio_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="portfolio_gates not configured — skipping",
            )

        # 2. escape hatch
        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        # 3. resolve initiative key (env var > branch regex > fail-open)
        key = os.environ.get(_KEY_ENV, "").strip()
        if not key:
            key = resolve_initiative_key(context.working_dir) or ""
        if not key:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No initiative key detected — before-ready check not applicable",
            )

        # 4-6. open store + hard checks — all wrapped; any error → fail-open
        # Mirrors strategic_fit_gate.py wrapping both adapter init and get_issue.
        from raise_cli.portfolio.storage import PortfolioStore

        try:
            store = PortfolioStore(context.working_dir)

            # 5. check (a): profile must exist
            profile = store.get_initiative_profile(key)
            if profile is None:
                return GateResult(
                    passed=False,
                    gate_id=self.gate_id,
                    message=(
                        f"No profile found for initiative {key}. "
                        "Run 'rai portfolio characterize' to create a profile before "
                        "moving to Validated."
                    ),
                    details=(f"Escape: {_SKIP_ENV}=<reason>",),
                )

            # 6. check (b): required fields populated
            field_error = _check_required_fields(profile, key)
            if field_error is not None:
                return field_error

        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"Could not evaluate portfolio profile for {key}: {exc}. "
                    f"Fail-open — escape hatch: {_SKIP_ENV}=<reason>"
                ),
            )

        # 7 + 8. soft checks (c) and (d): warnings only, never block
        warnings = _collect_soft_warnings(store, key)
        if warnings:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"Initiative {key} profile is complete. Warnings: "
                    + "; ".join(warnings)
                ),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Initiative {key} profile is complete and ready for Validated",
        )
