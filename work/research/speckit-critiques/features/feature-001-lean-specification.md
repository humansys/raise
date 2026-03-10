# Feature 001: Lean Specification Templates

**Feature ID**: FEAT-RAISE-SK-001
**Priority**: P0
**Effort**: Medium (4-6 weeks)
**Impact**: High (addresses #1 complaint)
**Based On**: Critique Gap 1

---

## Context

### Spec-Kit Limitation
Generates 2,577 lines of markdown for 689 lines of code (3.7:1 ratio)[^1]. User quote: "Much of the content is duplicative, and faux context."

### User Complaints
- 10x slowdown vs. iterative development
- Review burden overwhelming
- "You may need AI assistance just to navigate your own specifications"

### Opportunity
Apply **§7 Lean Software Development** principle: Eliminate waste (Muda); optimize for value, not completeness.

**Target**: Reduce markdown:code ratio from 3.7:1 to <1.5:1 while maintaining AI alignment quality.

---

## User Stories

### US1: As a developer, I want lean spec templates so I can create specs quickly without excessive documentation

**Acceptance Criteria**:
- [ ] Lean template variant available (`--lean` flag)
- [ ] Spec creation time ≤ 2x coding time (vs. 10x current)
- [ ] Template 40-60% smaller than standard spec-kit template
- [ ] AI adherence quality ≥ 90% of comprehensive template

**Priority**: P0

---

### US2: As a reviewer, I want concise specs I can read in <15 minutes so I can provide meaningful feedback

**Acceptance Criteria**:
- [ ] Spec summary section (1-2 pages) provides complete overview
- [ ] Detail sections optional/collapsible
- [ ] Review checklist auto-generated from lean template
- [ ] 80% of reviewers complete review in <15 min (user testing)

**Priority**: P0

---

### US3: As an AI agent, I want progressive disclosure so I can load only relevant spec sections without context window bloat

**Acceptance Criteria**:
- [ ] Core spec (problem, intent, constraints) always loaded
- [ ] Detail sections loaded on-demand
- [ ] API: AI can request specific section by ID
- [ ] Token usage reduced 30-50% vs. loading full spec

**Priority**: P1

---

### US4: As a team lead, I want redundancy detection so we don't duplicate content across spec/plan/tasks

**Acceptance Criteria**:
- [ ] Automated scan detects duplicate text (>80% similarity)
- [ ] Suggestions: Consolidate or cross-reference
- [ ] Report shows redundancy % per spec
- [ ] Target: <10% redundancy (vs. current unknown %)

**Priority**: P1

---

## Functional Requirements

### FR-001: 80/20 Template Design
Research-backed identification of 20% spec content driving 80% AI alignment value.

**Implementation**:
- Empirical testing: Vary spec detail level; measure AI adherence
- A/B test: Lean vs. comprehensive templates
- Publish findings; update template based on data

**Dependencies**: Requires telemetry (Feature 003: Observable Gates)

---

### FR-002: Lean Template Variant
Default minimal viable specification (MVS) template.

**Structure**:
```markdown
# Feature Spec: [Name]

## Problem (Required)
What problem does this solve? Why now?

## User Stories (Required)
As a [user], I want [capability], so that [benefit].
**AC**: [Specific, testable criteria]

## Technical Constraints (Required)
- Performance: [e.g., <200ms response time]
- Security: [e.g., encrypt PII at rest]
- Compatibility: [e.g., support Safari 15+]

## Success Criteria (Required)
How do we know it works?
- [ ] Metric 1
- [ ] Metric 2

## Context (Optional, collapsed by default)
Background, assumptions, dependencies.

## Detailed Flows (Optional, collapsed by default)
Step-by-step user/system interactions.

## Edge Cases (Optional, collapsed by default)
Rare scenarios, error handling.
```

**Comparison**:
- Standard spec-kit: ~15-20 sections, 10-50 pages
- Lean template: 4 required + 3 optional sections, 2-5 pages

---

### FR-003: Progressive Disclosure UI
Collapsible sections; expand on-demand.

**CLI**: Markdown with HTML `<details>` tags
**Web UI** (future): Accordion sections; "Expand for AI" button
**API**: `GET /spec/{id}/section/{section-id}`

---

### FR-004: Redundancy Scanner
Static analysis tool to detect duplicate content.

**Algorithm**:
- Text similarity (cosine similarity, Levenshtein distance)
- Identify: Spec ↔ Plan overlap, Plan ↔ Tasks overlap
- Report: `redundancy-report.md` with suggestions

**Threshold**: Flag if >80% similar across 2+ paragraphs

---

### FR-005: Template Customization
Allow teams to create org-specific lean templates.

**Mechanism**:
- `.raise/templates/custom-lean.md`
- Inherit from base lean template
- Override sections; add custom sections
- Validate: Ensure required sections present

---

## Technical Approach

### Architecture

**Template Engine**:
- Jinja2 or Liquid (variable substitution)
- Conditional sections: `{% if include_details %}...{% endif %}`
- Inheritance: `custom.md extends base-lean.md`

**Redundancy Scanner**:
- Python script: `check-redundancy.py`
- Libraries: `difflib`, `sklearn.feature_extraction.text`
- Output: JSON report + Markdown summary

**Progressive Disclosure**:
- Markdown: Use `<details><summary>` HTML tags
- Web UI: React accordion component (future)
- API: Section-based retrieval (FastAPI/Flask)

---

### Integration Points

**With Spec-Kit Core**:
- Drop-in replacement for standard templates
- `specify init --template=lean` flag
- Backward compatible: Standard template still available

**With Observable Gates (Feature 003)**:
- Telemetry: Track which sections AI actually reads
- Optimize: Remove unused sections from templates

**With Context Optimization (Feature 006)**:
- Chunking: Sections map to semantic chunks
- RAG: Embed sections for retrieval

---

### Data Model

**Template Metadata** (YAML frontmatter):
```yaml
---
template_name: "Lean Specification"
version: "1.0.0"
required_sections:
  - problem
  - user_stories
  - technical_constraints
  - success_criteria
optional_sections:
  - context
  - detailed_flows
  - edge_cases
target_length: "2-5 pages"
markdown_code_ratio_target: "<1.5:1"
---
```

**Redundancy Report** (JSON):
```json
{
  "spec_id": "001-auth-feature",
  "redundancy_score": 0.32,
  "duplicates": [
    {
      "section_1": "spec.md#user-stories",
      "section_2": "plan.md#functional-requirements",
      "similarity": 0.87,
      "suggestion": "Consolidate or reference spec.md#user-stories from plan.md"
    }
  ]
}
```

---

## Implementation Plan

### Phase 1: MVP (Weeks 1-2)
- [ ] Design lean template structure (research + user feedback)
- [ ] Implement lean template markdown file
- [ ] Add `--template=lean` flag to `/specify` command
- [ ] Basic testing: Create 5 specs with lean template

**Deliverable**: Lean template usable; 40-60% size reduction validated

---

### Phase 2: Redundancy Detection (Weeks 3-4)
- [ ] Implement redundancy scanner script
- [ ] Integrate into workflow (post-spec creation check)
- [ ] CLI command: `/specify.check-redundancy`
- [ ] Report generation (JSON + Markdown)

**Deliverable**: Redundancy detection operational; reports actionable

---

### Phase 3: Progressive Disclosure (Weeks 5-6)
- [ ] Add `<details>` tags to optional sections in lean template
- [ ] CLI: Render collapsible sections properly
- [ ] API design: Section retrieval endpoint (spec for future)
- [ ] Documentation: How to use progressive disclosure

**Deliverable**: Specs have collapsible sections; reduced visual clutter

---

### Phase 4: Optimization (Ongoing)
- [ ] Collect telemetry: Which sections AI reads (requires Feature 003)
- [ ] A/B test: Lean vs. comprehensive quality comparison
- [ ] Iterate: Remove low-value sections; refine templates
- [ ] Publish findings: Share data with community

**Deliverable**: Data-driven template optimization

---

## Success Metrics

### Quantitative

| Metric | Baseline (Spec-Kit) | Target (RaiSE Lean) | Measurement Method |
|--------|---------------------|---------------------|-------------------|
| Markdown:code ratio | 3.7:1 | <1.5:1 | Lines of markdown / lines of code |
| Spec creation time | 10x coding time | ≤2x coding time | User time tracking |
| Spec length | 10-50 pages | 2-5 pages | Page count |
| AI adherence | Unknown | ≥90% of comprehensive | Acceptance criteria met % |
| Review time | >30 min (anecdotal) | <15 min | User testing (n=20) |

---

### Qualitative

**User Feedback** (target: 80% agreement):
- [ ] "Lean specs feel manageable, not overwhelming"
- [ ] "I can create a spec quickly without sacrificing quality"
- [ ] "Redundancy scanner helps eliminate waste"
- [ ] "Progressive disclosure reduces cognitive load"

**NPS Impact**:
- Baseline: Unknown (spec-kit)
- Target: +20 points improvement among lean template users

---

## References

[^1]: Eberhardt, C. (2025). Putting Spec Kit Through Its Paces: Radical Idea or Reinvented Waterfall? https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html

---

**Related Features**:
- Feature 003: Observable Validation Gates (telemetry for optimization)
- Feature 006: Context Window Optimization (chunking aligns with sections)
- Feature 004: Agile Integration (lean specs fit iterative workflows)

**Status**: Specification Complete
**Next Steps**: Prototype lean template; user testing with 5-10 teams
