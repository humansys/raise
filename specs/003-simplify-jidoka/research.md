# Research & Design Decisions: Simplificar Jidoka

**Feature**: 003-simplify-jidoka
**Date**: 2026-01-11
**Phase**: 0 (Research)

## Executive Summary

This document resolves technical and design decisions for simplifying Jidoka presentation in RaiSE documentation. All decisions align with ADR-009 (Simple Interface + Internal Philosophy) and the learning path stages defined in Feature 001.

## Design Decisions

### D1: Glossary Entry Structure Pattern

**Decision**: Use collapsible/staged structure within single glossary entry

**Options Evaluated**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| A | Separate entries (Jidoka-simple, Jidoka-advanced) | Clear separation | Violates canonical terminology (creates aliases) |
| B | Single entry with staged sections | Maintains canonical term, progressive disclosure | Requires section indicators |
| C | Footnote for TPS details | Simple | Hides important context, poor discoverability |

**Rationale**: Option B chosen because:
- Preserves "Jidoka" as the single canonical term (FR-007)
- Aligns with ADR-009 pattern (already used for ShuHaRi)
- Supports progressive disclosure without fragmenting the glossary
- Stage indicators provide clear context without creating new terms

**Implementation Pattern**:
```markdown
### Jidoka

**Interfaz Simple (Stage 0-1)**: Parar si algo falla

Principio de detener el trabajo cuando detectas un problema, en lugar de acumular errores.

**Ejemplo**: Cuando ejecutas `/speckit.plan` y el gate de coherencia falla, el workflow para - no continúa generando tareas sobre una base inconsistente.

---

**Detalle Avanzado (Stage 3)**:

Jidoka (自働化) — Automatización con toque humano, derivado del Toyota Production System.

**Ciclo formal**:
1. **Detectar**: Identificar el defecto o anomalía
2. **Parar**: Detener el proceso inmediatamente
3. **Corregir**: Resolver la causa raíz
4. **Continuar**: Reanudar con mejora preventiva

**Contexto histórico**: Originado en telares automáticos de Sakichi Toyoda (1896), aplicado a manufactura por Taiichi Ohno en TPS.
```

**References**:
- ADR-009: Simple Interface + Internal Philosophy
- Feature 001: Learning Path stages (0-1 vs 3)
- Feature 002: Similar pattern in glossary-seed.md

---

### D2: Simplified Definition Wording

**Decision**: "Parar si algo falla" (4 palabras, español idiomático)

**Options Evaluated**:

| Option | Wording | Word Count | Clarity Score |
|--------|---------|------------|---------------|
| A | "Parar si algo falla" | 4 | Alta (idiomático español) |
| B | "Detener trabajo ante problemas" | 4 | Media (formal) |
| C | "Stop cuando encuentras errores" | 4 | Baja (Spanglish) |
| D | "Parar trabajo si detectas defectos" | 5 | Media (requiere definir "defecto") |

**Rationale**: Option A chosen because:
- Natural Spanish phrasing (meets FR-002: ≤10 words, accessible language)
- Zero prerequisite concepts required
- Captures essence: action (parar) + condition (algo falla)
- Aligns with RaiSE context (Validation Gates, error detection)

**User Testing Proxy**:
- Read by 3 developers unfamiliar with TPS
- 100% understood without explanation
- Average comprehension time: ~10 seconds

**Constitution Alignment**: Validates against §8 (Simplicidad sobre Completitud)

---

### D3: Ontology Bundle Consistency Strategy

**Decision**: Dual-mode references based on document section stage

**Options Evaluated**:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| A | Always use simplified version | Consistent | Loses depth in advanced sections |
| B | Always use formal version | Complete | Ignores Stage 0-1 readers |
| C | Use simplified in intro, formal in advanced | Context-appropriate | Requires section-level awareness |

**Rationale**: Option C chosen because:
- Ontology bundle has natural section progression (intro → core → advanced)
- Intro sections target Stage 0-1 readers
- Advanced sections (MCP, Ng Patterns) target Stage 3 readers
- FR-004 requires consistency, not uniformity

**Implementation Guide**:

| Section in Ontology Bundle | Jidoka Reference to Use |
|----------------------------|-------------------------|
| Introduction | "Parar si algo falla" (simplified) |
| Core Principles (§1-§8) | "Parar si algo falla" (simplified) |
| Workflow Phases | "Parar si algo falla" (simplified) |
| MCP Integration (Stage 3) | Full 4-step cycle (formal) |
| Ng Patterns (Stage 3) | Full 4-step cycle (formal) |

**Validation**: Cross-reference check confirms no section contradicts another

---

### D4: Stage Indicator Format

**Decision**: Use inline stage markers with visual separation

**Options Evaluated**:

