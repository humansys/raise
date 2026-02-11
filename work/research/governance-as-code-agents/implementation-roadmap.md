# Governance-as-Code Implementation Roadmap

**Document ID**: ROADMAP-GOV-001
**Date**: 2026-01-29
**Status**: Draft
**Version**: 1.0.0
**Related**:
- Research: `governance-patterns-research.md`
- Specification: `policy-dsl-specification.md`

---

## Executive Summary

This roadmap translates governance-as-code research into actionable implementation phases for the RaiSE Kata Harness. The MVP (Phase 1) delivers deterministic policy enforcement in 4 weeks, proving the concept with 3 katas (Discovery, Vision, Tech Design).

**Key Milestones**:
- **Week 1-2**: Policy DSL + Basic Engine
- **Week 3**: Pre-execution Gates
- **Week 4**: Post-execution Gates (YAML-based)
- **Week 5-8**: Observability & Telemetry (Phase 2)
- **Week 9-12**: Runtime Monitoring (Phase 3)

**Success Criteria**: User runs `/raise.1.discovery`, pre-gate checks preconditions (deterministic), kata executes, post-gate validates output (deterministic), errors include actionable recovery guidance.

---

## Phase 1: MVP (Weeks 1-4)

**Goal**: Prove policy-as-code concept with basic enforcement.

### Week 1: Foundation

#### 1.1 Policy DSL JSON Schema (Day 1-2)

**Deliverable**: `.raise/schemas/policy-schema.json`

**Task List**:
- [ ] Define JSON Schema for policy YAML (based on `policy-dsl-specification.md` Section 2.4)
- [ ] Add schema validation to policy loader
- [ ] Create CLI: `rai policy validate <policy.yaml>`
- [ ] Write unit tests for schema validation (10 test cases: valid, invalid field, missing required, etc.)

**Acceptance Criteria**:
- Schema file exists at `.raise/schemas/policy-schema.json`
- CLI validates YAML against schema, displays clear errors
- Tests pass: `pytest tests/policy_engine/test_schema_validation.py`

**Dependencies**: None

---

#### 1.2 Policy Engine Core (Day 3-5)

**Deliverable**: `raise/policy_engine/` module

**Task List**:
- [ ] Create `policy_engine/` package structure:
  ```
  raise/policy_engine/
  ├── __init__.py
  ├── loader.py         # Load policy YAML, validate schema
  ├── executor.py       # Execute checks, collect results
  ├── validators/       # Built-in validators
  │   ├── __init__.py
  │   ├── base.py       # Validator ABC, ValidationResult
  │   └── registry.py   # VALIDATOR_REGISTRY
  └── models.py         # Policy, Check, OnFailConfig dataclasses
  ```
- [ ] Implement `Policy` dataclass (mirrors YAML structure)
- [ ] Implement `PolicyLoader` (parse YAML, validate schema, return Policy object)
- [ ] Implement `PolicyExecutor` (run checks, collect results)
- [ ] Write unit tests for each module

**Acceptance Criteria**:
- Can load policy YAML into Policy object
- Can execute empty policy (no checks) without error
- Tests pass: `pytest tests/policy_engine/`

**Dependencies**: 1.1 (schema)

---

### Week 2: Built-In Validators

#### 2.1 Implement 5 Core Validators (Day 1-3)

**Deliverables**:
- `raise/policy_engine/validators/file_exists.py`
- `raise/policy_engine/validators/file_exists_any.py`
- `raise/policy_engine/validators/frontmatter_valid.py`
- `raise/policy_engine/validators/section_present.py`
- `raise/policy_engine/validators/count.py`

**Task List** (per validator):
- [ ] Implement validator class (inherit from `Validator`)
- [ ] Write unit tests (5+ test cases per validator: pass, fail, edge cases)
- [ ] Register validator in `VALIDATOR_REGISTRY`
- [ ] Document validator in `policy-dsl-specification.md` Section 3

**Example Test Cases** (file_exists):
- File exists → PASS
- File missing → FAIL
- Path is directory (not file) → FAIL
- Relative path resolution → PASS
- Symlink to existing file → PASS

