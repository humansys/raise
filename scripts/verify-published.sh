#!/usr/bin/env bash
# verify-published.sh — Post-publish verification for GitHub Actions workflows.
# RAISE-17080: confirms that published artifacts are actually served.
#
# Usage:
#   verify-published.sh pypi <package> <version>
#   verify-published.sh release-assets <tag>
#
# Environment overrides (for testing):
#   PYPI_BASE_URL       — default https://pypi.org/pypi
#   GH_REPO             — default ${GITHUB_REPOSITORY:-humansys/raise}
#   VERIFY_DEADLINE_SECONDS — pypi: 300, release-assets: 60
#   VERIFY_INTERVAL_SECONDS — pypi: 15, release-assets: 10
#
# Exit codes: 0 = verified, 1 = not verified, 2 = usage error
set -euo pipefail

PREFIX="[verify-published]"

# --- Expected GitHub Release assets (17 total) ---
EXPECTED_ASSETS=(
    "rai-linux-x86_64.tar.gz"
    "rai-linux-x86_64.tar.gz.sha256"
    "rai-darwin-arm64.tar.gz"
    "rai-darwin-arm64.tar.gz.sha256"
    "rai-mcp-pipeline-linux-x86_64.tar.gz"
    "rai-mcp-pipeline-linux-x86_64.tar.gz.sha256"
    "rai-mcp-pipeline-darwin-arm64.tar.gz"
    "rai-mcp-pipeline-darwin-arm64.tar.gz.sha256"
    "rai-windows-x86_64.zip"
    "rai-windows-x86_64.zip.sha256"
    "rai-mcp-pipeline-windows-x86_64.zip"
    "rai-mcp-pipeline-windows-x86_64.zip.sha256"
    "rai-installer-windows-x86_64.exe"
    "rai-installer-windows-x86_64.exe.sha256"
    "version.json"
    "install.sh"
    "install.ps1"
)

