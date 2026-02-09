# S16.5: Component ID Uniqueness — Scope

> **Status:** Pending
> **Epic:** E16 Incremental Coherence
> **Size:** S
> **Priority:** High — silent data loss in graph
> **Created:** 2026-02-09

---

## Problem

The `raise discover analyze` command generates component IDs using the pattern `comp-{file_stem}-{name}`, where `file_stem` is the filename without extension. This creates **ID collisions** when different modules have files with the same name.

**Evidence (SES-121, 2026-02-09):**

Discovery validated 345 components, but only 335 appear in the graph. The 10 missing components are silently dropped because `UnifiedGraph.add_concept()` overwrites nodes with duplicate IDs.

### Affected IDs (8 collisions, 10 lost components)

| Duplicate ID | Colliding Files | Lost |
|---|---|---|
| `comp-models-models` | `memory/models.py`, `governance/models.py`, `context/models.py`, `context/analyzers/models.py` | 3 |
| `comp-writer-writer` | `memory/writer.py`, `telemetry/writer.py` | 1 |
| `comp-skills-skills` | `skills/__init__.py`, `onboarding/skills.py` | 1 |
| `comp-discover-discover` | `cli/commands/discover.py`, `output/formatters/discover.py` | 1 |
| `comp-skill-skill` | `cli/commands/skill.py`, `output/formatters/skill.py` | 1 |
| `comp-migration-migration` | `memory/migration.py`, `onboarding/migration.py` | 1 |
| `comp-profile-profile` | `cli/commands/profile.py`, `onboarding/profile.py` | 1 |
| `comp-main-main` | `cli/main.py`, `__main__.py` | 1 |

**Impact:** 3% data loss is silent. No errors, no warnings. The graph builder doesn't know it's overwriting different components with the same ID.

---

## Root Cause

In `src/raise_cli/discovery/analyzer.py`, the `_generate_id()` function uses only the file stem:

```python
# Current: comp-{file_stem}-{symbol_name}
# models.py in memory/ → comp-models-MemoryScope
# models.py in governance/ → comp-models-ConceptType
# models.py (module-level) → comp-models-models  ← COLLISION
```

The module-level entries are worst because both the file stem and the symbol name are the same.

---

## Proposed Fix

Change ID generation to include the **parent module path** relative to the package root:

```python
# New: comp-{dotted.module.path}-{symbol_name}
# memory/models.py → comp-memory.models-MemoryScope
# governance/models.py → comp-governance.models-ConceptType
# memory/models.py (module) → comp-memory.models-module
# governance/models.py (module) → comp-governance.models-module
```

### Tasks

1. **Update `_generate_id()` in analyzer.py** — Use the `module` field (already computed as dotted path) instead of file stem. Replace dots with hyphens for URL-safe IDs: `comp-memory-models-MemoryScope`.

2. **Update tests** — Existing analyzer tests assert on specific IDs. Update expected values.

3. **Verify uniqueness** — Add a post-analysis assertion that all component IDs are unique. Fail loudly if duplicates found (Jidoka — stop on defect).

4. **Re-run discovery pipeline** — After fix: scan → analyze → validate (auto-approve unchanged, review new) → complete → build graph. Verify 345 == 345 in graph.

5. **Add uniqueness check to graph builder** — `UnifiedGraphBuilder.load_components()` should warn (or error) when a component ID already exists in the graph.

---

## Acceptance Criteria

- [ ] All 345 validated components appear in the graph (0 silent drops)
- [ ] Component IDs are unique across the entire discovery catalog
- [ ] `raise discover analyze` fails if duplicate IDs would be generated
- [ ] Graph builder warns on component ID collision
- [ ] All existing tests pass with updated IDs
- [ ] Quality gates pass (ruff, pyright, pytest >90%)

---

## Scope Boundaries

**In scope:**
- Fix ID generation in analyzer
- Add uniqueness assertion
- Add graph builder collision warning
- Re-run discovery pipeline

**Out of scope:**
- Changing IDs of non-component nodes (patterns, decisions, etc.)
- Backward compatibility with old components-validated.json (overwrite is fine)
- Migration of existing graph data (graph is rebuilt from scratch each time)

---

## Size Rationale

**S-sized:** Mechanical fix in one function + test updates + pipeline re-run. No architectural decisions, no new models, no new modules. The fix is straightforward; the discovery pipeline run adds calendar time but not complexity.

---

## Dependencies

- **Blocked by:** Nothing (can be done immediately)
- **Blocks:** S16.2 (Graph Diff Engine) — diff accuracy depends on unique node IDs

---

## Pattern

This is an instance of **silent data loss from ID collision** — a variant of PAT-195 (scope wiring bugs are silent). The system produces correct-looking output with quietly wrong data. The fix follows Jidoka: make the defect impossible (unique IDs) and stop loudly if it occurs (assertions).
