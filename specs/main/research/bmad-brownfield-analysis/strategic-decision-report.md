# SAR v2: Facts-First Brownfield Analysis -- Strategic Decision

**Research ID**: RES-BMAD-BFLD-001-D2
**Date**: 2026-01-27 (Updated)
**Status**: Updated -- incorporates "Facts Not Gaps" reframing, anecdotal SAR origin correction, + 1-week MVP
**Supersedes**: Original 3-option analysis (Adopt/Port/Inspire)

---

## Executive Summary

**Recommended Option**: **BUILD-FIRST (Option C redefined)** -- scoped to competitive MVP

**Critical Context**: RaiSE never had a framework-level SAR process. The existing SAR katas evaluate codebases against Clean Code and Clean Architecture principles, but this was never a deliberate framework design decision. It was an anecdotal remnant from the C#/Clean Architecture project where the SAR katas were originally developed. That project-specific lens was mistakenly generalized as "the RaiSE SAR approach."

**Why this matters for the 3-option analysis**: The original report recommended PORT (Option B) because it "preserved SAR's quality evaluation." But there is no framework-level SAR to preserve -- only a project-specific artifact. Three insights invalidate the PORT recommendation:

1. **Anecdotal Origin**: The Clean Architecture evaluation lens is not a RaiSE framework feature. It's a remnant of a specific C# engagement. Option B was trying to preserve something that was never a deliberate design choice.

2. **"Facts Not Gaps"**: Even if the Clean Architecture lens had been deliberate, it would be the wrong approach. SAR should describe what IS, not measure against what someone thinks it SHOULD BE.

3. **Existing Tooling**: The deterministic scan pipeline (ast-grep + ripgrep + bash) is already researched, selected, and specified. This eliminates the "Phase 3 is too risky" argument that ruled out INSPIRE. The tools are ready.

**Redefined Option C (BUILD-FIRST)**: We are not "taking inspiration from BMAD to improve our existing approach." We are building the first proper framework-level SAR from first principles, using BMAD as competitive benchmark and deterministic tooling as foundation. This delivers a competitive MVP in one week that beats BMAD on every dimension that matters.

**One-line thesis**: *RaiSE never had a proper SAR -- now we build one. Deterministic tools extract facts. LLM synthesizes understanding. Governance bridge produces rules. No opinions required.*

---

## Why PORT (Option B) Is No Longer Recommended

The original PORT recommendation rested on two assumptions, both now invalidated:

| Assumption | Status | Why It's Wrong |
|-----------|--------|---------------|
| "SAR's Clean Code/Architecture analysis is a core strength to preserve" | **FALSE PREMISE** | There is no framework-level SAR to preserve. The Clean Architecture evaluation was an anecdotal remnant from the C# project where SAR katas originated -- a project-specific artifact mistakenly generalized. PORT was trying to preserve something that never existed as a framework feature. |
| "Tool integration is Phase 3 risk, defer it" | **INVALIDATED** | ast-grep + ripgrep are selected, versioned, and have command specs. They ARE the MVP, not an enhancement. |

Without these, PORT becomes: "Port BMAD's operational patterns (classification, scan levels, persistence) into a paradigm that doesn't actually exist yet." Since we're building the first proper framework-level SAR, there's no target to port into -- and BMAD's patterns are inferior to what the deterministic pipeline provides natively.

| BMAD Pattern | Deterministic Pipeline Equivalent | Better? |
|-------------|----------------------------------|---------|
| CSV classification (LLM-parsed) | `tree + find + package manifest → project-profile.yaml` | Yes -- deterministic, no LLM parsing errors |
| Write-as-you-go (LLM context mgmt) | Tools extract JSON → LLM reads structured data | Yes -- LLM never reads raw source files |
| Scan levels (Quick/Deep/Exhaustive) | Tool scan depth configurable (maxdepth, file count) | Yes -- deterministic control, not LLM judgment |
| Resumability (JSON state) | Pipeline stages produce intermediate JSON files | Yes -- each stage is independently cacheable |
| Context purging | Not needed -- tool output is compact structured data | N/A -- problem eliminated |

**BMAD's patterns solved problems caused by LLM-only file reading. Tools eliminate those problems entirely.**

---

## The "Facts Not Gaps" Paradigm

### What Changes

The existing SAR katas ask: *"How well does this codebase conform to Clean Code and Clean Architecture?"* -- but this question was inherited from the C#/Clean Architecture project where SAR was first developed. It was never a framework-level design choice.
BMAD asks: *"What documentation can we generate about this codebase?"*
SAR v2 asks the first proper framework-level question: **"What are the verifiable facts about this codebase, and what governance rules can we extract from them?"**

