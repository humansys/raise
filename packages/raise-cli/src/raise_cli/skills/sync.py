"""Skill propagation logic — ADR-074 D3.

Propagates from .claude/skills/ (SST) to skills_base/ and all registered agent skill dirs.
"""

from __future__ import annotations

import filecmp
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from raise_cli.skills.parser import ParseError
from raise_cli.skills.parser import parse_frontmatter as _parse_skill_frontmatter


def skill_names(directory: Path) -> set[str]:
    """Return the set of skill names (``rai-*`` dirs with ``SKILL.md``) under *directory*.

    This is the canonical definition of "what counts as a skill directory" used
    by both ``SkillSyncer`` and ``codex_plugin``; sharing it prevents the three-
    way definition drift identified in RAISE-18967's quality review.

    Returns an empty set when *directory* does not exist.
    """
    if not directory.is_dir():
        return set()
    return {
        d.name
        for d in directory.iterdir()
        if d.is_dir() and d.name.startswith("rai-") and (d / "SKILL.md").exists()
    }


@dataclass
class SkillSyncResult:
    """Result of a sync or check operation."""

    synced_to_skills_base: list[str] = field(default_factory=list)
    synced_to_agents: dict[str, list[str]] = field(default_factory=dict)
    drift_skills_base: list[str] = field(default_factory=list)
    drift_agents: dict[str, list[str]] = field(default_factory=dict)
    # RAISE-18967: skills present in destination but absent from source (stale after rename)
    stale_skills_base: list[str] = field(default_factory=list)
    stale_agents: dict[str, list[str]] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        """Return True when no drift or stale entries were detected in any destination."""
        return (
            not self.drift_skills_base
            and not any(self.drift_agents.values())
            and not self.stale_skills_base
            and not any(self.stale_agents.values())
        )


