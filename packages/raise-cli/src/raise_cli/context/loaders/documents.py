"""Documents loader for the context graph.

Loads freeform documentation (SOPs, RFCs, research, proposals) from configurable
glob patterns as ``document`` nodes.

Configuration: manifest.yaml ``graph.document_sources`` — list of globs relative
to project root. If the section is absent or empty, no documents are loaded.

Two entry points, deliberately kept apart (RAISE-15990):

- :func:`load_documents` — one node per file. This is the cardinality the
  ``rai docs migrate`` planner depends on: one node in, one page published.
- :func:`load_document_chunks` — one node per section, used by ``GraphBuilder``
  so retrieval can land on the relevant section of a long document.

Story: S1700.5 | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from raise_core.cartridges.chunker import Chunk, GenericChunker
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

#: Heading level documents are split at for retrieval nodes. H2 is the RaiSE
#: markdown house style's section level (H1 is the document title).
_CHUNK_HEADING_LEVEL = 2

# Doc types inferred from path segments
_DOC_TYPE_MAP = {
    "sops": "sop",
    "rfcs": "rfc",
    "research": "research",
    "proposals": "proposal",
}

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def document_node_id(rel_path: str) -> str:
    """Derive a document node id from a project-root-relative path.

    The id encodes the whole path, not just the filename stem (RAISE-15989):
    the RaiSE work-item layout repeats basenames (``scope.md``, ``analysis.md``,
    ``retro.md``) under one directory per work item, so stem-derived ids
    collapsed every one of them onto a single node and ``GraphBuilder``'s
    duplicate-id pass then dropped all but the first.

    This is the single derivation point for document identity. Ids for
    sub-parts of a document (e.g. chunks) should be built by suffixing this
    base id rather than re-deriving a slug from the path. Ids are opaque
    exact-match keys — never prefix-match them, since ``doc-a`` is a prefix
    of ``doc-a-b``.

    Known limitation: the slug is flat, so every non-alphanumeric run (path
    separator, underscore, space, existing hyphen) collapses to ``-``. Paths
    that differ only in those characters — ``docs/rfc-001.md`` vs
    ``docs/rfc/001.md`` — still share an id. That residual is accepted rather
    than encoded away: ``GraphBuilder`` reports every id collision as a build
    warning, so the remaining cases surface instead of losing nodes silently.

    Args:
        rel_path: Path relative to the project root, POSIX or Windows style.

    Returns:
        Lowercase, filesystem-safe id of the form ``doc-<slugified-path>``,
        with the file suffix dropped.
    """
    stem_path = PurePosixPath(rel_path.replace("\\", "/")).with_suffix("")
    slug = _SLUG_RE.sub("-", str(stem_path).lower()).strip("-")
    return f"doc-{slug}"


@dataclass(frozen=True)
class _ParsedDocument:
    """A markdown file parsed once, shared by both loader entry points."""

    rel_path: str
    body: str
    title: str
    doc_type: str
    tags: list[str]
    created: str


def load_documents(project_root: Path, sources: list[str]) -> list[GraphNode]:
    """Load documents matching glob patterns as ``document`` graph nodes.

    One node per matched file, carrying the **whole body** as content
    (RAISE-15990: it used to carry a lead-paragraph summary, which discarded
    ~95% of the corpus). Callers that depend on one-node-per-file cardinality
    — ``rai docs migrate`` — must use this, not
    :func:`load_document_chunks`.

    Args:
        project_root: Project root directory (globs are resolved from here).
        sources: List of glob patterns (e.g., ``["dev/sops/*.md"]``).

    Returns:
        List of GraphNode instances (one per matched file). Missing files and
        unreadable files are skipped with a debug log.
    """
    return [_document_node(doc) for doc in _iter_documents(project_root, sources)]


def load_document_chunks(
    project_root: Path,
    sources: list[str],
    heading_level: int = _CHUNK_HEADING_LEVEL,
) -> list[GraphNode]:
    """Load documents as one ``document`` node per section (RAISE-15990).

    A whole document as a single node retrieves poorly: the TF-IDF scorer
    normalizes term frequency by document length and compares cosine
    magnitude, so a long document is diluted to near-zero similarity against
    a short query. Section-level nodes keep vectors small and matches sharp.

    Chunk ids are :func:`document_node_id` suffixed with the chunk ordinal, so
    document identity keeps a single derivation point (RAISE-15989) and
    chunks of the same file cannot collide.

    Known limitation: heading detection is not fence-aware, so a ``##`` line
    inside a fenced code block opens a new chunk. No text is lost — only the
    boundary is off — so this is left as-is rather than fixed here.

    Args:
        project_root: Project root directory (globs are resolved from here).
        sources: List of glob patterns (e.g., ``["dev/sops/*.md"]``).
        heading_level: Markdown heading level to split at (default H2).

    Returns:
        List of GraphNode instances, one per section, in document order. A
        document with no body still yields one title-only node so it stays
        findable.
    """
    chunker = GenericChunker(heading_level=heading_level)
    nodes: list[GraphNode] = []
    for doc in _iter_documents(project_root, sources):
        nodes.extend(_chunk_nodes(doc, chunker))
    return nodes


def _iter_documents(
    project_root: Path, sources: list[str]
) -> Iterator[_ParsedDocument]:
    """Yield each glob-matched markdown file, parsed once, deduplicated."""
    if not sources:
        return

    seen_paths: set[Path] = set()
    for pattern in sources:
        for path in sorted(project_root.glob(pattern)):
            if not path.is_file() or path in seen_paths:
                continue
            seen_paths.add(path)
            doc = _parse_document(path, project_root)
            if doc is not None:
                yield doc


def _parse_document(path: Path, project_root: Path) -> _ParsedDocument | None:
    """Parse a single markdown file. Returns None if it cannot be read."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Cannot read %s: %s", path, exc)
        return None

    rel_path = str(path.relative_to(project_root))
    frontmatter, body = _split_frontmatter(content)

    try:
        created = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    except OSError:
        created = datetime.now(UTC).isoformat()

    return _ParsedDocument(
        rel_path=rel_path,
        body=body.strip(),
        title=str(frontmatter.get("title") or _extract_h1(body) or path.stem),
        doc_type=str(frontmatter.get("doc_type") or _infer_doc_type(rel_path)),
        tags=_parse_tags(frontmatter.get("tags")),
        created=created,
    )


