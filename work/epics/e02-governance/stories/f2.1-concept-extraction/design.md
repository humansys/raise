---
story_id: "F2.1"
title: "Concept Extraction"
epic: "E2: Governance Toolkit"
story_points: 3
complexity: "moderate"
status: "design"
created: "2026-01-31"
---

# F2.1: Concept Extraction

## What & Why

**Problem**: RaiSE needs to extract semantic concepts from governance markdown files (PRD, Vision, Constitution) to build a concept-level graph that enables 97% token savings for AI context queries.

**Value**: Enables Minimum Viable Context (MVC) queries that return only relevant governance sections instead of entire files, reducing token usage from 13,657 to ~350 tokens for typical validation tasks.

## Approach

Build regex-based parsers that extract semantic concepts from structured markdown governance files:
- **Requirements** from PRD (RF-XX format sections)
- **Outcomes** from Vision (table rows)
- **Principles** from Constitution (§N sections)

Each parser produces `Concept` objects with metadata (type, file location, content, line numbers) that feed the graph builder (F2.2).

**Components affected**:
- CREATE: `src/raise_cli/governance/` (new module)
  - `parsers/prd.py` - Extract requirements
  - `parsers/vision.py` - Extract outcomes
  - `parsers/constitution.py` - Extract principles
  - `models.py` - Pydantic schemas for Concept
  - `extractor.py` - Orchestration interface
- CREATE: `tests/governance/` (test suite)

## Examples

### CLI Usage

```bash
# Extract concepts from single file
$ raise graph extract governance/projects/raise-cli/prd.md

Extracting concepts from prd.md...
  ✓ Found RF-01: Kata Engine
  ✓ Found RF-02: Gate Engine
  ✓ Found RF-05: Golden Context Generation
  ...
→ Extracted 8 requirements

# Extract from all governance files (default)
$ raise graph extract

Extracting concepts from governance files...
  📄 prd.md → 8 requirements
  📄 vision.md → 7 outcomes
  📄 constitution.md → 8 principles
→ Total: 23 concepts extracted

# Output as JSON
$ raise graph extract --format json
{
  "concepts": [
    {
      "id": "req-rf-05",
      "type": "requirement",
      "file": "governance/projects/raise-cli/prd.md",
      "section": "RF-05: Golden Context Generation",
      "lines": [206, 214],
      "content": "The system MUST generate CLAUDE.md...",
      "metadata": {
        "requirement_id": "RF-05",
        "title": "Golden Context Generation"
      }
    }
  ],
  "total": 23
}
```

### Python API

```python
from raise_cli.governance.extractor import GovernanceExtractor
from raise_cli.governance.models import Concept, ConceptType
from pathlib import Path

# Create extractor
extractor = GovernanceExtractor()

# Extract from single file
prd_path = Path("governance/projects/raise-cli/prd.md")
requirements = extractor.extract_from_file(prd_path, ConceptType.REQUIREMENT)

for req in requirements:
    print(f"{req.id}: {req.metadata['title']}")
    # Output: req-rf-05: Golden Context Generation

# Extract from all governance files
all_concepts = extractor.extract_all()
print(f"Total concepts: {len(all_concepts)}")
# Output: Total concepts: 23

# Filter by type
outcomes = [c for c in all_concepts if c.type == ConceptType.OUTCOME]
```

### Data Structures

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any

class ConceptType(str, Enum):
    """Types of concepts extracted from governance"""
    REQUIREMENT = "requirement"
    OUTCOME = "outcome"
    PRINCIPLE = "principle"
    PATTERN = "pattern"      # Future: from design docs
    PRACTICE = "practice"    # Future: from katas

class Concept(BaseModel):
    """A semantic concept extracted from governance markdown"""

    id: str = Field(..., description="Unique identifier (e.g., 'req-rf-05')")
    type: ConceptType = Field(..., description="Concept type")
    file: str = Field(..., description="Source file relative path")
    section: str = Field(..., description="Section heading")
    lines: tuple[int, int] = Field(..., description="Line range (start, end)")
    content: str = Field(..., description="Extracted content (truncated if long)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific metadata"
    )

class ExtractionResult(BaseModel):
    """Result of concept extraction operation"""

    concepts: list[Concept] = Field(default_factory=list)
    total: int = Field(..., description="Total concepts extracted")
    files_processed: int = Field(..., description="Number of files parsed")
    errors: list[str] = Field(default_factory=list)
```

## Acceptance Criteria

**MUST:**
- Extract requirements from PRD using regex pattern `### RF-\d+: (.+)`
- Extract outcomes from Vision markdown tables
- Extract principles from Constitution using regex pattern `### §\d+\. (.+)`
- Return `Concept` objects with complete metadata (id, type, file, section, lines, content)
- Handle missing files gracefully (skip with warning, not crash)
- Truncate long content (>500 chars) to avoid graph bloat
- CLI command `raise graph extract` functional
- >90% test coverage on parsers
- All parsers pass type checking (`pyright --strict`)

