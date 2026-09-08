"""Code discovery — symbol extraction and graph building.

Provides language-agnostic code scanning (scanner) and symbol-to-graph
conversion (symbols). Used by both raise-cli and raise-server.
"""

from raise_core.discovery.scanner import (
    EXTENSION_TO_LANGUAGE,
    Language,
    ScanResult,
    Symbol,
    SymbolKind,
    detect_language,
    extract_python_symbols,
    scan_directory,
)
from raise_core.discovery.symbols import (
    EDGE_CALLS,
    EDGE_IMPLEMENTS_SYMBOL,
    EDGE_INHERITS_FROM,
    IngestReport,
    SymbolDepth,
    load_symbols,
    qualified_module_id,
)

__all__ = [
    "EDGE_CALLS",
    "EDGE_IMPLEMENTS_SYMBOL",
    "EDGE_INHERITS_FROM",
    "EXTENSION_TO_LANGUAGE",
    "IngestReport",
    "Language",
    "ScanResult",
    "Symbol",
    "SymbolDepth",
    "SymbolKind",
    "detect_language",
    "extract_python_symbols",
    "load_symbols",
    "qualified_module_id",
    "scan_directory",
]
