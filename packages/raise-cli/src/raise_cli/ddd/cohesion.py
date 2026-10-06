"""DDD cohesion signal extraction — S16526.2.

Three signals are combined into a weighted CohesionMatrix that scores pairs of
SymbolNodes by how strongly they belong together in the same bounded context:

  1. co_change_matrix     — git co-change frequency (SZZ-style log parsing)
  2. import_coupling_matrix — calls/inherits_from edges in the knowledge graph
  3. module_colocation_matrix — shared module membership

The three matrices are composed via CohesionMatrix.compose() using
CohesionWeights (default 0.4 / 0.4 / 0.2).
"""

from __future__ import annotations

import logging
import subprocess
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from raise_core.graph.engine import Graph
from raise_core.graph.models import SymbolNode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pair key
# ---------------------------------------------------------------------------

_COUPLING_EDGE_TYPES: frozenset[str] = frozenset({"calls", "inherits_from"})


def _pair_key(a: str, b: str) -> str:
    """Return a canonical, symmetric key for a symbol pair.

    The key is ``"{min}::{max}"`` so ``_pair_key("b", "a") == _pair_key("a", "b")``.
    """
    x, y = (a, b) if a <= b else (b, a)
    return f"{x}::{y}"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class CohesionWeights(BaseModel):
    """Weights for the three cohesion signals.  Must each be in [0, 1] and sum to 1.0."""

    co_change: float = Field(default=0.4, ge=0.0, le=1.0)
    coupling: float = Field(default=0.4, ge=0.0, le=1.0)
    colocation: float = Field(default=0.2, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _weights_sum_to_one(self) -> CohesionWeights:
        total = self.co_change + self.coupling + self.colocation
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"CohesionWeights must sum to 1.0, got {total:.6f}")
        return self


class CohesionMatrix(BaseModel):
    """Pairwise cohesion scores, keyed by canonical pair key."""

    scores: dict[str, float] = Field(default_factory=dict)

    def score(self, sym_a: str, sym_b: str) -> float:
        """Return the cohesion score for a symbol pair (0.0 if unknown)."""
        return self.scores.get(_pair_key(sym_a, sym_b), 0.0)

    @classmethod
    def compose(
        cls,
        *,
        co_change: CohesionMatrix,
        coupling: CohesionMatrix,
        colocation: CohesionMatrix,
        weights: CohesionWeights | None = None,
    ) -> CohesionMatrix:
        """Weighted sum of three signal matrices.

        Args:
            co_change: Co-change signal matrix.
            coupling: Import-coupling signal matrix.
            colocation: Module-colocation signal matrix.
            weights: Optional custom weights (default: CohesionWeights()).

        Returns:
            New CohesionMatrix with weighted-average scores, clamped to [0, 1].
            Zero-score entries are omitted.
        """
        w = weights if weights is not None else CohesionWeights()
        all_keys = set(co_change.scores) | set(coupling.scores) | set(colocation.scores)
        composed: dict[str, float] = {}
        for key in all_keys:
            value = (
                w.co_change * co_change.scores.get(key, 0.0)
                + w.coupling * coupling.scores.get(key, 0.0)
                + w.colocation * colocation.scores.get(key, 0.0)
            )
            clamped = min(max(value, 0.0), 1.0)
            if clamped > 0.0:
                composed[key] = clamped
        return cls(scores=composed)


# ---------------------------------------------------------------------------
# Signal 1: co-change
# ---------------------------------------------------------------------------


