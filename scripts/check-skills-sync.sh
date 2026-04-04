#!/usr/bin/env bash
# Gate: verify .claude/skills/ and skills_base/ are in sync.
# Run in pre-commit or CI to prevent skill distribution drift.
# Exit 0 = synced, Exit 1 = drift detected.

set -euo pipefail

SRC=".claude/skills"
DST="packages/raise-cli/src/raise_cli/skills_base"

if [ ! -d "$SRC" ] || [ ! -d "$DST" ]; then
    echo "SKIP: skill directories not found (not in raise-commons root)"
    exit 0
fi

DIFFS=$(diff -rq "$SRC" "$DST" \
    --exclude='__pycache__' \
    --exclude='__init__.py' \
    --exclude='preamble.md' \
    --exclude='contract-template.md' \
    2>&1 | grep -E "differ|Only in" || true)

if [ -n "$DIFFS" ]; then
    echo "ERROR: Skills distribution out of sync!"
    echo ""
    echo "$DIFFS"
    echo ""
    echo "Fix: copy updated skills to skills_base/"
    echo "  rsync -a --delete --exclude='__pycache__' .claude/skills/rai-*/ $DST/"
    echo "  or run: scripts/sync-skills.sh"
    exit 1
fi

echo "OK: skills in sync"
