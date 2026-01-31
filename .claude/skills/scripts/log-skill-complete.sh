#!/bin/bash
# RaiSE Telemetry: Log skill completion event
# Called from skill hooks on Stop

INPUT=$(cat)
TIMESTAMP=$(date -Iseconds)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
SKILL_NAME="${RAISE_SKILL_NAME:-unknown}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/telemetry"

# Log event
echo "{\"event\":\"skill_completed\",\"skill\":\"$SKILL_NAME\",\"session_id\":\"$SESSION_ID\",\"timestamp\":\"$TIMESTAMP\"}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/telemetry/events.jsonl"

exit 0
