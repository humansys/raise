"""Deterministic validation gates for knowledge domains.

Each gate takes a GateConfig and returns a GateResult.
Gates are domain-agnostic — they work with any Pydantic node model.
"""
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# Reason: NetworkX has no type stubs — DiGraph/Graph operations are all Unknown.

from __future__ import annotations

import logging
import time
from collections import Counter
from pathlib import Path  # noqa: TC003 — used at runtime
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from rai_agent.knowledge.models import GateConfig, GateResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_yaml_files(
    node_dir: Path,
) -> list[tuple[Path, dict[str, Any]]]:
    """Load all YAML files from a directory, returning (path, data) pairs.

    Skips files that aren't dicts or don't have an 'id' field.
    """
    results: list[tuple[Path, dict[str, Any]]] = []
    if not node_dir.exists():
        return results
    for yaml_path in sorted(node_dir.rglob("*.yaml")):
        try:
            raw: object = yaml.safe_load(yaml_path.read_text())
        except yaml.YAMLError:
            continue
        if isinstance(raw, dict) and "id" in raw:
            results.append((yaml_path, raw))
    return results


def _timed(
    gate: str,
    domain: str,
    fn: object,  # callable, typed loosely for pyright
) -> GateResult:
    """Time a gate function and catch unexpected errors."""
    start = time.monotonic()
    try:
        result: GateResult = fn()  # type: ignore[operator]
    except Exception as exc:
        logger.warning("Gate '%s' crashed for domain '%s'", gate, domain, exc_info=True)
        elapsed = (time.monotonic() - start) * 1000
        return GateResult(
            gate=gate,
            domain=domain,
            passed=False,
            metrics={},
            errors=[f"Gate crashed: {exc}"],
            warnings=[],
            duration_ms=elapsed,
        )
    elapsed = (time.monotonic() - start) * 1000
    return result.model_copy(update={"duration_ms": elapsed})


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def run_validate(config: GateConfig, domain: str = "unknown") -> GateResult:
    """Validate YAML node files against the schema model.

    Checks each YAML file in config.node_dir against config.node_model.
    """

    def _run() -> GateResult:
        valid = 0
        invalid = 0
        skipped = 0
        errors: list[str] = []
        by_type: Counter[str] = Counter()

        yaml_files = (
            list(config.node_dir.rglob("*.yaml")) if config.node_dir.exists() else []
        )

        for yaml_path in sorted(yaml_files):
            try:
                raw: object = yaml.safe_load(yaml_path.read_text())
            except yaml.YAMLError as exc:
                invalid += 1
                errors.append(f"{yaml_path.name}: YAML parse error — {exc}")
                continue

            if not isinstance(raw, dict) or "id" not in raw:
                skipped += 1
                continue

            try:
                node = config.node_model.model_validate(raw)
                valid += 1
                node_type = getattr(node, "type", "unknown")
                by_type[str(node_type)] += 1
            except ValidationError as exc:
                invalid += 1
                first_err = exc.errors()[0]
                loc = ".".join(str(p) for p in first_err.get("loc", []))
                errors.append(f"{yaml_path.name}: {loc} — {first_err['msg']}")

        warnings: list[str] = []
        if valid == 0 and invalid == 0:
            warnings.append(f"No YAML node files found in {config.node_dir}")

        return GateResult(
            gate="validate",
            domain=domain,
            passed=invalid == 0,
            metrics={
                "valid": valid,
                "invalid": invalid,
                "skipped": skipped,
                "by_type": dict(by_type),
            },
            errors=errors,
            warnings=warnings,
            duration_ms=0,
        )

    return _timed("validate", domain, _run)


