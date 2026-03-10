---
epic_id: "E350"
tracker: "RAISE-364"
status: "done"
---

# E350: Rai Experience Portability — Retrospective

## Summary
Made the Rai experience fully reproducible: `git clone` + `rai init` + `rai graph build` gives any developer a complete Rai instance with same behavior, context, and capabilities.

## What Went Well
- **Infrastructure was ahead of scope**: 3-tier pattern system, hook system, and init flow were already partially built. 3 of 7 stories were smaller than estimated.
- **Process economy patterns (PAT-E-648, PAT-E-649)**: Applied from S350.2 onward — skipping unnecessary phases, running tests per code change not per phase. Reduced ceremony without losing quality.
- **Interactive design for complex stories**: S350.3 benefited from user challenging assumptions ("why regenerate CLAUDE.md on every graph build?"), leading to better architecture.
- **Semi-automatic destillation**: S350.4 used agent-assisted grouping + human validation to expand base patterns from 20 to 55 efficiently.

## What Could Improve
- **S350.1 over-ceremony**: Full 8-phase run for a doc-only S story took 24 min. Led to PAT-E-648/649 which fixed subsequent stories.
- **Estimation accuracy**: Epic estimated L+2M+3S, actual was M+M+3S+2XS. Root cause: didn't verify existing implementation before scoping (PAT-E-024).
- **S350.7 was already done**: Investigation-only — credentials were already separated. Should have been caught in S350.1 inventory.

## Key Decisions
- ADR-044: Four-layer artifact model (base/project/personal/derived)
- CLAUDE.md regenerated only on `rai init`, not `rai graph build` (static config, not graph-dependent)
- Default scope changed to personal (patterns born personal, promoted explicitly)
- Epics confirmed as logical containers, no epic branches

## Patterns Captured
- PAT-E-645: Doc-only stories adapt TDD via filesystem audit
- PAT-E-646: Bottom-up audit discovers invisible categories
- PAT-E-647: Mixed-concern flags as design tool
- PAT-E-648: Test economy — per code change, not per phase
- PAT-E-649: Phase economy — respect skill complexity gates
- PAT-E-650: Git rm + gitignore two-step
- PAT-E-597: future annotations mask NameError
- PAT-E-598: bare except hides import errors
- BASE-021 to BASE-055: 35 new universal base patterns

## Metrics
- Stories: 7/7 done
- Estimated total: L+2M+3S (~34 story points equivalent)
- Actual total: M+M+3S+2XS (~22 story points equivalent)
- Base patterns: 20 -> 55
- Project patterns: 626 (unchanged, now defaulting to personal scope for new ones)
