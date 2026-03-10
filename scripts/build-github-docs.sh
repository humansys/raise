#!/usr/bin/env bash
# build-github-docs.sh — Generate plain markdown docs for GitHub from Starlight .mdx sources
#
# Reads docs/src/content/docs/docs/**/*.mdx, strips Starlight frontmatter fields,
# converts links to relative .md paths, and writes to docs-github/.
#
# Usage:
#   ./scripts/build-github-docs.sh
#
# Output: docs-github/ with plain .md files, ready for GitHub sync.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/docs/src/content/docs/docs"
OUT_DIR="${REPO_ROOT}/docs-github"

# Clean output
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}"

echo "==> Building GitHub docs from ${SRC_DIR}"

# Copy and transform .mdx → .md
find "${SRC_DIR}" -name '*.mdx' | while read -r src_file; do
    # Compute relative path: docs/concepts/memory.mdx → concepts/memory.md
    rel_path="${src_file#${SRC_DIR}/}"
    dest_path="${OUT_DIR}/${rel_path%.mdx}.md"

    # Create parent directory
    mkdir -p "$(dirname "${dest_path}")"

    # Transform:
    # 1. Strip Starlight-specific frontmatter (sidebar, tableOfContents, etc.)
    # 2. Convert /docs/foo/bar/ links to relative paths
    # 3. Rename .mdx → .md
    sed \
        -e '/^sidebar:/,/^[^ ]/{ /^sidebar:/d; /^  /d; }' \
        -e '/^tableOfContents:/,/^[^ ]/{ /^tableOfContents:/d; /^  /d; }' \
        -e 's|](/docs/getting-started/)|](getting-started.md)|g' \
        -e 's|](/docs/concepts/\([^)]*\)/)|](concepts/\1.md)|g' \
        -e 's|](/docs/concepts/)|](concepts/README.md)|g' \
        -e 's|](/docs/guides/\([^)]*\)/)|](guides/\1.md)|g' \
        -e 's|](/docs/cli/\([^)]*\)/)|](cli/\1.md)|g' \
        -e 's|](/docs/cli/)|](cli/README.md)|g' \
        "${src_file}" > "${dest_path}"

    echo "  ${rel_path%.mdx}.md"
done

# Rename index.md → README.md for GitHub rendering
for idx in $(find "${OUT_DIR}" -name 'index.md'); do
    dir="$(dirname "${idx}")"
    mv "${idx}" "${dir}/README.md"
done

echo "==> Done. $(find "${OUT_DIR}" -name '*.md' | wc -l | tr -d ' ') files in ${OUT_DIR}/"