**Acceptance Criteria**:
- All 5 validators implemented
- Tests pass: `pytest tests/policy_engine/validators/`
- Can execute policy with all 5 validator types

**Dependencies**: 1.2 (policy engine core)

---

#### 2.2 Markdown Parsing Utility (Day 4-5)

**Deliverable**: `raise/policy_engine/utils/markdown_parser.py`

**Purpose**: Parse Markdown AST for `section_present`, `count`, `pattern_match_all` validators.

**Task List**:
- [ ] Choose Markdown parser library (`mistune` or `markdown-it-py`)
- [ ] Implement `MarkdownParser` class:
  - `parse(file_path)` → AST
  - `find_section(heading)` → Section node
  - `count_items(selector)` → int
  - `extract_frontmatter()` → dict
- [ ] Write unit tests (10+ cases with sample Markdown files)

**Acceptance Criteria**:
- Can parse Markdown to AST
- Can find sections by heading
- Can count list items under heading
- Tests pass: `pytest tests/policy_engine/utils/test_markdown_parser.py`

**Dependencies**: None (parallel with 2.1)

---

### Week 3: Pre-Execution Gates

#### 3.1 Create 3 Pre-Execution Policies (Day 1-2)

**Deliverables**:
- `.raise/policies/pre-discovery-policy.yaml`
- `.raise/policies/pre-vision-policy.yaml`
- `.raise/policies/pre-tech-design-policy.yaml`

**Task List** (per policy):
- [ ] Write policy YAML (based on `policy-dsl-specification.md` Section 4.1)
- [ ] Define preconditions (file existence, directory writable, etc.)
- [ ] Set appropriate severity levels (error vs warning)
- [ ] Write clear recovery guidance
- [ ] Validate policy: `rai policy validate <policy.yaml>`

**Example** (pre-tech-design-policy.yaml):
```yaml
policy_id: pre-tech-design-policy
policy_type: precondition_check
applies_to:
  katas: [flujo-03-tech-design]

checks:
  - check_id: PRE-001
    description: Solution Vision exists
    validator: file_exists
    params:
      path: specs/main/solution_vision.md
    severity: error
    on_fail:
      action: stop_execution
      message: "Solution Vision not found"
      recovery_guidance:
        - "Run: /raise.2.vision"
        - "Ensure gate-vision passes"
        - "Re-run: /raise.4.tech-design"
```

**Acceptance Criteria**:
- 3 policy files created
- All policies validate successfully
- Recovery guidance is actionable (user knows exactly what to do)

**Dependencies**: 2.1 (validators)

---

#### 3.2 Integrate Pre-Gates into Kata Executor (Day 3-5)

**Deliverable**: `raise/kata_executor/pre_gate_runner.py`

**Task List**:
- [ ] Create `PreGateRunner` class
- [ ] Load policy from `.raise/policies/pre-{kata-id}-policy.yaml`
- [ ] Execute all checks before kata starts
- [ ] Display results to user (PASS/FAIL/WARN)
- [ ] If error: stop execution, show recovery guidance
- [ ] If warning: log warning, allow continuation
- [ ] Write integration tests (mock kata execution)

**User Experience** (expected output):
```
User: /raise.4.tech-design

Kata Executor: Loading kata flujo-03-tech-design...
Kata Executor: Running pre-execution checks (pre-tech-design-policy)...
Kata Executor:   [❌ FAIL] PRE-001: Solution Vision exists

🛑 JIDOKA: Execution stopped due to failed precondition.

Solution Vision not found at: specs/main/solution_vision.md

🛠️  Recovery:
  1. Run: /raise.2.vision
  2. Ensure gate-vision passes
  3. Re-run: /raise.4.tech-design

Execution halted.
```

**Acceptance Criteria**:
- Pre-gate runs before kata execution
- User sees clear pass/fail/warn messages
- Errors block execution (Jidoka enforcement)
- Warnings log but allow continuation

**Dependencies**: 3.1 (pre-execution policies)

---

