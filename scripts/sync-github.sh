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
# Excluded (internal/proprietary):
#   Dirs:  work/, dev/, .raise/, archive/, blog/, governance/, .claude/,
#          .agent/, scripts/, htmlcov/, dist/, packages/raise-pro/,
#          packages/raise-server/, site/
#   Files: .claude.json, .cursorindexingignore, CLAUDE.md, CLAUDE.local.md,
#          .gitlab-ci.yml, .coverage, .envrc, .pre-commit-config.yaml,
#          .secrets.baseline, DEMO-STRATEGY.md, AGENTS.md,
#          sonar-project.properties, scope.md, docker-compose.yml, bug-*-*.md
#
# Included (public):
#   packages/raise-core/, packages/raise-cli/, framework/, docs/, .github/,
#   pyproject.toml, uv.lock, README.md, LICENSE, CONTRIBUTING.md,
#   CODE_OF_CONDUCT.md, NOTICE, CHANGELOG.md, SECURITY.md, llms.txt, .gitignore
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
EXCLUDED_DIRS=("work" "dev" ".raise" "archive" "blog" "governance" ".claude" ".agent" "scripts" "htmlcov" "dist" "packages/raise-pro" "packages/raise-server" "site")
EXCLUDED_FILES=(".claude.json" ".cursorindexingignore" "CLAUDE.md" "CLAUDE.local.md" ".gitlab-ci.yml" ".coverage" ".envrc" ".pre-commit-config.yaml" ".secrets.baseline" "DEMO-STRATEGY.md" "AGENTS.md" "sonar-project.properties" "scope.md" "docker-compose.yml" "bug-396-retro.md" "bug-396-scope.md" "bug-397-retro.md" "bug-397-scope.md" "bug-398-retro.md" "bug-398-scope.md" ".github/workflows/deploy-site.yml")

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

# 3b. No longer needed — proprietary code now lives in packages/raise-pro/
# and packages/raise-server/, both excluded as directories above.
# Tests are colocated per-package, so no selective test exclusion needed.

# 4. Patch pyproject.toml — remove references to excluded proprietary packages
#    (raise-pro, raise-server are excluded from GitHub mirror)
TMPTOML=$(mktemp)
git show :pyproject.toml > "$TMPTOML"

# Remove workspace source entries for proprietary packages
sed -i.bak '/^raise-server = { workspace = true }/d' "$TMPTOML"
sed -i.bak '/^raise-pro = { workspace = true }/d' "$TMPTOML"

# Remove dev dependency entries for proprietary packages
sed -i.bak '/^    "raise-pro",$/d' "$TMPTOML"
sed -i.bak '/^    "raise-server",$/d' "$TMPTOML"

# Remove proprietary package paths from pyright include
sed -i.bak '/"packages\/raise-pro\/src"/d' "$TMPTOML"
sed -i.bak '/"packages\/raise-server\/src"/d' "$TMPTOML"

# Remove proprietary package paths from pytest cov
sed -i.bak '/--cov=packages\/raise-pro/d' "$TMPTOML"
sed -i.bak '/--cov=packages\/raise-server/d' "$TMPTOML"

# Remove proprietary package test paths from testpaths
sed -i.bak '/"packages\/raise-pro\/tests"/d' "$TMPTOML"
sed -i.bak '/"packages\/raise-server\/tests"/d' "$TMPTOML"

# Remove proprietary package paths from coverage source
sed -i.bak '/"packages\/raise-pro\/src\/rai_pro"/d' "$TMPTOML"
sed -i.bak '/"packages\/raise-server\/src\/raise_server"/d' "$TMPTOML"

# Write patched pyproject.toml back into the git index
BLOB=$(git hash-object -w "$TMPTOML")
git update-index --replace --cacheinfo 100644,"$BLOB",pyproject.toml
rm -f "$TMPTOML" "$TMPTOML.bak"
info "Patched pyproject.toml — removed proprietary package references"

# 5. Write the filtered index as a tree object
TREE=$(git write-tree)

# 6. Create an orphan commit (no parent) from the filtered tree
COMMIT=$(git commit-tree "$TREE" -m "RaiSE Framework v2 — $(date +%Y-%m-%d)

Open core mirror of raise-commons.
Source: $SOURCE_BRANCH ($SOURCE_SHA)")

# 7. Force-push the commit to GitHub
info "Pushing to github/$TARGET_BRANCH..."
git push github "$COMMIT:refs/heads/$TARGET_BRANCH" --force

info "Done. GitHub mirror updated."
info "Source: $SOURCE_BRANCH ($SOURCE_SHORT)"
info "Target: github/$TARGET_BRANCH"
