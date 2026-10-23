"""Cross-cartridge deduplication pipeline for federated retrieval.

Provides a two-layer deduplication pipeline:
  - Layer A: Content hash dedup (SHA-256 of normalized text)
  - Layer B: Cosine similarity dedup (greedy clustering at threshold)

Design decisions: ADR-100 (Embedding Federation Architecture).
Integration with federated_retrieve: deferred to S-RFCC.I.5.
"""

from __future__ import annotations

import hashlib
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt

from raise_core.graph.retrieval.federation import FederatedCandidate

__all__ = [
    "CanonicalEntry",
    "CanonicalizationMap",
    "DeduplicationMetrics",
    "dedup_cross_cartridge",
]

_WS_RE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class CanonicalEntry:
    """Maps a non-canonical node to its canonical representative."""

    canonical_id: str
    sources: tuple[str, ...]
    merged_ids: tuple[str, ...]
    merge_reason: str


class CanonicalizationMap:
    """Lookup table from non-canonical node IDs to their canonical entries."""

    def __init__(self, entries: dict[str, CanonicalEntry]) -> None:
        """Initialize the map from non-canonical node ID to CanonicalEntry."""
        self._entries: dict[str, CanonicalEntry] = dict(entries)

    def canonical_for(self, node_id: str) -> str:
        """Return canonical_id for node_id, or node_id itself if not in map."""
        entry = self._entries.get(node_id)
        if entry is None:
            return node_id
        return entry.canonical_id

    def sources_for(self, canonical_id: str) -> tuple[str, ...]:
        """Return all non-canonical node IDs merged into canonical_id."""
        result: list[str] = []
        for nid, entry in self._entries.items():
            if entry.canonical_id == canonical_id:
                result.append(nid)
        return tuple(result)

    def __len__(self) -> int:
        """Return number of non-canonical entries in the map."""
        return len(self._entries)

    def __contains__(self, node_id: object) -> bool:
        """Return True if node_id is a non-canonical entry in the map."""
        return node_id in self._entries


class DeduplicationMetrics(BaseModel):
    """Metrics from the deduplication pipeline run."""

    duplicates_exact: int
    duplicates_semantic: int
    total_before: int
    total_after: int
    canonicalization_ratio: float
    merge_policy_picks: dict[str, int]
    processing_time_ms: float


def _content_hash(text: str) -> str:
    """Compute SHA-256 hash of normalized text.

    Normalization: Unicode NFC → casefold → whitespace collapse → strip.
    """
    normalized = unicodedata.normalize("NFC", text)
    casefolded = normalized.casefold()
    collapsed = _WS_RE.sub(" ", casefolded).strip()
    return hashlib.sha256(collapsed.encode("utf-8")).hexdigest()


def _hash_dedup(
    candidates: list[FederatedCandidate],
    node_texts: dict[str, str],
) -> tuple[list[FederatedCandidate], dict[str, CanonicalEntry], int]:
    """Layer A: deduplicate candidates by content hash.

    Groups candidates by SHA-256 hash of their normalized text. Within each
    group, the canonical is the candidate with the highest rrf_score.
    Tiebreaker: lexicographic (source_cartridge, node_id) ascending (smaller wins).

    Candidates with no entry in node_texts are not hashable and skip this layer.

    Returns:
        (canonical_list, entries_map, exact_dedup_count)
    """
    # Separate hashable from non-hashable candidates
    hashable: list[tuple[str, FederatedCandidate]] = []
    no_text: list[FederatedCandidate] = []
    for cand in candidates:
        if cand.node_id in node_texts:
            h = _content_hash(node_texts[cand.node_id])
            hashable.append((h, cand))
        else:
            no_text.append(cand)

    # Group by hash
    groups: dict[str, list[FederatedCandidate]] = {}
    for h, cand in hashable:
        groups.setdefault(h, []).append(cand)

    canonical_list: list[FederatedCandidate] = []
    entries_map: dict[str, CanonicalEntry] = {}
    exact_count = 0

    for group in groups.values():
        if len(group) == 1:
            canonical_list.append(group[0])
            continue
        # Select canonical: highest rrf_score; tiebreak by (source_cartridge, node_id) asc
        max_score = max(c.rrf_score for c in group)
        tied = [c for c in group if c.rrf_score == max_score]
        if len(tied) > 1:
            canonical = min(tied, key=lambda c: (c.source_cartridge, c.node_id))
        else:
            canonical = tied[0]

        canonical_list.append(canonical)
        non_canonicals = [c for c in group if c.node_id != canonical.node_id]
        exact_count += len(non_canonicals)

        for nc in non_canonicals:
            entries_map[nc.node_id] = CanonicalEntry(
                canonical_id=canonical.node_id,
                sources=(nc.node_id,),
                merged_ids=(nc.node_id,),
                merge_reason="content_hash",
            )

    # Preserve rrf_score ordering within canonical_list; append non-hashable at end
    canonical_list.sort(key=lambda c: c.rrf_score, reverse=True)
    return canonical_list + no_text, entries_map, exact_count


