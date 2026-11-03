"""Relationship inference for the context graph.

Infers edges between concept nodes using explicit metadata
(learned_from, part_of, prerequisites) and deterministic pattern edges.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, cast

from raise_core.discovery.symbols import (
    _PACKAGE_QUALIFIER_SEP,  # pyright: ignore[reportPrivateUsage]
    qualified_module_id,
)
from raise_core.graph.models import GraphEdge, GraphNode

logger = logging.getLogger(__name__)


@dataclass
class EdgeResolutionReport:
    """Tracks resolution metrics for one edge type."""

    edge_type: str
    attempted: int
    resolved: int
    unresolved: int
    dangling: int

    @property
    def resolution_rate(self) -> float:
        """Fraction of attempted resolutions that succeeded."""
        return self.resolved / self.attempted if self.attempted > 0 else 0.0


@dataclass
class GraphHealthReport:
    """Aggregated health report from graph build."""

    total_nodes: int
    total_edges: int
    edge_resolutions: list[EdgeResolutionReport] = field(default_factory=list)
    dangling_edges: int = 0


@dataclass(frozen=True)
class FilteredApplicabilityReport:
    """Filtered ``applies_to`` resolution for the RC1 gate (E14781).

    The unfiltered rate (~59% at the S3 baseline) is dominated by keywords like
    ``fastapi``, ``architecture`` or ``gemba`` that have no module counterpart
    at all. Those are vocabulary gaps, not resolver defects, so RC1 measures
    only the patterns where a module demonstrably exists.

    The critical property is that the denominator is decided *independently of
    the resolver*: it asks the graph "does a module for this keyword exist?"
    via :func:`_normalize_module_term`, while :attr:`resolved` asks the
    resolver "did you produce an edge?". Deriving both from the same helpers
    would make the rate identically 1.0 — measured at exactly 100.00% on the
    live graph — and the gate could never fail.

    Attributes:
        filtered_denominator: Patterns with at least one module-backed keyword.
        resolved: Of those, patterns that received at least one edge.
        no_candidate: Patterns excluded because no keyword is module-backed.
            Visibility only, never blocking.
        unresolved_keywords: Sorted, deduplicated keywords that are module-backed
            yet resolve to nothing — the actionable payload of a gate failure
            (``CLI``, ``MCP``, ``work-events`` on the live graph).
    """

    filtered_denominator: int
    resolved: int
    no_candidate: int
    unresolved_keywords: tuple[str, ...] = ()

    @property
    def rate(self) -> float:
        """Fraction of module-backed patterns the resolver connected."""
        if self.filtered_denominator == 0:
            return 0.0
        return self.resolved / self.filtered_denominator


def normalize_learned_from_ref(ref: str) -> tuple[str, str]:
    """Normalize a learned_from ref to (canonical_id, target_type).

    Returns ("", "") for unresolvable freetext refs.
    """
    ref = ref.strip()
    if not ref:
        return ("", "")
    # S1962.7, s583.1 → story (graph ID: story-s1962-7)
    if re.match(r"^[Ss]\d+\.\d+$", ref):
        slug = ref.lower().replace(".", "-")
        return (f"story-{slug}", "story")
    # F1.5, F14.13 → story (graph ID: story-f1-5)
    if re.match(r"^F\d+\.\d+$", ref):
        slug = ref.lower().replace(".", "-")
        return (f"story-{slug}", "story")
    # SES-357 → session
    if ref.startswith("SES-"):
        return (ref, "session")
    # S-E-260414-0743, S-F-260415-0128-AB12 → session
    # (entropy suffix optional: added by RAISE-15482, old ids lack it)
    if re.match(r"^S-[A-Z]+-\d{6}-\d{4}(-[0-9A-F]{4})?$", ref):
        return (ref, "session")
    # RAISE-1276 → epic
    if ref.startswith("RAISE-"):
        num = ref.split("-", 1)[1]
        return (f"epic-e{num}", "epic")
    # UUID → session
    if re.match(r"^[0-9a-f]{8}-", ref):
        return (ref, "session")
    return ("", "")


def infer_relationships(
    nodes: list[GraphNode],
) -> tuple[list[GraphEdge], GraphHealthReport]:
    """Infer relationships between concepts using deterministic metadata.

    Returns edges and a health report with resolution metrics.
    """
    if not nodes:
        return [], GraphHealthReport(total_nodes=0, total_edges=0)

    edges: list[GraphEdge] = []
    node_by_id: dict[str, GraphNode] = {n.id: n for n in nodes}
    resolutions: list[EdgeResolutionReport] = []

    lf_edges, lf_report = _infer_pattern_learned_from(nodes, node_by_id)
    edges.extend(lf_edges)
    resolutions.append(lf_report)

    at_edges, at_report = _infer_pattern_applies_to(nodes, node_by_id)
    edges.extend(at_edges)
    resolutions.append(at_report)

    pm_edges, pm_report = _infer_pattern_mission(nodes, node_by_id)
    edges.extend(pm_edges)
    resolutions.append(pm_report)

    edges.extend(_infer_part_of(nodes, node_by_id))
    edges.extend(_infer_skill_edges(nodes, node_by_id))
    edges.extend(_infer_depends_on(nodes, node_by_id))
    edges.extend(_infer_release_part_of(nodes, node_by_id))
    edges.extend(_infer_document_references(nodes, node_by_id))

    # Aggregate dangling refs from per-type resolution reports (RAISE-15988).
    # The previous implementation counted over `edges` after they were emitted,
    # which was structurally always 0 because edges are only appended after
    # their target passes the `in node_by_id` check. The real dangling count
    # lives in each resolver that sees the normalized canonical_id before deciding
    # to discard it.
    dangling_edges = sum(r.dangling for r in resolutions)

    report = GraphHealthReport(
        total_nodes=len(nodes),
        total_edges=len(edges),
        edge_resolutions=resolutions,
        dangling_edges=dangling_edges,
    )
    return edges, report


def _infer_pattern_learned_from(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → story/session/epic edges via learned_from metadata."""
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0
    dangling = 0

    for node in nodes:
        if node.type != "pattern":
            continue
        raw_lf = node.metadata.get("learned_from")
        if not raw_lf:
            continue

        attempted += 1
        refs = [r.strip() for r in str(raw_lf).replace(",", " ").split() if r.strip()]
        matched = False
        for ref in refs:
            canonical_id, _ = normalize_learned_from_ref(ref)
            if canonical_id:
                if canonical_id in node_by_id:
                    edges.append(
                        GraphEdge(
                            source=node.id,
                            target=canonical_id,
                            type="learned_from",
                            weight=1.0,
                        )
                    )
                    matched = True
                else:
                    # ref resolved to a valid canonical_id but the target node
                    # is absent from the graph — count as dangling (RAISE-15988)
                    dangling += 1
        if matched:
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="learned_from",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=dangling,
    )


