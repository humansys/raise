# RAISE-537: Regex operator precedence ambiguous in adr.py

WHAT:      Regex alternation `^##\s|\Z` without explicit grouping in lookahead (line 81)
WHEN:      When extracting Decision section from ADR content
WHERE:     src/raise_cli/governance/parsers/adr.py:81
EXPECTED:  Explicit non-capturing group around alternation
Done when: `(?=(?:^##\s)|\Z)` with regression test
