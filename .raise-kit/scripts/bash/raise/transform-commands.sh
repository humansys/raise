#!/usr/bin/env bash
#
# transform-commands.sh
#
# Transforms command files from flat structure (.claude/commands/)
# to organized structure (.specify-raise/commands/) with:
# - File renaming according to FILE_MAP
# - Internal reference updates according to REF_MAP
#
# Usage: ./transform-commands.sh
#
# Requirements: Bash 4.0+ (for associative arrays)
#
# Author: RaiSE Framework
# Date: 2026-01-20
# Version: 1.0.0

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

# Get script directory for relative path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# Project directory (defaults to speckit if not provided)
PROJECT_NAME="${1:-speckit}"
PROJECT_DIR="${REPO_ROOT}/${PROJECT_NAME}"

# Source and destination directories
# Source and destination directories
SRC_DIR="${PROJECT_DIR}/.claude/commands"
# Destination for transformed commands depends on where the agent expects them.
# The user wants them in ".claude/commands" (or the same as source).
# But since we are transforming them, we should output them to the agent's command directory.
# Assuming standard .claude/commands for now.
COMMANDS_DEST="${PROJECT_DIR}/.claude/commands" 
ASSETS_ROOT="${PROJECT_DIR}/.specify"
# DEST_DIR is legacy variable used in transform_file, update it:
DEST_DIR="$COMMANDS_DEST"

# File mapping: source filename -> destination path (relative to DEST_DIR)
declare -A FILE_MAP=(
    ["speckit.specify.md"]="03-feature/speckit.1.specify.md"
    ["speckit.clarify.md"]="03-feature/speckit.2.clarify.md"
    ["speckit.plan.md"]="03-feature/speckit.3.plan.md"
    ["speckit.tasks.md"]="03-feature/speckit.4.tasks.md"
    ["speckit.analyze.md"]="03-feature/speckit.5.analyze.md"
    ["speckit.implement.md"]="03-feature/speckit.6.implement.md"
    ["speckit.checklist.md"]="03-feature/speckit.util.checklist.md"
    ["speckit.taskstoissues.md"]="03-feature/speckit.util.issues.md"
    ["speckit.constitution.md"]="01-onboarding/speckit.2.constitution.md"
)

