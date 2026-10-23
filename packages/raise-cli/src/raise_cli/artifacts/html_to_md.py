"""Derive a Markdown companion from a self-contained HTML artifact.

RAISE-16870 introduced HTML as a first-class artifact format for governance
documents (self-contained reports published to the RaiSE platform target).
Downstream tooling (artifact-validation gates, grep/diff/git-blame,
search) still expects a paired ``.md`` file next to the ``.html`` one --
this module is the single place that derives it, so every publish path
(MCP tool, CLI) can share it instead of hand-rolling a conversion on
demand (RAISE-17804).

The conversion is intentionally lossy and dependency-free (stdlib
``html.parser`` only, no markdownify/html2text): headings, paragraphs,
lists, bold/italic and links degrade to Markdown syntax; everything else
degrades to plain text. ``<script>``/``<style>`` content is dropped
entirely. It exists to keep the companion readable and searchable, not to
round-trip the original HTML.
"""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

_SKIPPED_TAGS = {"script", "style"}
_BLOCK_TAGS = {"p", "div", "section", "article", "header", "footer", "tr", "table"}
_HEADING_LEVELS = {f"h{n}": n for n in range(1, 7)}


class _HtmlToMdParser(HTMLParser):
    """Minimal streaming HTML -> Markdown-ish text converter (stdlib only)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._out: list[str] = []
        self._skip_depth = 0
        self._link_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIPPED_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in _HEADING_LEVELS or tag in _BLOCK_TAGS or tag in ("br", "li"):
            self._start_structural(tag)
        else:
            self._start_inline(tag, attrs)

    def _start_structural(self, tag: str) -> None:
        """Headings, block containers, line breaks, and list items."""
        if tag in _HEADING_LEVELS:
            self._out.append("\n\n" + "#" * _HEADING_LEVELS[tag] + " ")
        elif tag == "br":
            self._out.append("\n")
        elif tag == "li":
            self._out.append("\n- ")
        else:  # block tag
            self._out.append("\n\n")

    def _start_inline(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Links and inline emphasis markers."""
        if tag == "a":
            href = dict(attrs).get("href")
            self._link_href = href
            if href:
                self._out.append("[")
        elif tag in ("strong", "b"):
            self._out.append("**")
        elif tag in ("em", "i"):
            self._out.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIPPED_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if tag == "a" and self._link_href:
            self._out.append(f"]({self._link_href})")
            self._link_href = None
        elif tag in ("strong", "b"):
            self._out.append("**")
        elif tag in ("em", "i"):
            self._out.append("_")
        elif tag in (*_HEADING_LEVELS, *_BLOCK_TAGS, "li", "ul", "ol"):
            self._out.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._out.append(data)

    def get_markdown(self) -> str:
        text = "".join(self._out)
        text = unescape(text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        stripped = text.strip()
        return f"{stripped}\n" if stripped else ""


def html_to_md(html_content: str) -> str:
    """Convert self-contained HTML content into a readable Markdown companion.

    Best-effort, dependency-free conversion: headings, paragraphs, lists,
    bold/italic and links are preserved as Markdown; everything else
    degrades to plain text. ``<script>``/``<style>`` content is dropped
    entirely so generated CSS/JS never leaks into the companion.
    """
    parser = _HtmlToMdParser()
    parser.feed(html_content)
    parser.close()
    return parser.get_markdown()
