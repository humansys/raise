"""Regression test for RAISE-735: no stale 'raise' command references."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Commands that exist (or existed) as CLI subcommands.
# Pattern matches: raise <cmd>, `raise <cmd>`, 'raise <cmd>'
_STALE_PATTERN = re.compile(
    r"""(?<![.\-_/a-zA-Z])raise\s+"""  # "raise " not preceded by . - _ / alpha
    r"""(?:init|session|context|memory|graph|validate|parse|pull|kata"""
    r"""|hydrate|audit|check|discover|info|profile|signal|pattern"""
    r"""|backlog|mcp|gate|skill|doctor|release|publish|adapter|base"""
    r"""|--help|-V|--version)""",
)

# Directories to scan
_REPO_ROOT = Path(__file__).resolve().parents[4]  # raise-commons root
_SOURCE_DIR = _REPO_ROOT / "packages" / "raise-cli" / "src"
_FRAMEWORK_DIR = _REPO_ROOT / "framework"


def _collect_violations(directory: Path, glob: str) -> list[str]:
    """Find files with stale 'raise <cmd>' references."""
    violations: list[str] = []
    for path in sorted(directory.rglob(glob)):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if _STALE_PATTERN.search(line):
                rel = path.relative_to(_REPO_ROOT)
                violations.append(f"{rel}:{i}: {line.strip()}")
    return violations


class TestNoStaleRaiseRefs:
    """RAISE-735: all CLI command references must use 'rai', not 'raise'."""

    def test_source_files(self) -> None:
        violations = _collect_violations(_SOURCE_DIR, "*.py")
        assert violations == [], (
            f"Stale 'raise' command references in source:\n"
            + "\n".join(violations)
        )

    def test_framework_docs(self) -> None:
        violations = _collect_violations(_FRAMEWORK_DIR, "*.md")
        assert violations == [], (
            f"Stale 'raise' command references in framework:\n"
            + "\n".join(violations)
        )
