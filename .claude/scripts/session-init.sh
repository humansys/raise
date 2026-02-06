#!/bin/bash
# RaiSE Session Initialization Hook
# Called automatically on new Claude Code sessions
# Output is injected into Claude's context

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
IDENTITY_DIR="$PROJECT_DIR/.raise/rai/identity"
MEMORY_DIR="$PROJECT_DIR/.raise/rai/memory"

# Preload identity (who I am)
if [ -d "$IDENTITY_DIR" ]; then
    echo "## Rai Identity (preloaded)"
    echo ""
    if [ -f "$IDENTITY_DIR/core.md" ]; then
        cat "$IDENTITY_DIR/core.md"
        echo ""
    fi
    if [ -f "$IDENTITY_DIR/perspective.md" ]; then
        cat "$IDENTITY_DIR/perspective.md"
        echo ""
    fi
    echo "---"
    echo ""
fi

# Check if memory directory exists
if [ ! -d "$MEMORY_DIR" ]; then
    echo "## Session Context"
    echo ""
    echo "**Note:** Memory directory not found at .rai/memory/"
    echo "Run /session-start for full context loading."
    exit 0
fi

# Memory summary (retrieve details on-demand)
echo "## Memory Context (summary)"
echo ""

# Count entries
PATTERN_COUNT=$(wc -l < "$MEMORY_DIR/patterns.jsonl" 2>/dev/null | tr -d ' ' || echo "0")
CAL_COUNT=$(wc -l < "$MEMORY_DIR/calibration.jsonl" 2>/dev/null | tr -d ' ' || echo "0")
SESSION_COUNT=$(wc -l < "$MEMORY_DIR/sessions/index.jsonl" 2>/dev/null | tr -d ' ' || echo "0")

echo "**Memory loaded:** $PATTERN_COUNT patterns, $CAL_COUNT calibrations, $SESSION_COUNT sessions"
echo ""

# Get last session
if [ -f "$MEMORY_DIR/sessions/index.jsonl" ]; then
    LAST_SESSION=$(tail -1 "$MEMORY_DIR/sessions/index.jsonl" 2>/dev/null | jq -r '.summary // "Unknown"' 2>/dev/null || echo "Unknown")
    LAST_DATE=$(tail -1 "$MEMORY_DIR/sessions/index.jsonl" 2>/dev/null | jq -r '.date // "Unknown"' 2>/dev/null || echo "Unknown")
    echo "**Last session:** $LAST_SESSION ($LAST_DATE)"
fi

# Get current focus from CLAUDE.local.md
if [ -f "$PROJECT_DIR/CLAUDE.local.md" ]; then
    # Extract Epic line (contains "| Epic |")
    EPIC=$(grep "| Epic |" "$PROJECT_DIR/CLAUDE.local.md" 2>/dev/null | sed 's/.*| Epic | \(.*\) |/\1/' | sed 's/\*//g' | head -c 60 || echo "Unknown")
    # Extract Next Work line
    NEXT=$(grep "| Next |" "$PROJECT_DIR/CLAUDE.local.md" 2>/dev/null | sed 's/.*| Next | \(.*\) |/\1/' | head -c 60 || echo "")
    echo "**Current focus:** $EPIC"
    echo "**Next work:** $NEXT"
fi

echo ""

# Get recent calibration (velocity indicator)
if [ -f "$MEMORY_DIR/calibration.jsonl" ]; then
    LAST_CAL=$(tail -1 "$MEMORY_DIR/calibration.jsonl" 2>/dev/null)
    if [ -n "$LAST_CAL" ]; then
        CAL_RATIO=$(echo "$LAST_CAL" | jq -r '.ratio // "N/A"' 2>/dev/null || echo "N/A")
        CAL_FEATURE=$(echo "$LAST_CAL" | jq -r '.feature // "Unknown"' 2>/dev/null || echo "Unknown")
        if [ "$CAL_RATIO" != "null" ] && [ "$CAL_RATIO" != "N/A" ]; then
            echo "**Recent velocity:** ${CAL_RATIO}x ($CAL_FEATURE)"
        fi
    fi
fi

echo ""
echo "---"
echo "_Run /session-start for full analysis with improvement signals._"