def _module_target_candidates(keyword: str) -> list[str]:
    """Ordered ``mod-*`` ids to try for one pattern context keyword.

    The chain is exact-first and its branches are mutually exclusive, so a
    keyword yields at most one *inflected* candidate and exact match always
    wins by short-circuit rather than by a later dedup pass (RAISE-15809 D2)::

        mod-{k}         always
        mod-{k}s        only when k does not already end in "s"
        mod-{k[:-1]}    only when k ends in "s" and len(k) > 2

    Module directory names are predominantly plural while pattern context
    keywords are predominantly singular, so ``adapter -> mod-adapters`` is the
    load-bearing direction; the strip direction is kept for the smaller
    ``worktrees -> mod-worktree`` population.

    ``str.rstrip("s")`` is deliberately NOT used: it strips a character *set*
    repeatedly (``"access".rstrip("s") == "acce"``, ``"s".rstrip("s") == ""``).
    The ``len(k) > 2`` guard keeps the *stripped* candidate at least two
    characters long, which makes the empty id ``mod-`` unrepresentable.

    Args:
        keyword: A single pattern ``context`` keyword.

    Returns:
        Candidate module ids in resolution order; empty for a blank keyword.
    """
    keyword = keyword.strip()
    if not keyword:
        return []

    candidates = [f"mod-{keyword}"]
    if not keyword.endswith("s"):
        candidates.append(f"mod-{keyword}s")
    elif len(keyword) > 2:
        candidates.append(f"mod-{keyword[:-1]}")
    return candidates


