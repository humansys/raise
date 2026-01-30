# Feature 002: Brownfield-First Architecture

**Feature ID**: FEAT-RAISE-SK-002
**Priority**: P0
**Effort**: High (8-12 weeks)
**Impact**: Critical (unlocks 70% of market)
**Based On**: Critique Gap 2

---

## Context

### Spec-Kit Limitation
"Installing Spec-Kit with uvx for existing projects fails"[^1]. Designed exclusively for greenfield scenarios.

### User Complaints
- 70-80% of software work is maintenance/enhancement (brownfield)
- User quote: "Clean examples work beautifully for greenfield; brownfield shaped by months of evolving decisions"
- No workflow for retrofitting specs onto existing code
- Multi-repo features unsupported

### Opportunity
**§1 Principio/Flujo/Patrón/Técnica over Generic Abstraction**: Meet teams where they are; incremental adoption.

**Market Expansion**: Greenfield = 20-30% of projects; Brownfield = 70-80%. Currently untapped.

---

## User Stories

### US1: As a developer on a legacy codebase, I want to generate specs from existing code so I don't have to write them from scratch

**Acceptance Criteria**:
- [ ] `/specify.retrofit` command analyzes code → generates draft spec
- [ ] AI extracts: Purpose, user stories, architecture, constraints
- [ ] Human reviews/refines generated spec
- [ ] Success rate: 80% of specs usable with <30 min refinement

**Priority**: P0

---

### US2: As a tech lead, I want incremental spec adoption so I can start with one module without specifying the entire codebase

**Acceptance Criteria**:
- [ ] Install RaiSE Spec-Kit on existing project (no greenfield requirement)
- [ ] Create spec for single feature/module (not whole app)
- [ ] Spec coverage metric: % of codebase covered by specs
- [ ] Gradually expand coverage (like test coverage)

**Priority**: P0

---

### US3: As a developer, I want spec-code drift detection so I know when my implementation diverges from the spec

**Acceptance Criteria**:
- [ ] Automated comparison: Spec vs. implementation
- [ ] Alert when divergence exceeds threshold (configurable)
- [ ] Suggestion: Update spec, update code, or acknowledge drift
- [ ] Integrate into CI/CD (PR checks)

**Priority**: P1

---

### US4: As an architect, I want multi-repo feature specs so I can coordinate changes across microservices

**Acceptance Criteria**:
- [ ] Single spec references multiple repos (YAML frontmatter)
- [ ] Cross-repo consistency checks
- [ ] Validate: All affected repos updated before feature complete
- [ ] Link PRs across repos

**Priority**: P0

---

### US5: As a developer, I want to understand existing code's intent so I can maintain/enhance without breaking it

**Acceptance Criteria**:
- [ ] Spec acts as "documentation of current state"
- [ ] Clearly marks: Original intent vs. evolved behavior
- [ ] Includes: Architecture diagrams (auto-generated from code)
- [ ] Links: Code → Spec sections (traceability)

**Priority**: P1

---

## Functional Requirements

### FR-001: Reverse Spec Generation
AI-powered analysis of existing code to draft specification.

**Input**:
- Codebase path(s)
- Module/feature to spec (optional; default: entire codebase)
- Context: README, existing docs, commit history

**Process**:
1. **Static Analysis**: Parse code structure (AST)
2. **Semantic Analysis**: Identify: Endpoints, functions, classes, data models
3. **Intent Extraction**: Analyze names, comments, tests → infer purpose
4. **Architectural Mapping**: Dependencies, data flow, integrations
5. **Draft Spec Generation**: Populate template with extracted info

**Output**:
- `spec.md` (draft, marked as "GENERATED - REQUIRES REVIEW")
- Confidence scores per section (low/medium/high)
- Gaps: Sections AI couldn't infer (manual input required)

**Technologies**:
- Tree-sitter (multi-language parsing)
- LLM (GPT-4, Claude Opus) for semantic understanding
- Graph analysis (dependency mapping)

---

### FR-002: Incremental Spec Adoption
No big-bang requirement; start small, expand coverage.

**Mechanism**:
- Spec coverage tracking: `coverage-report.json`
- Metric: % of files/functions/modules with specs
- Dashboard: Visualize coverage (like code coverage tools)
- Goal setting: Team sets target coverage (e.g., 60% by Q2)

**Workflow**:
1. Install RaiSE Spec-Kit (bypasses greenfield checks)
2. Run `/specify.retrofit --module=auth` (single module)
3. Review/refine generated spec
4. Repeat for additional modules
5. Track coverage growth over time