class SkillSyncer:
    """Propagates skills from .claude/skills/ to skills_base/ and agent skill dirs.

    Usage:
        syncer = SkillSyncer(source, skills_base, agent_skill_dirs=[...])
        result = syncer.sync()          # propagate
        result = syncer.check()         # dry-run drift check
    """

    def __init__(
        self,
        source: Path,
        skills_base: Path,
        agent_skill_dirs: list[Path],
    ) -> None:
        self._source = source
        self._skills_base = skills_base
        self._agent_skill_dirs = agent_skill_dirs

    # ── public API ──────────────────────────────────────────────────────────

    def sync(
        self, include_internal: bool = False, purge_stale: bool = False
    ) -> SkillSyncResult:
        """Propagate from source to skills_base/ and all agent skill dirs.

        Args:
            include_internal: When True, also sync internal-visibility skills to
                skills_base/ (they always go to agent dirs regardless).
            purge_stale: When True, remove skill directories that are present in a
                destination but absent from source (RAISE-18967).  Defaults to
                False so that automated callers (e.g. ``rai worktree provision``)
                do not silently delete content they did not add; pass True only
                from the explicit ``rai skill sync`` CLI command.
        """
        result = SkillSyncResult()
        all_skills = self._get_source_skills()
        source_names = set(all_skills)

        # skills_base/ — public only (or all if include_internal)
        self._skills_base.mkdir(parents=True, exist_ok=True)
        public_skills: list[str] = []
        for name in all_skills:
            if include_internal or self._is_public(name):
                self._copy_skill(name, self._skills_base)
                result.synced_to_skills_base.append(name)
                public_skills.append(name)

        # Stale in skills_base is measured against the public set that belongs
        # there — not against all_skills — so a skill demoted to internal has
        # its skills_base copy cleaned up (RAISE-18967 QR finding).
        if purge_stale:
            public_skill_names = set(public_skills)
            self._remove_stale(self._skills_base, public_skill_names)

        self._update_distributable_list(public_skills)

        # agent skill dirs — all rai-* skills, no visibility filter
        for agent_dir in self._agent_skill_dirs:
            agent_dir.mkdir(parents=True, exist_ok=True)
            synced: list[str] = []
            for name in all_skills:
                self._copy_skill(name, agent_dir)
                synced.append(name)
            result.synced_to_agents[str(agent_dir)] = synced

            # Stale in agent dirs is measured against all source skills.
            if purge_stale:
                self._remove_stale(agent_dir, source_names)

        return result

    def check(self, include_internal: bool = False) -> SkillSyncResult:
        """Dry-run: compare source against destinations, return drift without writing.

        Reports both missing/outdated skills (drift) and skills present in a
        destination that no longer exist in source (stale, RAISE-18967).
        """
        result = SkillSyncResult()
        all_skills = self._get_source_skills()
        source_names = set(all_skills)
        public_skill_names = {
            name for name in source_names if include_internal or self._is_public(name)
        }

        for name in all_skills:
            if name in public_skill_names and not self._skill_in_sync(
                name, self._skills_base
            ):
                result.drift_skills_base.append(name)

        # Detect stale in skills_base against the PUBLIC set — a demoted skill's
        # copy in skills_base is stale even though the skill exists in source.
        if self._skills_base.exists():
            result.stale_skills_base = self._find_stale(
                self._skills_base, public_skill_names
            )

        for agent_dir in self._agent_skill_dirs:
            drifted: list[str] = []
            for name in all_skills:
                if not self._skill_in_sync(name, agent_dir):
                    drifted.append(name)
            if drifted:
                result.drift_agents[str(agent_dir)] = drifted

            # Detect stale in agent dirs against all source skills.
            if agent_dir.exists():
                stale = self._find_stale(agent_dir, source_names)
                if stale:
                    result.stale_agents[str(agent_dir)] = stale

        return result

    # ── private helpers ─────────────────────────────────────────────────────

    def _get_source_skills(self) -> list[str]:
        return sorted(skill_names(self._source))

    def _is_public(self, skill_name: str) -> bool:
        skill_md = self._source / skill_name / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
            fm, _ = _parse_skill_frontmatter(content)
            metadata = fm.get("metadata", {}) or {}
            return metadata.get("raise.visibility", "public") == "public"
        except (OSError, ParseError):
            return True  # default public on read/parse failure

    def _skill_in_sync(self, skill_name: str, dest_dir: Path) -> bool:
        src_dir = self._source / skill_name
        dst_dir = dest_dir / skill_name
        if not (dst_dir / "SKILL.md").exists():
            return False
        if not filecmp.cmp(src_dir / "SKILL.md", dst_dir / "SKILL.md", shallow=False):
            return False
        for ref_name in ("references", "_references"):
            src_ref = src_dir / ref_name
            if src_ref.is_dir():
                dst_ref = dst_dir / ref_name
                if not dst_ref.exists():
                    return False
                src_files = [f.name for f in src_ref.iterdir() if f.is_file()]
                _, mismatch, errors = filecmp.cmpfiles(
                    src_ref, dst_ref, src_files, shallow=False
                )
                if mismatch or errors:
                    return False
        return True

    def _find_stale(self, dest_dir: Path, source_names: set[str]) -> list[str]:
        """Return skill names present in dest_dir but absent from source_names."""
        return sorted(
            name for name in skill_names(dest_dir) if name not in source_names
        )

    def _remove_stale(self, dest_dir: Path, source_names: set[str]) -> None:
        """Delete skill directories in dest_dir that are absent from source_names."""
        if not dest_dir.exists():
            return
        for stale_dir in self._find_stale(dest_dir, source_names):
            shutil.rmtree(dest_dir / stale_dir)

    def _copy_skill(self, skill_name: str, dest_dir: Path) -> None:
        src = self._source / skill_name
        dst = dest_dir / skill_name
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / "SKILL.md", dst / "SKILL.md")
        for ref_name in ("references", "_references"):
            ref_src = src / ref_name
            if ref_src.is_dir():
                ref_dst = dst / ref_name
                if ref_dst.exists():
                    shutil.rmtree(ref_dst)
                shutil.copytree(ref_src, ref_dst)

    def _update_distributable_list(self, public_skills: list[str]) -> None:
        init_file = self._skills_base / "__init__.py"
        if not init_file.exists():
            return

        content = init_file.read_text(encoding="utf-8")

        lines = ["DISTRIBUTABLE_SKILLS: list[str] = ["]
        skills_by_category: dict[str, list[str]] = {
            "Session lifecycle": [
                s for s in public_skills if s.startswith("rai-session-")
            ],
            "Mission lifecycle": [
                s for s in public_skills if s.startswith("rai-mission-")
            ],
            "Story lifecycle": [s for s in public_skills if s.startswith("rai-story-")],
            "Epic lifecycle": [s for s in public_skills if s.startswith("rai-epic-")],
            "Bugfix lifecycle": [
                s for s in public_skills if s.startswith("rai-bugfix-")
            ],
            "Discovery": [s for s in public_skills if s.startswith("rai-discover")],
            "Onboarding": [
                s
                for s in public_skills
                if s in ("rai-project-create", "rai-project-onboard", "rai-welcome")
            ],
            "Governance": [s for s in public_skills if s == "rai-docs-update"],
            "Meta": [
                s
                for s in public_skills
                if s.startswith("rai-skill-") or s.startswith("rai-skillset-")
            ],
            "MCP": [s for s in public_skills if s.startswith("rai-mcp-")],
            "Worktree": [s for s in public_skills if s.startswith("rai-worktree-")],
        }
        categorized = {s for skills in skills_by_category.values() for s in skills}
        skills_by_category["Tools"] = [s for s in public_skills if s not in categorized]

        for category, skills in skills_by_category.items():
            if skills:
                lines.append(f"    # {category}")
                for s in skills:
                    lines.append(f'    "{s}",')
        lines.append("]")
        new_block = "\n".join(lines)

        start_marker = "DISTRIBUTABLE_SKILLS: list[str] = ["
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return

        list_open_idx = start_idx + len(start_marker) - 1
        depth = 0
        end_idx = list_open_idx
        for i, ch in enumerate(content[list_open_idx:], start=list_open_idx):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        new_content = content[:start_idx] + new_block + content[end_idx + 1 :]
        init_file.write_text(new_content, encoding="utf-8")
