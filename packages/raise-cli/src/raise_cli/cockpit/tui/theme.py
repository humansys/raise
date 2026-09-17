"""Copper & Patina theme tokens for the cockpit TUI (RAISE-16858).

Single sanctioned home for hex colors in cockpit/tui. CSS uses $tokens;
Rich markup uses the MARKUP_* constants below.
"""

from __future__ import annotations

from textual.theme import Theme

COPPER_PATINA_DARK = Theme(
    name="copper-patina-dark",
    dark=True,
    primary="#c2813d",  # copper — primary brand chrome
    secondary="#d4944f",  # copper-bright — secondary actions
    accent="#d4944f",  # copper-bright — focus rings, hover states
    foreground="#fafafa",  # text-primary (near-white)
    background="#121212",  # surface-base
    surface="#1a1a1a",  # surface-elevated
    panel="#0a0a0a",  # surface-deep
    warning="#d9b25c",  # amber — PAUSED state
    error="#e0664a",  # terracotta — ERROR state
    success="#8fae7e",  # sage — WORKING state
    variables={
        "overlay1": "#71717a",  # text-tertiary, overlay/inert
        "selection_wash": "#201810",  # copper wash for selected row
        "surface_warm": "#14110d",  # warm surface for TopBar/FilterBar
    },
)

# LATTE (light variant, H2 scope) — copy-paste starting point for H2:
#
# LATTE = Theme(
#     name="copper-patina-light",
#     dark=False,
#     primary="#8839ef",
#     secondary="#ea76cb",
#     accent="#1e66f5",
#     foreground="#4c4f69",
#     background="#eff1f5",
#     surface="#ccd0da",
#     panel="#e6e9ef",
#     warning="#df8e1d",
#     error="#d20f39",
#     success="#40a02b",
#     variables={"overlay1": "#8c8fa1"},
# )

# State-specific Rich markup colors (render-time, not CSS layer). Copper
# (#c2813d, COPPER_PATINA_DARK.primary) is chrome-only — never a state color.
MARKUP_WORKING = "#8fae7e"  # sage — active work
MARKUP_PAUSED = "#d9b25c"  # amber — paused/awaiting
MARKUP_ERROR = "#e0664a"  # terracotta — failure/blocked
MARKUP_DONE = "#6fa08c"  # verdigris — completed
MARKUP_BLOCKED = "#b3627c"  # rosewood — resource conflict
MARKUP_IDLE = "#7a746c"  # warm taupe — idle/inactive

# Non-state uses (command palette, metadata, inert text)
MARKUP_MUTED = "#71717a"  # text-tertiary (matches overlay1)
MARKUP_COPPER = "#c2813d"  # chrome-only — selection marker, never a state color

# Selection/surface washes
MARKUP_SELECTION_WASH = "#201810"
MARKUP_SURFACE_WARM = "#14110d"
