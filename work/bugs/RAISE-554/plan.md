## Tasks

### T1 [RED] — Regression tests for symbols module
File: tests/output/test_symbols.py
- test_unicode_symbols_on_utf8_terminal
- test_ascii_fallbacks_on_cp1252_terminal
- test_ascii_fallbacks_are_encodable_in_cp1252
- test_module_constants_reflect_runtime_encoding
Commit: test(RAISE-554): regression — symbols crash on CP1252 [RED]

### T2 [GREEN] — Create symbols module
File: src/raise_cli/output/symbols.py
- get_symbols(encoding=None) -> tuple[str, str, str]
- Module-level CHECK, CROSS, WARN using sys.stdout.encoding
Commit: fix(RAISE-554): add symbols module with CP1252 fallbacks [GREEN]

### T3 — Update output/console.py
Replace literal ✓ and ⚠ with CHECK/WARN from symbols module
Commit: fix(RAISE-554): use symbols constants in OutputConsole

### T4 — Update CLI commands (graph, gate, release, session, signal, adapters, artifact, init, pattern, skill_set)
Replace all literal occurrences in src/raise_cli/cli/commands/
Commit: fix(RAISE-554): replace Unicode literals in cli/commands/

### T5 — Update output formatters + other files (formatters/, session/bundle.py, onboarding/, governance/)
Replace remaining occurrences
Commit: fix(RAISE-554): replace Unicode literals in remaining files

## Verification
.venv/bin/pytest tests/output/test_symbols.py -v
.venv/bin/ruff check src/ tests/
.venv/bin/pyright
