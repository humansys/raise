"""ADF ↔ Markdown conversion for Jira Cloud (BASE-048 / S2503.4).

Public API:
  adf_to_markdown(value) -> str   — ADF dict → Markdown
  markdown_to_adf(text)  -> dict  — Markdown → ADF doc node

All other symbols are module-private helpers.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, cast

# ── ADF → Markdown ───────────────────────────────────────────────────
#
# Dispatch-table design: each node type maps to a handler function.
# _adf_walk() is the single entry point; _ADF_DISPATCH is populated
# after all handlers are defined.


def _adf_walk(node: dict[str, Any], buf: list[str]) -> None:
    """Dispatch an ADF node to its registered handler."""
    node_type = node.get("type", "")
    handler = _ADF_DISPATCH.get(node_type)
    if handler is not None:
        handler(node, buf)
    elif node_type:
        buf.append(f"[unsupported: {node_type}]")


def _adf_children(node: dict[str, Any], buf: list[str]) -> None:
    for child in cast("list[Any]", node.get("content") or []):
        _adf_walk(child, buf)


def _adf_block(node: dict[str, Any], buf: list[str]) -> None:
    _adf_children(node, buf)
    buf.append("\n")


def _adf_text(node: dict[str, Any], buf: list[str]) -> None:
    text = str(node.get("text", ""))
    marks: set[str | None] = {
        m.get("type") for m in cast("list[dict[str, Any]]", node.get("marks") or [])
    }
    if marks & {"strong", "em", "code"}:
        inner = text.strip()
        prefix = text[: len(text) - len(text.lstrip())]
        suffix = text[len(text.rstrip()) :]
        if "strong" in marks:
            text = f"{prefix}**{inner}**{suffix}"
        elif "em" in marks:
            text = f"{prefix}*{inner}*{suffix}"
        else:
            text = f"{prefix}`{inner}`{suffix}"
    buf.append(text)


def _adf_heading(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    level = int(attrs.get("level", 1))
    buf.append("#" * level + " ")
    _adf_children(node, buf)
    buf.append("\n")


def _adf_code_block(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    buf.append(f"```{attrs.get('language', '')}\n")
    _adf_children(node, buf)
    if buf and buf[-1] != "\n":
        buf.append("\n")
    buf.append("```\n")


def _adf_list_item(node: dict[str, Any], buf: list[str]) -> None:
    buf.append("- ")
    _adf_children(node, buf)
    if buf and buf[-1] != "\n":
        buf.append("\n")


def _adf_mention(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    buf.append(f"@{attrs.get('text', attrs.get('id', '?'))}")


def _adf_inline_card(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    url = attrs.get("url", "")
    buf.append(f"[{url}]({url})")


def _adf_media(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    buf.append(f"!({attrs.get('id', '')})")


def _adf_media_group(node: dict[str, Any], buf: list[str]) -> None:
    _adf_children(node, buf)
    buf.append("\n")


def _adf_cell_text(cell: dict[str, Any]) -> str:
    """Return flattened Markdown text for a single tableCell/tableHeader."""
    parts: list[str] = []
    _adf_children(cell, parts)
    return "".join(parts).strip()


def _adf_table(node: dict[str, Any], buf: list[str]) -> None:
    rows = [
        [_adf_cell_text(c) for c in cast("list[Any]", r.get("content") or [])]
        for r in cast("list[Any]", node.get("content") or [])
    ]
    if not rows:
        return
    header = rows[0]
    buf.append("| " + " | ".join(header) + " |\n")
    buf.append("|" + "|".join("---" for _ in header) + "|\n")
    for row in rows[1:]:
        buf.append("| " + " | ".join(row) + " |\n")


def _adf_panel(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    panel_type = attrs.get("panelType", "info")
    inner: list[str] = []
    _adf_children(node, inner)
    for line in "".join(inner).strip().splitlines() or [""]:
        buf.append(f"> [{panel_type}] {line}\n")


def _adf_expand(node: dict[str, Any], buf: list[str]) -> None:
    attrs = cast("dict[str, Any]", node.get("attrs") or {})
    inner: list[str] = []
    _adf_children(node, inner)
    buf.append(f"> **{attrs.get('title', '')}**\n")
    for line in "".join(inner).strip().splitlines() or [""]:
        buf.append(f"> {line}\n")


_ADF_DISPATCH: dict[str, Callable[[dict[str, Any], list[str]], None]] = {
    "text": _adf_text,
    "hardBreak": lambda _n, b: b.append("\n"),
    "mention": _adf_mention,
    "inlineCard": _adf_inline_card,
    "media": _adf_media,
    "mediaSingle": _adf_media_group,
    "mediaGroup": _adf_media_group,
    "table": _adf_table,
    "tableRow": _adf_children,
    "tableCell": _adf_children,
    "tableHeader": _adf_children,
    "panel": _adf_panel,
    "expand": _adf_expand,
    "nestedExpand": _adf_expand,
    "listItem": _adf_list_item,
    "codeBlock": _adf_code_block,
    "heading": _adf_heading,
    "paragraph": _adf_block,
    "blockquote": _adf_block,
    "doc": _adf_children,
    "bulletList": _adf_children,
    "orderedList": _adf_children,
}


def adf_to_markdown(value: object) -> str:
    """Convert ADF dict to Markdown. Passes plain strings through unchanged."""
    if not value:
        return ""
    if not isinstance(value, dict):
        return str(value)
    buf: list[str] = []
    _adf_walk(cast("dict[str, Any]", value), buf)
    return "".join(buf).strip()


# ── Markdown → ADF ───────────────────────────────────────────────────
#
# Custom block parser (state machine over lines) + inline regex chain.
# No external dependencies — markdown>=3.6 already in pyproject but
# MD→HTML→ADF double conversion is avoided for simplicity.

_MD_INLINE_RE = re.compile(
    r"(\*\*(.+?)\*\*)"  # bold
    r"|(\*(.+?)\*)"  # italic
    r"|(`(.+?)`)"  # code
    r"|(\[(.+?)\]\((.+?)\))",  # link
)


def _md_inline(text: str) -> list[dict[str, Any]]:
    """Parse inline Markdown marks → list of ADF text nodes."""
    nodes: list[dict[str, Any]] = []
    pos = 0
    for m in _MD_INLINE_RE.finditer(text):
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos : m.start()]})
        if m.group(1):  # bold
            nodes.append(
                {"type": "text", "text": m.group(2), "marks": [{"type": "strong"}]}
            )
        elif m.group(3):  # italic
            nodes.append(
                {"type": "text", "text": m.group(4), "marks": [{"type": "em"}]}
            )
        elif m.group(5):  # code
            nodes.append(
                {"type": "text", "text": m.group(6), "marks": [{"type": "code"}]}
            )
        else:  # link
            nodes.append(
                {
                    "type": "text",
                    "text": m.group(8),
                    "marks": [{"type": "link", "attrs": {"href": m.group(9)}}],
                }
            )
        pos = m.end()
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})
    return nodes or [{"type": "text", "text": text}]


def _md_paragraph(text: str) -> dict[str, Any]:
    return {"type": "paragraph", "content": _md_inline(text)}


def _md_table_to_adf(lines: list[str]) -> dict[str, Any]:
    """Parse GFM table lines into ADF table node."""
    rows: list[dict[str, Any]] = []
    for i, line in enumerate(lines):
        if re.match(r"^\|[-| :]+\|?\s*$", line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cell_type = "tableHeader" if i == 0 else "tableCell"
        rows.append(
            {
                "type": "tableRow",
                "content": [
                    {
                        "type": cell_type,
                        "content": [_md_paragraph(c)],
                    }
                    for c in cells
                ],
            }
        )
    return {"type": "table", "content": rows}


def _is_md_block_start(line: str) -> bool:
    """Return True if line opens a structural block (not a plain paragraph)."""
    return bool(
        re.match(r"^#{1,6}\s", line)
        or line.startswith("```")
        or line.startswith("> ")
        or line.startswith("|")
        or re.match(r"^[*\-] ", line)
        or re.match(r"^\d+\. ", line)
        or re.match(r"^---+\s*$", line)
    )


def _consume_code_fence(
    lines: list[str], i: int, lang: str
) -> tuple[tuple[str, list[str]], int]:
    code: list[str] = []
    i += 1
    while i < len(lines) and not lines[i].startswith("```"):
        code.append(lines[i])
        i += 1
    return ("codeBlock:" + lang, code), i + 1


def _consume_bq(lines: list[str], i: int) -> tuple[tuple[str, list[str]], int]:
    bq: list[str] = []
    while i < len(lines) and lines[i].startswith("> "):
        bq.append(lines[i][2:])
        i += 1
    return ("blockquote", bq), i


def _consume_tbl(lines: list[str], i: int) -> tuple[tuple[str, list[str]], int]:
    tbl: list[str] = []
    while i < len(lines) and lines[i].startswith("|"):
        tbl.append(lines[i])
        i += 1
    return ("table", tbl), i


def _consume_list_md(
    lines: list[str], i: int, pattern: str, block_type: str
) -> tuple[tuple[str, list[str]], int]:
    items: list[str] = []
    while i < len(lines) and re.match(pattern, lines[i]):
        items.append(re.sub(pattern, "", lines[i]))
        i += 1
    return (block_type, items), i


def _consume_para(lines: list[str], i: int) -> tuple[tuple[str, list[str]] | None, int]:
    para: list[str] = []
    while i < len(lines) and lines[i].strip() and not _is_md_block_start(lines[i]):
        para.append(lines[i])
        i += 1
    return (("paragraph", para) if para else None), i


def _consume_md_block(
    lines: list[str], i: int
) -> tuple[tuple[str, list[str]] | None, int]:
    """Consume one block from lines[i:] and return (block, new_i)."""
    line = lines[i]
    fence = re.match(r"^```(\w*)", line)
    if fence:
        return _consume_code_fence(lines, i, fence.group(1))
    hm = re.match(r"^(#{1,6})\s+(.*)", line)
    if hm:
        return (f"heading:{len(hm.group(1))}", [hm.group(2)]), i + 1
    if re.match(r"^---+\s*$", line):
        return ("rule", []), i + 1
    if line.startswith("> "):
        return _consume_bq(lines, i)
    if line.startswith("|"):
        return _consume_tbl(lines, i)
    if re.match(r"^[*\-] ", line):
        return _consume_list_md(lines, i, r"^[*\-] ", "bulletList")
    if re.match(r"^\d+\. ", line):
        return _consume_list_md(lines, i, r"^\d+\. ", "orderedList")
    return _consume_para(lines, i)


def _md_blocks(text: str) -> list[tuple[str, list[str]]]:
    """Split Markdown text into (block_type, lines) tuples."""
    blocks: list[tuple[str, list[str]]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        result, i = _consume_md_block(lines, i)
        if result is not None:
            blocks.append(result)
    return blocks


def _md_list_node(block_type: str, items: list[str]) -> dict[str, Any]:
    return {
        "type": block_type,
        "content": [
            {"type": "listItem", "content": [_md_paragraph(item)]} for item in items
        ],
    }


def _md_block_to_adf(block_type: str, lines: list[str]) -> dict[str, Any]:
    """Convert a single parsed block to ADF node."""
    if block_type.startswith("heading:"):
        level = int(block_type.split(":")[1])
        return {
            "type": "heading",
            "attrs": {"level": level},
            "content": _md_inline(lines[0] if lines else ""),
        }
    if block_type.startswith("codeBlock:"):
        lang = block_type.split(":", 1)[1]
        code = "\n".join(lines)
        node: dict[str, Any] = {
            "type": "codeBlock",
            "attrs": {"language": lang},
            "content": [{"type": "text", "text": code}],
        }
        return node
    if block_type == "rule":
        return {"type": "rule"}
    if block_type == "blockquote":
        return {"type": "blockquote", "content": [_md_paragraph(" ".join(lines))]}
    if block_type == "table":
        return _md_table_to_adf(lines)
    if block_type in ("bulletList", "orderedList"):
        return _md_list_node(block_type, lines)
    # paragraph (default)
    return _md_paragraph(" ".join(lines))


def markdown_to_adf(text: str) -> dict[str, Any]:
    """Convert Markdown text to ADF doc node."""
    if not text.strip():
        return {"type": "doc", "version": 1, "content": []}
    content = [_md_block_to_adf(btype, lines) for btype, lines in _md_blocks(text)]
    return {"type": "doc", "version": 1, "content": content}


_adf_to_markdown = adf_to_markdown
_markdown_to_adf = markdown_to_adf
