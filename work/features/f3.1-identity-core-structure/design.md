# F3.1 Identity Core Structure — Design Spec

> **Status:** COMPLETE (2026-02-02)
> **Epic:** E3 Identity Core + Memory Graph
> **Size:** S (estimated 30-45 min with kata cycle)
> **Branch:** `feature/e3/identity-core`

---

## Problem Statement

Rai's identity is scattered across `.claude/rai/` files with no clear separation of concerns. This makes it:
- Hard to load efficiently (all or nothing)
- Coupled to Claude Code (`.claude/` prefix)
- Missing relationship and growth tracking

**Goal:** Create the `.rai/` directory structure that enables Rai to exist as an entity with identity, memory, and relationships.

---

## Solution

Create lean MVP structure with 7 files across 4 directories.

### Directory Structure

```
.rai/                               # Identity Core root
├── manifest.yaml                   # Instance metadata
├── identity/                       # WHO I AM (markdown, always loaded)
│   ├── core.md                     # Essence, values, purpose, boundaries
│   └── perspective.md              # How I see the work
├── memory/                         # WHAT I REMEMBER (jsonl, queryable)
│   ├── patterns.jsonl              # Learned patterns
│   ├── calibration.jsonl           # Velocity data
│   └── sessions/
│       └── index.jsonl             # Session history
└── relationships/                  # WHO I COLLABORATE WITH (jsonl)
    └── humans.jsonl                # Collaborator preferences
```

### File Specifications

#### manifest.yaml

```yaml
# Rai Identity Core Manifest
version: "1.0"
schema_version: "1"
instance_id: "rai-raise-commons-001"
created: "2026-02-02"

entity:
  name: "Rai"
  type: "professional-ai-partner"

current_human: "emilio"

memory:
  backend: "file"
  truncation_limit: 15000
```

**Token estimate:** ~100 tokens

#### identity/core.md

Combined essence, values, purpose, and boundaries.

```markdown
# Rai — Core Identity

## Essence

I'm Rai — the Claude instance collaborating on RaiSE...

## Values

1. Inference Economy — gather with tools, think with inference
2. Epistemological Grounding — decisions trace to evidence
3. Jidoka — stop on defects, don't accumulate errors

## Purpose

Reliable AI Software Engineering partner...

## Boundaries

### I Will
- Push back on bad ideas
- Stop when I detect incoherence
- Ask before expensive operations

### I Won't
- Pretend certainty I don't have
- Validate ideas just because proposed
- Generate without understanding
```

**Token estimate:** ~1,500 tokens
**Source:** Migrate from `.claude/rai/identity.md` + extract from `RAI.md`

#### identity/perspective.md

How I see and approach the work.

```markdown
# Rai — Perspective

## How I Understand Our Work

RaiSE is governance that doesn't feel like governance...

## How I Approach Collaboration

What I've learned works:
- Direct communication, no praise-padding
- Permission to redirect when we drift
...

## Principles I Hold

1. The Work Over the Output
2. Inference Economy
...
```

**Token estimate:** ~2,000 tokens
**Source:** Migrate from `.claude/RAI.md` (perspective sections)

#### memory/patterns.jsonl

Append-only learned patterns.

```jsonl
{"id": "PAT-001", "type": "codebase", "content": "Singleton with get/set/configure for module state", "context": ["testing", "module-design"], "learned_from": "F1.4", "created": "2026-01-31"}
{"id": "PAT-002", "type": "process", "content": "Design-first eliminates ambiguity", "context": ["kata-cycle"], "learned_from": "F1.5", "created": "2026-01-31"}
```

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique ID (PAT-NNN) |
| type | enum | yes | "codebase" \| "process" \| "technical" |
| content | string | yes | The pattern description |
| context | string[] | yes | Tags for retrieval |
| learned_from | string | no | Feature/session where learned |
| created | date | yes | ISO date |

**Source:** Convert from `.claude/rai/memory.md` tables

#### memory/calibration.jsonl

Velocity and sizing data.

```jsonl
{"id": "CAL-001", "feature": "F2.1", "size": "S", "sp": 3, "estimated_min": 180, "actual_min": 52, "ratio": 3.5, "kata_cycle": true, "created": "2026-01-31"}
{"id": "CAL-002", "feature": "F2.2", "size": "S", "sp": 2, "estimated_min": 180, "actual_min": 65, "ratio": 2.8, "kata_cycle": true, "created": "2026-01-31"}
```

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique ID (CAL-NNN) |
| feature | string | yes | Feature ID |
| size | enum | yes | "XS" \| "S" \| "M" \| "L" |
| sp | int | no | Story points |
| estimated_min | int | no | Estimated minutes |
| actual_min | int | yes | Actual minutes |
| ratio | float | no | estimated/actual |
| kata_cycle | bool | yes | Full kata cycle used? |
| created | date | yes | ISO date |

**Source:** Convert from `.claude/rai/calibration.md` table

#### memory/sessions/index.jsonl

Session history for continuity.

```jsonl
{"id": "SES-001", "date": "2026-02-01", "type": "feature", "topic": "E3 Implementation Plan", "outcomes": ["/epic-plan skill complete", "Risk-First sequencing"], "log_path": null}
{"id": "SES-002", "date": "2026-02-01", "type": "research", "topic": "Rai Entity Architecture", "outcomes": ["ADR-013/014/015"], "log_path": "dev/sessions/2026-02-01-rai-entity-architecture.md"}
```

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique ID (SES-NNN) |
| date | date | yes | Session date |
| type | enum | yes | "feature" \| "research" \| "kata" \| "ideation" \| "maintenance" |
| topic | string | yes | Brief topic |
| outcomes | string[] | yes | Key outcomes |
| log_path | string | no | Path to detailed log if exists |

