---
story_id: "S211.3"
title: "rai memory build → registry"
epic_ref: "RAISE-211"
status: "approved"
created: "2026-02-22"
complexity: "moderate"
modules: ["mod-governance", "mod-context"]
adrs: ["ADR-033", "ADR-034"]
---

# Design: S211.3 — rai memory build → registry

## 1. What & Why

**Problem:** GovernanceExtractor hardcodes 10 parser imports and file paths. Adding a governance parser requires modifying core code. The adapter Protocol contracts (S211.1) and entry point registry (S211.2) exist but have zero consumers — they're YAGNI until this story wires them.

**Value:** After this story, governance parsers are discovered via entry points. External packages can contribute parsers without modifying raise-cli. This is the proof point for the entire adapter foundation.

## 2. Approach

**Option B (confirmed):** Extractor keeps path/location knowledge. Delegates parsing to registry-discovered parsers instead of hardcoded imports.

Three components:

1. **Parser wrapper classes** — Thin classes in each parser module that conform to `GovernanceParser` Protocol. Wrap existing `extract_*` functions. Return `list[GraphNode]` by converting `Concept` → appropriate typed node.

2. **GovernanceExtractor refactor** — Same public API, new internals. Builds `ArtifactLocator` for each artifact type (paths stay hardcoded here). Queries registry for parsers via `get_governance_parsers()`. Delegates to matching parser via `can_parse()`.

3. **Entry point registration** — All parser wrappers registered in `pyproject.toml` under `rai.governance.parsers`.

**What does NOT change:**
- Existing `extract_*` functions (public API, used by `rai memory extract` CLI)
- `GovernanceExtractor.extract_from_file()` (backward compat for single-file extraction)
- `GovernanceExtractor.extract_with_result()` return type (`ExtractionResult` with `list[Concept]`)
- Builder's `load_work()` (separate path, not part of this refactor)
- `_concept_to_node()` stays in builder for non-governance uses

**Flow (before):**
```
Builder.load_governance()
  → Extractor.extract_all()
    → [10 hardcoded imports] → list[Concept]
  → [_concept_to_node(c) for c in concepts] → list[ConceptNode]
```

**Flow (after):**
```
Builder.load_governance()
  → Extractor.extract_all()
    → _build_locators() → list[ArtifactLocator]
    → get_governance_parsers() → dict[str, type]
    → for each locator: find parser via can_parse(), call parse()
    → list[GraphNode]  (parsers handle conversion internally)
  → list[GraphNode]  (no _concept_to_node loop needed)
```

**Layer dependency note:** Parser wrappers in `governance/parsers/` will import typed node classes from `context/models.py` (e.g., `RequirementNode`, `DecisionNode`). This is a new dependency direction (domain → integration models). Acceptable because:
- The `GovernanceParser` Protocol already requires `list[GraphNode]`
- It's a data model import, not behavior coupling
- `GraphNode` is the shared vocabulary of the system (ADR-033)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `governance/extractor.py` | `extract_all() → list[Concept]`, `extract_with_result() → ExtractionResult` | Internal: uses registry + locators instead of hardcoded imports. `extract_all()` returns `list[GraphNode]` | `extract_from_file()`, `extract_with_result()` (backward compat) |
| `governance/parsers/prd.py` | `extract_requirements(path, root) → list[Concept]` | Add `PrdParser` class | Function unchanged |
| `governance/parsers/vision.py` | `extract_outcomes(path, root) → list[Concept]` | Add `VisionParser` class | Function unchanged |
| `governance/parsers/constitution.py` | `extract_principles(path, root) → list[Concept]` | Add `ConstitutionParser` class | Function unchanged |
| `governance/parsers/roadmap.py` | `extract_releases(path, root) → list[Concept]` | Add `RoadmapParser` class | Function unchanged |
| `governance/parsers/backlog.py` | `extract_epics(path, root)`, `extract_project(path, root)` | Add `BacklogParser` class | Functions unchanged |
| `governance/parsers/epic.py` | `extract_epic_details(path, root)`, `extract_stories(path, root)` | Add `EpicScopeParser` class | Functions unchanged |
| `governance/parsers/adr.py` | `extract_all_decisions(root) → list[Concept]` | Add `AdrParser` class (per-file, receives locator) | Functions unchanged |
| `governance/parsers/guardrails.py` | `extract_all_guardrails(root) → list[Concept]` | Add `GuardrailsParser` class | Functions unchanged |
| `governance/parsers/glossary.py` | `extract_all_terms(root) → list[Concept]` | Add `GlossaryParser` class | Functions unchanged |
| `adapters/registry.py` | `get_governance_parsers() → dict[str, type]` | No changes | All functions |
| `adapters/models.py` | `ArtifactLocator`, `CoreArtifactType` | No changes | All models |
| `adapters/protocols.py` | `GovernanceParser` Protocol | No changes | All Protocols |
| `context/builder.py` | `load_governance() → list[ConceptNode]` | Simplified: extractor returns `list[GraphNode]` directly, no `_concept_to_node` loop | All other `load_*` methods, `_concept_to_node()` (used by `load_work()`) |
| `context/models.py` | `GraphNode`, typed subclasses, `ConceptNode` alias | No changes | Everything |
| `pyproject.toml` | No parser entry points | Add `rai.governance.parsers` group with 10 entries | Existing entry points |
| `cli/commands/memory.py` | `rai memory extract` uses `extract_with_result()` | No changes (backward compat via `ExtractionResult`) | CLI command |

