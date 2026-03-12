# RAISE-541: Sonar Code Smells — Mechanical Fixes

## Scope

WHAT:      SonarQube reports 8 rule violations across the codebase (S1192, S1172, S5713,
           S6019, S125, S7503, S5754, S7632) — all mechanical, no logic change.
WHEN:      Present in current codebase on `dev`. Detected via local SonarQube scan.
WHERE:     ~60 instances across src/raise_cli/ and src/rai_pro/
EXPECTED:  Zero violations for these 8 rules in SonarQube analysis.
Done when: `sonar list issues` returns no rows for rules S1192, S1172, S5713, S6019,
           S125, S7503, S5754, S7632. All gates pass (pytest, ruff, pyright).

## Rules in Scope

| Rule | Severity | Count | Nature |
|------|----------|-------|--------|
| S1192 | CRITICAL | ~28 | Duplicate string literals → extract constant |
| S1172 | MAJOR | ~13 | Unused function parameters → prefix `_` or remove |
| S5713 | MINOR | ~9 | Redundant exception in `except (A, B)` where B extends A |
| S6019 | MAJOR | ~7 | Reluctant regex quantifier `*?` or `+?` that matches 0/1 only |
| S125 | MAJOR | 1 | Commented-out code block |
| S7503 | MINOR | 1 | `async def` with no `await` → remove `async` |
| S5754 | CRITICAL | 1 | Silenced exception should be reraised |
| S7632 | MAJOR | 1 | Malformed `# type: ignore` syntax |

## Out of Scope

- S3776 (cognitive complexity) — separate story, requires refactoring
- S3923 / S5850 — tracked in RAISE-540 (bugs, not smells)
- S6395 / S1700 / S6353 — not listed in RAISE-541
