# Framework Directory

> Governance OF the RaiSE framework itself

---

## Purpose

This directory contains **authoritative artifacts that govern the RaiSE framework**. It is the parallel of `governance/` but for the framework's own definition.

| Directory | Governs | Audience |
|-----------|---------|----------|
| `governance/` | Consumer projects using RaiSE | Project teams |
| `framework/` | The RaiSE framework itself | Framework maintainers |

## Structure

```
framework/
├── index.yaml          # Manifest of all framework artifacts
├── vision.md           # What RaiSE IS (framework vision)
├── README.md           # This file
├── schemas/            # JSON Schemas for validation
│   ├── rule-schema.json
│   ├── graph-schema.json
│   └── mvc-schema.json
├── context/            # Framework wisdom
│   ├── glossary.md     # Canonical terminology
│   ├── constitution.md # Core principles
│   ├── philosophy.md   # Learning philosophy
│   ├── work-cycles.md  # The 5 work cycles
│   └── compliance.md   # Compliance patterns
└── decisions/          # Framework ADRs (accepted)
    ├── README.md
    └── adr-*.md
```

## Key Documents

| Document | Purpose |
|----------|---------|
| `vision.md` | Defines what RaiSE IS - the framework's identity |
| `context/glossary.md` | Canonical terminology (v2.4) |
| `context/constitution.md` | Core principles that never change |
| `decisions/adr-*.md` | Architecture decisions that shaped the framework |

## Relationship to .raise/

```
framework/              .raise/
──────────              ───────
Defines WHAT            Implements HOW
(vision, principles)    (katas, gates, templates)

"RaiSE uses Jidoka"     "gate-vision.md validates..."
"5 Work Cycles exist"   "katas/project/vision.md"
```

- `framework/` = the specification
- `.raise/` = the implementation

## Maintenance

Use `dev/skills/` tools to maintain framework integrity:

- `impact-analysis.md` - Before changing framework docs
- `governance-audit.md` - Detect drift between spec and implementation

---

*Part of the Three-Directory Model (ADR-011)*
