#!/usr/bin/env bash
# Sync .claude/skills/ → skills_base/ (distribution source).
# Run after modifying any skill to keep distribution in sync.

set -euo pipefail

SRC=".claude/skills"
DST="packages/raise-cli/src/raise_cli/skills_base"

if [ ! -d "$SRC" ] || [ ! -d "$DST" ]; then
    echo "ERROR: must run from raise-commons root"
    exit 1
fi

for skill_dir in "$SRC"/rai-*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$DST/$skill_name"
    cp "$skill_dir/SKILL.md" "$DST/$skill_name/SKILL.md"
    # Copy reference dirs if they exist
    for ref_dir in "$skill_dir"references "$skill_dir"_references; do
        if [ -d "$ref_dir" ]; then
            cp -r "$ref_dir" "$DST/$skill_name/"
        fi
    done
done

echo "Synced $(ls -d "$SRC"/rai-*/ | wc -l) skills to $DST"
