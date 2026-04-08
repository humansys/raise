"""Built-in ProjectCheck — validates .raise/ structure and project coherence.

Checks .raise/ directory, manifest.yaml, graph staleness, adapter config,
skill deployment, and .gitignore entries.

Architecture: ADR-045, S352.3
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

_RAISE_DIR_NAME = ".raise"
_FIX_HINT_INIT = "run: rai init"
_FIX_HINT_GRAPH_BUILD = "run: rai graph build"


class ProjectCheck:
    """Diagnostic check for .raise/ project structure and coherence.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "project"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = ".raise/ structure, manifest, graph staleness, config"
    requires_online: ClassVar[bool] = False

    _GRAPH_STALENESS_DAYS: ClassVar[int] = 7

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run all project coherence checks."""
        root = context.working_dir
        results: list[CheckResult] = []

        results.append(self._check_raise_dir(root))
        results.append(self._check_manifest(root))
        results.append(self._check_graph_staleness(root))
        results.append(self._check_adapter_config(root))
        results.append(self._check_skills_deployed(root))
        results.append(self._check_gitignore(root))

        return results

    def _check_raise_dir(self, root: Path) -> CheckResult:
        """Check that .raise/ directory exists."""
        raise_dir = root / _RAISE_DIR_NAME
        if raise_dir.is_dir():
            return CheckResult(
                check_id="project-raise-dir",
                category=self.category,
                status=CheckStatus.PASS,
                message=".raise/ directory exists",
            )
        return CheckResult(
            check_id="project-raise-dir",
            category=self.category,
            status=CheckStatus.ERROR,
            message=".raise/ directory missing",
            fix_hint=_FIX_HINT_INIT,
        )

    def _check_manifest(self, root: Path) -> CheckResult:
        """Check that manifest.yaml exists and is valid YAML."""
        manifest = root / _RAISE_DIR_NAME / "manifest.yaml"
        if not manifest.is_file():
            return CheckResult(
                check_id="project-manifest",
                category=self.category,
                status=CheckStatus.ERROR,
                message="manifest.yaml missing",
                fix_hint=_FIX_HINT_INIT,
            )
        try:
            content = manifest.read_text(encoding="utf-8")
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                return CheckResult(
                    check_id="project-manifest",
                    category=self.category,
                    status=CheckStatus.ERROR,
                    message="manifest.yaml is not a valid YAML mapping",
                )
        except yaml.YAMLError as exc:
            return CheckResult(
                check_id="project-manifest",
                category=self.category,
                status=CheckStatus.ERROR,
                message=f"manifest.yaml has invalid YAML: {exc}",
            )
        return CheckResult(
            check_id="project-manifest",
            category=self.category,
            status=CheckStatus.PASS,
            message="manifest.yaml is valid",
        )

    def _check_graph_staleness(self, root: Path) -> CheckResult:
        """Check if graph index exists and is not stale."""
        # Graph is stored at .raise/rai/memory/index.json (rai graph build output)
        graph_index = root / _RAISE_DIR_NAME / "rai" / "memory" / "index.json"
        if not graph_index.is_file():
            return CheckResult(
                check_id="project-graph",
                category=self.category,
                status=CheckStatus.WARN,
                message="graph not built (.raise/rai/memory/index.json missing)",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
                fix_id="rebuild-graph",
            )

        graph_files = [graph_index]
        # Also check for additional graph files in the directory
        graph_dir = graph_index.parent
        graph_files.extend(
            f for f in graph_dir.rglob("*") if f.is_file() and f != graph_index
        )
        if not graph_files:
            return CheckResult(
                check_id="project-graph",
                category=self.category,
                status=CheckStatus.WARN,
                message="graph directory is empty",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
                fix_id="rebuild-graph",
            )

        newest_graph = max(f.stat().st_mtime for f in graph_files)
        now = time.time()
        days_old = (now - newest_graph) / 86400

        if days_old > self._GRAPH_STALENESS_DAYS:
            return CheckResult(
                check_id="project-graph",
                category=self.category,
                status=CheckStatus.WARN,
                message=f"graph is {days_old:.0f} days old",
                fix_hint=_FIX_HINT_GRAPH_BUILD,
                fix_id="rebuild-graph",
            )

        # Check if governance files are newer than graph
        governance_dir = root / "governance"
        if governance_dir.is_dir():
            gov_files = list(governance_dir.rglob("*.md"))
            if gov_files:
                newest_gov = max(f.stat().st_mtime for f in gov_files)
                if newest_gov > newest_graph:
                    return CheckResult(
                        check_id="project-graph",
                        category=self.category,
                        status=CheckStatus.WARN,
                        message="governance files are newer than graph",
                        fix_hint=_FIX_HINT_GRAPH_BUILD,
                        fix_id="rebuild-graph",
                    )

        return CheckResult(
            check_id="project-graph",
            category=self.category,
            status=CheckStatus.PASS,
            message="graph is up to date",
        )

    def _check_adapter_config(self, root: Path) -> CheckResult:
        """Check if adapter config files are present (informational)."""
        jira_config = root / _RAISE_DIR_NAME / "jira.yaml"
        if jira_config.is_file():
            return CheckResult(
                check_id="project-adapter-config",
                category=self.category,
                status=CheckStatus.PASS,
                message="jira.yaml adapter config found",
            )
        return CheckResult(
            check_id="project-adapter-config",
            category=self.category,
            status=CheckStatus.WARN,
            message="jira.yaml not found (optional — needed for Jira integration)",
        )

    def _check_skills_deployed(self, root: Path) -> CheckResult:
        """Check if skills are deployed to .claude/skills/."""
        skills_dir = root / ".claude" / "skills"
        if not skills_dir.is_dir():
            return CheckResult(
                check_id="project-skills",
                category=self.category,
                status=CheckStatus.WARN,
                message=".claude/skills/ directory missing",
                fix_hint="run: rai skill sync",
            )
        skill_files = list(skills_dir.rglob("SKILL.md"))
        if not skill_files:
            return CheckResult(
                check_id="project-skills",
                category=self.category,
                status=CheckStatus.WARN,
                message="no skills deployed in .claude/skills/",
                fix_hint="run: rai skill sync",
            )
        return CheckResult(
            check_id="project-skills",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"{len(skill_files)} skills deployed",
        )

    def _check_gitignore(self, root: Path) -> CheckResult:
        """Check if .raise/rai/personal/ is in .gitignore."""
        gitignore = root / ".gitignore"
        if not gitignore.is_file():
            return CheckResult(
                check_id="project-gitignore",
                category=self.category,
                status=CheckStatus.WARN,
                message=".gitignore missing",
                fix_hint=_FIX_HINT_INIT,
            )
        content = gitignore.read_text(encoding="utf-8")
        # Check for the personal directory pattern
        if ".raise/rai/personal/" in content or ".raise/rai/personal" in content:
            return CheckResult(
                check_id="project-gitignore",
                category=self.category,
                status=CheckStatus.PASS,
                message=".raise/rai/personal/ is in .gitignore",
            )
        return CheckResult(
            check_id="project-gitignore",
            category=self.category,
            status=CheckStatus.WARN,
            message=".raise/rai/personal/ not found in .gitignore",
            fix_hint=_FIX_HINT_INIT,
            fix_id="add-gitignore-personal",
        )
