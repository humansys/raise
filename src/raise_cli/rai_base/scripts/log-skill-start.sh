#!/bin/bash
# RaiSE Telemetry: Log skill start event
# Called from skill hooks on SessionStart or first tool use
# Emits SkillEvent per ADR-018

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SKILL_NAME="${RAISE_SKILL_NAME:-unknown}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/rai/personal/telemetry"

# Store start timestamp for duration calculation
TIMESTAMP_FILE="$CLAUDE_PROJECT_DIR/.raise/rai/personal/telemetry/.skill_start_${SKILL_NAME}"
echo "$TIMESTAMP" > "$TIMESTAMP_FILE"

# Emit SkillEvent (ADR-018 format)
echo "{\"type\":\"skill_event\",\"timestamp\":\"$TIMESTAMP\",\"skill\":\"$SKILL_NAME\",\"event\":\"start\",\"duration_sec\":null}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/rai/personal/telemetry/signals.jsonl"

exit 0
