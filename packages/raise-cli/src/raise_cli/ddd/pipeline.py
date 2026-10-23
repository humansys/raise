"""DDD classification pipeline — orchestrates filter → classify → escalate → persist."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, cast

from raise_cli.ddd.classifier import (
    ClassificationResult,
    DddLayer,
    classify_symbols,
)
from raise_cli.ddd.panel import escalate_symbols
from raise_cli.ddd.persistence import content_hash_for, should_classify
from raise_core.graph.engine import Graph
from raise_core.graph.models import SymbolNode

logger = logging.getLogger(__name__)

ESCALATION_THRESHOLD = 0.7


def _apply_to_graph(
    graph: Graph,
    node: SymbolNode,
    *,
    ddd_layer: str,
    confidence: float,
    ddd_source: str = "proposed",
) -> None:
    """Write DDD metadata into the graph's internal networkx node data."""
    nx_data = graph.graph.nodes[node.id]
    meta = dict(nx_data.get("metadata", {}))
    meta["ddd_layer"] = ddd_layer
    meta["ddd_source"] = ddd_source
    meta["ddd_content_hash"] = content_hash_for(node)
    meta["ddd_confidence"] = confidence
    nx_data["metadata"] = meta


@dataclass
class ModuleDensity:
    """Domain density for a single module."""

    module_id: str
    total_accepted: int
    count_d: int
    count_i: int
    ratio_d: float
    classification: str  # "domain" | "infra" | "mixed"


@dataclass
class ClassifyReport:
    """Summary of a classification run."""

    total: int = 0
    classified: int = 0
    skipped: int = 0
    escalated: int = 0
    count_d: int = 0
    count_i: int = 0
    count_ambiguous: int = 0
    ratified_skipped: int = 0
    already_agreed_skipped: int = 0
    results: list[ClassificationResult] = field(default_factory=list)
    auto_accepted: int = 0
    propagated: int = 0
    still_uncertain: int = 0
    module_densities: dict[str, ModuleDensity] = field(default_factory=dict)
    uncertain_results: list[ClassificationResult] = field(default_factory=list)
    module_by_symbol: dict[str, str] = field(default_factory=dict)
    # RAISE-16788: prompt-hint string injected into Pass 1 LLM call (None when
    # no --context was given without --pass2).
    domain_context: str | None = None


def partition_by_confidence(
    results: list[ClassificationResult],
    threshold: float = 0.85,
) -> tuple[list[ClassificationResult], list[ClassificationResult]]:
    """Split results into auto-accepted (≥threshold) and uncertain (<threshold)."""
    accepted: list[ClassificationResult] = []
    uncertain: list[ClassificationResult] = []
    for r in results:
        if r.confidence >= threshold:
            accepted.append(r)
        else:
            uncertain.append(r)
    return accepted, uncertain


def compute_module_densities(
    accepted: list[ClassificationResult],
    symbols: list[SymbolNode],
    d_threshold: float = 0.8,
    i_threshold: float = 0.2,
    min_module_size: int = 3,
) -> dict[str, ModuleDensity]:
    """Derive domain density per module from auto-accepted labels."""
    sym_map: dict[str, SymbolNode] = {s.id: s for s in symbols}
    module_counts: dict[str, list[str]] = {}
    for r in accepted:
        node = sym_map.get(r.id)
        if node is None:
            continue
        mod = str(node.metadata.get("module", ""))
        if not mod:
            continue
        module_counts.setdefault(mod, []).append(r.ddd_layer)

    densities: dict[str, ModuleDensity] = {}
    for mod, layers in module_counts.items():
        total = len(layers)
        count_d = sum(1 for la in layers if la == "D")
        count_i = sum(1 for la in layers if la == "I")
        ratio_d = count_d / total if total > 0 else 0.0
        if total < min_module_size:
            classification = "mixed"
        elif ratio_d >= d_threshold:
            classification = "domain"
        elif ratio_d <= i_threshold:
            classification = "infra"
        else:
            classification = "mixed"
        densities[mod] = ModuleDensity(
            module_id=mod,
            total_accepted=total,
            count_d=count_d,
            count_i=count_i,
            ratio_d=ratio_d,
            classification=classification,
        )
    return densities


