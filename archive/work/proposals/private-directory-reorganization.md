# Proposal: .private Directory Reorganization

> Aligning `.private/` contents with the Three-Directory Model (ADR-011)

---

## Current State Analysis

### `.private/decisions/` - Technical Implementation ADRs

**Contents:** 12 ADRs about technical implementation decisions
- adr-001: Python CLI
- adr-002: Git distribution
- adr-003: MCP protocol
- adr-004: Markdown/JSON formats
- adr-005: Local-first architecture
- adr-006/006a: Validation Gates
- adr-007: Guardrails
- adr-008: Observable Workflow
- adr-009: ShuHaRi Hybrid
- adr-010: CLI Ontology
- adr-011: Hybrid Kata/Template/Gate
- adr-012: spec-kit command consolidation

**Analysis:** These are **different** from `framework/decisions/` ADRs. The framework ADRs cover methodology/ontology decisions. These cover technical implementation architecture.

**Recommendation:** → `framework/decisions/technical/`

| Reason | Rationale |
|--------|-----------|
| Public value | These decisions inform CLI/tooling implementers |
| Framework scope | Technical architecture IS part of the framework |
| No sensitivity | Nothing proprietary here |

---

### `.private/business/` - Business Documents

**Contents:**
- `business-model.md` - RaiSE business model
- `market-context.md` - Market analysis
- `stakeholder-map.md` - Stakeholder mapping

**Analysis:** Sensitive business strategy documents.

**Recommendation:** → **Keep in `.private/business/`**

| Reason | Rationale |
|--------|-----------|
| Competitive sensitivity | Business model details are proprietary |
| Not framework content | Business docs ≠ framework specification |

---

### `.private/planning/` - Internal Planning

**Contents:**
- `current-state.md` - Project status (outdated Dec 2025)
- `roadmap.md` - Development roadmap
- `roadmap-tech-legacy.md` - Legacy tech roadmap
- `roadmap-tech-mvp.md` - MVP tech roadmap

**Analysis:** Planning documents, some outdated.

**Recommendation:** Split
- Active roadmap → `work/proposals/roadmap.md`
- Outdated state docs → `archive/planning/`

---

### `.private/work-artifacts/` - Development Artifacts

**Contents:**
- `dependencies-blockers.md` - Dependency tracking
- `issues-decisions.md` - Issue log
- `ontology-backlog.md` - Ontology work backlog
- `session-log.md` - Session history

**Analysis:** Work-in-progress tracking artifacts.

**Recommendation:** → `work/tracking/`

| Reason | Rationale |
|--------|-----------|
| Work directory purpose | These ARE work artifacts |
| Useful context | Agents can use for continuity |

---

### `.private/tools/` - Internal Tooling

**Contents:**
- `cursor-rules/` - Cursor rules templates
- `kata-L0-validacion-ontologica-v2.md` - Validation kata
- `kata-refinamiento-ontologico.md` - Refinement kata
- `kata-shuhari-schema-v2.1.md` - ShuHaRi schema kata
- `PROMPT-CONTINUACION-P2.md` - Continuation prompt
- `prompt-esceptico-informado-raise.md` - Skeptic prompt
- `prompt-procesar-transcript.md` - Transcript processing prompt

**Analysis:** Mix of prompts and validation tools.

**Recommendation:** Split
- Prompts → `dev/prompts/`
- Validation katas → `.raise/katas/meta/` (katas about katas)
- Cursor rules → `archive/tools/cursor-rules/` (if deprecated)

---

### `.private/agents/` - Agent Configurations

**Contents:**
- `current/` - 7 active agent XML prompts (SAR, Rules Engineer, Kata Architect, etc.)
- `agent-engineer/` - Agent engineering docs
- `cursor-rules-engineer/` - Rules engineering agent
- `documentation-engineer/` - Docs agent
- `raise-architect/` - Architect agent prompts
- `raise-coder/` - Coder agent
- `raise-tech-lead/` - Tech lead agent
- `transcript-analyst/` - Transcript analysis agent
- `agent-spec-gpt-5.1-codex.yaml` - Agent spec

**Analysis:** Rich collection of agent prompts - framework value!

**Recommendation:** Split by status
- Active agents (`current/`) → `.raise/agents/`
- Agent development docs → `dev/agents/`
- Historical/experimental → `archive/agents/`

---

### `.private/research/` - Research Notes

**Contents:**
- `raise-literature-review-v1.md` - Literature review
- `raise-research-backlog-v1.md` - Research backlog
- `Skills y Comandos como Prompts.md` - Skills research

**Analysis:** Research artifacts with framework value.

**Recommendation:** → `work/research/foundations/`

| Reason | Rationale |
|--------|-----------|
| Research continuity | Preserves research context |
| Framework evolution | Informs future decisions |

