"""Backward-compatible re-export from raise_core.discovery.symbols.

The symbols loader implementation moved to raise-core in S9950.15.
This module re-exports the public API so existing external consumers
continue to work.
"""

from raise_core.discovery.symbols import (
    EDGE_CALLS as EDGE_CALLS,
)
from raise_core.discovery.symbols import (
    EDGE_IMPLEMENTS_SYMBOL as EDGE_IMPLEMENTS_SYMBOL,
)
from raise_core.discovery.symbols import (
    EDGE_INHERITS_FROM as EDGE_INHERITS_FROM,
)
from raise_core.discovery.symbols import (
    IngestReport as IngestReport,
)
from raise_core.discovery.symbols import (
    SymbolDepth as SymbolDepth,
)
from raise_core.discovery.symbols import (
    _file_discriminator as _file_discriminator,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.symbols import (
    _find_package_root_index as _find_package_root_index,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.symbols import (
    _module_id_from_file as _module_id_from_file,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.symbols import (
    _resolve_source_roots as _resolve_source_roots,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.discovery.symbols import (
    load_symbols as load_symbols,
)