def run_reconcile(config: GateConfig, domain: str = "unknown") -> GateResult:
    """Check cross-reference consistency in node files.

    Detects phantom targets, orphan nodes, and cross-decision edges.
    Works with any model that has 'id' and optional 'relationships' and 'decision'.
    """

    def _run() -> GateResult:
        file_data = _load_yaml_files(config.node_dir)
        nodes: list[BaseModel] = []
        for _path, data in file_data:
            try:
                nodes.append(config.node_model.model_validate(data))
            except ValidationError:
                continue  # skip invalid — validate gate catches these

        # Build maps
        node_ids: set[str] = set()
        all_targets: set[str] = set()
        node_decisions: dict[str, str | None] = {}

        for node in nodes:
            nid: str = getattr(node, "id", "")
            node_ids.add(nid)
            node_decisions[nid] = getattr(node, "decision", None)
            rels: list[Any] = getattr(node, "relationships", [])
            for rel in rels:
                target = rel.target if hasattr(rel, "target") else rel.get("target", "")
                all_targets.add(str(target))

        # Phantoms: referenced but no node exists (exclude structural anchors)
        phantoms = sorted(
            t
            for t in all_targets
            if t not in node_ids and not t.startswith("decision-")
        )

        # Orphans: no outbound rels AND not referenced
        referenced = all_targets & node_ids
        orphans = sorted(
            getattr(n, "id", "")
            for n in nodes
            if len(getattr(n, "relationships", [])) == 0
            and getattr(n, "id", "") not in referenced
        )

        # Cross-decision edges
        cross_edges: list[str] = []
        for node in nodes:
            src_decision = getattr(node, "decision", None)
            if src_decision is None:
                continue
            for rel in getattr(node, "relationships", []):
                target = rel.target if hasattr(rel, "target") else rel.get("target", "")
                if str(target).startswith("decision-"):
                    continue
                tgt_decision = node_decisions.get(str(target))
                if tgt_decision is not None and tgt_decision != src_decision:
                    cross_edges.append(f"{getattr(node, 'id', '')} -> {target}")

        errors = [f"Phantom target: {p}" for p in phantoms]
        warnings = [f"Orphan node: {o}" for o in orphans]
        if cross_edges:
            warnings.extend(f"Cross-decision edge: {e}" for e in cross_edges)

        return GateResult(
            gate="reconcile",
            domain=domain,
            passed=len(phantoms) == 0,
            metrics={
                "total_nodes": len(nodes),
                "phantoms": len(phantoms),
                "orphans": len(orphans),
                "cross_decision_edges": len(cross_edges),
            },
            errors=errors,
            warnings=warnings,
            duration_ms=0,
        )

    return _timed("reconcile", domain, _run)


