# Business Case: RaiSE

> Reliable AI Software Engineering

## Executive Summary

Professional software engineering is about **evolution**, not creation. While current AI tools can vibe-code an MVP, they fail at the real work: maintaining, evolving, and governing production systems in regulated industries. RaiSE enables professional engineers to reliably evolve production systems with AI assistance, through deterministic governance and observable workflows, resulting in audit-ready software from concept to value.

**Market opportunity:** 70-80% of software development is brownfield work — ignored by current AI-assisted development tools (Spec-Kit, BMAD) which focus on greenfield. Regulated industries (financial services, telecom) require deterministic governance that "LLM said so" cannot provide.

**Recommendation:** GO — First mover advantage in governance-grade AI development for professional engineers.

---

## Oportunidad de Negocio

### Problema

AI code generation is unreliable at scale:

| Evidence | Data Point | Source |
|----------|-----------|--------|
| Security failures | **45% of AI-generated code fails security tests** | Veracode 2025 |
| XSS vulnerabilities | AI is **2.74x more likely** to introduce XSS than humans | CodeRabbit |
| Hallucinations persist | **17-33% hallucination rate** even in production RAG | Journal of Empirical Legal Studies 2025 |
| Code churn | **5.7% requires rework within 2 weeks** post-merge | GitClear 2025 |
| Stability trade-off | **7.2% decrease in delivery stability** with AI use | Google DORA 2024 |
| Productivity paradox | Devs report **+20% productivity**, actual is **-19%** | METR Study 2025 |

### Quién Sufre

- **Brownfield teams** (70-80% of all development work) — current tools ignore them
- **Tech leads and architects** — no governance enforcement, can't prove ROI
- **Regulated industries** — "LLM said so" rejected by compliance auditors

### Causas Raíz

1. **No deterministic governance** — LLMs can only be *asked* not to violate constraints, not *prevented*
2. **Context engineering immaturity** — only formalized as discipline in 2025
3. **Greenfield bias** — Spec-Kit, BMAD designed for new projects; 70-80% of work is brownfield
4. **Measurement gap** — no benchmarks for governance effectiveness

### Por Qué Ahora

- **Technical foundation ready:** ast-grep + ripgrep enable deterministic scanning; RAG reduces hallucinations 18-68%
- **Regulatory push:** EU AI Act 2025, ISO 42001 — auditors demand deterministic governance
- **Market validation:** Spec-Kit (39k stars) + BMAD (32k stars) prove demand; brownfield underserved
- **Tool maturation:** Claude Code, Cursor reaching professional-grade capability

---

## Propuesta de Valor

### Statement

> **RaiSE enables professional engineers to reliably evolve production systems with AI assistance, through deterministic governance and observable workflows, resulting in audit-ready software from concept to value.**

### Tagline

> **"From Concept to Value — a single engineer, with RaiSE and you."**

### The RaiSE Triad

```
        RaiSE Engineer
        (Human - Strategy, Judgment, Ownership)
              │
              │ orchestrates
              ▼
┌─────────────────────────────────────┐
│             RaiSE                   │
│   (Methodology + Governance)        │
│   Deterministic, Observable         │
└─────────────────────────────────────┘
              │
              │ constrains + enables
              ▼
           Claude
    (AI Partner - Execution)
```

- **RaiSE Engineer** = Professional who orchestrates AI-assisted evolution of production systems
- **RaiSE** = The governance/methodology that makes AI development trustworthy
- **"You"** = Claude (or capable LLM) — AI as partner, not replacement

### Diferenciadores (Priority Order)

| # | Differentiator | Why It Matters | vs. Competitors |
|---|----------------|----------------|-----------------|
| 1 | **Deterministic governance** | Auditors reject "LLM said so" | BMAD = prompt-based ("NEVER skip") |
| 2 | **Compliance-ready** | EU AI Act, SOC2, ISO 42001 | Neither Spec-Kit nor BMAD addresses |
| 3 | **Brownfield-native** | 70-80% of real work is evolution | Both competitors = greenfield only |

### Competitive Positioning

**New Category:** "Reliable AI Software Engineering"

- Not competing with Spec-Kit/BMAD — they serve hobbyists and greenfield
- RaiSE serves **RaiSE Engineers** — professionals in regulated industries who need audit-ready evolution
- "Even a monkey can vibe-code an MVP with current models. The real challenge is evolution."

---

## Stakeholders y Usuarios

### Usuario Primario: RaiSE Engineer

