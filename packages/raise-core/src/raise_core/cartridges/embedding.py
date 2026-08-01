"""Cartridge embedding generation.

Provides EmbeddingProvider protocol and implementations for generating
vector embeddings from graph node content. Used by extract_cartridge()
to enable semantic search in the retrieval engine.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

_FINGERPRINTS_FILE = "fingerprints.json"


@dataclass(frozen=True)
class EmbeddingSpec:
    """Identifies the embedding configuration for fingerprinting purposes."""

    model_name: str
    format_version: str
    query_prefix: str
    passage_prefix: str


def compute_node_fingerprint(node_id: str, content: str, spec: EmbeddingSpec) -> str:
    """Return a deterministic SHA-256 hex fingerprint for a node + spec combination."""
    payload = f"{node_id}\x00{content}\x00{spec.model_name}\x00{spec.query_prefix}\x00{spec.passage_prefix}\x00{spec.format_version}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_fingerprints(instances_dir: Path) -> dict[str, str]:
    """Load the fingerprint index from instances_dir.

    Resolves via manifest.json → generation_dir/fingerprints.json if present,
    otherwise falls back to instances_dir/fingerprints.json.
    Returns empty dict when no fingerprint file exists.
    """
    manifest = instances_dir / "manifest.json"
    if manifest.exists():
        with contextlib.suppress(Exception):
            gen_dir_name = json.loads(manifest.read_text(encoding="utf-8")).get(
                "generation_dir", ""
            )
            fp_path = instances_dir / gen_dir_name / _FINGERPRINTS_FILE
            if fp_path.exists():
                return json.loads(fp_path.read_text(encoding="utf-8"))
    fp_path = instances_dir / _FINGERPRINTS_FILE
    if fp_path.exists():
        return json.loads(fp_path.read_text(encoding="utf-8"))
    return {}


def save_fingerprints(index: dict[str, str], instances_dir: Path) -> None:
    """Persist fingerprint index to instances_dir/fingerprints.json."""
    instances_dir.mkdir(parents=True, exist_ok=True)
    (instances_dir / _FINGERPRINTS_FILE).write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8"
    )


def write_embeddings_atomic(
    embeddings: dict[str, list[float]],
    fingerprints: dict[str, str],
    nodes: list[GraphNode],
    spec: EmbeddingSpec,
    instances_dir: Path,
) -> None:
    """Publish an immutable embedding generation atomically.

    Writes matrix + index + fingerprints to a new generation directory, then
    replaces manifest.json with an atomic rename.  Cleans up the previous
    generation directory after publication (best-effort).

    On POSIX, Path.replace() is atomic.  On Windows it is not guaranteed
    cross-volume, but within the same filesystem it is.
    """
    if not embeddings:
        return

    import numpy as np  # noqa: I001

    ids = [n.id for n in nodes if n.id in embeddings]
    if not ids:
        return

    instances_dir.mkdir(parents=True, exist_ok=True)

    # Determine previous generation for cleanup
    manifest_path = instances_dir / "manifest.json"
    prev_gen_dir: str | None = None
    if manifest_path.exists():
        with contextlib.suppress(Exception):
            prev_gen_dir = json.loads(manifest_path.read_text(encoding="utf-8")).get(
                "generation_dir"
            )

    # Write new generation to a unique directory
    gen_id = f"gen-{uuid.uuid4().hex[:12]}"
    gen_dir = instances_dir / gen_id
    gen_dir.mkdir(parents=True)

    matrix = np.array([embeddings[nid] for nid in ids], dtype=np.float32)
    np.save(gen_dir / "embeddings.npy", matrix)
    (gen_dir / "embedding_index.json").write_text(
        json.dumps({nid: i for i, nid in enumerate(ids)}, ensure_ascii=False),
        encoding="utf-8",
    )
    (gen_dir / _FINGERPRINTS_FILE).write_text(
        json.dumps(fingerprints, ensure_ascii=False), encoding="utf-8"
    )
    (gen_dir / "spec.json").write_text(
        json.dumps(
            {
                "model_name": spec.model_name,
                "format_version": spec.format_version,
                "query_prefix": spec.query_prefix,
                "passage_prefix": spec.passage_prefix,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Atomic manifest replacement
    tmp_manifest = instances_dir / f".manifest.{gen_id}.tmp"
    tmp_manifest.write_text(
        json.dumps({"generation_dir": gen_id}, ensure_ascii=False), encoding="utf-8"
    )
    tmp_manifest.replace(manifest_path)

    # Best-effort cleanup of previous generation
    if prev_gen_dir and prev_gen_dir != gen_id:
        with contextlib.suppress(Exception):
            shutil.rmtree(instances_dir / prev_gen_dir, ignore_errors=True)


# Cross-lingual dense embedder (RAISE-9926/ADR-114). e5-base chosen over e5-large:
# e5-large ~1.12 GB RSS OOMs prod VM (1024 MB shared-cpu-1x); e5-base ~730 MB RSS
# fits with margin. avg_top1_cosine ≥ 0.82 on RaiSE ES+EN corpus (S9795.6 3way benchmark,
# not NDCG@10). NDCG@10 baseline on English-only eval corpus = 0.4142 (RAISE-15094).
DEFAULT_MODEL = "intfloat/multilingual-e5-base"
EMBEDDING_DIM = 768

# e5 models require asymmetric prefixes: queries are prefixed "query: " and
# documents/passages "passage: ". The prefixes default to e5's because the model
# above is e5; a non-e5 model would need different (or empty) prefixes passed in.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers.

    Implementations must convert text to fixed-dimension float vectors.
    `embed` encodes documents/passages (ingest side); `embed_query` encodes
    queries (retrieval side). The split exists because e5-family models score
    best with distinct query/passage prefixes.
    """

    def embed(self, texts: list[str]) -> list[list[float]]:  # noqa: D102
        ...

    def embed_query(self, texts: list[str]) -> list[list[float]]:  # noqa: D102
        ...


