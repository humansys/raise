#!/bin/bash
# RaiSE Pre-Compact Hook — log journal state before compaction
# Called before context compaction (auto or manual).
# PreCompact has NO decision control — stdout is ignored by Claude Code.
# This hook is purely for logging/side effects.

# Hardcode project dir — hook environment is unpredictable
PROJECT_DIR="/home/emilio/Code/raise-commons-e325"
LOG="/tmp/rai-hook-pre-compact.log"

# Log everything for debugging
exec 2>"$LOG"
echo "=== pre-compact-journal.sh ===" >&2
echo "date: $(date)" >&2
echo "PWD: $(pwd)" >&2
echo "CLAUDE_PROJECT_DIR: ${CLAUDE_PROJECT_DIR:-UNSET}" >&2
echo "PATH: $PATH" >&2

# Ensure uv is on PATH
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"

# Log current journal state (for debugging — stdout not used by PreCompact)
OUTPUT=$(uv run --project "$PROJECT_DIR" rai session journal show --compact --project "$PROJECT_DIR" 2>&1)
RC=$?
echo "uv exit code: $RC" >&2
echo "uv output: $OUTPUT" >&2
echo "journal snapshot logged before compaction" >&2
