"""Secret pattern scanning for cartridge publish safety (RAISE-14974)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = ["SecretMatch", "scan_for_secrets"]


@dataclass(frozen=True)
class SecretMatch:
    """A single secret pattern match found in a cartridge file."""

    pattern_name: str
    file_path: str  # relative to cartridge_dir
    line_number: int


_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Generic API Key", re.compile(r"api[_-]?key\s*[=:]\s*\S{8,}", re.IGNORECASE)),
    (
        "PEM Private Key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "Bearer Token",
        re.compile(r"(?:bearer|token)\s*[=:]\s*\S{20,}", re.IGNORECASE),
    ),
]

_MAX_FILE_SIZE = 1_048_576  # 1 MB


def scan_for_secrets(cartridge_dir: Path) -> list[SecretMatch]:
    """Scan all text files in cartridge_dir for common secret patterns.

    Skips binary files (UnicodeDecodeError) and files larger than 1 MB.
    Returns matches sorted by file path then line number.
    """
    matches: list[SecretMatch] = []
    for path in sorted(cartridge_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.stat().st_size > _MAX_FILE_SIZE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable file
        rel = str(path.relative_to(cartridge_dir))
        for name, pattern in _PATTERNS:
            for i, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    matches.append(
                        SecretMatch(pattern_name=name, file_path=rel, line_number=i)
                    )
    return matches