| Attribute | Description |
|-----------|-------------|
| **Profile** | Professional software engineer, 5-15 years experience |
| **Context** | Maintains/evolves production systems in any industry |
| **Pain** | AI tools are fast but unreliable; can't pass audits |
| **Need** | Governance that doesn't slow them down |
| **Goal** | Ship reliable software at AI speed |
| **Relationship** | Partner ("RaiSE and you") — collaborative, not directive |

### Usuarios Secundarios (Influencers, Not Gates)

| User | How They Benefit | Interaction |
|------|------------------|-------------|
| Tech Leads / Architects | Governance enforced automatically | Configure guardrails |
| Compliance / Audit Teams | Observable workflows provide audit trails | Consume reports |
| Security Teams | Deterministic security gates | Define security guardrails |
| Engineering Managers | Observable metrics prove ROI | Dashboard consumers |

### Modelo de Adopción

| Model | Expectation |
|-------|-------------|
| **Bottom-up** | Individual RaiSE Engineers adopt | **Primary path** |
| **Team adoption** | Small teams (2-5 devs) | **Secondary** |
| **Enterprise-wide** | Full org adoption | **Expect resistance** |

Growth comes from individual professionals → teams → maybe orgs. Enterprises will resist initially.

### Market Segments

| Segment | Priority | Rationale |
|---------|----------|-----------|
| Professional software developers | **Primary** | Any industry, real day-to-day problems |
| Financial services | High | Founder experience, highest regulation |
| Telecom | High | Regulatory rigor, large codebases |
| Healthcare | Secondary | HIPAA compliance needs |
| Enterprise SaaS | Secondary | SOC2 requirements |

---

## Constraints

| Category | Decision | Implication |
|----------|----------|-------------|
| **Team** | Small team forming (internal hires) | Real commitment, sustainable pace |
| **Funding** | Seeking external funding (ASAP) | Business Case serves dual purpose |
| **Timeline** | Active fundraising | Need demonstrable value quickly |
| **AI Platforms** | Claude + Cursor | Focused on professional market |
| **Git** | Platform-agnostic | Methodology over platform lock-in |
| **License** | MIT | Maximum adoption, enterprise-friendly |
| **SaaS** | Dashboard planned | Future SOC2/GDPR compliance needed |

### Business Model: Open Core

| Tier | Contents | Target |
|------|----------|--------|
| **Core (Free)** | Constitution, katas, basic governance | Community, adoption |
| **Enterprise (Paid)** | Advanced gates, compliance dashboard, integrations | Revenue, regulated industries |

---

## Métricas de Éxito

### Business Metrics

| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| Active projects using RaiSE | 0 | 100-500 | Year 1 |

### Product Metrics (Reliability Score)

| Metric | Industry Baseline | RaiSE Target | Improvement |
|--------|-------------------|--------------|-------------|
| Gate pass rate (1st attempt) | N/A | >80% | Establish baseline |
| Code churn (<2 weeks post-merge) | 5.7% | <3% | ~50% reduction |
| Security vulnerabilities | 45% | <15% | ~67% reduction |

### User Satisfaction

| Metric | Target | Rationale |
|--------|--------|-----------|
| NPS | >40 | Strong product-market fit indicator |

---

## Riesgos y Mitigaciones

| Risk | Category | Prob | Impact | Mitigation |
|------|----------|------|--------|------------|
| AI tools become reliable, governance unnecessary | Market | Medium | High | Multiple strategies: compliance floor, orchestration ceiling, graceful pivot |
| Solo technical capacity insufficient | Technical | High | High | AI-augmented development (dogfooding RaiSE) |
| Funding doesn't materialize | Resource | Medium | Medium | Bootstrap from humansys.ai revenue |
| Miss go-to-market timing window | Execution | Medium | High | Ship fast, iterate — Lean approach |

---

## Recomendación

**GO** — Proceed with RaiSE development.

**Rationale:**
1. Clear market gap (brownfield, governance, compliance)
2. Timing aligned with regulatory push (EU AI Act 2025)
3. Differentiated positioning (new category, not better mousetrap)
4. Founder expertise matches target market (SAFe at scale, regulated industries)
5. Fallback exists (bootstrap from humansys.ai)

---

## Aprobaciones

| Rol | Nombre | Fecha | Decisión |
|-----|--------|-------|----------|
| Founder/CEO | Emilio Osorio | | |
| | | | |

---

## Trazabilidad

| Documento | Ubicación |
|-----------|-----------|
| Research: Competitive Analysis | `work/research/` |
| Research: Layered Grounding | `work/research/outputs/layered-grounding-analysis.md` |
| Session Log | `work/research/sessions/2026-01-30-solution-discovery-kata.md` |
| Framework Vision | `framework/vision.md` |

---

*Document created: 2026-01-30*
*Kata: solution/discovery*
*Version: 1.0.0*
