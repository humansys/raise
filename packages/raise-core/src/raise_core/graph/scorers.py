"""Concrete SemanticScorer implementations for the retrieval engine.

Two backends: NumpySemanticScorer (local dev fallback) and
ServerSemanticScorer (raise-server pgvector). Both implement the
SemanticScorer + CandidateSearcher protocols from retrieval.engine.

Also provides the shared hybrid scorer (TF-IDF ⊕ dense, α-blend) and
InMemorySemanticScorer (TF-IDF, stdlib-only) — the single source of truth
for both eval and production hybrid scoring (ADR-120).
"""

# drift: ignore — este módulo cita legítimamente varios ADRs que gobiernan sus
# backends (ADR-117/118/120); la densidad de story-tokens es documentación de
# diseño, no accretion. Exención pre-existente (drift-story-accretion CAND-05).

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Protocol

import httpx


class _ScorerBackend(Protocol):
    """Combined protocol satisfied by all scorer backends.

    Both ``score_nodes`` (SemanticScorer) and ``search_candidates``
    (CandidateSearcher) are required — CompositeSemanticScorer delegates
    both methods to its primary and fallback.
    """

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]: ...

    def search_candidates(
        self, query: str, limit: int = 20
    ) -> list[dict[str, Any]]: ...


logger = logging.getLogger(__name__)


class NumpySemanticScorer:
    """SemanticScorer + CandidateSearcher backed by local numpy cosine similarity."""

    def __init__(self, embeddings_dirs: list[Path], provider: Any) -> None:
        from raise_core.graph.semantic import NumpySemanticSearch

        self._search = NumpySemanticSearch.from_dirs(embeddings_dirs)
        self._provider = provider

    def _embed_query(self, query: str) -> list[float] | None:
        try:
            # Query side: embed_query applies the e5 "query: " prefix (RAISE-9756).
            vecs = self._provider.embed_query([query])
        except Exception:
            logger.warning("EmbeddingProvider.embed_query failed for query")
            return None
        return vecs[0] if vecs else None

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        vec = self._embed_query(query)
        if vec is None:
            return {}
        requested = set(node_ids)
        results = self._search.search_by_vector(vec, limit=1000)
        return {r.node_id: r.similarity for r in results if r.node_id in requested}

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by cosine similarity over .npy embeddings."""
        vec = self._embed_query(query)
        if vec is None:
            return []
        results = self._search.search_by_vector(vec, limit=limit)
        return [{"node_id": r.node_id, "similarity": r.similarity} for r in results]


class ServerSemanticScorer:
    """SemanticScorer + CandidateSearcher backed by raise-server pgvector endpoint."""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        sem_alpha: float | None = None,
    ) -> None:
        self._url = f"{server_url.rstrip('/')}/api/v2/graph/semantic-search"
        self._api_key = api_key
        self._sem_alpha = sem_alpha
        self._unreachable = False

    def reset(self) -> None:
        """Clear the reachability latch (RAISE-11749).

        Call once per logical query (e.g. at the start of a federated
        per-cartridge loop) so a confirmed network failure only skips the
        redundant HTTP attempts for the *rest of that query*, not forever —
        the scorer instance is long-lived (CLI/MCP singleton) and must
        re-probe on the next query.
        """
        self._unreachable = False

    def _search_remote(self, query: str, limit: int) -> list[dict[str, Any]]:
        if self._unreachable:
            # Already confirmed unreachable this query — skip the HTTP
            # attempt entirely (RAISE-11749: unreachable != empty).
            return []
        payload: dict[str, Any] = {"query": query, "limit": limit}
        if self._sem_alpha is not None and self._sem_alpha > 0:
            payload["sem_alpha"] = self._sem_alpha
        try:
            response = httpx.post(
                self._url,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=10.0,
            )
            response.raise_for_status()
        except Exception:
            logger.warning("ServerSemanticScorer request failed")
            self._unreachable = True
            return []
        # Reachable but empty is a legitimate result, not a failure — do NOT
        # latch here (empty != unreachable).
        return response.json().get("results", [])

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        requested = set(node_ids)
        results = self._search_remote(query, limit=len(node_ids) * 2)
        return {
            r["node_id"]: r["similarity"] for r in results if r["node_id"] in requested
        }

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by pgvector cosine distance."""
        return self._search_remote(query, limit=limit)


