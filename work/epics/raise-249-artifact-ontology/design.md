# Epic RAISE-249: Artifact Ontology & Contract Chain — Design

> **Created:** 2026-02-21
> **Grounded in:** Gemba of 5 skill files + 3 research threads (SAFe, Connextra+Gherkin, SDLD)

---

## Affected Surface (Gemba)

| Skill File | Version | Current Output | Gap |
|------------|---------|---------------|-----|
| `rai-epic-start/SKILL.md` | 1.0.0 | branch + scope commit (informal) | No structured Epic Brief artifact |
| `rai-epic-design/SKILL.md` | 1.1.0 (on RAISE-247) / 1.0.0 (on v2) | `scope.md` (everything mixed) | Scope and design not separated |
| `rai-story-start/SKILL.md` | 1.2.0 | branch + scope commit (informal) | No User Story in standard format |
| `rai-story-design/SKILL.md` | 1.1.0 | `design.md` (WHAT not HOW) | No Gemba, no function-level interfaces |
| `rai-story-plan/SKILL.md` | 1.0.0 | `plan.md` (generic tasks) | No signatures, no test specs, no exact paths |

**Template affected:** `.raise/templates/tech/tech-design-story-v2.md` — Gherkin is optional (section 5, collapsible). Will become required in AC section.

**NOT affected:** `rai-epic-plan`, `rai-story-implement`, `rai-story-review`, `rai-story-close`, katas, CLI code.

---

## Integration Design: The Contract Chain

### Overview

Each skill produces a typed artifact that the next skill consumes as structured input. The chain progressively adds grounding detail from abstract (hypothesis) to concrete (code signatures).

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Epic Brief   │───▶│ Epic Scope   │───▶│ Epic Plan   │
│ (epic-start) │    │ + Design     │    │ (epic-plan)  │
│              │    │ (epic-design)│    │              │
└─────────────┘    └──────┬───────┘    └──────┬───────┘
                          │                    │
                    Component interfaces  Sequencing
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐    ┌──────────────┐
                   │ User Story   │───▶│ Story Design │
                   │ (story-start)│    │(story-design)│
                   └─────────────┘    └──────┬───────┘
                                             │
                                       Function interfaces
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ Story Plan   │
                                      │ (story-plan) │
                                      └──────┬───────┘
                                             │
                                       SDLD Blueprints
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │ Implement    │
                                      │ (mechanical) │
                                      └──────────────┘
```

### Grounding Cascade

| Level | Artifact | Abstraction | Example |
|-------|----------|-------------|---------|
| 1 | Epic Brief | Hypothesis + boundaries | "If we formalize contracts..." |
| 2 | Epic Design | Component interfaces | `GraphGroup` module with `build`, `query`, `context` commands |
| 3 | User Story | Behavior specification | `Given graph is built / When user runs rai graph query / Then results returned` |
| 4 | Story Design | Function interfaces | `def query(query: str, types: list[str]) -> QueryResult` |
| 5 | Story Plan | Code blueprints | File: `src/cli/commands/graph.py:L1-45`, test: `test_graph_query_returns_results` |
| 6 | Implement | Mechanical execution | Write the test, make it pass, commit |

---

## Artifact Contracts

### Contract 1: Epic Brief (epic-start → epic-design)

**Format:** YAML frontmatter + structured markdown
**Location:** `work/epics/{epic-id}/brief.md`

```markdown
---
epic_id: "RAISE-249"
title: "Artifact Ontology & Contract Chain"
status: "draft"
created: "2026-02-21"
---

# Epic Brief: {title}

## Hypothesis
For [target users] who [have this need/pain],
the [solution] is a [category]
that [delivers this value].
Unlike [current state], our solution [key differentiator].

## Success Metrics
- **Leading:** [early signal measurable in first story]
- **Lagging:** [outcome measurable after epic complete]

## Appetite
[S/M/L] — [what this means: S=2-4 stories, M=5-7, L=8-10]

## Scope Boundaries
### In (MUST)
- [non-negotiable 1]

### In (SHOULD)
- [nice-to-have 1]

### No-Gos
- [explicit exclusion with rationale]

