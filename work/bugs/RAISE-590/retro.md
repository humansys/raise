## Retrospective: RAISE-590

### Summary
- Root cause: Copy-paste — both if/else branches had identical code. In scanner.py the branches should have differed (bare vs path patterns). In python.py the condition was entirely dead.
- Fix approach: scanner.py — differentiated the branches (RAISE-534, commit 458e0e3b). python.py — collapsed to unconditional (RAISE-535, commit 4f5a1f65).
- Classification: Logic/S2-Medium/Code/Extraneous

### Verification
- RAISE-534: scanner.py `_read_gitignore` — else branch changed from `**/{entry}/**` to `{entry}/**`. 3 tests added.
- RAISE-535: python.py — collapsed 6-line if/else to 2 lines. 1 regression test added.
- Both fixes correct and minimal.

### Process Improvement
**Prevention:** Same as RAISE-540 — SAST gate catches dead code. Additionally, code review should flag if/else blocks where both branches are visually identical.
**Pattern:** Logic + Code + Extraneous → dead conditional from copy-paste. The if/else existed because the developer intended different behavior but forgot to implement the difference.

### Heutagogical Checkpoint
1. Learned: Two different root causes under the same Sonar rule: scanner.py was a real bug (wrong behavior), python.py was dead code (no behavior difference). Classification matters — Extraneous (python.py) vs Incorrect (scanner.py).
2. Process change: Covered by SAST gate.
3. Framework improvement: None.
4. Capability gained: Distinguishing "dead code" (safe to remove) from "wrong code" (needs fix) under the same S3923 rule.

### Patterns
- Added: none (covered by PAT-F-046)
- Reinforced: none evaluated
