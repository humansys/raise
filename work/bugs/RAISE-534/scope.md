# RAISE-534: Identical if-branch bodies in discovery/scanner.py

WHAT:      `_parse_gitignore_patterns()` has identical code in both if/else branches (line 1561-1564)
WHEN:      When parsing .gitignore entries that contain a `/` (path-relative patterns)
WHERE:     src/raise_cli/discovery/scanner.py:1561-1564
EXPECTED:  Entries with `/` should be treated as path-relative (no `**/` prefix); bare names should match anywhere (`**/name/**`)
Done when: Both branches produce distinct glob patterns matching gitignore semantics