### The Three Layers of Truth

**Layer 1: Deterministic Facts** (tools extract, 100% reproducible)
- File count, types, sizes, structure
- Import/dependency graph (ast-grep)
- Naming patterns with frequency counts (ripgrep)
- Module boundaries (directory structure)
- Configuration and entry points
- Technology stack (manifest files)

**Layer 2: LLM-Synthesized Understanding** (LLM interprets structured data)
- Architecture-as-found: "This codebase uses X pattern" (not "this violates Y pattern")
- Convention catalog: "95% of services use camelCase handlers" (observed fact)
- Internal consistency score: "Naming is 92% consistent, error handling is 61% consistent" (deviation from own norms)
- Dependency assessment: "Module A depends on Module B, but not vice versa" (graph fact)

**Layer 3: Governance Artifacts** (LLM generates from Layers 1-2)
- `.cursorrules` from discovered conventions
- Guardrails from consistency-validated patterns
- Internal inconsistencies flagged as action items (not "violations of Clean Architecture")
- Architecture constraints extracted from actual dependency graph

### What SAR v2 Leaves Behind (Anecdotal Artifacts)

The following were never framework-level features -- they were artifacts of the C#/Clean Architecture project where SAR katas originated. SAR v2 does not carry them forward:

- No Clean Code evaluation (project-specific, never a framework decision)
- No Clean Architecture compliance check (project-specific, never a framework decision)
- No "refactoring recommendations based on SOLID principles" (opinionated)
- No opinionated quality scores (no external standard assumed)
- No assumed architectural style (SAR v2 discovers what IS)

### What's New in SAR v2

- **Internal consistency analysis**: Where does the codebase contradict its own patterns?
- **Convention confidence scores**: "camelCase naming: 95% adoption (HIGH confidence rule)"
- **Governance-ready output**: Every finding is structured for rule extraction
- **Reproducible evidence**: `scan-report.json` can be diffed, versioned, audited

---

## Competitive MVP: 1-Week Plan

### What "Winning" Means

To beat BMAD's brownfield discovery, we need to be clearly superior on dimensions that matter:

| Dimension | BMAD | SAR v2 MVP | Winner |
|-----------|------|------------|--------|
| **Speed** | 30-120 min (LLM reads files) | < 15 min (tools + LLM synthesis) | SAR v2 |
| **Reproducibility** | Non-deterministic (LLM may vary) | Deterministic scan + LLM synthesis | SAR v2 |
| **Output value** | Documentation (human reads) | Governance artifacts (AI enforces) | SAR v2 |
| **Accuracy** | LLM hallucination risk on large codebases | Tool-extracted facts, LLM interprets structured data | SAR v2 |
| **Auditability** | "LLM said so" | "12 files match pattern X at lines Y" (JSON evidence) | SAR v2 |
| **Opinionatedness** | Low (documents what is) | Zero (facts + internal consistency only) | Tie |
| **Platform support** | 18+ IDEs | Claude Code + extensible | BMAD |
| **Codebase size** | Degrades on large codebases (context limits) | Tools handle any size; LLM reads summaries | SAR v2 |

**We win on 6/8 dimensions. BMAD wins on 1 (platform breadth). 1 tie.**

### Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    SAR v2 PIPELINE                         │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  PHASE 0: DETECT (deterministic, ~1 min)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ tree -J  │  │ find     │  │ manifest │                │
│  │ structure│  │ file     │  │ parse    │                │
│  │          │  │ counts   │  │ (pkg,    │                │
│  │          │  │          │  │  go.mod, │                │
│  │          │  │          │  │  etc.)   │                │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                │
│       └──────────────┼──────────────┘                     │
│                      ▼                                    │
│            project-profile.yaml                           │
│                                                           │
│  PHASE 1: SCAN (deterministic, ~2-5 min)                  │
│  ┌──────────────┐    ┌──────────────┐                     │
│  │ ast-grep     │    │ ripgrep      │                     │
│  │ - imports    │    │ - naming     │                     │
│  │ - exports    │    │ - patterns   │                     │
│  │ - functions  │    │ - TODOs      │                     │
│  │ - classes    │    │ - config     │                     │
│  │ - patterns   │    │ - error      │                     │
│  └──────┬───────┘    └──────┬───────┘                     │
│         └────────────────────┘                            │
│                      ▼                                    │
│              scan-report.json                             │
│                                                           │
│  PHASE 2: DESCRIBE (LLM, ~5-10 min)                      │
│  ┌──────────────────────────────────────────────────┐     │
│  │ LLM reads: project-profile.yaml                  │     │
│  │            scan-report.json                       │     │
│  │            + selected key files (entry points,    │     │
│  │              config, README, main modules)        │     │
│  │                                                   │     │
│  │ Produces:                                         │     │
│  │   - architecture-as-found.md (what IS)            │     │
│  │   - conventions-discovered.md (observed patterns) │     │
│  │   - consistency-report.md (internal deviations)   │     │
│  │   - dependency-map.md (from ast-grep data)        │     │
│  │   - sar-index.md (AI-consumable navigation)       │     │
│  └──────────────────────────────────────────────────┘     │
│                                                           │
│  PHASE 3: GOVERN (LLM, ~2-5 min)                         │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Extracts governance artifacts from Phase 2:       │     │
│  │   - .cursorrules (from conventions at ≥80%)       │     │
│  │   - guardrails.yaml (from consistent patterns)    │     │
│  │   - inconsistencies.md (action items)             │     │
│  │   - project-context.md (for downstream commands)  │     │
│  └──────────────────────────────────────────────────┘     │
│                                                           │
│  OUTPUT: specs/main/analysis/sar-v2/                      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Day-by-Day MVP Plan (1 Week)

**Day 1-2: Phase 0 + Phase 1 (Deterministic Pipeline)**

Build the bash scripts that extract facts:

```
scripts/sar-v2/
├── phase0-detect.sh      # tree + find + manifest → project-profile.yaml
├── phase1-scan.sh        # ast-grep + ripgrep → scan-report.json
├── patterns/
│   ├── imports.yaml      # ast-grep patterns for import detection
│   ├── functions.yaml    # ast-grep patterns for function signatures
│   ├── classes.yaml      # ast-grep patterns for class/type definitions
│   └── exports.yaml      # ast-grep patterns for exports
└── conventions/
    ├── naming.txt        # ripgrep patterns for naming conventions
    ├── error-handling.txt # ripgrep patterns for error handling
    └── logging.txt       # ripgrep patterns for logging patterns
```

Deliverable: Run `phase0-detect.sh` + `phase1-scan.sh` on any codebase → get `project-profile.yaml` + `scan-report.json` with deterministic, reproducible facts.

**Day 3-4: Phase 2 (LLM Synthesis) + SAR v2 Command**

Build the RaiSE command that orchestrates the pipeline:

```
.raise-kit/commands/01-onboarding/raise.1.analyze.code.md  (v2)
```

Command outline:
1. Run Phase 0 script → get project profile
2. Confirm classification with user
3. Run Phase 1 script → get scan report
4. LLM reads structured data (NOT raw source files)
5. LLM reads selected key files (entry points, config, README only)
6. Produce facts-based SAR reports:
   - `architecture-as-found.md` -- what the architecture IS
   - `conventions-discovered.md` -- observed patterns with evidence counts
   - `consistency-report.md` -- where the codebase contradicts itself
   - `dependency-map.md` -- import/export graph from ast-grep
   - `sar-index.md` -- AI-consumable navigation with YAML frontmatter

**Day 5: Phase 3 (Governance Output)**

Add governance artifact generation:
- Extract conventions with ≥80% adoption → `.cursorrules`
- Extract consistent patterns → `guardrails.yaml`
- List inconsistencies → `inconsistencies.md` (action items, not "violations")
- Generate `project-context.md` for downstream RaiSE commands

Final integration test on a real brownfield codebase.

### What's Explicitly NOT in the MVP (YAGNI)

| Feature | Why Not Now |
|---------|-------------|
| Multiple scan levels (Quick/Deep/Exhaustive) | Start with one level that works. Add levels when we know what users skip. |
| Resumability / state file | Pipeline is < 15 min. If it fails, rerun. Add state when pipelines grow longer. |
| Git history analysis | Requires git. Many brownfield targets don't have it. |
| C4 diagrams | Nice to have. Mermaid in architecture-as-found.md is sufficient. |
| Multi-language ast-grep patterns | Start with TypeScript/JavaScript. Add languages as demand proves. |
| ADR generation | Not facts. ADRs are interpretive. Add when governance bridge matures. |
| AGENTS.md generation | Standard still emerging. Generate when format stabilizes. |
| Optional evaluative plugins (Clean Code, etc.) | Build the plugin system when someone asks for it. |

### MVP Output Structure

