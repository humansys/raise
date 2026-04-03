WHAT:      CLI crashes with UnicodeEncodeError when printing ✓, ✗, ⚠ symbols
WHEN:      Windows terminal with CP1252 codepage (legacy, non-UTF-8)
WHERE:     68 literal occurrences across 16 files in src/raise_cli/
EXPECTED:  CLI renders ASCII fallbacks ([ok], [x], [!]) on non-Unicode terminals
Done when: `rai graph build` (and all other commands) complete without UnicodeEncodeError on CP1252 terminals

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
