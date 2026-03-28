#!/usr/bin/env python3
"""Build the RaiSE Strategic Dossier from Confluence.

Reads the dossier index page from Confluence, fetches all listed pages
in order, and assembles them into a single markdown file optimized for
LLM context.

Auth: reads from .raise/adapters/confluence.yaml or env vars.
Order: defined by the index page in Confluence (not hardcoded).

Usage:
    python dev/scripts/build-dossier.py
    python dev/scripts/build-dossier.py --output /tmp/dossier.md
    python dev/scripts/build-dossier.py --index-id 3145302059
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import requests
import yaml


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_INDEX_PAGE_ID = "3145302059"
DEFAULT_OUTPUT = "dev/output/raise-strategic-dossier.md"
DEFAULT_CONFIG = ".raise/adapters/confluence.yaml"
CONFLUENCE_SPACE = "STRAT"


class ConfluenceAuth(NamedTuple):
    url: str
    user: str
    token: str


def load_auth(config_path: str | None = None) -> ConfluenceAuth:
    """Load Confluence auth from .env, yaml config, or env vars.

    Priority: .env file → yaml config → environment variables.
    """
    import os

    # Try .env file first (dotenv format)
    env_paths = [".env", str(Path.home() / "Code" / "raise-commons" / ".env")]
    for env_path in env_paths:
        if Path(env_path).exists():
            env_vars = _parse_dotenv(env_path)
            url = env_vars.get("JIRA_URL", env_vars.get("CONFLUENCE_URL", ""))
            user = env_vars.get("CONFLUENCE_USERNAME", env_vars.get("CONFLUENCE_USER", ""))
            token = env_vars.get("CONFLUENCE_API_TOKEN", "")
            if url and user and token:
                return ConfluenceAuth(url=url.rstrip("/"), user=user, token=token)

    # Try yaml config
    paths_to_try = [
        config_path,
        DEFAULT_CONFIG,
        str(Path.home() / ".raise" / "adapters" / "confluence.yaml"),
    ]

    for p in paths_to_try:
        if p and Path(p).exists():
            with open(p) as f:
                cfg = yaml.safe_load(f)
            if cfg and "url" in cfg:
                return ConfluenceAuth(
                    url=cfg["url"].rstrip("/"),
                    user=cfg["user"],
                    token=cfg["token"],
                )

    # Fallback to env vars
    url = os.environ.get("JIRA_URL", os.environ.get("CONFLUENCE_URL", ""))
    user = os.environ.get("CONFLUENCE_USERNAME", os.environ.get("CONFLUENCE_USER", ""))
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")

    if url and user and token:
        return ConfluenceAuth(url=url.rstrip("/"), user=user, token=token)

    print(
        "ERROR: No Confluence auth found.\n"
        "Add JIRA_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN to .env,\n"
        f"or create {DEFAULT_CONFIG} with url/user/token fields.",
        file=sys.stderr,
    )
    sys.exit(1)


def _parse_dotenv(path: str) -> dict[str, str]:
    """Parse a .env file into a dict. Ignores comments and blank lines."""
    result: dict[str, str] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                result[key] = value
    return result


# ---------------------------------------------------------------------------
# Confluence API
# ---------------------------------------------------------------------------


def confluence_get(auth: ConfluenceAuth, endpoint: str, params: dict | None = None) -> dict:
    """GET request to Confluence REST API v2."""
    resp = requests.get(
        f"{auth.url}/wiki/api/v2{endpoint}",
        params=params or {},
        auth=(auth.user, auth.token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_page_content_markdown(auth: ConfluenceAuth, page_id: str) -> str:
    """Fetch a page's body in 'atlas_doc_format' and convert to markdown-ish text.

    The v2 API can return body in storage or atlas_doc_format.
    We use the v1 API with expand=body.export_view for cleaner HTML,
    then do a lightweight HTML-to-markdown conversion.
    """
    # Use v1 API for export_view (cleanest HTML output)
    resp = requests.get(
        f"{auth.url}/wiki/rest/api/content/{page_id}",
        params={"expand": "body.export_view"},
        auth=(auth.user, auth.token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    html = data["body"]["export_view"]["value"]
    return html_to_markdown(html)


def get_page_by_title(auth: ConfluenceAuth, title: str, space_key: str = CONFLUENCE_SPACE) -> dict | None:
    """Find a page by exact title in a space. Returns page dict or None."""
    # Try STRAT first, then RGTM
    for space in [space_key, "RGTM"]:
        data = confluence_get(
            auth,
            "/pages",
            params={"title": title, "space-id": get_space_id(auth, space), "limit": 1},
        )
        results = data.get("results", [])
        if results:
            return results[0]
    return None


_space_id_cache: dict[str, str] = {}


def get_space_id(auth: ConfluenceAuth, space_key: str) -> str:
    """Get space ID from space key (cached)."""
    if space_key not in _space_id_cache:
        data = confluence_get(auth, "/spaces", params={"keys": space_key, "limit": 1})
        results = data.get("results", [])
        if not results:
            print(f"ERROR: Space '{space_key}' not found", file=sys.stderr)
            sys.exit(1)
        _space_id_cache[space_key] = results[0]["id"]
    return _space_id_cache[space_key]


def search_pages_by_title(auth: ConfluenceAuth, title: str) -> list[dict]:
    """Search for pages by title using CQL (fallback for cross-space search)."""
    resp = requests.get(
        f"{auth.url}/wiki/rest/api/content/search",
        params={"cql": f'title = "{title}" AND type = page', "limit": 5},
        auth=(auth.user, auth.token),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


# ---------------------------------------------------------------------------
# HTML to Markdown (lightweight, no dependencies)
# ---------------------------------------------------------------------------


def html_to_markdown(html: str) -> str:
    """Convert Confluence export HTML to readable markdown.

    This is a lightweight converter — not perfect but good enough for
    assembling a dossier. Handles headings, paragraphs, lists, tables,
    bold, italic, code blocks, and links.
    """
    import html as html_mod

    text = html

    # Remove style/script tags
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)

    # Headings
    for i in range(6, 0, -1):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m, level=i: f"\n{'#' * level} {m.group(1).strip()}\n",
            text,
            flags=re.DOTALL,
        )

    # Bold / italic
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.DOTALL)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.DOTALL)

    # Code blocks
    text = re.sub(
        r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
        lambda m: f"\n```\n{html_mod.unescape(m.group(1).strip())}\n```\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: f"\n```\n{m.group(1).strip()}\n```\n", text, flags=re.DOTALL)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL)

    # Links
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.DOTALL)

    # Lists
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", text, flags=re.DOTALL)
    text = re.sub(r"</?[ou]l[^>]*>", "\n", text)

    # Table handling (simple)
    text = re.sub(r"<th[^>]*>(.*?)</th>", r"| \1 ", text, flags=re.DOTALL)
    text = re.sub(r"<td[^>]*>(.*?)</td>", r"| \1 ", text, flags=re.DOTALL)
    text = re.sub(r"<tr[^>]*>", "", text)
    text = re.sub(r"</tr>", " |\n", text)
    text = re.sub(r"</?table[^>]*>", "\n", text)
    text = re.sub(r"</?thead[^>]*>", "", text)
    text = re.sub(r"</?tbody[^>]*>", "", text)

    # Paragraphs and line breaks
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\1\n", text, flags=re.DOTALL)
    text = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>", lambda m: "\n> " + m.group(1).strip() + "\n", text, flags=re.DOTALL)

    # Horizontal rules
    text = re.sub(r"<hr[^>]*/?>", "\n---\n", text)

    # Strip remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Unescape HTML entities
    text = html_mod.unescape(text)

    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


# ---------------------------------------------------------------------------
# Index parser
# ---------------------------------------------------------------------------


class Section(NamedTuple):
    number: str
    title: str
    pages: list[str]  # page titles in order


def parse_index(markdown: str) -> list[Section]:
    """Parse the dossier index page into ordered sections with page lists.

    Expected format:
        ## 1. Visión e Identidad
        - Page Title One
        - Page Title Two

        ## 2. Modelo de Producto
        - Page Title Three
    """
    sections: list[Section] = []
    current_section: Section | None = None

    for line in markdown.split("\n"):
        line = line.strip()

        # Match section header: "## 1. Title" or "1. Title" (after Confluence rendering)
        section_match = re.match(r"^(?:#{1,3}\s+)?(\d+)\.\s+(.+)$", line)
        if section_match:
            if current_section:
                sections.append(current_section)
            current_section = Section(
                number=section_match.group(1),
                title=section_match.group(2).strip(),
                pages=[],
            )
            continue

        # Match page entry: "- Page Title" or "* Page Title"
        page_match = re.match(r"^[-*]\s+(.+)$", line)
        if page_match and current_section:
            current_section.pages.append(page_match.group(1).strip())

    if current_section:
        sections.append(current_section)

    return sections


# ---------------------------------------------------------------------------
# Dossier assembler
# ---------------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars / 4."""
    return math.ceil(len(text) / 4)