def propagate_by_module_density(
    uncertain: list[ClassificationResult],
    symbols: list[SymbolNode],
    densities: dict[str, ModuleDensity],
) -> tuple[list[ClassificationResult], list[ClassificationResult]]:
    """Propagate labels to uncertain symbols in homogeneous modules."""
    sym_map: dict[str, SymbolNode] = {s.id: s for s in symbols}
    propagated: list[ClassificationResult] = []
    still_uncertain: list[ClassificationResult] = []
    for r in uncertain:
        node = sym_map.get(r.id)
        mod = str(node.metadata.get("module", "")) if node else ""
        density = densities.get(mod)
        if density and density.classification == "domain":
            propagated.append(
                ClassificationResult(
                    id=r.id,
                    ddd_layer="D",
                    confidence=r.confidence,
                    reasoning=f"Propagated from module {mod} (domain, {density.ratio_d:.0%} D)",
                    heuristics=r.heuristics,
                )
            )
        elif density and density.classification == "infra":
            propagated.append(
                ClassificationResult(
                    id=r.id,
                    ddd_layer="I",
                    confidence=r.confidence,
                    reasoning=f"Propagated from module {mod} (infra, {density.ratio_d:.0%} D)",
                    heuristics=r.heuristics,
                )
            )
        else:
            still_uncertain.append(r)
    return propagated, still_uncertain


def _symbol_to_dict(node: SymbolNode) -> dict[str, object]:
    """Convert a SymbolNode to the dict format expected by classify_symbols."""
    meta = node.metadata
    return {
        "id": node.id,
        "module": str(meta.get("module", "")),
        "kind": str(meta.get("kind", "")),
        "signature": str(meta.get("signature", "")),
        "file": str(meta.get("file", "")),
        "line": meta.get("line", 0),
    }


def _filter_symbols(
    symbol_nodes: list[SymbolNode],
    *,
    full: bool,
    report: ClassifyReport,
    repo_wide_annotations: dict[str, dict[str, Any]] | None = None,
) -> list[SymbolNode]:
    """Apply incremental filter and populate skip counts in the report."""
    to_classify: list[SymbolNode] = []
    for node in symbol_nodes:
        # RAISE-16612 Path 2: use REPO_WIDE annotation for the ratified gate so
        # a checkout-scoped "ratified" cannot suppress REPO_WIDE classification.
        # Use `is not None` (not truthiness) so an empty dict (fresh system with
        # no REPO_WIDE annotations) still activates the REPO_WIDE gate. Use
        # `.get(key, {})` so absent nodes get an empty dict (not None) —
        # `should_classify` treats {} as "no ratified annotation" (correct).
        rw_meta: dict[str, Any] | None = (
            repo_wide_annotations.get(node.id, {})
            if repo_wide_annotations is not None
            else None
        )
        gate_meta: dict[str, Any] = rw_meta if rw_meta is not None else node.metadata
        if gate_meta.get("ddd_source") == "ratified":
            report.ratified_skipped += 1
            report.skipped += 1
        elif full or should_classify(node, repo_wide_meta=rw_meta):
            to_classify.append(node)
        else:
            report.skipped += 1
    return to_classify


def _count_layer(report: ClassifyReport, layer: str) -> None:
    if layer == "D":
        report.count_d += 1
    elif layer == "I":
        report.count_i += 1
    else:
        report.count_ambiguous += 1


def parse_domain_context(context_json: str) -> tuple[set[str], str, dict[str, str]]:
    """Parse a domain context JSON string into module IDs, a context prompt, and a module -> expected ddd_layer map.

    Returns (module_ids, context_string, expected_layers):
      - context_string is formatted for injection into the classification prompt.
      - expected_layers maps each module to "D" (domain) or "I" (infra), used by
        Pass 2 (RAISE-16565) to target only symbols that disagree with — or are
        uncertain about — their module's confirmed classification, instead of
        reclassifying every symbol in the module.

    Parses the JSON exactly once — do not re-parse `context_json` elsewhere;
    thread the returned values through instead (RAISE-16565 review finding).
    """
    decisions = json.loads(context_json)
    modules: set[str] = set()
    lines: list[str] = []
    expected_layers: dict[str, str] = {}
    for d in decisions:
        mod = d["module"]
        cls = str(d["classification"]).strip()
        reasoning = d.get("reasoning", "")
        modules.add(mod)
        lines.append(f"- {mod} is a {cls.upper()} module: {reasoning}")
        expected_layers[mod] = "D" if cls.lower() == "domain" else "I"
    return modules, "\n".join(lines), expected_layers


