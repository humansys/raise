"""Cartridge quality audit — 7 dimensions, deterministic go/no-go verdict.

Aggregates over existing validators (validate_cartridge, reconcile_nodes,
dedup_nodes) plus 4 new dimensions: trazabilidad, frescura, granularidad,
aptitud cross-cartridge.

Instances are stored as JSON files — YAML gate runners do not apply here.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from raise_core.cartridges.reconcile import reconcile_nodes
from raise_core.cartridges.validate import validate_cartridge
from raise_core.graph.models import GraphNode

DimensionStatus = Literal["pass", "warn", "fail"]

FRESHNESS_GRACE: timedelta = timedelta(days=7)
GRANULARITY_MIN_CHARS: int = 50
GRANULARITY_MAX_CHARS: int = 2000
BROKEN_REL_FAIL_RATIO: float = 0.05


class DimensionResult(BaseModel):
    """Result of a single audit dimension."""

    status: DimensionStatus
    metrics: dict[str, object] = {}
    findings: list[str] = []


class AuditReport(BaseModel):
    """Full audit report for a cartridge."""

    cartridge: str
    verdict: Literal["GO", "NO-GO"]
    no_go: bool
    dimensions: dict[str, DimensionResult]


# ---------------------------------------------------------------------------
# Instance loading
# ---------------------------------------------------------------------------


def _resolve_source_path(cartridge_dir: Path, sf: str) -> Path | None:
    """Resolve source_file to an existing path.

    Tries cartridge_dir-relative first (synthetic fixtures), then as-is
    (real cartridges store paths relative to project CWD).
    """
    p_cartridge = cartridge_dir / sf
    if p_cartridge.exists():
        return p_cartridge
    p_cwd = Path(sf)
    if p_cwd.exists():
        return p_cwd
    p_normalized = Path(sf).resolve()
    if p_normalized.exists():
        return p_normalized
    return None


def _load_instances(cartridge_dir: Path) -> list[GraphNode]:
    """Load all instances from JSON files in cartridge_dir/instances/."""
    instances_dir = cartridge_dir / "instances"
    if not instances_dir.exists():
        return []
    nodes: list[GraphNode] = []
    for json_file in sorted(instances_dir.glob("*.json")):
        try:
            raw = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict) and "id" in item:
                    try:
                        nodes.append(GraphNode.model_validate(item))
                    except Exception:  # noqa: S112
                        continue
        elif isinstance(raw, dict) and "id" in raw:
            with contextlib.suppress(Exception):
                nodes.append(GraphNode.model_validate(raw))
    return nodes


def _source_modified_at(source_path: Path) -> datetime:
    """Return the durable change time for a source, falling back to its mtime.

    Git assigns freshly checked-out files the checkout time as their mtime.  A
    cartridge committed before that checkout is therefore not stale merely
    because CI cloned it today.
    """
    source_path = source_path.resolve()
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(source_path.parent),
                "log",
                "-1",
                "--format=%cI",
                "--",
                str(source_path),
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        commit_time = result.stdout.strip()
        if result.returncode == 0 and commit_time:
            parsed = datetime.fromisoformat(commit_time)
            return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
    except OSError:
        pass
    return datetime.fromtimestamp(os.stat(source_path).st_mtime, tz=UTC)


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------


def _dim_integridad(cartridge_dir: Path) -> DimensionResult:
    """Integridad estructural: manifest válido + estructura de dirs."""
    result = validate_cartridge(cartridge_dir)
    if not result.valid:
        return DimensionResult(
            status="fail",
            findings=result.errors,
            metrics={"errors": len(result.errors)},
        )
    if result.warnings:
        return DimensionResult(
            status="warn",
            findings=result.warnings,
            metrics={"warnings": len(result.warnings)},
        )
    return DimensionResult(status="pass", metrics={"valid": True})


def _dim_trazabilidad(cartridge_dir: Path, nodes: list[GraphNode]) -> DimensionResult:
    """Trazabilidad: cada instancia tiene source_file resoluble y no vacío."""
    if not nodes:
        return DimensionResult(
            status="warn",
            findings=["No instances found"],
            metrics={"traced": 0, "total": 0},
        )
    untraced: list[str] = []
    for node in nodes:
        sf = node.source_file
        if not sf:
            untraced.append(node.id)
            continue
        if not _resolve_source_path(cartridge_dir, sf):
            untraced.append(node.id)

    traced = len(nodes) - len(untraced)
    if untraced:
        return DimensionResult(
            status="fail",
            findings=[
                f"Untraced nodes: {untraced[:5]}"
                + (" ..." if len(untraced) > 5 else "")
            ],
            metrics={"traced": traced, "total": len(nodes), "untraced": len(untraced)},
        )
    return DimensionResult(
        status="pass",
        metrics={"traced": traced, "total": len(nodes)},
    )


def _dim_frescura(cartridge_dir: Path, nodes: list[GraphNode]) -> DimensionResult:
    """Frescura: source change time vs instance synchronization timestamp."""
    if not nodes:
        return DimensionResult(
            status="pass",
            findings=["No instances — skipped"],
            metrics={"checked": 0},
        )

    stale: list[str] = []
    seen_stale: set[str] = set()
    source_timestamps: dict[Path, datetime] = {}
    checked = 0
    max_drift_days: float = 0.0

    for node in nodes:
        sf = node.source_file
        if not sf:
            continue
        src_path = _resolve_source_path(cartridge_dir, sf)
        if not src_path:
            continue

        try:
            synchronized_at = node.updated_at or node.created
            synchronized_dt = (
                datetime.fromisoformat(synchronized_at).replace(tzinfo=UTC)
                if datetime.fromisoformat(synchronized_at).tzinfo is None
                else datetime.fromisoformat(synchronized_at)
            )
        except ValueError:
            continue

        source_modified_at = source_timestamps.get(src_path)
        if source_modified_at is None:
            source_modified_at = _source_modified_at(src_path)
            source_timestamps[src_path] = source_modified_at
        drift = source_modified_at - synchronized_dt
        checked += 1
        if drift.total_seconds() > 0:
            drift_days = drift.total_seconds() / 86400
            max_drift_days = max(max_drift_days, drift_days)
            key = src_path.name
            if drift > FRESHNESS_GRACE and key not in seen_stale:
                seen_stale.add(key)
                stale.append(
                    f"{key} drift {drift_days:.0f}d > {FRESHNESS_GRACE.days}d grace"
                )

    if stale:
        return DimensionResult(
            status="fail",
            findings=stale[:5],
            metrics={
                "max_drift_days": round(max_drift_days, 1),
                "stale_groups": len(stale),
            },
        )
    return DimensionResult(
        status="pass",
        metrics={"checked": checked, "max_drift_days": round(max_drift_days, 1)},
    )


def _dim_cobertura(cartridge_dir: Path, nodes: list[GraphNode]) -> DimensionResult:
    """Cobertura: instancias extraídas vs corpus disponible."""
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    corpus_globs: list[str] = []
    if manifest_path.exists():
        try:
            raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                corpus_globs = raw.get("corpus", []) or []
        except yaml.YAMLError:
            pass

    if not corpus_globs:
        return DimensionResult(
            status="pass",
            findings=["No corpus configured — curated cartridge"],
            metrics={"nodes": len(nodes)},
        )

    corpus_files: list[Path] = []
    for glob in corpus_globs:
        corpus_files.extend(cartridge_dir.glob(glob))

    if not corpus_files:
        return DimensionResult(
            status="warn",
            findings=["Corpus globs defined but no files found"],
            metrics={"corpus_files": 0, "nodes": len(nodes)},
        )

    if not nodes:
        return DimensionResult(
            status="warn",
            findings=[f"0 instances but {len(corpus_files)} corpus file(s) found"],
            metrics={"corpus_files": len(corpus_files), "nodes": 0},
        )

    return DimensionResult(
        status="pass",
        metrics={"corpus_files": len(corpus_files), "nodes": len(nodes)},
    )


def _dim_granularidad(nodes: list[GraphNode]) -> DimensionResult:
    """Granularidad: distribución de content length. Solo warn, nunca fail."""
    if not nodes:
        return DimensionResult(
            status="warn",
            findings=["No instances — cannot assess granularity"],
            metrics={},
        )

    lengths = sorted(len(n.content) for n in nodes)
    n = len(lengths)
    p10 = lengths[max(0, int(n * 0.10) - 1)]
    p90 = lengths[min(n - 1, int(n * 0.90))]

    findings: list[str] = []
    if p10 < GRANULARITY_MIN_CHARS:
        findings.append(
            f"p10={p10} chars (< {GRANULARITY_MIN_CHARS} threshold — nodes may be too short)"
        )
    if p90 > GRANULARITY_MAX_CHARS:
        findings.append(
            f"p90={p90} chars (> {GRANULARITY_MAX_CHARS} threshold — nodes may be too long)"
        )

    status: DimensionStatus = "warn" if findings else "pass"
    return DimensionResult(
        status=status,
        findings=findings,
        metrics={"p10": p10, "p50": lengths[n // 2], "p90": p90, "count": n},
    )


def _dim_relaciones(nodes: list[GraphNode], cartridge_name: str) -> DimensionResult:
    """Calidad de relaciones: detecta phantom targets via reconcile_nodes."""
    if not nodes:
        return DimensionResult(
            status="pass",
            metrics={"broken": 0, "total_edges": 0},
        )

    report = reconcile_nodes(nodes, id_prefix=f"kc-{cartridge_name}-")
    broken = len(report.broken_relationships)
    total_edges = sum(
        len(n.metadata.get("relationships", []))
        for n in nodes
        if isinstance(n.metadata.get("relationships"), list)
    )

    if broken == 0:
        return DimensionResult(
            status="pass",
            metrics={"broken": 0, "total_edges": total_edges},
        )

    ratio = broken / max(total_edges, 1)
    status: DimensionStatus = "fail" if ratio >= BROKEN_REL_FAIL_RATIO else "warn"
    return DimensionResult(
        status=status,
        findings=[f"{broken} broken relationship(s) ({ratio:.1%} of edges)"],
        metrics={
            "broken": broken,
            "total_edges": total_edges,
            "ratio": round(ratio, 3),
        },
    )


def _dim_aptitud(
    nodes: list[GraphNode],
    other_cartridges: list[Path] | None,
) -> DimensionResult:
    """Aptitud cross-cartridge: diversidad de conceptos. Solo warn, nunca fail."""
    if not other_cartridges:
        return DimensionResult(
            status="warn",
            findings=[
                "Single-cartridge mode — use --compare for cross-cartridge assessment"
            ],
            metrics={"mode": "single"},
        )

    my_ids = {n.id for n in nodes}
    other_ids: set[str] = set()
    for other_dir in other_cartridges:
        for other_node in _load_instances(other_dir):
            other_ids.add(other_node.id)

    if not other_ids:
        return DimensionResult(
            status="warn",
            findings=["Other cartridges have no instances"],
            metrics={"overlap": 0.0},
        )

    overlap_count = len(my_ids & other_ids)
    unique_count = len(my_ids - other_ids)
    overlap_ratio = overlap_count / len(my_ids) if my_ids else 0.0

    status: DimensionStatus = "pass" if unique_count > 0 else "warn"
    return DimensionResult(
        status=status,
        findings=[]
        if status == "pass"
        else ["No unique concepts vs other cartridge(s)"],
        metrics={
            "overlap": round(overlap_ratio, 3),
            "unique": unique_count,
            "shared": overlap_count,
        },
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class ParityTypeResult(BaseModel):
    """Parity result for a single node type."""

    node_type: str
    regex_count: int
    llm_count: int
    ratio: float
    passed: bool


class ParityResult(BaseModel):
    """Result of a parity gate check comparing LLM vs regex node counts."""

    passed: bool
    threshold: float
    by_type: list[ParityTypeResult]
    summary: str


def check_parity(
    regex_nodes: list[GraphNode],
    llm_nodes: list[GraphNode],
    *,
    threshold: float = 0.8,
) -> ParityResult:
    """Compare LLM cartridge output vs regex parser output by node type.

    Groups nodes by ``node.type``, compares counts.  The gate passes when
    ``llm_count >= threshold * regex_count`` for every type present in the
    regex output.  Types that exist only in the LLM output are ignored
    (extra coverage is fine).

    Args:
        regex_nodes: Nodes produced by regex parsers (legacy, for parity comparison).
        llm_nodes: Nodes produced by the LLM cartridge pipeline.
        threshold: Minimum ratio (0-1) of LLM count to regex count.

    Returns:
        ParityResult with per-type breakdown and overall pass/fail.
    """
    from collections import Counter

    regex_counts: Counter[str] = Counter(n.type for n in regex_nodes)
    llm_counts: Counter[str] = Counter(n.type for n in llm_nodes)

    by_type: list[ParityTypeResult] = []
    all_passed = True

    for node_type in sorted(regex_counts):
        r_count = regex_counts[node_type]
        l_count = llm_counts.get(node_type, 0)
        ratio = l_count / r_count if r_count > 0 else 1.0
        passed = ratio >= threshold
        if not passed:
            all_passed = False
        by_type.append(
            ParityTypeResult(
                node_type=node_type,
                regex_count=r_count,
                llm_count=l_count,
                ratio=round(ratio, 3),
                passed=passed,
            )
        )

    failed = [t for t in by_type if not t.passed]
    if not by_type:
        summary = "No regex types to compare — pass by default"
    elif all_passed:
        summary = f"All {len(by_type)} types meet {threshold:.0%} threshold"
    else:
        summary = (
            f"{len(failed)}/{len(by_type)} types below {threshold:.0%}: "
            + ", ".join(f"{t.node_type} ({t.ratio:.0%})" for t in failed)
        )

    return ParityResult(
        passed=all_passed,
        threshold=threshold,
        by_type=by_type,
        summary=summary,
    )


def audit_cartridge(
    cartridge_dir: Path,
    *,
    other_cartridges: list[Path] | None = None,
) -> AuditReport:
    """Audit a cartridge across 7 quality dimensions.

    Returns an AuditReport with a GO/NO-GO verdict. GO requires all
    dimensions to be pass or warn. Any fail → NO-GO.

    Heuristic dimensions (granularidad, aptitud) can only warn, never fail.
    """
    cartridge_name = cartridge_dir.name
    nodes = _load_instances(cartridge_dir)

    dimensions: dict[str, DimensionResult] = {
        "integridad": _dim_integridad(cartridge_dir),
        "trazabilidad": _dim_trazabilidad(cartridge_dir, nodes),
        "frescura": _dim_frescura(cartridge_dir, nodes),
        "cobertura": _dim_cobertura(cartridge_dir, nodes),
        "granularidad": _dim_granularidad(nodes),
        "relaciones": _dim_relaciones(nodes, cartridge_name),
        "aptitud": _dim_aptitud(nodes, other_cartridges),
    }

    no_go = any(d.status == "fail" for d in dimensions.values())
    return AuditReport(
        cartridge=cartridge_name,
        verdict="NO-GO" if no_go else "GO",
        no_go=no_go,
        dimensions=dimensions,
    )
