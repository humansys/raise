"""Session protocol module.

Manages session state persistence and context bundle assembly
for deterministic session continuity.
"""

# --- Bundle ---
from raise_cli.session.bundle import assemble_context_bundle, assemble_sections

# --- Close ---
from raise_cli.session.close import (
    CloseInput,
    CoachingInput,
    CorrectionCloseEntry,
    PatternCloseEntry,
    load_state_file,
    process_session_close,
)

# --- Context ---
from raise_cli.session.context_backend import get_session_context_backend
from raise_cli.session.context_env import write_context_env

# --- Derive ---
from raise_cli.session.derive import GitStateDeriver

# --- Doctor ---
from raise_cli.session.doctor import SessionDoctor, format_findings

# --- Identity & Index ---
from raise_cli.session.identity import generate_session_id
from raise_cli.session.index import (
    ActiveSessionPointer,
    SessionIndexEntry,
    clear_active_session,
    count_missing_prefix_sessions,
    find_last_closed_in_scope,
    read_active_session,
    read_all_active_sessions,
    read_session_entries,
    write_active_session,
    write_session_entry,
)

# --- Journal ---
from raise_cli.session.journal import (
    append_journal_entry,
    format_journal_compact,
    read_journal,
)

# --- Ledger ---
from raise_cli.session.ledger import read_entries, render_sections, upsert_entry

# --- Measure ---
from raise_cli.session.measure import measure_bundle

# --- Monitor ---
from raise_cli.session.monitor import LocalWorkstreamMonitor

# --- Prefix ---
from raise_cli.session.prefix import PrefixRegistry

# --- Protocols ---
# --- Resolver ---
from raise_cli.session.resolver import resolve_session_id, resolve_session_id_optional

# --- State ---
from raise_cli.session.state import (
    cleanup_session_dir,
    load_session_state,
    migrate_flat_to_session,
)

__all__ = [
    # Bundle
    "assemble_context_bundle",
    "assemble_sections",
    # Close
    "CloseInput",
    "CoachingInput",
    "CorrectionCloseEntry",
    "PatternCloseEntry",
    "load_state_file",
    "process_session_close",
    # Context
    "get_session_context_backend",
    "write_context_env",
    # Derive
    "GitStateDeriver",
    # Doctor
    "SessionDoctor",
    "format_findings",
    # Identity & Index
    "generate_session_id",
    "ActiveSessionPointer",
    "SessionIndexEntry",
    "clear_active_session",
    "count_missing_prefix_sessions",
    "find_last_closed_in_scope",
    "read_active_session",
    "read_all_active_sessions",
    "read_session_entries",
    "write_active_session",
    "write_session_entry",
    # Journal
    "append_journal_entry",
    "format_journal_compact",
    "read_journal",
    # Ledger
    "read_entries",
    "render_sections",
    "upsert_entry",
    # Measure
    "measure_bundle",
    # Monitor
    "LocalWorkstreamMonitor",
    # Prefix
    "PrefixRegistry",
    # Resolver
    "resolve_session_id",
    "resolve_session_id_optional",
    # State
    "cleanup_session_dir",
    "load_session_state",
    "migrate_flat_to_session",
]