def _run_pass2(
    graph: Graph,
    report: ClassifyReport,
    symbol_nodes: list[SymbolNode],
    domain_context: str,
    *,
    dry_run: bool,
) -> ClassifyReport:
    """Execute Pass 2: reclassify symbols in context-named modules.

    RAISE-16565: targeted, not blanket. Only symbols that are uncertain (no
    confident ddd_layer yet) or that disagree with the module's confirmed
    classification are sent for reclassification. Symbols already agreeing
    with the confirmed label are left untouched — this avoids the collateral
    damage measured in S16503.9, where reclassifying every symbol in a
    confirmed module dragged plain infra utility functions toward "domain"
    (and vice versa) alongside the real fixes.
    """
    context_modules, context_str, expected_layers = parse_domain_context(domain_context)

    to_reclassify: list[SymbolNode] = []
    for node in symbol_nodes:
        mod = str(node.metadata.get("module", ""))
        if mod not in context_modules:
            report.skipped += 1
            continue
        if node.metadata.get("ddd_source") == "ratified":
            report.ratified_skipped += 1
            report.skipped += 1
            continue
        current_layer = node.metadata.get("ddd_layer")
        if current_layer is not None and current_layer == expected_layers.get(mod):
            report.already_agreed_skipped += 1
            report.skipped += 1
            continue
        to_reclassify.append(node)

    if not to_reclassify:
        return report

    sym_dicts = [_symbol_to_dict(n) for n in to_reclassify]
    logger.info("Pass 2: reclassifying %d symbols with domain context", len(sym_dicts))
    results = classify_symbols(sym_dicts, domain_context=context_str)
    result_map: dict[str, ClassificationResult] = {r.id: r for r in results}

    for node in to_reclassify:
        r = result_map.get(node.id)
        if r is None:
            continue
        report.classified += 1
        report.results.append(r)
        _count_layer(report, r.ddd_layer)
        if not dry_run:
            _apply_to_graph(
                graph,
                node,
                ddd_layer=r.ddd_layer,
                confidence=r.confidence,
                ddd_source="pass2",
            )

    return report


def _populate_module_by_symbol(
    report: ClassifyReport,
    results: list[ClassificationResult],
    node_map: dict[str, SymbolNode],
) -> None:
    """Fill report.module_by_symbol for every classified/uncertain result id."""
    for r in results:
        node = node_map.get(r.id)
        if node:
            report.module_by_symbol[r.id] = str(node.metadata.get("module", ""))


