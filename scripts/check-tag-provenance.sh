#!/usr/bin/env bash
# check-tag-provenance.sh — Channel guard for the public GitHub mirror.
# RAISE-17079: Verifies that a tag points at a sanctioned orphan snapshot
# from scripts/sync-github.sh before allowing build/publish workflows to
# proceed.
#
# Three checks (all fail-closed with ::error:: annotations):
#   1. Orphan: commit has 0 parents (mirror invariant, RAISE-16591)
#   2. Source line: trailer Source: <branch> (<sha>) where branch matches
#      main or release/X.Y.0 derived from the tag version
#   3. Version parity: pyproject.toml version == tag version
#
# Inputs (env):
#   GITHUB_REF  — e.g. refs/tags/v3.1.1 or refs/heads/ci/pre-release-abc
#   SHA         — commit SHA to check (default: HEAD)
#   GITHUB_OUTPUT — path to GitHub Actions output file (optional)
#
# Outputs (written to $GITHUB_OUTPUT when set):
#   package     — resolved package name (raise-cli or raise-core)
#   version     — version string from the tag
#   prerelease  — true|false
#
# Exits 0 on success or bypass (non-tag ref); exits 1 on rejection.
set -euo pipefail

PREFIX="[channel-guard]"

# ---------------------------------------------------------------------------
# Bypass: non-tag refs (workflow_dispatch)
# ---------------------------------------------------------------------------
GITHUB_REF="${GITHUB_REF:-}"
if [[ ! "$GITHUB_REF" =~ ^refs/tags/ ]]; then
    echo "::notice::${PREFIX} GITHUB_REF=${GITHUB_REF:-<unset>} is not a tag (workflow_dispatch) — no channel to verify, skipping."
    exit 0
fi

TAG="${GITHUB_REF#refs/tags/}"
SHA="${SHA:-HEAD}"
SHA=$(git rev-parse "$SHA")

# ---------------------------------------------------------------------------
# Parse tag → (package, version, release line)
# ---------------------------------------------------------------------------
# Tag formats:
#   v3.1.0         → package=raise-cli, version=3.1.0
#   v3.1.0rc5      → package=raise-cli, version=3.1.0rc5
#   raise-cli-v3.1.1  → package=raise-cli, version=3.1.1
#   raise-core-v3.2.0a1 → package=raise-core, version=3.2.0a1

PACKAGE=""
VERSION=""

if [[ "$TAG" =~ ^v([0-9]+\.[0-9]+\..+)$ ]]; then
    # Bare version tag: v3.1.0, v3.1.0rc5
    PACKAGE="raise-cli"
    VERSION="${BASH_REMATCH[1]}"
elif [[ "$TAG" =~ ^([a-z][a-z0-9-]*)-v([0-9]+\.[0-9]+\..+)$ ]]; then
    # Package-prefixed: raise-cli-v3.1.1, raise-core-v3.2.0a1, raise-agent-spi-v0.1.0
    PACKAGE="${BASH_REMATCH[1]}"
    VERSION="${BASH_REMATCH[2]}"
else
    echo "::error::${PREFIX} tag '${TAG}' does not match any known format (v{version} or {package}-v{version}). Cannot verify provenance."
    exit 1
fi

# Derive the release line: strip pre-release suffixes to get X.Y.Z, then
# use X.Y.0 → release/X.Y.0. Same rule as .gitlab-ci.yml guard:tag-ancestry
# (RAISE-17082 D3).
BASE_VERSION="${VERSION%%[abr]*}"
# Handle rc specifically since 'r' alone would match release versions
if [[ "$VERSION" == *rc* ]]; then
    BASE_VERSION="${VERSION%%rc*}"
fi
# Also handle alpha (a) and beta (b) — already handled by the first strip,
# but be explicit for versions like 3.2.0a1
if [[ "$VERSION" == *a* ]]; then
    BASE_VERSION="${VERSION%%a*}"
fi
if [[ "$VERSION" == *b* ]]; then
    BASE_VERSION="${VERSION%%b*}"
fi

# Extract major.minor from base version (X.Y.Z → X.Y)
if [[ "$BASE_VERSION" =~ ^([0-9]+\.[0-9]+)\. ]]; then
    MAJOR_MINOR="${BASH_REMATCH[1]}"
else
    echo "::error::${PREFIX} cannot extract major.minor from version '${VERSION}' (base: ${BASE_VERSION})."
    exit 1
fi
RELEASE_LINE="release/${MAJOR_MINOR}.0"

