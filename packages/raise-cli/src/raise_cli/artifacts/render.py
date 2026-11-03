"""Generate Markdown from structured artifact content.

Output is disposable — the SQLite artifact is the source of truth.
"""

from __future__ import annotations

from typing import Any

from raise_cli.artifacts.models import (
    ArtifactBase,
    DesignArtifact,
    ImplementArtifact,
    PlanArtifact,
    RetroArtifact,
    ReviewArtifact,
)


def render_artifact(artifact: ArtifactBase) -> str:
    """Render an artifact to human-readable Markdown."""
    if isinstance(artifact, DesignArtifact):
        return _render_design(artifact)
    if isinstance(artifact, PlanArtifact):
        return _render_plan(artifact)
    if isinstance(artifact, ImplementArtifact):
        return _render_implement(artifact)
    if isinstance(artifact, ReviewArtifact):
        return _render_review(artifact)
    if isinstance(artifact, RetroArtifact):
        return _render_retro(artifact)
    return f"# Artifact (schema_version={artifact.schema_version})\n\nNo renderer available."


def _render_design(d: DesignArtifact) -> str:
    lines: list[str] = ["# Design\n"]
    if d.complexity:
        lines.append(f"**Complexity:** {d.complexity}\n")
    lines.extend([f"## Problem\n\n{d.problem}\n", f"## Value\n\n{d.value}\n"])
    lines.append(f"## Approach\n\n{d.approach}\n")
    _render_design_components(d, lines)
    _render_design_decisions(d, lines)
    _render_design_examples(d, lines)
    _render_design_ac(d, lines)
    _render_design_deps(d, lines)
    if d.legacy_sweep:
        lines.append(f"## Legacy Sweep\n\n{d.legacy_sweep}\n")
    _render_design_drift(d, lines)
    _render_design_testing(d, lines)
    _render_design_questions(d, lines)
    return "\n".join(lines)


def _render_design_components(d: DesignArtifact, lines: list[str]) -> None:
    if not d.components:
        return
    lines.append("## Components\n")
    lines.append("| Name | Change | Purpose |")
    lines.append("|------|--------|---------|")
    for c in d.components:
        lines.append(f"| {c.name} | {c.change} | {c.purpose} |")
    lines.append("")


def _render_design_decisions(d: DesignArtifact, lines: list[str]) -> None:
    if not d.decisions:
        return
    lines.append("## Decisions\n")
    for dec in d.decisions:
        lines.append(f"- **{dec.id}: {dec.title}** — {dec.rationale}")
        if dec.body:
            lines.append(f"\n  {dec.body}\n")
    lines.append("")


def _render_design_examples(d: DesignArtifact, lines: list[str]) -> None:
    if not d.examples:
        return
    lines.append("## Examples\n")
    for ex in d.examples:
        lines.append(f"### {ex.title}\n")
        lines.append(f"```{ex.language}")
        lines.append(ex.code)
        lines.append("```\n")
        if ex.explanation:
            lines.append(f"{ex.explanation}\n")


def _render_design_ac(d: DesignArtifact, lines: list[str]) -> None:
    if not d.acceptance_criteria:
        return
    lines.append("## Acceptance Criteria\n")
    buckets: dict[str, list[tuple[str, str, bool]]] = {
        "must": [],
        "should": [],
        "must_not": [],
    }
    for ac in d.acceptance_criteria:
        buckets[ac.severity].append((ac.id, ac.description, ac.verifiable))
    has_multiple_severities = sum(1 for v in buckets.values() if v) > 1
    for severity, label in [
        ("must", "MUST"),
        ("should", "SHOULD"),
        ("must_not", "MUST NOT"),
    ]:
        if buckets[severity]:
            if has_multiple_severities:
                lines.append(f"### {label}\n")
            for ac_id, desc, verifiable in buckets[severity]:
                check = "x" if not verifiable else " "
                lines.append(f"- [{check}] {ac_id}: {desc}")
            lines.append("")


