"""Cartridge synonym loader — per-cartridge vocabulary bridge for retrieval."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SYNONYMS_FILE = "synonyms.json"


def load_synonyms(instances_dir: Path) -> dict[str, frozenset[str]]:
    """Load per-cartridge synonym map from instances/synonyms.json.

    Returns a bidirectional dict: each term maps to a frozenset of its
    synonyms. Returns {} if the file is missing or malformed (graceful
    degradation — a cartridge without synonyms still works, just without
    query expansion).
    """
    path = instances_dir / _SYNONYMS_FILE
    if not path.exists():
        return {}

    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("Failed to parse synonyms at %s", path)
        return {}

    if not isinstance(raw, dict):
        return {}

    groups = raw.get("groups")
    if not isinstance(groups, list):
        return {}

    result: dict[str, frozenset[str]] = {}
    for group in groups:
        if not isinstance(group, list) or len(group) < 2:
            continue
        terms = [str(t).lower() for t in group]
        term_set = frozenset(terms)
        for term in terms:
            result[term] = term_set - {term}

    return result
