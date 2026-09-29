"""Deterministic rendering for impact reports."""

from __future__ import annotations

import json

from raise_cli.impact.models import FullRunReason, ImpactReport
from raise_cli.impact.recommendations import render_gate_command


def render_report_json(report: ImpactReport) -> str:
    """Render an impact report as deterministic JSON."""
    return json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True)


def _format_reason(reason: FullRunReason) -> str:
    paths = f" ({', '.join(reason.paths)})" if reason.paths else ""
    return f"{reason.code}: {reason.message}{paths}"


def render_report_human(report: ImpactReport) -> str:
    """Render an impact report as deterministic human-readable text."""
    lines = [
        "Impact report",
        f"Base: {report.base_ref}",
        f"Head: {report.head_ref}",
        f"Confidence: {report.confidence}",
        "",
        "Changed files",
    ]

    if report.changed_files:
        for item in report.changed_files:
            owner = item.owner_app or "unknown"
            lines.append(f"- {item.path} [{item.category}] owner={owner}")
    else:
        lines.append("- No changed files found")

    lines.extend(["", "Affected apps"])
    if report.affected_apps:
        for app in report.affected_apps:
            inferred = " inferred" if app.inferred else ""
            lines.append(f"- {app.name} ({app.path}){inferred}")
    else:
        lines.append("- none")

    lines.extend(["", "Recommended commands"])
    if report.recommended_gates:
        for gate in report.recommended_gates:
            lines.append(f"- {render_gate_command(gate)}")
    else:
        lines.append("- none")

    lines.extend(["", "Full-run reasons"])
    if report.full_run_reasons:
        for reason in report.full_run_reasons:
            lines.append(f"- {_format_reason(reason)}")
    else:
        lines.append("- none")

    return "\n".join(lines)
