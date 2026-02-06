# F11.2 Graph Builder — Design Spec

> **Status:** DESIGNED
> **Epic:** E11 Unified Context Architecture
> **Size:** M (2 SP)
> **Created:** 2026-02-03

---

## Overview

Build a unified context graph by merging governance, memory, work, and skills into a single `UnifiedGraph` that can be queried for relevant context.

**Value:** Every skill invocation starts with relevant context. I don't re-discover patterns — I build on accumulated knowledge.

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    UnifiedGraphBuilder                      │
│                                                            │
│  load_governance() ─► GovernanceExtractor.extract_all()    │
│  load_memory()     ─► Read JSONL directly                  │
│  load_work()       ─► extract_epics(), extract_stories()  │
│  load_skills()     ─► Parse SKILL.md frontmatter (new)     │
│                                                            │
│  infer_relationships() ─► Explicit + heuristic edges       │
│                                                            │
│  build() ─► UnifiedGraph                                   │
└────────────────────────────────────────────────────────────┘
```

**Design decisions:**
- **KISS:** One builder class, no adapter abstraction
- **DRY:** Reuse existing extractors (E2, E8)
- **YAGNI:** Frontmatter only for skills, full rebuild (no incremental)

---

## Data Flow

### Source → ConceptNode Mapping

| Source | Extractor | Node Type | ID Format |
|--------|-----------|-----------|-----------|
| Constitution | `extract_principles()` | `principle` | `§N` |
| PRD | `extract_requirements()` | `requirement` | `req-rf-*` |
| Vision | `extract_outcomes()` | `outcome` | `outcome-*` |
| patterns.jsonl | Direct JSONL | `pattern` | `PAT-*` |
| calibration.jsonl | Direct JSONL | `calibration` | `CAL-*` |
| sessions/index.jsonl | Direct JSONL | `session` | `SES-*` |
| backlog.md | `extract_epics()` | `epic` | `E*` |
| epic-*.md | `extract_stories()` | `feature` | `F*.*` |
| SKILL.md | New parser | `skill` | `/name` |

### Field Mapping

**Governance Concept → ConceptNode:**
```python
ConceptNode(
    id=concept.id,
    type=concept.type.value,  # principle, requirement, outcome
    content=concept.content,
    source_file=concept.file,
    created=datetime.now().isoformat(),  # extraction time
    metadata=concept.metadata
)
```

**Memory JSONL → ConceptNode:**
```python
ConceptNode(
    id=record["id"],
    type=record["type"],  # pattern, calibration, session
    content=record.get("content") or record.get("summary", ""),
    source_file=f".rai/memory/{file_name}",
    created=record.get("created") or record.get("date"),
    metadata={k: v for k, v in record.items() if k not in core_fields}
)
```

**Skill YAML → ConceptNode:**
```python
ConceptNode(
    id=f"/{frontmatter['name']}",
    type="skill",
    content=frontmatter.get("description", ""),
    source_file=skill_path,
    created=file_mtime.isoformat(),
    metadata=frontmatter.get("metadata", {})
)
```

---

## Relationship Inference

### Explicit Edges (weight=1.0)

| Source Data | Edge Type | Logic |
|-------------|-----------|-------|
| Pattern `learned_from` field | `learned_from` | `PAT-* → SES-*` |
| Skill `raise.prerequisites` | `needs_context` | `/skill → /prereq` |
| Skill `raise.next` | `related_to` | `/skill → /next` |
| Feature in epic scope | `part_of` | `F*.* → E*` |

### Inferred Edges (weight=0.5-0.8)

| Heuristic | Edge Type | Weight | Logic |
|-----------|-----------|--------|-------|
| Pattern context matches skill name | `applies_to` | 0.7 | `PAT-* → /skill` |
| Shared keywords (≥2) | `related_to` | 0.5 | Any → Any |
| Principle number in requirement | `governed_by` | 0.8 | `req-* → §N` |

### Keyword Extraction

Reuse existing `extract_keywords()` from E2:
- Lowercase, split on non-alphanumeric
- Filter stopwords
- Return set of keywords

---

## CLI Command

Extend `raise graph build` with `--unified` flag:

```bash
# Existing behavior (governance only)
raise graph build

# New: unified graph with all sources
raise graph build --unified