# --- PyPI verification ---
verify_pypi() {
    local package="$1" version="$2"
    local base_url="${PYPI_BASE_URL:-https://pypi.org/pypi}"
    local deadline="${VERIFY_DEADLINE_SECONDS:-300}"
    local interval="${VERIFY_INTERVAL_SECONDS:-15}"
    local url="$base_url/$package/$version/json"

    echo "$PREFIX pypi: $package==$version via $url (deadline ${deadline}s, every ${interval}s)"

    local start elapsed attempt=0 http_code body_file last_status="unknown" last_reason=""
    start=$(date +%s)
    body_file=$(mktemp)
    trap 'rm -f "$body_file"' RETURN

    while true; do
        elapsed=$(( $(date +%s) - start ))
        if [[ $elapsed -ge $deadline ]]; then
            local reason_suffix=""
            [[ -n "$last_reason" ]] && reason_suffix=" Last check: $last_reason."
            echo "::error::$PREFIX pypi: $package==$version NOT served after ${deadline}s — last response HTTP $last_status from $url.${reason_suffix} The publish job reported success; check https://pypi.org/project/$package/#history and the Trusted Publisher configuration (dev/sops/release-common.md)."
            return 1
        fi

        attempt=$(( attempt + 1 ))
        http_code=$(curl -sS -o "$body_file" -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        last_status="$http_code"

        if [[ "$http_code" != "200" ]]; then
            echo "$PREFIX pypi: attempt $attempt — HTTP $http_code, not served yet"
            sleep "$interval"
            continue
        fi

        # Check for wheel and sdist, and that none are yanked
        local has_wheel has_sdist yanked_names
        has_wheel=$(jq '[.urls[] | select(.packagetype == "bdist_wheel" and .yanked != true)] | length' "$body_file" 2>/dev/null || echo "0")
        has_sdist=$(jq '[.urls[] | select(.packagetype == "sdist" and .yanked != true)] | length' "$body_file" 2>/dev/null || echo "0")
        yanked_names=$(jq -r '[.urls[] | select(.yanked == true) | .filename] | join(", ")' "$body_file" 2>/dev/null || echo "")

        if [[ -n "$yanked_names" ]]; then
            last_reason="yanked files: $yanked_names"
            echo "$PREFIX pypi: attempt $attempt — HTTP 200, but yanked files: $yanked_names"
            # Re-poll in case CDN served a stale version document
            sleep "$interval"
            continue
        fi

        if [[ "$has_wheel" -eq 0 ]] || [[ "$has_sdist" -eq 0 ]]; then
            local found_types missing_types=""
            found_types=$(jq -r '[.urls[] | "\(.filename) (\(.packagetype))"] | join(", ")' "$body_file" 2>/dev/null || echo "none")
            [[ "$has_wheel" -eq 0 ]] && missing_types="bdist_wheel"
            [[ "$has_sdist" -eq 0 ]] && { [[ -n "$missing_types" ]] && missing_types="$missing_types, sdist" || missing_types="sdist"; }
            last_reason="found: $found_types; missing: $missing_types"
            echo "$PREFIX pypi: attempt $attempt — HTTP 200, found: $found_types; missing: $missing_types"
            sleep "$interval"
            continue
        fi

        # All good
        local file_list
        file_list=$(jq -r '[.urls[] | "\(.filename) (\(.packagetype))"] | join(", ")' "$body_file" 2>/dev/null || echo "")
        echo "$PREFIX pypi: attempt $attempt — HTTP 200, files: $file_list, yanked: none"
        echo "$PREFIX pypi: VERIFIED $package==$version (wheel + sdist)"
        return 0
    done
}

# --- GitHub Release assets verification ---
verify_release_assets() {
    local tag="$1"
    local repo="${GH_REPO:-${GITHUB_REPOSITORY:-humansys/raise}}"
    local deadline="${VERIFY_DEADLINE_SECONDS:-60}"
    local interval="${VERIFY_INTERVAL_SECONDS:-10}"

    echo "$PREFIX release-assets: $repo release $tag (deadline ${deadline}s, every ${interval}s)"

    local start elapsed attempt=0
    start=$(date +%s)

    while true; do
        elapsed=$(( $(date +%s) - start ))
        if [[ $elapsed -ge $deadline ]]; then
            echo "::error::$PREFIX release-assets: no GitHub Release for tag $tag in $repo after ${deadline}s (gh release view exit 1). The release job must create it before this job runs."
            return 1
        fi

        attempt=$(( attempt + 1 ))
        local gh_output gh_rc=0
        gh_output=$(gh release view "$tag" --repo "$repo" --json isDraft,assets \
            --jq '{draft: .isDraft, assets: [.assets[] | {name, state, size}]}' 2>/dev/null) || gh_rc=$?

        if [[ $gh_rc -ne 0 ]]; then
            echo "$PREFIX release-assets: attempt $attempt — gh release view failed (exit $gh_rc), retrying"
            sleep "$interval"
            continue
        fi

        # Check draft
        local is_draft
        is_draft=$(echo "$gh_output" | jq -r '.draft' 2>/dev/null || echo "false")
        if [[ "$is_draft" == "true" ]]; then
            echo "::error::$PREFIX release-assets: $tag exists but is a draft — not published."
            return 1
        fi

        # Check all 17 expected assets
        local missing_details="" missing_count=0
        local expected_count=${#EXPECTED_ASSETS[@]}
        for asset_name in "${EXPECTED_ASSETS[@]}"; do
            local asset_info
            asset_info=$(echo "$gh_output" | jq -r --arg name "$asset_name" \
                '.assets[] | select(.name == $name) | "\(.state) \(.size)"' 2>/dev/null || echo "")

            if [[ -z "$asset_info" ]]; then
                missing_details+="$asset_name (absent), "
                missing_count=$(( missing_count + 1 ))
            else
                local state size
                state=$(echo "$asset_info" | awk '{print $1}')
                size=$(echo "$asset_info" | awk '{print $2}')
                if [[ "$state" != "uploaded" ]] || [[ "$size" -le 0 ]]; then
                    missing_details+="$asset_name (state=$state, size=$size), "
                    missing_count=$(( missing_count + 1 ))
                fi
            fi
        done

        if [[ $missing_count -gt 0 ]]; then
            # Remove trailing ", "
            missing_details="${missing_details%, }"
            echo "::error::$PREFIX release-assets: $tag is missing $missing_count of $expected_count expected assets — $missing_details. softprops/action-gh-release ignores unmatched globs (fail_on_unmatched_files=false); check the build-* artifacts and the release job's download-artifact step."
            return 1
        fi

        local uploaded_count
        uploaded_count=$(echo "$gh_output" | jq '[.assets[] | select(.state == "uploaded" and .size > 0)] | length' 2>/dev/null || echo "0")
        echo "$PREFIX release-assets: $expected_count expected, $uploaded_count uploaded, 0 missing"
        echo "$PREFIX release-assets: VERIFIED $tag"
        return 0
    done
}

# --- Main dispatch ---
MODE="${1:-}"
case "$MODE" in
    pypi)
        [[ $# -eq 3 ]] || { echo "Usage: $0 pypi <package> <version>"; exit 2; }
        verify_pypi "$2" "$3"
        ;;
    release-assets)
        [[ $# -eq 2 ]] || { echo "Usage: $0 release-assets <tag>"; exit 2; }
        verify_release_assets "$2"
        ;;
    *)
        echo "Usage: $0 {pypi <package> <version> | release-assets <tag>}"
        exit 2
        ;;
esac
