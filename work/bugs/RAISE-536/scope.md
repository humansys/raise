# RAISE-536: Regex operator precedence ambiguous in changelog.py

WHAT:      Regex alternation `^## \[|\Z` without explicit grouping in lookahead (line 18)
WHEN:      When parsing [Unreleased] section in changelog
WHERE:     src/raise_cli/publish/changelog.py:18
EXPECTED:  Regex groups are explicit so precedence is unambiguous
Done when: Alternation in lookahead uses explicit non-capturing group `(?:^## \[)|\Z`
