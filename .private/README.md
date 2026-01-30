# Private Content

This directory contains sensitive internal content not intended for public consumption.

## Structure

| Directory | Content | Purpose |
|-----------|---------|---------|
| `business/` | Business model, market context, stakeholder map | Competitive-sensitive business documents |

## What Was Moved

As of v2.5 (ADR-011 Three-Directory Model), most content was reorganized:

| Original | New Location | Rationale |
|----------|--------------|-----------|
| `decisions/` | `dev/decisions/` | Technical implementation ADRs |
| `agents/` | `.raise/agents/` + `dev/agents/` | Framework engine + dev reference |
| `tools/` | `dev/prompts/` + `.raise/katas/meta/` | Dev tools + meta-katas |
| `work-artifacts/` | `work/tracking/` | Work in progress |
| `research/` | `work/research/foundations/` | Research artifacts |
| `reports/` | `work/analysis/validations/` | Validation reports |
| `planning/` | `work/proposals/` + `archive/planning/` | Active + archived |
| `archive/` | `archive/private-legacy-*/` | Historical content |

## Access

This content is:
- **Not** included in public documentation
- **Not** linked from README.md or public docs
- Available for internal reference only

---

*Private content managed by RaiSE team*
