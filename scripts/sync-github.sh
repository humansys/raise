#!/usr/bin/env bash
# sync-github.sh — Push filtered raise-commons content to GitHub mirror
#
# This script creates a clean orphan commit from a source branch, excluding
# internal directories and files, and force-pushes it to the GitHub remote.
# No git history is carried — the public repo shows only the current state.
#
# Excluded (internal):
#   Dirs:  work/, dev/, .raise/, archive/, blog/, docs/, governance/, .claude/, scripts/
#   Files: .claude.json, .cursorindexingignore, CLAUDE.md, CLAUDE.local.md
#
# Included (public):
#   src/, tests/, framework/, .github/, pyproject.toml, uv.lock,
#   README.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, NOTICE, CHANGELOG.md, .gitignore
#
# Usage:
#   ./scripts/sync-github.sh [source-branch] [target-branch]
#
# Defaults:
#   source-branch: main
#   target-branch: main
#
# Prerequisites:
#   - 'github' remote configured: git remote add github https://github.com/humansys/raise.git
#   - Clean working tree (no uncommitted changes)
#
# WARNING: This force-pushes to the GitHub remote. The GitHub mirror is a
# read-only target — all development happens in GitLab (origin).

set -euo pipefail

SOURCE_BRANCH="${1:-main}"
TARGET_BRANCH="${2:-main}"
TEMP_BRANCH="__sync-github-temp"
EXCLUDED_DIRS=("work" "dev" ".raise" "archive" "blog" "docs" "governance" ".claude" "scripts")
EXCLUDED_FILES=(".claude.json" ".cursorindexingignore" "CLAUDE.md" "CLAUDE.local.md")

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
    error "Run: git remote add github https://github.com/humansys/raise.git"
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

SOURCE_SHA=$(git rev-parse "$SOURCE_BRANCH")
SOURCE_SHORT=$(git rev-parse --short "$SOURCE_BRANCH")

info "Syncing $SOURCE_BRANCH ($SOURCE_SHORT) → github/$TARGET_BRANCH"
info "Excluded dirs: ${EXCLUDED_DIRS[*]}"
info "Excluded files: ${EXCLUDED_FILES[*]}"

# Check out source branch content
git checkout "$SOURCE_BRANCH" --quiet

# Create orphan branch (no history)
git checkout --orphan "$TEMP_BRANCH" --quiet

# Remove excluded directories
for dir in "${EXCLUDED_DIRS[@]}"; do
    if git ls-files --error-unmatch "$dir" &>/dev/null 2>&1; then
        git rm -rf --quiet "$dir"
        info "Removed $dir/"
    fi
done

# Remove excluded files (--ignore-unmatch handles gitignored/missing files)
for file in "${EXCLUDED_FILES[@]}"; do
    git rm -f --quiet --ignore-unmatch "$file"
done

# Create single clean commit
git commit --quiet -m "RaiSE Framework v2 — $(date +%Y-%m-%d)

Open core mirror of raise-commons.
Source: $SOURCE_BRANCH ($SOURCE_SHA)"

# Force-push to GitHub
info "Pushing to github/$TARGET_BRANCH..."
git push github "$TEMP_BRANCH:$TARGET_BRANCH" --force

info "Done. GitHub mirror updated."
info "Source: $SOURCE_BRANCH ($SOURCE_SHORT)"
info "Target: github/$TARGET_BRANCH"