### Week 4: Post-Execution Gates

#### 4.1 Convert 3 Markdown Gates to YAML (Day 1-2)

**Deliverables**:
- `.raise/gates/gate-discovery.yaml`
- `.raise/gates/gate-vision.yaml`
- `.raise/gates/gate-design.yaml`

**Task List** (per gate):
- [ ] Read current Markdown gate (e.g., `.raise/gates/gate-discovery.md`)
- [ ] Extract validation criteria (checklist items)
- [ ] Map criteria to validator checks
- [ ] Write YAML gate policy (based on `policy-dsl-specification.md` Section 4.2)
- [ ] Test gate: `rai gate run gate-discovery --artifact specs/main/project_requirements.md`

**Migration Example**:

**Before** (Markdown):
```markdown
## Criterios Obligatorios
- [ ] 1. >= 5 requisitos funcionales
```

**After** (YAML):
```yaml
checks:
  - validation_id: VAL-002
    criterion: ">= 5 requisitos funcionales"
    check:
      type: count
      selector: "## Requisitos Funcionales > list items[starts-with='FR-']"
      operator: ">="
      threshold: 5
    automated: true
    severity: error
```

**Acceptance Criteria**:
- 3 YAML gates created
- Gates validate successfully: `rai policy validate gate-discovery.yaml`
- All criteria from Markdown gates mapped to YAML checks

**Dependencies**: 2.1 (validators)

---

#### 4.2 Implement Gate Runner (Day 3-5)

**Deliverable**: `raise/kata_executor/gate_runner.py`

**Task List**:
- [ ] Create `GateRunner` class
- [ ] Load gate policy from `.raise/gates/{gate-id}.yaml`
- [ ] Execute all validation checks on artifact
- [ ] Collect results (PASS/FAIL, evidence)
- [ ] Display results to user (formatted table)
- [ ] If fail: display recovery guidance, suggest fixes
- [ ] Write integration tests

**User Experience** (expected output):
```
Kata Executor: Running post-execution gate (gate-discovery)...

Validating specs/main/project_requirements.md...
  [✅ PASS] VAL-001: Frontmatter has 'titulo' field
  [✅ PASS] VAL-002: >= 5 functional requirements (found: 7)
  [❌ FAIL] VAL-003: Each requirement has acceptance criteria
    → FR-003 missing 'Criterios de Aceptación' subsection
    → FR-006 missing 'Criterios de Aceptación' subsection

Gate Result: FAIL (1 error)

🛑 JIDOKA: Fix validation errors before proceeding.

🛠️  Recovery:
  1. Add 'Criterios de Aceptación' to FR-003
  2. Add 'Criterios de Aceptación' to FR-006
  3. Re-run: raise gate run gate-discovery

Execution halted.
```

**Acceptance Criteria**:
- Gate runs after kata completes
- Results display with pass/fail/evidence
- Failures block handoff to next kata
- User sees actionable recovery guidance

**Dependencies**: 4.1 (YAML gates)

---

#### 4.3 CLI for Gate Management (Day 5)

**Deliverable**: `rai gate` CLI commands

**Task List**:
- [ ] Implement `rai gate run <gate-id>` (run gate manually)
- [ ] Implement `rai gate run-all --kata <kata-id>` (run all gates for kata)
- [ ] Implement `rai gate list` (list all gates)
- [ ] Implement `rai gate show <gate-id>` (display gate details)
- [ ] Add help text and examples
- [ ] Write CLI integration tests

**Acceptance Criteria**:
- CLI commands work as documented
- Help text is clear: `rai gate --help`
- Can run gates manually for testing

**Dependencies**: 4.2 (gate runner)

---

### Week 4: End-to-End Integration

#### 4.4 Full Kata Execution with Gates (Day 5)

**Deliverable**: Integrated kata executor with pre/post gates

**Task List**:
- [ ] Modify `/raise.1.discovery` command to use kata executor
- [ ] Executor runs pre-gate → kata → post-gate
- [ ] Test full flow: user runs `/raise.1.discovery`, gates enforce policies
- [ ] Verify Jidoka stops execution on failures
- [ ] Verify recovery guidance displays correctly

