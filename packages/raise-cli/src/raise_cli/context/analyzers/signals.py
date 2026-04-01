"""Signal scanner for technical debt markers in source files.

Scans for TODO, HACK, FIXME, XXX, DEPRECATED, and custom patterns.
Produces per-file hits and per-module aggregated counts.

Architecture: S1132.0c — Signal Scanner
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field

_SKIP_DIRS = frozenset({"node_modules", "__pycache__", ".git", "dist", "build"})
_TS_EXTENSIONS = frozenset({".ts", ".tsx"})

_DEFAULT_TAGS = ["TODO", "HACK", "FIXME", "XXX", "DEPRECATED", "@deprecated"]


class SignalHit(BaseModel):
    """A single signal occurrence in a source file."""

    file: str = Field(..., description="Relative path to the file")
    line: int = Field(..., description="1-based line number")
    tag: str = Field(..., description="Signal tag (e.g., TODO, HACK)")
    message: str = Field(..., description="Text following the tag")


class ModuleSignals(BaseModel):
    """Aggregated signals for a single module."""

    module_name: str = Field(..., description="Module directory name")
    hits: list[SignalHit] = Field(default_factory=lambda: list[SignalHit]())
    counts: dict[str, int] = Field(
        default_factory=lambda: dict[str, int](),
        description="Tag → count mapping",
    )


class SignalScanner:
    """Scans source files for technical debt signal markers.

    Attributes:
        tags: List of signal tags to scan for.
    """

    def __init__(self, extra_tags: list[str] | None = None) -> None:
        self.tags = list(_DEFAULT_TAGS)
        if extra_tags:
            self.tags.extend(extra_tags)
        # Build regex: match tag followed by optional colon and message
        escaped = [re.escape(t) for t in self.tags]
        # @deprecated needs word boundary handling differently
        pattern = r"(?:" + "|".join(escaped) + r")[:\s]*(.*)"
        self._regex = re.compile(pattern)

    def scan_file(self, file_path: Path) -> list[SignalHit]:
        """Scan a single file for signal markers.

        Args:
            file_path: Path to the source file.

        Returns:
            List of SignalHit for each signal found.
        """
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []

        hits: list[SignalHit] = []
        for line_num, line_text in enumerate(lines, start=1):
            match = self._regex.search(line_text)
            if match:
                full_match = match.group(0)
                message = match.group(1).strip()
                # Extract the tag from the match
                tag = self._extract_tag(full_match)
                if tag:
                    hits.append(
                        SignalHit(
                            file=str(file_path),
                            line=line_num,
                            tag=tag,
                            message=message,
                        )
                    )
        return hits

    def _extract_tag(self, matched_text: str) -> str | None:
        """Extract the signal tag from the matched text.

        Args:
            matched_text: Full regex match string.

        Returns:
            The tag string, or None.
        """
        for tag in self.tags:
            if matched_text.startswith(tag):
                return tag
        return None

    def scan_module(self, module_dir: Path, module_name: str) -> ModuleSignals:
        """Scan all .ts/.tsx files in a module directory.

        Args:
            module_dir: Path to the module directory.
            module_name: Name of the module.

        Returns:
            ModuleSignals with aggregated hits and counts.
        """
        all_hits: list[SignalHit] = []
        for f in sorted(module_dir.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix not in _TS_EXTENSIONS:
                continue
            if f.name.endswith(".d.ts"):
                continue
            all_hits.extend(self.scan_file(f))

        counts = dict(Counter(h.tag for h in all_hits))

        return ModuleSignals(
            module_name=module_name,
            hits=all_hits,
            counts=counts,
        )

    def scan_project(self, src_path: Path) -> list[ModuleSignals]:
        """Scan all modules under a source directory.

        Args:
            src_path: Path to the source root (e.g., project/src/).

        Returns:
            List of ModuleSignals, one per module directory.
        """
        if not src_path.exists():
            return []

        results: list[ModuleSignals] = []
        for entry in sorted(src_path.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith(".") or entry.name in _SKIP_DIRS:
                continue
            # Must have at least one .ts/.tsx file
            has_ts = any(
                f.suffix in _TS_EXTENSIONS and not f.name.endswith(".d.ts")
                for f in entry.rglob("*")
                if f.is_file()
            )
            if not has_ts:
                continue

            result = self.scan_module(entry, entry.name)
            results.append(result)

        return results