**SHOULD:**
- Detect and warn about malformed sections (missing RF-XX, §N patterns)
- Support `--format json` for machine-readable output
- Include source location (file:line) in error messages
- Log extraction statistics (concepts per file, total time)

**MUST NOT:**
- Extract from non-governance files (no code parsing in F2.1)
- Attempt relationship inference (deferred to F2.2)
- Build graph structure (deferred to F2.2)
- Require LinkML or complex schema tooling (regex is sufficient)

## Algorithm Details

### Requirements Parser (PRD)

```python
def extract_requirements(file_path: Path) -> list[Concept]:
    """Extract RF-XX requirements from PRD"""
    text = file_path.read_text()
    lines = text.split('\n')
    concepts = []

    for i, line in enumerate(lines, 1):
        # Match: ### RF-05: Golden Context Generation
        match = re.match(r'^### (RF-\d+):\s*(.+)$', line)

        if match:
            req_id = match.group(1)      # "RF-05"
            title = match.group(2)        # "Golden Context Generation"

            # Extract section content until next ###
            content_lines = []
            j = i
            while j < len(lines) and not lines[j].startswith('###'):
                content_lines.append(lines[j])
                j += 1

            # Truncate to first ~20 lines or 500 chars
            content = '\n'.join(content_lines[:20])
            if len(content) > 500:
                content = content[:500] + "..."

            concept = Concept(
                id=f"req-{req_id.lower()}",
                type=ConceptType.REQUIREMENT,
                file=str(file_path.relative_to(project_root)),
                section=f"{req_id}: {title}",
                lines=(i, min(i + 20, len(lines))),
                content=content.strip(),
                metadata={"requirement_id": req_id, "title": title}
            )
            concepts.append(concept)

    return concepts
```

### Outcomes Parser (Vision)

```python
def extract_outcomes(file_path: Path) -> list[Concept]:
    """Extract outcomes from Vision table"""
    # Detect table: | **Outcome** | Description |
    # Parse rows: | **Outcome Name** | Outcome description text |
    # Generate ID from name: outcome-context-generation
    # Return Concept objects
```

### Principles Parser (Constitution)

```python
def extract_principles(file_path: Path) -> list[Concept]:
    """Extract §N principles from Constitution"""
    # Match: ### §2. Governance as Code
    # Extract section content until next ###
    # Return Concept objects with principle metadata
```

## Constraints

**Performance:**
- Parse all raise-commons governance files (<10 files) in <1 second
- Memory usage <50MB for typical governance corpus

**Quality:**
- No false positives (every extracted concept must be valid)
- Tolerate false negatives (better to miss a concept than extract garbage)

**Compatibility:**
- Support Python 3.12+
- Work with existing governance file formats (no format changes required)

## Testing Approach

**Unit tests** for each parser:
```python
def test_extract_requirements():
    """Test PRD requirements extraction"""
    # Given: PRD with 3 requirements
    prd_content = """
    ### RF-01: First Requirement
    Description here...

    ### RF-02: Second Requirement
    More content...
    """

    # When: Extract requirements
    concepts = extract_requirements(prd_content)

    # Then: Should extract 2 requirements
    assert len(concepts) == 2
    assert concepts[0].id == "req-rf-01"
    assert concepts[0].metadata["title"] == "First Requirement"
```

**Integration test** for extractor:
```python
def test_extract_all_governance():
    """Test extraction from all governance files"""
    # Given: Real raise-commons governance files
    extractor = GovernanceExtractor()

    # When: Extract all concepts
    concepts = extractor.extract_all()

    # Then: Should extract 20+ concepts
    assert len(concepts) >= 20
    assert any(c.type == ConceptType.REQUIREMENT for c in concepts)
    assert any(c.type == ConceptType.OUTCOME for c in concepts)
    assert any(c.type == ConceptType.PRINCIPLE for c in concepts)
```

**Edge cases:**
- Empty files → Return empty list
- Malformed sections → Log warning, skip
- Missing governance directory → Graceful error message
- Special characters in titles → Sanitize for ID generation

## Dependencies

**Blocked by**: None (E1 foundation complete)

**Blocks**:
- F2.2 (Graph Builder) - needs `Concept` objects
- F2.3 (MVC Query Engine) - needs concept graph
- F2.4 (CLI Commands) - needs extraction working

**External dependencies**:
- Standard library only (re, pathlib, typing)
- Pydantic (already in project)
- No new packages required

## References

- **Spike validation**: `dev/experiments/concept_extraction_spike.py` (23 concepts extracted)
- **Architecture**: `dev/decisions/adr-011-concept-level-graph-architecture.md`
- **Epic scope**: `dev/epic-e2-scope.md`
- **Backlog**: `governance/projects/raise-cli/backlog.md` (E2 section)

---

*Created: 2026-01-31*
*Ready for: `/story-plan`*