---

### `.private/reports/` - Validation Reports

**Contents:**
- `adr-010-impact-analysis.md` - Impact analysis
- `VALIDATION-REPORT-ADR-010.md` - Validation report
- `raise-ontology-validation-report.md` - Ontology validation

**Analysis:** Validation artifacts with potential framework value.

**Recommendation:** Split
- Methodology reports → `work/analysis/validations/`
- ADR-specific reports → Stay with ADR in `framework/decisions/technical/`

---

### `.private/archive/` - Historical Content

**Contents:**
- `legacy-katas/` - 40+ katas using old L0-L3 naming
- `v1-framework/` - Original v1.x framework (constitution, vision, methodology, research PDFs)

**Analysis:** Historical artifacts already archived.

**Recommendation:** → `archive/private-legacy/`

| Reason | Rationale |
|--------|-----------|
| Consolidate archives | One archive location |
| Preserve history | Valuable for archaeology |

---

## Proposed Migration Plan

### Phase 1: Framework Decisions (High Value, Safe)

```bash
# Create technical decisions directory
mkdir -p framework/decisions/technical

# Move technical ADRs
mv .private/decisions/*.md framework/decisions/technical/
```

### Phase 2: Agent Configurations (High Value)

```bash
# Move active agents to .raise
mv .private/agents/current/*.xml .raise/agents/

# Move agent development to dev
mkdir -p dev/agents
mv .private/agents/agent-engineer dev/agents/
mv .private/agents/cursor-rules-engineer dev/agents/
# ... etc

# Archive experimental
mv .private/agents/transcript-analyst archive/agents/
```

### Phase 3: Work Artifacts (Medium Value)

```bash
# Create tracking directory
mkdir -p work/tracking

# Move work artifacts
mv .private/work-artifacts/*.md work/tracking/

# Move research
mv .private/research/*.md work/research/foundations/
```

### Phase 4: Tools and Prompts (Medium Value)

```bash
# Move prompts to dev
mkdir -p dev/prompts
mv .private/tools/prompt-*.md dev/prompts/
mv .private/tools/PROMPT-*.md dev/prompts/

# Move validation katas to .raise
mkdir -p .raise/katas/meta
mv .private/tools/kata-*.md .raise/katas/meta/
```

### Phase 5: Archive Consolidation (Cleanup)

```bash
# Move legacy archive
mv .private/archive/legacy-katas archive/private-legacy-katas
mv .private/archive/v1-framework archive/private-v1-framework

# Move outdated planning
mkdir -p archive/planning
mv .private/planning/current-state.md archive/planning/
mv .private/planning/roadmap-tech-legacy.md archive/planning/
```

### Phase 6: Keep in .private (Sensitive)

The following remain in `.private/`:
- `business/` - Business strategy (sensitive)
- `planning/roadmap.md` - If still active
- `planning/roadmap-tech-mvp.md` - If still active

---

## Final Structure After Migration

```
.private/                          # Truly private content only
├── business/                      # Business strategy (sensitive)
│   ├── business-model.md
│   ├── market-context.md
│   └── stakeholder-map.md
└── README.md

framework/decisions/
├── technical/                     # NEW: Technical implementation ADRs
│   ├── adr-000-index.md
│   ├── adr-001-python-cli.md
│   └── ... (12 files)
└── (existing methodology ADRs)

.raise/
├── agents/                        # Active agent prompts
│   ├── raise-sar-agent.xml
│   ├── raise-rules-engineer.xml
│   └── ...
└── katas/
    └── meta/                      # NEW: Katas about katas
        ├── kata-validacion-ontologica.md
        └── kata-shuhari-schema.md

dev/
├── agents/                        # Agent development
│   ├── agent-engineer/
│   └── cursor-rules-engineer/
└── prompts/                       # Internal prompts
    ├── prompt-esceptico.md
    └── prompt-transcript.md

work/
├── tracking/                      # NEW: Development tracking
│   ├── ontology-backlog.md
│   ├── session-log.md
│   └── issues-decisions.md
└── research/
    └── foundations/               # NEW: Foundational research
        ├── raise-literature-review.md
        └── raise-research-backlog.md

archive/
├── private-legacy-katas/          # From .private/archive/legacy-katas
├── private-v1-framework/          # From .private/archive/v1-framework
├── agents/                        # Experimental agents
└── planning/                      # Outdated planning docs
```

---

## Decision Required

1. **Proceed with full migration?**
2. **Keep technical ADRs private?** (I recommend making public)
3. **Which agents are "active" vs "experimental"?**
4. **Any business docs safe to publicize?**

---

*Proposal created: 2026-01-30*
*Related: ADR-011 Three-Directory Model*