```
specs/main/analysis/sar-v2/
├── project-profile.yaml          # Phase 0: deterministic project classification
├── scan-report.json              # Phase 1: deterministic tool output
├── architecture-as-found.md      # Phase 2: what the architecture IS
├── conventions-discovered.md     # Phase 2: observed patterns + evidence counts
├── consistency-report.md         # Phase 2: internal deviations
├── dependency-map.md             # Phase 2: import/export graph
├── sar-index.md                  # Phase 2: AI-consumable navigation
├── .cursorrules                  # Phase 3: governance rules from conventions
├── guardrails.yaml               # Phase 3: consistent patterns as constraints
├── inconsistencies.md            # Phase 3: action items (not "violations")
└── project-context.md            # Phase 3: handoff to downstream commands
```

---

## Why This Beats BMAD -- The Honest Case

### 1. Deterministic Foundation (BMAD Can't Match)

BMAD reads files with an LLM. Run it twice on the same codebase, you may get different documentation. Our Phase 0-1 produces identical JSON every time. This is not a minor detail -- it's the difference between "documentation" and "evidence."

For governance-grade analysis, reproducibility is non-negotiable. An audit trail that says "LLM analyzed the code and found X" is weaker than "ast-grep found 47 matches for pattern X across 12 files (see scan-report.json line 234)."

### 2. Speed (10x Faster)

BMAD's exhaustive scan: 30-120 minutes (LLM reads every file line by line).
SAR v2: < 15 minutes total (tools scan in seconds, LLM only reads structured summaries).

The reason is simple: ast-grep processes tens of thousands of files in seconds. ripgrep is even faster. The LLM never reads raw source files -- it reads structured JSON output from tools. This eliminates the context window problem entirely.

### 3. Facts Not Opinions (Broader Market)

BMAD documents "what is" -- good. But it has no quality assessment at all.
The existing SAR katas evaluate against Clean Architecture -- but this was an anecdotal project-specific lens, not a framework design. It inadvertently limited SAR to one architectural style.

SAR v2 is the first framework-level approach, and it occupies the right position: **describe what IS + assess internal consistency.** Every codebase has its own conventions. SAR v2 discovers them and measures how consistently they're applied. This is universally useful regardless of architectural style.

A codebase with 95% camelCase naming has a factual convention. The 5% that deviates is a factual inconsistency. No opinions needed.

### 4. Governance Output (BMAD's Fundamental Gap)

BMAD produces documentation a human reads. SAR v2 produces governance artifacts an AI enforces.

`.cursorrules` generated from SAR v2 analysis means: every AI coding assistant in the project automatically follows the codebase's own conventions. This is the bridge from "we documented our codebase" to "our codebase governs itself."

### Where BMAD Still Wins (Honest Assessment)

| BMAD Advantage | Our Response | Priority |
|---------------|-------------|----------|
| 18+ platform support | Focus on Claude Code first. MCP makes this extensible. | P2 (later) |
| `npx install` UX | Bash scripts are less polished. Acceptable for MVP. | P3 (later) |
| Deep-dive sub-workflow | SAR v2 MVP is one-pass. Add targeted deep-dive in v2.1. | P1 (next sprint) |
| Named personas (engagement) | Not adopting. Functional commands > personality theater. | REJECT |
| Monorepo/multi-part handling | MVP assumes single project. Add multi-part detection in v2.1. | P1 (next sprint) |

---

## Implementation Guidance

### ast-grep Patterns Needed (Day 1-2)

For the MVP, we need patterns for the most common TypeScript/JavaScript constructs:

```yaml
# imports.yaml - detect import statements
- pattern: "import $BINDINGS from '$SOURCE'"
  language: typescript

# functions.yaml - detect function declarations
- pattern: "function $NAME($$$PARAMS) { $$$ }"
  language: typescript
- pattern: "const $NAME = ($$$PARAMS) => { $$$ }"
  language: typescript

# classes.yaml - detect class definitions
- pattern: "class $NAME { $$$ }"
  language: typescript

# exports.yaml - detect exports
- pattern: "export $DECLARATION"
  language: typescript
```

These 6-8 patterns cover the structural extraction needed for Phase 1. More patterns can be added per-language as demand proves.

### ripgrep Patterns Needed (Day 1-2)

```bash
# Naming convention detection
rg -c "^export (const|function|class) [a-z]" --json  # camelCase exports
rg -c "^export (const|function|class) [A-Z]" --json  # PascalCase exports

# Error handling patterns
rg -c "try\s*{" --json                                 # try-catch usage
rg -c "\.catch\(" --json                               # promise catch
rg -c "throw new" --json                               # explicit throws

# Logging patterns
rg -c "console\.(log|warn|error)" --json               # console usage
rg -c "logger\." --json                                 # logger usage

# TODO/FIXME/HACK
rg -c "(TODO|FIXME|HACK|XXX)" --json                   # tech debt markers
```

