# Retrospective: S15.5 Architectural Context Query Helpers

## Summary
- **Story:** S15.5
- **Size:** S (3 SP)
- **Started:** 2026-02-08
- **Completed:** 2026-02-08
- **Commits:** 5 (scope, skill fix, design, plan, Task 1, Task 2)

## What Went Well
- Two-hop traversal pattern (module → BC → guardrails) worked exactly as designed — no surprises during implementation
- Reuse of `get_neighbors(edge_types=...)` from S15.4 meant zero new graph-level code
- Integration test showed rich real data: mod-memory has 21 constraints, 4 dependencies
- Governance drift catch led to fixing 3 skills — valuable side-effect

## What Could Improve
- Almost skipped `/story-design` for an S-sized story despite PAT-186 saying "design is not optional" — the skill template still had stale "optional" language
- Should have queried the graph for methodology guidance before making the skip decision

## Heutagogical Checkpoint

### What did you learn?
- Skills can encode stale guidance that pattern memory has already corrected. The graph evolves through experience, but skills only update when someone explicitly touches them. This is a form of governance drift (PAT-150) applied to process artifacts, not just code.

### What would you change about the process?
- Add a "check graph for lifecycle guidance" step to `/story-start` — not just for architectural context (that's S15.6), but for process methodology itself. The graph already has patterns about when to design, when to skip, etc.

### Are there improvements for the framework?
- Fixed: 3 skills updated to remove "optional design" language (story-start, story-design, story-plan)
- Future: Consider a `rai doctor` style check that compares skill descriptions against pattern memory for drift

### What are you more capable of now?
- Composing typed BFS traversals into higher-level helper methods
- Understanding the two-hop pattern for constraint discovery in ontology graphs
- Recognizing governance drift between different layers of the framework (skills vs patterns)

## Improvements Applied
- `story-start/SKILL.md`: Removed "Optional for simple features", now says "Design is not optional (PAT-186)"
- `story-design/SKILL.md`: Updated description and frequency from "per-story-as-needed" to "per-story"
- `story-plan/SKILL.md`: Removed "for simple stories that skip design"

## Action Items
- [ ] Consider adding graph-based methodology check to `/story-start` (parking lot candidate)