class CompositeSemanticScorer:
    """Server-first SemanticScorer with graceful numpy fallback (ADR-118).

    Returns primary results when non-empty; falls through to fallback on empty.
    Trigger is empty-result, not a network probe — simplest safe choice.
    """

    def __init__(self, primary: _ScorerBackend, fallback: _ScorerBackend) -> None:
        self._primary = primary
        self._fallback = fallback

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        result = self._primary.score_nodes(query, node_ids)
        if result:
            return result
        return self._fallback.score_nodes(query, node_ids)

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates; fall to numpy when server yields nothing."""
        results = self._primary.search_candidates(query, limit)
        if results:
            return results
        return self._fallback.search_candidates(query, limit)

    def reset(self) -> None:
        """Forward reset to primary/fallback when they support it (RAISE-11749).

        Composite semantics (ADR-118, server-first/empty-fallback) stay
        byte-identical — this only clears any reachability latch the
        underlying backends may hold, safely (no-op when unsupported).
        """
        for backend in (self._primary, self._fallback):
            backend_reset = getattr(backend, "reset", None)
            if callable(backend_reset):
                backend_reset()


class ServerFederatedScorer:
    """Federated search backed by raise-server /federated-search endpoint."""

    def __init__(self, server_url: str, api_key: str) -> None:
        self._url = f"{server_url.rstrip('/')}/api/v2/graph/federated-search"
        self._api_key = api_key

    def federated_search(
        self,
        query: str,
        cartridge_names: list[str],
        limit: int = 20,
        rrf_k: int = 60,
        sem_alpha: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search across cartridges via server-side RRF merge.

        When ``sem_alpha > 0``, the server will apply TF-IDF α-blend re-rank
        on each per-cartridge dense retrieval (AC5).
        """
        payload: dict[str, Any] = {
            "query": query,
            "cartridge_names": cartridge_names,
            "limit": limit,
            "rrf_k": rrf_k,
        }
        if sem_alpha is not None and sem_alpha > 0:
            payload["sem_alpha"] = sem_alpha
        try:
            response = httpx.post(
                self._url,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=15.0,
            )
            response.raise_for_status()
        except Exception:
            logger.warning("ServerFederatedScorer request failed")
            return []
        return response.json().get("results", [])


SEM_ALPHA: float = 0.3
"""Default α-blend weight for TF-IDF in the hybrid scorer (RAISE-10203 spike)."""


