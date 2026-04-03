WHAT:      Epic directory naming collisions — e14-rai-distribution + e14-skill-product-evaluation both normalize to epic-e14
WHEN:      graph build with multiple epic directories sharing the same number
WHERE:     epic.py:85 — int() normalizer strips leading zeros and ignores slug
EXPECTED:  Node IDs include slug or use full directory name to avoid collisions
Done when: No duplicate node IDs from epic directories with same number

TRIAGE:
  Bug Type:    Data
  Severity:    S2-Medium
  Origin:      Design
  Qualifier:   Incorrect

STATUS: Still valid — causes RAISE-648 crash. Root cause of the naming collision.
