#!/usr/bin/env bash
# scripts/install.sh — Install rai + rai-mcp-pipeline standalone binaries (Linux/macOS)
#
# No Python required — downloads prebuilt onedir binaries and installs them
# atomically: if either binary fails to download or verify, nothing is
# installed or modified (rai and rai-mcp-pipeline never end up at different
# versions).
#
# Usage:
#   curl -fsSL https://github.com/humansys/raise/releases/latest/download/install.sh | bash
#   ./install.sh                                 # installs latest release
#   ./install.sh --version v3.1.0               # install a specific release
#   ./install.sh --version v3.1.0 --prefix /usr/local
#   BASE_URL=https://example.com ./install.sh --version v3.1.0
#
# Env overrides: BASE_URL, RAI_VERSION, PREFIX (same as --base-url/--version/--prefix)
#
# Prerequisites: curl, tar, sha256sum or shasum.

set -euo pipefail

# BASE_URL default: GitHub Releases in humansys/raise (RAISE-15664) — the
# build.yml workflow publishes each binary + .sha256 as a Release asset.
DEFAULT_BASE_URL="https://github.com/humansys/raise/releases/download"
BASE_URL="${BASE_URL:-$DEFAULT_BASE_URL}"
VERSION="${RAI_VERSION:-}"
PREFIX="${PREFIX:-$HOME/.local}"
PREFIX_EXPLICIT=0
BINARIES=(rai rai-mcp-pipeline)

if [[ -t 1 ]]; then
  C_CYAN=$'\033[36m'; C_GREEN=$'\033[32m'; C_RED=$'\033[31m'; C_RESET=$'\033[0m'
else
  C_CYAN=""; C_GREEN=""; C_RED=""; C_RESET=""
fi
step() { printf "\n${C_CYAN}[STEP]${C_RESET} %s\n" "$*"; }
ok()   { printf "  ${C_GREEN}[OK]${C_RESET} %s\n" "$*"; }
fail() { printf "  ${C_RED}[FAIL]${C_RESET} %s\n" "$*" >&2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; PREFIX_EXPLICIT=1; shift 2 ;;
    -h|--help) sed -n '2,/^$/p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) fail "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  step "No version specified — resolving latest release from GitHub"
  VERSION=$(curl -fsSL "https://api.github.com/repos/humansys/raise/releases/latest" \
    | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": "\(.*\)".*/\1/')
  if [[ -z "$VERSION" ]]; then
    fail "Could not resolve latest version. Pass --version vX.Y.Z or set RAI_VERSION."
    exit 1
  fi
  ok "Latest version: $VERSION"
fi

# Root installs default to /usr/local unless the caller passed --prefix explicitly.
if [[ "$(id -u)" -eq 0 && "$PREFIX_EXPLICIT" -eq 0 ]]; then
  PREFIX="/usr/local"
fi

# --- OS/arch detection ---
OS_RAW="$(uname -s)"
ARCH_RAW="$(uname -m)"

case "$OS_RAW" in
  Linux) OS="linux" ;;
  Darwin) OS="darwin" ;;
  *) fail "Unsupported OS: $OS_RAW"; exit 1 ;;
esac

case "$ARCH_RAW" in
  x86_64|amd64) ARCH="x86_64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *) fail "Unsupported architecture: $ARCH_RAW"; exit 1 ;;
esac

PLATFORM="${OS}-${ARCH}"
case "$PLATFORM" in
  linux-x86_64|darwin-arm64) ;;
  *) fail "Unsupported platform: $PLATFORM (supported: linux-x86_64, darwin-arm64)"; exit 1 ;;
esac

step "Installing rai + rai-mcp-pipeline $VERSION for $PLATFORM"

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

sha256_verify() {
  local file="$1" sumfile="$2"
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$(dirname "$file")" && sha256sum -c "$(basename "$sumfile")") >/dev/null 2>&1
  else
    (cd "$(dirname "$file")" && shasum -a 256 -c "$(basename "$sumfile")") >/dev/null 2>&1
  fi
}

# --- Phase 1: download + verify ALL binaries before installing ANY of them.
# This is what makes the install atomic — a failure here never reaches the
# filesystem mutation phase below, so rai and rai-mcp-pipeline can never end
# up at different versions.
for name in "${BINARIES[@]}"; do
  archive="${name}-${PLATFORM}.tar.gz"
  url="${BASE_URL}/${VERSION}/${archive}"
  dest="$TMP_ROOT/${archive}"

  step "Downloading $name ($archive)"
  if ! curl -fsSL -o "$dest" "$url"; then
    fail "Download failed: $url"
    fail "Aborting — nothing was installed or modified."
    exit 1
  fi
  if ! curl -fsSL -o "${dest}.sha256" "${url}.sha256"; then
    fail "Checksum download failed: ${url}.sha256"
    fail "Aborting — nothing was installed or modified."
    exit 1
  fi

  step "Verifying checksum for $name"
  if ! sha256_verify "$dest" "${dest}.sha256"; then
    fail "Checksum verification failed for $archive"
    fail "Aborting — nothing was installed or modified."
    exit 1
  fi
  ok "$name verified"
done

# --- Phase 2: extract + install. Only reached once every binary above has
# downloaded and verified successfully.
SHARE_ROOT="$PREFIX/share"
BIN_DIR="$PREFIX/bin"
mkdir -p "$SHARE_ROOT" "$BIN_DIR"

for name in "${BINARIES[@]}"; do
  archive="$TMP_ROOT/${name}-${PLATFORM}.tar.gz"
  target_dir="$SHARE_ROOT/$name"
  staging="$TMP_ROOT/staging-$name"

  mkdir -p "$staging"
  tar -xzf "$archive" -C "$staging"
  chmod +x "$staging/$name"

  # Atomic swap: rename is atomic within the same filesystem (PREFIX is a
  # single tree), so an install never leaves target_dir half-written.
  rm -rf "${target_dir}.old"
  [[ -d "$target_dir" ]] && mv "$target_dir" "${target_dir}.old"
  mv "$staging" "$target_dir"
  rm -rf "${target_dir}.old"

  ln -sf "$target_dir/$name" "$BIN_DIR/$name"
  ok "$name installed to $target_dir (symlinked from $BIN_DIR/$name)"
done

step "Done"
ok "rai + rai-mcp-pipeline $VERSION installed"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) printf "\n${C_CYAN}NOTE:${C_RESET} %s is not on your PATH. Add it to your shell profile:\n  export PATH=\"%s:\$PATH\"\n" "$BIN_DIR" "$BIN_DIR" ;;
esac
