# RAISE-505: Orphan SES-025 from flat-to-directory migration

WHAT:      migrate_flat_to_session moves flat state into the NEW session's directory
           instead of the PREVIOUS session's directory. Creates phantom session dir.
WHEN:      First session start after migration to per-session layout.
WHERE:     src/raise_cli/session/state.py:migrate_flat_to_session (line 67)
           src/raise_cli/cli/commands/session.py:186 (caller passes new session_id)
EXPECTED:  Flat state migrated to directory matching last_session.id from the state file.
Done when: 1. Migration reads last_session.id from flat state and uses it as target
           2. No orphan directories created
           3. Regression test covers migration target ID
