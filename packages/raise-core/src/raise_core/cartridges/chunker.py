"""Generic markdown chunker — configurable heading-level splitting with line numbers."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

# Límite máximo de caracteres por chunk en el path sin headings.
# Fundamento (ADR-114): intfloat/multilingual-e5-base tiene 512 tokens de límite.
# A ~4 chars/token (ES/EN mixto), ceiling real ≈ 2.048 chars.
# 1.800 deja buffer para tokens especiales y texto denso.
MAX_CHUNK_CHARS = 1_800


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

        When no headings are found, the text is split by paragraphs to ensure
        no chunk exceeds MAX_CHUNK_CHARS (RAISE-18709).
        """
        if not text.strip():
            return []

        lines = text.splitlines(keepends=True)
        matches = list(self._pattern.finditer(text))

        if not matches:
            if len(text) <= MAX_CHUNK_CHARS:
                return [Chunk(heading="", text=text, line_start=0, line_end=len(lines))]
            segments = _split_by_paragraphs(text)
            return [
                Chunk(heading="", text=seg, line_start=0, line_end=len(lines))
                for seg in segments
            ]

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


def _split_by_paragraphs(text: str) -> list[str]:
    r"""Divide texto en segmentos de ≤MAX_CHUNK_CHARS separando por doble salto de línea.

    Si un párrafo individual supera MAX_CHUNK_CHARS, se subdivide por líneas simples
    (caso real: tablas markdown con solo \\n entre filas, sin \\n\\n).
    Hard cap solo en líneas individuales que por sí solas superen el límite.
    """
    paragraphs = re.split(r"\n{2,}", text.strip())
    segments: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= MAX_CHUNK_CHARS:
            current = candidate
        else:
            if current:
                segments.append(current)
            current = ""
            if len(para) > MAX_CHUNK_CHARS:
                # RAISE-18709: párrafo gigante sin saltos dobles (ej. tabla markdown)
                # → subdividir por líneas simples para no perder contenido
                for line in para.splitlines():
                    line_cand = f"{current}\n{line}".strip() if current else line
                    if len(line_cand) <= MAX_CHUNK_CHARS:
                        current = line_cand
                    else:
                        if current:
                            segments.append(current)
                        current = line[:MAX_CHUNK_CHARS]  # hard cap en línea gigante
            else:
                current = para
    if current:
        segments.append(current)
    return segments or [text[:MAX_CHUNK_CHARS]]


def _offset_to_line(text: str, offset: int) -> int:
    return text[:offset].count("\n")


__all__ = ["Chunk", "GenericChunker", "MAX_CHUNK_CHARS"]
