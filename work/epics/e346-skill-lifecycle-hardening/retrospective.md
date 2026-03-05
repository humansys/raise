# E346: Skill Lifecycle Hardening — Retrospective

**Epic:** E346 (RAISE-346)
**Date:** 2026-03-02
**Duration:** Single session
**Stories:** 4 (1S audit + 1M genericize QR + 1S genericize SR + 1S promote)

## Metrics

| Story | Size | Velocity | Key Deliverable |
|-------|------|----------|-----------------|
| S346.1 | S | ~2x | Full Execution Rule in orchestrators |
| S346.2 | M | 1.5x | QR genericized for 8 languages |
| S346.3 | S | ~2x | SR genericized + toolchain auto-detect in `rai init` |
| S346.4 | S | ~3x | AR+QR promoted to builtin |
| **Total** | **S+M+S+S** | **~2.1x avg** | **27 commits, 35 files, +1704/-51 lines** |

## What Went Well

1. **Pattern compounding** — S346.2 (QR genericization) established the language-detection pattern. S346.3 and S346.4 were mechanical applications of the same pattern, yielding higher velocity each iteration.
2. **User-driven course correction** — The developer caught two critical issues:
   - S346.1 initially produced only an audit doc with no code changes. Reopened to add the Full Execution Rule.
   - Skill compression under orchestration was identified as the core problem this epic should address.
3. **Configuration over convention** — Developer's question "what if we want unsupported languages?" led to `project.test_command` in manifest, then to auto-detection in `rai init`. Better outcome than the original plan.

## What to Improve

1. **Orchestrator compression still partially unsolved** — The Full Execution Rule is a textual instruction, not an enforcement mechanism. The Skill-tool-invocation hypothesis was tested in S346.3 but not yet formally adopted. Needs follow-up.
2. **Language table duplication** — QR, SR, and AR each have their own language tables/patterns. A shared reference could reduce drift risk.
3. **Greenfield interactive prompting** — `rai init` for greenfield projects doesn't ask for toolchain commands yet. Low priority but deferred to parking lot.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Keep name `quality-review` (not `code-review`) | QR scope is broader — test quality, API surface, security |
| Configuration over convention for toolchain | Manifest `test_command` is explicit and reliable vs agent guessing |
| Auto-detect in `rai init` always (not just `--detect`) | File extension counting is cheap, provides immediate value |

## Patterns Identified

- **PAT-E-610** (from S346.2): Language-agnostic skill design — universal checks first, then per-language sections with equivalent depth
- **PAT-E-442 reinforced**: Repetitive extractions compound — each successive language-agnostic conversion was faster
- **Orchestrator compression**: Textual rules help but don't fully prevent — structural boundaries (Skill tool invocation) are more reliable

## Done Criteria Verification

- [x] Orchestrators execute full lifecycle without gaps (Full Execution Rule added)
- [x] Quality-review works on Python, JS/TS, C#, Go, PHP, Dart, Java codebases
- [x] Story-review test verification is language-agnostic
- [x] AR and QR exist in builtin (`src/rai_cli/skills_base/`) with identical deployment copies
- [x] `rai init` auto-detects language and populates toolchain commands
- [x] 3385 tests passing, 0 failures
