# Retrospective: RAISE-202 — Roo Code agent support

## Summary
- **Story:** RAISE-202
- **Started:** 2026-02-19
- **Completed:** 2026-02-19
- **Estimated:** S (~45-60 min)
- **Actual:** ~20 min
- **Velocity:** 2.5x

## What Went Well

- ADR-032 architecture delivered on its promise — adding a new agent was pure data (1 YAML, 3 lines Python). Zero structural changes.
- TDD cycle caught the `instructions_file` assumption immediately. Wrong test → gemba (read init.py) → corrected in <2 min.
- Research session at session start gave us the full technical picture before writing a single line.
- `roo.yaml` + `agents.py` changes are minimal and self-documenting.

## What Could Improve

- The design should explicitly document that `instructions_file` is only generated with `--detect`. Saves the test correction cycle.

## Heutagogical Checkpoint

### What did you learn?
- `rai init --agent` scaffolds skills only. `instructions_file` generation is gated behind `--detect`. The distinction is intentional (brownfield detection drives instructions content), but not obvious from the YAML config alone.
- Roo Code's Agent Skills format is identical to Claude Code's. No transformation required — PAT-E-354 confirmed, 6 agents now.

### What would you change about the process?
- For agent addition stories: add explicit "read init.py scaffolding path" step in design to map what each flag generates. Prevents assumption errors in test RED phase.

### Are there improvements for the framework?
- PAT-E-354 says "4 of 5 IDEs" — now outdated (6 agents). Update pattern.
- Consider adding a note in `AgentConfig` docstring or agent YAMLs clarifying `instructions_file` generation behavior.

### What are you more capable of now?
- Adding new agents to RaiSE is fully internalized. Pattern: YAML + Literal + Enum + dict entry + 4 tests. Sub-30-min cycle confirmed.

## Improvements Applied

- PAT-E-372 added: `rai init --agent` vs `--detect` distinction for test writing
- Behavioral patterns reinforced: PAT-E-152, PAT-E-183, PAT-E-186, PAT-E-187, PAT-E-192

## Action Items

- [ ] Update PAT-E-354 ("4 of 5 IDEs") → "6 agents natively support Agent Skills"
- [ ] Consider docstring note in `AgentConfig.instructions_file` about `--detect` requirement
