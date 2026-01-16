# Research: Katas Ontology Normalization

**Feature**: 006-katas-normalization
**Date**: 2026-01-11
**Purpose**: Consolidate research findings for kata normalization approach

## Executive Summary

This feature normalizes kata content (not file locations - already done in feature 005). The research confirms that all technical decisions are already defined in the ontology v2.1, requiring only consolidation rather than new decisions.

---

## Research Topics

### 1. Jidoka Inline Format Specification

**Question**: What is the exact format for Jidoka Inline structure in kata steps?

**Decision**: Use the format defined in `20-glossary-v2.1.md` §Jidoka:

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

**Rationale**: This format is the canonical definition from the ontology. Using any variant would violate Principle I (Coherencia Semántica).

**Alternatives Considered**:
- English format (`**Verification:**`) - Rejected: Spanish is canonical for RaiSE documentation
- Separate section for all verifications - Rejected: Defeats "inline" purpose of immediate feedback

**Source**: `docs/framework/v2.1/model/20-glossary-v2.1.md` lines 104-111

---

### 2. Terminology Mapping Completeness

**Question**: Are all deprecated terms identified for replacement?

**Decision**: Use the mapping from §Anti-Términos in glossary v2.1:

| Deprecated | Canonical | Regex Pattern |
|------------|-----------|---------------|
| DoD | Validation Gate | `\bDoD\b` |
| Developer | Orquestador | `\b[Dd]eveloper\b` (in role context) |
| Rule | Guardrail | `\b[Rr]ule\b` (in governance context) |
| L0 | principios | `\bL0\b` |
| L1 | flujo | `\bL1\b` |
| L2 | patrón | `\bL2\b` |
| L3 | técnica | `\bL3\b` |

**Rationale**: These are the explicit deprecated terms listed in the glossary v2.1. The list is closed - no additional terms need replacement.

**Context-Sensitive Replacements**:
- "Developer" in code examples → Preserve (refers to software, not human role)
- "Rule" in business rules context → Preserve (not governance concept)
- Proper nouns containing deprecated terms → Preserve with clarification note

**Source**: `docs/framework/v2.1/model/20-glossary-v2.1.md` §Anti-Términos (lines 342-354)

---

### 3. Semantic Level Guiding Questions

**Question**: How to validate kata content against its semantic level?

**Decision**: Use the guiding questions from §Kata in glossary v2.1:

| Level | Guiding Question | Validation Heuristic |
|-------|------------------|---------------------|
| Principios | ¿Por qué? ¿Cuándo? | Content explains rationale, timing, or philosophy |
| Flujo | ¿Cómo fluye? | Content describes sequences, workflows, value streams |
| Patrón | ¿Qué forma? | Content describes recurring structures, templates |
| Técnica | ¿Cómo hacer? | Content provides specific instructions, procedures |

**Rationale**: These questions are the ontology's definition of level semantics. A kata is misaligned if its content primarily answers a different level's question.

**Validation Process**:
1. Read kata content
2. Identify the primary question it answers
3. Compare to expected question for its level
4. If mismatch → Flag for reclassification (do not proceed with normalization)

**Source**: `docs/framework/v2.1/model/20-glossary-v2.1.md` lines 126-134

---

### 4. Step Header Format Variations

**Question**: What step header formats exist in current katas that need standardization?

**Decision**: Standardize to `### Paso N: [Acción]` format.

**Observed Variations** (from migration-roadmap.md analysis):
- `### Paso 1:` (correct)
- `### Step 1:` (English - needs translation)
- `## 1.` (missing "Paso" - needs restructure)
- `**1.**` (bold numbering - needs restructure)
- Unnumbered headers (needs numbering)

**Rationale**: Consistent format enables Jidoka Inline structure recognition and tooling.

**Transformation Rules**:
1. English "Step" → Spanish "Paso"
2. Missing "Paso" prefix → Add "Paso N: "
3. Wrong heading level → Convert to `###`
4. Bold numbering → Convert to heading

---

### 5. Preservation Rules

**Question**: What content must be preserved during normalization?

**Decision**: Preserve ALL existing content; only ADD structural elements.

**Preservation Rules**:
- Original instructions text → Verbatim preservation
- Existing verification text (non-standard format) → Move to `**Verificación:**` format
- Existing notes or warnings → Preserve inline
- Code blocks → Preserve unchanged
- Links and references → Preserve unchanged
- Language (Spanish/English) → Preserve as-is

**Addition Rules**:
- Add `**Verificación:**` after step instructions if missing
- Add `> **Si no puedes continuar:**` after verification if missing
- Generate verification/correction content based on step purpose

**Rationale**: Normalization should not alter kata semantics, only add structural elements.

---

## Unknowns Resolved

| Unknown | Resolution | Source |
|---------|------------|--------|
| Jidoka Inline format | Defined in glossary | 20-glossary-v2.1.md:104-111 |
| Terminology mapping | Closed list in §Anti-Términos | 20-glossary-v2.1.md:342-354 |
| Level validation | Guiding questions in §Kata | 20-glossary-v2.1.md:126-134 |
| Step format | Standardize to `### Paso N:` | Consistent with glossary examples |
| Preservation scope | Add-only; no content removal | Principle IV (Simplicidad) |

---

## Dependencies Validated

| Dependency | Status | Notes |
|------------|--------|-------|
| Feature 005 migration | ✅ Complete | Katas in semantic directories |
| Glossary v2.1 | ✅ Available | Source of truth for format |
| Migration roadmap | ✅ Available | Priority order defined |

---

## Recommendations

1. **Process first kata as pilot** - Validate approach on `principios/00-raise-katas-documentation.md` before proceeding
2. **Generate verification content contextually** - Each step's verification should reflect its specific action
3. **Document edge cases encountered** - Capture unexpected patterns for future reference
4. **Commit after each kata** - Maintain atomic changes for rollback capability