# Custom output path
raise graph build --unified --output .raise/graph/unified.json
```

**Default output:** `.raise/graph/unified.json`

**Output format:**
```
Building unified context graph...
  ✓ Governance: 25 concepts (8 principles, 12 requirements, 5 outcomes)
  ✓ Memory: 50 concepts (35 patterns, 10 calibrations, 5 sessions)
  ✓ Work: 12 concepts (4 epics, 8 features)
  ✓ Skills: 12 concepts

Inferring relationships...
  ✓ Explicit: 45 edges
  ✓ Inferred: 23 edges

Graph: 99 nodes, 68 edges
  → Saved to .raise/graph/unified.json
```

---

## File Structure

```
src/raise_cli/context/
├── __init__.py       # Existing (F11.1)
├── models.py         # Existing (F11.1)
├── graph.py          # Existing (F11.1)
├── builder.py        # NEW - UnifiedGraphBuilder
└── extractors/
    └── skills.py     # NEW - SKILL.md frontmatter parser
```

---

## Public API

### UnifiedGraphBuilder

```python
class UnifiedGraphBuilder:
    """Builds unified graph from all context sources."""

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize builder with project root."""

    def build(self) -> UnifiedGraph:
        """Build unified graph from all sources.

        Returns:
            UnifiedGraph with all concepts and relationships.
        """

    def load_governance(self) -> list[ConceptNode]:
        """Load concepts from governance documents."""

    def load_memory(self) -> list[ConceptNode]:
        """Load concepts from memory JSONL files."""

    def load_work(self) -> list[ConceptNode]:
        """Load concepts from work tracking (backlog, epics)."""

    def load_skills(self) -> list[ConceptNode]:
        """Load concepts from skill YAML frontmatter."""

    def infer_relationships(
        self,
        nodes: list[ConceptNode]
    ) -> list[ConceptEdge]:
        """Infer relationships between concepts."""
```

### Skill Extractor

```python
def extract_skill_metadata(skill_path: Path) -> ConceptNode | None:
    """Extract metadata from SKILL.md frontmatter.

    Args:
        skill_path: Path to SKILL.md file.

    Returns:
        ConceptNode for the skill, or None if parsing fails.
    """

def extract_all_skills(skills_dir: Path) -> list[ConceptNode]:
    """Extract metadata from all skills in directory.

    Args:
        skills_dir: Path to .claude/skills/ directory.

    Returns:
        List of ConceptNode for each skill.
    """
```

---

## Test Strategy

| Test Area | Coverage |
|-----------|----------|
| `load_governance()` | Mock extractor, verify conversion |
| `load_memory()` | Real JSONL fixtures, verify all types |
| `load_work()` | Mock parsers, verify epic/feature nodes |
| `load_skills()` | Real SKILL.md fixtures, verify frontmatter parsing |
| `infer_relationships()` | Unit tests for each inference rule |
| `build()` | Integration test with all sources |
| CLI command | Invoke `--unified`, verify output |

**Target:** >90% coverage on new code.

---

## Dependencies

- F11.1 (UnifiedGraph, ConceptNode, ConceptEdge) ✓
- E2 GovernanceExtractor ✓
- E8 work parsers ✓
- PyYAML (already in deps for skill parsing)

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Extractor output incompatible | Medium | Adapter functions per source, fail fast |
| YAML parsing edge cases | Low | Use ruamel.yaml or pyyaml, handle errors gracefully |
| Graph too sparse | Low | Start with explicit edges, add inference |
| Graph too noisy | Low | Weight filtering in query (F11.3) |

---

## Out of Scope

- Incremental builds (full rebuild is fast enough)
- Vector embeddings
- Auto-rebuild on file changes
- Skill body parsing (frontmatter only)

---

## Done Criteria

- [ ] `UnifiedGraphBuilder` class with `build()` method
- [ ] All 4 sources loading correctly
- [ ] Explicit relationships created (weight=1.0)
- [ ] Inferred relationships created (weight<1.0)
- [ ] `raise graph build --unified` command works
- [ ] Tests passing (>90% coverage)
- [ ] Quality checks pass (ruff, pyright, bandit)

---

*Design complete: 2026-02-03*
*Ready for: /story-plan*
