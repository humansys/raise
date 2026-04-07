#!/usr/bin/env python3
"""Sync public skills from .claude/skills/ to src/raise_cli/skills_base/

This script filters skills by visibility metadata and syncs only public skills
to the distribution package. Internal skills (rai-framework-sync, rai-publish)
remain available for framework development but are excluded from PyPI distribution.

Usage:
    python scripts/sync-skills.py [--dry-run]

The script:
1. Reads all skills from .claude/skills/
2. Parses YAML frontmatter to extract raise.visibility
3. Filters to only visibility: public skills
4. Syncs SKILL.md files to src/raise_cli/skills_base/
5. Updates DISTRIBUTABLE_SKILLS list in __init__.py

Exit codes:
    0: Success
    1: Error (missing directories, parse failures, no public skills found)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from SKILL.md.

    Args:
        skill_md: Path to SKILL.md file

    Returns:
        Parsed frontmatter as dict, or empty dict if no frontmatter found

    Raises:
        yaml.YAMLError: If frontmatter is malformed
    """
    content = skill_md.read_text(encoding="utf-8")

    # Look for YAML frontmatter between --- delimiters
    if not content.startswith("---\n"):
        return {}

    # Find the closing ---
    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return {}

    frontmatter_yaml = content[4:end_marker]
    return yaml.safe_load(frontmatter_yaml) or {}


def get_public_skills(source_dir: Path) -> list[str]:
    """Find all skills with visibility: public.

    Args:
        source_dir: Path to .claude/skills/ directory

    Returns:
        Sorted list of public skill names

    Raises:
        FileNotFoundError: If source_dir doesn't exist
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    public_skills: list[str] = []

    for skill_dir in sorted(source_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"⚠️  Warning: {skill_dir.name} missing SKILL.md, skipping")
            continue

        try:
            frontmatter = parse_frontmatter(skill_md)
            metadata = frontmatter.get("metadata", {})
            visibility = metadata.get("raise.visibility", "public")  # default public

            if visibility == "public":
                public_skills.append(skill_dir.name)
            else:
                print(f"🔒 Internal: {skill_dir.name}")

        except yaml.YAMLError as e:
            print(f"❌ Error parsing {skill_dir.name}/SKILL.md: {e}", file=sys.stderr)
            raise

    return sorted(public_skills)


def sync_skills(
    source_dir: Path, target_dir: Path, public_skills: list[str], dry_run: bool = False
) -> None:
    """Sync public skills from source to target.

    Removes all existing skills in target, then copies only public skills.

    Args:
        source_dir: Path to .claude/skills/
        target_dir: Path to src/raise_cli/skills_base/
        public_skills: List of public skill names to sync
        dry_run: If True, print actions without executing
    """
    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory not found: {target_dir}")

    # Remove all existing skill directories (except __pycache__)
    for item in target_dir.iterdir():
        if item.is_dir() and item.name not in ("__pycache__", "__init__.py") and item.name.startswith("rai-"):
                if dry_run:
                    print(f"[DRY RUN] Would remove: {item.name}")
                else:
                    shutil.rmtree(item)
                    print(f"🗑️  Removed: {item.name}")

    # Copy public skills
    for skill_name in public_skills:
        source_skill = source_dir / skill_name
        target_skill = target_dir / skill_name

        if dry_run:
            print(f"[DRY RUN] Would copy: {skill_name}")
        else:
            shutil.copytree(source_skill, target_skill, dirs_exist_ok=True)
            print(f"✅ Synced: {skill_name}")


def update_distributable_list(
    target_dir: Path, public_skills: list[str], dry_run: bool = False
) -> None:
    """Update DISTRIBUTABLE_SKILLS list in __init__.py.

    Args:
        target_dir: Path to src/raise_cli/skills_base/
        public_skills: List of public skill names
        dry_run: If True, print actions without executing
    """
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        raise FileNotFoundError(f"__init__.py not found: {init_file}")

    content = init_file.read_text(encoding="utf-8")

    # Build new DISTRIBUTABLE_SKILLS list
    skills_by_category = {
        "Session lifecycle": [s for s in public_skills if s.startswith("rai-session-")],
        "Story lifecycle": [s for s in public_skills if s.startswith("rai-story-")],
        "Epic lifecycle": [s for s in public_skills if s.startswith("rai-epic-")],
        "Discovery": [s for s in public_skills if s.startswith("rai-discover-")],
        "Onboarding": [
            s
            for s in public_skills
            if s in ("rai-project-create", "rai-project-onboard", "rai-welcome")
        ],
        "Governance": [s for s in public_skills if s in ("rai-docs-update",)],
    }

    # Catch-all: anything not covered by the named categories goes to Tools
    categorized = {s for skills in skills_by_category.values() for s in skills}
    skills_by_category["Tools"] = [s for s in public_skills if s not in categorized]

    # Generate formatted list
    lines = ["DISTRIBUTABLE_SKILLS: list[str] = ["]
    for category, skills in skills_by_category.items():
        if skills:
            lines.append(f"    # {category}")
            for skill in skills:
                lines.append(f'    "{skill}",')

    lines.append("]")
    new_list = "\n".join(lines)

    # Replace existing DISTRIBUTABLE_SKILLS
    start_marker = "DISTRIBUTABLE_SKILLS: list[str] = ["

    start_idx = content.find(start_marker)
    if start_idx == -1:
        raise ValueError("DISTRIBUTABLE_SKILLS not found in __init__.py")

    # Find the matching closing bracket
    bracket_depth = 0
    end_idx = start_idx
    for i, char in enumerate(content[start_idx:], start=start_idx):
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
            if bracket_depth == 0:
                end_idx = i + 1
                break

    new_content = content[:start_idx] + new_list + content[end_idx:]

    if dry_run:
        print("\n[DRY RUN] Would update __init__.py with:")
        print(new_list)
    else:
        init_file.write_text(new_content, encoding="utf-8")
        print(f"\n📝 Updated DISTRIBUTABLE_SKILLS: {len(public_skills)} skills")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync public skills to distribution package"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    # Resolve paths relative to repo root
    repo_root = Path(__file__).parent.parent
    source_dir = repo_root / ".claude" / "skills"
    target_dir = repo_root / "packages" / "raise-cli" / "src" / "raise_cli" / "skills_base"

    print("🔄 Syncing skills from .claude/skills/ to packages/raise-cli/src/raise_cli/skills_base/\n")

    try:
        # Get public skills
        public_skills = get_public_skills(source_dir)

        if not public_skills:
            print("❌ No public skills found!", file=sys.stderr)
            return 1

        print(f"\n📦 Found {len(public_skills)} public skills\n")

        # Sync files
        sync_skills(source_dir, target_dir, public_skills, dry_run=args.dry_run)

        # Update __init__.py
        update_distributable_list(target_dir, public_skills, dry_run=args.dry_run)

        if args.dry_run:
            print("\n✅ Dry run complete (no changes made)")
        else:
            print("\n✅ Sync complete")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
