"""Naming drift detection between code symbols and domain vocabulary.

Compares symbol names from the diff against TermNode canonical names and
aliases loaded from the knowledge graph. Returns recommendation strings —
never blocking errors (DDD-3, RAISE-16487).
"""

from __future__ import annotations

import re
from typing import Any


def _normalise(name: str) -> str:
    """Lowercase and convert underscores/hyphens to spaces."""
    return re.sub(r"[_\-\s]+", " ", name.lower().strip())


def detect_naming_drift(
    symbols: list[str],
    terms: list[dict[str, Any]],
) -> list[str]:
    """Return recommendation strings for symbols with no match in domain vocabulary.

    Args:
        symbols: Public symbol names extracted from the diff (function/class names).
        terms: Dicts with 'canonical_name' and optional 'aliases' list — as returned
               by ``rai graph query --types term --format json``.

    Returns:
        List of recommendation strings. Empty when all symbols match or terms is empty.
    """
    if not terms or not symbols:
        return []

    vocab: list[tuple[str, list[str]]] = []
    for term in terms:
        canon_raw = term.get("canonical_name") or ""
        canon = _normalise(str(canon_raw))
        raw_aliases = term.get("aliases") or []
        aliases = [
            _normalise(str(a))
            for a in (raw_aliases if isinstance(raw_aliases, list) else [])
        ]
        if canon:
            vocab.append((canon, aliases))

    if not vocab:
        return []

    recommendations: list[str] = []
    for sym in symbols:
        norm = _normalise(sym)
        matched = any(norm == canon or norm in aliases for canon, aliases in vocab)
        if not matched:
            known = ", ".join(f"`{c}`" for c, _ in vocab[:3])
            suffix = "…" if len(vocab) > 3 else ""
            recommendations.append(
                f"Naming: `{sym}` has no match in known vocabulary "
                f"({known}{suffix}). If this concept exists by another name, "
                f"consider aligning."
            )

    return recommendations
