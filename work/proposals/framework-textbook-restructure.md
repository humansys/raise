# Proposal: Framework as Textbook Restructure

> Transforming `framework/` from internal reference to adoption-friendly textbook

---

## Problem Statement

Current `framework/` mixes:
- Authoritative definitions (good)
- Internal decision records (wrong place)
- Technical schemas (wrong place)
- Missing: educational content for adopters

## Target Structure

```
framework/
├── README.md                    # NEW: "What is RaiSE?" - 5 min overview
├── index.yaml                   # Manifest (updated)
│
├── getting-started/             # NEW: Adoption path
│   ├── README.md                # Quick start overview
│   ├── brownfield.md            # Existing projects
│   └── greenfield.md            # New projects
│
├── concepts/                    # NEW: Core concepts explained simply
│   ├── README.md                # Concepts overview
│   ├── governance.md            # Why explicit governance matters
│   ├── work-cycles.md           # The 5 cycles (simplified from context/)
│   ├── katas.md                 # What katas are, how to use them
│   ├── gates.md                 # Validation gates explained
│   └── artifacts.md             # Solution → Project → Feature hierarchy
│
├── reference/                   # Dense reference (moved from context/)
│   ├── glossary.md              # Canonical terminology
│   ├── constitution.md          # Core principles
│   ├── philosophy.md            # Heutagogy, Jidoka (deep reading)
│   ├── compliance.md            # Compliance patterns
│   └── work-cycles-detailed.md  # Full work cycles spec
│
└── vision.md                    # Framework vision (keep at root)
```

## Migration Plan

### Phase 1: Move Internal Content to dev/

```bash
# ADRs are decision records, not teaching material
mv framework/decisions/* dev/decisions/framework/
rmdir framework/decisions

# Schemas are implementation details
mv framework/schemas/* dev/schemas/
rmdir framework/schemas
```

### Phase 2: Reorganize Existing Content

```bash
# Create reference/ for dense material
mkdir -p framework/reference
mv framework/context/* framework/reference/
rmdir framework/context
```

### Phase 3: Create Textbook Skeleton

New files to create:
- `framework/README.md` - Main entry point
- `framework/getting-started/README.md`
- `framework/getting-started/brownfield.md`
- `framework/getting-started/greenfield.md`
- `framework/concepts/README.md`
- `framework/concepts/governance.md`
- `framework/concepts/work-cycles.md`
- `framework/concepts/katas.md`
- `framework/concepts/gates.md`
- `framework/concepts/artifacts.md`

### Phase 4: Update index.yaml

Reflect new structure in manifest.

---

## Content Guidelines

### README.md (Entry Point)
- 5 minute read max
- Answer: What is RaiSE? Why use it? Who is it for?
- Link to getting-started for next steps
- No jargon without immediate explanation

### Concepts (concepts/)
- One concept per file
- Start with "why" before "what"
- Use examples, not abstract definitions
- Link to reference/ for deep dives

### Getting Started (getting-started/)
- Task-oriented, not concept-oriented
- "Do this, then this, then this"
- Minimal theory, maximum action
- Different paths for different contexts

### Reference (reference/)
- Dense, complete, authoritative
- For lookup, not learning
- OK to be technical and comprehensive

---

## Success Criteria

1. New adopter can understand RaiSE value prop in 5 minutes (README)
2. New adopter can start using RaiSE in 30 minutes (getting-started)
3. Concepts are understandable without prior RaiSE knowledge
4. Reference material remains authoritative and complete

---

*Proposal created: 2026-01-30*
*Related: ADR-011 Three-Directory Model*