def run_coverage(config: GateConfig, domain: str = "unknown") -> GateResult:
    """Check competency question coverage.

    Loads CQs from config.cq_file, loads nodes, and runs coverage check.

    CQ format: YAML list of objects with fields:
      id, question, decision, expected_path, expected_min_results
    This is the ScaleUp CQ format (from schema_validator). Other domains
    must match this format for full coverage evaluation. If the evaluator
    is unavailable, a fallback mode reports node counts only.
    """

    def _run() -> GateResult:
        if config.cq_file is None or not config.cq_file.exists():
            return GateResult(
                gate="coverage",
                domain=domain,
                passed=True,
                metrics={"covered": 0, "total": 0, "coverage_pct": 100.0},
                errors=[],
                warnings=["No CQ file configured — skipping coverage check"],
                duration_ms=0,
            )

        # Load nodes
        file_data = _load_yaml_files(config.node_dir)
        nodes: list[BaseModel] = []
        for _, data in file_data:
            try:
                nodes.append(config.node_model.model_validate(data))
            except ValidationError:
                continue

        # Try to use the ScaleUp coverage checker if available
        try:
            from rai_agent.scaleup.validation.models import CompetencyQuestion  # pyright: ignore[reportMissingImports]
            from rai_agent.scaleup.validation.schema_validator import check_competency  # pyright: ignore[reportMissingImports]

            cq_raw: object = yaml.safe_load(config.cq_file.read_text())
            if not isinstance(cq_raw, list):
                return GateResult(
                    gate="coverage",
                    domain=domain,
                    passed=False,
                    metrics={},
                    errors=["CQ file is not a list"],
                    warnings=[],
                    duration_ms=0,
                )

            questions = [CompetencyQuestion.model_validate(q) for q in cq_raw]
            result = check_competency(nodes, questions)  # type: ignore[arg-type]

            passed = result.coverage_pct >= config.cq_threshold
            uncovered_ids = [uq.id for uq in result.uncovered]
            warnings = [f"Uncovered: {uid}" for uid in uncovered_ids]

            return GateResult(
                gate="coverage",
                domain=domain,
                passed=passed,
                metrics={
                    "covered": result.covered,
                    "total": result.total,
                    "coverage_pct": result.coverage_pct,
                    "threshold": config.cq_threshold,
                },
                errors=[]
                if passed
                else [
                    f"Coverage {result.coverage_pct:.1f}% "
                    f"< threshold {config.cq_threshold}%"
                ],
                warnings=warnings,
                duration_ms=0,
            )
        except ImportError:
            # Fallback: CQ evaluator not available for this domain.
            # Full evaluation requires CQs in ScaleUp format:
            # {id, question, decision, expected_path, expected_min_results}
            cq_raw_fallback: object = yaml.safe_load(config.cq_file.read_text())
            total_cqs = len(cq_raw_fallback) if isinstance(cq_raw_fallback, list) else 0
            return GateResult(
                gate="coverage",
                domain=domain,
                passed=True,
                metrics={
                    "total_cqs": total_cqs,
                    "total_nodes": len(nodes),
                },
                errors=[],
                warnings=[
                    "CQ evaluator unavailable — showing counts only. "
                    "Ensure CQs use format: {id, question, decision, "
                    "expected_path, expected_min_results}"
                ],
                duration_ms=0,
            )

    return _timed("coverage", domain, _run)


def run_graph(config: GateConfig, domain: str = "unknown") -> GateResult:
    """Build a graph from node files and report stats.

    Uses NetworkX for graph metrics (connectivity, density, degree).
    """

    def _run() -> GateResult:
        import networkx as nx

        file_data = _load_yaml_files(config.node_dir)
        nodes: list[BaseModel] = []
        for _, data in file_data:
            try:
                nodes.append(config.node_model.model_validate(data))
            except ValidationError:
                continue

        # Build NetworkX graph
        g = nx.DiGraph()
        by_type: Counter[str] = Counter()

        for node in nodes:
            nid = str(getattr(node, "id", ""))
            ntype = str(getattr(node, "type", "unknown"))
            g.add_node(nid, type=ntype)
            by_type[ntype] += 1

            for rel in getattr(node, "relationships", []):
                target = rel.target if hasattr(rel, "target") else rel.get("target", "")
                rel_type = (
                    rel.type if hasattr(rel, "type") else rel.get("type", "unknown")
                )
                g.add_edge(nid, str(target), type=str(rel_type))

        node_count = g.number_of_nodes()
        edge_count = g.number_of_edges()

        # Connectivity (on undirected view)
        if node_count > 0:
            undirected = g.to_undirected()
            components = nx.number_connected_components(undirected)
            density = nx.density(g)
            degrees = [d for _, d in g.degree()]
            avg_degree = sum(degrees) / len(degrees) if degrees else 0.0
        else:
            components = 0
            density = 0.0
            avg_degree = 0.0

        warnings: list[str] = []
        if node_count == 0:
            warnings.append("Empty graph — no nodes found")
        if components > 1:
            warnings.append(f"{components} disconnected components")

        return GateResult(
            gate="graph",
            domain=domain,
            passed=True,  # graph gate always passes if it builds
            metrics={
                "nodes": node_count,
                "edges": edge_count,
                "by_type": dict(by_type),
                "components": components,
                "density": round(density, 4),
                "avg_degree": round(avg_degree, 2),
            },
            errors=[],
            warnings=warnings,
            duration_ms=0,
        )

    return _timed("graph", domain, _run)