def _build_alias_index(node_by_id: dict[str, GraphNode]) -> dict[str, list[str]]:
    """Map each declared alias to the module ids that claim it (RAISE-15810).

    Aliases are module-owned: each module YAML declares the historical or
    colloquial names that refer to it, so ownership stays with the module
    instead of a global dictionary that only one team can edit.

    The value is a *list*, not a single id, so ambiguity is representable and
    the caller can refuse to guess: exactly one claimant resolves, more than
    one is a curation conflict the caller warns about and skips.

    Non-module nodes and malformed ``aliases`` values (a bare string, nested
    lists, blanks) are ignored rather than raising — the graph is built from
    hand-edited YAML and a typo must not abort the whole build.

    Args:
        node_by_id: All graph nodes keyed by id.

    Returns:
        Alias string → module ids declaring it, in node iteration order.
    """
    index: dict[str, list[str]] = {}
    for node in node_by_id.values():
        if node.type != "module":
            continue
        raw_aliases: Any = node.metadata.get("aliases", [])
        if not isinstance(raw_aliases, list):
            continue
        for alias in cast("list[Any]", raw_aliases):
            if isinstance(alias, str) and alias:
                index.setdefault(alias, []).append(node.id)
    return index


def _resolve_alias_target(
    keyword: str,
    alias_index: dict[str, list[str]],
) -> str | None:
    """Resolve one keyword through the alias index (RAISE-15810).

    An alias claimed by two or more modules is a curation conflict: it is
    logged and refused rather than resolved to the first claimant, because
    first-found depends on node iteration order and would make the graph
    silently non-deterministic across builds.

    Args:
        keyword: A pattern ``context`` keyword the module chain did not match.
        alias_index: Output of :func:`_build_alias_index`.

    Returns:
        The single claiming module id, or None when unclaimed or ambiguous.
    """
    alias_targets = alias_index.get(keyword, [])
    if len(alias_targets) > 1:
        logger.warning(
            "Alias %r is ambiguous: claimed by %s - skipping",
            keyword,
            ", ".join(sorted(alias_targets)),
        )
        return None
    return alias_targets[0] if alias_targets else None


def _resolve_keyword_target(
    keyword: str,
    node_by_id: dict[str, GraphNode],
    alias_index: dict[str, list[str]],
) -> tuple[str, str] | None:
    """Resolve one pattern context keyword to ``(module_id, match_kind)``.

    The single source of truth for "what does the resolver do with this
    keyword" (RAISE-15811). Both the edge builder and the RC1 metric call it,
    so the measured numerator cannot drift from the edges the graph actually
    receives — a second copy of this chain would silently diverge the moment
    either side changed.

    The keyword walks the ordered candidate chain from
    :func:`_module_target_candidates` and stops at the first id present in the
    graph, so exact matches take precedence over inflected ones. Only when that
    chain is exhausted does the module-owned alias index get a turn
    (RAISE-15810); ordering the alias branch last is what guarantees an alias
    can never shadow a real module id.

    Args:
        keyword: A single pattern ``context`` keyword.
        node_by_id: All graph nodes keyed by id.
        alias_index: Output of :func:`_build_alias_index`.

    Returns:
        The target module id paired with ``"exact"``, ``"inflection"`` or
        ``"alias"``, or None when the keyword resolves to nothing.
    """
    for position, mod_id in enumerate(_module_target_candidates(keyword)):
        if mod_id in node_by_id:
            return (mod_id, "exact" if position == 0 else "inflection")

    alias_id = _resolve_alias_target(keyword, alias_index)
    return (alias_id, "alias") if alias_id is not None else None


