---
name: rai-research
description: "Research pipeline entry point. Routes to /rai-research-run (adaptive pipeline with depth-based phase selection)."

allowed-tools:
  - Skill

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public

---

# Research

## Purpose

Conduct epistemologically rigorous research to inform decisions. Entry point that delegates to the adaptive research pipeline.

## v3 Architecture

Research is a **pipeline with conditional phases**. The Frame phase determines depth (quick/standard/deep) and subsequent phases are routed accordingly:

| Phase | quick | standard | deep | Purpose |
|-------|:-----:|:--------:|:----:|---------|
| Frame | yes | yes | yes | Define question, determine depth |
| Scope | — | yes | yes | Decompose into divergent search angles |
| Search | yes | yes | yes | Execute searches (scales internally) |
| Evidence | — | yes | yes | Merge, dedup, catalog with evidence levels |
| Verify | — | — | yes | Adversarial refutation of major claims |
| Critic | — | — | yes | Completeness audit, targeted re-search |
| Synthesize | yes | yes | yes | Final report with recommendations |

**Depth selection:**

| Depth | Sources | Phases | Use when |
|-------|---------|--------|----------|
| quick | 5-10 | 3 | Low-stakes, familiar domains |
| standard | 15-30 | 5 | ADRs, technology evaluation |
| deep | 50-100+ | 7 | Strategic decisions, unfamiliar domains |

## Usage

Invoke the pipeline orchestrator:

```
/rai-research-run {question} [depth=quick|standard|deep]
```

Or start via pipeline CLI:

```bash
rai pipeline start research --issue-id {topic}
```

## Epistemological Principles

These apply across all depths:
- **Falsifiability** — questions must be specific and falsifiable
- **Triangulation** — 3+ independent sources per major claim
- **Source hierarchy** — primary > secondary > tertiary
- **Contrary evidence** — always acknowledged, never hidden
- **No false consensus** — single-source findings never presented as consensus

## Tooling

| Tool | API | Free tier |
|------|-----|-----------|
| Tavily | `api.tavily.com` via `$TAVILY_API_KEY` | 1000 credits/month |
| Brave Search | `api.search.brave.com` via `$BRAVE_API_KEY` | 2000 queries/month |
| ddgr | CLI, no API key | Unlimited |
| WebSearch | Built-in | Built-in |
| WebFetch | Built-in | Built-in |

## Output

| Item | Destination |
|------|-------------|
| Report | `work/research/{topic}/{topic}-report.md` |
| Evidence catalog | `work/research/{topic}/sources/evidence-catalog.md` |
| Navigation | `work/research/{topic}/README.md` |
| Next | ADR, backlog item, or parking lot update |

## References

- Pipeline definition: `.raise/pipelines/research.yaml`
- Orchestrator: `/rai-research-run`
- Phase skills: `/rai-research-{frame,scope,search,evidence,verify,critic,synthesize}`
- Research prompt template: `references/research-prompt-template.md`
