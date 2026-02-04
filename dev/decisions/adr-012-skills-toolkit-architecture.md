---
id: "ADR-012"
title: "Skills + CLI Toolkit Architecture (vs Kata/Gate Engines)"
date: "2026-01-31"
status: "Accepted"
related_to: ["ADR-005", "ADR-011"]
supersedes: ["Original E2/E3 Engine Architecture"]
---

# ADR-012: Skills + CLI Toolkit Architecture

## Context

### Original Architecture (Backlog v1.0)

The initial RaiSE design proposed programmatic execution engines:

**E2: Kata Engine (31 SP)**
- Kata Parser, Discovery, State Manager
- Interactive execution with prompts
- `raise kata run project/prd` command

**E3: Gate Engine (29 SP)**
- Gate Parser, Criterion Validators
- Deterministic validation execution
- `raise gate validate prd` command

**Total: 60 SP of programmatic orchestration**

### The Shift: Skills as Process Guides

Through dogfooding RaiSE development using Claude Code, we discovered:

1. **Katas work better as Agent Skills** (markdown guides Claude reads)
2. **Skills call deterministic CLI tools** for data extraction
3. **No execution engine needed** - Claude interprets the process
4. **CLI provides structured data** - Claude provides judgment

**Example: `/session-start` skill**
```markdown
# Skill: Session Start
## Step 1: Load Context
Bash: raise session analyze
# Returns: {memory: {...}, progress: {...}, signals: [...]}

## Step 2: Synthesize
[Claude interprets JSON and creates greeting]
```

**Works beautifully. No engine needed.**

### The Realization

**Original vision (with engines):**
```
User → raise kata run prd → Kata Engine → Prompts user → Tracks state
User → raise gate validate prd → Gate Engine → Runs validators → Reports
```

**Actual usage (with skills):**
```
User → Claude Code
     → /prd skill (Claude reads markdown)
     → Calls: raise parse prd.md, raise validate structure prd.md
     → Claude synthesizes guidance from structured data
```

**Same outcome, 10x simpler architecture.**

### Key Question from Session

> "If katas are skills (Claude reads them), and gates are skills (Claude validates), why build engines? Why not build CLI toolkit that skills call?"

**Answer: No reason. Skills + Toolkit is superior.**

## Decision

**Replace E2 Kata Engine + E3 Gate Engine with E2 Governance Toolkit.**

### What Changes

| Original | New | Rationale |
|----------|-----|-----------|
| E2: Kata Engine (31 SP) | E2: Governance Toolkit (9 SP) | Skills execute katas, not engines |
| E3: Gate Engine (29 SP) | [Merged into E2] | Skills execute gates, not engines |
| Interactive prompts | Skills guide user | Claude is the interface |
| State persistence | Git commits | Observable via git history |
| Execution orchestration | Skills compose tools | Claude orchestrates |

**Savings: 60 SP → 9 SP (85% reduction)**

## Architecture

### Skills (Process Guidance)

**Agent Skills** are markdown documents Claude reads to execute processes:

```
.claude/skills/
├── session-start/SKILL.md     # Load context, analyze progress
├── session-close/SKILL.md     # Extract learnings, update memory
├── feature-design/SKILL.md    # Design a feature
├── feature-plan/SKILL.md      # Plan implementation
├── validate-prd/SKILL.md      # Validate PRD quality
└── research/SKILL.md          # Conduct research
```

**Skills contain:**
- Process steps (what to do)
- Validation criteria (what good looks like)
- Tool calls (deterministic data gathering)
- Synthesis guidance (how Claude should interpret)

**Skills do NOT contain:**
- Code to execute
- Programmatic logic
- State machines
- Execution engines

### CLI Toolkit (Deterministic Operations)

**raise-cli** provides deterministic tools skills call:

```bash
# Parsing & Extraction
raise parse <file> --type <prd|vision|design>
raise extract sections <file>
raise extract frontmatter <file>

# Validation
raise validate structure <file> --schema <type>
raise validate references <file>
raise validate consistency --prd <file> --vision <file>

# Graph Operations (ADR-011)
raise graph build --from <dir>
raise context query --task <task>

# Session Management
raise session analyze
raise progress show <epic-id>

# Analysis (Brownfield - E5)
raise analyze structure <dir>
raise analyze patterns <dir>
```

**Each command:**
- Returns structured JSON
- Is deterministic (same input → same output)
- Is fast (<5s for common operations)
- Is observable (can log exact command run)
- Is testable (CLI integration tests)

