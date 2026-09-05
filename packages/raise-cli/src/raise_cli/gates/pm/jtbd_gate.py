"""JTBDGate — guards story implement with a JTBD statement requirement.

Checks that the active story's story.md contains a non-empty ``## JTBD``
section before implementation begins.

Opt-in: skips silently if ``project.pm_gates.enabled`` is not True in
``.raise/manifest.yaml``. Distributable to all users without imposing PM
discipline on projects that have not opted in.

Architecture: RAISE-11404, S11404.1
"""

from __future__ import annotations

import os
import re
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.pm._config import pm_gates_enabled
from raise_cli.gates.pm._utils import extract_section_content, git_branch

_SKIP_ENV: str = "RAISE_PM_JTBD_SKIP_REASON"
_STORY_RE: re.Pattern[str] = re.compile(r"story/s(\d+\.\d+)/")
_JTBD_MIN_CHARS: int = 10


class JTBDGate:
    """Quality gate requiring a JTBD statement before story implementation.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Fail-open policy: non-story branches and missing story.md files pass
    silently — the gate only enforces on recognized ``story/s{N}.{M}/`` branches
    where a story.md exists.

    Escape hatch: set ``RAISE_PM_JTBD_SKIP_REASON=<reason>`` to bypass with a
    logged warning — for internal tooling stories with no external user job.
    """

    gate_id: ClassVar[str] = "gate-pm-jtbd"
    description: ClassVar[str] = "JTBD statement required before story implement"
    workflow_point: ClassVar[str] = "before:story:implement"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for a JTBD statement in the active story's story.md.

        Enforces only on story branches (``story/s{N}.{M}/…``) when pm_gates
        are enabled. Passes silently otherwise.
        """
        # 1. Skip if not opted in
        if not pm_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="pm_gates not configured — skipping",
            )

        # 2. Escape hatch via env var
        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        # 3. Parse branch → story_id (fail-open on non-story branches)
        branch = git_branch(context.working_dir)
        match = _STORY_RE.search(branch)
        if not match:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="non-story branch — skipping",
            )
        story_id = match.group(1)

        # 4. Find story.md (fail-open if not found yet)
        story_files = list(
            context.working_dir.glob(f"work/epics/**/*{story_id}-story.md")
        )
        if not story_files:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"story.md for s{story_id} not found — skipping",
            )
        story_path = story_files[0]

        # 5. Check ## JTBD section content
        content = story_path.read_text(encoding="utf-8")
        jtbd_content = extract_section_content(content, "JTBD")

        if len(jtbd_content) < _JTBD_MIN_CHARS:
            rel = story_path.relative_to(context.working_dir)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"JTBD statement required. Add content to '## JTBD' in {rel} "
                    f"(format: 'Help me X so I can Y')"
                ),
            )

        return GateResult(passed=True, gate_id=self.gate_id)