def _pattern_applies_to_edges(
    node: GraphNode,
    context: list[Any],
    node_by_id: dict[str, GraphNode],
    alias_index: dict[str, list[str]],
) -> list[GraphEdge]:
    """Build the deduplicated ``applies_to`` edges for one pattern node.

    Per-keyword resolution — exact, then inflection, then alias — lives in
    :func:`_resolve_keyword_target`; this function owns only iteration,
    deduplication and edge construction.

    ``seen_targets`` deduplicates within this pattern, closing the RAISE-15809
    TODO: two synonymous keywords in one context list (``["adapter",
    "adapters"]``, or an exact hit plus an alias for the same module) now
    yield one edge by construction. The set is local to this call, so distinct
    patterns may still each point at the same module.

    Args:
        node: The pattern node being resolved.
        context: Its ``context`` keyword list.
        node_by_id: All graph nodes keyed by id.
        alias_index: Output of :func:`_build_alias_index`.

    Returns:
        Zero or more edges, at most one per distinct target module.
    """
    edges: list[GraphEdge] = []
    seen_targets: set[str] = set()

    for keyword in context:
        if not isinstance(keyword, str):
            continue
        target = _resolve_keyword_target(keyword, node_by_id, alias_index)
        if target is None:
            continue
        mod_id, match = target
        if mod_id in seen_targets:
            continue
        metadata = {"match": match}
        if match == "alias":
            metadata["alias_term"] = keyword
        edges.append(
            GraphEdge(
                source=node.id,
                target=mod_id,
                type="applies_to",
                weight=0.8,
                metadata=metadata,
            )
        )
        seen_targets.add(mod_id)

    return edges