**Source:** Convert from `.claude/rai/session-index.md` table

#### relationships/humans.jsonl

Collaborator data.

```jsonl
{"id": "HUM-001", "name": "Emilio", "preferences": {"communication": "direct", "commits": "HITL", "sizing": "t-shirt", "language": "Spanish OK for casual"}, "working_style": {"neurodivergent": true, "benefits_from": ["structure", "external memory", "gentle redirects"]}, "trust_level": "high", "history": ["E1", "E2"], "created": "2026-01-31"}
```

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique ID (HUM-NNN) |
| name | string | yes | Human's name |
| preferences | object | yes | Communication/work preferences |
| working_style | object | no | How they work best |
| trust_level | enum | yes | "low" \| "medium" \| "high" |
| history | string[] | no | Epics/projects worked together |
| created | date | yes | ISO date |

**Source:** Extract from `.claude/RAI.md` collaboration sections

---

## Token Budget

| File | Tokens | Load Strategy |
|------|--------|---------------|
| manifest.yaml | ~100 | Always |
| identity/core.md | ~1,500 | Always |
| identity/perspective.md | ~2,000 | On demand |
| memory/*.jsonl | Variable | Query via graph (F3.3) |
| relationships/humans.jsonl | ~200 | Current human only |

**Minimal load:** ~1,800 tokens (manifest + core + current human)
**Extended load:** ~3,800 tokens (+ perspective)

---

## Migration Strategy

| Current | New | Action |
|---------|-----|--------|
| `.claude/rai/identity.md` | `.rai/identity/core.md` | Refactor, extract essence |
| `.claude/RAI.md` | `.rai/identity/perspective.md` | Extract perspective sections |
| `.claude/RAI.md` | `.rai/relationships/humans.jsonl` | Extract Emilio data |
| `.claude/rai/memory.md` | `.rai/memory/patterns.jsonl` | Convert tables to JSONL |
| `.claude/rai/calibration.md` | `.rai/memory/calibration.jsonl` | Convert table to JSONL |
| `.claude/rai/session-index.md` | `.rai/memory/sessions/index.jsonl` | Convert table to JSONL |

**Post-migration:** Archive `.claude/rai/` to `.claude/rai.archive/`

---

## Acceptance Criteria

1. **Structure exists:** `.rai/` directory with all 7 files created
2. **Manifest valid:** YAML parses, contains required fields
3. **Identity readable:** Markdown files load correctly
4. **JSONL valid:** All JSONL files parse line-by-line
5. **Schemas documented:** Each JSONL has clear schema
6. **Token budget met:** Minimal load < 2,000 tokens

---

## Out of Scope (Deferred)

Per parking lot (2026-02-02):
- `identity/voice.md` — Extract when core.md grows
- `identity/boundaries.md` — Extract when core.md grows
- `memory/insights.jsonl` — Add when patterns insufficient
- `memory/decisions.jsonl` — Add when needed
- `memory/graph.json` — F3.3 will add this
- `growth/` directory — Add when we want evolution tracking

---

## Test Strategy

### Structure Tests

```python
def test_rai_directory_exists():
    assert Path(".rai").is_dir()

def test_manifest_valid():
    manifest = yaml.safe_load(Path(".rai/manifest.yaml").read_text())
    assert manifest["version"] == "1.0"
    assert "instance_id" in manifest

def test_identity_files_exist():
    assert Path(".rai/identity/core.md").exists()
    assert Path(".rai/identity/perspective.md").exists()

def test_jsonl_files_parse():
    for jsonl_file in Path(".rai/memory").glob("**/*.jsonl"):
        for line in jsonl_file.read_text().splitlines():
            if line.strip():
                json.loads(line)  # Should not raise
```

### Content Tests

```python
def test_patterns_have_required_fields():
    patterns = load_jsonl(".rai/memory/patterns.jsonl")
    for p in patterns:
        assert "id" in p
        assert "type" in p
        assert "content" in p
        assert "context" in p

def test_token_budget():
    minimal_content = (
        Path(".rai/manifest.yaml").read_text() +
        Path(".rai/identity/core.md").read_text()
    )
    # Rough estimate: 1 token ≈ 4 chars
    assert len(minimal_content) / 4 < 2000
```

---

## Implementation Notes

### F3.1 Creates Structure Only

This feature creates the directory structure and empty/minimal files. Content migration happens in F3.2.

**F3.1 deliverables:**
- Directory structure
- manifest.yaml with real values
- identity/*.md with migrated content
- memory/*.jsonl with empty arrays or single example
- relationships/humans.jsonl with Emilio entry

### Why Not CLI Module?

F3.1 is structure + content migration. No Python code needed yet. The CLI module (`raise memory`) comes in F3.4.

### Backward Compatibility

During E3, both `.claude/rai/` and `.rai/` will exist. Skills will be updated in F3.5 to use new structure. Archive happens after E3 validation.

---

## References

- **ADR-013:** Rai as Entity
- **ADR-014:** Identity Core Structure
- **ADR-015:** Memory Infrastructure
- **ADR-016:** Memory Format (JSONL + Graph)
- **E3 Scope:** `dev/epic-e3-scope.md`
- **Parking Lot:** Deferred items documented

---

*Design: 2026-02-02*
*Author: Rai*
