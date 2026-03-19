"""Scaffold workflow shims for IDEs that support workflows.

Generates one workflow file per distributable skill.
Each workflow is a minimal .md with YAML frontmatter (name + description)
and a one-line body referencing the skill.

IDEs without workflows (e.g., Claude Code) get a no-op.
Per-file idempotency: existing files are never overwritten.
"""

from __future__ import annotations

import logging
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.config.agents import AgentConfig, get_agent_config
from raise_cli.skills.parser import parse_frontmatter

logger = logging.getLogger(__name__)


class WorkflowScaffoldResult(BaseModel):
    """Result of workflow scaffolding operation."""

    workflows_created: int = 0
    already_existed: bool = False
    skipped_no_workflows_dir: bool = False
    files_created: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)


def scaffold_workflows(
    project_root: Path,
    *,
    agent_config: AgentConfig | None = None,
) -> WorkflowScaffoldResult:
    """Generate workflow shim files for each distributable skill.

    Reads each skill's SKILL.md frontmatter (name + description)
    and writes a minimal workflow file that references the skill.
    Skips when the IDE has no workflows_dir (e.g., Claude Code).

    Args:
        project_root: Project root directory.
        agent_config: Agent configuration. Defaults to Claude.

    Returns:
        WorkflowScaffoldResult with details of what was created or skipped.
    """
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    config = agent_config or get_agent_config()
    result = WorkflowScaffoldResult()

    if config.workflows_dir is None:
        result.skipped_no_workflows_dir = True
        return result

    base = files("raise_cli.skills_base")
    workflows_dir = project_root / config.workflows_dir
    workflows_dir.mkdir(parents=True, exist_ok=True)

    for skill_name in DISTRIBUTABLE_SKILLS:
        workflow_file = workflows_dir / f"{skill_name}.md"

        if workflow_file.exists():
            result.files_skipped.append(skill_name)
            logger.debug("Skipped (exists): %s", workflow_file)
            continue

        # Read skill frontmatter for name + description
        skill_md = base / skill_name / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(content)

        name = frontmatter.get("name", skill_name)
        description = frontmatter.get("description", "")

        # Write workflow shim
        skills_path = f"{config.skills_dir}/{skill_name}/SKILL.md"
        workflow_content = (
            f"---\nname: {name}\n"
            f"description: >\n"
            f"  {description.strip()}\n"
            f"---\n\n"
            f"Run the `{skill_name}` skill from `{skills_path}`.\n"
        )

        workflow_file.write_text(workflow_content, encoding="utf-8")
        result.files_created.append(str(workflow_file))
        result.workflows_created += 1
        logger.debug("Created: %s", workflow_file)

    result.already_existed = (
        result.workflows_created == 0 and len(result.files_skipped) > 0
    )

    return result
