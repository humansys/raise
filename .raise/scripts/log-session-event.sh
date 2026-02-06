#!/bin/bash
# RaiSE Telemetry: Log session event
# Called from session-close skill
# Emits SessionEvent per ADR-018

# Read from stdin or environment
INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Session metadata from environment (set by skill context)
SESSION_TYPE="${RAISE_SESSION_TYPE:-unknown}"
SESSION_OUTCOME="${RAISE_SESSION_OUTCOME:-unknown}"
SESSION_DURATION_MIN="${RAISE_SESSION_DURATION_MIN:-null}"
SESSION_FEATURES="${RAISE_SESSION_FEATURES:-[]}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry"

# Format features as JSON array if it's a comma-separated string
if [ "$SESSION_FEATURES" != "[]" ] && [ "$SESSION_FEATURES" != "null" ]; then
  # Convert "F1,F2,F3" to ["F1","F2","F3"]
  FEATURES_JSON="[$(echo "$SESSION_FEATURES" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/'))]"
else
  FEATURES_JSON="[]"
fi

# Emit SessionEvent (ADR-018 format)
echo "{\"type\":\"session_event\",\"timestamp\":\"$TIMESTAMP\",\"session_type\":\"$SESSION_TYPE\",\"outcome\":\"$SESSION_OUTCOME\",\"duration_min\":$SESSION_DURATION_MIN,\"features\":$FEATURES_JSON}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry/signals.jsonl"

exit 0
