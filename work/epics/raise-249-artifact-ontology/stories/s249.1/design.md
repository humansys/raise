---
story_id: "S249.1"
title: "story-design v1.2 — Gemba Walk + Integration Design"
epic_ref: "RAISE-249"
complexity: "moderate"
status: "draft"
---

# Design: story-design v1.2

## 1. What & Why

**Problem:** story-design v1.1 produces specs that say WHAT but not HOW at function level. The implementer AI still makes architectural decisions (which functions to create, what signatures to use, how components connect) that should have been resolved in design.

**Value:** Adding Gemba Walk and Target Interfaces grounds the design in actual code state, producing function-level contracts that story-plan can turn into mechanical SDLD blueprints. Zero design decisions at implementation time.

## 2. Approach

Modify `rai-story-design/SKILL.md` to add two new steps and adjust AC flow:
- **+Step 2.5 Gemba Walk** — read actual source, map current interfaces
- **+Step 3.5 Target Interfaces** — define function signatures, models, integration points
- **Adjust Step 5** — AC referenced from story.md (Gherkin), not generated in design
- **Update Output section** — match Contract 4 format from epic design.md

Single file modified: `.claude/skills/rai-story-design/SKILL.md`

## 3. Gemba: Current State

| Section | Current Content | What Changes | What Stays |
|---------|----------------|--------------|------------|
| Frontmatter | version 1.1.0 | → 1.2.0 | All other metadata |
| Step 0–0.2 | Telemetry + Prerequisites + Arch Context | No change | As-is |
| Step 1 | Complexity assessment matrix | No change | As-is |
| Step 1.5 | Risk assessment (conditional) | No change | As-is |
| Step 1.7 | Research gate for UX (conditional) | No change | As-is |
| Step 2 | Frame What & Why | No change | As-is |
| *(gap)* | — | **+Step 2.5 Gemba Walk** | — |
| Step 3 | Approach (high-level, "trust AI for HOW") | Soften "trust AI" language; approach now includes component mapping | Core purpose stays |
| *(gap)* | — | **+Step 3.5 Target Interfaces** | — |
| Step 4 | Create Examples (CRITICAL) | No change | As-is |
| Step 5 | Define AC (MUST/SHOULD/MUST NOT) | Reference Gherkin from story.md; fallback if no story.md | Structure stays |
| Step 6 | Optional sections | No change | As-is |
| Step 7 | AI optimization | No change | As-is |
| Step 8 | Review checklist | Add Gemba + interfaces to checklist | Structure stays |
| Step 9 | Telemetry | No change | As-is |
| Output | Artifact path + next skill | Add Contract 4 output format spec | Path stays |
| Inputs | "Feature from backlog, Technical Design" | Add: "User Story (story.md) with Gherkin AC" as optional input | Other inputs stay |

## 4. New Content Specification

### Step 2.5: Gemba Walk (new)

**Purpose:** Read actual source files the story will modify. Map current interfaces before designing new ones.

**Depth heuristic by story size:**

| Size | Gemba Depth | What to Capture |
|------|-------------|-----------------|
| XS | Skip | — |
| S | Skim | File list + key function names |
| M | Full | File, current interface, what changes, what stays |
| L+ | Full + dependencies | Same as M + upstream/downstream consumers |

**Output table:**
```markdown
| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
```

**Key instruction:** "Read the actual source. Do not guess from memory or documentation. If you haven't read the file, you don't know its interface." (Reinforces PAT-E-187: Code as Gemba)

### Step 3.5: Target Interfaces (new)

**Purpose:** Define the function-level contracts that story-plan will consume as task deliverables.

**Three sub-sections:**

1. **New/Modified Functions** — actual Python signatures with type hints and one-line docstrings
2. **New/Modified Models** — Pydantic model definitions with field types
3. **Integration Points** — which function calls which, which model is consumed where

**Key instruction:** "Use actual signatures, not pseudocode. These become the implementation target in story-plan tasks."

**Depth heuristic:** Same as Gemba — XS=skip, S=key signatures only, M+=full.

### Step 5 adjustment: AC from story.md

**Change:** Instead of "Define Acceptance Criteria", the step becomes "Reference Acceptance Criteria":
- If `story.md` exists with Gherkin scenarios → reference them, don't duplicate
- If no `story.md` (backward compat) → fall back to current behavior (define AC inline)

**Template:**
```markdown
## 5. Acceptance Criteria
[From User Story Gherkin — referenced, not duplicated]
See: `story.md` § Acceptance Criteria
```

### Output section update

Add Contract 4 output format to the Output section, showing the target design.md structure:
```markdown
## Design Output Structure (Contract 4)
1. What & Why
2. Approach
3. Gemba: Current State (table)
4. Target Interfaces (signatures, models, integration points)
5. Acceptance Criteria (reference to story.md)
6. Constraints (if applicable)
```

## 5. Acceptance Criteria

**MUST:**
- [ ] SKILL.md has Step 2.5 Gemba Walk with depth heuristic table (XS/S/M/L+)
- [ ] SKILL.md has Step 3.5 Target Interfaces with 3 sub-sections (functions, models, integration)
- [ ] Step 5 references Gherkin from story.md with fallback to inline AC
- [ ] Output section describes Contract 4 format
- [ ] Version bumped to 1.2.0 in frontmatter

**SHOULD:**
- [ ] Step 8 checklist updated with Gemba + interfaces items
- [ ] Inputs section mentions story.md as optional input
- [ ] Step 3 language adjusted (remove "trust AI for HOW", since HOW is now designed)

**MUST NOT:**
- [ ] Break backward compat — story.md is optional input, not required
- [ ] Add code or CLI changes — this is pure skill content
- [ ] Change step numbering of existing steps (use .5 insertion)
