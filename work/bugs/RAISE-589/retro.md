## Retrospective: RAISE-589

### Summary
- Root cause: RAISE-536/537 fix was incomplete — added grouping but left \Z outside the group. Second pass needed to move \Z inside.
- Fix approach: Restructured regex lookahead to `(?=(?:^## \[|\Z))` — both alternatives inside one group (commits 7e8e1a5f, 52ca55d0)
- Classification: Logic/S3-Low/Code/Incorrect

### Verification
- adr.py:81 — `(?=(?:^##\s)|\Z)` → `(?=(?:^##\s|\Z))` — \Z now inside group
- changelog.py:18,47 — same pattern applied to both regexes, NOSONAR comments removed (no longer needed)
- Behavior unchanged — regex semantics identical in Python, but now unambiguous to static analyzers

### Process Improvement
**Prevention:** When fixing regex ambiguity, verify ALL alternatives are inside the group — partial grouping creates a second bug. Test with the Sonar rule specifically, not just behavior tests.
**Pattern:** Logic + Code + Incorrect → incomplete fix creates follow-up bug. The fix-verify cycle needs to include the SAST check that detected the original issue.

### Heutagogical Checkpoint
1. Learned: RAISE-536/537 → RAISE-589 is a fix-quality bug. The first fix addressed the symptom (add grouping) but not fully (left \Z outside). Running Sonar after the fix would have caught it immediately.
2. Process change: After fixing a SAST finding, re-run the specific rule to confirm it's actually resolved before closing.
3. Framework improvement: /rai-bugfix Step 5 should include "re-run the detection tool" as explicit verification.
4. Capability gained: Regex precedence in lookaheads is subtle — `(?=A|B)` vs `(?=(?:A|B))` are semantically different in some engines.

### Patterns
- Added: PAT-F-047 (see below)
- Reinforced: none evaluated