**User Experience** (expected):
```
User: /raise.1.discovery --context "E-commerce platform"

Kata Executor: Loading kata flujo-01-discovery...
Kata Executor: Running pre-execution checks (pre-discovery-policy)...
Kata Executor:   [⚠️  WARN] PRE-001: No context documents found
Kata Executor:   [✅ PASS] PRE-002: Write access to specs/main/

⚠️  Warning: No context documents found. PRD will be based solely on user input.
Continue? [Y/n] Y

Kata Executor: Starting kata execution...
[... LLM generates PRD ...]

Kata Executor: Running post-execution gate (gate-discovery)...
Kata Executor:   [✅ PASS] VAL-001: Frontmatter valid
Kata Executor:   [✅ PASS] VAL-002: >= 5 functional requirements (found: 7)
Kata Executor:   [✅ PASS] VAL-003: Acceptance criteria present

✅ Gate passed. PRD is ready.

→ Next step: /raise.2.vision (create Solution Vision from PRD)
```

**Acceptance Criteria**:
- Full kata execution works end-to-end
- Pre-gate checks preconditions
- Post-gate validates output
- Jidoka stops on errors
- Handoff suggests next kata

**Dependencies**: 3.2 (pre-gate runner), 4.2 (gate runner)

---

## Phase 2: Observability (Weeks 5-8)

**Goal**: Add telemetry, audit logging, and gate reporting.

### Week 5: Audit Logging

#### 5.1 Database Schema (Day 1-2)

**Deliverable**: PostgreSQL schema for audit logs

**Task List**:
- [ ] Design schema (tables: `kata_executions`, `gate_results`, `policy_violations`)
- [ ] Create migration script (`migrations/001_create_audit_tables.sql`)
- [ ] Implement `AuditLogger` class (insert events to DB)
- [ ] Write unit tests

**Schema**:
```sql
CREATE TABLE kata_executions (
  execution_id UUID PRIMARY KEY,
  kata_id VARCHAR(100),
  user_id_hash VARCHAR(64),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  status VARCHAR(20),  -- success, failed, stopped
  policy_version VARCHAR(20),
  metadata JSONB
);

CREATE TABLE gate_results (
  result_id UUID PRIMARY KEY,
  execution_id UUID REFERENCES kata_executions(execution_id),
  gate_id VARCHAR(100),
  gate_version VARCHAR(20),
  status VARCHAR(20),  -- pass, fail
  validations JSONB,
  timestamp TIMESTAMP
);
```

**Acceptance Criteria**:
- Schema migrations run successfully
- Can insert audit events to database
- Tests pass: `pytest tests/audit/`

---

#### 5.2 Integrate Logging into Kata Executor (Day 3-5)

**Task List**:
- [ ] Modify kata executor to log all executions
- [ ] Log pre-gate results
- [ ] Log post-gate results
- [ ] Log final status (success/fail/stopped)
- [ ] Write integration tests

**Acceptance Criteria**:
- All kata executions logged to database
- Can query logs: `SELECT * FROM kata_executions WHERE status = 'failed'`

---

### Week 6: Gate Dashboard

#### 6.1 CLI Dashboard (Day 1-3)

**Deliverable**: `rai gate report` command

**Task List**:
- [ ] Query database for gate execution stats
- [ ] Display summary (total runs, pass rate, top failures)
- [ ] Display time-series trends (daily pass rate)
- [ ] Add filters (`--since`, `--kata`, `--gate`)
- [ ] Write CLI tests

**Example Output**:
```
$ raise gate report --since 2026-01-01

Gate Execution Report (2026-01-01 to 2026-01-29)

Total Gate Runs: 45
Passed: 38 (84.4%)
Failed: 7 (15.6%)

Failed Gates:
  gate-discovery: 2 failures (10% failure rate)
  gate-design: 4 failures (20% failure rate)
  gate-backlog: 1 failure (5% failure rate)

Top Failing Checks:
  1. VAL-003 (acceptance criteria): 3 occurrences
  2. VAL-008 (architecture diagram): 2 occurrences

Recommendation: Review gate-design checks for common failure patterns.
```

