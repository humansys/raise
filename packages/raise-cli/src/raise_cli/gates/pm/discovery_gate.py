"""DiscoveryGroundingGate — guards story implement with a discovery grounding requirement.

Checks that the active story's story.md contains a non-empty
``## Discovery Grounding`` section before implementation begins.

Opt-in: skips silently if ``project.pm_gates.enabled`` is not True in
``.raise/manifest.yaml``.

Architecture: RAISE-11404, S11404.2
"""

from __future__ import annotations

import os
import re
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.pm._config import pm_gates_enabled
from raise_cli.gates.pm._utils import extract_section_content, git_branch

_SKIP_ENV: str = "RAISE_PM_DISCOVERY_SKIP_REASON"
_STORY_RE: re.Pattern[str] = re.compile(r"story/s(\d+\.\d+)/")
_DISCOVERY_MIN_CHARS: int = 10


class DiscoveryGroundingGate:
    """Quality gate requiring discovery grounding before story implementation.

    Fail-open: non-story branches and missing story.md pass silently.
    Escape hatch: ``RAISE_PM_DISCOVERY_SKIP_REASON=<reason>`` → passes with warning.
    """

    gate_id: ClassVar[str] = "gate-pm-discovery"
    description: ClassVar[str] = "Discovery grounding required before story implement"
    workflow_point: ClassVar[str] = "before:story:implement"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for a Discovery Grounding section in the active story's story.md."""
        if not pm_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="pm_gates not configured — skipping",
            )

        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        branch = git_branch(context.working_dir)
        match = _STORY_RE.search(branch)
        if not match:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="non-story branch — skipping",
            )
        story_id = match.group(1)

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

        content = story_path.read_text(encoding="utf-8")
        discovery_content = extract_section_content(content, "Discovery Grounding")

        if len(discovery_content) < _DISCOVERY_MIN_CHARS:
            rel = story_path.relative_to(context.working_dir)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Discovery Grounding required. Add content to '## Discovery Grounding' "
                    f"in {rel} (format: 'Evidence from [research/observation] showing [assumption validated]')"
                ),
            )

        return GateResult(passed=True, gate_id=self.gate_id)