def _infer_pattern_applies_to(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → module edges via exact match, then inflection, then alias.

    Per-pattern resolution lives in :func:`_pattern_applies_to_edges`; this
    function owns only iteration and the aggregate resolution report.

    Every edge carries ``metadata["match"]`` — ``"exact"``, ``"inflection"``
    or ``"alias"`` — so the epic's resolution-rate gate can be read as exact
    vs. fallback matches instead of one opaque aggregate (RAISE-15809 D4).
    Alias edges additionally carry ``metadata["alias_term"]`` with the
    original keyword, the provenance record that makes a curated mapping
    auditable (RAISE-15810).

    A pattern counts as resolved when it produced at least one edge.
    """
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0
    alias_index = _build_alias_index(node_by_id)

    for node in nodes:
        if node.type != "pattern":
            continue
        context: Any = node.metadata.get("context", [])
        if not isinstance(context, list) or not context:
            continue

        attempted += 1
        pattern_edges = _pattern_applies_to_edges(
            node, cast("list[Any]", context), node_by_id, alias_index
        )
        if pattern_edges:
            edges.extend(pattern_edges)
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="applies_to",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=0,
    )


def _normalize_module_term(term: str) -> str:
    """Reduce a term to a case/separator/plural-insensitive comparison key.

    Deliberately looser than :func:`_module_target_candidates`, and that
    looseness is the entire point (RAISE-15811): the RC1 denominator has to be
    able to state that ``mod-cli`` exists for the keyword ``CLI`` even though
    the resolver — which is case- and separator-sensitive — cannot reach it.
    A denominator built from the resolver's own chain can only ever agree with
    the resolver, which is how the rate became a tautology.

    Non-alphanumerics are dropped rather than mapped, so ``work-events``,
    ``work_events`` and ``Work Events`` share one key. The trailing-plural strip
    reuses the ``len > 2`` guard from :func:`_module_target_candidates` so short
    terms are not eroded into noise.

    Args:
        term: A module id (already stripped of its ``mod-`` prefix) or a
            pattern context keyword.

    Returns:
        The comparison key; empty for a term with no alphanumerics.
    """
    normalized = re.sub(r"[^a-z0-9]", "", term.lower())
    if normalized.endswith("s") and len(normalized) > 2:
        normalized = normalized[:-1]
    return normalized


def _build_module_term_index(
    node_by_id: dict[str, GraphNode],
) -> dict[str, list[str]]:
    """Map each normalized module term to the module ids carrying it.

    Built from module nodes only, with no reference to the resolver, so it can
    answer "does a module for this keyword exist in the graph?" as a question
    about the graph alone (RAISE-15811).

    The value is a list because normalization can legitimately merge distinct
    ids (``mod-adapter`` and ``mod-adapters``); the RC1 metric only needs to
    know whether the list is non-empty, so ambiguity here is recorded rather
    than resolved.

    Args:
        node_by_id: All graph nodes keyed by id.

    Returns:
        Normalized term → module ids, in node iteration order.
    """
    index: dict[str, list[str]] = {}
    for node in node_by_id.values():
        if node.type != "module":
            continue
        term = _normalize_module_term(node.id.removeprefix("mod-"))
        if term:
            index.setdefault(term, []).append(node.id)
    return index


def compute_filtered_applicability(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> FilteredApplicabilityReport:
    """Measure ``applies_to`` resolution over module-backed patterns only (RC1).

    A pattern enters the denominator when at least one of its context keywords
    is *module-backed*: a module node exists whose id matches the keyword under
    :func:`_normalize_module_term`, or a module declares the keyword as an
    alias. It counts as resolved when :func:`_resolve_keyword_target` — the same
    function the edge builder uses — resolves at least one of its keywords.

    Patterns whose keywords are all pure concepts (``fastapi``, ``gemba``) are
    excluded and reported under ``no_candidate``: the graph has nothing for them
    to point at, so counting them would measure vocabulary coverage rather than
    resolver quality.

    See :class:`FilteredApplicabilityReport` for why the two sides of the ratio
    must stay independent.

    Args:
        nodes: All graph nodes.
        node_by_id: The same nodes keyed by id.

    Returns:
        The RC1 report; a zero denominator yields rate 0.0, which callers are
        expected to treat as "undefined" rather than "failing".
    """
    alias_index = _build_alias_index(node_by_id)
    term_index = _build_module_term_index(node_by_id)

    filtered_denominator = 0
    resolved = 0
    no_candidate = 0
    unresolved_keywords: set[str] = set()

    for node in nodes:
        if node.type != "pattern":
            continue
        context: Any = node.metadata.get("context", [])
        if not isinstance(context, list) or not context:
            continue

        backed = False
        pattern_resolved = False
        for keyword in cast("list[Any]", context):
            if not isinstance(keyword, str) or not keyword.strip():
                continue
            is_backed = bool(term_index.get(_normalize_module_term(keyword))) or bool(
                alias_index.get(keyword)
            )
            if not is_backed:
                continue
            backed = True
            if _resolve_keyword_target(keyword, node_by_id, alias_index) is not None:
                pattern_resolved = True
            else:
                unresolved_keywords.add(keyword)

        if not backed:
            no_candidate += 1
            continue
        filtered_denominator += 1
        if pattern_resolved:
            resolved += 1

    return FilteredApplicabilityReport(
        filtered_denominator=filtered_denominator,
        resolved=resolved,
        no_candidate=no_candidate,
        unresolved_keywords=tuple(sorted(unresolved_keywords)),
    )


def _infer_pattern_mission(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> tuple[list[GraphEdge], EdgeResolutionReport]:
    """Pattern → mission edges via mission_id metadata."""
    edges: list[GraphEdge] = []
    attempted = 0
    resolved = 0

    for node in nodes:
        if node.type != "pattern":
            continue
        mission_id = node.metadata.get("mission_id")
        if not mission_id:
            continue

        attempted += 1
        target_id = f"mission-{mission_id}"
        if target_id in node_by_id:
            edges.append(
                GraphEdge(
                    source=node.id,
                    target=target_id,
                    type="part_of_mission",
                    weight=1.0,
                )
            )
            resolved += 1

    return edges, EdgeResolutionReport(
        edge_type="part_of_mission",
        attempted=attempted,
        resolved=resolved,
        unresolved=attempted - resolved,
        dangling=0,
    )


def _infer_part_of(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer part_of edges from story to epic.

    Story nodes use the normalized id convention from
    :func:`normalize_learned_from_ref`:
    - F-type stories → ``story-f<epic>-<num>`` (e.g. ``story-f1-5``)
    - S-type stories → ``story-s<num>-<sub>`` (no fixed epic parent)

    Only F-type normalized ids have a deterministic epic parent: the first
    segment after ``story-f`` maps to ``epic-e<segment>`` (RAISE-15988).
    """
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "story":
            continue

        story_id = node.id
        # Normalized format: story-f<epic>-<num> → epic-e<epic>
        if story_id.startswith("story-f"):
            slug = story_id[len("story-f") :]  # e.g. "1-5" or "14-13"
            parts = slug.split("-")
            if parts and parts[0]:
                epic_id = f"epic-e{parts[0]}"
                if epic_id in node_by_id:
                    edges.append(
                        GraphEdge(
                            source=node.id,
                            target=epic_id,
                            type="part_of",
                            weight=1.0,
                        )
                    )

    return edges


def _infer_skill_edges(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer edges from skill metadata (prerequisites, next)."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "skill":
            continue

        prereq = node.metadata.get("raise.prerequisites")
        if prereq:
            prereq_id = f"/{prereq}" if not str(prereq).startswith("/") else prereq
            if prereq_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=prereq_id,
                        type="needs_context",
                        weight=1.0,
                    )
                )

        next_skill = node.metadata.get("raise.next")
        if next_skill:
            next_id = (
                f"/{next_skill}" if not str(next_skill).startswith("/") else next_skill
            )
            if next_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=next_id,
                        type="related_to",
                        weight=1.0,
                    )
                )

    return edges