---

### FR-003: Spec-Code Drift Detection
Continuous validation that implementation matches spec.

**Detection Methods**:
- **Structural Drift**: API endpoints added/removed; function signatures changed
- **Behavioral Drift**: Tests fail that previously passed; behavior diverges
- **Semantic Drift**: Code comments contradict spec; naming mismatches

**Alert Thresholds**:
- Low drift (<10% changes): Info
- Medium drift (10-30%): Warning
- High drift (>30%): Error (block merge)

**Remediation**:
- **Option 1**: Update spec (if code is correct)
- **Option 2**: Update code (if spec is correct)
- **Option 3**: Acknowledge drift (rare; intentional divergence)

**Integration**:
- Pre-commit hook: Check drift locally
- CI/CD: Validate on PR; comment with drift report
- Dashboard: Real-time drift status per spec

---

### FR-004: Multi-Repo Feature Specs
Coordinate changes across distributed repositories.

**YAML Frontmatter** (spec.md):
```yaml
---
spec_id: "feature-001-unified-auth"
repos:
  - name: "web-app"
    url: "https://github.com/org/web-app"
    paths: ["src/auth/*"]
  - name: "api-service"
    url: "https://github.com/org/api-service"
    paths: ["auth/**/*.py"]
  - name: "shared-lib"
    url: "https://github.com/org/shared-lib"
    paths: ["lib/auth.ts"]
---
```

**Cross-Repo Reference Syntax**:
```markdown
## Implementation

### Web App Changes
See: `@web-app/src/auth/login.tsx`

### API Service Changes
See: `@api-service/auth/endpoints.py`
```

**Validation**:
- Check all repos updated (PR status)
- Atomic merge (all or nothing)
- Conflict detection (overlapping changes)

**Tooling**:
- `/specify.multi-repo` command
- GitHub Actions workflow (coordinate PRs)
- Dashboard: Multi-repo feature status

---

### FR-005: Current State Spec Template
Variant template for brownfield specs.

**Sections** (different from greenfield):
- **Current Behavior**: How it works today
- **Historical Context**: Why it evolved this way
- **Technical Debt**: Known issues, shortcuts, workarounds
- **Proposed Changes**: What we're modifying (delta, not greenfield)
- **Migration Plan**: How to transition from current → target state
- **Rollback Strategy**: If changes fail, how to revert

**Emphasis**: Document reality first; propose changes second.

---

## Technical Approach

### Architecture

**Reverse Spec Generation Pipeline**:
```
Code → Parser → AST → Analyzer → LLM → Draft Spec → Human Review → Final Spec
```

**Components**:
1. **Parser**: Tree-sitter (multi-language)
2. **Analyzer**: Extract structure, dependencies
3. **LLM Agent**: GPT-4/Claude Opus (intent extraction)
4. **Template Engine**: Populate brownfield template
5. **Review UI**: Side-by-side (code ↔ spec) for refinement

---

**Drift Detection System**:
```
Spec + Code → Diff Engine → Drift Report → Alerts (CI, PR, Dashboard)
```

**Components**:
1. **Diff Engine**: Compare spec ↔ code (structural, behavioral, semantic)
2. **Scorer**: Calculate drift % (weighted by change type)
3. **Alerter**: Threshold-based notifications
4. **Dashboard**: Real-time visualization (Grafana/custom)

---

**Multi-Repo Orchestration**:
```
Feature Spec → Repo Linker → PR Coordinator → Validation Gate → Atomic Merge
```

**Components**:
1. **Repo Linker**: Parse YAML; clone/analyze multiple repos
2. **PR Coordinator**: Create linked PRs (GitHub API)
3. **Validation Gate**: Check all repos pass; dependencies satisfied
4. **Atomic Merge**: Merge all or none (transaction)

---

### Integration Points

**With Spec-Kit Core**:
- Override install checks (allow brownfield)
- Add `/specify.retrofit` command
- Template variant: `--template=brownfield`

**With CI/CD**:
- Pre-commit hook: Drift detection
- GitHub Actions: Drift report on PR
- GitLab CI: Same, adapted

**With Observable Gates (Feature 003)**:
- Telemetry: Track retrofit success rate
- Metrics: Spec coverage %, drift frequency

---

### Data Model

**Spec Coverage Report** (JSON):
```json
{
  "repo": "my-app",
  "coverage": {
    "overall": 0.42,
    "by_type": {
      "files": 0.38,
      "functions": 0.45,
      "modules": 0.50
    }
  },
  "specs": [
    {
      "spec_id": "001-auth",
      "covers": ["src/auth/*"],
      "files_covered": 12,
      "files_total": 15,
      "coverage": 0.80
    }
  ]
}
```

