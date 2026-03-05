# Epic Retrospective: E340 — Skill Set Ecosystem

## Summary

| Field | Value |
|-------|-------|
| Epic | RAISE-340 |
| Stories | 5 (4S + 1M) |
| Commits | 35 |
| Tests added | 22 (8 + 4 + 0 + 10 + 0) |
| Total tests | 3367 passing |
| Code | +752 lines Python (10 files), +779 lines docs (17 files) |
| Avg velocity | 1.2x (range: 1.0x – 2.0x) |

## Stories

| ID | Story | Size | Actual | Velocity |
|----|-------|------|--------|----------|
| S340.1 | Skill set overlay deployment | S | S | 1.0x |
| S340.2 | Skill creation targets sets | S | S | 1.0x |
| S340.3 | Refactor /rai-skill-create (SRP) | S | S | 1.0x |
| S340.4 | `rai skill set` CLI group | M | M | 1.0x |
| S340.5 | `/rai-skillset-manage` skill | S | XS | 2.0x |

## Key Decisions

| ID | Decision | Outcome |
|----|----------|---------|
| D1 | Overlay-only (no intermediate default/) | Correct — simpler, two-hop deferred to v2.3 |
| D2 | Same-name = full replacement | Natural, consistent with Helm/OMZ patterns |
| D3 | Overlay skills NOT three-hash managed | User-owned, no surprise overwrites |
| D4 | `--skill-set` flag (explicit) | Clear mental model, no magic |
| D5 | SRP split: skill-create vs skillset-manage | Emerged mid-epic, correct call |
| D6 | Unify copy_skill_tree (Path \| Traversable) | AR R1 — structural typing worked cleanly |

## Architecture Review

Formal AR pre-implementation. Verdict: PASS WITH QUESTIONS.
Q2 (two-hop vs overlay-only) resolved to overlay-only for v2.2.
R1 adopted (unified copy function). R2/R3 deferred.

## Patterns

| ID | Pattern |
|----|---------|
| PAT-E-610 | Path \| Traversable structural typing — both share iterdir/is_file/read_text |
| PAT-E-611 | Customize builtin = copy deployed file to overlay set |
| PAT-E-612 | Typer nested groups via add_typer — clean CLI hierarchy |
| PAT-E-613 | Conversational skills as CLI wrappers — skill guides, CLI executes |

## What Went Well

- Research-grounded architecture (14 projects analyzed) gave confidence in design
- SRP split caught mid-epic saved future tech debt
- overlay-only kept implementation proportional
- S340.5 at 2.0x velocity — CLI wrapper pattern is mechanical once established

## What Could Improve

- Epic-run orchestrator cortocircuited sub-skills twice — needs enforcement mechanism
- Initial scope missed SRP issue (S340.3 added mid-epic) — scope review should check for responsibility mixing
- pyright caught `_copy_skill_tree` as private after implementation — type check earlier in pipeline

## Market Impact

Named skill sets are a market differentiator. No AI coding tool (Cursor, Copilot, Windsurf, Cline, Roo Code, Aider, Continue.dev) offers team-level skill customization with upgrade safety.
