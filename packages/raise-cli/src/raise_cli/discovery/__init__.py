"""Discovery module for codebase analysis.

This module provides tools to scan codebases and extract structural
information (classes, functions, modules) for the unified context graph.

Supports Python, TypeScript, and JavaScript via ast (Python) and
tree-sitter (TS/JS).

Architecture: Epic E13 Discovery
"""

from __future__ import annotations

from raise_cli.discovery.check import (
    DriftCheckConfig,
    DriftCheckReport,
    DriftSignal,
    run_drift_check,
)
from raise_cli.discovery.clone import (
    CloneCluster,
    CloneConfig,
    CloneFragment,
    CloneReport,
    detect_clones,
    segment_by_authorship,
)
from raise_cli.discovery.drift import (
    DriftSeverity,
    DriftWarning,
    detect_drift,
)
from raise_cli.discovery.sast import (
    SASTConfig,
    SASTFinding,
    SASTResult,
    run_sast,
)
from raise_cli.discovery.temporal import (
    TemporalConfig,
    TemporalReport,
    delta_update,
    snapshot,
)
from raise_core.discovery.scanner import (
    EXTENSION_TO_LANGUAGE,
    Language,
    ScanResult,
    Symbol,
    SymbolKind,
    detect_language,
    extract_javascript_symbols,
    extract_python_symbols,
    extract_symbols,
    extract_typescript_symbols,
    scan_directory,
)

__all__ = [
    # DriftCheck orchestrator
    "DriftCheckConfig",
    "DriftCheckReport",
    "DriftSignal",
    "run_drift_check",
    # SAST wrapper
    "SASTConfig",
    "SASTFinding",
    "SASTResult",
    "run_sast",
    # Clone detection
    "CloneConfig",
    "CloneFragment",
    "CloneCluster",
    "CloneReport",
    "detect_clones",
    "segment_by_authorship",
    # Drift detection
    "DriftWarning",
    "DriftSeverity",
    "detect_drift",
    # Temporal ingestion
    "TemporalConfig",
    "TemporalReport",
    "snapshot",
    "delta_update",
    # Scanner
    "Symbol",
    "SymbolKind",
    "Language",
    "ScanResult",
    "EXTENSION_TO_LANGUAGE",
    "detect_language",
    "extract_symbols",
    "extract_python_symbols",
    "extract_typescript_symbols",
    "extract_javascript_symbols",
    "scan_directory",
]