# Classify channel: prerelease if version contains a, b, or rc
PRERELEASE="false"
case "$VERSION" in
    *a*|*b*|*rc*) PRERELEASE="true" ;;
esac

if [[ "$PRERELEASE" == "true" ]]; then
    CHANNEL="prerelease"
else
    CHANNEL="stable"
fi

echo "${PREFIX} tag ${TAG} -> package ${PACKAGE}, version ${VERSION}, line ${RELEASE_LINE}"

# ---------------------------------------------------------------------------
# Check 1: Orphan (commit must have 0 parents)
# Uses git cat-file -p to read raw object data, which preserves parent lines
# even in shallow clones (depth=1). git rev-list --parents is unreliable in
# shallow clones because graft boundaries hide parent information (C1 fix).
# ---------------------------------------------------------------------------
PARENT_COUNT=$(git cat-file -p "$SHA" | grep -c '^parent ' || true)

if [[ "$PARENT_COUNT" -ne 0 ]]; then
    echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — commit has ${PARENT_COUNT} parent(s); every publishable ref on the mirror must be an orphan snapshot from scripts/sync-github.sh (RAISE-16591)."
    exit 1
fi
echo "${PREFIX} commit ${SHA:0:8} is an orphan snapshot"

# ---------------------------------------------------------------------------
# Check 2: Source line — trailer must name main or release/X.Y.0
# ---------------------------------------------------------------------------
COMMIT_MSG=$(git log -1 --format='%B' "$SHA")
SOURCE_BRANCH=""
SOURCE_SHA=""

if [[ "$COMMIT_MSG" =~ Source:\ ([^[:space:]]+)\ \(([0-9a-f]{40})\) ]]; then
    SOURCE_BRANCH="${BASH_REMATCH[1]}"
    SOURCE_SHA="${BASH_REMATCH[2]}"
else
    echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — commit message has no 'Source: <branch> (<sha>)' trailer. Only orphan snapshots produced by scripts/sync-github.sh carry this trailer."
    exit 1
fi

ALLOWED_PATTERN="^(main|${RELEASE_LINE//./\\.})$"
if [[ ! "$SOURCE_BRANCH" =~ $ALLOWED_PATTERN ]]; then
    echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — Source branch '${SOURCE_BRANCH}' is not main or ${RELEASE_LINE}. Only snapshots produced by scripts/sync-github.sh from main or release/X.Y.0 may be tagged; ci/* snapshots (sync-github-ci-snapshot.sh, check-release-binaries.sh) are dispatch-only."
    exit 1
fi
echo "${PREFIX} source: ${SOURCE_BRANCH} (${SOURCE_SHA}) — allowed (main | ${RELEASE_LINE})"

# ---------------------------------------------------------------------------
# Check 3: Version parity — pyproject.toml version must match tag version
# ---------------------------------------------------------------------------
PYPROJECT_PATH="packages/${PACKAGE}/pyproject.toml"
PYPROJECT_VERSION=""

if git cat-file -e "${SHA}:${PYPROJECT_PATH}" 2>/dev/null; then
    PYPROJECT_VERSION=$(git show "${SHA}:${PYPROJECT_PATH}" | grep -E '^version = "' | head -1 | sed 's/version = "//;s/"//') || true
    if [[ -z "$PYPROJECT_VERSION" ]]; then
        echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — ${PYPROJECT_PATH} at this commit has no static 'version = \"...\"' line. Dynamic versioning is not supported for release tags."
        exit 1
    fi
else
    echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — ${PYPROJECT_PATH} does not exist at this commit."
    exit 1
fi

if [[ "$PYPROJECT_VERSION" != "$VERSION" ]]; then
    echo "::error::${PREFIX} tag ${TAG} (sha ${SHA}) rejected — ${PYPROJECT_PATH} at this commit is version ${PYPROJECT_VERSION}, tag says ${VERSION}. A stable tag on prerelease content (or vice versa) is the channel leak this guard exists to stop."
    exit 1
fi
echo "${PREFIX} ${PYPROJECT_PATH} version ${PYPROJECT_VERSION} == tag version ${VERSION}"

# ---------------------------------------------------------------------------
# Emit outputs
# ---------------------------------------------------------------------------
echo "${PREFIX} channel: ${CHANNEL}"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    {
        echo "package=${PACKAGE}"
        echo "version=${VERSION}"
        echo "prerelease=${PRERELEASE}"
    } >> "$GITHUB_OUTPUT"
fi

exit 0
