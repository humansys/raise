#!/bin/bash
# RaiSE Telemetry: Log skill start event
# Called from skill hooks on SessionStart or first tool use

INPUT=$(cat)
TIMESTAMP=$(date -Iseconds)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
SKILL_NAME="${RAISE_SKILL_NAME:-unknown}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/telemetry"

# Log event
echo "{\"event\":\"skill_started\",\"skill\":\"$SKILL_NAME\",\"session_id\":\"$SESSION_ID\",\"timestamp\":\"$TIMESTAMP\"}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/telemetry/events.jsonl"

exit 0
