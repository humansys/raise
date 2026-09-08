"""Backward-compatible re-export from raise_core.discovery.scanner.

The scanner implementation moved to raise-core in S9950.15.
This module re-exports the public API so existing external consumers
continue to work.
"""

from raise_core.discovery.scanner import (
    DEFAULT_EXCLUDE_PATTERNS as DEFAULT_EXCLUDE_PATTERNS,
)
from raise_core.discovery.scanner import (
    DEFAULT_LANGUAGE_PATTERNS as DEFAULT_LANGUAGE_PATTERNS,
)
from raise_core.discovery.scanner import (
    EXTENSION_TO_LANGUAGE as EXTENSION_TO_LANGUAGE,
)
from raise_core.discovery.scanner import (
    Language as Language,
)
from raise_core.discovery.scanner import (
    ScanResult as ScanResult,
)
from raise_core.discovery.scanner import (
    Symbol as Symbol,
)
from raise_core.discovery.scanner import (
    SymbolKind as SymbolKind,
)
from raise_core.discovery.scanner import (
    _get_ts_parser as _get_ts_parser,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.scanner import (
    _read_gitignore as _read_gitignore,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.scanner import (
    detect_language as detect_language,
)
from raise_core.discovery.scanner import (
    extract_csharp_symbols as extract_csharp_symbols,
)
from raise_core.discovery.scanner import (
    extract_dart_symbols as extract_dart_symbols,
)
from raise_core.discovery.scanner import (
    extract_go_symbols as extract_go_symbols,
)
from raise_core.discovery.scanner import (
    extract_java_symbols as extract_java_symbols,
)
from raise_core.discovery.scanner import (
    extract_javascript_symbols as extract_javascript_symbols,
)
from raise_core.discovery.scanner import (
    extract_php_symbols as extract_php_symbols,
)
from raise_core.discovery.scanner import (
    extract_python_symbols as extract_python_symbols,
)
from raise_core.discovery.scanner import (
    extract_sql_symbols as extract_sql_symbols,
)
from raise_core.discovery.scanner import (
    extract_svelte_symbols as extract_svelte_symbols,
)
from raise_core.discovery.scanner import (
    extract_symbols as extract_symbols,
)
from raise_core.discovery.scanner import (
    extract_typescript_symbols as extract_typescript_symbols,
)
from raise_core.discovery.scanner import (
    scan_directory as scan_directory,
)