### Rabbit Holes
- [attractive trap to avoid]
```

**How epic-design consumes it:**
- Hypothesis → frames objective and success criteria
- Appetite → constrains feature count
- No-Gos → direct to Out of Scope
- Rabbit Holes → direct to Risks

---

### Contract 2: Epic Scope + Design (epic-design → epic-plan, story-start)

**Epic-design produces TWO artifacts** (separated):

**2a. `scope.md`** — WHAT and WHY (consumed by epic-plan for sequencing)
```markdown
---
epic_id: "RAISE-249"
title: "Artifact Ontology & Contract Chain"
status: "in_progress"
stories_count: 6
---

# Epic Scope: {title}

## Objective
[from brief hypothesis, refined]

## Stories
| ID | Story | Size | Status | Dependencies | Description |
|----|-------|------|--------|--------------|-------------|

## In Scope / Out of Scope
[from brief, refined after design]

## Done Criteria
[per-story + epic-level]
```

**2b. `design.md`** — HOW at component level (consumed by story-design for grounding)
```markdown
---
epic_id: "RAISE-249"
grounded_in: "Gemba of [files read]"
---

# Epic Design: {title}

## Affected Surface (Gemba)
| Module/File | Current State | Changes | Stays |

## Target Components
| Component | Responsibility | Key Interface | Consumes | Produces |

## Key Contracts
[Actual types, not pseudocode]

## Migration Path (if restructuring)
- Backward compat strategy
- Consumer changes needed
```

**How story-design consumes `design.md`:**
- Target Components → identifies which component this story implements
- Key Contracts → provides the component-level interface to refine to function level
- Migration Path → informs backward compat requirements

---

### Contract 3: User Story (story-start → story-design)

**Format:** Connextra + Gherkin + SbE
**Location:** `work/epics/{epic-id}/stories/{story-id}/story.md`

```markdown
---
story_id: "S249.1"
title: "story-design Gemba + Integration Design"
epic_ref: "RAISE-249"
size: "M"
status: "draft"
created: "2026-02-21"
---

# Story: {title}

## User Story
As a [role/persona],
I want [capability],
so that [benefit/outcome].

## Acceptance Criteria

### Scenario: {happy path title}
```gherkin
Given [initial context]
When [action]
Then [expected outcome]
```

### Scenario: {edge case title}
```gherkin
Given [context]
When [action]
Then [outcome]
```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|----------------|
| [concrete value] | [concrete action] | [concrete result] |

## Notes
[any context, constraints, references to epic design.md]
```

**How story-design consumes it:**
- User Story → frames the What & Why (Step 2)
- Gherkin scenarios → become acceptance criteria (skip Step 5 of current skill)
- SbE examples → become test cases in story-plan
- Notes → link to epic design.md for component context

**Key change:** Gherkin moves from OPTIONAL (section 5 in current template, collapsible) to REQUIRED in the User Story artifact. story-design no longer generates AC — it receives them.

---

### Contract 4: Story Design (story-design → story-plan)

**Format:** Lean spec + Gemba + function interfaces
**Location:** `work/epics/{epic-id}/stories/{story-id}/design.md`

```markdown
---
story_id: "S249.1"
title: "story-design Gemba + Integration Design"
epic_ref: "RAISE-249"
complexity: "moderate"
status: "draft"
---

# Design: {title}

## 1. What & Why
[from User Story, refined]

## 2. Approach
[high-level solution + components affected]

## 3. Gemba: Current State
[Read actual source files. Map current interfaces.]

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|

## 4. Target Interfaces (Function Level)

### New/Modified Functions
```python
# Actual signatures, not pseudocode
def new_function(param: Type) -> ReturnType:
    """One-line docstring."""
    ...
```

### New/Modified Models
```python
class NewModel(BaseModel):
    field: type
    field2: type
```

### Integration Points
- {function} calls {other_function} from {module}
- {model} is consumed by {component}

## 5. Acceptance Criteria
[From User Story Gherkin — referenced, not duplicated]

See: `story.md` § Acceptance Criteria

## 6. Constraints (if applicable)
[Performance, security, compatibility]
```

**How story-plan consumes it:**
- Gemba § Current State → knows which files to modify and current line ranges
- Target Interfaces → function signatures become task deliverables
- Integration Points → inform task dependencies
- Acceptance Criteria (via story.md) → Gherkin scenarios become test specs

---

### Contract 5: Story Plan — SDLD Task Blueprints (story-plan → story-implement)

**Format:** SDLD-style paired test+implementation tasks
**Location:** `work/epics/{epic-id}/stories/{story-id}/plan.md`

```markdown
---
story_id: "S249.1"
title: "story-design Gemba + Integration Design"
task_count: 4
status: "ready"
---

