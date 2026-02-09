# Retrospective: S7.3 `/project-onboard` Skill

## Summary
- **Story:** S7.3 — `/project-onboard` brownfield onboarding skill
- **Size:** M
- **Started:** 2026-02-08
- **Completed:** 2026-02-08
- **Estimated:** ~60 min (M-sized)
- **Actual:** ~45 min

## What Went Well
- S7.2 (`/project-create`) provided an excellent template — same parser contracts, same structure, adapted for brownfield
- Discovery pipeline (`raise discover scan` + `analyze`) worked seamlessly on the temp project
- `raise init --detect` convention detection integrated naturally into the skill flow
- Integration test validated end-to-end: 80 concepts, 134 relationships from a 12-file temp project
- PAT-201 (separate skills for greenfield/brownfield) continues to prove out — distinct user experiences with shared contracts

## What Could Improve
- Deleted temp dir while shell cwd was inside it, killing the Bash tool for the rest of the session. Cost ~10 min of debugging + session restart.
- Convention detection output format (`MUST-STYLE-001` with backticks) differs from parser-compatible format (`must-code-001` without backticks). The skill documents the merge strategy, but the CLI-generated guardrails.md may confuse users who compare formats.

## Heutagogical Checkpoint

### What did you learn?
- Shell cwd persistence is fragile — never delete a directory you're standing in. Always cd out first.
- `raise init --detect` generates guardrails in a different format than the parser expects. The skill handles this by documenting a merge strategy, but a future improvement could harmonize the formats in the CLI.

### What would you change about the process?
- For integration tests on temp directories, always use absolute paths and never cd into the temp dir, OR cd out explicitly before cleanup.

### Are there improvements for the framework?
- Consider harmonizing `raise init --detect` guardrail format with the governance parser contract (YAML frontmatter, lowercase IDs, "Derived from" column). Currently two different formats for the same concept.

### What are you more capable of now?
- Full onboarding pipeline validated: init → detect → discover → governance → graph → session-start
- Pattern of skill reuse with adaptation (greenfield → brownfield) is now proven and repeatable

## Improvements Applied
- None needed in framework — the skill captures the format merge strategy

## Action Items
- [ ] Future: harmonize `raise init --detect` guardrails format with parser contract (parking lot item)
