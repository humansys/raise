#!/usr/bin/env bash
# sync-github.sh — Push filtered raise-commons content to GitHub mirror
#
# This script creates a clean orphan commit from a source branch, excluding
# internal directories and files, and force-pushes it to the GitHub remote.
# No git history is carried — the public repo shows only the current state.
#
# IMPORTANT: Uses git plumbing (read-tree/write-tree) to build the filtered
# commit entirely in the object store. The working tree is NEVER modified.
# This prevents Claude Code from losing track of skills when .claude/ is
# temporarily removed during sync.
#
# Excluded (internal):
#   Dirs:  work/, dev/, .raise/, archive/, blog/, docs/, governance/, .claude/, scripts/, src/rai_pro/
#   Files: .claude.json, .cursorindexingignore, CLAUDE.md, CLAUDE.local.md, .gitlab-ci.yml
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
#
# WARNING: This force-pushes to the GitHub remote. The GitHub mirror is a
# read-only target — all development happens in GitLab (origin).

set -euo pipefail

SOURCE_BRANCH="${1:-main}"
TARGET_BRANCH="${2:-main}"
EXCLUDED_DIRS=("work" "dev" ".raise" "archive" "blog" "docs" "governance" ".claude" "scripts")
EXCLUDED_FILES=(".claude.json" ".cursorindexingignore" "CLAUDE.md" "CLAUDE.local.md" ".gitlab-ci.yml")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[sync]${NC} $*"; }
warn()  { echo -e "${YELLOW}[sync]${NC} $*"; }
error() { echo -e "${RED}[sync]${NC} $*" >&2; }

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

SOURCE_SHA=$(git rev-parse "$SOURCE_BRANCH")
SOURCE_SHORT=$(git rev-parse --short "$SOURCE_BRANCH")

info "Syncing $SOURCE_BRANCH ($SOURCE_SHORT) → github/$TARGET_BRANCH"
info "Excluded dirs: ${EXCLUDED_DIRS[*]}"
info "Excluded files: ${EXCLUDED_FILES[*]}"

# Build filtered tree using git plumbing (no working tree changes)
# 1. Read source tree into a temporary index
export GIT_INDEX_FILE=$(mktemp)
trap "rm -f '$GIT_INDEX_FILE'" EXIT

git read-tree "$SOURCE_BRANCH"

# 2. Remove excluded directories from the temporary index
for dir in "${EXCLUDED_DIRS[@]}"; do
    git rm -r --cached --quiet --ignore-unmatch "$dir"
    info "Excluded $dir/"
done

# 3. Remove excluded files from the temporary index
for file in "${EXCLUDED_FILES[@]}"; do
    git rm --cached --quiet --ignore-unmatch "$file"
done

# 3b. Remove private source directories
git rm -r --cached --quiet --ignore-unmatch "src/rai_pro"
info "Excluded src/rai_pro/"

# 4. Write the filtered index as a tree object
TREE=$(git write-tree)

# 5. Create an orphan commit (no parent) from the filtered tree
COMMIT=$(git commit-tree "$TREE" -m "RaiSE Framework v2 — $(date +%Y-%m-%d)

Open core mirror of raise-commons.
Source: $SOURCE_BRANCH ($SOURCE_SHA)")

# 6. Force-push the commit to GitHub
info "Pushing to github/$TARGET_BRANCH..."
git push github "$COMMIT:refs/heads/$TARGET_BRANCH" --force

info "Done. GitHub mirror updated."
info "Source: $SOURCE_BRANCH ($SOURCE_SHORT)"
info "Target: github/$TARGET_BRANCH"
