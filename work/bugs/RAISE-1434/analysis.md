# RAISE-1434: Analysis

## Root Cause

CLAUDE.local.md was designed as machine-managed local state — a file that skills would update
to reflect current epic/story focus. The design had two fatal flaws:

1. **No enforcement mechanism:** Skills instructed LLM subagents to "update CLAUDE.local.md" as a
   secondary step. Subagents deprioritize secondary artifacts when context saturates.
2. **Redundant with git state:** ADR-038 (GitStateDeriver, GH-15) made git the authoritative source
   for session state. `rai session context` already derives current focus from git branches and
   work artifacts. CLAUDE.local.md became a redundant, unreliable shadow copy.

## Method
Direct analysis — single cause, well-evidenced.

## Evidence
- CLAUDE.local.md does not exist in repo (drifted and was never recreated)
- `.gitignore` line 9 lists it (was intended as local-only)
- No CLI code generates it — only 3 skill SKILL.md files reference it
- `rai session context` already provides the same data reliably from git

## Fix Approaches

- **A (simplest): Remove all references** — delete mentions from 3 SKILL.md files + .gitignore.
  Replace with `rai session context` as the authoritative source. Trade-off: none, it's already broken.
- **B (CLI command):** Add `rai context update` to regenerate deterministically.
  Trade-off: maintains a redundant artifact that duplicates git-derived state.
- **C (full deprecation):** A + update ADRs/docs that reference it.
  Trade-off: more thorough but touches many historical docs unnecessarily.

## Recommendation
**A** — the simplest approach fully addresses the root cause. The file is already dead.
Historical docs are historical — they describe what was true at the time.
