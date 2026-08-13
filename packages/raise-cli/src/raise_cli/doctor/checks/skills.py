"""SkillCommandReferenceCheck — validates CLI commands referenced in SKILL.md files.

Extracts ``rai <subcommand>`` patterns from each deployed SKILL.md and validates
them against the installed CLI via Click introspection (no subprocess).

Architecture note: first ``doctor`` → ``session`` cross-dependency. The import
of ``get_cli_commands`` from ``raise_cli.session.bundle_data`` is intentional
and lazily resolved inside ``evaluate()`` to prevent circular imports at module
load time (bundle_data → cli.main → doctor would be the problematic chain).

MCP migration note:
    This check validates CLI command references only. When SKILL.md files migrate
    from ``rai <cmd>`` to ``mcp__rai-workspace__<tool>`` as the primary call path,
    coverage will degrade progressively because MCP tool references are not yet
    validated. See work/bugs/RAISE-4339/plan.md § "MCP Migration Guide" for the
    concrete extension steps (MCP pattern extractor, ground truth source, new
    CheckResult pattern with ``check_id = "skills-mcp-reference-{skill_name}"``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_SKILLS_DIR = Path(".claude") / "skills"
# Space-only separator prevents greedy capture across newlines.
_RAI_CMD_RE = re.compile(r"\brai +([a-z][a-z0-9-]*(?:[ ]+[a-z][a-z0-9-]*)*)")
# Matches fenced code blocks: ```bash, ```sh, or plain ```.
_FENCED_BLOCK_RE = re.compile(r"```(?:bash|sh)?\n(.*?)```", re.DOTALL)


def _extract_bash_block_text(text: str) -> str:
    """Return concatenated content of all fenced code blocks in *text*."""
    return "\n".join(m.group(1) for m in _FENCED_BLOCK_RE.finditer(text))


def _extract_rai_commands(text: str) -> list[str]:
    """Extract ``rai <subcommand>`` references from fenced code blocks only."""
    matches = _RAI_CMD_RE.findall(_extract_bash_block_text(text))
    seen: set[str] = set()
    result: list[str] = []
    for sub in matches:
        full = f"rai {sub.strip()}"
        if full not in seen:
            seen.add(full)
            result.append(full)
    return result


def _is_valid_command(cmd: str, known: list[str]) -> bool:
    """Return True if *cmd* is a valid CLI invocation.

    Accepts three forms:
    - exact leaf match (``rai db status``)
    - leaf command with trailing arguments (``rai gate check gate-id``)
    - valid group invocation without subcommand (``rai doctor``, ``rai backlog``)
    """
    return any(
        cmd == k or cmd.startswith(k + " ") or k.startswith(cmd + " ") for k in known
    )


class SkillCommandReferenceCheck(DoctorCheck):
    """Validates that CLI commands referenced in SKILL.md files exist in the installed CLI.

    Produces one ``CheckResult`` per SKILL.md file — PASS when all referenced
    commands are found in ``get_cli_commands()``, WARN when one or more are stale.
    Returns an empty list when ``.claude/skills/`` does not exist.

    MCP migration note: see module docstring for extension steps.
    """

    check_id: ClassVar[str] = "skills-command-reference"
    category: ClassVar[str] = "skills"
    description: ClassVar[str] = (
        "Validates that CLI commands referenced in SKILL.md files exist in the installed CLI"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan SKILL.md files and flag stale CLI command references."""
        # Lazy import — avoids circular: bundle_data → cli.main → (any doctor import)
        from raise_cli.session.bundle_data import get_cli_commands  # noqa: PLC0415

        skills_dir = context.working_dir / _SKILLS_DIR
        if not skills_dir.is_dir():
            return []

        known = get_cli_commands()
        results: list[CheckResult] = []

        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            skill_name = skill_md.parent.name
            text = skill_md.read_text(encoding="utf-8")
            refs = _extract_rai_commands(text)
            if not refs:
                results.append(
                    CheckResult(
                        check_id=f"skills-command-reference-{skill_name}",
                        category=self.category,
                        status=CheckStatus.PASS,
                        message=f"{skill_name}: no CLI command references found",
                    )
                )
                continue

            stale = [cmd for cmd in refs if not _is_valid_command(cmd, known)]
            if stale:
                stale_list = ", ".join(stale)
                results.append(
                    CheckResult(
                        check_id=f"skills-command-reference-{skill_name}",
                        category=self.category,
                        status=CheckStatus.WARN,
                        message=f"{skill_name}: stale CLI references — {stale_list}",
                        fix_hint=f"Update {skill_md.relative_to(context.working_dir)} — replace stale commands",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id=f"skills-command-reference-{skill_name}",
                        category=self.category,
                        status=CheckStatus.PASS,
                        message=f"{skill_name}: all {len(refs)} CLI reference(s) valid",
                    )
                )

        return results
