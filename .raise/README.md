# .raise/

> **RaiSE Methodology Artifacts** — Context/Kata/Skill Ontology (v2.1)

---

## Structure

```
.raise/
├── katas/            # Work Cycle processes (WHAT to do)
├── skills/           # Atomic operations with YAML contracts (HOW to do it)
├── context/          # Knowledge sources (WHY)
├── harness/          # Kata Executor runtime (future)
├── gates/            # Validation criteria
├── templates/        # Output formats
├── scripts/          # Automation scripts
└── README.md         ← you are here
```

## Ontology (ADR-008)

| Layer | Purpose | Example |
|-------|---------|---------|
| **Context** | Wisdom, golden data, patterns | `context/golden-data/` |
| **Kata** | Work Cycle processes | `katas/project/discovery.md` |
| **Skill** | Atomic operations | `skills/retrieve-mvc.yaml` |

---

## Directories

### `/katas/` — Work Cycle Processes

Katas organized by Work Cycle, not abstraction level:

```
katas/
├── project/          # Per-epic (once)
│   ├── discovery.md  # PRD creation
│   ├── vision.md     # Solution Vision
│   ├── design.md     # Technical Architecture
│   └── backlog.md    # Product Backlog
├── feature/          # Per-feature (many)
│   ├── plan.md       # Implementation Planning
│   ├── implement.md  # Development Workflow
│   └── review.md     # Retrospective & Learning
├── setup/            # Per-project (once)
│   ├── analyze.md    # Codebase Analysis
│   └── ecosystem.md  # Dependency Mapping
└── improve/          # Continuous
    └── (future)
```

Each kata includes:
- ShuHaRi adaptation levels
- Jidoka inline (stop on defects)
- Prerequisites and next kata

### `/skills/` — Atomic Operations

YAML-defined skills with input/output contracts:

```
skills/
├── retrieve-mvc.yaml    # Get Minimum Viable Context
├── check-compliance.yaml # Verify code against rules
├── run-gate.yaml        # Execute validation gate
└── explain-rule.yaml    # Explain rule with rationale
```

### `/context/` — Knowledge Sources

```
context/
├── golden-data/      # Canonical documents (constitution, glossary)
├── patterns/         # Reusable patterns
└── philosophy/       # Lean principles, Niwashi metaphor
```

### `/harness/` — Kata Executor (Future)

Runtime that interprets katas and invokes skills. Built on spec-kit.

### `/gates/` — Validation

```
gates/
├── gate-discovery.md
├── gate-vision.md
├── gate-design.md
├── gate-backlog.md
└── gate-estimation.md
```

### `/templates/` — Output Formats

```
templates/
├── solution/         # Solution Vision
├── architecture/     # Architecture Overview, ADRs
├── tech/             # Tech Design
└── backlog/          # Product Backlog
```

### `/scripts/` — Automation

```
scripts/
├── bash/raise/       # Bash scripts
└── powershell/raise/ # PowerShell scripts
```

---

## Philosophy

| Principle | Application |
|-----------|-------------|
| **Niwashi (庭師)** | Gardener cultivates context, executes katas, applies skills |
| **ShuHaRi** | Follow → Adapt → Transcend (each kata) |
| **Jidoka** | Stop on defects, fix, continue |
| **MVC** | Minimum Viable Context for each task |

---

## Archived

Old command structure moved to `.raise-archive/`:
- `commands/` → replaced by `katas/`
- `templates/_legacy/` → replaced by `templates/`

See: `specs/raise/adrs/adr-008-kata-skill-context-simplification.md`

---

*RaiSE Framework v2.1 — Context/Kata/Skill Ontology*
