"""Discovery module for codebase analysis.

This module provides tools to scan codebases and extract structural
information (classes, functions, modules) for the unified context graph.

Supports Python, TypeScript, and JavaScript via ast (Python) and
tree-sitter (TS/JS).

Architecture: Epic E13 Discovery
"""

from __future__ import annotations

from raise_cli.discovery.drift import (
    DriftSeverity,
    DriftWarning,
    detect_drift,
)
from raise_cli.discovery.scanner import (
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
    # Drift detection
    "DriftWarning",
    "DriftSeverity",
    "detect_drift",
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