def _render_design_deps(d: DesignArtifact, lines: list[str]) -> None:
    if not d.dependencies:
        return
    lines.append("## Dependencies\n")
    for dep in d.dependencies:
        line = f"- {dep.description}"
        if dep.blocks:
            line += f" (blocks: {dep.blocks})"
        lines.append(line)
    lines.append("")


def _render_design_drift(d: DesignArtifact, lines: list[str]) -> None:
    if not d.drift_risks:
        return
    lines.append("## Drift Risk\n")
    for dr in d.drift_risks:
        line = f"- **{dr.id}:** {dr.description}"
        if dr.mitigation:
            line += f" — {dr.mitigation}"
        lines.append(line)
    lines.append("")


def _render_design_testing(d: DesignArtifact, lines: list[str]) -> None:
    if not d.testing_strategy:
        return
    lines.append("## Testing Strategy\n")
    lines.append("| Layer | Test | Purpose |")
    lines.append("|-------|------|---------|")
    for ts in d.testing_strategy:
        lines.append(f"| {ts.layer} | {ts.name} | {ts.purpose} |")
    lines.append("")


def _render_design_questions(d: DesignArtifact, lines: list[str]) -> None:
    if not d.open_questions:
        return
    lines.append("## Open Questions\n")
    for q in d.open_questions:
        lines.append(f"- {q}")
    lines.append("")


def _render_plan(p: PlanArtifact) -> str:
    lines = ["# Plan\n"]
    if p.estimated_points is not None:
        lines.append(f"**Estimated:** {p.estimated_points} SP\n")
    if p.tasks:
        lines.append("## Tasks\n")
        lines.append("| # | Description | Size |")
        lines.append("|---|-------------|------|")
        for t in p.tasks:
            lines.append(
                f"| {t.get('id', '?')} | {t.get('description', '')} | {t.get('size', '')} |"
            )
        lines.append("")
    if p.risk_order:
        lines.append(f"**Risk order:** {' → '.join(p.risk_order)}\n")
    return "\n".join(lines)


def _render_implement(impl: ImplementArtifact) -> str:
    lines = ["# Implementation\n"]
    if impl.coverage_percent is not None:
        lines.append(f"**Coverage:** {impl.coverage_percent}%\n")
    if impl.files_changed:
        lines.append("## Files Changed\n")
        for f in impl.files_changed:
            lines.append(f"- {f}")
        lines.append("")
    if impl.tests_added:
        lines.append("## Tests Added\n")
        for t in impl.tests_added:
            lines.append(f"- {t}")
        lines.append("")
    return "\n".join(lines)


def _render_review(r: ReviewArtifact) -> str:
    lines = [f"# {r.review_type.title()} Review\n", f"**Verdict:** {r.verdict}\n"]
    if r.findings:
        lines.append("## Findings\n")
        for i, f in enumerate(r.findings, 1):
            lines.append(f"{i}. {_format_finding(f)}")
        lines.append("")
    return "\n".join(lines)


def _format_finding(f: dict[str, Any]) -> str:
    parts = []
    if "issue" in f:
        parts.append(f["issue"])
    if "severity" in f:
        parts.append(f"(severity: {f['severity']})")
    return " ".join(parts) if parts else str(f)


def _render_retro(r: RetroArtifact) -> str:
    lines = ["# Retrospective\n"]
    if r.velocity_ratio is not None:
        lines.append(f"**Velocity ratio:** {r.velocity_ratio}x\n")
    if r.patterns_learned:
        lines.append("## Patterns Learned\n")
        for p in r.patterns_learned:
            lines.append(f"- {p}")
        lines.append("")
    if r.reinforcements:
        lines.append("## Reinforcements\n")
        for p in r.reinforcements:
            lines.append(f"- {p}")
        lines.append("")
    if r.notes:
        lines.append(f"## Notes\n\n{r.notes}\n")
    return "\n".join(lines)
