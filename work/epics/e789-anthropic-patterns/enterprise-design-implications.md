# Enterprise Design Implications — Derived from S789.1 Research

> How the Anthropic/RaiSE divergence analysis informs the enterprise edition design.
> Source: s789.1-research.md
> Date: 2026-03-27

---

## Core Insight

RaiSE OSS and RaiSE Enterprise serve fundamentally different users:

| | RaiSE OSS | RaiSE Enterprise |
|-|-----------|-----------------|
| **User profile** | Developer building discipline from scratch | Engineering org with established teams, needing governance at scale |
| **Trust mode** | Building trust through structure | Verifying trust through audit |
| **Process role** | Scaffold (learn the discipline) | Guardrail (enforce the discipline) |
| **AI autonomy** | Conservative (HITL gates, full ceremony) | Higher (automated evaluation, scaled effort) |
| **Memory scope** | Per-project, per-developer | Cross-team, cross-repo, organizational |

**Consequence:** Anthropic's patterns — which assume mature engineering discipline — map more directly to the enterprise edition than to OSS. This is not a contradiction; it's market segmentation encoded in the architecture.

---

## The Four Divergences, Enterprise-Translated

### 1. Simplicity vs Discipline → Enterprise gets scaled effort

**OSS position:** Full gates always, ceremony scales with size (refined after research).
**Enterprise position:** Explicitly configurable effort profiles by story type, team maturity, and organizational risk level.

**Enterprise feature implication:**
- `effort_profile` per team or project, defined in org cartridge
- Profiles: `strict` (full ceremony, for juniors/regulated domains), `standard` (current OSS), `lean` (Anthropic-style, for senior teams)
- Gate configuration per profile — some gates waived for senior-flagged teams
- Audit trail of which profile was applied and why (observability requirement)

**Why this belongs in enterprise:** An org with 500 developers needs to calibrate discipline differently for their lead architects vs. their junior contractors. OSS treats everyone as "still building the muscle." Enterprise needs the full spectrum.

---

### 2. Agent as Tool vs Rai as Entity → Enterprise gets specialized agents

**OSS position:** Rai is a unified entity with persistent identity. One Rai per project.
**Enterprise position:** Role-specialized agents (Critic, Architect, Security Reviewer) operating within the Rai identity framework, orchestrated by an enterprise orchestrator.

**Enterprise feature implication:**
- Enterprise cartridges can define specialized skill sets per role (`security-review.cartridge`, `architecture-review.cartridge`)
- Specialized agents inherit Rai's core identity (values, boundaries) but have domain-specific knowledge and tools
- Orchestrator-worker model for multi-team coordination (Anthropic Art.6 pattern — 1 agent for simple, 10+ for complex research)
- Multi-repo knowledge graph federates memory across teams without losing per-project isolation

**Why this belongs in enterprise:** A single Rai entity per developer is the right model for OSS. An org needs specialized agents that collaborate — a security reviewer Rai, an architecture Rai, a compliance Rai — all sharing organizational memory but with distinct roles.

**Key constraint:** Specialized agents must NOT violate P1 (Humans Define). Orchestration between agents is acceptable; agents defining what humans should build is not.

---

### 3. HITL Gates vs Automated Evaluation → Enterprise gets LLM-as-judge

**OSS position:** HITL Default — pause after significant work for human review. All quality gates are human-confirmed checkpoints.
**Enterprise position:** Automated evaluation loops for mechanical verification (code quality, test coverage, style compliance), human gates reserved for judgment-requiring decisions (architecture, scope, business logic).

