# Retrospective: S7.2 — /project-create skill

## Summary
- **Feature:** S7.2 `/project-create` skill (greenfield onboarding)
- **Started:** 2026-02-08
- **Completed:** 2026-02-08
- **Estimated:** M (~60-90 min)
- **Actual:** ~50 min
- **Velocity:** ~1.4x (ahead of estimate)

## What Went Well
- Skill-only story kept scope tight — no Python modules, no CLI commands, just one well-crafted SKILL.md
- S7.1's template-as-contract pattern (PAT-202) carried forward perfectly — templates provided the structure, skill fills the content
- Reading all 4 parser source files before writing the skill ensured format correctness from the start
- Integration test on temp project validated the full flow: `rai init` → fill docs → `rai memory build` → node extraction

## What Could Improve
- First integration test only produced 19 nodes (target: 30+). The design suggested "3-5 requirements" but didn't calculate whether that volume could hit the gate.
- Should have done the arithmetic proof during design: 3-5 + 3-5 + 5-10 + 3-5 + 1 = 15-26 (not reliably 30+)

## Heutagogical Checkpoint

### What did you learn?
- Vision parser needs "outcome" or "context" keyword in the header row to enter table parsing mode — bold-pipe alone isn't enough
- Architecture docs (system-context, system-design) don't produce individual graph nodes — they're consumed as markdown but not parsed into concepts
- The 30+ gate is carried entirely by prd (RF-XX), vision (outcomes), guardrails (table rows), and backlog (project + epics)

### What would you change about the process?
- Add arithmetic proof step when design includes numeric gates (PAT-204)

### Are there improvements for the framework?
- PAT-204: When a skill has a numeric gate, design should prove suggested volumes achieve it
- Transfer to S7.3: parser contract knowledge carries directly — same docs, same parsers, just different content source (discovery vs conversation)

### What are you more capable of now?
- Full parser contract knowledge for all 4 governance parsers
- Can generate reliably parseable governance content
- Calibrated content density targets for the 30+ node gate

## Improvements Applied
- PAT-204 persisted to memory
- Updated skill Step 3 guidance: "3-5 features → 5-8 RF-XX requirements"
- Updated skill Step 7 node counts to reflect calibrated minimums

## Action Items
- None — all improvements applied inline