**Acceptance Criteria**:
- CLI report displays stats
- Data is accurate (matches DB query)
- Filters work correctly

---

#### 6.2 Web Dashboard (Day 4-5, Optional)

**Deliverable**: Simple web UI for gate metrics

**Stack**: FastAPI (backend) + HTML/CSS/JS (frontend, no framework for MVP)

**Task List**:
- [ ] Create FastAPI app with `/api/gate-stats` endpoint
- [ ] Serve simple HTML dashboard
- [ ] Display charts (pass rate over time, top failures)
- [ ] Deploy locally (Docker container)

**Acceptance Criteria** (if implemented):
- Web dashboard accessible at `http://localhost:8000/dashboard`
- Displays real-time gate stats

**Note**: Optional for MVP. Can defer to Phase 3.

---

### Week 7: Policy Versioning

#### 7.1 Version Management (Day 1-3)

**Task List**:
- [ ] Add `compatible_kata_versions` field to policy schema
- [ ] Implement version compatibility check in policy loader
- [ ] Warn user if policy version outdated
- [ ] Implement `rai policy upgrade` command
- [ ] Write unit tests

**Example**:
```
Kata Executor: Loading policy gate-discovery-policy...
⚠️  Warning: Policy version 1.5.0 is outdated. Latest: 2.0.0
Run: raise policy upgrade gate-discovery-policy
Continuing with v1.5.0...
```

**Acceptance Criteria**:
- Version compatibility checked on policy load
- User warned if outdated
- Can upgrade policy via CLI

---

#### 7.2 Policy Changelog (Day 4-5)

**Task List**:
- [ ] Add `changelog` field to policy YAML
- [ ] Display changelog in `rai policy show <policy-id>`
- [ ] Generate changelog diff for upgrades
- [ ] Write tests

**Example**:
```
$ raise policy show gate-discovery-policy

Policy: gate-discovery-policy
Version: 2.0.0 (latest)
Type: validation_gate

Changelog:
  v2.0.0 (2026-01-29):
    - Migrated from Markdown to YAML executable format
    - Added 5 validation checks (3 error, 2 warning)
  v1.5.0 (2025-12-20):
    - Added VAL-005: Success criteria check
  v1.0.0 (2025-12-15):
    - Initial version
```

**Acceptance Criteria**:
- Changelog displayed in CLI
- Upgrade command shows changelog diff

---

### Week 8: Custom Validators

#### 8.1 Plugin System (Day 1-3)

**Task List**:
- [ ] Implement validator plugin loader (`.raise/policies/custom_validators/`)
- [ ] Document custom validator API
- [ ] Create example custom validator (`has_mermaid_diagram.py`)
- [ ] Write integration tests

**Acceptance Criteria**:
- Can load custom validators from project directory
- Custom validators work alongside built-in validators
- Documentation clear: `docs/custom-validators.md`

---

#### 8.2 Validator Testing Framework (Day 4-5)

**Task List**:
- [ ] Implement `rai validator test <validator-name>` command
- [ ] Allow validators to define test cases in YAML
- [ ] Run test cases, report pass/fail
- [ ] Write tests

**Example**:
```yaml
# .raise/policies/custom_validators/has_mermaid_diagram.test.yaml
test_cases:
  - name: "File with Mermaid diagram"
    input_file: "tests/fixtures/tech_design_with_diagram.md"
    expected: pass

  - name: "File without Mermaid diagram"
    input_file: "tests/fixtures/tech_design_no_diagram.md"
    expected: fail
```

**Acceptance Criteria**:
- Can test validators via CLI
- Test results accurate

---

## Phase 3: Runtime Monitoring (Weeks 9-12, Optional)

**Goal**: Add mid-execution monitoring (detect deviations during kata).

**Note**: This phase is advanced and can be deferred post-MVP. Requires significant instrumentation.

### Week 9-10: File Watcher

