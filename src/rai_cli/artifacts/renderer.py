"""Render typed artifacts to human-readable Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from rai_cli.artifacts.models import SkillArtifact
from rai_cli.artifacts.story_design import (
    StoryDesignArtifact,
    StoryDesignContent,
)
from rai_cli.artifacts.writer import _artifact_filename


def _render_acceptance_criteria(content: StoryDesignContent) -> str:
    """Render AC as a numbered list."""
    lines = []
    for i, ac in enumerate(content.acceptance_criteria, 1):
        lines.append(f"{i}. [{ac.id}] {ac.description}")
    return "\n".join(lines)


def _render_integration_points(content: StoryDesignContent) -> str:
    """Render integration points as bullet list."""
    if not content.integration_points:
        return ""
    lines = []
    for ip in content.integration_points:
        files = ", ".join(f"`{f}`" for f in ip.files) if ip.files else ""
        line = f"- `{ip.module}` — {ip.change_type}"
        if files:
            line += f": {files}"
        lines.append(line)
    return "\n".join(lines)


def _render_decisions(content: StoryDesignContent) -> str:
    """Render decisions with rationale and alternatives."""
    if not content.decisions:
        return ""
    blocks = []
    for d in content.decisions:
        block = f"### {d.id}: {d.choice}\n"
        block += f"**Rationale:** {d.rationale}\n"
        if d.alternatives_considered:
            alts = ", ".join(d.alternatives_considered)
            block += f"**Alternatives:** {alts}"
        blocks.append(block)
    return "\n\n".join(blocks)


def _remove_empty_sections(md: str) -> str:
    """Remove sections whose placeholder was empty."""
    # Match ## heading followed by only whitespace until next ## or end
    return re.sub(r"\n## [^\n]+\n\n\s*(?=\n##|\Z)", "", md)


def _get_template(project_root: Path | None = None) -> str:
    """Load the story-design template."""
    if project_root:
        template_path = (
            project_root / ".raise" / "templates" / "artifacts" / "story-design.md"
        )
        if template_path.exists():
            return template_path.read_text()

    # Fallback: inline default
    return (
        "# {story} Design: {summary}\n\n"
        "**Story:** {story} | **Epic:** {epic} | **Complexity:** {complexity}\n"
        "**Skill:** {skill} | **Created:** {created}\n\n"
        "## Summary\n\n{summary}\n\n"
        "## Acceptance Criteria\n\n{acceptance_criteria}\n\n"
        "## Integration Points\n\n{integration_points}\n\n"
        "## Decisions\n\n{decisions}\n"
    )


def render_artifact(
    artifact: SkillArtifact, project_root: Path | None = None
) -> str:
    """Render a typed artifact to Markdown.

    Uses the template from ``.raise/templates/artifacts/`` if available,
    falls back to a built-in default.
    """
    if not isinstance(artifact, StoryDesignArtifact):
        # Fallback for non-story-design artifacts
        return f"# Artifact: {artifact.artifact_type}\n\n{artifact.content}\n"

    content = artifact.content
    template = _get_template(project_root)

    md = template.format(
        story=artifact.story or "—",
        epic=artifact.epic or "—",
        summary=content.summary,
        complexity=content.complexity.value,
        skill=artifact.skill,
        created=artifact.created.strftime("%Y-%m-%d"),
        acceptance_criteria=_render_acceptance_criteria(content),
        integration_points=_render_integration_points(content),
        decisions=_render_decisions(content),
    )

    return _remove_empty_sections(md)


def write_doc(artifact: SkillArtifact, project_root: Path) -> Path:
    """Write rendered Markdown to ``work/docs/``.

    Returns:
        Path to the written Markdown file.
    """
    docs_dir = project_root / "work" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Same naming as YAML but with .md extension
    yaml_name = _artifact_filename(artifact)
    md_name = yaml_name.replace(".yaml", ".md")
    path = docs_dir / md_name

    path.write_text(render_artifact(artifact, project_root))
    return path
