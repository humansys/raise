#!/usr/bin/env bash
# SonarCloud issues viewer — raise-commons
# Usage: SONAR_TOKEN=<token> ./dev/sops/sonarcloud-issues.sh [OPTIONS]
#
# Options:
#   --type    VULNERABILITY|BUG|CODE_SMELL|SECURITY_HOTSPOT (default: all)
#   --sev     BLOCKER|CRITICAL|MAJOR|MINOR|INFO (default: all)
#   --status  OPEN|CONFIRMED|REOPENED|RESOLVED|CLOSED (default: OPEN)
#   --raw     Print raw JSON instead of formatted output

set -euo pipefail

SONAR_HOST="https://sonarcloud.io"
PROJECT_KEY="humansys-demos_raise-commons"
ORG="test-raise"
PAGE_SIZE=500

TYPE_FILTER=""
SEV_FILTER=""
STATUS_FILTER="OPEN"
RAW=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)  TYPE_FILTER="&types=$2";       shift 2 ;;
    --sev)   SEV_FILTER="&severities=$2";   shift 2 ;;
    --status) STATUS_FILTER="$2";           shift 2 ;;
    --raw)   RAW=true;                      shift   ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${SONAR_TOKEN:-}" ]]; then
  echo "ERROR: SONAR_TOKEN is not set." >&2
  echo "  → sonarcloud.io → My Account → Security → Generate Token" >&2
  exit 1
fi

fetch_page() {
  local page=$1
  curl -sf \
    "${SONAR_HOST}/api/issues/search?componentKeys=${PROJECT_KEY}&organization=${ORG}&statuses=${STATUS_FILTER}${TYPE_FILTER}${SEV_FILTER}&ps=${PAGE_SIZE}&p=${page}" \
    -u "${SONAR_TOKEN}:"
}

# ── Fetch all pages ──────────────────────────────────────────────────────────
all_issues="[]"
page=1

while true; do
  response=$(fetch_page "$page")
  total=$(echo "$response" | jq '.total')
  issues=$(echo "$response" | jq '.issues')
  count=$(echo "$issues" | jq 'length')

  all_issues=$(echo "$all_issues $issues" | jq -s 'add')

  fetched=$(( (page - 1) * PAGE_SIZE + count ))
  [[ "$fetched" -ge "$total" ]] && break
  (( page++ ))
done

total_fetched=$(echo "$all_issues" | jq 'length')

if $RAW; then
  echo "$all_issues" | jq .
  exit 0
fi

# ── Formatted output ─────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  SonarCloud · ${PROJECT_KEY}"
echo "  Status: ${STATUS_FILTER}${TYPE_FILTER}${SEV_FILTER}"
echo "  Total: ${total_fetched} issues"
echo "══════════════════════════════════════════════════════════"
echo ""

echo "$all_issues" | jq -r '
  group_by(.severity)[] |
  (.[0].severity) as $sev |
  "── \($sev) (\(length)) ──────────────────────────────",
  (.[] |
    "  [\(.type)] \(.message)",
    "  File: \(.component | split(":")[1] // .component)\(.line // "" | if . != "" then ":\(.)" else "" end)",
    "  Key:  \(.key)",
    ""
  )
'
