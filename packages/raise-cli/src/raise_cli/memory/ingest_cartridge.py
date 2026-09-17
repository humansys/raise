"""Generate/refresh the external memory cartridge — RAISE-13911 Task 5.

Scaffolds ``$RAI_HOME/cartridges/memory/`` (external — DD-2 (b), so a
derived index over personal memory is structurally impossible to commit)
on first ``--apply``, runs ``MemoryFrontmatterExtractor`` via
``extract_cartridge()`` (raise-core's generic pipeline: hygiene/dedup,
instance writing, embeddings), and — only on ``--apply`` — re-tiers
``MEMORY.md`` (DD-6/Task 6's wiring, closed here rather than deferred).

Dry-run (default) never writes anything: it runs the extractor directly
(bypassing the scaffold + ``extract_cartridge`` write path entirely) purely
to report a candidate node count.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from raise_cli.config.paths import get_claude_memory_dir, get_global_rai_dir

logger = logging.getLogger(__name__)

MEMORY_CARTRIDGE_NAME = "memory"


class MemoryIngestResult(BaseModel):
    """Outcome of a dry-run preview or a real ``--apply`` ingest."""

    node_count: int
    cartridge_dir: Path
    applied: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def resolve_memory_cartridge_dir(project_root: Path) -> Path:  # noqa: ARG001
    """Resolve the external memory cartridge directory.

    ``project_root`` is accepted (not used to derive the cartridge path —
    it lives under ``$RAI_HOME``, not the repo) so callers have a uniform
    signature with ``get_claude_memory_dir(project_root)`` and so a future
    per-project external layout is not a breaking signature change.
    """
    return get_global_rai_dir() / "cartridges" / MEMORY_CARTRIDGE_NAME


def _assert_external(cartridge_dir: Path, repo_root: Path) -> None:
    """AC-6 guard — the memory cartridge must never resolve under repo_root.

    Structural safety net for DD-2 (b)'s "imposible de commitear por
    construcción" guarantee: even a misconfigured ``RAI_HOME`` pointing
    inside the repo tree must fail loud here rather than silently ingest
    personal memory into a path git can see.
    """
    if cartridge_dir.resolve().is_relative_to(repo_root.resolve()):
        msg = (
            f"Memory cartridge path {cartridge_dir} resolves inside the repo "
            f"root {repo_root} — refusing to ingest personal memory into a "
            "path that could be committed (AC-6). Check $RAI_HOME."
        )
        raise ValueError(msg)


def _write_extractor_config(cartridge_dir: Path) -> None:
    """Write extractors/config.yaml with relationship_mode EXPLICIT 'none'.

    The generic scaffold template defaults to 'guided' — this cartridge
    must override it explicitly (design doc's "Ejemplos" section), since a
    memory node must never gain schema-guided relationships (DD-4 already
    excludes it from cross-cartridge edges; intra-cartridge relationships
    are out of scope for v1 too).
    """
    config: dict[str, Any] = {
        "extractors": [
            {
                "name": "memory",
                "type": "frontmatter",
                "sources": [],
                "node_type": "memory",
                "relationship_mode": "none",
            }
        ]
    }
    config_path = cartridge_dir / "extractors" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _ensure_scaffold(cartridge_dir: Path) -> None:
    """Scaffold CARTRIDGE.yaml + extractors/config.yaml if not already present.

    ``scaffold_cartridge()`` (raise-core) already defaults
    ``source.authority`` to ``"local"`` — no override needed for that field.
    Idempotent: does nothing if the manifest already exists (second
    ``--apply`` reuses the existing scaffold).
    """
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    if manifest_path.exists():
        return
    from raise_core.cartridges.loader import scaffold_cartridge

    scaffold_cartridge(
        base_dir=cartridge_dir.parent,
        cartridge_name=MEMORY_CARTRIDGE_NAME,
        corpus_paths=[],
    )
    _write_extractor_config(cartridge_dir)


def _default_embedding_provider() -> Any | None:
    """Resolve the default embedding provider, degrading gracefully if unavailable."""
    try:
        from raise_cli.embeddings.provider import get_default_provider

        return get_default_provider()
    except (ImportError, RuntimeError) as exc:
        logger.warning("embedding provider unavailable, skipping embeddings: %r", exc)
        return None


def ingest_memory_cartridge(
    project_root: Path,
    *,
    apply: bool = False,
    active_mission_id: str | None = None,
    embedding_provider: Any | None = None,
) -> MemoryIngestResult:
    """Preview (default) or apply the external memory cartridge ingest.

    Dry-run reports a candidate node count and writes nothing. ``--apply``
    scaffolds the cartridge on first run (idempotent thereafter), runs the
    full ``extract_cartridge()`` pipeline (hygiene/dedup + instances +
    embeddings), and re-tiers ``MEMORY.md`` (DD-6) — dry-run never touches
    ``MEMORY.md``.
    """
    from raise_cli.memory.frontmatter_extractor import MemoryFrontmatterExtractor

    cartridge_dir = resolve_memory_cartridge_dir(project_root)
    _assert_external(cartridge_dir, project_root)

    memory_root = get_claude_memory_dir(project_root)
    extractor = MemoryFrontmatterExtractor(memory_root=memory_root)

    if not apply:
        preview_nodes = extractor.extract(
            [], node_type="memory", cartridge_name=MEMORY_CARTRIDGE_NAME
        )
        return MemoryIngestResult(
            node_count=len(preview_nodes),
            cartridge_dir=cartridge_dir,
            applied=False,
        )

    from raise_core.cartridges.extract import extract_cartridge

    _ensure_scaffold(cartridge_dir)
    provider = (
        embedding_provider
        if embedding_provider is not None
        else _default_embedding_provider()
    )
    result = extract_cartridge(
        cartridge_dir,
        extractors={"frontmatter": extractor},
        embedding_provider=provider,
        dry_run=False,
    )

    from raise_cli.memory.memory_index import regenerate_memory_index

    regenerate_memory_index(memory_root, active_mission_id=active_mission_id)

    return MemoryIngestResult(
        node_count=result.node_count,
        cartridge_dir=cartridge_dir,
        applied=True,
        warnings=result.warnings,
        errors=result.errors,
    )


__all__ = [
    "MEMORY_CARTRIDGE_NAME",
    "MemoryIngestResult",
    "ingest_memory_cartridge",
    "resolve_memory_cartridge_dir",
]