def _resolve_module_dep_id(
    source_id: str,
    dep_name: str,
    node_by_id: dict[str, GraphNode],
) -> str:
    """Resolve a bare ``depends_on`` name to a real module node id.

    Curated sidecars declare dependencies as bare module names
    (``depends_on: [auth, channels, db]``), but module ids are
    package-qualified since RAISE-16033 (``mod-<package>--<name>``). A
    dependency a sidecar names is a sibling inside that sidecar's own
    package, so resolve within the source's package first. Without this,
    ``f"mod-{dep_name}"`` matches nothing and the caller's
    ``if target_id in node_by_id`` guard drops **every** curated
    module-to-module edge silently — the whole architecture dependency
    layer disappears from the graph with no warning.

    Falls back to the unqualified id, which is still correct for a
    package-less module (single-package project, or a sidecar with no
    ``package:`` frontmatter).
    """
    prefix = "mod-"
    if source_id.startswith(prefix) and _PACKAGE_QUALIFIER_SEP in source_id:
        package = source_id[len(prefix) :].split(_PACKAGE_QUALIFIER_SEP, 1)[0]
        same_package = qualified_module_id(dep_name, package)
        if same_package in node_by_id:
            return same_package
    return f"mod-{dep_name}"


def _infer_depends_on(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer depends_on edges from module and component metadata (RAISE-573)."""
    edges: list[GraphEdge] = []

    # Build name→id index for component nodes (class name → node ID)
    comp_name_index: dict[str, str] = {}
    for node in nodes:
        if node.type == "component":
            name = node.metadata.get("name", "")
            if name:
                comp_name_index[name] = node.id

    for node in nodes:
        if node.type not in ("module", "component"):
            continue

        raw_deps: Any = node.metadata.get("depends_on", [])
        if not isinstance(raw_deps, list):
            continue
        deps = cast("list[str]", raw_deps)

        for dep_name in deps:
            # Resolution order: component name → same-package module → bare
            # module id.
            target_id = comp_name_index.get(dep_name) or _resolve_module_dep_id(
                node.id, dep_name, node_by_id
            )
            if target_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=node.id,
                        target=target_id,
                        type="depends_on",
                        weight=1.0,
                    )
                )

    return edges


SALIENCE_THRESHOLD = 0.4


def _salience_score(
    doc_node: GraphNode,
    module_id: str,
    module_symbols: list[str],
) -> float:
    """Composite salience: heading + density + co-occurrence."""
    module_name = module_id.removeprefix("mod-")
    short_name = (
        module_name.split(_PACKAGE_QUALIFIER_SEP)[-1]
        if _PACKAGE_QUALIFIER_SEP in module_name
        else module_name
    )

    chunk_heading = (doc_node.metadata or {}).get("heading", "")
    heading_signal = 1.0 if short_name.lower() in chunk_heading.lower() else 0.0

    doc_content = doc_node.content or ""
    words = doc_content.lower().split()
    pattern = re.compile(rf"\b{re.escape(short_name.lower())}\b")
    mentions = len(pattern.findall(doc_content.lower()))
    density_signal = min(mentions / max(len(words) / 100, 1), 1.0)

    doc_lower = doc_content.lower()
    symbol_mentions = sum(1 for sym in module_symbols if sym.lower() in doc_lower)
    cooccurrence_signal = min(symbol_mentions / max(len(module_symbols), 1), 1.0)

    return heading_signal * 0.4 + density_signal * 0.3 + cooccurrence_signal * 0.3


def _infer_document_references(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer doc→module edges using composite salience scoring."""
    doc_nodes = [n for n in nodes if n.type == "document"]
    module_nodes = [n for n in nodes if n.type == "module"]

    if not doc_nodes or not module_nodes:
        return []

    module_symbols: dict[str, list[str]] = {}
    for n in nodes:
        if n.type == "symbol":
            mod = n.metadata.get("module", "")
            if mod:
                module_symbols.setdefault(mod, []).append(n.id.removeprefix("sym-"))

    edges: list[GraphEdge] = []
    seen: set[tuple[str, str]] = set()
    for doc in doc_nodes:
        for mod in module_nodes:
            if mod.id not in node_by_id:
                continue
            pair = (doc.id, mod.id)
            if pair in seen:
                continue
            mod_name = mod.id.removeprefix("mod-")
            short_name = (
                mod_name.split(_PACKAGE_QUALIFIER_SEP)[-1]
                if _PACKAGE_QUALIFIER_SEP in mod_name
                else mod_name
            )
            syms = module_symbols.get(short_name, [])
            score = _salience_score(doc, mod.id, syms)
            if score >= SALIENCE_THRESHOLD:
                seen.add(pair)
                edges.append(
                    GraphEdge(
                        source=doc.id,
                        target=mod.id,
                        type="references",
                        weight=score,
                        metadata={
                            "salience": round(score, 4),
                            "source": "doc_module_extractor",
                        },
                    )
                )

    return edges


def _infer_release_part_of(
    nodes: list[GraphNode],
    node_by_id: dict[str, GraphNode],
) -> list[GraphEdge]:
    """Infer part_of edges from epics to releases."""
    edges: list[GraphEdge] = []

    for node in nodes:
        if node.type != "release":
            continue

        epic_refs: Any = node.metadata.get("epics", [])
        if not isinstance(epic_refs, list):
            continue

        for epic_ref in cast("list[str]", epic_refs):
            epic_id = f"epic-{epic_ref.lower()}"
            if epic_id in node_by_id:
                edges.append(
                    GraphEdge(
                        source=epic_id,
                        target=node.id,
                        type="part_of",
                        weight=1.0,
                    )
                )

    return edges
