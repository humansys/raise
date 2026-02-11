## Epic Scope: E16 Incremental Coherence

**Objective:** Prevent architecture documentation and graph drift through small-batch updates integrated into the story lifecycle, with full discovery as a validation safety net.

**Problem:**
- Architecture docs drift from code silently (PAT-196)
- Graph cache invalidates on schema changes (PAT-152)
- `rai discover drift` produces 383 warnings, near-zero actionable (SES-118)
- Full discovery workflow overwrites human validation — no incremental path
- No mechanism to detect *what changed* in the graph between builds

**In Scope:**
- Graph diffing: compare old vs new unified graph, emit structured change set
- Incremental doc regeneration: AI subagent updates affected docs from graph diff
- Story-close integration: trigger coherence check when structural changes detected
- Full discovery as validation: rerun discovery to verify incremental updates haven't drifted
- HITL gate: human reviews doc changes before commit

**Out of Scope:**
- Drift detector calibration (separate parking lot item — SES-118)
- Real-time/watch-mode detection
- Cross-project coherence
- Auto-commit without human review

**Stories (planned):**
- S16.1: Graph diffing capability
- S16.2: Doc regeneration subagent
- S16.3: Story-close integration
- S16.4: Discovery-as-validation flow

**Done when:**
- [ ] Graph diff produces structured change sets
- [ ] Affected docs regenerated from change sets via subagent
- [ ] Story-close triggers coherence check on structural changes
- [ ] Full discovery validates incremental state
- [ ] All stories complete with retrospectives
- [ ] Epic retrospective done
- [ ] Merged to v2