**Drift Report** (JSON):
```json
{
  "spec_id": "001-auth",
  "drift_score": 0.23,
  "threshold": 0.30,
  "status": "warning",
  "drifts": [
    {
      "type": "structural",
      "severity": "medium",
      "description": "New endpoint /auth/logout added without spec update",
      "file": "src/auth/endpoints.py:L42",
      "suggestion": "Add logout endpoint to spec.md#api-endpoints"
    }
  ]
}
```

---

## Implementation Plan

### Phase 1: Retrofit Foundation (Weeks 1-4)
- [ ] Bypass greenfield checks (allow install on existing projects)
- [ ] Brownfield template design (current state variant)
- [ ] Basic reverse spec generation (simple codebases)
  - [ ] Tree-sitter integration (parsing)
  - [ ] LLM integration (GPT-4/Claude)
  - [ ] Template population

**Deliverable**: `/specify.retrofit` command works on simple projects (80% success)

---

### Phase 2: Drift Detection (Weeks 5-8)
- [ ] Diff engine implementation (structural drift)
- [ ] Scoring algorithm (drift %)
- [ ] CI/CD integration (pre-commit, GitHub Actions)
- [ ] Dashboard (basic drift visualization)

**Deliverable**: Drift detection operational; alerts on PRs

---

### Phase 3: Multi-Repo Support (Weeks 9-12)
- [ ] YAML frontmatter parsing (`repos: []`)
- [ ] Cross-repo reference syntax (`@repo/path`)
- [ ] PR coordination (GitHub API)
- [ ] Validation gates (all repos pass)

**Deliverable**: Multi-repo specs functional; coordinate 2-3 repos

---

### Phase 4: Advanced Features (Ongoing)
- [ ] Improve retrofit: Handle complex codebases (microservices, monorepos)
- [ ] Behavioral drift detection (test-based, runtime monitoring)
- [ ] Semantic drift (NLP analysis)
- [ ] Coverage dashboard (visualize trends)

**Deliverable**: Enterprise-grade brownfield support

---

## Success Metrics

### Quantitative

| Metric | Baseline (Spec-Kit) | Target (RaiSE Brownfield) | Measurement |
|--------|---------------------|---------------------------|-------------|
| Installation success (brownfield) | 0% (fails) | 95% | Install attempts / successes |
| Retrofit accuracy | N/A | 80% usable w/ <30 min refinement | User survey (n=50) |
| Spec coverage adoption | 0% | Avg 40% coverage in 6 months | Coverage reports |
| Drift detection recall | N/A | 70% of real drifts caught | Manual audit vs. automated |
| Multi-repo feature coordination | 0 (unsupported) | 90% of features coordinated | User adoption rate |

---

### Qualitative

**User Feedback** (target: 85% agreement):
- [ ] "I successfully installed RaiSE Spec-Kit on my existing codebase"
- [ ] "Retrofit-generated specs saved me significant time"
- [ ] "Drift detection helps keep specs and code in sync"
- [ ] "Multi-repo specs simplified feature coordination"

**Case Studies** (target: 3 by Month 6):
1. Enterprise SaaS: Multi-repo microservices coordination
2. Fintech: Legacy monolith retrofit success
3. Startup: Incremental adoption alongside active development

---

## Risks & Mitigations

### Risk 1: Retrofit Accuracy Low
**Mitigation**: Set expectations (draft, not final); human review required; continuous improvement via telemetry

### Risk 2: Drift Detection False Positives
**Mitigation**: Tunable thresholds; whitelist intentional drifts; user feedback loop

### Risk 3: Multi-Repo Complexity
**Mitigation**: Start simple (2 repos); iterative complexity; clear error messages

### Risk 4: Performance (Large Codebases)
**Mitigation**: Incremental analysis (module-by-module); caching; async processing

---

## References

[^1]: EPAM. (2026). How to use spec-driven development for brownfield code exploration? https://www.epam.com/insights/ai/blogs/using-spec-kit-for-brownfield-codebase

---

**Related Features**:
- Feature 001: Lean Specification (brownfield specs should be lean)
- Feature 003: Observable Gates (track retrofit success, drift frequency)
- Feature 010: Spec Evolution (brownfield requires versioning)

**Status**: Specification Complete
**Next Steps**: Prototype retrofit on 3 diverse codebases (Python, TypeScript, Java)