# Reference mapping: old reference -> new reference (for agent: field in YAML)
declare -A REF_MAP=(
    ["speckit.specify"]="speckit.1.specify"
    ["speckit.clarify"]="speckit.2.clarify"
    ["speckit.plan"]="speckit.3.plan"
    ["speckit.tasks"]="speckit.4.tasks"
    ["speckit.analyze"]="speckit.5.analyze"
    ["speckit.implement"]="speckit.6.implement"
    ["speckit.checklist"]="speckit.util.checklist"
    ["speckit.taskstoissues"]="speckit.util.issues"
    ["speckit.constitution"]="speckit.2.constitution"
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Print error message to stderr and exit
error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Print warning message to stderr (does not exit)
warn() {
    echo "WARNING: $1" >&2
}

# Print info message to stdout
info() {
    echo "$1"
}

# =============================================================================
# COUNTERS
# =============================================================================

SUCCESS_COUNT=0
ERROR_COUNT=0
SKIPPED_COUNT=0
declare -a ERROR_FILES=()

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

# Create destination subdirectories
create_directories() {
    info "Creating destination directories..."
    mkdir -p "${DEST_DIR}/01-onboarding"
    mkdir -p "${DEST_DIR}/03-feature"
}

# Transform a single file: apply reference replacements and copy to destination
# Arguments: $1 = source filename (without path), $2 = destination path (relative to DEST_DIR)
transform_file() {
    local src_file="$1"
    local dest_path="$2"
    local src_full="${SRC_DIR}/${src_file}"
    local dest_full="${DEST_DIR}/${dest_path}"

    # Check if source file exists
    if [[ ! -f "$src_full" ]]; then
        warn "Source file not found: $src_file"
        ERROR_FILES+=("$src_file: source not found")
        ((ERROR_COUNT++)) || true
        return 1
    fi

    # Read file content
    local content
    content=$(<"$src_full")

    # Apply reference replacements
    for old_ref in "${!REF_MAP[@]}"; do
        local new_ref="${REF_MAP[$old_ref]}"
        # Global replacement of the reference string
        content="${content//${old_ref}/${new_ref}}"
    done

    # Write to destination
    echo "$content" > "$dest_full"

    # Remove source file
    rm "$src_full"

    info "  Moved: $src_file -> $dest_path"
    ((SUCCESS_COUNT++)) || true
    return 0
}

# Main transformation loop
run_transformation() {
    info "Starting transformation..."
    info "Source: $SRC_DIR"
    info "Destination: $DEST_DIR"
    info ""

    create_directories

    for src_file in "${!FILE_MAP[@]}"; do
        local dest_path="${FILE_MAP[$src_file]}"
        transform_file "$src_file" "$dest_path" || true
    done
}

# Copy base assets from .raise-kit to .specify
copy_base_assets() {
    info "Copying base assets from .raise-kit..."
    local base_src="${REPO_ROOT}/.raise-kit"
    
    if [[ ! -d "$base_src" ]]; then
        error "Base .raise-kit directory not found at $base_src"
    fi

    # List of directories to copy (excluding scripts which is handled separately)
    # Commands are verified separately. Let's merge raise-kit commands into COMMANDS_DEST.
    # But wait, raise-kit commands structure might differ from transformed structure?
    # Raise-kit commands are already organized (01-onboarding, etc).
    # Transformed commands are being organized into the same structure.
    # So both should go to COMMANDS_DEST.
    
    # 1. Copy base commands from .raise-kit/commands to COMMANDS_DEST
    local cmd_src="${base_src}/commands"
    if [[ -d "$cmd_src" ]]; then
        info "  Copying commands base..."
        mkdir -p "$COMMANDS_DEST"
        cp -r "$cmd_src"/* "$COMMANDS_DEST"/ 2>/dev/null || true
    fi

    # 2. Copy gates and templates to .specify
    local assets=("gates" "templates")
    for dir in "${assets[@]}"; do
        local src="${base_src}/${dir}"
        local dest="${ASSETS_ROOT}/${dir}"
        
        # Ensure destination parent exists
        mkdir -p "$(dirname "$dest")"

        if [[ -d "$src" ]]; then
            info "  Copying $dir..."
            cp -r "$src"/* "$dest"/ 2>/dev/null || true
            ((SUCCESS_COUNT++)) || true
        else
            warn "  Base directory not found: $src"
        fi
    done

    # 3. Handle scripts specifically: Copy only bash, exclude powershell
    local scripts_src="${base_src}/scripts"
    local scripts_dest="${ASSETS_ROOT}/scripts"
    
    if [[ -d "$scripts_src" ]]; then
        info "  Copying scripts (Bash only)..."
        mkdir -p "$scripts_dest"
        
        # Copy bash folder
        if [[ -d "${scripts_src}/bash" ]]; then
             mkdir -p "${scripts_dest}/bash"
             cp -r "${scripts_src}/bash"/* "${scripts_dest}/bash"/ 2>/dev/null || true
        fi
        
        # Copy direct files
        find "$scripts_src" -maxdepth 1 -type f -exec cp {} "$scripts_dest" \;
    fi
    info ""
}

# Validate source directory
validate_source() {
    info "Validating source directory..."
    if [[ ! -d "$SRC_DIR" ]]; then
        error "Source directory not found: $SRC_DIR"
    fi

    # Check for empty directory (no .md files)
    # Use nullglob to handle case with no matches
    shopt -s nullglob
    local files=("${SRC_DIR}"/*.md)
    shopt -u nullglob

    if [[ ${#files[@]} -eq 0 ]]; then
        warn "No .md files found in source directory: $SRC_DIR"
        exit 0
    fi
}

# Check for files in source that are not in FILE_MAP
check_unrecognized_files() {
    info "Checking for unrecognized files..."
    shopt -s nullglob
    local files=("${SRC_DIR}"/*.md)
    shopt -u nullglob

    for file_path in "${files[@]}"; do
        local filename
        filename=$(basename "$file_path")
        if [[ -z "${FILE_MAP[$filename]-}" ]]; then
            warn "Unrecognized file (will be ignored): $filename"
        fi
    done
    info ""
}

# Print execution summary
print_summary() {
    info "========================================"
    info "TRANSFORMATION SUMMARY"
    info "========================================"
    info "Successful: $SUCCESS_COUNT"
    info "Skipped:    $SKIPPED_COUNT"
    info "Failed:     $ERROR_COUNT"
    
    if [[ ${#ERROR_FILES[@]} -gt 0 ]]; then
        info ""
        info "Errors:"
        for err in "${ERROR_FILES[@]}"; do
            echo "  - $err"
        done
        exit 1
    fi
    
    info ""
    if [[ $ERROR_COUNT -eq 0 ]]; then
        info "SUCCESS: All processed files transformed correctly."
        exit 0
    else
        info "WARNING: Completed with errors."
        exit 1
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    info "Transform Commands Script v1.0.0"
    info "========================================"
    
    validate_source
    check_unrecognized_files
    copy_base_assets
    run_transformation
    print_summary
}

# Execute main
main "$@"

