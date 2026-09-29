"""Content hash computation for pattern dedup (ADR-069).

Canonical hash shared between CLI and server — must produce identical
output for the same (content, type, context) triple.
"""

from __future__ import annotations

import hashlib
import json


def content_hash(content: str, pattern_type: str, context: list[str]) -> str:
    """Compute SHA-256 content hash for dedup detection.

    Canonical form: JSON of {content, type, context} with sorted keys,
    no whitespace, lowercased values, sorted context list.
    """
    canonical = json.dumps(
        {
            "content": content.strip().lower(),
            "type": pattern_type.strip().lower(),
            "context": sorted(c.strip().lower() for c in context),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"
