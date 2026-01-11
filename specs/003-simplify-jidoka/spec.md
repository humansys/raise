# Feature Specification: Simplificar Exposición de Jidoka

**Feature Branch**: `003-simplify-jidoka`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Simplificar la exposición de Jidoka en documentación de Stage 0-1, presentándolo como 'Parar si algo falla' en lugar de los 4 pasos formales del TPS (Detectar → Parar → Corregir → Continuar). Los pasos formales se revelan en Stage 3. Esto elimina la barrera terminológica B-01 y conceptual B-02 (cluster Lean/TPS) reduciendo sobrecarga cognitiva en onboarding. Archivos afectados: glosario v2.1 y ontology-bundle v2.1. Reducción de complejidad proyectada: 5%. Implementa QW-01 del backlog de mejoras."

## Executive Summary

This feature simplifies how Jidoka is presented to new Orquestadores (learners at Stage 0-1) by removing Toyota Production System (TPS) terminology and presenting it with a simple, accessible interface: "Parar si algo falla" (Stop if something fails). The formal 4-step cycle (Detectar → Parar → Corregir → Continuar) is preserved but moved to Stage 3 documentation for advanced learners.

**Problem**: New Orquestadores encounter cognitive overload when onboarding due to Lean/TPS terminology that requires prerequisite knowledge of manufacturing methodologies.

**Solution**: Apply the ADR-009 pattern (Simple Interface + Internal Philosophy) to Jidoka, presenting a beginner-friendly definition upfront while preserving depth for advanced users.

**Impact**: 5% reduction in onboarding complexity, elimination of barriers B-01 (terminological) and B-02 (conceptual Lean/TPS cluster).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simplified Jidoka for New Learners (Priority: P1) 🎯 MVP

A new Orquestador is reading the RaiSE glossary for the first time during onboarding (Stage 0). They encounter the term "Jidoka" and need to understand it immediately without having background knowledge of Toyota Production System or Lean manufacturing.

**Why this priority**: This is the only user story for this feature. New learner comprehension is the core value delivered - without it, the barrier B-01/B-02 persists.

**Independent Test**: Can be fully tested by showing the updated glossary entry to a developer unfamiliar with TPS and measuring comprehension time. Delivers immediate value: new Orquestadores can understand Jidoka in <30 seconds without external research.

**Acceptance Scenarios**:

1. **Given** a new Orquestador reads the Jidoka entry in glossary v2.1 (Stage 0-1 section), **When** they see the definition, **Then** they understand the concept without needing to know TPS terminology
2. **Given** an advanced Orquestador reads the Jidoka entry (Stage 3 section), **When** they expand the details, **Then** they see the formal 4-step TPS cycle for deeper understanding
3. **Given** the glossary v2.1 is updated, **When** the ontology bundle v2.1 references Jidoka, **Then** it uses consistent terminology (simple version for general docs, detailed version for advanced sections)

---

### Edge Cases

- **What happens when** an Orquestador searches for "TPS" or "Toyota Production System" in the glossary?
  - Expected: These terms appear only in Stage 3 advanced sections or historical notes, not in primary definitions

- **What happens when** the simplified definition is referenced in other framework documents (ADRs, Constitution)?
  - Expected: Those documents use the simplified form unless they are explicitly Stage 3 content

- **What happens when** a user expects the full 4-step cycle in Stage 0-1?
  - Expected: A note or link points to the Stage 3 section for the detailed definition

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The glossary entry for "Jidoka" in `docs/framework/v2.1/model/20-glossary-v2.1.md` MUST present a simplified definition as the primary content (visible to Stage 0-1 learners)

- **FR-002**: The simplified definition MUST be ≤10 words and use accessible language (e.g., "Parar si algo falla" or "Stop work when you detect a problem")

- **FR-003**: The formal 4-step TPS definition (Detectar → Parar → Corregir → Continuar) MUST be preserved but moved to a Stage 3 section, historical note, or expandable details section within the same glossary entry

- **FR-004**: The ontology bundle document `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md` MUST be updated to reflect the simplified Jidoka presentation in sections targeting Stage 0-1 learners

- **FR-005**: All references to TPS, Lean, or "自働化" (Japanese term) MUST be moved to Stage 3 sections or noted as "advanced context"

- **FR-006**: The glossary MUST maintain a clear indicator (e.g., "Stage 0-1" vs "Stage 3") to show which definition applies to which learning stage

- **FR-007**: No new terminology MUST be introduced - "Jidoka" remains the canonical term, only the presentation structure changes

