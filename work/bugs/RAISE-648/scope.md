WHAT:      graph build crashes with ValueError on duplicate node IDs instead of warn+skip
WHEN:      Any graph build when epic directories have naming collisions (e.g. e14-rai-distribution + e14-skill-product-evaluation → both epic-e14)
WHERE:     context/builder.py:102 — raises ValueError on duplicate
EXPECTED:  Default: warn+skip duplicates. --strict for CI.
Done when: graph build completes with duplicate warnings, --strict available

TRIAGE:
  Bug Type:    Functional
  Severity:    S1-High
  Origin:      Design
  Qualifier:   Incorrect

STATUS: Still valid — confirmed crash on current codebase. epic-e14 collision.
NOTE: Related to RAISE-1128 (epic naming collisions). RAISE-648 is the crash behavior, RAISE-1128 is the naming root cause.
