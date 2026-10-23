"""Dataset loaders for TREC qrels, corpus, and queries."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str:
    """Read a text file, transparently decompressing ``.gz`` paths."""
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8")
    return path.read_text(encoding="utf-8")


class QrelsFormatError(Exception):
    """Raised when a qrels file has invalid TREC format."""


def load_qrels(path: Path | str) -> dict[str, dict[str, int]]:
    """Load TREC-format qrels file.

    Expected format: ``query_id<TAB>iteration<TAB>doc_id<TAB>relevance``

    Returns:
        Nested dict ``{query_id: {doc_id: relevance_grade}}``.
    """
    path = Path(path)
    qrels: dict[str, dict[str, int]] = {}

    for line_num, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            msg = (
                f"Invalid qrels at line {line_num}: expected 4 tab-separated "
                f"columns (query_id, iteration, doc_id, relevance), "
                f"got {len(parts)} columns.\n"
                f'Line content: "{line}"'
            )
            raise QrelsFormatError(msg)

        query_id, _iteration, doc_id, relevance_str = parts

        try:
            relevance = int(relevance_str)
        except ValueError:
            msg = (
                f"Invalid qrels at line {line_num}: relevance must be an "
                f'integer, got "{relevance_str}".\n'
                f'Line content: "{line}"'
            )
            raise QrelsFormatError(msg) from None

        if query_id not in qrels:
            qrels[query_id] = {}
        qrels[query_id][doc_id] = relevance

    return qrels


def load_corpus(path: Path | str) -> list[dict[str, Any]]:
    """Load corpus fixture JSON (plain or ``.gz``).

    Returns:
        List of node dicts with at least ``id`` and ``content`` keys.
    """
    path = Path(path)
    data = json.loads(_read_text(path))
    return list(data["nodes"])


def load_corpus_edges(path: Path | str) -> list[dict[str, Any]]:
    """Load the optional ``edges`` section from a corpus fixture.

    Returns:
        List of edge dicts ``{source, target, type}``. Empty list when
        the fixture has no edges section (backward compatible).
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("edges", []))


def load_queries(path: Path | str) -> dict[str, dict[str, Any]]:
    """Load queries JSON.

    Returns:
        Dict ``{query_id: {text, category, source_cartridge, ...}}``.
    """
    path = Path(path)
    return dict(json.loads(path.read_text(encoding="utf-8")))
