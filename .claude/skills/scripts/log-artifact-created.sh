#!/bin/bash
# RaiSE Telemetry: Log artifact creation event
# Called from skill hooks on PostToolUse for Write/Edit

INPUT=$(cat)
TIMESTAMP=$(date -Iseconds)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"')
SKILL_NAME="${RAISE_SKILL_NAME:-unknown}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/telemetry"

# Log event
echo "{\"event\":\"artifact_created\",\"skill\":\"$SKILL_NAME\",\"tool\":\"$TOOL_NAME\",\"path\":\"$FILE_PATH\",\"session_id\":\"$SESSION_ID\",\"timestamp\":\"$TIMESTAMP\"}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/telemetry/events.jsonl"

exit 0
