---
id: "ADR-044"
title: "Rai Context Lifecycle — Distribution, Ownership & Patterns"
date: "2026-03-04"
status: "Accepted"
epic: "E350"
tracker: "RAISE-364"
---

# ADR-044: Rai Context Lifecycle — Distribution, Ownership & Patterns

## Contexto

Rai evolved organically on a single machine. As we scale to multiple developers (Sprint 4+), the context that makes Rai effective — identity, patterns, memory, skills, methodology — must be reliably distributed and kept current. No formal inventory existed of what constitutes "the Rai experience," and generated artifacts (MEMORY.md, CLAUDE.md) became stale after initial creation.

Research: `work/research/agent-context-distribution/report.md`, `work/problem-briefs/rai-experience-portability-2026-03-04.md`.

## Decisión

Four interconnected decisions:

### D1: Context Ownership — Event-driven hooks

Each CLI command leaves context clean on exit. Hooks on existing events (`GraphBuildEvent`, init lifecycle) trigger regeneration of derived artifacts. No separate `rai sync` command. `rai doctor` (RAISE-378) serves as diagnostic, not repair.

### D2: CLAUDE.md — Always generated, never hand-edited

CLAUDE.md is a derived artifact regenerated from `.raise/` canonical sources (methodology.yaml, manifest.yaml, identity/core.md). Project customization goes in `.raise/` config; per-developer overrides go in `CLAUDE.local.md`. `rai init` regenerates CLAUDE.md on every run.

### D3: Patterns — Three levels

| Level | Location | Scope | Mechanism |
|-------|----------|-------|-----------|
| Base | `src/rai_cli/patterns_base/base.jsonl` | Universal, ships with package | Curated per release, ~50 first-principles patterns |
| Project | `.raise/rai/memory/patterns.jsonl` | Team, in git | Explicit promotion via `rai pattern promote` |
| Personal | `.raise/rai/personal/patterns.jsonl` | Per-dev, not in git | Free accumulation via `rai pattern add` |

Session loads all three (base + project + personal) merged in memory. `rai pattern add` writes to personal. `rai pattern promote` moves from personal to project.

### D4: Init — Single idempotent command

`rai init` detects first-time vs existing project and acts accordingly. No separate `rai upgrade`. Uses dpkg three-hash algorithm for skills (already implemented). Shows diff preview before destructive changes.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | New dev gets full Rai experience from `git clone` + `rai init` + `rai graph build` |
| ✅ Positivo | Zero merge conflicts on patterns (personal absorbs 90% of writes) |
| ✅ Positivo | CLAUDE.md always consistent with framework — no drift |
| ✅ Positivo | Base patterns provide framework wisdom to all projects |
| ⚠️ Negativo | CLAUDE.md not freely editable (must customize via `.raise/` or `CLAUDE.local.md`) |
| ⚠️ Negativo | Pattern destillation requires manual curation effort (~2h for 727 → ~50 base) |
| ⚠️ Negativo | Three-level patterns adds conceptual complexity |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| `rai sync` command for context repair | Adds API surface; if hooks work, sync is unnecessary |
| Hybrid CLAUDE.md (generated sections + free sections) | Fragile markers, merge conflicts, ambiguous ownership |
| Two-level patterns (project + personal only) | Misses opportunity to ship framework wisdom with package |
| Separate `rai init` + `rai upgrade` | More concepts to teach; idempotent init is simpler |
| Auto-update agent context on pip install | Violates consent principle (Rai value #3: Observability IS Trust) |

---

<details>
<summary><strong>Referencias</strong></summary>

- Problem Brief: `work/problem-briefs/rai-experience-portability-2026-03-04.md`
- Research: `work/research/agent-context-distribution/report.md`
- Inventory: Agent task a97bf2de (full artifact inventory)
- dpkg three-hash: `src/rai_cli/onboarding/skill_manifest.py`
- Prior art: ESLint shareable configs, Docker layers, chezmoi three-way merge

</details>