class InMemorySemanticScorer:
    """TF-IDF-based semantic scorer — no neural deps required.

    Builds a term-frequency index from corpus node content and computes
    cosine similarity against queries at scoring time. Uses only stdlib
    (math) — no numpy, no sentence-transformers.

    Implements SemanticScorer + CandidateSearcher protocols so it can be
    used standalone or as the TF-IDF branch of HybridSemanticScorer.
    """

    def __init__(self, corpus: list[dict[str, Any]]) -> None:
        self._vectors: dict[str, dict[str, float]] = {}
        self._idf: dict[str, float] = {}
        self._build_index(corpus)

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()

    def _build_index(self, corpus: list[dict[str, Any]]) -> None:
        doc_freq: dict[str, int] = {}
        tf_docs: dict[str, dict[str, float]] = {}
        n_docs = len(corpus)

        for node in corpus:
            nid = node["id"]
            tokens = self._tokenize(node.get("content", ""))
            tf: dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0.0) + 1.0
            norm = max(len(tokens), 1)
            tf_docs[nid] = {t: c / norm for t, c in tf.items()}
            for t in set(tokens):
                doc_freq[t] = doc_freq.get(t, 0) + 1

        self._idf = {t: math.log((n_docs + 1) / (df + 1)) for t, df in doc_freq.items()}
        self._vectors = {
            nid: {t: freq * self._idf.get(t, 0.0) for t, freq in tf.items()}
            for nid, tf in tf_docs.items()
        }

    def _query_vector(self, query: str) -> dict[str, float]:
        tokens = self._tokenize(query)
        tf: dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        norm = max(len(tokens), 1)
        return {t: (c / norm) * self._idf.get(t, 0.0) for t, c in tf.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        keys = set(a) & set(b)
        if not keys:
            return 0.0
        dot = sum(a[k] * b[k] for k in keys)
        mag_a = math.sqrt(sum(v * v for v in a.values()))
        mag_b = math.sqrt(sum(v * v for v in b.values()))
        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0
        return dot / (mag_a * mag_b)

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        qvec = self._query_vector(query)
        return {nid: self._cosine(qvec, self._vectors.get(nid, {})) for nid in node_ids}

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by TF-IDF cosine similarity."""
        qvec = self._query_vector(query)
        scored = [(nid, self._cosine(qvec, vec)) for nid, vec in self._vectors.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {"node_id": nid, "similarity": sim}
            for nid, sim in scored[:limit]
            if sim > 0.0
        ]


class HybridSemanticScorer:
    """Alpha-blend of TF-IDF and dense embeddings for scoring.

    score = alpha * tfidf + (1 - alpha) * dense

    RAISE-10203 spike showed alpha=0.3 eliminates the -15% regression on
    technical cartridges while preserving +8.7% gains on conceptual ones.

    The ``dense`` parameter accepts any SemanticScorer (Protocol), not a
    concrete eval class — this allows the same hybrid to wrap both the
    eval-only EvalSemanticScorer and production scorers like NumpySemanticScorer
    (ADR-120, D4).

    Implements SemanticScorer + CandidateSearcher so it drops in anywhere
    a scorer is accepted.
    """

    def __init__(
        self,
        tfidf: Any,  # SemanticScorer Protocol (typically InMemorySemanticScorer)
        dense: Any,  # SemanticScorer Protocol — typed as Any to avoid circular import
        alpha: float = SEM_ALPHA,
    ) -> None:
        self._tfidf = tfidf
        self._dense = dense
        self._alpha = alpha

    def score_nodes(self, query: str, node_ids: list[str]) -> dict[str, float]:  # noqa: D102
        t = self._tfidf.score_nodes(query, node_ids)
        d = self._dense.score_nodes(query, node_ids)
        return {
            nid: self._alpha * t.get(nid, 0.0) + (1 - self._alpha) * d.get(nid, 0.0)
            for nid in node_ids
        }

    def search_candidates(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Return top-K candidates by alpha-blended similarity."""
        t_cands = {
            c["node_id"]: c["similarity"]
            for c in self._tfidf.search_candidates(query, limit * 2)
        }
        d_cands = {
            c["node_id"]: c["similarity"]
            for c in self._dense.search_candidates(query, limit * 2)
        }
        all_ids = set(t_cands) | set(d_cands)
        scored = [
            (
                nid,
                self._alpha * t_cands.get(nid, 0.0)
                + (1 - self._alpha) * d_cands.get(nid, 0.0),
            )
            for nid in all_ids
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {"node_id": nid, "similarity": sim}
            for nid, sim in scored[:limit]
            if sim > 0.0
        ]

    def reset(self) -> None:
        """Forward reset to both branches when they support it (RAISE-11749).

        Under ADR-120 (sem_alpha>0) this hybrid is the effective scorer
        wrapping a possibly Server-backed ``_dense`` (and ``_tfidf``). Without
        this forward, federation's ``getattr(scorer, "reset")`` would miss the
        inner ServerSemanticScorer latch, blinding it permanently in
        long-lived instances. Mirrors CompositeSemanticScorer.reset() — safe
        no-op when a branch has no reset().
        """
        for backend in (self._dense, self._tfidf):
            backend_reset = getattr(backend, "reset", None)
            if callable(backend_reset):
                backend_reset()


def resolve_semantic_scorer(
    embeddings_dirs: list[Path] | None = None,  # noqa: ARG001
    server_url: str | None = None,
    api_key: str | None = None,
    sem_alpha: float | None = None,
    tfidf_corpus: list[dict[str, Any]] | None = None,
) -> ServerSemanticScorer | HybridSemanticScorer | None:
    """Pick the best available SemanticScorer backend.

    Returns ServerSemanticScorer when server credentials are present, optionally
    wrapped in HybridSemanticScorer when sem_alpha > 0 with a TF-IDF corpus.
    Returns None when no server credentials are provided — local numpy scoring
    requires an ML provider (raise_cli.embeddings.provider) that cannot
    be imported from raise_core (ADR-139 C2).
    """
    if server_url and api_key:
        server_scorer = ServerSemanticScorer(server_url=server_url, api_key=api_key)
        if sem_alpha and sem_alpha > 0 and tfidf_corpus:
            return HybridSemanticScorer(
                InMemorySemanticScorer(tfidf_corpus), server_scorer, alpha=sem_alpha
            )
        return server_scorer

    return None


__all__ = [
    "CompositeSemanticScorer",
    "HybridSemanticScorer",
    "InMemorySemanticScorer",
    "NumpySemanticScorer",
    "SEM_ALPHA",
    "ServerFederatedScorer",
    "ServerSemanticScorer",
    "resolve_semantic_scorer",
]
