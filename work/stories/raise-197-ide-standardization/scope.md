# Story Scope: RAISE-197

> **Standardize IDE abstraction layer to design decisions**
> **Epic:** RAISE-144 (Engineering Health)
> **Branch:** Working on `epic/raise-168` (post-merge of RAISE-128)
> **Size:** S

---

## In Scope

- Rename `claudemd.py` → `instructions.py`, `ClaudeMdGenerator` → `IdeInstructionsGenerator`
- Update all imports and references across codebase
- Align instructions generator with ADR-012 (projection from `.raise/` canonical source)
- Evaluate `"gemini"` as IdeType (clarify relationship with Antigravity)
- Remove large binary (PDF) and files with special characters from `dev/`
- Update tests to reflect renames

## Out of Scope

- Full ADR-012 generator implementation (that's a separate M-sized story)
- Adding new IDE types beyond evaluation
- Changing Fernando's `IdeConfig` architecture (it's solid)
- Modifying `scaffold_workflows()` logic

## Done Criteria

- [ ] No Claude-specific naming in multi-IDE code paths
- [ ] Generator function signature accepts `ide_config` and routes correctly
- [ ] All existing tests pass with updated imports
- [ ] Quality gates pass (ruff, pyright)
- [ ] Binary artifacts removed from repo history consideration (`.gitignore` or delete)
