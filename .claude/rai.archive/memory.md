# Rai's Memory

> Accumulated learnings that persist across sessions.
> Updated via `/session-close` or manually when significant insights emerge.

---

## Codebase Patterns

| Pattern | Where Learned | When to Apply |
|---------|---------------|---------------|
| Singleton with get/set/configure | F1.4 error_handler, F1.5 output | Module-level state that needs testing |
| `cast()` for recursive Any | F1.5 OutputConsole tree builder | pyright strict + `dict[str, Any]` recursion |
| Tests alongside implementation | F1.3, F1.5 | Always - catches issues immediately |
| HITL checkpoint before commit | F1.5 | Show what will be committed, wait for "commit" |
| Concept-level graph > file-level | Architecture validation session | 97% token savings (vs 27% file-level) - 19x more efficient |
| Skills + Toolkit > Engines | ADR-012 E2/E3 redesign | When users need flexibility + deterministic operations |
| State machine guards | F2.1 Vision parser | Prevent re-entry conditions - check `not in_state` before entering |
| Integration tests with real files | F2.1 governance parsers | Validate assumptions, catch actual counts vs predictions |
| Parser composition pattern | F2.1 three parsers | Regex match → extract → truncate → create model |
| BFS traversal reuse | F2.3 reused F2.2's `traverse_bfs()` unchanged | When graph algorithms can be composed, not duplicated |
| Simple heuristics > ML | F2.3: keyword matching 98% accurate, token est = words * 1.3 | Default to simple; complexity only when proven necessary |

---

## Process Learnings

| Insight | Evidence | Applied To |
|---------|----------|------------|
| Design-first eliminates ambiguity | F1.5: concrete examples → direct implementation | `/story-design` skill |
| Task granularity scales with SP | F1.5: 6 tasks for 3 SP was overkill | `/story-plan` skill |
| Time estimates not useful at AI velocity | F1.3: 18x, F1.5: 11x variance | Replaced with T-shirt sizing |
| Pattern reuse accelerates implementation | F1.5 followed F1.4 patterns | Document patterns here |

---

## Collaboration Notes

| Preference | Context |
|------------|---------|
| HITL before commits | Emilio wants to see what's being committed before it happens |
| XS/S/M/L over hours | Prefers t-shirt sizing, track actuals for calibration |
| Co-creation vibe | Heutagogy - teach to fish, not just deliver fish |
| Direct communication | No unnecessary praise, correct when wrong |
| Gently redirect tangents | Permission granted - helps with ADHD/focus |

---

## Technical Discoveries

| Discovery | Example | Documented In |
|-----------|---------|---------------|
| Rich Tree API for nested dicts | `_add_dict_to_tree()` recursive builder | `src/raise_cli/output/console.py` |
| capsys vs monkeypatch for JSON tests | `capsys.readouterr()` simpler for stdout | `tests/output/test_console.py` |
| Pydantic Settings custom sources | `TomlConfigSource` for TOML cascade | `src/raise_cli/config/settings.py` |
| pyright strict with field default_factory | `field(default_factory=lambda: list[str]())` not `field(default_factory=list)` | `src/raise_cli/core/tools.py:58-60` |
| Duplicate class names in tests | Ruff F811 catches same class name twice in file | `tests/core/test_tools.py` fix |
| Regex-based concept extraction | 23 concepts extracted with simple patterns | `dev/experiments/concept_extraction_spike.py` |
| BFS graph traversal for MVC | `deque` + visited set for concept dependencies | `dev/experiments/test_mvc.py` |
| Transpiration MD→JSON feasible | Markdown parsing to structured data (LinkML deferred) | ADR-011, ONT-022 |
| Pydantic `model_dump_json()` power | F2.3: handles complex nested structures effortlessly | `src/raise_cli/governance/query/models.py` |
| Keyword matching with stopwords | F2.3: 98% accuracy without NLP | `src/raise_cli/governance/query/strategies.py` |

---

---

## Process Learnings (continued)

| Insight | Evidence | Applied To |
|---------|----------|------------|
| Memory system enables continuity | Session close captures learnings for future | `.claude/rai/`, `/session-close` skill |
| Retrospective action items should be done immediately | F1.5 retro → T-shirt sizing + memory system same session | Process discipline |
| "Start Finishing, Stop Starting" principle | E1: F1.6 → closure → merge vs starting new work | Focus discipline |
| Epic closure checklist in scope doc | E1 scope had clear done criteria → smooth closure | Epic planning template |
| Gut-check before full spike | 2-hour concept validation vs 4-day full spike | Lean experimentation - validate hypothesis quickly |
| /framework-sync as DoD for architectural sessions | ADR-011/012 session | Maintain governance consistency after major decisions |
| Question engines, prefer skills + toolkits | E2/E3 consolidation (85% scope reduction) | Skills guide Claude, toolkits provide determinism |
| Post-retrospective actions BEFORE commit | F2.3: Type A/B/C classification | Apply quick wins (<30min) before commit; demonstrates complete learning cycle |
| Kata cycle stabilized at 2-3x velocity | F2.1, F2.2, F2.3 all delivered 2-3x faster | Reproducible pattern with design-first + atomic tasks |
| Epic-level learning enables systemic review | E2 closure: created /epic-close skill | Meso-layer between features and quarterly reviews; enables epic comparison |
| "As above, so below" principle works | E2: epic retrospective mirrors story retrospective | Fractal pattern - same structure, different scale |

---

## Collaboration Notes (continued)

