## Retrospective: RAISE-635

### Summary
- Root cause: Close skills referenced CLAUDE.local.md for context updates — an undocumented file. Context capture is already handled by rai session close (next_session_prompt) and rai signal emit-work.
- Fix approach: Remove CLAUDE.local.md references from both close skills (commit d6fdf09d)
- Classification: Configuration/S3-Low/Design/Extraneous

### Verification
- rai-story-close/SKILL.md and rai-epic-close/SKILL.md: CLAUDE.local.md references removed
- Context continuity still works via session close pipeline (verified today — next_session_prompt loaded correctly)

### Process Improvement
**Prevention:** Skills should only reference documented, canonical CLI mechanisms for state persistence. Ad-hoc file references create undocumented dependencies.
**Pattern:** Configuration + Design + Extraneous → skill references undocumented file. The fix is removal, not documentation — if the mechanism isn't canonical, don't use it.

### Heutagogical Checkpoint
1. Learned: CLAUDE.local.md was an early experiment that got baked into skills before the session close pipeline existed. Once session close handled context, the old mechanism became dead weight.
2. Process change: When adding a new state mechanism (like session close), audit existing skills for references to the mechanism it replaces.
3. Framework improvement: None — the skill update process caught this.
4. Capability gained: Recognizing "extraneous" bugs — things that should be removed, not fixed.

### Patterns
- Added: none (too specific)
- Reinforced: none evaluated