def classify_graph(
    graph: Graph,
    *,
    full: bool = False,
    dry_run: bool = False,
    threshold: float = 0.85,
    pass2_only: bool = False,
    domain_context: str | None = None,
    repo_wide_annotations: dict[str, dict[str, Any]] | None = None,
) -> ClassifyReport:
    """Run the DDD classification pipeline on a loaded graph.

    Flow: classify → escalate contested → partition by confidence →
    propagate via module density → persist.

    When pass2_only=True + domain_context provided: skip Pass 1, reclassify
    only symbols in context-named modules (excluding ratified) with injected
    domain knowledge.
    """
    report = ClassifyReport()

    symbol_nodes: list[SymbolNode] = [
        n for n in graph.iter_concepts() if isinstance(n, SymbolNode)
    ]
    report.total = len(symbol_nodes)
    node_map: dict[str, SymbolNode] = {n.id: n for n in symbol_nodes}

    if pass2_only:
        if not domain_context:
            msg = "pass2_only=True requires non-empty domain_context"
            raise ValueError(msg)
        return _run_pass2(graph, report, symbol_nodes, domain_context, dry_run=dry_run)

    to_classify = _filter_symbols(
        symbol_nodes,
        full=full,
        report=report,
        repo_wide_annotations=repo_wide_annotations,
    )
    if not to_classify:
        return report

    sym_dicts = [_symbol_to_dict(n) for n in to_classify]
    logger.info("Sending %d symbols for classification", len(sym_dicts))
    # RAISE-16788: forward domain_context (prompt-hint string from domain-model.yaml)
    # to Pass 1 so the LLM receives BC→module hints.  Pass 2 uses its own context
    # path (_run_pass2) and does not go through this branch.
    if domain_context is not None:
        report.domain_context = domain_context
    results = classify_symbols(sym_dicts, domain_context=domain_context)
    result_map: dict[str, ClassificationResult] = {r.id: r for r in results}

    # Stage 1: escalate contested symbols (<0.7) to panel
    all_results: list[ClassificationResult] = []
    escalated_ids: set[str] = set()
    contested: list[dict[str, object]] = []
    contested_nodes: dict[str, SymbolNode] = {}

    for node in to_classify:
        r = result_map.get(node.id)
        if r is None:
            continue
        if r.confidence < ESCALATION_THRESHOLD:
            contested.append(_symbol_to_dict(node))
            contested_nodes[node.id] = node
        else:
            all_results.append(r)

    if contested:
        verdicts = escalate_symbols(contested)
        for v in verdicts:
            report.escalated += 1
            escalated_ids.add(v.id)
            all_results.append(
                ClassificationResult(
                    id=v.id,
                    ddd_layer=cast("DddLayer", v.ddd_layer),
                    confidence=v.confidence,
                    reasoning=f"Panel verdict ({v.agreement}/{v.vote_count} agreement)",
                    heuristics={},
                )
            )

    # Stage 2: partition by confidence (panel verdicts skip partition → auto-accepted)
    accepted, uncertain = partition_by_confidence(
        [r for r in all_results if r.id not in escalated_ids],
        threshold=threshold,
    )
    # Panel verdicts are always auto-accepted (DD2)
    panel_results = [r for r in all_results if r.id in escalated_ids]
    accepted = panel_results + accepted

    # Stage 3: module density propagation
    densities = compute_module_densities(accepted, symbol_nodes)
    propagated, still_uncertain_results = propagate_by_module_density(
        uncertain,
        symbol_nodes,
        densities,
    )

    report.auto_accepted = len(accepted)
    report.propagated = len(propagated)
    report.still_uncertain = len(still_uncertain_results)
    report.module_densities = densities
    report.uncertain_results = still_uncertain_results
    _populate_module_by_symbol(
        report, accepted + propagated + still_uncertain_results, node_map
    )

    _persist_results(
        graph,
        report,
        accepted,
        propagated,
        still_uncertain_results,
        node_map=node_map,
        dry_run=dry_run,
    )
    return report


def _persist_results(
    graph: Graph,
    report: ClassifyReport,
    accepted: list[ClassificationResult],
    propagated: list[ClassificationResult],
    still_uncertain: list[ClassificationResult],
    *,
    node_map: dict[str, SymbolNode],
    dry_run: bool,
) -> None:
    """Write classification results to graph and populate report counters."""
    for r in accepted:
        report.classified += 1
        report.results.append(r)
        _count_layer(report, r.ddd_layer)
        node = node_map.get(r.id)
        if node and not dry_run:
            _apply_to_graph(
                graph,
                node,
                ddd_layer=r.ddd_layer,
                confidence=r.confidence,
                ddd_source="pass1",
            )

    for r in propagated:
        report.classified += 1
        report.results.append(r)
        _count_layer(report, r.ddd_layer)
        node = node_map.get(r.id)
        if node and not dry_run:
            _apply_to_graph(
                graph,
                node,
                ddd_layer=r.ddd_layer,
                confidence=r.confidence,
                ddd_source="propagated",
            )

    for r in still_uncertain:
        _count_layer(report, r.ddd_layer)
