"""Schema migration integrity file — Atlas-style Merkle sum for schema.py migrations.

Generates and verifies `.raise/schema.sum`, a git-tracked file containing a
SHA-256 hash of every migration DDL. When two branches independently add the same
migration version, their schema.sum files differ → Git merge conflict → forced
coordination before merge.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from raise_cli.storage.schema import (
    _MIGRATIONS,  # type: ignore[reportPrivateUsage]
    SCHEMA_VERSION,
)

__all__ = ["SUM_FILE", "write_sum_file", "verify_sum_file"]

SUM_FILE = Path(".raise") / "schema.sum"


def compute_sums() -> dict[str, str]:
    """Compute a 16-char SHA-256 prefix for each migration DDL.

    DDL strings are stripped of leading/trailing whitespace before hashing
    to avoid spurious hash changes from formatting differences.
    """
    return {
        f"V{v + 1}": hashlib.sha256(ddl.strip().encode()).hexdigest()[:16]
        for v, ddl in sorted(_MIGRATIONS.items())
    }


def compute_total(sums: dict[str, str]) -> str:
    """Compute a 32-char SHA-256 of all version hashes combined."""
    return hashlib.sha256(json.dumps(sums, sort_keys=True).encode()).hexdigest()[:32]


def write_sum_file(path: Path = SUM_FILE) -> None:
    """Generate schema.sum at the given path.

    Args:
        path: Output path. Defaults to .raise/schema.sum relative to CWD.
    """
    sums = compute_sums()
    lines = [
        "# RaiSE schema migration integrity",
        "# Auto-generated — do not edit manually",
        "# Update: rai schema sum update | Check: rai schema sum check",
        f"schema_version: {SCHEMA_VERSION}",
        *[f"{k}: {v}" for k, v in sorted(sums.items(), key=lambda x: int(x[0][1:]))],
        f"total: {compute_total(sums)}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_sum_file(path: Path = SUM_FILE) -> tuple[bool, str]:
    """Verify schema.sum matches current schema.py migrations.

    Detects: missing file, stale hashes, unresolved Git merge conflict markers.

    Args:
        path: Path to schema.sum. Defaults to .raise/schema.sum relative to CWD.

    Returns:
        (valid, message) — valid=True means the file is current and conflict-free.
    """
    if not path.exists():
        return False, "schema.sum not found — run: rai schema sum update"
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, "schema.sum is unreadable or corrupt — run: rai schema sum update"
    if "<<<<<<<" in content or "=======" in content:
        return (
            False,
            "schema.sum has unresolved merge conflict — coordinate version numbers with the other epic",
        )
    expected_total = compute_total(compute_sums())
    if f"total: {expected_total}" not in content:
        return False, "schema.sum is stale — run: rai schema sum update"
    return (
        True,
        f"schema.sum valid (schema_version={SCHEMA_VERSION}, {len(_MIGRATIONS)} migrations)",
    )