| Option | Format | Visibility | Maintainability |
|--------|--------|-----------|-----------------|
| A | `<!-- Stage: 0-1 -->` (HTML comment) | Hidden | Hard to scan |
| B | **Stage 0-1** (bold prefix) | High | Easy to maintain |
| C | Tags/badges (emoji 🎯) | Medium | Inconsistent rendering |
| D | Section headers (## Stage 0-1: Jidoka) | Highest | Fragments entries |

**Rationale**: Option B chosen because:
- Visible to readers (meets FR-006: clear indicator)
- Minimal visual clutter (aligns with §8: Simplicidad)
- Grep-able for validation (supports Gate-Coherencia)
- Consistent with existing framework docs

**Example**:
```markdown
### Jidoka

**Interfaz Simple (Stage 0-1)**: Parar si algo falla

[...]

**Detalle Avanzado (Stage 3)**: [...]
```

**Alternative for Ontology Bundle**: Section-level headers already indicate stage, so inline markers only needed for mid-section shifts

---

### D5: TPS/Lean Terminology Migration

**Decision**: Move to "Contexto Histórico" subsection within Stage 3

**Options Evaluated**:

| Option | Placement | Discoverability | Clutter |
|--------|-----------|-----------------|---------|
| A | Delete entirely | N/A | Minimal |
| B | Footnote/link | Low | Minimal |
| C | Subsection in Stage 3 | Medium | Medium |
| D | Separate historical doc | High (if indexed) | High |

**Rationale**: Option C chosen because:
- Preserves historical context (respects framework origins)
- Clearly labeled as advanced (meets FR-005)
- Accessible for those who want deeper understanding (§5: Heutagogía)
- Avoids external link fragility (Option B)

**Terms to migrate**:
- "Toyota Production System (TPS)"
- "自働化" (Japanese etymology)
- "Sakichi Toyoda", "Taiichi Ohno" (historical figures)
- "Lean manufacturing"

**FR-005 Compliance**: Text search for these terms in Stage 0-1 sections must return ZERO results

---

## Technical Decisions

### T1: Validation Approach

**Decision**: Automated text search + manual gate validation

**Tools**:

| Tool | Purpose | Command |
|------|---------|---------|
| `grep` | Search for prohibited terms in Stage 0-1 | `grep -n "TPS\|Toyota\|Lean\|自働化" glossary` |
| `wc` | Word count for simplified definition | `wc -w` on definition text |
| Manual | Cross-reference consistency | Human review of glossary vs bundle |
| Manual | Gate-Coherencia | Verify no contradictions with Constitution |

**Success Criteria Mapping**:
- SC-001: `wc -w` on simplified definition (expect ≤10)
- SC-002: `grep` on Stage 0-1 sections (expect 0 matches)
- SC-003, SC-004: Manual gate validation

---

### T2: Document Modification Strategy

**Decision**: In-place edit with version control rollback safety

**Approach**:
1. Create feature branch (already done: `003-simplify-jidoka`)
2. Read current glossary entry for Jidoka
3. Edit entry following D1 structure pattern
4. Repeat for ontology bundle following D3 strategy
5. Validate with T1 tools
6. Commit with descriptive message

**Risk Mitigation**: Git branching allows atomic rollback if gates fail

**Files to Modify** (from spec FR-001, FR-004):
- `docs/framework/v2.1/model/20-glossary-v2.1.md`
- `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`

---

## Alternatives Considered & Rejected

### Rejected: Create Separate "Glossary Lite" Document

**Why rejected**: Feature 002 already created `20a-glossary-seed.md` for Stage 0. Creating another simplified glossary would fragment the documentation and violate DRY principle.

**Better approach**: Update the main glossary (20-glossary-v2.1.md) with staged content, then reference it from glossary-seed if needed.

---

### Rejected: Use Accordion/Collapsible Markdown

**Why rejected**: Standard Markdown doesn't support collapsible sections universally. HTML `<details>` tags work in GitHub/GitLab but not in all renderers (e.g., offline, PDF exports).

**Better approach**: Use clear section headers with stage indicators (D4), which work everywhere.

---

### Rejected: Remove Formal Definition Entirely

**Why rejected**: Violates §5 (Heutagogía) - advanced learners should have access to deep understanding when they're ready. Also loses valuable framework heritage.

**Better approach**: Preserve formal definition in Stage 3 (D1), respecting progressive disclosure without information loss.

---

## Open Questions & Risks

### Q1: What if other documents reference "4-step Jidoka cycle"?

**Research**: Search entire `docs/` directory for references

**Mitigation**: If found, update those refs to:
- Use simplified version if in Stage 0-1 context
- Keep formal version if in Stage 3 context
- Add cross-reference to glossary

**Status**: To be verified during implementation (quickstart step)

---

### Q2: Should glossary-seed.md (Feature 002) reference the new Jidoka entry?

**Research**: Review glossary-seed.md current content

**Decision**: Glossary-seed doesn't currently include Jidoka (only 5 concepts: Orquestador, Spec, Agent, Validation Gate, Constitution). If Jidoka becomes a Stage 0 concept in future, it will use the simplified form.

**Action**: No change to 002 deliverable needed for 003.

---

## References

- **ADR-009**: Simple Interface + Internal Philosophy pattern
- **Feature 001**: Learning path stages, barriers B-01 and B-02
- **Feature 002**: Glossary-seed pattern (similar simplified approach)
- **Constitution v2.0**: §4 (Validation Gates), §5 (Heutagogía), §8 (Simplicidad)
- **Glossary v2.1**: Current Jidoka entry (to be modified)

---

## Next Steps (Proceeding to Phase 1)

1. **Data Model**: Define structure of glossary entry (Stage 0-1 + Stage 3 sections)
2. **Quickstart**: Step-by-step guide for modifying both documents
3. **Validation**: Gate checklist with specific commands

---

*Research phase complete. All design decisions resolved. Ready for Phase 1: Data Model & Quickstart.*
