"""PublicMirrorPushGate — CI gate for RAISE-16591.

The GitHub mirror must only ever receive an orphan, sanitized snapshot
produced by ``scripts/sync-github.sh`` (forbidden-content scan, secret
scan, install-smoke) — invoked exclusively from the ``rai-publish``
skill. Nothing outside that script previously stopped an agent from
citing (and later running) a direct ``git push github ...`` — the exact
gap that let 40 unsanitized pushes reach the public mirror.

This gate scans every SKILL.md surface plus operational SOPs (excluding
``rai-publish``, the sole authorized publisher) for that pattern and fails
closed on any match — same mold as ``gate-workflow-transition-ownership``:
asserting a forbidden string is absent outside its one legitimate home.

A raw branch push (``git push github {branch} --tags``) is the dangerous
form — it publishes the private branch's full history unsanitized. The
authorized form pushes an already-sanitized orphan SHA to an explicit
``refs/tags/...`` refspec (``git push github "$SHA:refs/tags/v1.2.3"``,
rai-publish Step 6) and is never flagged — see ``_is_violation_line``.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

# The one skill allowed to reference a direct push to the `github` remote —
# it documents the sole authorized path (scripts/sync-github.sh, an orphan
# commit vetted by content-scan/secret-scan/install-smoke gates).
_ALLOWED_SKILL = "rai-publish"

# Matches `git push github ...` and the `$PUBLIC_REMOTE` alias
# scripts/sync-github.sh itself uses (`PUBLIC_REMOTE="${PUBLIC_REMOTE:-github}"`)
# — both are the literal shell invocation an agent would cite or run.
_FORBIDDEN_PUSH_RE = re.compile(r'git push (github\b|"?\$PUBLIC_REMOTE"?)')

# Marker of the one authorized push form (rai-publish Step 6): an explicit
# `<sha>:refs/tags/...` refspec pushing an already-sanitized orphan commit to
# a tag. A raw branch push (`git push github {branch} --tags`) never has
# this — it's the RAISE-16591 root cause (release SOPs instructed exactly
# that, bypassing scripts/sync-github.sh's sanitization gates entirely).
_SAFE_REFSPEC_MARKER = ":refs/tags/"


def _is_violation_line(line: str) -> bool:
    return bool(_FORBIDDEN_PUSH_RE.search(line)) and _SAFE_REFSPEC_MARKER not in line


def _discover_skill_files(working_dir: Path) -> list[Path]:
    """Discover every SKILL.md surface to scan.

    ``.claude/skills/*/SKILL.md`` (the primary authoring source) and
    ``.raise/skills/*/*/SKILL.md`` (independent skill-set variants — never
    mirrors of ``.claude/skills``, can genuinely diverge; same surface
    ``skill-cli-refint`` scans, D2) are both real places an agent reads
    skill instructions from.
    """
    claude_skills = working_dir / ".claude" / "skills"
    raise_skills = working_dir / ".raise" / "skills"

    files: list[Path] = []
    if claude_skills.is_dir():
        files.extend(sorted(claude_skills.glob("*/SKILL.md")))
    if raise_skills.is_dir():
        files.extend(sorted(raise_skills.glob("*/*/SKILL.md")))
    return files


def _discover_doc_surfaces(working_dir: Path) -> list[Path]:
    """Discover operational doc surfaces to scan.

    ``dev/sops/**/*.md`` are runbooks a developer or agent follows
    literally — same surface ``skill-cli-refint`` scans for the same
    reason (RAISE-15776). ``work/**/*`` is deliberately excluded: those are
    historical retrospectives/plans, not live guidance (GUARD_EXEMPT_PATHS
    in scripts/audit_test_imports.py already treats it the same way).
    """
    sops_dir = working_dir / "dev" / "sops"
    if not sops_dir.is_dir():
        return []
    return sorted(sops_dir.rglob("*.md"))


def _scan_files(files: list[Path]) -> dict[Path, list[str]]:
    """Scan the given files for direct github-mirror push guidance.

    Excludes any file under a ``rai-publish`` skill directory — the sole
    authorized publisher. Returns a mapping of file path -> list of
    matching lines; an empty dict means the scan found no violations.
    """
    violations: dict[Path, list[str]] = {}
    for file_path in files:
        if file_path.parent.name == _ALLOWED_SKILL:
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.debug("public-mirror-push-scan-read-error: %s — %s", file_path, exc)
            continue
        matching = [
            line.rstrip() for line in text.splitlines() if _is_violation_line(line)
        ]
        if matching:
            violations[file_path] = matching

    return violations


class PublicMirrorPushGate:
    """Fail-closed CI gate: only ``rai-publish`` may cite a direct github-mirror push.

    Scans every SKILL.md surface and dev/sops/ runbook (excluding
    ``rai-publish``) for a raw ``git push github {branch} ...`` — the
    dangerous form with no explicit ``refs/tags/...`` refspec. Any match
    means a skill or SOP would let someone bypass the mirror's
    sanitization gates (RAISE-16591).

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-public-mirror-push"
    description: ClassVar[str] = (
        "CI gate: only rai-publish may instruct a direct push to the "
        "github mirror remote (RAISE-16591)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = True

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan every SKILL.md/SOP surface and report unauthorized github-mirror pushes."""
        working_dir = context.working_dir
        files = _discover_skill_files(working_dir) + _discover_doc_surfaces(working_dir)
        violations = _scan_files(files)

        if not violations:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    "no SKILL.md/SOP outside rai-publish references a direct "
                    "github-mirror push"
                ),
            )

        details: list[str] = []
        for file_path, lines in violations.items():
            rel = file_path.relative_to(working_dir)
            details.append(
                f"{rel}: {lines[0]!r}"
                + (f" (+{len(lines) - 1} more)" if len(lines) > 1 else "")
            )

        file_names = ", ".join(str(f.relative_to(working_dir)) for f in violations)
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=(
                f"{len(violations)} file(s) outside rai-publish reference a "
                "direct github-mirror push — only scripts/sync-github.sh "
                "via rai-publish may push to the github remote "
                f"(RAISE-16591): {file_names}"
            ),
            details=tuple(details),
        )
