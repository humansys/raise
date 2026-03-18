## Root Cause

Unicode symbols (✓ U+2713, ✗ U+2717, ⚠ U+26A0) are hardcoded as Python string
literals in 16 source files. When Rich renders these via stdout on a Windows
terminal with CP1252 codepage, Python raises UnicodeEncodeError because CP1252
has no mapping for these code points.

## 5 Whys

Problem: UnicodeEncodeError on Windows
Why1: CLI writes Unicode chars to stdout → stdout uses CP1252 → no mapping
Why2: Symbols are literal Unicode strings — no encoding check before output
Why3: No central symbols abstraction — each file hardcodes symbols independently
Why4: No Windows CI environment to catch the regression
Root cause: Unicode symbols hardcoded at 68 call sites with no terminal capability check

## Countermeasure

Create `src/raise_cli/output/symbols.py` exposing:
- `get_symbols(encoding)` — returns (CHECK, CROSS, WARN) based on encoding
- Module-level `CHECK`, `CROSS`, `WARN` — computed from current `sys.stdout.encoding`

Replace all 68 literal occurrences with imports from the symbols module.
ASCII fallbacks: CHECK=[ok], CROSS=[x], WARN=[!]
