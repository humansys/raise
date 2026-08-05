"""WorkflowTransitionOwnershipGate — CI gate for RAISE-15027 ownership enforcement.

Scans ``.claude/skills/*.md`` (the SKILL.md files used by the pipeline engine)
for stray ``rai backlog transition`` or ``raise_backlog_transition`` calls.
Any match means a skill is still attempting to own a Jira state transition
directly, bypassing the engine — this gate fails-closed to prevent regressions.

Architecture: ADR-039 (WorkflowGate Protocol), S10 (RAISE-15037)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

# Patterns that indicate a stray transition call in a SKILL.md file.
_STRAY_PATTERNS: tuple[str, ...] = (
    "rai backlog transition",
    "raise_backlog_transition",
)

# Built-in shipped pipelines, relative to this package. Used as the fall-back
# scan target when the repo has no local ``pipelines_base/``.
_BUILTIN_PIPELINES: Path = (
    Path(__file__).resolve().parents[2] / "pipeline" / "pipelines_base"
)


def _scan_skills(working_dir: Path) -> dict[Path, list[str]]:
    """Scan ``.claude/skills/*/SKILL.md`` for stray transition call patterns.

    Returns a mapping of SKILL.md path → list of matching lines.
    An empty dict means the scan found no violations.
    """
    skills_root = working_dir / ".claude" / "skills"
    if not skills_root.exists():
        return {}

    violations: dict[Path, list[str]] = {}
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        try:
            text = skill_file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.debug("skill-scan-read-error: %s — %s", skill_file, exc)
            continue
        matching = [
            line.rstrip()
            for line in text.splitlines()
            if any(pat in line for pat in _STRAY_PATTERNS)
        ]
        if matching:
            violations[skill_file] = matching

    return violations


def _find_pipelines_dir(working_dir: Path) -> Path | None:
    """Resolve the pipeline definitions directory to scan.

    Highest-priority first: a repo-local ``pipelines_base/``, then the
    in-tree package source (raise-commons layout), then the built-in shipped
    pipelines. The first directory that exists wins; ``None`` if none do.
    """
    candidates = (
        working_dir / "pipelines_base",
        working_dir
        / "packages"
        / "raise-cli"
        / "src"
        / "raise_cli"
        / "pipeline"
        / "pipelines_base",
        _BUILTIN_PIPELINES,
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def _scan_pipelines_missing_target_status(working_dir: Path) -> list[str]:
    """Find pipelines that HAVE a ``close`` phase but no ``target_status``.

    The engine transitions the tracker at the close phase using its
    ``target_status``; a close phase without one silently ships work that
    never advances in Jira. Pipelines with no close phase at all
    (epic-design-pdcv, initiative, initiative-enterprise, upgrade) are
    intentionally excluded — they are not flagged.

    Returns a sorted list of pipeline names (advisory, non-blocking).
    """
    pipelines_dir = _find_pipelines_dir(working_dir)
    if pipelines_dir is None:
        return []

    flagged: list[str] = []
    for yaml_file in sorted(pipelines_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            logger.debug("pipeline-scan-read-error: %s — %s", yaml_file, exc)
            continue
        if not isinstance(data, dict):
            continue
        phases = data.get("phases")
        if not isinstance(phases, list):
            continue
        close_phase = next(
            (
                phase
                for phase in phases
                if isinstance(phase, dict) and phase.get("id") == "close"
            ),
            None,
        )
        # No close phase → not applicable, not flagged.
        if close_phase is None:
            continue
        if not close_phase.get("target_status"):
            name = data.get("name")
            flagged.append(str(name) if name else yaml_file.stem)

    return sorted(flagged)


class WorkflowTransitionOwnershipGate:
    """Fail-closed CI gate: no SKILL.md may contain stray backlog transition calls.

    Scans ``.claude/skills/*/SKILL.md`` for ``rai backlog transition`` or
    ``raise_backlog_transition`` calls.  Any match indicates a skill is
    bypassing the engine's ownership of Jira state transitions.

    Returns ``passed=False`` listing the offending files when violations are
    found; ``passed=True`` with a clean-scan message otherwise.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-workflow-transition-ownership"
    description: ClassVar[str] = (
        "CI gate: no SKILL.md contains stray backlog transition calls (RAISE-15027)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan .claude/skills/ (fail-closed) and pipelines (advisory)."""
        violations = _scan_skills(context.working_dir)

        # Advisory (non-blocking): pipelines with a close phase but no
        # target_status. These NEVER flip ``passed`` — they surface as
        # warnings appended to details (RAISE-15200).
        missing_ts = _scan_pipelines_missing_target_status(context.working_dir)
        warning_details = tuple(
            f"pipeline '{name}' has a close phase without target_status — the "
            f"engine cannot transition the tracker at close (advisory, RAISE-15200)"
            for name in missing_ts
        )

        if not violations:
            if warning_details:
                return GateResult(
                    passed=True,
                    gate_id=self.gate_id,
                    message=(
                        "no stray transition calls found in .claude/skills/; "
                        f"{len(warning_details)} pipeline(s) have a close phase "
                        "missing target_status (advisory)"
                    ),
                    details=warning_details,
                    advisory=True,
                )
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no stray transition calls found in .claude/skills/",
            )

        # Build details: one line per file listing the first matching line
        details: list[str] = []
        for skill_path, lines in violations.items():
            rel = skill_path.relative_to(context.working_dir)
            details.append(
                f"{rel}: {lines[0]!r}"
                + (f" (+{len(lines) - 1} more)" if len(lines) > 1 else "")
            )

        file_names = ", ".join(skill_path.parent.name for skill_path in violations)
        summary = (
            f"{len(violations)} SKILL.md file(s) contain stray backlog transition "
            f"calls — engine owns transitions (RAISE-15027): {file_names}"
        )
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=summary,
            details=tuple(details) + warning_details,
        )
