"""Prompt resolution for LLM pipeline phases.

Resolves a PhaseDefinition's prompt source — either a direct prompt string
or a skill reference (reads SKILL.md content).  When a PipelineRun is
provided alongside a skill, appends a structured context block with story
metadata and prior artifacts (S1065.2).

Story: S1064.4 T3 — Prompt Resolution
Extended: S1065.2 — Pipeline-Skill Invocation Contract
Epic: E1064 / E1065

Design decision D5: read full SKILL.md content, no frontmatter parsing.
Design decision D7: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import logging
from pathlib import Path

from raise_core.workflow.models import PhaseDefinition, PipelineRun

logger = logging.getLogger(__name__)


def resolve_prompt(
    phase: PhaseDefinition,
    skill_base: Path | None = None,
    pipeline_run: PipelineRun | None = None,
) -> str:
    """Resolve the prompt for an LLM phase.

    When ``pipeline_run`` is provided and the phase references a skill,
    appends a context block with story ID, prior artifacts, worktree
    path, and run metadata.

    Args:
        phase: Phase definition with ``prompt`` or ``skill`` set.
        skill_base: Base directory containing skill directories.
            Each skill is a subdirectory with a ``SKILL.md`` file.
            If None, uses a default path relative to the project.
        pipeline_run: Optional pipeline run for context injection.
            When provided alongside a skill phase, a structured context
            block is appended after the SKILL.md content.

    Returns:
        The resolved prompt string.

    Raises:
        ValueError: If neither ``prompt`` nor ``skill`` is set,
            or if the skill file cannot be found.
    """
    if phase.prompt is not None:
        return phase.prompt

    if phase.skill is not None:
        skill_content = _load_skill_prompt(phase.skill, skill_base)
        if pipeline_run is not None:
            context_block = _build_context_block(pipeline_run)
            return f"{skill_content}\n\n{context_block}"
        return skill_content

    msg = "No prompt configured: set 'prompt' or 'skill' on the phase definition"
    raise ValueError(msg)


def _load_skill_prompt(skill_name: str, skill_base: Path | None) -> str:
    """Load SKILL.md content for a named skill."""
    if skill_base is None:
        msg = f"Cannot resolve skill '{skill_name}': no skill_base path provided"
        raise ValueError(msg)

    skill_path = skill_base / skill_name / "SKILL.md"
    if not skill_path.is_file():
        msg = f"Skill file not found: {skill_path}"
        raise FileNotFoundError(msg)

    content = skill_path.read_text(encoding="utf-8")
    logger.debug("Loaded skill prompt from %s (%d chars)", skill_path, len(content))
    return content


# ─── S1065.2: Context block builder + artifact discovery ────────────────────


def _build_context_block(run: PipelineRun) -> str:
    """Build the story context block from pipeline run metadata.

    Returns a markdown section with story ID, epic path, worktree,
    run ID, prior artifacts, and an ARGUMENTS line for skill parsing.
    """
    lines: list[str] = ["## Story Context"]

    if run.issue_id is not None:
        lines.append(f"- Story ID: {run.issue_id}")

    epic_path = _find_epic_path(run)
    if epic_path is not None:
        lines.append(f"- Epic path: {epic_path}")

    if run.worktree_path is not None:
        lines.append(f"- Worktree: {run.worktree_path}")

    lines.append(f"- Run ID: {run.run_id}")

    artifacts = _discover_prior_artifacts(run)
    if artifacts:
        lines.append(f"- Prior artifacts: {', '.join(artifacts)}")
    else:
        lines.append("- Prior artifacts: (none)")

    if run.issue_id is not None:
        lines.append(f"\nARGUMENTS: {run.issue_id}")

    return "\n".join(lines)


def _discover_prior_artifacts(run: PipelineRun) -> list[str]:
    """Find existing artifacts for the current story on disk.

    Scans the stories directory for files matching the pattern
    ``{issue_id}-*.md`` (case-insensitive on the story prefix).

    Returns:
        Sorted list of filenames (not full paths).
    """
    if run.issue_id is None:
        return []

    stories_dir = _find_stories_dir(run)
    if stories_dir is None or not stories_dir.is_dir():
        return []

    prefix = f"{run.issue_id.lower()}-"
    artifacts = sorted(
        f.name
        for f in stories_dir.iterdir()
        if f.is_file() and f.name.lower().startswith(prefix)
    )
    return artifacts


def _find_stories_dir(run: PipelineRun) -> Path | None:
    """Locate the stories directory for this run.

    Convention: if worktree_path exists, look for
    ``work/epics/e{epic_num}-*/stories/`` using the epic number
    derived from the issue_id prefix (e.g. S1065.2 -> e1065).

    Returns None on ambiguity (D5 fail-safe).
    """
    if run.worktree_path is None:
        return None

    issue_id = run.issue_id
    if issue_id is None:
        return None

    parts = issue_id.lstrip("Ss").split(".")
    if not parts:
        return None
    epic_num = parts[0]

    epic_pattern = f"e{epic_num}-*"
    epics_base = run.worktree_path / "work" / "epics"
    if not epics_base.is_dir():
        return None

    matches = list(epics_base.glob(epic_pattern))
    if len(matches) == 1:
        stories_dir = matches[0] / "stories"
        if stories_dir.is_dir():
            return stories_dir

    return None


def _find_epic_path(run: PipelineRun) -> str | None:
    """Derive the epic path relative to the worktree root.

    Returns:
        Relative path string like ``work/epics/e1065-dev-lifecycle``,
        or None if the stories directory cannot be located.
    """
    stories_dir = _find_stories_dir(run)
    if stories_dir is None:
        return None

    epic_dir = stories_dir.parent
    if run.worktree_path is not None:
        try:
            return str(epic_dir.relative_to(run.worktree_path))
        except ValueError:
            pass
    return str(epic_dir)