class SentenceTransformerProvider:
    """Embedding provider using sentence-transformers (local inference)."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        *,
        query_prefix: str = QUERY_PREFIX,
        passage_prefix: str = PASSAGE_PREFIX,
        _model: object | None = None,
    ) -> None:
        # `_model` is a test seam: inject a stub encoder to assert prefixing
        # without downloading the real model.
        if _model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]  # noqa: I001

            _model = SentenceTransformer(model_name)
        self._model = _model
        self._query_prefix = query_prefix
        self._passage_prefix = passage_prefix

    def _encode(self, texts: list[str], prefix: str) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(  # type: ignore[attr-defined]
            [prefix + t for t in texts], convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Encode documents/passages (ingest side)."""
        return self._encode(texts, self._passage_prefix)

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        """Encode queries (retrieval side)."""
        return self._encode(texts, self._query_prefix)


class EmbeddingGenerator:
    """Orchestrates embedding generation for a list of graph nodes."""

    def __init__(self, provider: EmbeddingProvider) -> None:
        self._provider = provider

    def generate(self, nodes: list[GraphNode]) -> dict[str, list[float]]:
        """Generate embeddings for each node's content.

        Returns:
            Mapping of node_id → embedding vector.
        """
        if not nodes:
            return {}
        texts = [n.content for n in nodes]
        vectors = self._provider.embed(texts)
        return {node.id: vec for node, vec in zip(nodes, vectors, strict=True)}

    def generate_incremental(
        self,
        nodes: list[GraphNode],
        existing_embeddings: dict[str, list[float]],
        existing_fingerprints: dict[str, str],
        spec: EmbeddingSpec,
    ) -> tuple[dict[str, list[float]], dict[str, str]]:
        """Generate embeddings only for nodes whose fingerprint changed or is new.

        Reuses existing vectors for nodes with matching fingerprints.
        Nodes absent from `nodes` are excluded from the output (deleted).

        Returns:
            (embeddings, new_fingerprint_index) — both keyed by node_id.
        """
        to_embed: list[GraphNode] = []
        reused: dict[str, list[float]] = {}
        new_fps: dict[str, str] = {}

        for node in nodes:
            fp = compute_node_fingerprint(node.id, node.content, spec)
            new_fps[node.id] = fp
            if (
                fp == existing_fingerprints.get(node.id)
                and node.id in existing_embeddings
            ):
                reused[node.id] = existing_embeddings[node.id]
            else:
                to_embed.append(node)

        fresh: dict[str, list[float]] = {}
        if to_embed:
            texts = [n.content for n in to_embed]
            vectors = self._provider.embed(texts)
            fresh = {n.id: vec for n, vec in zip(to_embed, vectors, strict=True)}

        return {**reused, **fresh}, new_fps


def write_embeddings(
    embeddings: dict[str, list[float]],
    nodes: list[GraphNode],
    instances_dir: Path,
) -> None:
    """Persist embeddings as .npy matrix + index JSON."""
    ids = [n.id for n in nodes if n.id in embeddings]
    if not ids:
        return
    import numpy as np  # noqa: I001

    instances_dir.mkdir(parents=True, exist_ok=True)
    matrix = np.array([embeddings[nid] for nid in ids], dtype=np.float32)
    np.save(instances_dir / "embeddings.npy", matrix)
    index = {nid: i for i, nid in enumerate(ids)}
    (instances_dir / "embedding_index.json").write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8"
    )


__all__ = [
    "DEFAULT_MODEL",
    "EMBEDDING_DIM",
    "PASSAGE_PREFIX",
    "QUERY_PREFIX",
    "EmbeddingGenerator",
    "EmbeddingProvider",
    "EmbeddingSpec",
    "SentenceTransformerProvider",
    "compute_node_fingerprint",
    "load_fingerprints",
    "save_fingerprints",
    "write_embeddings",
    "write_embeddings_atomic",
]