def _run_git_log(repo_path: Path) -> str | None:
    """Run git log and return raw stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:%H"],
            capture_output=True,
            text=True,
            cwd=str(repo_path),
            timeout=60,
        )
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ) as exc:
        logger.warning("git log error: %s", exc)
        return None
    if result.returncode != 0:
        logger.warning("git log failed (rc=%d)", result.returncode)
        return None
    return result.stdout


def _parse_git_log(raw: str, file_to_syms: dict[str, list[str]]) -> dict[str, int]:
    r"""Parse git log output and count co-change pair occurrences.

    Format: ``<hash>\n\n<file1>\n<file2>\n\n<hash>\n…``
    Split by ``\n\n`` yields alternating (hash, files) chunks at (even, odd) indices.
    """
    pair_counts: dict[str, int] = defaultdict(int)
    chunks = [c.strip() for c in raw.split("\n\n")]
    for i in range(0, len(chunks) - 1, 2):
        hash_chunk = chunks[i]
        files_chunk = chunks[i + 1]
        if not hash_chunk:
            continue
        changed_files = [
            line.strip() for line in files_chunk.splitlines() if line.strip()
        ]
        if len(changed_files) >= 2:
            _accumulate_pairs(changed_files, file_to_syms, pair_counts)
    return pair_counts


def co_change_matrix(symbols: list[SymbolNode], repo_path: Path) -> CohesionMatrix:
    """Build a co-change cohesion matrix from git history.

    Runs ``git log --name-only --pretty=format:"%H"`` and counts how often each
    pair of symbol-owning files appear in the same commit.  Scores are
    normalised by the maximum co-occurrence count.

    Args:
        symbols: Domain symbols to score.
        repo_path: Path to the git repository root.

    Returns:
        CohesionMatrix (empty if git fails or fewer than 2 symbols are given).
    """
    if len(symbols) < 2:
        return CohesionMatrix()

    file_to_syms: dict[str, list[str]] = defaultdict(list)
    for sym in symbols:
        file_val = sym.metadata.get("file", "")
        if file_val:
            file_to_syms[str(file_val)].append(sym.id)

    if len(file_to_syms) < 2:
        return CohesionMatrix()

    raw = _run_git_log(repo_path)
    if raw is None:
        return CohesionMatrix()

    pair_counts = _parse_git_log(raw, file_to_syms)
    if not pair_counts:
        return CohesionMatrix()

    max_count = max(pair_counts.values())
    if max_count == 0:
        return CohesionMatrix()

    scores = {key: count / max_count for key, count in pair_counts.items()}
    return CohesionMatrix(scores=scores)


def _accumulate_pairs(
    files: list[str],
    file_to_syms: dict[str, list[str]],
    counts: dict[str, int],
) -> None:
    """Increment co-change counts for all domain-symbol pairs in a commit."""
    domain_files = [f for f in files if f in file_to_syms]
    for f1, f2 in combinations(domain_files, 2):
        for s1 in file_to_syms[f1]:
            for s2 in file_to_syms[f2]:
                counts[_pair_key(s1, s2)] += 1


# ---------------------------------------------------------------------------
# Signal 2: import coupling
# ---------------------------------------------------------------------------


def _transitive_pairs(
    direct_targets: dict[str, set[str]],
    direct_pairs: set[str],
) -> set[str]:
    """Compute depth-2 transitive pairs not already in direct_pairs."""
    transitive: set[str] = set()
    for neighbors in direct_targets.values():
        neighbor_list = list(neighbors)
        for i in range(len(neighbor_list)):
            for j in range(i + 1, len(neighbor_list)):
                key = _pair_key(neighbor_list[i], neighbor_list[j])
                if key not in direct_pairs:
                    transitive.add(key)
    return transitive


def import_coupling_matrix(symbols: list[SymbolNode], graph: Graph) -> CohesionMatrix:
    """Build a coupling matrix from calls/inherits_from edges in the graph.

    Direct edges score 1.0; transitive depth-2 edges score 0.5.
    Only edges where BOTH endpoints are in the input symbol set are counted.

    Args:
        symbols: Domain symbols to score.
        graph: Knowledge graph providing iter_relationships().

    Returns:
        CohesionMatrix with direct (1.0) and transitive-depth-2 (0.5) scores.
    """
    if not symbols:
        return CohesionMatrix()

    domain_ids: set[str] = {sym.id for sym in symbols}
    direct_pairs: set[str] = set()
    direct_targets: dict[str, set[str]] = defaultdict(set)

    for edge in graph.iter_relationships():
        if edge.type not in _COUPLING_EDGE_TYPES:
            continue
        if edge.source not in domain_ids or edge.target not in domain_ids:
            continue
        direct_pairs.add(_pair_key(edge.source, edge.target))
        direct_targets[edge.source].add(edge.target)
        direct_targets[edge.target].add(edge.source)

    transitive = _transitive_pairs(direct_targets, direct_pairs)
    scores: dict[str, float] = dict.fromkeys(direct_pairs, 1.0)
    scores.update(dict.fromkeys(transitive, 0.5))
    return CohesionMatrix(scores=scores)


# ---------------------------------------------------------------------------
# Signal 3: module colocation
# ---------------------------------------------------------------------------


def module_colocation_matrix(symbols: list[SymbolNode]) -> CohesionMatrix:
    """Build a colocation matrix from shared module membership.

    All pairs of symbols in the same non-empty module score 1.0.

    Args:
        symbols: Domain symbols to score.

    Returns:
        CohesionMatrix with 1.0 for intra-module pairs.
    """
    if not symbols:
        return CohesionMatrix()

    module_to_syms: dict[str, list[str]] = defaultdict(list)
    for sym in symbols:
        mod = str(sym.metadata.get("module", ""))
        if mod:
            module_to_syms[mod].append(sym.id)

    scores: dict[str, float] = {}
    for sym_ids in module_to_syms.values():
        if len(sym_ids) < 2:
            continue
        for s1, s2 in combinations(sym_ids, 2):
            scores[_pair_key(s1, s2)] = 1.0

    return CohesionMatrix(scores=scores)