### Key Entities

- **Simplified Jidoka Definition (Stage 0-1)**: The accessible, <10-word explanation presented to new learners
  - Attributes: term ("Jidoka"), simple definition, example from RaiSE context, stage indicator

- **Formal Jidoka Definition (Stage 3)**: The complete 4-step TPS cycle with philosophical context
  - Attributes: term ("Jidoka"), full 4-step cycle, TPS origin, Japanese etymology, stage indicator

- **Glossary Entry**: The container for both definitions
  - Relationships: contains both simplified and formal definitions, belongs to glossary v2.1

- **Ontology Bundle Section**: References to Jidoka in the comprehensive framework documentation
  - Relationships: must align with glossary entry, respects stage-appropriate presentation

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The simplified Jidoka definition is ≤10 words (measurable via word count)

- **SC-002**: Stage 0-1 sections of glossary and ontology bundle contain ZERO references to "TPS", "Toyota Production System", "Lean", or "自働化" (measurable via text search)

- **SC-003**: Gate-Terminología passes: All terminology remains canonical, no new terms introduced, Jidoka term is preserved (verifiable against glossary v2.1 canonical list)

- **SC-004**: Gate-Coherencia passes: No contradictions with Constitution v2.0 principles (specifically §4 - Validation Gates and §8 - Simplicidad) or existing glossary definitions (verifiable via cross-reference check)

- **SC-005**: Complexity reduction of 5%: Proxy metric based on prerequisite concept count - Jidoka currently requires understanding TPS (1 additional concept), simplified version requires 0 prerequisites (reduction from N to N-1 concepts = 5% of ~20 Stage 0-1 concepts)

- **SC-006**: Comprehension time <30 seconds: New learners can read and understand the simplified definition without external research (testable via user study or proxy: reading time at 200 words/min for <10 words ≈ 3 seconds, leaving 27 seconds for comprehension)

## Scope & Boundaries *(mandatory)*

### In Scope

- Updating glossary entry for Jidoka in `docs/framework/v2.1/model/20-glossary-v2.1.md`
- Updating ontology bundle references in `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`
- Structuring definitions by learning stage (Stage 0-1 vs Stage 3)
- Preserving formal TPS definition for advanced learners

### Out of Scope

- Creating new documents (all changes are to existing files)
- Modifying Constitution or ADRs (this is documentation presentation only)
- Changing the fundamental meaning or philosophy of Jidoka
- Applying this pattern to other Lean concepts (QW-01 scope is Jidoka only; other concepts are separate features)
- Updating katas or exercises (those are addressed in future features)
- Translating to other languages (Spanish/English versions maintained separately)

## Dependencies & Assumptions *(mandatory)*

### Dependencies

- Depends on: Existing glossary v2.1 and ontology bundle v2.1 documents
- Depends on: ADR-009 pattern (Simple Interface + Internal Philosophy) already established
- Depends on: Learning path stages (Stage 0-1 vs Stage 3) defined in Feature 001

### Assumptions

- **Assumption 1**: New Orquestadores do not have background in Lean/TPS methodologies (based on Feature 001 analysis showing B-02 barrier)

- **Assumption 2**: The phrase "Parar si algo falla" accurately captures the essence of Jidoka for RaiSE context (validated against Constitution §4 and existing framework usage)

- **Assumption 3**: Stage 3 learners will seek out the detailed definition when they need deeper understanding (aligns with §5 Heutagogía principle)

- **Assumption 4**: Existing references to Jidoka in other docs (if any) use it as a principle, not requiring the 4-step cycle detail (to be verified during implementation)

## Risks *(mandatory)*

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Simplified definition loses important nuance | Medium | Medium | Preserve formal definition in Stage 3 section, cross-validate against Constitution §4 |
| Advanced users frustrated by "dumbed down" content | Low | Low | Clear stage indicators, formal definition readily accessible |
| Inconsistency between glossary and bundle | Low | High | Validation gate checks both documents, tasks ensure parallel updates |
| Breaking existing references in other docs | Low | Medium | Search all docs for Jidoka references before finalizing changes |

## Success Metrics (Post-Launch) *(optional)*

- Reduction in onboarding questions about Jidoka (baseline: unknown, target: measure in next cohort)
- Time to comprehension for new Orquestadores (baseline: unknown, target: <30 seconds)
- Feedback from Stage 0-1 learners on glossary clarity (target: >80% report understanding without additional research)

---

*Feature specification complete. Ready for `/speckit.plan`.*