def _cosine_dedup(
    candidates: list[FederatedCandidate],
    embeddings: dict[str, npt.NDArray[np.float32]],
    threshold: float = 0.92,
) -> tuple[list[FederatedCandidate], dict[str, CanonicalEntry], int]:
    """Layer B: deduplicate candidates by cosine similarity.

    Greedy clustering: candidates processed in rrf_score desc order (invariant).
    Each candidate is compared against all current cluster leaders. If cosine
    similarity >= threshold with any leader, the candidate is non-canonical.
    Otherwise, it becomes a new cluster leader.

    Candidates without an embedding in the embeddings dict auto-become leaders
    (cannot be compared).

    numpy is imported lazily inside this function body.

    Returns:
        (canonical_list, entries_map, semantic_dedup_count)
    """
    import numpy as np

    if not candidates:
        return [], {}, 0

    # Candidates are assumed sorted by rrf_score desc (invariant from pipeline)
    leaders: list[tuple[FederatedCandidate, npt.NDArray[np.float32]]] = []
    canonical_list: list[FederatedCandidate] = []
    entries_map: dict[str, CanonicalEntry] = {}
    semantic_count = 0

    for cand in candidates:
        emb = embeddings.get(cand.node_id)
        if emb is None:
            # No embedding — auto-becomes a leader, cannot be clustered
            canonical_list.append(cand)
            leaders.append((cand, np.zeros(1, dtype=np.float32)))  # placeholder
            continue

        # Compare against all existing leaders that have embeddings
        merged = False
        norm_emb = np.linalg.norm(emb)
        if norm_emb == 0.0:
            # Zero vector — treat as leader
            canonical_list.append(cand)
            leaders.append((cand, emb))
            continue

        unit_emb = emb / norm_emb

        for leader_cand, leader_emb in leaders:
            # Skip placeholder leaders (no-embedding)
            if (
                leader_emb.shape == (1,)
                and leader_emb[0] == 0.0
                and embeddings.get(leader_cand.node_id) is None
            ):
                continue
            leader_norm = np.linalg.norm(leader_emb)
            if leader_norm == 0.0:
                continue
            unit_leader = leader_emb / leader_norm
            cosine = float(np.dot(unit_emb, unit_leader))
            if cosine >= threshold:
                # Non-canonical — merge into this leader
                entries_map[cand.node_id] = CanonicalEntry(
                    canonical_id=leader_cand.node_id,
                    sources=(cand.node_id,),
                    merged_ids=(cand.node_id,),
                    merge_reason="cosine_similarity",
                )
                semantic_count += 1
                merged = True
                break

        if not merged:
            canonical_list.append(cand)
            leaders.append((cand, emb))

    return canonical_list, entries_map, semantic_count


def dedup_cross_cartridge(
    candidates: list[FederatedCandidate],
    node_texts: dict[str, str],
    embeddings: dict[str, npt.NDArray[np.float32]] | None = None,
    cosine_threshold: float = 0.92,
) -> tuple[list[FederatedCandidate], CanonicalizationMap, DeduplicationMetrics]:
    """Run the two-layer cross-cartridge deduplication pipeline.

    Layer A: Content hash dedup (exact text matches).
    Layer B: Cosine similarity dedup (semantic near-duplicates, if embeddings provided).

    Args:
        candidates: List of FederatedCandidate sorted by rrf_score desc.
        node_texts: Mapping of node_id → full text content.
        embeddings: Optional mapping of node_id → embedding vector.
        cosine_threshold: Cosine similarity threshold for Layer B (default 0.92).

    Returns:
        (deduplicated_candidates, canonicalization_map, metrics)
    """
    start = time.perf_counter()
    total_before = len(candidates)

    after_hash, hash_entries, exact_count = _hash_dedup(candidates, node_texts)

    if embeddings is not None:
        after_cosine, cosine_entries, semantic_count = _cosine_dedup(
            after_hash, embeddings, cosine_threshold
        )
    else:
        after_cosine = after_hash
        cosine_entries = {}
        semantic_count = 0

    all_entries = {**hash_entries, **cosine_entries}
    canon_map = CanonicalizationMap(all_entries)

    total_after = len(after_cosine)
    merged = total_before - total_after
    ratio = merged / total_before if total_before > 0 else 0.0
    elapsed_ms = (time.perf_counter() - start) * 1000

    metrics = DeduplicationMetrics(
        duplicates_exact=exact_count,
        duplicates_semantic=semantic_count,
        total_before=total_before,
        total_after=total_after,
        canonicalization_ratio=ratio,
        merge_policy_picks={"rrf_score": merged},
        processing_time_ms=elapsed_ms,
    )

    return after_cosine, canon_map, metrics
