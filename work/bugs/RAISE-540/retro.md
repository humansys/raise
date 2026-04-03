## Retrospective: RAISE-540

### Summary
- Root cause: Copy-paste (S3923) and ad-hoc regex without explicit grouping (S5850) — both accumulated because no SAST gate existed in CI during early development
- Fix approach: 1-line fixes per sub-bug + regression tests. Sub-bugs: RAISE-534, 535, 536, 537
- Classification: Logic/S2-Medium/Code/Incorrect

### Verification
- RAISE-534 fix verified: `scanner.py:1561` — else branch changed from `**/{entry}/**` to `{entry}/**` (commit 458e0e3b). 3 regression tests added.
- RAISE-536 fix verified: `changelog.py:18` — explicit `(?:...)` grouping in regex lookahead (commit f737be16). 2 regression tests added.
- RAISE-537 fix verified: `adr.py:81` — same pattern as 536 (commit f8458cf4).
- All fixes are correct, minimal, and tested.

### Process Improvement
**Prevention:** SAST gate (SonarQube) in CI before merge catches dead code and regex ambiguity before accumulation. This was added after this bug batch — the gate now exists.
**Pattern:** Logic + Code + Incorrect → static analysis detectable bugs that accumulate silently when no SAST gate exists. The fix is always trivial; the cost is in detection latency.

### Heutagogical Checkpoint
1. Learned: These 4 bugs are the same class — "things a linter catches that humans don't notice." The ROI of SAST is in catching the boring stuff reliably.
2. Process change: SAST gate was added to CI after this batch. Correct response.
3. Framework improvement: None needed — the bug workflow correctly separates these as Logic/Code bugs.
4. Capability gained: Confidence that umbrella tickets with sub-bugs don't need re-analysis — verify the sub-bug artifacts exist and are correct.

### Patterns
- Added: PAT-F-046
- Reinforced: none evaluated
