#!/usr/bin/env bash
# sync-github.sh — Push filtered raise-commons content to GitHub mirror
#
# This script creates a filtered copy of a source branch and force-pushes
# it to the GitHub remote. Internal directories (work/, dev/, .raise/,
# archive/, blog/, docs/) are excluded so the public repo shows only the product.
#
# Usage:
#   ./scripts/sync-github.sh [source-branch] [target-branch]
#
# Defaults:
#   source-branch: main
#   target-branch: main
#
# Prerequisites:
#   - 'github' remote configured: git remote add github git@github.com:humansys/raise.git
#   - Clean working tree (no uncommitted changes)
#
# WARNING: This force-pushes to the GitHub remote. The GitHub mirror is a
# read-only target — all development happens in GitLab (origin).

set -euo pipefail

SOURCE_BRANCH="${1:-main}"
TARGET_BRANCH="${2:-main}"
TEMP_BRANCH="__sync-github-temp"
EXCLUDED_DIRS=("work" "dev" ".raise" "archive" "blog" "docs")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[sync]${NC} $*"; }
warn()  { echo -e "${YELLOW}[sync]${NC} $*"; }
error() { echo -e "${RED}[sync]${NC} $*" >&2; }

# Save current state
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
REPO_ROOT=$(git rev-parse --show-toplevel)

cleanup() {
    info "Cleaning up..."
    cd "$REPO_ROOT"
    git checkout "$ORIGINAL_BRANCH" --quiet 2>/dev/null || true
    git branch -D "$TEMP_BRANCH" --quiet 2>/dev/null || true
}
trap cleanup EXIT

# Preflight checks
if ! git remote get-url github &>/dev/null; then
    error "'github' remote not configured."
    error "Run: git remote add github git@github.com:humansys/raise.git"
    exit 1
fi

if ! git rev-parse --verify "$SOURCE_BRANCH" &>/dev/null; then
    error "Source branch '$SOURCE_BRANCH' does not exist."
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    error "Working tree is not clean. Commit or stash changes first."
    exit 1
fi

info "Syncing $SOURCE_BRANCH → github/$TARGET_BRANCH"
info "Excluded: ${EXCLUDED_DIRS[*]}"

# Create temp branch from source
git checkout "$SOURCE_BRANCH" --quiet
git checkout -b "$TEMP_BRANCH" --quiet

# Remove excluded directories
for dir in "${EXCLUDED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        git rm -rf --quiet "$dir"
        info "Removed $dir/"
    fi
done

# Commit the filtered state
git commit --quiet -m "sync: filtered mirror of $SOURCE_BRANCH

Excluded: ${EXCLUDED_DIRS[*]}
Source: $(git rev-parse "$SOURCE_BRANCH")"

# Force-push to GitHub
info "Pushing to github/$TARGET_BRANCH..."
git push github "$TEMP_BRANCH:$TARGET_BRANCH" --force

info "Done. GitHub mirror updated."
info "Source: $SOURCE_BRANCH ($(git rev-parse --short "$SOURCE_BRANCH"))"
info "Target: github/$TARGET_BRANCH"
