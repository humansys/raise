"""Test that package __init__.py files re-export key symbols."""

from __future__ import annotations


def test_schemas_reexports_journal_entry() -> None:
    from raise_cli.schemas import JournalEntry

    assert JournalEntry is not None


def test_schemas_reexports_journal_entry_type() -> None:
    from raise_cli.schemas import JournalEntryType

    assert JournalEntryType is not None


def test_schemas_reexports_session_state() -> None:
    from raise_cli.schemas import SessionState

    assert SessionState is not None


def test_schemas_reexports_current_work() -> None:
    from raise_cli.schemas import CurrentWork

    assert CurrentWork is not None


def test_backlog_reexports_sync_result() -> None:
    from raise_cli.backlog import SyncResult

    assert SyncResult is not None


def test_backlog_reexports_sync_backlog() -> None:
    from raise_cli.backlog import sync_backlog

    assert sync_backlog is not None


def test_tier_reexports_tier_context() -> None:
    from raise_cli.tier import TierContext

    assert TierContext is not None


def test_tier_reexports_tier_level() -> None:
    from raise_cli.tier import TierLevel

    assert TierLevel is not None


def test_tier_reexports_capability() -> None:
    from raise_cli.tier import Capability

    assert Capability is not None
