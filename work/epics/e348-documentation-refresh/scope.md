---
epic_id: "E348"
title: "Documentation Refresh"
status: "in-progress"
created: "2026-03-05"
backlog_key: "RAISE-348"
---

# E348: Documentation Refresh

## Objective

Bring all user, developer, and agent documentation up to date through v2.2. Three audiences: users (install + use), developers (extend + contribute), AI agents (discover + consume). Shipping pre-requisite — no release without current docs.

## Research

Evidence catalog: `work/research/e348-documentation-practices/`
- Diataxis framework as organizing taxonomy (HIGH confidence, 5 sources)
- llms.txt as AI entry point (HIGH confidence, 7 sources)
- pyOpenSci minimum viable doc set (HIGH confidence, 3 sources)
- uv (Astral) as exemplar structure (Very High evidence)

## Current State (Gemba)

**Exists and is reasonable:**
- Astro doc site (en/es) with Diataxis-aligned structure
- Getting Started, Concepts (4), Guides (2), CLI Reference (partial)
- README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE, CHANGELOG.md

**Gaps:**
- CLI Reference covers ~40% of commands (missing: graph, backlog, docs, doctor, gate, adapter, artifact, mcp, pattern, signal, publish)
- Zero developer/extension documentation (adapters, MCP, skills, hooks)
- No llms.txt
- AGENTS.md is a placeholder
- Docs don't reflect v2.2 features

## In Scope

- Complete CLI reference for all v2.2 commands
- Developer extension guides: adapters, MCP servers, skills, hooks
- llms.txt + AGENTS.md for AI agent consumption
- README refresh with current feature set
- Validate all docs against actual CLI behavior

## Out of Scope

- MkDocs migration (Astro site already exists and works)
- API reference auto-generation (mkdocstrings — separate effort)
- Video tutorials or interactive content
- Confluence publishing automation (RAISE-433)
- Internal module documentation (covered by /rai-discover)
- Spanish translations for new content (follow-up)

## Stories

| ID | Name | Size | Depends On | Description |
|----|------|------|------------|-------------|
| S348.1 | Documentation audit | XS | — | Systematic gap analysis: current vs needed, per Diataxis type |
| S348.2 | CLI reference completion | M | S348.1 | Document all missing commands: graph, backlog, docs, doctor, gate, adapter, artifact, mcp, pattern, signal, publish, release |
| S348.3 | llms.txt + AGENTS.md | S | S348.1 | Create llms.txt index per spec, expand AGENTS.md with extension patterns |
| S348.4 | Developer extension guides | M | S348.2 | How-to guides: create adapter, register MCP server, create skill, wire hook |
| S348.5 | README + community files refresh | S | S348.2 | Update README for v2.2, review CONTRIBUTING.md, verify CHANGELOG |
| S348.6 | Docs validation + cross-links | S | S348.2, S348.4 | Validate all docs against actual CLI, fix broken links, ensure self-contained pages |

## Done Criteria

- [ ] All `rai` CLI commands documented with flags, options, examples
- [ ] Developer guides for 4 extension points (adapter, MCP, skill, hook)
- [ ] llms.txt indexes all documentation pages
- [ ] AGENTS.md provides useful cross-agent context
- [ ] README accurately describes v2.2 feature set
- [ ] All docs validated against actual CLI behavior (no stale examples)
- [ ] Pages are self-contained and <5000 chars where practical (agent-friendly)
- [ ] Retrospective complete

## Implementation Plan

### Sequence

| # | Story | Size | Rationale | Enables |
|---|-------|------|-----------|---------|
| 1 | S348.1: Documentation audit | XS | Quick win — maps all gaps, informs every other story | All stories |
| 2 | S348.2: CLI reference completion | M | Critical path — biggest content gap, most value per effort | S348.4, S348.5, S348.6 |
| 2' | S348.3: llms.txt + AGENTS.md | S | **Parallel with S348.2** — only needs audit output, not CLI ref | S348.6 |
| 3 | S348.4: Developer extension guides | M | Depends on CLI ref for cross-links to commands | S348.6 |
| 3' | S348.5: README + community files | S | **Parallel with S348.4** — depends on CLI ref for feature list | S348.6 |
| 4 | S348.6: Docs validation | S | Final — validates everything, fixes cross-links | Epic close |

### Critical Path

```
S348.1 → S348.2 → S348.4 → S348.6
```

### Parallel Streams

```
Stream A:  S348.1 → S348.2 → S348.4 ──→ S348.6
                  ↘                   ↗
Stream B:          S348.3    S348.5 ─┘
```

### Milestones

**M1: Reference Foundation** (after S348.1 + S348.2 + S348.3)
- All CLI commands documented
- llms.txt indexes docs
- Success: `rai --help` output matches docs for every command

**M2: Feature Complete** (after S348.4 + S348.5)
- Extension guides for 4 extension points
- README reflects v2.2
- Success: New developer can find how to extend RaiSE using only docs

**M3: Epic Complete** (after S348.6)
- All docs validated against actual CLI
- Cross-links verified, pages self-contained
- Retrospective complete
- Success: All done criteria met

### Progress Tracking

| # | Story | Status | Actual Size | Notes |
|---|-------|--------|-------------|-------|
| 1 | S348.1: Documentation audit | Done | XS | Gap analysis complete; removed work/docs/ redundancy |
| 2 | S348.2: CLI reference completion | Done | M | 17 command group pages, 72 subcommands documented |
| 2' | S348.3: llms.txt + AGENTS.md | Done | S | llms.txt created, AGENTS.md rewritten from placeholder |
| 3 | S348.4: Developer extension guides | Done | M | 5 guide pages (extending, adapter, skill, mcp, hook) |
| 3' | S348.5: README + community files | Done | S | Version, URLs, branch model, skill count fixed |
| 4 | S348.6: Docs validation | Done | S | All rai memory refs replaced, 66 pages build clean |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CLI behavior changes during doc writing | Medium | Medium | Write docs from `--help` output + actual execution, not memory |
| Extension point APIs not stable enough to document | Low | High | Add "alpha — may change" notice; document current behavior |
| Scope creep into tutorials/explanations | Medium | Low | Strict Diataxis typing: this epic is reference + how-to only |
