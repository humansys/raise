"""Deterministic frontmatter extractor for Claude Code memory notes.

RAISE-13911 Task 2 (DD-3). Parses ``name``/``description``/``type``
frontmatter already curated in each memory note — no LLM, no API key
(AC-8). Reuses ``extract_frontmatter()`` from ``memory_index`` (AG2 — the
same regex-based parser that drives ``MEMORY.md`` regeneration), so a note
that is indexable there is parseable here too.

Lives in raise-cli, not raise-core, despite implementing the
``CartridgeExtractor`` Protocol (raise-core): it must reuse
``extract_frontmatter()`` (raise-cli-only) and its scan root is injected by
a caller that resolves ``get_claude_memory_dir()`` (also raise-cli-only,
Claude-Code-specific path knowledge). raise-core has zero dependency on
raise-cli (one-directional layering — see packages/raise-core/pyproject.toml
vs. packages/raise-cli/pyproject.toml), so a raise-core-resident class
cannot import either helper. Protocol conformance is structural (PEP 544),
so this still plugs into ``extract_cartridge()`` unchanged.

Departure from ``YAMLExtractor``/``MarkdownExtractor``: those receive
``paths`` resolved from ``sources:`` globs in ``extractors/config.yaml``.
This extractor ignores ``paths`` entirely — CC memory lives outside the
cartridge/repo tree (``~/.claude/projects/{encoded}/memory/``), so its root
is injected at construction instead of resolved per-call from cartridge-
relative globs.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from raise_cli.core.text import slugify
from raise_cli.memory.memory_index import extract_frontmatter, frontmatter_body
from raise_core.graph.models import GraphNode

if TYPE_CHECKING:
    from raise_core.cartridges.extract import RelationshipSchema

# Mirrors memory_index._IGNORED_DIRS — any path component here excludes the
# file from the scan. `_backup/` in particular must never be ingested: it
# holds superseded/orphaned notes (DD-3, AC-N2 territory).
_IGNORED_DIRS = frozenset({"_backup", "__pycache__", ".git"})


class MemoryFrontmatterExtractor:
    """Extract ``type=memory`` GraphNodes from Claude Code memory notes."""

    def __init__(self, memory_root: Path) -> None:
        """Args: memory_root — the CC memory directory (get_claude_memory_dir())."""
        self._memory_root = memory_root

    def extract(  # noqa: D102 -- Protocol signature, paths unused (see module docstring)
        self,
        paths: list[Path],  # noqa: ARG002
        node_type: str,
        cartridge_name: str,
        *,
        schema: RelationshipSchema | None = None,  # noqa: ARG002
        domain_context: str = "",  # noqa: ARG002
    ) -> list[GraphNode]:
        now = datetime.now(tz=UTC).isoformat()
        nodes: list[GraphNode] = []
        for md_file in self._iter_memory_files():
            node = self._extract_note(md_file, node_type, cartridge_name, now)
            if node is not None:
                nodes.append(node)
        return nodes

    def _extract_note(
        self, md_file: Path, node_type: str, cartridge_name: str, now: str
    ) -> GraphNode | None:
        frontmatter = extract_frontmatter(md_file)
        if frontmatter is None:
            return None
        memory_type = frontmatter.get("type", "").strip()
        if not memory_type:
            return None

        body = frontmatter_body(md_file)
        slug = slugify(md_file.stem)
        return GraphNode(
            id=f"kc-{cartridge_name}-{slug}",
            type=node_type,
            content=body,
            source_file=str(md_file),
            created=now,
            metadata={"cartridge": cartridge_name, "memory_type": memory_type},
        )

    def _iter_memory_files(self) -> list[Path]:
        found: list[Path] = []
        found.extend(self._scan(self._memory_root / "_global", recurse=True))
        found.extend(self._scan(self._memory_root / "_unassigned", recurse=True))
        missions_dir = self._memory_root / "missions"
        if missions_dir.is_dir():
            for mission_dir in sorted(p for p in missions_dir.iterdir() if p.is_dir()):
                found.extend(self._scan(mission_dir, recurse=True))
        found.extend(self._scan(self._memory_root, recurse=False))
        return found

    @staticmethod
    def _scan(directory: Path, *, recurse: bool) -> list[Path]:
        if not directory.is_dir():
            return []
        pattern = "**/*.md" if recurse else "*.md"
        return [
            md_file
            for md_file in sorted(directory.glob(pattern))
            if md_file.name != "MEMORY.md"
            and not any(part in _IGNORED_DIRS for part in md_file.parts)
        ]


__all__ = ["MemoryFrontmatterExtractor"]
