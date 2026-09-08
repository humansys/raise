"""The ``<!-- rai: -->`` MR governance block (RAISE-15009, moved here by RAISE-16773).

Until S3 this block was assembled by bash inside ``rai-mr-create`` Step 4 —
prompt-layer logic replicated across ten synced copies of the skill, enforceable
only by hoping the agent ran it. D-S3-3 moves construction here so that every
adapter-mediated MR carries it whether or not the caller remembered, and so the
D6 regression check is a unit test instead of a line in a checklist.

The byte format is a contract (RAISE-15009). Existing MR descriptions are parsed
by consumers that expect exactly::

    <!-- rai: worktree=/path, harness=claude_code, session=SES-177 -->

one space after the colon, ``", "`` between pairs, one space before ``-->``, keys
in that order, empty keys omitted entirely. This module reproduces the previous
bash output byte for byte with one deliberate difference: when nothing resolves,
the bash emitted an empty ``<!-- rai: -->`` husk and this returns nothing, which
is what the skill's own verification text always claimed happened.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_GIT_TIMEOUT_S = 10.0


def build_governance_block(
    *, worktree: str = "", harness: str = "", session: str = ""
) -> str:
    """Render the metadata comment block.

    Args:
        worktree: Absolute path of the checkout the MR was created from.
        harness: Agent runtime that drove the work, e.g. ``claude_code``.
        session: RaiSE session id, e.g. ``SES-177``.

    Returns:
        The block, or ``""`` when no value resolved. Values that are blank or
        whitespace are dropped rather than emitted as ``key=``, which would look
        like recorded data rather than an absence.
    """
    pairs = [
        (key, value.strip())
        for key, value in (
            ("worktree", worktree),
            ("harness", harness),
            ("session", session),
        )
        if value.strip()
    ]
    if not pairs:
        return ""

    rendered = ", ".join(f"{key}={value}" for key, value in pairs)
    return f"<!-- rai: {rendered} -->"


def append_governance_block(
    description: str, *, worktree: str = "", harness: str = "", session: str = ""
) -> str:
    """Prepend the block to an MR description, before the human-readable content.

    RAISE-16904: the block goes first so it survives GitLab CI's ~2700-char
    truncation of ``CI_MERGE_REQUEST_DESCRIPTION``. The HTML comment is
    invisible in rendered markdown, so there is no visual impact.

    Returns:
        The description unchanged when no metadata resolved.
    """
    block = build_governance_block(worktree=worktree, harness=harness, session=session)
    if not block:
        return description

    body = description.lstrip()
    if not body:
        return block
    return f"{block}\n\n{body}"


def resolve_worktree(project: Path | None = None) -> str:
    """Best-effort absolute path of the current checkout.

    Falls back to the working directory when git is unavailable or this is not a
    repository. Metadata is best-effort by design: a missing value omits a key,
    it never blocks the MR.
    """
    start = project if project is not None else Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return str(start)

    root = result.stdout.strip()
    if result.returncode != 0 or not root:
        return str(start)
    return root