## 4. Target Interfaces

### concept_to_node utility (extracted from builder)

```python
# governance/parsers/_convert.py
from rai_cli.context.models import ConceptNode
from rai_cli.governance.models import Concept

def concept_to_node(concept: Concept) -> ConceptNode:
    """Convert governance Concept to ConceptNode (GraphNode).

    Extracted from UnifiedGraphBuilder._concept_to_node() for reuse
    by parser wrappers. Builder's method becomes a thin delegation.

    Preserves section and lines in metadata (R3 from quality review):
    GraphNode has no section/lines fields, so these are stored in
    metadata to avoid silent data loss.
    """
```

### Parser wrapper pattern (6 simple parsers)

```python
# Example: governance/parsers/prd.py (added to existing module)
from rai_cli.adapters.models import ArtifactLocator, CoreArtifactType
from rai_cli.context.models import GraphNode
from rai_cli.governance.parsers._convert import concept_to_node

class PrdParser:
    """GovernanceParser wrapper for PRD requirements."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return locator.artifact_type == CoreArtifactType.PRD

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        path = Path(locator.metadata["project_root"]) / locator.path
        root = Path(locator.metadata["project_root"])
        concepts = extract_requirements(path, root)
        return [concept_to_node(c) for c in concepts]
```

Same pattern for: `VisionParser`, `ConstitutionParser`, `RoadmapParser`, `BacklogParser`, `EpicScopeParser`.

**BacklogParser note:** Wraps both `extract_project()` and `extract_epics()`. Also handles `_extract_work_concepts` merge logic currently in extractor.

**EpicScopeParser note:** Wraps `extract_epic_details()` and `extract_stories()`. Receives one locator per scope.md file.

### Explicit parsers (3 with internal path logic)

```python
# governance/parsers/adr.py (added to existing module)
class AdrParser:
    """GovernanceParser for ADR decisions. Handles per-file parsing."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return locator.artifact_type == CoreArtifactType.ADR

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        """Parse single ADR file pointed to by locator."""
        path = Path(locator.metadata["project_root"]) / locator.path
        root = Path(locator.metadata["project_root"])
        concept = extract_decision_from_file(path, root)
        return [concept_to_node(concept)] if concept else []
```

```python
# governance/parsers/guardrails.py
class GuardrailsParser:
    """GovernanceParser for guardrail rules."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return locator.artifact_type == CoreArtifactType.GUARDRAILS

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        path = Path(locator.metadata["project_root"]) / locator.path
        root = Path(locator.metadata["project_root"])
        concepts = extract_guardrails(path, root)
        return [concept_to_node(c) for c in concepts]
```