# Plan: {title}

## Overview
- **Size:** M
- **Tasks:** 4
- **Derived from:** design.md § Target Interfaces

## Tasks

### Task 1: {descriptive name}

**Objective:** [one sentence — what this task delivers]

**RED — Write Failing Test:**
- **File:** `tests/path/to/test_file.py`
- **Test function:** `test_descriptive_name`
- **Setup:** [Given — from Gherkin scenario]
- **Action:** [When — from Gherkin scenario]
- **Assertion:** [Then — from Gherkin scenario]
```python
def test_descriptive_name():
    # Given
    [setup code sketch]
    # When
    result = function_under_test(args)
    # Then
    assert result == expected
```

**GREEN — Implement:**
- **File:** `src/path/to/module.py`
- **Function/Class:**
```python
def function_under_test(param: Type) -> ReturnType:
    """Docstring from design."""
    ...
```
- **Imports:** `from module import dependency`
- **Integration:** [how this connects to existing code]

**Verification:**
```bash
pytest tests/path/to/test_file.py::test_descriptive_name -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenario "happy path" from story.md

---

### Task 2: {next task}
[same structure]

---

### Task N (Final): Integration Verification
- **Objective:** Validate story works end-to-end
- **Verification:** Run all story tests + manual demo
```bash
pytest tests/path/ -v
ruff check src/path/
pyright src/path/
```
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order
1. Task 1 (foundation)
2. Task 2 (depends on 1)
3. Task N — Integration verification

## Traceability
| Task | AC Scenario | Design § |
|------|-------------|----------|
| 1 | "happy path" | Target Interfaces → function_x |
| 2 | "edge case" | Target Interfaces → function_y |
```

**How story-implement consumes it:**
- RED section → write the exact test shown (copy + fill in `...`)
- GREEN section → implement the exact function shown
- Verification → run the exact command shown
- Zero design decisions required

---

## Stories Refined

| ID | Story | Size | Skill | Key Changes |
|----|-------|:----:|-------|-------------|
| S1 | story-design v1.2 | M | rai-story-design | +Step 2.5 Gemba Walk, +Step 3.5 Target Interfaces, Gherkin AC from story.md |
| S2 | story-plan v1.1 | M | rai-story-plan | SDLD task format: RED/GREEN paired, test+impl signatures, traceability |
| S3 | epic-start v1.1 | S | rai-epic-start | +Step 3.5 Epic Brief artifact (SAFe hypothesis + Shape Up) |
| S4 | epic-design v1.2 | S | rai-epic-design | Separate scope.md / design.md output |
| S5 | story-start v1.1 | S | rai-story-start | +Step 5.5 User Story artifact (Connextra + Gherkin + SbE) |
| S6 | Validation | S | — | Run RAISE-247 S1 through new pipeline end-to-end |

### Execution Priority

**Batch 1 (immediate impact — use in RAISE-247):**
- S1 + S2: story-design + story-plan (the grounding gap)

**Batch 2 (complete upstream chain):**
- S3 + S4 + S5: epic-start + epic-design + story-start (the input chain)

**Batch 3 (prove it works):**
- S6: validation with a real story

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Over-specification makes skills too rigid for novel work | Medium | Medium | Depth heuristic: adapt detail to story size (XS=light, L=full SDLD) |
| Gherkin ceremony overhead for simple stories | Medium | Low | story-start skip condition: XS stories can use informal AC |
| SDLD blueprints add planning time | Medium | Medium | Time saved in implement should exceed time spent in plan |
| Meta-circularity: improving skills with current skills | Low | Low | Use current skills for batch 1, new skills for batch 2+ |

---

## What Does NOT Change

- **epic-plan:** Scheduling layer, orthogonal to design cascade. No changes.
- **story-implement:** Only change is consuming the new plan format (richer input). Skill logic stays the same.
- **story-review / story-close:** No changes.
- **CLI code:** Zero code changes. All work is skill content (SKILL.md markdown).
- **Katas:** Skills are the active artifacts; katas are reference.

---

*Grounded in: Gemba of 5 skill files, 1 template, 3 research threads*
*Research: SAFe (epic brief), Connextra+Gherkin+SbE (user stories), SDLD (task blueprints)*