### The Handoff Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ Skill: /validate-prd (Claude reads markdown)                │
│                                                              │
│ Step 1: Check structure                                     │
│   Bash: raise validate structure prd.md --schema prd        │
│   ↓ Returns: {valid: true, sections: [...]}                │
│                                                              │
│ Step 2: Check references                                    │
│   Bash: raise validate references prd.md                    │
│   ↓ Returns: {broken: [], valid: [...]}                    │
│                                                              │
│ Step 3: Check alignment                                     │
│   Bash: raise context query --artifact prd --related vision │
│   ↓ Returns: {concepts: [...], alignment: {...}}           │
│                                                              │
│ Step 4: Synthesize report                                   │
│   [Claude interprets JSON, generates validation report]     │
└─────────────────────────────────────────────────────────────┘
```

**Skills = Judgment + Guidance**
**Toolkit = Data + Determinism**

### Why This is Better

| Aspect | Engine Approach | Skills + Toolkit | Winner |
|--------|----------------|------------------|--------|
| **Complexity** | 60 SP implementation | 9 SP implementation | Skills ✅ |
| **Flexibility** | Hardcoded workflows | Claude adapts naturally | Skills ✅ |
| **Observability** | Black box execution | See exact commands run | Skills ✅ |
| **Inference Economy** | No savings | CLI extracts data (cheap) | Skills ✅ |
| **Maintenance** | Update engine code | Update markdown | Skills ✅ |
| **User Experience** | CLI-driven | Natural conversation | Skills ✅ |
| **Third-party adoption** | Install CLI engine | Drop markdown in `.claude/skills/` | Skills ✅ |

**Skills + Toolkit wins on every dimension.**

## Consequences

### Positive ✅

1. **Massive scope reduction**: 60 SP → 9 SP (85% less work)
2. **Faster to MVP**: Ship toolkit in weeks, not months
3. **Better UX**: Natural conversation vs CLI commands
4. **More flexible**: Claude adapts process to context
5. **Observable**: See exact tools called, not engine internals
6. **Inference economy**: CLI gathers data cheaply, Claude synthesizes
7. **Third-party friendly**: Companies add skills, not rebuild engines
8. **Aligns with Claude Code**: Works natively with skills system

### Negative ⚠️

1. **Requires Claude Code**: Can't use RaiSE without AI assistant (by design)
2. **Non-deterministic execution**: Skills adapt, engines are fixed
3. **Harder to measure**: "Did user complete kata?" = check artifacts, not state file
4. **Skills discipline**: Users must learn to write effective skills

### Neutral 🔄

1. **Still need CLI**: Toolkit provides deterministic operations
2. **Still need validation**: Skills validate, just not engines
3. **Still need process**: Skills ARE the process, just not code
4. **Observability shifts**: Git history + session logs vs execution logs

## Impact on Roadmap

### Original Backlog (60 SP)

- E2: Kata Engine (31 SP)
  - F2.1: Kata Parser (5 SP)
  - F2.2: Kata Discovery (3 SP)
  - F2.3: State Manager (5 SP)
  - F2.4: Executor (8 SP)
  - F2.5: Handler (5 SP)
  - F2.6: Interactive Mode (5 SP)

- E3: Gate Engine (29 SP)
  - F3.1: Gate Parser (5 SP)
  - F3.2: Gate Discovery (3 SP)
  - F3.3: Criterion Validators (8 SP)
  - F3.4: Gate Executor (5 SP)
  - F3.5: Gate Handler (3 SP)
  - F3.6: Fix Suggestions (5 SP)

### New Backlog (9 SP)

**E2: Governance Toolkit (9 SP)**

- F2.1: Concept Extraction (3 SP)
  - Parse PRD requirements
  - Parse Vision outcomes
  - Parse Constitution principles

- F2.2: Graph Builder (2 SP)
  - Relationship inference
  - Graph serialization
  - Validation

- F2.3: MVC Query Engine (2 SP)
  - Graph traversal
  - Concept aggregation
  - Fallback to file-level

- F2.4: CLI Commands (2 SP)
  - `raise graph build`
  - `raise context query`
  - `raise validate structure`
  - `raise parse <file>`

**Skills (content, not SP):**
- `/validate-prd` - Validate PRD quality
- `/validate-design` - Validate design completeness
- `/session-start` - Load context, analyze progress
- `/session-close` - Extract learnings
- [More as needed - just markdown files]

### Timeline Impact

| Milestone | Original | New | Savings |
|-----------|----------|-----|---------|
| **E2 Complete** | ~3 weeks | ~1 week | 2 weeks ⚡ |
| **E3 Complete** | ~3 weeks | [Merged] | 3 weeks ⚡ |
| **MVP Ready** | 6 weeks | 1 week | 5 weeks ⚡ |

**Can reach Feb 9 deadline comfortably.**

## Implementation Strategy

### Phase 1: E2 Toolkit (1 week)

**Days 1-2: Concept Extraction**
- Implement parsers (requirements, outcomes, principles)
- Pydantic schemas for concepts
- Tests for extraction accuracy

**Days 3-4: Graph Builder**
- Relationship inference (keyword matching)
- Graph serialization (JSON)
- Validation (detect broken refs)

**Days 5-6: MVC Query**
- Graph traversal (BFS)
- Concept aggregation
- Fallback to file-level

**Day 7: CLI Commands**
- `raise graph build`
- `raise context query`
- `raise validate structure`
- `raise parse`

### Phase 2: Skills Library (ongoing)

**Already have:**
- ✅ `/session-start`
- ✅ `/session-close`
- ✅ `/feature-design`
- ✅ `/feature-plan`
- ✅ `/research`

**Add as needed:**
- `/validate-prd`
- `/validate-design`
- `/create-adr`
- `/plan-sprint`

**Skills are content, not code** - add incrementally based on real needs.

## Migration Path

### For RaiSE Development (Dogfooding)

**Already using skills:**
- We've been dogfooding skills since F1.3
- `/session-start`, `/session-close` work great
- No migration needed - continue current approach

**Add toolkit:**
- Build E2 toolkit (1 week)
- Skills start calling toolkit commands
- Measure token savings in real usage

### For External Users

**They adopt:**
1. Install raise-cli (toolkit)
2. Copy `.claude/skills/` to their repo
3. Customize skills for their processes
4. Claude Code uses skills + toolkit naturally

**No engine installation, no complex setup.**

## Validation

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Scope reduction | >80% | SP count (60 → 9 = 85% ✅) |
| Token savings | >20% | CLI extraction vs manual reading |
| Time to MVP | <2 weeks | E2 completion date |
| Skills adoption | >5 skills | Count `.claude/skills/*` |

### Proof Points

**Already validated:**
- ✅ Skills work (dogfooding since F1.3)
- ✅ Concept extraction feasible (spike proven)
- ✅ Token savings real (97% in experiments)
- ✅ Architecture simpler (observable, composable)

## Alternatives Considered

### Alternative 1: Build Engines as Planned

**Rejected because:**
- 60 SP vs 9 SP (7x more work)
- Slower (6 weeks vs 1 week to MVP)
- Less flexible (hardcoded workflows)
- Worse UX (CLI-driven vs conversational)
- Doesn't leverage Claude Code's strengths

### Alternative 2: Hybrid (Engines for Some, Skills for Others)

**Rejected because:**
- Complexity (maintain both approaches)
- Confusion (when to use which?)
- Doesn't reduce scope meaningfully
- Violates "simplicity over completeness"

### Alternative 3: Pure Skills, No CLI Toolkit

**Rejected because:**
- Skills would duplicate parsing logic (waste)
- No inference economy (Claude re-parses every time)
- Less observable (can't see what data extracted)
- Misses 97% token savings from concept extraction

**Skills + Toolkit is the sweet spot.**

## Ontology Alignment

This decision aligns with core RaiSE principles:

**ONT-018: "Ontología bajo demanda"**
> "MCP devuelve grafo estructurado con principios/patrones/prácticas bajo demanda"

**Implemented as:**
- Concept graph (ADR-011)
- CLI toolkit queries graph
- Skills request MVC for specific tasks

**ONT-020: "RAG estructurado vs probabilístico"**
> "Contexto determinista estructurado = mejores resultados"

**Implemented as:**
- CLI provides deterministic data extraction
- Skills provide probabilistic synthesis
- Best of both worlds

**Constitution §7: Lean Software Development**
> "Eliminar desperdicio, contexto primero, Jidoka"

**Implemented as:**
- Eliminate 85% of scope (engines are waste)
- Context-first (concept graph)
- Jidoka via skills (Claude stops on errors)

## References

- **ADR-005**: Skills Format Adoption (precursor)
- **ADR-011**: Concept-Level Graph (enables this)
- **Ontology Backlog**: ONT-018, ONT-020, ONT-022
- **Session Logs**: Dogfooding sessions demonstrating skills work
- **Experiments**: `dev/experiments/` (proof of feasibility)

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-31 | Question: Do we need engines if skills work? | Katas/gates work as skills |
| 2026-01-31 | Explore: Skills + toolkit vs engines | Test if toolkit provides value |
| 2026-01-31 | Validate: Concept extraction spike | Prove toolkit can extract structured data |
| 2026-01-31 | **Accept: Skills + Toolkit** | 85% scope reduction, proven feasible, better UX |

---

**Status**: Accepted (2026-01-31)

**Approved by**: Emilio Osorio, Rai

**Impact**:
- E2: Kata Engine → E2: Governance Toolkit (31 SP → 9 SP)
- E3: Gate Engine → [Merged into E2] (29 SP → 0 SP)
- Total: 60 SP → 9 SP (85% reduction)

**Next steps**:
1. Update backlog.md with new E2 scope
2. Archive original E2/E3 designs (for reference)
3. Begin E2 toolkit implementation
4. Add validation skills to `.claude/skills/`
