"""GovernanceArtifactsGate — blocks implementation without governance trail.

Verifies that a scope artifact exists before story/bug implementation begins.
Extracts context from the git branch name:
  - story/s{N}.{M}/{slug} → work/epics/**/s{N}.{M}-scope.md
  - bug/{KEY}/{slug}       → work/bugs/{KEY}/scope.md

Fail-open: unrecognized branch patterns pass silently (chore, hotfix, CI).
Escape hatch: RAISE_GOVERNANCE_SKIP_REASON=<reason> bypasses with logged warning.

Architecture: ADR-039 §1 (WorkflowGate Protocol), RAISE-9271.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

_SKIP_ENV = "RAISE_GOVERNANCE_SKIP_REASON"
_STORY_RE = re.compile(r"story/s(\d+\.\d+)/")
_BUG_RE = re.compile(r"bug/(RAISE-\d+)/")


def _git_branch(working_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return ""


def _find_story_scope(working_dir: Path, story_id: str) -> bool:
    return bool(list(working_dir.glob(f"work/epics/**/{story_id}-scope.md")))


def _find_bug_scope(working_dir: Path, bug_key: str) -> bool:
    return (working_dir / "work" / "bugs" / bug_key / "scope.md").is_file()


class GovernanceArtifactsGate:
    """Blocks implementation when governance scope artifact is missing."""

    gate_id: ClassVar[str] = "gate-governance-artifacts"
    description: ClassVar[str] = (
        "Governance scope artifact exists before implementation"
    )
    workflow_point: ClassVar[str] = "before:story:implement"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check scope artifact exists for the current story/bug branch."""
        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Governance check skipped: {skip_reason}",
            )

        branch = _git_branch(context.working_dir)

        story_m = _STORY_RE.search(branch)
        if story_m:
            story_id = f"s{story_m.group(1)}"
            if _find_story_scope(context.working_dir, story_id):
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message=f"Scope artifact found for {story_id}",
                )
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"No scope artifact for {story_id} — run story-start/story-design first",
                details=(
                    f"Expected: work/epics/**/{story_id}-scope.md",
                    f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
                ),
            )

        bug_m = _BUG_RE.search(branch)
        if bug_m:
            bug_key = bug_m.group(1)
            if _find_bug_scope(context.working_dir, bug_key):
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message=f"Scope artifact found for {bug_key}",
                )
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"No scope artifact for {bug_key} — run bugfix-start first",
                details=(
                    f"Expected: work/bugs/{bug_key}/scope.md",
                    f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
                ),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="No story/bug context detected — governance check not applicable",
        )