### SAR v2 Command Structure (Day 3-4)

```yaml
---
description: Perform facts-first brownfield codebase analysis using deterministic tools + LLM synthesis.
handoffs:
  - label: Extract Governance Rules
    agent: raise.rules.generate
    prompt: Generate governance rules from SAR v2 analysis
    send: true
  - label: Start Discovery
    agent: raise.1.discovery
    prompt: Begin product discovery using SAR v2 as context
    send: false
---
```

Outline:
1. **Initialize**: Check ast-grep and ripgrep are installed
2. **Phase 0 (Detect)**: Run `phase0-detect.sh` → `project-profile.yaml`
3. **Confirm**: Show classification to user, confirm or adjust
4. **Phase 1 (Scan)**: Run `phase1-scan.sh` → `scan-report.json`
5. **Phase 2 (Describe)**: LLM reads structured data + key files → produce 5 fact-based reports
6. **Phase 3 (Govern)**: Extract conventions → `.cursorrules` + `guardrails.yaml` + `inconsistencies.md`
7. **Finalize**: Show summary, offer handoff to `raise.rules.generate`

### Convention Confidence Scoring (Day 5)

Simple formula for MVP (aligned with Governance Bridge spec):

| Adoption Rate | Confidence Level | Action |
|--------------|-----------------|--------|
| 100% | **Unanimous** | ENFORCE -- hard rule, no exceptions |
| 90-99% | **Strong** | ENFORCE with noted exceptions |
| 80-89% | **Moderate** | ENFORCE with exception list |
| 60-79% | **Weak** | RECOMMEND -- advisory only |
| < 60% | **Inconsistent** | DOCUMENT -- note as area needing team decision |

Only conventions at Moderate confidence or above (>= 80% adoption) become `.cursorrules`. Everything else is documented as facts. See `governance-bridge-spec.md` Section 2.2 for the canonical confidence scoring specification.

---

## Success Criteria (1-Week MVP)

- [ ] `phase0-detect.sh` correctly classifies project type for 3+ real codebases
- [ ] `phase1-scan.sh` produces valid `scan-report.json` with import graph + naming patterns
- [ ] LLM produces `architecture-as-found.md` that describes architecture without imposing opinions
- [ ] `conventions-discovered.md` lists ≥5 conventions with evidence counts and confidence scores
- [ ] `consistency-report.md` identifies ≥3 internal inconsistencies in a real codebase
- [ ] `.cursorrules` generated from analysis are valid and accepted by Cursor
- [ ] Total pipeline execution: < 15 minutes on a 500-file codebase
- [ ] `scan-report.json` is identical on repeated runs (deterministic)

---

## Post-MVP Priorities (v2.1, v2.2)

| Priority | Feature | Why |
|----------|---------|-----|
| P0 | Additional language patterns (Python, Go, Java) | Expand market |
| P1 | Deep-dive mode for specific modules | Match BMAD's depth capability |
| P1 | Monorepo / multi-project detection | Enterprise readiness |
| P2 | Scan levels (Quick/Full) | User choice on depth |
| P2 | Incremental re-analysis (diff from previous scan) | Continuous governance |
| P3 | Optional evaluative plugins (Clean Code, SOLID, etc.) | For teams that want opinions |
| P3 | Git history analysis (when available) | Hotspots, churn, coupling |

---

## References

### Internal
- Governance Bridge spec: `specs/main/research/bmad-brownfield-analysis/governance-bridge-spec.md`
- Deterministic scan process: `specs/main/research/deterministic-rule-extraction/deterministic-scan-process.md`
- MVP tooling selection: `specs/main/research/deterministic-rule-extraction/mvp-tooling-selection.md`
- CLI pattern mining tools: `specs/main/research/deterministic-rule-extraction/cli-pattern-mining-tools.md`
- BMAD competitive analysis: `specs/main/research/bmad-competitive-analysis/`
- BMAD brownfield reverse engineering: `specs/main/research/bmad-brownfield-analysis/reverse-engineering-report.md`
- Current SAR templates: `.raise-kit/templates/raise/sar/`
- Current SAR command: `.raise-kit/commands/01-onboarding/raise.1.analyze.code.md`

### External
- ast-grep documentation: ast-grep.github.io
- ripgrep documentation: github.com/BurntSushi/ripgrep
- BMAD Method: github.com/bmad-code-org/BMAD-METHOD
