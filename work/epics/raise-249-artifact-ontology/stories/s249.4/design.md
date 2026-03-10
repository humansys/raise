---
story_id: "S249.4"
title: "epic-design v1.2 — Separate scope.md / design.md"
epic_ref: "RAISE-249"
complexity: "simple"
status: "draft"
---

# Design: epic-design v1.2 — Separate scope.md / design.md

## 1. What & Why

**Problem:** `rai-epic-design` v1.0.0 produces a single `scope.md` that mixes project management concerns (stories, done criteria, in/out scope) with engineering concerns (Gemba, component interfaces, contracts). Downstream consumers must parse one monolithic document to find their relevant sections.

**Value:** Separating into `scope.md` (WHAT/WHY) and `design.md` (HOW/interfaces) gives each consumer a focused input — `epic-plan` sequences from scope, `story-design` grounds from design. This is Contract 2 in the artifact ontology chain.

## 2. Approach

Modify `rai-epic-design/SKILL.md` to:
- Split Step 10 (Create Epic Scope Document) into two steps: one for `scope.md`, one for `design.md`
- Add a `design.md` template alongside the existing `scope.md` template
- Update the Output section to list both artifacts
- Update the template section with Contract 2 format from epic design.md

Single file change: `.claude/skills/rai-epic-design/SKILL.md`

## 3. Gemba: Current State

| Section | Current State | What Changes | What Stays |
|---------|--------------|--------------|------------|
| Step 10 | Creates single `scope.md` with everything | Split: scope.md gets WHAT/WHY, new step for design.md gets HOW | Step numbering for 0-9 |
| Output section | Lists `scope.md` only | Add `design.md` as primary output | ADRs, parking lot as secondary |
| Epic Scope Template | Single monolithic template | Trim to scope-only (remove Gemba, interfaces) | YAML frontmatter pattern |
| metadata.version | 1.0.0 | Bump to 1.2.0 | All other metadata |
| Context.Outputs | Lists `scope.md` only | Add `design.md` | Everything else in Context |

**Key observation:** Steps 2-3 (Scope Boundaries, Architectural Impact) feed scope.md. Steps 4-6 (Features, ADRs, Dependencies) feed both. Step 3 assessment + any Gemba work feeds design.md. The split is natural along the WHAT/HOW boundary.

## 4. Target Interfaces

N/A — this is skill content (markdown), not code. The "interface" is the artifact format defined in Contract 2.

**Contract 2a — scope.md format:**
- YAML frontmatter: epic_id, title, status, stories_count
- Sections: Objective, Stories table, In/Out Scope, Done Criteria, Dependencies

**Contract 2b — design.md format:**
- YAML frontmatter: epic_id, grounded_in
- Sections: Affected Surface (Gemba), Target Components, Key Contracts, Migration Path

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- PAT-E-400: Examples in templates must not assume Python-only — use language-neutral or multi-language examples
- No CLI code changes — pure skill content
