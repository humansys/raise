"""MR create gate — block direct glab/gh MR creation (RAISE-16936).

PreToolUse check: Bash commands containing ``glab mr create`` or
``gh pr create`` are blocked with exit 2 and a message directing the
agent to use ``/rai-mr-create`` instead.

Direct MR creation bypasses 5 local admission checks:
  1. Governance artifact check
  2. Governance trail check
  3. CI contract/lint check
  4. Merge policy check
  5. Provenance metadata injection
"""

from __future__ import annotations

import re
import sys

_MR_CREATE_PATTERN = re.compile(
    r"\bglab\s+mr\s+create\b|\bgh\s+pr\s+create\b",
)


def check_mr_create_gate(
    *,
    tool_name: str,
    tool_input: dict[str, object],
) -> int:
    """Check if a Bash command attempts direct MR/PR creation.

    Returns 0 (allow) or 2 (block).
    """
    if tool_name != "Bash":
        return 0

    command = str(tool_input.get("command") or "")
    if not command:
        return 0

    if _MR_CREATE_PATTERN.search(command):
        print(
            "[governance] BLOCKED: direct MR/PR creation is not allowed.\n"
            "  Use /rai-mr-create instead — it runs 5 local admission checks\n"
            "  (governance artifact, governance trail, CI contract, merge policy,\n"
            "  provenance metadata) before creating the MR.\n"
            "  See: RAISE-16936",
            file=sys.stderr,
        )
        return 2

    return 0