**Task List**:
- [ ] Implement file modification monitor (track file writes during kata)
- [ ] Define allowed/forbidden paths in policy
- [ ] Alert user if agent modifies file outside scope
- [ ] Write integration tests

**Deliverable**: `raise/kata_executor/runtime_monitors/file_watcher.py`

---

### Week 11: Token Budget Monitor

**Task List**:
- [ ] Instrument LLM API calls to track token usage
- [ ] Define max token budget in policy
- [ ] Alert if budget exceeded (possible runaway loop)
- [ ] Write tests

**Deliverable**: `raise/kata_executor/runtime_monitors/token_monitor.py`

---

### Week 12: Time Limit Monitor

**Task List**:
- [ ] Track kata execution time
- [ ] Define expected duration in policy
- [ ] Warn if kata taking too long
- [ ] Write tests

**Deliverable**: `raise/kata_executor/runtime_monitors/time_monitor.py`

---

## Success Metrics

### Phase 1 (MVP)

**Quantitative**:
- [ ] 3 pre-execution policies created
- [ ] 3 post-execution gates converted to YAML
- [ ] 5 built-in validators implemented
- [ ] 100% test coverage for policy engine core
- [ ] 3 katas execute with policy enforcement (Discovery, Vision, Tech Design)

**Qualitative**:
- [ ] User runs kata, sees clear pass/fail messages
- [ ] Errors include actionable recovery guidance (no ambiguity)
- [ ] Jidoka stops execution on critical failures (deterministic)
- [ ] Team agrees: "This is better than Markdown checklists"

---

### Phase 2 (Observability)

**Quantitative**:
- [ ] Audit logging implemented (all executions logged)
- [ ] Gate dashboard shows stats (pass rate, top failures)
- [ ] Policy versioning implemented (upgrade command works)
- [ ] 1 custom validator created (proof of plugin system)

**Qualitative**:
- [ ] Team uses gate report to identify patterns
- [ ] Policy upgrades smooth (no breaking user workflows)

---

### Phase 3 (Runtime Monitoring)

**Quantitative**:
- [ ] 3 runtime monitors implemented (file, token, time)
- [ ] Runtime violations detected and logged

**Qualitative**:
- [ ] Monitoring provides value (detects actual issues)
- [ ] False positive rate < 5%

---

## Risk Mitigation

### Risk 1: Policy DSL Too Complex (Users Don't Adopt)

**Likelihood**: Medium
**Impact**: High (defeats purpose if unused)

**Mitigation**:
- Start with simplest possible DSL (5 validators, basic YAML)
- Provide migration tool: `rai policy convert gate-discovery.md` (Markdown → YAML)
- Document with examples, not just reference docs
- Get feedback from 3 teams before finalizing DSL

---

### Risk 2: Performance Overhead (Gates Slow Down Workflow)

**Likelihood**: Medium
**Impact**: Medium (users skip gates if slow)