def _document_node(doc: _ParsedDocument) -> GraphNode:
    """Build the file-level node for a parsed document."""
    return GraphNode(
        id=document_node_id(doc.rel_path),
        type="document",
        content=doc.body or doc.title,
        source_file=doc.rel_path,
        created=doc.created,
        metadata=_base_metadata(doc),
    )


def _chunk_nodes(doc: _ParsedDocument, chunker: GenericChunker) -> list[GraphNode]:
    """Build the section-level nodes for a parsed document."""
    base_id = document_node_id(doc.rel_path)
    chunks = chunker.split_text(doc.body)
    if not chunks:
        # Empty body: keep the document findable by its title.
        chunks = [Chunk(heading="", text=doc.title, line_start=0, line_end=0)]

    return [
        GraphNode(
            id=f"{base_id}-{index}",
            type="document",
            content=_chunk_content(chunk) or doc.title,
            source_file=doc.rel_path,
            created=doc.created,
            metadata={
                **_base_metadata(doc),
                "heading": chunk.heading,
                "chunk_index": index,
                "chunk_count": len(chunks),
            },
        )
        for index, chunk in enumerate(chunks)
    ]


def _base_metadata(doc: _ParsedDocument) -> dict[str, Any]:
    return {"title": doc.title, "doc_type": doc.doc_type, "tags": doc.tags}


def _chunk_content(chunk: Chunk) -> str:
    """Prepend the section heading so its terms are searchable in the chunk."""
    if not chunk.heading:
        return chunk.text
    return f"{chunk.heading}\n\n{chunk.text}".strip()


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
