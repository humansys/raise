# Epic E477: Agile HR Performance Management — Scope

> **Status:** IN PROGRESS
> **Created:** 2026-03-10
> **Partner:** Just Leading Solutions (JLS)

## Objective

Enable HR Business Partners to run continuous performance cycles using AI-governed katas, replacing annual reviews with iterative monthly check-ins, OKR tracking, and structured feedback — all configurable by JLS consultants for their clients.

**Value:** JLS gains a differentiated, AI-powered methodology platform to offer clients. HRBPs get a structured, repeatable process that makes Agile Performance Management actionable — not just theoretical.

## Stories (estimated)

| ID | Story | Size | Status | Description |
|----|-------|------|--------|-------------|
| S477.1 | Performance Domain Model | S (2) | TODO | Core data types: CheckIn, OKR, Feedback, PerformanceCycle, Participant, Agreement |
| S477.2 | Dual Prepare Skills | M (3) | TODO | `prepare-coaching-brief` (HRBP) + `prepare-check-in` (Manager) — dual-perspective 1:1 preparation |
| S477.3 | Capture & Agreements | S (2) | TODO | `capture-agreements` — post 1:1 registration with actionability validation |
| S477.4 | AI Feedback Drafting | S (2) | TODO | `draft-feedback` — context-aware, guardrail-governed feedback suggestions (manager→collaborator) |
| S477.5 | OKR Progress Analysis | S (2) | TODO | `analyze-okr-progress` — assess objectives, flag risks, suggest adjustments |
| S477.6 | Advisory Governance Gates | S (2) | TODO | Advisory gates: feedback quality, bias detection, OKR measurability, check-in frequency, agreement actionability |
| S477.7 | JLS Configuration Layer | M (3) | TODO | YAML-based config for JLS to customize cycle duration, gate mode, OKR framework, prepare options per client |

**Total: 7 stories, 16 SP estimated**

## Scope

**In scope (MUST):**
- Domain model for performance management entities (annual cycle, monthly check-ins)
- Dual prepare: coaching brief for HRBP + agenda prep for Manager
- Post check-in agreement capture with validation
- Feedback drafting with anti-bias and specificity guardrails
- OKR tracking and progress analysis
- Advisory governance gates (suggest, don't block)
- JLS-configurable YAML layer per client

**In scope (SHOULD):**
- Feedback-360 multi-source kata (future epic)
- Talent calibration kata (future epic)

**Out of scope:**
- HRIS system integration (Workday, SAP) → future epic
- Employee self-service UI → not in vision
- Compensation linkage → explicitly excluded
- Multi-language feedback analysis → separate epic
- Dashboard → premature for MVP
- SaaS product → this is a methodology toolkit, not a product

## Done Criteria

**Per story:**
- [ ] Code with type annotations (Pyright strict)
- [ ] Tests passing (pytest)
- [ ] Quality checks pass (ruff, pyright)
- [ ] Story retrospective completed

**Epic complete:**
- [ ] All stories S477.1–S477.7 complete
- [ ] JLS can configure a client performance cycle via YAML
- [ ] HRBP receives coaching brief before manager 1:1
- [ ] Manager receives prep agenda with concrete topics
- [ ] Post 1:1 agreements are captured and validated as actionable
- [ ] Governance gates run as advisory (alert, don't block)
- [ ] Epic retrospective done
- [ ] Merged to dev branch

## Dependencies

```
S477.1 (Domain Model)
  ├── S477.2 (Dual Prepare Skills)
  ├── S477.3 (Capture & Agreements)
  ├── S477.4 (Feedback Drafting)
  ├── S477.5 (OKR Analysis)
  └── S477.6 (Advisory Gates)
        └── S477.7 (JLS Config)
```

S477.1 is the foundation. S477.2–S477.6 can partially parallelize after S477.1. S477.7 depends on gates being defined.

## Architecture

### Check-in Kata Flow

```
┌─────────────────────────────────────────────────────┐
│                  MONTHLY CHECK-IN KATA               │
│                                                      │
│  PREPARE (dual)                                      │
│  ├─ HRBP: prepare-coaching-brief                     │
│  │   → context, patterns, alerts, coaching tips      │
│  └─ Manager: prepare-check-in                        │
│      → agenda, OKR review points, feedback topics    │
│                                                      │
│  CONDUCT (human — 1:1 offline, no AI)                │
│                                                      │
│  CAPTURE (AI + human)                                │
│  └─ capture-agreements                               │
│      → actions, owners, dates, OKR adjustments       │
│                                                      │
│  VALIDATE (advisory gates)                           │
│  ├─ agreement-actionability                          │
│  ├─ feedback-quality                                 │
│  ├─ bias-detection                                   │
│  ├─ okr-measurability                                │
│  └─ check-in-frequency                               │
└─────────────────────────────────────────────────────┘
```

### Skills

| Skill | Consumer | Input | Output |
|-------|----------|-------|--------|
| `prepare-coaching-brief` | HRBP | Collaborator history, OKRs, prior feedback | Coaching brief with alerts and suggestions |
| `prepare-check-in` | Manager | OKRs, last check-in agreements, pending feedback | Agenda with concrete topics |
| `capture-agreements` | Manager/HRBP | 1:1 notes | Structured agreements (action, owner, date) |
| `draft-feedback` | Manager (via HRBP) | Context, observations | Constructive feedback draft with guardrails |
| `analyze-okr-progress` | HRBP | OKR definitions, check-in data | Progress assessment, risk flags, adjustments |

### Advisory Gates

| Gate | Validates | Mode |
|------|----------|------|
| `feedback-quality` | Specificity, actionability (not generic) | Advisory |
| `bias-detection` | Gender, age, ethnicity bias in language | Advisory |
| `okr-measurability` | Key Results are quantifiable | Advisory |
| `check-in-frequency` | Monthly cadence compliance | Advisory |
| `agreement-actionability` | Has responsible, action, date | Advisory |

### JLS Configuration

```yaml
# client config example
client:
  name: "Client Name"
  industry: "Industry"
performance_cycle:
  duration: annual
  check_in_frequency: monthly
gates:
  mode: advisory
  bias_detection: true
  feedback_quality: true
  okr_measurability: true
prepare:
  coaching_brief: true
  manager_prep: true
okr:
  framework: okr        # okr | kpi | hybrid
  review_cadence: quarterly
feedback:
  type: manager_direct   # manager_direct only in v1
  language: en
```

## Risks

| Risk | L/I | Mitigation |
|------|-----|------------|
| HR domain complexity underestimated — performance management has deep org-specific variations | M/H | Start with JLS-defined "canonical" flow, make configurable in S477.7 |
| AI feedback guardrails too restrictive or too permissive | M/M | Iterative tuning with JLS HR expertise; advisory mode allows HRBP override |
| Scope creep into HRIS integration | H/M | Hard boundary: file-based data import only. No API adapters in this epic |
