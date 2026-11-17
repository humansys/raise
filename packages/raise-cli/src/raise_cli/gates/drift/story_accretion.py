r"""StoryAccretionGate — CAND-05 drift detector.

Rule: single source file contains ≥3 distinct story-ID tokens without consolidation.
Story-ID patterns: ``S\d+\.\d+``, ``RAISE-\d+``, ``ADR-[A-Z0-9-]+``.
Advisory: returns passed=True with violation details.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.gates.drift._base import DriftGate, is_excluded, scoped_rglob
from raise_cli.gates.models import GateContext, GateResult

_STORY_TOKEN = re.compile(r"S\d+\.\d+|RAISE-\d+|ADR-[A-Z0-9-]+")
_THRESHOLD = 3


def _count_tokens(path: Path) -> set[str]:
    """Return distinct story-ID tokens found in the file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(_STORY_TOKEN.findall(text))


class StoryAccretionGate(DriftGate):
    """Flags files accumulating references to ≥3 distinct stories without consolidation.

    Evidence: κ=0.802, precision=0.25 (E2161 CAND-05).
    """

    gate_id = "drift-story-accretion"
    description = "Multi-story accretion density (CAND-05)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan .py files for story-token density."""
        violations: list[str] = []
        for path in scoped_rglob(context.working_dir, "*.py", context.changed_files):
            if is_excluded(path, context.working_dir) or self._has_ignore_marker(path):
                continue
            tokens = _count_tokens(path)
            if len(tokens) >= _THRESHOLD:
                rel = path.relative_to(context.working_dir)
                violations.append(
                    f"{rel}: {len(tokens)} tokens ({', '.join(sorted(tokens)[:5])})"
                )
        return self._advisory(self.gate_id, violations)
