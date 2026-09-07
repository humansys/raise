"""Generic markdown chunker — configurable heading-level splitting with line numbers."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel


class Chunk(BaseModel):
    """A section of a markdown document, split by heading level."""

    heading: str
    text: str
    line_start: int
    line_end: int


class GenericChunker:
    """Splits markdown files by a configurable heading level."""

    def __init__(self, heading_level: int = 2) -> None:
        if not 1 <= heading_level <= 6:
            msg = f"heading_level must be 1-6, got {heading_level}"
            raise ValueError(msg)
        self._pattern = re.compile(rf"^{'#' * heading_level}\s+(.+)$", re.MULTILINE)

    def split(self, path: Path) -> list[Chunk]:
        """Split a markdown file into chunks by heading level."""
        return self.split_text(path.read_text(encoding="utf-8"))

    def split_text(self, text: str) -> list[Chunk]:
        """Split in-memory markdown text into chunks by heading level.

        Line numbers are relative to ``text``. Callers that strip a prologue
        (e.g. YAML frontmatter) before chunking therefore get body-relative
        lines, not file-relative ones.
        """
        if not text.strip():
            return []

        lines = text.splitlines(keepends=True)
        matches = list(self._pattern.finditer(text))

        if not matches:
            return [Chunk(heading="", text=text, line_start=0, line_end=len(lines))]

        chunks: list[Chunk] = []

        # Preamble before first heading
        pre_end = _offset_to_line(text, matches[0].start())
        preamble = "".join(lines[:pre_end]).strip()
        if preamble:
            chunks.append(
                Chunk(heading="", text=preamble, line_start=0, line_end=pre_end)
            )

        for i, match in enumerate(matches):
            heading = match.group(1).strip()
            start_line = _offset_to_line(text, match.start())
            end_line = (
                _offset_to_line(text, matches[i + 1].start())
                if i + 1 < len(matches)
                else len(lines)
            )
            body = "".join(lines[start_line + 1 : end_line]).strip()
            chunks.append(
                Chunk(
                    heading=heading,
                    text=body,
                    line_start=start_line,
                    line_end=end_line,
                )
            )

        return chunks


def _offset_to_line(text: str, offset: int) -> int:
    return text[:offset].count("\n")


__all__ = ["Chunk", "GenericChunker"]
