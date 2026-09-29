"""Mermaid dialect allowlist — D-S1, AC4.

RAISE-15886 T4 confirmed exactly one dialect reliable across all four
rendering targets (mmdc, GitLab passthrough, mkdocs, Confluence):
``flowchart`` (+ ``subgraph``). ``C4Context``/``C4Container``/
``C4Component``/``architecture-beta`` each have an untested Confluence
cell and Mermaid's own C4 support is officially experimental — a pipeline
whose premise is "publish everywhere, unattended" cannot ship on an
untested cell.

This module enforces the allowlist mechanically: a synthesized block
opening with anything other than ``flowchart`` fails validation and is
never written. The allowlist is a module constant so a follow-up story
that spot-checks C4 against Confluence (T4's own recommendation) flips
one list without touching the region writer.
"""

from __future__ import annotations

import re

# Module constant, deliberately: promoting a dialect later is a one-line
# change here, not a redesign of validate.py or regions.py.
ALLOWED_DIALECTS: tuple[str, ...] = ("flowchart",)

_FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
_FIRST_TOKEN_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_-]*)")


class DialectError(ValueError):
    """A mermaid fence uses a dialect outside ``ALLOWED_DIALECTS``.

    Also raised when no mermaid fence is found at all, or the fence body
    is empty — both are "nothing valid to write" conditions from the
    writer's point of view.
    """


def validate_mermaid_block(text: str) -> str:
    """Validate the mermaid dialect of every fenced block in ``text``.

    Args:
        text: Markdown text expected to contain one or more
            ` ```mermaid ` fences.

    Returns:
        The dialect keyword found (always ``"flowchart"`` on success —
        useful for logging/tests that want to assert what was accepted).

    Raises:
        DialectError: no fence found, an empty fence, or ANY fenced block
            using a disallowed dialect (R1 — every fence in the payload is
            checked via ``finditer``, not just the first: a payload with
            an allowed ``flowchart`` fence followed by a rejected
            ``C4Container`` fence must not slip through because only the
            first match was ever inspected).
    """
    matches = list(_FENCE_RE.finditer(text))
    if not matches:
        raise DialectError(
            "no ```mermaid fence found — nothing to validate\n"
            f"  Allowed: {', '.join(ALLOWED_DIALECTS)}"
        )

    dialect = ""
    for match in matches:
        body = match.group(1).strip()
        if not body:
            raise DialectError(
                f"```mermaid fence is empty\n  Allowed: {', '.join(ALLOWED_DIALECTS)}"
            )

        token_match = _FIRST_TOKEN_RE.match(body)
        dialect = token_match.group(1) if token_match else body.splitlines()[0].strip()

        if dialect not in ALLOWED_DIALECTS:
            raise DialectError(
                f"unsupported mermaid dialect '{dialect}'\n"
                f"  Allowed: {', '.join(ALLOWED_DIALECTS)}\n"
                "  Reason: only flowchart+subgraph is confirmed to render on all 4"
                " targets (RAISE-15886 T4 — Confluence cell untested for C4*)"
            )

    return dialect
