"""Impact report assembly from Git diff and project manifest."""

from __future__ import annotations

from pathlib import Path

from raise_cli.impact.git_diff import GitDiffError, collect_changed_files
from raise_cli.impact.models import ImpactReport
from raise_cli.impact.ownership import classify_ownership
from raise_cli.impact.policy import build_policy_report
from raise_cli.impact.recommendations import build_recommendations
from raise_cli.onboarding.manifest import load_manifest


class ImpactReportError(RuntimeError):
    """Raised when an impact report cannot be produced."""


def build_impact_report(
    *,
    base_ref: str,
    head_ref: str | None,
    project_root: Path,
) -> ImpactReport:
    """Build a complete advisory impact report for a project Git diff."""
    root = project_root.resolve()
    manifest = load_manifest(root)
    if manifest is None:
        raise ImpactReportError(
            "manifest could not be loaded from .raise/manifest.yaml"
        )

    try:
        changed_files = collect_changed_files(
            base_ref=base_ref,
            head_ref=head_ref,
            cwd=root,
        )
    except GitDiffError as exc:
        raise ImpactReportError(str(exc)) from exc

    resolved_head = head_ref or "HEAD"
    ownership = classify_ownership(files=changed_files, manifest=manifest)
    report = build_policy_report(
        base_ref=base_ref,
        head_ref=resolved_head,
        changed_files=changed_files,
        ownership=ownership,
    )
    return report.model_copy(
        update={"recommended_gates": build_recommendations(report)}
    )
