"""Markdown → Confluence storage-format converter (RAISE-1679).

TRUSTED-CONTENT-ONLY: this converter does not sanitize HTML. It is intended
for repo-internal markdown authored by trusted developers. Do not expose to
user-supplied input without a sanitization layer.

Fixes RAISE-1679 by converting markdown-authored docs into Confluence Cloud
storage XHTML before hand-off to ``atlassian-python-api``'s
``Confluence.create_page`` / ``update_page`` (which default to
``representation='storage'``).

Fenced code blocks become Confluence ``<ac:structured-macro ac:name="code">``
with a language parameter. Fenced mermaid blocks become
``ac:name="mermaid"`` (or fall back to a code macro with
``language=mermaid`` when the Mermaid Confluence app is not available).
"""

from __future__ import annotations

import re
import uuid

import markdown

_MERMAID_FENCE = re.compile(
    r"^[ \t]*```mermaid[ \t]*\r?\n(?P<body>.*?)\r?\n[ \t]*```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)

_PRE_CODE_BLOCK = re.compile(
    r'<pre><code(?:\s+class="language-(?P<lang>[^"]+)")?>(?P<body>.*?)</code></pre>',
    re.DOTALL,
)


def markdown_to_storage(md: str, *, mermaid_macro: bool = True) -> str:
    """Convert markdown to Confluence storage-format XHTML.

    The mermaid pre/post-processor runs outside the ``markdown`` lib so
    that mermaid content is not HTML-escaped during conversion.
    """
    if not md:
        return ""
    md = md.replace("\r\n", "\n")

    # Per-call sentinel: NUL bytes cannot appear in markdown source; UUID prevents
    # any two calls from sharing tokens, and prevents collision with author text.
    _token_base = f"\x00RAISE1893MERMAID{uuid.uuid4().hex}\x00"

    def _make_token(idx: int) -> str:
        return f"{_token_base}{idx}"

    mermaid_blocks: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        idx = len(mermaid_blocks)
        mermaid_blocks.append(match.group("body"))
        return _make_token(idx)

    md_stashed = _MERMAID_FENCE.sub(_stash, md)

    html = markdown.markdown(
        md_stashed,
        extensions=["fenced_code", "tables", "sane_lists"],
    )

    def _code_macro_sub(match: re.Match[str]) -> str:
        lang = match.group("lang") or ""
        body = _html_unescape(match.group("body"))
        return _make_code_macro(lang, body)

    html = _PRE_CODE_BLOCK.sub(_code_macro_sub, html)

    for idx, body in enumerate(mermaid_blocks):
        token = _make_token(idx)
        replacement = (
            _make_mermaid_macro(body)
            if mermaid_macro
            else _make_code_macro("mermaid", body)
        )
        # Tokens may survive wrapped in <p>...</p> after markdown conversion
        html = html.replace(f"<p>{token}</p>", replacement)
        html = html.replace(token, replacement)

    return html


def _html_unescape(s: str) -> str:
    """Reverse markdown-lib's HTML-escaping inside fenced code blocks.

    Safe inside CDATA, which does not require entity escaping.
    """
    return (
        s.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&amp;", "&")
    )


def _escape_cdata_terminator(body: str) -> str:
    """Split any literal ``]]>`` so it cannot close the enclosing CDATA.

    Standard XML trick: split the payload at ``]]>`` and rejoin with
    ``]]]]><![CDATA[>``, which the XML parser reads as ``]]`` then a
    normal CDATA resume, producing the literal sequence in the output.
    """
    return body.replace("]]>", "]]]]><![CDATA[>")


def _make_code_macro(lang: str, body: str) -> str:
    lang_param = (
        f'<ac:parameter ac:name="language">{lang}</ac:parameter>' if lang else ""
    )
    safe_body = _escape_cdata_terminator(body)
    return (
        '<ac:structured-macro ac:name="code">'
        f"{lang_param}"
        f"<ac:plain-text-body><![CDATA[{safe_body}]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    )


def _make_mermaid_macro(body: str) -> str:
    safe_body = _escape_cdata_terminator(body)
    return (
        '<ac:structured-macro ac:name="mermaid">'
        f"<ac:plain-text-body><![CDATA[{safe_body}]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    )
