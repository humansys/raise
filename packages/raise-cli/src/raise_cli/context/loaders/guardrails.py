"""Guardrails loader for the context graph.

Parses governance/guardrails.md during `rai graph build` → list[GuardrailNode].
Pattern: identity.py. Anchors on 5-column Markdown table rows + ID regex.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.compat import portable_path
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

# Matches MUST/SHOULD/COULD (with optional -NOT) + category + number.
# Backtick-wrapped or plain. Case-insensitive.
_ID_RE = re.compile(
    r"^`?((?:MUST|SHOULD|COULD)(?:-NOT)?-[A-Z]+-\d+)`?$",
    re.IGNORECASE,
)

# Markdown table separator row (e.g. |----|----|----|)
_SEP_RE = re.compile(r"^\|[-| :]+\|$")


def load_guardrails(project_root: Path) -> list[GraphNode]:
    """Load guardrail nodes from governance/guardrails.md.

    Parses 5-column Markdown tables. Each valid data row becomes a
    GuardrailNode. `always_on=True` when Level column is MUST.
    Fail-open: returns [] on missing file or any parse error.

    Args:
        project_root: Root directory of the project.

    Returns:
        List of GuardrailNode objects.
    """
    guardrails_file = project_root / "governance" / "guardrails.md"
    if not guardrails_file.is_file():
        return []

    try:
        text = guardrails_file.read_text(encoding="utf-8")
    except OSError:
        return []

    try:
        source_file = portable_path(guardrails_file, project_root)
    except ValueError:
        source_file = str(guardrails_file)

    now = datetime.now(tz=UTC).isoformat()
    return _parse(text, source_file, now)


def _parse(text: str, source_file: str, now: str) -> list[GraphNode]:
    """Parse guardrail rows from Markdown text."""
    nodes: list[GraphNode] = []
    current_category = ""
    in_table = False

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("###"):
            current_category = stripped.lstrip("#").strip()
            in_table = False
            continue

        if not stripped.startswith("|"):
            in_table = False
            continue

        if _SEP_RE.match(stripped):
            in_table = True
            continue

        if not in_table:
            continue

        node = _parse_row(stripped, current_category, source_file, now)
        if node is not None:
            nodes.append(node)

    return nodes


def _parse_row(
    stripped: str, category: str, source_file: str, now: str
) -> GraphNode | None:
    """Parse one table data row into a GuardrailNode, or None if invalid."""
    cols = [c.strip() for c in stripped.split("|") if c.strip()]
    if len(cols) != 5:
        return None

    raw_id, level, guardrail, verification, derived = cols
    m = _ID_RE.match(raw_id)
    if not m:
        return None

    canonical_id = m.group(1).upper()
    if not category:
        logger.debug("guardrail row %s has no ### category parent", canonical_id)

    level_upper = level.upper()
    return GraphNode(
        id=f"guardrail-{canonical_id.lower()}",
        type="guardrail",
        content=guardrail,
        source_file=source_file,
        created=now,
        metadata={
            "always_on": level_upper == "MUST",
            "level": level_upper,
            "category": category,
            "verification": verification,
            "derived_from": derived,
        },
    )
