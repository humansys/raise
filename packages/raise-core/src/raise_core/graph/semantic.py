"""Local numpy-based semantic search fallback.

Provides cosine similarity search over .npy embeddings for development
environments without raise-server. Loads embeddings.npy + embedding_index.json
from cartridge instances directories.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt

from raise_core.graph.retrieval.models import SemanticResult

logger = logging.getLogger(__name__)


class NumpySemanticSearch:
    """Cosine similarity search using numpy — local dev fallback."""

    def __init__(self, embeddings_dir: Path) -> None:
        self._matrix: npt.NDArray[np.float32] | None = None
        self._index: dict[str, int] | None = None
        self._ids: list[str] = []
        self._load(embeddings_dir)

    def _load(self, embeddings_dir: Path) -> None:
        npy_path = embeddings_dir / "embeddings.npy"
        index_path = embeddings_dir / "embedding_index.json"
        if not npy_path.exists() or not index_path.exists():
            logger.debug("No embeddings found at %s", embeddings_dir)
            return
        self._matrix = np.load(npy_path).astype(np.float32)
        self._index = json.loads(index_path.read_text(encoding="utf-8"))
        self._ids = sorted(self._index, key=lambda k: self._index[k])  # type: ignore[index]

    def search_by_vector(
        self, query_vec: list[float], limit: int = 10
    ) -> list[SemanticResult]:
        """Search by pre-computed embedding vector."""
        if self._matrix is None or len(self._ids) == 0:
            return []

        q = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q = q / q_norm

        norms = np.linalg.norm(self._matrix, axis=1)
        norms = np.where(norms == 0, 1, norms)
        normalized = self._matrix / norms[:, np.newaxis]

        similarities = normalized @ q
        top_k = min(limit, len(self._ids))
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            SemanticResult(
                node_id=self._ids[i],
                similarity=float(similarities[i]),
            )
            for i in top_indices
        ]

    @classmethod
    def from_dirs(cls, dirs: list[Path]) -> NumpySemanticSearch:
        """Create a fused instance from multiple cartridge embeddings directories.

        Concatenates .npy matrices row-wise and merges index dicts. Directories
        without embeddings.npy are silently skipped. Directories whose .npy is
        corrupt or unreadable are also skipped with a warning (ADR-118 graceful
        degradation — one bad cartridge must not crash the whole query).
        """
        instance = cls.__new__(cls)
        matrices: list[npt.NDArray[np.float32]] = []
        ids: list[str] = []

        for d in dirs:
            # Resolve via manifest if present (RAISE-14952 incremental format)
            manifest = d / "manifest.json"
            if manifest.exists():
                try:
                    gen_dir_name = json.loads(manifest.read_text(encoding="utf-8")).get(
                        "generation_dir", ""
                    )
                    gen_dir = d / gen_dir_name
                    if (gen_dir / "embeddings.npy").exists() and (
                        gen_dir / "embedding_index.json"
                    ).exists():
                        d = gen_dir
                except (OSError, ValueError, KeyError):
                    pass

            npy_path = d / "embeddings.npy"
            index_path = d / "embedding_index.json"
            if not npy_path.exists() or not index_path.exists():
                logger.debug("Skipping %s — no embeddings found", d)
                continue
            try:
                matrix = np.load(npy_path).astype(np.float32)
                index: dict[str, int] = json.loads(
                    index_path.read_text(encoding="utf-8")
                )
            except (ValueError, OSError, Exception) as exc:
                logger.warning("Skipping %s — failed to load embeddings: %s", d, exc)
                continue
            dir_ids = sorted(index, key=lambda k: index[k])
            matrices.append(matrix)
            ids.extend(dir_ids)

        if matrices:
            try:
                instance._matrix = np.concatenate(matrices, axis=0)
            except ValueError as exc:
                logger.warning(
                    "Embedding matrix concatenation failed (dim mismatch across "
                    "cartridges): %s — falling back to first compatible set",
                    exc,
                )
                # Keep only the first matrix to preserve partial results rather
                # than losing everything. The dim-mismatched entry is already
                # loaded but we can't concatenate — use what we have.
                instance._matrix = matrices[0]
                ids = ids[: len(matrices[0])]
        else:
            instance._matrix = None

        instance._ids = ids
        instance._index = {nid: i for i, nid in enumerate(ids)}
        return instance


__all__ = ["NumpySemanticSearch", "SemanticResult"]
