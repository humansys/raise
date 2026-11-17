"""Parser for SKILL.md files.

Extracts YAML frontmatter and markdown body from skill files,
converting them into structured Skill objects.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.skills.schema import (
    Skill,
    SkillFrontmatter,
    SkillHook,
    SkillHookCommand,
    SkillMetadata,
)


class ParseError(Exception):
    """Error parsing a skill file."""

    pass


# Regex to match YAML frontmatter (--- at start, content, --- to close)
# Handles empty frontmatter (---\n---) and content with or without trailing newline
FRONTMATTER_PATTERN = re.compile(
    r"^---[ \t]*\n(.*?)^---[ \t]*\n?",
    re.DOTALL | re.MULTILINE,
)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and body from markdown content.

    Args:
        content: Raw markdown content with YAML frontmatter.

    Returns:
        Tuple of (frontmatter dict, body string).

    Raises:
        ParseError: If frontmatter is missing, unclosed, or invalid YAML.
    """
    # Check if content starts with ---
    if not content.startswith("---"):
        raise ParseError("No YAML frontmatter found (must start with ---)")

    # Find the closing ---
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        # Check if there's an unclosed frontmatter
        # Look for --- at start of a line (not just anywhere in content)
        lines = content.split("\n")
        closing_markers = sum(1 for line in lines[1:] if line.strip() == "---")
        if closing_markers == 0:
            raise ParseError("Unclosed frontmatter (missing closing ---)")
        raise ParseError("No YAML frontmatter found")

    yaml_content = match.group(1)
    body = content[match.end() :]

    # Parse YAML
    frontmatter: dict[str, Any] = {}
    try:
        raw_yaml = yaml.safe_load(yaml_content)
        if isinstance(raw_yaml, dict):
            frontmatter = cast("dict[str, Any]", raw_yaml)
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML in frontmatter: {e}") from e

    return frontmatter, body


def _parse_hooks(raw_hooks: dict[str, Any] | None) -> dict[str, list[SkillHook]] | None:
    """Parse hooks from raw frontmatter dict."""
    if not raw_hooks:
        return None

    result: dict[str, list[SkillHook]] = {}
    for hook_name, hook_list in raw_hooks.items():
        parsed_hooks: list[SkillHook] = []
        for hook_entry in hook_list:
            commands: list[SkillHookCommand] = []
            for cmd in hook_entry.get("hooks", []):
                commands.append(
                    SkillHookCommand(
                        type=cmd.get("type", "command"),
                        command=cmd.get("command", ""),
                    )
                )
            parsed_hooks.append(SkillHook(hooks=commands))
        result[hook_name] = parsed_hooks

    return result


def _parse_frontmatter_to_model(raw: dict[str, Any]) -> SkillFrontmatter:
    """Convert raw frontmatter dict to SkillFrontmatter model."""
    metadata = None
    if "metadata" in raw and raw["metadata"]:
        metadata = SkillMetadata.from_raw(raw["metadata"])

    hooks = _parse_hooks(raw.get("hooks"))

    return SkillFrontmatter(
        name=raw.get("name", ""),
        description=raw.get("description", ""),
        license=raw.get("license"),
        metadata=metadata,
        hooks=hooks,
    )


def parse_skill(path: str | Path) -> Skill:
    """Parse a SKILL.md file into a Skill object.

    Args:
        path: Path to the SKILL.md file.

    Returns:
        Parsed Skill object.

    Raises:
        ParseError: If file not found or parsing fails.
    """
    path = Path(path)

    if not path.exists():
        raise ParseError(f"Skill file not found: {path}")

    content = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(content)
    frontmatter = _parse_frontmatter_to_model(raw_frontmatter)

    return Skill(
        frontmatter=frontmatter,
        body=body,
        path=str(path),
    )
