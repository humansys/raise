# Retrospective: F128.2 — Decouple Init from Claude Paths

## Summary
- **Feature:** F128.2
- **Started:** 2026-02-18
- **Completed:** 2026-02-18
- **Size:** M (5 SP)
- **Estimated:** 65 min
- **Actual:** ~25 min
- **Tasks:** 5 (4 refactoring + 1 quality gate)
- **Commits:** 8 (scope + design + plan + 4 refactors + progress)

## What Went Well
- Gemba review caught scope inaccuracy before implementation — 4 coupling points, not 5
- Bottom-up execution (leaf → domain → integration) — each task built on Task 1's pattern
- Consistent API pattern (`*, ide_config: IdeConfig | None = None`) applied across all 4 functions
- Zero regression — 2028 tests pass, 90.45% coverage, ruff clean, pyright 0 errors
- Clean TDD cycle for each task — red/green/refactor

## What Could Improve
- Calibration was generous — M estimate for what turned out to be a repeating-pattern refactor
- Task 4 (claudemd.py) was API consistency only — content was already IDE-agnostic. Design flagged this but estimated S; actual was XS

## Heutagogical Checkpoint

### What did you learn?
- Gemba catches scope drift that abstract planning misses. The epic said 5 coupling points; code said 4. `get_claude_memory_path()` handles IDE user-state (`~/.claude/projects/`), not project structure.
- Keyword-only args prevent positional confusion when functions already have multiple optional params
- Bottom-up refactoring (leaf → integration) creates natural dependency flow and clean commits

### What would you change about the process?
- Account for pattern compression in calibration: when tasks repeat a template established in Task 1, subsequent tasks execute faster. First instance = S, repeats = XS.

### Are there improvements for the framework?
- Calibration pattern captured (PAT-F-012): repeated-pattern tasks compress. Calibrate by novelty, not count.

### What are you more capable of now?
- The init chain is fully decoupled from Claude paths. F128.3 can pass `get_ide_config("antigravity")` and get `.agent/skills/` everywhere. The refactor is invisible to existing callers.

## Improvements Applied
- PAT-F-012: Repeated-pattern calibration insight persisted to memory

## Action Items
- [ ] Update ADR-031 "dataclass" → "Pydantic BaseModel (frozen)" (carried from F128.1 retro)
