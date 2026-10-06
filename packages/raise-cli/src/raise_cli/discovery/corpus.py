"""Corpus orchestrator — rank modules by drift signal violations (S2161.1 · T3).

Loads a corpus manifest (YAML), calibrates self-hosted thresholds from the
healthy subset (via :mod:`raise_cli.discovery.thresholds`), runs the full
detector stack over each target module, and emits a ranked
:class:`HotspotRanking` suitable for downstream consumers (Pass 2 / S2161.2).

The output JSON is a stable v1 contract — breaking changes require a schema
version bump.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from raise_cli.discovery.check import DriftSignal, run_drift_check
from raise_cli.discovery.thresholds import HealthyModuleRef, calibrate_thresholds

__all__ = [
    "CorpusManifest",
    "HotspotEntry",
    "HotspotRanking",
    "ModuleRef",
    "SignalBreakdown",
    "scan_corpus",
]


# ---------------------------------------------------------------------------
# Manifest models
# ---------------------------------------------------------------------------


class ModuleRef(BaseModel):
    """A module to be scanned. Path is repo-relative."""

    module_id: str
    path: Path


class CorpusManifest(BaseModel):
    """YAML-backed manifest declaring scan targets and healthy references."""

    schema_version: Literal["1"] = "1"
    modules: list[ModuleRef]
    healthy_refs: list[HealthyModuleRef] = Field(default_factory=lambda: [])


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------


class SignalBreakdown(BaseModel):
    """Per-signal snapshot for a ranked module."""

    name: str
    status: Literal["ok", "warn", "unavailable"]
    detail: str


class HotspotEntry(BaseModel):
    """One module's position in the hotspot ranking."""

    module_id: str
    path: Path
    violation_score: int
    signals: list[SignalBreakdown]


class HotspotRanking(BaseModel):
    """Ranked hotspot list with calibration trace. Schema v1 — additive only.

    ``excluded_metrics`` names signals neutralized by the calibrator because the
    healthy subset's distribution was degenerate. For those signals every entry
    will show ``status="unavailable"`` with a degenerate-calibration detail.
    """

    schema_version: Literal["1"] = "1"
    healthy_n: int
    quantile: float
    thresholds: dict[str, float]
    excluded_healthy: list[str] = Field(default_factory=lambda: [])
    excluded_metrics: list[str] = Field(default_factory=lambda: [])
    entries: list[HotspotEntry]
    computed_at: str = Field(default_factory=lambda: datetime.now(tz=UTC).isoformat())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scan_corpus(manifest_path: Path, top_n: int = 20) -> HotspotRanking:
    """Calibrate thresholds, score every module, return the top-N hotspots.

    Args:
        manifest_path: Path to the corpus YAML manifest.
        top_n:         Retain only the N highest-scoring modules (ties → alphabetical).

    Returns:
        :class:`HotspotRanking` with calibration trace + ranked entries.

    Raises:
        FileNotFoundError: If the manifest itself or any declared module path is missing.
        ValueError:        If the manifest schema version is not supported.
    """
    manifest = _load_manifest(manifest_path)

    repo_root = manifest_path.parent
    cfg, calibration = calibrate_thresholds(manifest.healthy_refs, repo_root=repo_root)

    _ensure_all_modules_exist(manifest.modules)

    excluded_metrics = frozenset(calibration.excluded_metrics)

    entries: list[HotspotEntry] = []
    for mod in manifest.modules:
        report = run_drift_check(mod.path, cfg)
        entries.append(_entry_from_signals(mod, report.signals, excluded_metrics))

    entries.sort(key=lambda e: (-e.violation_score, e.module_id))
    top_entries = entries[:top_n]

    return HotspotRanking(
        healthy_n=calibration.healthy_n,
        quantile=calibration.quantile,
        thresholds=calibration.thresholds,
        excluded_healthy=calibration.excluded,
        excluded_metrics=calibration.excluded_metrics,
        entries=top_entries,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _load_manifest(manifest_path: Path) -> CorpusManifest:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Corpus manifest not found: {manifest_path}")
    raw: object = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(
            f"Corpus manifest must be a YAML mapping at top level: {manifest_path}"
        )
    data: dict[str, object] = raw  # type: ignore[assignment]
    version = data.get("schema_version")
    if version != "1":
        raise ValueError(
            f"Unsupported corpus manifest schema_version={version!r}; expected '1'"
        )
    return CorpusManifest.model_validate(data)


def _ensure_all_modules_exist(modules: list[ModuleRef]) -> None:
    for mod in modules:
        if not mod.path.exists():
            raise FileNotFoundError(
                f"Module {mod.module_id!r} path does not exist: {mod.path}. "
                "Fix the manifest or remove the stale entry."
            )


def _entry_from_signals(
    mod: ModuleRef,
    signals: list[DriftSignal],
    excluded_metrics: frozenset[str],
) -> HotspotEntry:
    breakdown: list[SignalBreakdown] = []
    for s in signals:
        if s.name in excluded_metrics:
            breakdown.append(
                SignalBreakdown(
                    name=s.name,
                    status="unavailable",
                    detail="calibration degenerate — healthy subset variance too low",
                )
            )
        else:
            breakdown.append(
                SignalBreakdown(name=s.name, status=s.status, detail=s.detail)
            )
    score = sum(1 for b in breakdown if b.status == "warn")
    return HotspotEntry(
        module_id=mod.module_id,
        path=mod.path,
        violation_score=score,
        signals=breakdown,
    )
