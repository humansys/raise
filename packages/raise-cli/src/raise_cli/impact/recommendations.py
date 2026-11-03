"""Validation gate recommendations for impact reports."""

from __future__ import annotations

from raise_cli.impact.models import GateId, ImpactReport, RecommendedGate

DEFAULT_GATE_ORDER: tuple[GateId, ...] = (
    "gate-tests",
    "gate-lint",
    "gate-format",
    "gate-types",
)


def build_recommendations(report: ImpactReport) -> list[RecommendedGate]:
    """Build deterministic validation recommendations for an impact report."""
    if not report.changed_files and not report.affected_apps:
        return []

    if report.full_run_reasons:
        reason_codes = ",".join(reason.code for reason in report.full_run_reasons)
        reason = f"broadened by {reason_codes}"
        return [
            RecommendedGate(gate_id=gate_id, scope="repo", reason=reason)
            for gate_id in DEFAULT_GATE_ORDER
        ]

    recommendations: list[RecommendedGate] = []
    for app in sorted(report.affected_apps, key=lambda item: (item.name, item.path)):
        reason = f"{app.name} changed with {report.confidence} confidence"
        recommendations.extend(
            RecommendedGate(
                gate_id=gate_id,
                scope="app",
                path=app.path,
                reason=reason,
            )
            for gate_id in DEFAULT_GATE_ORDER
        )
    return recommendations


def render_gate_command(gate: RecommendedGate) -> str:
    """Render a recommended gate as an executable RaiSE command."""
    command = f"rai gate check {gate.gate_id}"
    if gate.path:
        command += f" --scope {gate.path}"
    return command