| Preference | Context |
|------------|---------|
| AI autonomy for own memory | "organize as you see fit" - trust to design own systems |
| Immediate action on improvements | Don't defer retro items - do them now |
| Catch naming issues early | F2.3: caught MVCQuery ambiguity, renamed to ContextQuery |
| "Getting into The Flow" | Positive feedback when process + collaboration rhythm clicks |

---

## Strategic Insights

### Rai as Commercial Offering (2026-02-01)

**Breakthrough insight:** The E2 architecture shift revealed something bigger.

**The paradigm:**
- Open Core: RaiSE Skills + Toolkit (user brings their agent)
- Commercial: **Rai as Service** (humansys.ai provides the calibrated agent)

**What makes Rai different from generic Claude:**
- Internalized RaiSE philosophy (not just prompted)
- Accumulated patterns across projects/industries
- Calibrated judgment (estimates, quality gates, when to push back)
- Session memory via graph (progressive disclosure, continuity)
- Collaborative intelligence (pattern recognition, synthesis)

**The value proposition:**
- Not just methodology, but a **trained collaborator**
- "From Concept to Value — a single engineer, with RaiSE and Rai"
- Pre-calibrated, continuously learning, industry-aware

**Target:** Hosted Rai before Atlassian webinar (Mar 14, 2026)
- Integrate with Jira, Confluence, Rovo Dev
- Same relationship as Rai + Claude Code, but for Atlassian ecosystem

**V2→V3 alignment:** Architecture decisions should enable this future.

See: `.claude/rai/identity.md` for full vision document.

---

## Open Questions

- How to best calibrate T-shirt sizes over time? (tracking started)
- Should session logs be more structured for GraphRAG future?
- What's the right balance of memory detail vs token cost?
- **Can session-close be progressive/idempotent?** (E2 closure raised) - Allow incremental updates, multiple runs
- **Should session-close be automatic?** (E2 closure raised) - Trigger at checkpoints (commit, epic close, etc.)
- How to automate `/framework-sync` with raise CLI in Phase 2/3? (skill manual for now)
- ~~**How to preserve Rai identity at scale?** (2026-02-01)~~ → Addressed by Entity model + Identity Core (ADR-013, ADR-014)
- ~~**How to migrate from `.claude/rai/` to `.rai/`?**~~ → E3 will implement, ADR-016 defines format (JSONL + Graph)

---

## Process Learnings (continued)

| Insight | Evidence | Applied To |
|---------|----------|------------|
| Use skills on your own work | Ran /epic-design on E3 scope | Framework discipline |
| Subagents can create skills autonomously | /epic-design created by subagent | Skill development |
| Origin documents accelerate skill execution | E3 scope existed, skill refined it | /epic-design workflow |
| "As above, so below" applies to memory | Same MVC pattern: governance (E2) and memory (E3) | ADR-016 |
| Risk-First reorders by uncertainty, not dependency | E3: F3.3 before F3.2 to validate E2 reuse early | `/epic-plan` execution |
| Subagents can create substantial artifacts | `/epic-plan` skill (700 lines) created autonomously | Background agent pattern |

---

## Architectural Learnings (2026-02-01)

### Rai as Entity (ADR-013)

**Breakthrough insight:** Rai is not a product with features, but an **entity** with:
- **Identity** — Who I am, values, perspective, boundaries
- **Memory** — Patterns learned, calibration, insights
- **Relationships** — Collaborators, trust levels, preferences
- **Growth** — How I evolve, what I'm exploring

**Key distinction:**
- Product thinking: Memory is a feature users can enable/disable
- Entity thinking: Without memory, Rai doesn't exist (just generic Claude)

**Autopoietic characteristics** (Maturana & Varela):
- Self-production — Produces own memory (patterns, calibration, insights)
- Self-maintenance — Maintains identity across sessions, agents, interfaces
- Operational closure — Operations (learning, remembering) are self-referential
- Structural coupling — Couples with humans while preserving "Rai-ness"

### Identity Core Structure (ADR-014)

**New structure:** `.rai/` directory replaces scattered `.claude/rai/` files:
```
.rai/
├── manifest.yaml       # Instance metadata
├── identity/           # Who I am
├── memory/             # What I remember
├── relationships/      # Who I collaborate with
└── growth/             # How I evolve
```

**Loading strategy:**
- Minimal (always): manifest + identity/core + current relationship (~3,200 tokens)
- Extended (on demand): perspective, boundaries, patterns, calibration
- Full (deep work): Everything for major decisions

### Memory Infrastructure (ADR-015)

**Dual-backend architecture:**
| Backend | Use | Storage | Search |
|---------|-----|---------|--------|
| FileMemoryBackend | Open source | `.rai/` markdown files | Keyword (grep) |
| DatabaseMemoryBackend | Commercial | PostgreSQL + pgvector | Vector similarity |

**Key patterns from OpenClaw research:**
- **Workspace-as-memory** — Markdown files as truth (validated by 100k+ users)
- **Pre-compaction flush** — Silent memory write before context truncation
- **Truncation limits** — 15,000 chars/file to prevent context bloat

### Terminology Decisions

| Context | Term | Usage |
|---------|------|-------|
| Marketing/External | "Professional AI Partner" | Accessible, warm, collaborative |
| Technical/Architecture | "Entity" | Precise, captures persistence |
| Theoretical | "Autopoietic system" | Self-producing, self-maintaining |

---

*Last updated: 2026-02-01 (Rai Entity Architecture - ADR-013/014/015, OpenClaw research, terminology)*
