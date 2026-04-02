## Analysis: RAISE-735

### Root Cause
When the CLI entry point was renamed from `raise` to `rai`, string literals
(docstrings, user-facing messages, examples, hints) were not updated consistently.
The code logic is correct — only human-readable strings are stale.

### Scope (larger than ticket)
Ticket listed 8 files. Actual scan found ~22 files across 3 areas:

**Source (9 files):** init.py, session.py, memory/__init__.py, profile.py,
info.py, discover.py, rai_base/__init__.py, onboarding/governance.py,
onboarding/bootstrap.py

**Framework docs (4 files):** glossary.md, compliance.md, philosophy.md,
greenfield.md

**Tests (9 files):** docstrings and fixtures in test_exceptions, test_models,
test_graph_viz, test_profile, test_init, test_graph_build_diff, test_memory,
test_graph_context, test_session

### Fix Approach
Search-and-replace `raise <command>` → `rai <command>` in all string contexts.
Preserve: Python `raise` keyword, `.raise/` paths, `raise_cli`/`raise-cli` names.

Note: Some glossary entries reference legacy commands (raise pull, raise kata,
raise validate, raise audit, raise parse) that have no direct `rai` equivalent.
These still get the entry point rename since the entry point IS `rai`.
