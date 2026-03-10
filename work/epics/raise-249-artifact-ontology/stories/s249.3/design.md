---
story_id: "S249.3"
title: "epic-start v1.1 — Epic Brief Artifact (Contract 1)"
epic_ref: "RAISE-249"
complexity: "simple"
status: "draft"
---

# Design: epic-start v1.1 — Epic Brief Artifact

## 1. What & Why

**Problem:** epic-start v1.0 produces a scope commit with informal text but no structured artifact. epic-design starts from scratch — it infers the hypothesis, appetite, and boundaries from the scope commit or conversation. There's no typed handoff between epic-start and epic-design.

**Value:** Adding an Epic Brief artifact (Contract 1) gives epic-design structured input: hypothesis (SAFe), appetite (Shape Up), explicit no-gos and rabbit holes. The brief becomes the authoritative source of epic intent.

## 2. Approach

Add Step 3.5 to `rai-epic-start/SKILL.md` that produces a `brief.md` artifact in Contract 1 format. Update Output and Summary sections. Bump version.

**Components affected:**
- `.claude/skills/rai-epic-start/SKILL.md` — modify (add Step 3.5, update Output, bump version)

## 3. Gemba: Current State

| Section | Current Content | What Changes | What Stays |
|---------|----------------|--------------|------------|
| Frontmatter | version 1.0.0 | → 1.1.0 | All other metadata |
| Steps 1-3 | Verify branch, create branch, define scope | No change | As-is |
| *(gap)* | — | **+Step 3.5 Epic Brief Artifact** | — |
| Step 4 | Scope commit | Update to mention `brief.md` included | Logic stays |
| Step 5 | Register in backlog | No change | As-is |
| Steps 6-7 | Telemetry + lifecycle | No change | As-is |
| Output | Branch + commit + telemetry | Add `brief.md` | Existing outputs stay |
| Summary Template | Quick Scope | Add brief mention | Template stays |

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## Notes
- Contract 1 format fully defined in epic design.md § Contract 1
- Step 3.5 goes between Step 3 (Define Scope) and Step 4 (Scope Commit) — brief is created alongside scope, committed together
