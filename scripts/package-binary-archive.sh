#!/usr/bin/env bash
# scripts/package-binary-archive.sh — RAISE-15631
#
# Packages a PyInstaller onedir output (executable + _internal/) into a
# platform archive + .sha256 sidecar. Fixes a defect introduced in S6
# (RAISE-15630): the CI build jobs published the loose executable only,
# dropping _internal/ — the published "binary" could not run standalone.
#
# Usage: package-binary-archive.sh <dist_dir> <archive_path_without_ext> <platform>
#   dist_dir                 directory containing the executable + _internal/
#   archive_path_without_ext output path, no extension (extension is derived
#                             from <platform>)
#   platform                 linux | darwin (tar.gz) — windows packaging is
#                             inline pwsh in .gitlab-ci.yml, not this script
set -euo pipefail

DIST_DIR="${1:?usage: package-binary-archive.sh <dist_dir> <archive_path_without_ext> <platform>}"
ARCHIVE_BASE="${2:?usage: package-binary-archive.sh <dist_dir> <archive_path_without_ext> <platform>}"
PLATFORM="${3:?usage: package-binary-archive.sh <dist_dir> <archive_path_without_ext> <platform>}"

if [ ! -d "$DIST_DIR" ]; then
  echo "FAIL: dist dir not found: $DIST_DIR" >&2
  exit 1
fi

case "$PLATFORM" in
  linux|darwin)
    ARCHIVE="${ARCHIVE_BASE}.tar.gz"
    ;;
  *)
    echo "FAIL: unknown platform '$PLATFORM' (expected linux|darwin)" >&2
    exit 1
    ;;
esac

mkdir -p "$(dirname "$ARCHIVE")"
tar -czf "$ARCHIVE" -C "$DIST_DIR" .

if command -v sha256sum >/dev/null 2>&1; then
  (cd "$(dirname "$ARCHIVE")" && sha256sum "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256")
else
  (cd "$(dirname "$ARCHIVE")" && shasum -a 256 "$(basename "$ARCHIVE")" > "$(basename "$ARCHIVE").sha256")
fi

echo "Packaged $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1)) + ${ARCHIVE}.sha256"
