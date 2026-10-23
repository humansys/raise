"""Shared design tokens for the cockpit TUI.

Single source of truth for colors and glyphs consumed by both the Rich
and Textual rendering paths.
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Colors (GitHub dark palette)
# ---------------------------------------------------------------------------

BLUE = "#58A6FF"
GREEN = "#3FB950"
AMBER = "#D29922"
RED = "#F85149"
PURPLE = "#BC8CFF"
TEXT_BRIGHT = "#F0F6FC"
TEXT = "#C9D1D9"
TEXT_DIM = "#8B949E"

# ---------------------------------------------------------------------------
# State glyphs — Unicode with ASCII fallback
#
# One unique shape per SessionState (WCAG 1.4.1: shape is the primary
# channel, color is secondary). ASCII fallbacks are also unique.
# ---------------------------------------------------------------------------


def _use_unicode() -> bool:
    if os.environ.get("RAI_ASCII", "") == "1":
        return False
    try:
        return sys.stdout.encoding.lower().startswith("utf")
    except (AttributeError, LookupError):
        return False


_UNI = _use_unicode()

GLYPH_WORKING: str = "●" if _UNI else "*"  # filled circle — active work
GLYPH_PAUSED: str = "◔" if _UNI else "~"  # quarter circle — paused/awaiting
GLYPH_ERROR: str = "✗" if _UNI else "x"  # cross — failure
GLYPH_DONE: str = "✓" if _UNI else "+"  # check — completed
GLYPH_BLOCKED: str = "⊘" if _UNI else "#"  # circled slash — resource conflict
GLYPH_IDLE: str = "○" if _UNI else "."  # hollow circle — idle/inactive