```python
# governance/parsers/glossary.py
class GlossaryParser:
    """GovernanceParser for glossary terms."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return locator.artifact_type == CoreArtifactType.GLOSSARY

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        path = Path(locator.metadata["project_root"]) / locator.path
        root = Path(locator.metadata["project_root"])
        concepts = extract_glossary_terms(path, root)
        return [concept_to_node(c) for c in concepts]
```

### GovernanceExtractor refactored internals

```python
# governance/extractor.py
class GovernanceExtractor:
    def __init__(
        self,
        project_root: Path | None = None,
        parsers: dict[str, type] | None = None,
    ) -> None:
        """Initialize with optional DI for parsers (testing)."""

    def extract_all(self) -> list[GraphNode]:
        """Extract all governance concepts via registry parsers.

        Returns list[GraphNode] instead of list[Concept].
        """

    def extract_with_result(self) -> ExtractionResult:
        """Backward compat: keeps its own legacy path using direct extract_*
        imports. Does NOT call extract_all() — the two methods are independent
        paths. This avoids GraphNode→Concept back-conversion and preserves
        Concept fields (section, lines) that GraphNode doesn't carry.
        Marked for future deprecation once rai memory extract migrates to GraphNode.
        """

    def extract_from_file(self, file_path, concept_type=None) -> list[Concept]:
        """Unchanged — single-file extraction for CLI."""

    def _build_locators(self) -> list[ArtifactLocator]:
        """Build ArtifactLocators for all known artifact locations.

        Hardcodes paths (same as current). For ADR and epic_scope,
        globs to produce one locator per file.
        """

    def _find_parser(
        self, locator: ArtifactLocator, parsers: list[GovernanceParser]
    ) -> GovernanceParser | None:
        """Find first parser that can_parse this locator."""
```

### Builder simplified

```python
# context/builder.py
def load_governance(self) -> list[ConceptNode]:
    """Load governance concepts. Extractor returns GraphNode directly."""
    try:
        extractor = self._get_governance_extractor()
        return extractor.extract_all()  # Already list[GraphNode]
    except Exception:
        return []
```

### Entry points in pyproject.toml

```toml
[project.entry-points."rai.governance.parsers"]
prd = "rai_cli.governance.parsers.prd:PrdParser"
vision = "rai_cli.governance.parsers.vision:VisionParser"
constitution = "rai_cli.governance.parsers.constitution:ConstitutionParser"
roadmap = "rai_cli.governance.parsers.roadmap:RoadmapParser"
backlog = "rai_cli.governance.parsers.backlog:BacklogParser"
epic_scope = "rai_cli.governance.parsers.epic:EpicScopeParser"
adr = "rai_cli.governance.parsers.adr:AdrParser"
guardrails = "rai_cli.governance.parsers.guardrails:GuardrailsParser"
glossary = "rai_cli.governance.parsers.glossary:GlossaryParser"
```

**Note:** 9 entry points, not 10. The original "10 parsers" counted backlog as 2 (project + epics) and epic as 2 (details + stories), but each wrapper class handles its full artifact type.

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Zero regression:** `rai memory build` must produce functionally identical graph. Verified via snapshot test comparing node IDs + types before/after.
- **Backward compat (C1 fix):** `extract_with_result()` keeps its own legacy path with direct `extract_*` imports — does NOT call `extract_all()`. Two independent paths: `extract_all()` = new registry path returning `list[GraphNode]`, `extract_with_result()` = legacy path returning `ExtractionResult` with `list[Concept]`. No back-conversion needed. Mark `extract_with_result()` as deprecated for future cleanup.
- **Graceful degradation:** Broken parser logs warning, build continues (already in `_discover()` in registry.py).
- **No SchemaProvider:** Extractor keeps path knowledge. YAGNI per scope.md.
- **`_concept_to_node()` stays in builder:** Used by `load_work()` which is NOT refactored in this story. Extracted copy in `_convert.py` for parser wrappers.
