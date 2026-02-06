#!/bin/bash
# RaiSE Telemetry: Log error event
# Called when tool errors occur
# Emits ErrorEvent per ADR-018

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Error metadata from environment
ERROR_TOOL="${RAISE_ERROR_TOOL:-unknown}"
ERROR_TYPE="${RAISE_ERROR_TYPE:-unknown}"
ERROR_CONTEXT="${RAISE_ERROR_CONTEXT:-null}"
ERROR_RECOVERABLE="${RAISE_ERROR_RECOVERABLE:-true}"

# Ensure telemetry directory exists
mkdir -p "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry"

# Format context as JSON string or null
if [ "$ERROR_CONTEXT" != "null" ] && [ -n "$ERROR_CONTEXT" ]; then
  CONTEXT_JSON="\"$ERROR_CONTEXT\""
else
  CONTEXT_JSON="null"
fi

# Emit ErrorEvent (ADR-018 format)
echo "{\"type\":\"error_event\",\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$ERROR_TOOL\",\"error_type\":\"$ERROR_TYPE\",\"context\":$CONTEXT_JSON,\"recoverable\":$ERROR_RECOVERABLE}" \
  >> "$CLAUDE_PROJECT_DIR/.raise/rai/telemetry/signals.jsonl"

exit 0
