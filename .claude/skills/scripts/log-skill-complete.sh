#!/bin/bash
# RaiSE Telemetry: Log skill completion event
# Called from skill hooks on Stop
# Emits SkillEvent per ADR-018

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SKILL_NAME="${RAISE_SKILL_NAME:-unknown}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry"

# Calculate duration from start timestamp
TIMESTAMP_FILE="$CLAUDE_PROJECT_DIR/.raise/rai/telemetry/.skill_start_${SKILL_NAME}"
DURATION_SEC="null"

if [ -f "$TIMESTAMP_FILE" ]; then
  START_TIMESTAMP=$(cat "$TIMESTAMP_FILE")

  # Convert timestamps to seconds since epoch and calculate difference
  START_EPOCH=$(date -d "$START_TIMESTAMP" +%s 2>/dev/null || echo "0")
  END_EPOCH=$(date -d "$TIMESTAMP" +%s 2>/dev/null || date +%s)

  if [ "$START_EPOCH" != "0" ]; then
    DURATION_SEC=$((END_EPOCH - START_EPOCH))
  fi

  # Clean up start timestamp file
  rm -f "$TIMESTAMP_FILE"
fi

# Emit SkillEvent (ADR-018 format)
echo "{\"type\":\"skill_event\",\"timestamp\":\"$TIMESTAMP\",\"skill\":\"$SKILL_NAME\",\"event\":\"complete\",\"duration_sec\":$DURATION_SEC}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry/signals.jsonl"

exit 0
