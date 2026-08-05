"""Documents loader for the context graph.

Loads freeform documentation (SOPs, RFCs, research, proposals) from configurable
glob patterns as ``document`` nodes.

Configuration: manifest.yaml ``graph.document_sources`` — list of globs relative
to project root. If the section is absent or empty, no documents are loaded.

Story: S1700.5 | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

# Doc types inferred from path segments
_DOC_TYPE_MAP = {
    "sops": "sop",
    "rfcs": "rfc",
    "research": "research",
    "proposals": "proposal",
}

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def load_documents(project_root: Path, sources: list[str]) -> list[GraphNode]:
    """Load documents matching glob patterns as ``document`` graph nodes.

    Args:
        project_root: Project root directory (globs are resolved from here).
        sources: List of glob patterns (e.g., ``["dev/sops/*.md"]``).

    Returns:
        List of GraphNode instances (one per matched file). Missing files and
        unreadable files are skipped with a debug log.
    """
    if not sources:
        return []

    nodes: list[GraphNode] = []
    seen_paths: set[Path] = set()
    for pattern in sources:
        for path in sorted(project_root.glob(pattern)):
            if not path.is_file() or path in seen_paths:
                continue
            seen_paths.add(path)
            node = _load_single_document(path, project_root)
            if node is not None:
                nodes.append(node)

    return nodes


def _load_single_document(path: Path, project_root: Path) -> GraphNode | None:
    """Parse a single markdown file into a document GraphNode."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Cannot read %s: %s", path, exc)
        return None

    rel_path = str(path.relative_to(project_root))
    frontmatter, body = _split_frontmatter(content)

    title = frontmatter.get("title") or _extract_h1(body) or path.stem
    doc_type = frontmatter.get("doc_type") or _infer_doc_type(rel_path)
    tags = _parse_tags(frontmatter.get("tags"))
    summary = _extract_summary(body)

    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    node_id = f"doc-{slug}"

    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    except OSError:
        mtime = datetime.now(UTC).isoformat()

    return GraphNode(
        id=node_id,
        type="document",
        content=summary or str(title),
        source_file=rel_path,
        created=mtime,
        metadata={
            "title": str(title),
            "doc_type": doc_type,
            "tags": tags,
        },
    )


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from body. Returns ({}, content) if no frontmatter."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    try:
        raw: object = yaml.safe_load(content[3:end])
        if isinstance(raw, dict):
            return {str(k): v for k, v in raw.items()}, content[end + 3 :].lstrip()  # type: ignore[union-attr]
    except yaml.YAMLError:
        pass
    return {}, content


def _extract_h1(body: str) -> str | None:
    """Extract first H1 heading from body."""
    m = _H1_RE.search(body)
    return m.group(1).strip() if m else None


def _extract_summary(body: str, max_chars: int = 500) -> str:
    """Extract first non-heading paragraph as summary."""
    lines = body.splitlines()
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith("#"):
            continue
        paragraph.append(stripped)

    summary = " ".join(paragraph)
    return summary[:max_chars].strip()


def _infer_doc_type(rel_path: str) -> str:
    """Infer doc_type from path segments. Returns 'document' if no match."""
    parts = rel_path.lower().split("/")
    for part in parts:
        if part in _DOC_TYPE_MAP:
            return _DOC_TYPE_MAP[part]
    return "document"


def _parse_tags(raw: Any) -> list[str]:
    """Parse tags field — accept list or comma-separated string."""
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]  # type: ignore[redundant-expr]
    if isinstance(raw, str):
        return [t.strip() for t in raw.split(",") if t.strip()]
    return []
