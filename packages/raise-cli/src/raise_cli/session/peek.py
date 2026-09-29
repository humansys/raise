"""Session peek — ANSI sanitization, header formatting, and output assembly.

Pure string transforms only; no subprocess calls.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from raise_cli.session.catalog.models import RuntimeSessionRecord

_ANSI_ESCAPE = re.compile(
    r"\x1b(?:"
    r"\][^\x07\x1b]*(?:\x07|\x1b\\)"  # OSC sequences — must precede single-char Fe
    r"|[PX^_][^\x1b]*\x1b\\"  # DCS / PM / APC / SOS — must precede single-char Fe
    r"|\[[0-?]*[ -/]*[@-~]"  # CSI sequences
    r"|[@-Z\\-_]"  # single-char Fe sequences — catch-all, must be last
    r")"
)


def sanitize_ansi(text: str) -> str:
    """Strip ANSI escape sequences from *text*."""
    return _ANSI_ESCAPE.sub("", text)


def reflow_text(text: str, width: int) -> str:
    """Wrap lines in *text* to at most *width* characters."""
    if not text:
        return text
    lines: list[str] = []
    for line in text.splitlines():
        if len(line) <= width:
            lines.append(line)
        else:
            for i in range(0, len(line), width):
                lines.append(line[i : i + width])
    return "\n".join(lines)


def format_age(seconds: float) -> str:
    """Return a human-readable age string for *seconds* elapsed."""
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds // 60)}m"
    return f"{int(seconds // 3600)}h"


def format_peek_header(record: RuntimeSessionRecord, *, source_id: str) -> str:
    """Return a single-line banner: ``alias@source · project · activity ~Xm ago``."""
    qualified = record.source_qualified_alias(source_id)
    age_s = (datetime.now(tz=UTC) - record.updated_at).total_seconds()
    age_str = format_age(age_s)
    return f"─── {qualified} · {record.project_id} · activity ~{age_str} ago ───"


def build_peek_output(
    record: RuntimeSessionRecord,
    *,
    source_id: str,
    raw: str,
    cols: int,
) -> str:
    """Assemble the full peek output: header + sanitized + reflowed body."""
    header = format_peek_header(record, source_id=source_id)
    body = reflow_text(sanitize_ansi(raw), cols)
    body_lines = body.strip().splitlines()
    footer = f"[END OF SNAPSHOT — {len(body_lines)} lines captured]"
    return "\n".join([header, body.strip(), footer])
