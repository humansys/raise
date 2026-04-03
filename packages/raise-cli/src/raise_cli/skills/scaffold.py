"""Skill scaffolding for creating new skills.

Generates new skill directories with properly structured SKILL.md files
following the RaiSE skill template.
"""

from __future__ import annotations

from textwrap import dedent

from pydantic import BaseModel, Field

from raise_cli.skills.locator import SKILL_MD_FILENAME, get_default_skill_dir

# Mapping from domain prefix to lifecycle
DOMAIN_TO_LIFECYCLE = {
    "session": "session",
    "epic": "epic",
    "story": "story",
    "discover": "discovery",
    "skill": "meta",
    "research": "utility",
    "debug": "utility",
    "framework": "meta",
}


class ScaffoldResult(BaseModel):
    """Result of scaffolding a skill."""

    created: bool = Field(description="Whether the skill was created")
    path: str | None = Field(default=None, description="Path to created skill")
    error: str | None = Field(default=None, description="Error message if failed")


def _infer_lifecycle(name: str) -> str:
    """Infer lifecycle from skill name domain."""
    parts = name.split("-")
    if parts:
        domain = parts[0]
        return DOMAIN_TO_LIFECYCLE.get(domain, "utility")
    return "utility"


def _generate_skill_content(
    name: str,
    lifecycle: str,
    prerequisites: str | None,
    next_skill: str | None,
) -> str:
    """Generate SKILL.md content from template."""
    # Extract title from name (e.g., story-validate -> Story Validate)
    title = " ".join(word.capitalize() for word in name.split("-"))

    # Build prerequisites and next strings
    prereq_str = prerequisites or ""
    next_str = next_skill or ""

    # Determine frequency based on lifecycle
    frequency_map = {
        "session": "per-session",
        "epic": "per-epic",
        "story": "per-story",
        "discovery": "per-project",
        "utility": "on-demand",
        "meta": "on-demand",
    }
    frequency = frequency_map.get(lifecycle, "on-demand")

    content = dedent(f"""\
        ---
        name: {name}
        description: >
          [TODO: Add description of what this skill does]

        license: MIT

        metadata:
          raise.work_cycle: {lifecycle}
          raise.frequency: {frequency}
          raise.fase: ""
          raise.prerequisites: "{prereq_str}"
          raise.next: "{next_str}"
          raise.gate: ""
          raise.adaptable: "true"
          raise.version: "1.0.0"
        ---

        # {title}

        ## Purpose

        [TODO: Describe the purpose of this skill]

        ## Mastery Levels (ShuHaRi)

        - **Shu**: [TODO: Beginner behavior]
        - **Ha**: [TODO: Intermediate behavior]
        - **Ri**: [TODO: Expert behavior]

        ## Context

        **When to use:** [TODO: Add trigger conditions]

        **When to skip:** [TODO: Add skip conditions]

        **Inputs:** [TODO: Add required inputs]

        ## Steps

        ### Step 1: [TODO: Step Name]

        [TODO: Describe what to do in this step]

        ```bash
        # Example command
        ```

        **Verification:** [TODO: How to verify this step succeeded]

        ## Output

        | Item | Destination |
        |------|-------------|
        | [TODO] | [TODO] |

        ## Quality Checklist

        - [ ] [TODO: Add verification items]

        ## References

        - Previous: `/{prereq_str if prereq_str else "[none]"}`
        - Next: `/{next_str if next_str else "[none]"}`
    """)

    return content


def scaffold_skill(
    name: str,
    lifecycle: str | None = None,
    after: str | None = None,
    before: str | None = None,
    skill_set: str | None = None,
    from_builtin: bool = False,
) -> ScaffoldResult:
    """Scaffold a new skill with proper structure.

    When ``skill_set`` is provided, creates the skill in
    ``.raise/skills/{skill_set}/{name}/`` instead of the default
    IDE skill directory. When ``from_builtin`` is also True, copies
    the existing deployed skill as a starting point. (S340.2)

    Args:
        name: Skill name (e.g., 'story-validate').
        lifecycle: Lifecycle category. If not specified, inferred from name.
        after: Skill that should come before this one (prerequisites).
        before: Skill that should come after this one (next).
        skill_set: Skill set name (e.g., 'my-team'). Creates in .raise/skills/{set}/.
        from_builtin: Copy from deployed .claude/skills/{name}/ as starting point.

    Returns:
        ScaffoldResult with creation status and path or error.
    """
    from pathlib import Path

    # Determine target directory
    if skill_set is not None:
        skill_dir = Path.cwd() / ".raise" / "skills" / skill_set
    else:
        skill_dir = get_default_skill_dir()
    if not skill_dir.exists():
        skill_dir.mkdir(parents=True)

    # Check if skill already exists in target
    skill_path = skill_dir / name
    if skill_path.exists():
        return ScaffoldResult(
            created=False,
            error=f"Skill '{name}' already exists at {skill_path}",
        )

    # "Customize builtin" mode: copy from deployed skill
    if from_builtin and skill_set is not None:
        deployed = get_default_skill_dir() / name / SKILL_MD_FILENAME
        if deployed.exists():
            skill_path.mkdir(parents=True, exist_ok=True)
            skill_file = skill_path / SKILL_MD_FILENAME
            skill_file.write_text(
                deployed.read_text(encoding="utf-8"), encoding="utf-8"
            )
            return ScaffoldResult(created=True, path=str(skill_file))
        return ScaffoldResult(
            created=False,
            error=f"Builtin '{name}' not found at {deployed}",
        )

    # Infer lifecycle if not specified
    if lifecycle is None:
        lifecycle = _infer_lifecycle(name)

    # Generate content
    content = _generate_skill_content(name, lifecycle, after, before)

    # Create skill directory and file
    skill_path.mkdir(parents=True, exist_ok=True)
    skill_file = skill_path / SKILL_MD_FILENAME
    skill_file.write_text(content, encoding="utf-8")

    return ScaffoldResult(
        created=True,
        path=str(skill_file),
    )