def build_dossier(auth: ConfluenceAuth, index_page_id: str) -> str:
    """Build the full dossier markdown from the Confluence index page."""
    # 1. Fetch and parse index
    print(f"Fetching index page {index_page_id}...", file=sys.stderr)
    index_content = get_page_content_markdown(auth, index_page_id)
    sections = parse_index(index_content)

    if not sections:
        print("ERROR: No sections found in index page", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(sections)} sections, {sum(len(s.pages) for s in sections)} pages", file=sys.stderr)

    # 2. Fetch all pages
    pages_content: dict[str, str] = {}  # title -> markdown content
    total_pages = sum(len(s.pages) for s in sections)
    fetched = 0

    for section in sections:
        for page_title in section.pages:
            fetched += 1
            print(f"  [{fetched}/{total_pages}] {page_title}...", file=sys.stderr)

            # Find page by title (try CQL search)
            results = search_pages_by_title(auth, page_title)
            if not results:
                print(f"    WARNING: Page not found: '{page_title}'", file=sys.stderr)
                pages_content[page_title] = f"*Page not found: {page_title}*"
                continue

            page_id = results[0]["id"]
            content = get_page_content_markdown(auth, page_id)
            pages_content[page_title] = content

    # 3. Assemble dossier
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts: list[str] = []

    # Header
    parts.append("# RaiSE Strategic Dossier")
    parts.append("")
    parts.append(f"> Generated: {now} | Pages: {total_pages} | Source: Confluence STRAT space")
    parts.append(">")
    parts.append("> This document contains the complete strategic context for RaiSE —")
    parts.append("> product, market, GTM, partnerships, evidence, and roadmap.")
    parts.append("> Assembled automatically from Confluence pages labeled `dossier`.")
    parts.append("")

    # Table of contents
    parts.append("## Table of Contents")
    parts.append("")
    for section in sections:
        parts.append(f"- **{section.number}. {section.title}** ({len(section.pages)} pages)")
        for page_title in section.pages:
            parts.append(f"  - {page_title}")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Sections
    for section in sections:
        parts.append(f"# {section.number}. {section.title}")
        parts.append("")

        for page_title in section.pages:
            content = pages_content.get(page_title, f"*Page not found: {page_title}*")
            parts.append(f"## {page_title}")
            parts.append("")
            parts.append(content)
            parts.append("")
            parts.append("---")
            parts.append("")

    dossier = "\n".join(parts)

    # Add token count to header
    tokens = estimate_tokens(dossier)
    dossier = dossier.replace(
        f"Pages: {total_pages} |",
        f"Pages: {total_pages} | Est. tokens: ~{tokens // 1000}k |",
    )

    return dossier


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RaiSE Strategic Dossier from Confluence")
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--index-id",
        default=DEFAULT_INDEX_PAGE_ID,
        help=f"Confluence page ID of the dossier index (default: {DEFAULT_INDEX_PAGE_ID})",
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help=f"Path to confluence.yaml config (default: {DEFAULT_CONFIG})",
    )
    args = parser.parse_args()

    auth = load_auth(args.config)
    print(f"Connected to {auth.url}", file=sys.stderr)

    dossier = build_dossier(auth, args.index_id)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dossier, encoding="utf-8")

    tokens = estimate_tokens(dossier)
    print(f"\nDossier written to {output_path}", file=sys.stderr)
    print(f"Size: {len(dossier):,} chars | Est. tokens: ~{tokens // 1000}k", file=sys.stderr)


if __name__ == "__main__":
    main()
