"""Re-export shim: raise_cli.pipeline.rai_header → raise_cli.core.rai_header.

Canonical location moved to core/ (RAISE-16509 W8) so that distillation (T3)
can import without an upward waiver. All existing T2 callers (fleet, pipeline)
continue to import from this shim — T2→T5 is a valid downward import.
"""

from raise_cli.core.rai_header import (
    RAI_HEADER_RE,
    build_rai_header,
    parse_rai_header,
)

__all__ = ["RAI_HEADER_RE", "build_rai_header", "parse_rai_header"]