**Enterprise feature implication:**
- `rai gate check --auto` mode: runs LLM-as-judge for code quality, style, coverage (Anthropic's rubric model)
- Scoring output (0.0-1.0 per dimension) instead of binary pass/fail
- Iterative loop for auto-fixable issues (linting, formatting, type errors) — human gate only for verdict disagreements
- Evaluation corpus: 20+ canonical scenarios per skill type for regression testing agent behavior
- Production tracing: step-level agent decision logs for post-incident diagnosis

**Why this belongs in enterprise:** At 500 developer scale, HITL for every gate is a bottleneck. Enterprise needs automated evaluation that scales. OSS needs the discipline of human review at every step. The mechanism (LLM-as-judge) is the same; the policy (when to invoke it automatically) is the differentiator.

**Preserved from OSS:** Human gates remain at: architecture decisions, epic scope changes, production deployments, security reviews. Automation covers the mechanical, not the judgmental.

---

### 4. Process as Governance → Enterprise gets governance telemetry

**OSS position:** Governance as Code — policies versioned in git, local JSONL telemetry, audit trail through commits.
**Enterprise position:** Governance as Observable Infrastructure — real-time dashboards, org-level adoption metrics, drift detection, compliance reporting.

**Enterprise feature implication:**
- Org-level telemetry aggregation (individual JSONL → org-level events stream)
- Dashboards: gate pass rates by team, pattern adoption velocity, skill usage heatmaps
- Drift detection: alert when a team's gate compliance drops below threshold
- Compliance reporting: automated evidence export for ISO 27001, SOC2 (extends E479)
- Adoption metrics: which skills used most/least, where process breaks down
- ROI calculation: story cycle time before/after RaiSE, defect rates, rework frequency

**Why this belongs in enterprise:** The GTM says "governance as a byproduct of work." In enterprise, the byproduct needs to be *visible to buyers*. Saira at Coppel doesn't run `git log` to see governance compliance — she needs a dashboard. This is the proof point that converts enterprise pilots to contracts.

---

## Proposed Enterprise Epic Structure

Based on these implications, the enterprise edition (referenced in GTM as E9) should be structured as:

### E9-A: Enterprise Effort Scaling & Profiles
Configurable ceremony profiles per team/maturity. Gates always, ceremony varies.
- Size: M
- Dependency: S789.1 (RAISE-797 — rule #3 refinement must ship first in OSS)
- Key stories: Effort profile config, per-team skill set assignment, profile audit trail

### E9-B: Specialized Agent Roles via Cartridges
Security reviewer, architecture reviewer, compliance checker as domain cartridges.
- Size: L
- Dependency: RAISE-650 (Domain Cartridges — the runtime must exist first)
- Key stories: Security cartridge, architecture cartridge, multi-cartridge orchestration

### E9-C: Automated Evaluation & LLM-as-Judge
Scoring rubrics, evaluation corpus, iterative auto-fix loops, production tracing.
- Size: L
- Dependency: None (can start after OSS evaluation baseline)
- Key stories: Rubric definition, LLM-as-judge integration, evaluation corpus, tracing infrastructure

### E9-D: Governance Telemetry & Dashboards
Org-level aggregation, drift detection, compliance reporting, ROI metrics.
- Size: XL
- Dependency: E9-C (need evaluation data to feed dashboards)
- Key stories: Aggregation pipeline, dashboard UI, compliance export, adoption metrics

---

## What Should NOT Move to Enterprise

These stay in OSS regardless of enterprise:

| Feature | Why OSS | Risk if Enterprise-only |
|---------|---------|------------------------|
| Quality gates (all 9) | Core discipline, must be free | Enterprise-only gates = governance as paywall |
| Memory (patterns, journal, graph) | The moat — must be accessible | Locking memory = locking the learning |
| Full skill cycle | Discipline scaffold | Enterprise-only skills = OSS is toy |
| HITL gates | Trust mechanism | Automating trust = selling false safety |
| Identity (values, boundaries) | Rai's essence | Can't be pro-only feature |

---

## Timeline Recommendation

| Phase | What | When |
|-------|------|------|
| Now (2.4.0) | RAISE-794 (context policy), RAISE-797 (rule #3) | This sprint |
| Next (2.4.0) | RAISE-795 (scope fence), RAISE-796 (test guide) | Next sprint |
| Q2 2026 | RAISE-650 (Domain Cartridges) — enterprise foundation | Before E9 |
| H1 2026 | E9-C (Automated Evaluation) — highest value enterprise feature | After 650 |
| H2 2026 | E9-B (Specialized Roles), E9-D (Governance Telemetry) | After Coppel pilot |

---

*Derived from S789.1 research. Informs E9 enterprise epic design.*
*Next step: Share with Eduardo and Gerardo before formalizing E9 structure.*