**Mitigation**:
- Benchmark validators (each must run <100ms)
- Cache policy loads (don't re-parse YAML on every run)
- Parallelize checks where possible (independent validators run concurrently)
- Add `--skip-gates` flag for development mode (opt-out, not default)

---

### Risk 3: False Positives (Gates Fail When They Shouldn't)

**Likelihood**: High (initial iterations)
**Impact**: High (trust erosion)

**Mitigation**:
- Start with warning-only mode (log failures, don't block)
- Collect data for 2 weeks, tune thresholds
- Implement override mechanism (`--override VAL-003 "Reason: legacy code"`)
- User feedback loop: `rai gate report-false-positive VAL-003`

---

### Risk 4: Validator Bugs (Incorrect Pass/Fail)

**Likelihood**: Medium
**Impact**: High (governance failure)

**Mitigation**:
- 100% test coverage for validators (5+ test cases per validator)
- Validator testing framework (users can verify validators)
- Canary deployment (roll out new validators to 1 team first)
- Validator version pinning (policy specifies validator version)

---

## Dependencies

### External Libraries

| Library | Purpose | Version | License |
|---------|---------|---------|---------|
| PyYAML | Parse policy YAML | 6.0+ | MIT |
| pydantic | Data validation (Policy models) | 2.0+ | MIT |
| mistune | Markdown parsing | 3.0+ | BSD |
| click | CLI framework | 8.0+ | BSD |
| psycopg2 | PostgreSQL driver (audit logs) | 2.9+ | LGPL |

### RaiSE Components

- **Kata files**: `.raise/katas/` (process knowledge)
- **Templates**: `.raise/templates/` (artifact templates)
- **Existing gates**: `.raise/gates/` (Markdown gates to migrate)

---

## Deployment Strategy

### Phase 1 Rollout

1. **Week 1-2**: Internal dev environment only (Emilio)
2. **Week 3**: Alpha testing with 1 external team
3. **Week 4**: Beta release to 3 teams
4. **After MVP stable**: Announce to RaiSE community

### Feedback Collection

- **Alpha**: Daily sync with test team, rapid iteration
- **Beta**: Weekly feedback survey, GitHub issues
- **GA**: Monthly retrospective, feature prioritization

---

## Next Steps (Immediate)

1. **Review this roadmap** with Emilio and RaiSE team
2. **Approve Phase 1 scope** (4 weeks, MVP features)
3. **Set up project structure**:
   ```bash
   mkdir -p raise/policy_engine/{validators,utils}
   mkdir -p .raise/{policies,gates,schemas}
   mkdir -p tests/policy_engine/{validators,integration}
   ```
4. **Create GitHub project board** (track tasks from Week 1-4)
5. **Start Week 1, Task 1.1**: Define JSON Schema for policy YAML
6. **Schedule daily standups** (async, 15min) during Phase 1

---

## Appendix: File Structure (After Phase 1)

```
raise-commons/
├── raise/
│   ├── policy_engine/
│   │   ├── __init__.py
│   │   ├── loader.py                 # Load/validate policy YAML
│   │   ├── executor.py               # Execute policy checks
│   │   ├── models.py                 # Policy, Check dataclasses
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Validator ABC
│   │   │   ├── registry.py           # VALIDATOR_REGISTRY
│   │   │   ├── file_exists.py
│   │   │   ├── file_exists_any.py
│   │   │   ├── frontmatter_valid.py
│   │   │   ├── section_present.py
│   │   │   └── count.py
│   │   └── utils/
│   │       └── markdown_parser.py    # Parse Markdown AST
│   └── kata_executor/
│       ├── __init__.py
│       ├── executor.py               # Main kata executor
│       ├── pre_gate_runner.py        # Pre-execution gates
│       └── gate_runner.py            # Post-execution gates
├── .raise/
│   ├── schemas/
│   │   └── policy-schema.json        # JSON Schema for policies
│   ├── policies/
│   │   ├── pre-discovery-policy.yaml
│   │   ├── pre-vision-policy.yaml
│   │   └── pre-tech-design-policy.yaml
│   ├── gates/
│   │   ├── gate-discovery.yaml       # YAML gates (migrated)
│   │   ├── gate-vision.yaml
│   │   └── gate-design.yaml
│   └── katas/
│       ├── flujo-01-discovery.md     # Existing katas (unchanged)
│       ├── flujo-02-solution-vision.md
│       └── flujo-03-tech-design.md
├── tests/
│   ├── policy_engine/
│   │   ├── test_loader.py
│   │   ├── test_executor.py
│   │   ├── validators/
│   │   │   ├── test_file_exists.py
│   │   │   ├── test_count.py
│   │   │   └── ...
│   │   └── integration/
│   │       └── test_full_policy_execution.py
│   └── kata_executor/
│       ├── test_pre_gate_runner.py
│       └── test_gate_runner.py
└── docs/
    ├── policy-dsl-specification.md   # Reference docs
    ├── custom-validators.md          # How to write custom validators
    └── governance-patterns-research.md
```

---

**End of Roadmap**

**Status**: Draft (pending approval)
**Next Review**: 2026-01-30 (team sync)
**Owner**: Emilio (RaiSE Framework Lead)
