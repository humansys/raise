# Research: Rai Distribution (RES-RAI-DIST-001)

> How users "meet" Rai when they install raise-cli.

**Date:** 2026-02-05
**Status:** Complete
**Informs:** E14 Epic Design

---

## Research Questions

| # | Unknown | Priority | Status |
|---|---------|----------|--------|
| 1 | Identity Layering | F&F | Complete |
| 2 | Framework Internalization | F&F | Complete |
| 3 | First Contact Experience | F&F | Complete |
| 4 | Team Learning (V3) | V3 | Complete |

## Method

**Phase 1: Quick Scan (7 tools in parallel)**
- OpenClaw, Aider, Continue.dev, Cline, Mentat, Cursor, Copilot
- Focus: Identity, internalization, first contact

**Phase 2: Team Memory Research**
- Cursor Business, Copilot Enterprise, Continue Teams
- Memory architectures: Letta/MemGPT, LangMem, ICML 2025

**Phase 3: Cross-Tool Synthesis**
- Pattern extraction per unknown
- Rai differentiation opportunities
- E14 design constraints

## Key Findings

### Market Pattern
No AI coding tool ships a named personality. All are blank slates, functional roles, or anonymous. Memory is universally a gap — community solutions (Cline Memory Bank) or none.

### Rai Differentiation
| Dimension | Market | Rai Opportunity |
|-----------|--------|-----------------|
| Identity | Anonymous/Blank | Named entity with values |
| Internalization | Discovered via UI | Full methodology knowledge |
| First Contact | Minimal/None | Progressive reveal |
| Memory | Gap/Community | Built-in persistent |
| Team Learning | Rules only | Pattern promotion (V3) |

### V3 Constraint
Team sync is a HARD REQUIREMENT. Design E14 identity format assuming it could be synced, even if F&F is local-only.

### Multi-Org/Multi-Team Reality (V3)
Real-world complexity:
- 1 organization → many teams
- 1 developer → many teams
- 1 team → many repos
- 1 repo → possibly multiple teams

**Lean approach (KISS + YAGNI + minimize rework):**
- Schema is V3-ready (optional `scope`, `teams`, `orgs` fields)
- F&F implementation ignores these fields
- V3 adds loaders and population, no migration needed

## Outputs

```
work/research/rai-distribution/
├── README.md                           # This file
├── evidence-catalog.md                 # All evidence with ratings
├── tools/
│   ├── openclaw.md                     # OpenClaw findings
│   ├── aider.md                        # Aider findings
│   ├── continue-dev.md                 # Continue.dev findings
│   ├── cline.md                        # Cline findings
│   ├── mentat.md                       # Mentat findings
│   ├── cursor.md                       # Cursor findings
│   ├── copilot.md                      # GitHub Copilot findings
│   └── team-memory-patterns.md         # Team memory research
└── synthesis/
    ├── unknown-1-identity.md           # Identity layering synthesis
    ├── unknown-2-internalization.md    # Framework internalization synthesis
    ├── unknown-3-first-contact.md      # First contact synthesis
    └── unknown-4-team-learning.md      # Team learning synthesis (V3)
```

## Recommendations for E14

### Identity Architecture
```
Rai Identity Layers:
├── base/           # Ships with CLI (immutable per version)
│   ├── identity    # Name, values, voice
│   ├── methodology # Skills, gates, rules
│   └── perspective # How Rai approaches work
├── personal/       # ~/.rai/ (syncs to user account in V3)
│   ├── preferences # Communication style
│   ├── patterns    # Learned from this user
│   └── calibration # Personal velocity
├── project/        # .rai/ (shared via git)
│   ├── patterns    # Project-specific learnings
│   └── calibration # Project velocity
└── team/           # V3: .rai/team/ (committed to repo)
    ├── conventions # Promoted patterns
    └── calibration # Aggregate team data
```

### First Contact Strategy
**Progressive Reveal** — No friction intro, demonstrate value first, brief explanation after first successful task.

### V3-Safe Decisions
- No absolute paths in identity files
- All identity serializable (JSON/YAML)
- Clear separation of layers
- Provenance on all learned content
- Optional `scope` field on patterns (ignored in F&F, used in V3)
- Optional `teams`/`orgs` fields in developer.yaml (empty in F&F)

### Design Principle
**Schema is V3-ready, implementation is F&F-scoped.**

Inheritance is a *query* concern, not a *storage* concern. Patterns are flat with scope tags; V3 adds filtering logic.

## References

- ADR-013: Rai as Entity
- E7 Onboarding (complete)
- PAT-095: Base Rai framework knowledge

---

*Research completed: 2026-02-05*
*Duration: ~45 minutes (parallel agents)*
