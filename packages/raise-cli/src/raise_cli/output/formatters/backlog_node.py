"""T0/T1 renderer for backlog nodes shared by CLI formatters and MCP (RAISE-16449).

Pure functions over ``Mapping[str, Any]`` node metadata — no ``GraphNode``
dependency — so the same code serves ``GraphNode.metadata`` (CLI formatters)
and the ``properties`` dict returned by the MCP graph backend.

Tiers (design s17000.6, D3.1-D3.2, D3.9):
    T0 — ``render_t0``: one line, key/status/priority/summary/parent. Never
         description, never comments, never dates.
    T1 — ``render_t1``: T0 line + indented detail block (type, labels, fix
         versions, assignee, updated, description, links summary, comment
         count). Never comment bodies.
    T2 — everything on the node (``--format json`` / MCP ``verbose=True``),
         not handled here.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def is_backlog_node(node_type: str, metadata: Mapping[str, Any] | None) -> bool:
    """True when a node tiers as a backlog node.

    Requires ``node_type`` to start with ``backlog.`` AND ``metadata`` to
    carry both ``key`` and ``summary``. Server-first results, hand-built
    nodes, and stale stubs that lack metadata fall back to legacy rendering.
    """
    if not node_type.startswith("backlog."):
        return False
    if not metadata:
        return False
    return bool(metadata.get("key")) and bool(metadata.get("summary"))


def render_t0(metadata: Mapping[str, Any]) -> str:
    """Render the T0 line: '{key} {status} {priority} → {summary} (parent {parent})'.

    Absent fields (priority, parent) are omitted. The summary is never
    truncated — it is the only payload; everything else is overhead.
    """
    key = metadata.get("key", "")
    status = metadata.get("status", "")
    priority = metadata.get("priority")
    summary = metadata.get("summary", "")
    parent = metadata.get("parent")

    line = f"{key} {status}".strip()
    if priority:
        line = f"{line} {priority}"
    line = f"{line} → {summary}"
    if parent:
        line = f"{line} (parent {parent})"
    return line


def render_t1(
    metadata: Mapping[str, Any],
    *,
    updated_at: str | None = None,
    indent: str = "  ",
) -> list[str]:
    """Render the T1 block: T0 line + indented detail lines.

    Reads only ``metadata`` (plus the optional ``updated_at``, which is a
    top-level ``GraphNode`` field, not a metadata key). Never prints
    ``created``/``synced_at`` and never prints comment bodies. Absent
    sections are omitted; absent counts (links, comments) print as 0.
    """
    lines: list[str] = [render_t0(metadata)]

    meta_parts: list[str] = []
    item_type = metadata.get("issue_type") or metadata.get("type")
    if item_type:
        meta_parts.append(str(item_type))
    labels = metadata.get("labels")
    if labels:
        meta_parts.append("labels " + ",".join(labels))
    fix_versions = metadata.get("fix_versions")
    if fix_versions:
        meta_parts.append("fix " + ",".join(fix_versions))
    assignee = metadata.get("assignee")
    if assignee:
        meta_parts.append(str(assignee))
    if updated_at:
        meta_parts.append(f"updated {updated_at}")
    if meta_parts:
        lines.append(indent + " · ".join(meta_parts))

    description = metadata.get("description")
    if description:
        lines.append(f"{indent}description:")
        for description_line in str(description).splitlines():
            lines.append(f"{indent * 2}{description_line}")

    links = metadata.get("links") or []
    if links:
        link_summary = "; ".join(
            f"{link.get('link_type', '')} {link.get('target', '')}".strip()
            for link in links
        )
        lines.append(f"{indent}links: {len(links)} ({link_summary})")
    else:
        lines.append(f"{indent}links: 0")

    comment_count = metadata.get("comment_count") or 0
    truncated_suffix = " (+more on Jira)" if metadata.get("comments_truncated") else ""
    lines.append(f"{indent}comments: {comment_count}{truncated_suffix}")

    return lines
