# Feature Specification: Katas Ontology Normalization

**Feature Branch**: `006-katas-normalization`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Normalizar las katas migradas (en src/katas/principios/, flujo/, patron/) al contexto de la ontología v2.1. Trabajo una kata a la vez para aplicar: (1) Estructura Jidoka Inline obligatoria en cada paso (Verificación + Si no puedes continuar), (2) Actualización de terminología deprecated (DoD→Validation Gate, Developer→Orquestador, Rule→Guardrail, L0-L3→principios/flujo/patron/tecnica), (3) Coherencia semántica con glosario canónico. Basado en migration-roadmap.md del feature 005."

## Clarifications

### Session 2026-01-11

- Q: When semantic level misalignment is detected, should we proceed with changes or stop? → A: Stop processing that kata; flag for reclassification decision before continuing

## Context: Building on Feature 005

This feature continues the work initiated in `005-katas-ontology-audit`, which:
- Audited existing katas against ontology v2.1
- **Completed**: Renamed/moved katas to semantic directories (`principios/`, `flujo/`, `patron/`)
- **Completed**: Archived 6 project-specific orphan katas
- **Pending**: Internal normalization of kata content (this feature's scope)

**Reference Documents**:
- `specs/005-katas-ontology-audit/outputs/migration-roadmap.md` → Migration tasks MIG-RST-* and MIG-TERM-*
- `docs/framework/v2.1/model/20-glossary-v2.1.md` → Canonical terminology

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Jidoka Inline Structure Application (Priority: P1)

Framework maintainers need each kata step to include embedded verification and correction guidance, following the Jidoka Inline format defined in the ontology v2.1. This transforms passive documentation into active quality sensors.

**Why this priority**: Jidoka Inline is the core structural requirement that enables katas to function as "deviation detectors" per the ontology definition. Without this structure, katas remain passive documentation.

**Independent Test**: Can be tested by verifying a single kata file contains the required format in each step: action header, instructions, `**Verificación:**` line, and `> **Si no puedes continuar:**` block.

**Acceptance Scenarios**:

1. **Given** a kata step without Jidoka structure, **When** normalization is applied, **Then** the step includes `**Verificación:** [how to know it worked]` immediately after instructions
2. **Given** a kata step without correction guidance, **When** normalization is applied, **Then** the step includes `> **Si no puedes continuar:** [Cause → Resolution]` as a blockquote
3. **Given** a kata with partial Jidoka (verification but no correction), **When** normalization is applied, **Then** the missing correction guidance is added while preserving existing verification
4. **Given** a kata with full Jidoka compliance, **When** normalization runs, **Then** no changes are made to that kata

---

### User Story 2 - Deprecated Terminology Update (Priority: P1)

Framework maintainers need all deprecated terms replaced with their canonical equivalents from the ontology v2.1 glossary. This ensures semantic coherence across the kata ecosystem.

**Why this priority**: Terminology consistency is required for governance-as-code. Deprecated terms create confusion and violate the ontology contract.

**Independent Test**: Can be tested by searching a normalized kata for deprecated terms (DoD, Rule as governance, Developer as role, L0-L3) and confirming zero matches.

**Acceptance Scenarios**:

1. **Given** a kata containing "DoD", **When** normalization is applied, **Then** all occurrences are replaced with "Validation Gate"
2. **Given** a kata containing "Developer" (referring to the human role), **When** normalization is applied, **Then** all occurrences are replaced with "Orquestador"
3. **Given** a kata containing "Rule" (as governance concept), **When** normalization is applied, **Then** all occurrences are replaced with "Guardrail"
4. **Given** a kata referencing "L0", "L1", "L2", or "L3" levels, **When** normalization is applied, **Then** references are updated to "principios", "flujo", "patrón", or "técnica" respectively
5. **Given** a kata with no deprecated terminology, **When** normalization runs, **Then** no terminology changes are made

---

### User Story 3 - Semantic Level Coherence (Priority: P2)

Framework maintainers need each kata to answer the guiding question for its semantic level, ensuring the kata's content matches its classification.

**Why this priority**: Katas misaligned with their level create cognitive dissonance and undermine the ontology's pedagogical structure.

**Independent Test**: Can be tested by reviewing a kata's content against its level's guiding question and confirming coherence.

**Acceptance Scenarios**:

1. **Given** a kata in `principios/`, **When** reviewed for coherence, **Then** its content primarily answers "¿Por qué?" or "¿Cuándo?"
2. **Given** a kata in `flujo/`, **When** reviewed for coherence, **Then** its content primarily answers "¿Cómo fluye?" (describes value sequences)
3. **Given** a kata in `patron/`, **When** reviewed for coherence, **Then** its content primarily answers "¿Qué forma?" (describes recurring structures)
4. **Given** a kata incorrectly classified during migration, **When** coherence review identifies misalignment, **Then** processing stops for that kata and it is flagged for Orquestador reclassification decision before any Jidoka/terminology changes are applied

---

### User Story 4 - Incremental Processing with Validation (Priority: P2)

Framework maintainers need to normalize katas one at a time, with explicit validation after each, to enable iterative review and course correction.

**Why this priority**: Batch processing risks propagating errors across multiple files. Incremental processing follows Jidoka principles (detect-stop-correct-continue).

**Independent Test**: Can be tested by processing one kata and observing that the workflow pauses for validation before proceeding to the next.

**Acceptance Scenarios**:

1. **Given** a list of katas to normalize, **When** the workflow starts, **Then** it processes exactly one kata before requesting validation
2. **Given** a kata has been normalized, **When** validation is requested, **Then** the Orquestador can approve, request changes, or skip
3. **Given** a kata normalization is approved, **When** proceeding, **Then** the next kata in priority order is processed
4. **Given** a kata normalization requires changes, **When** the Orquestador provides feedback, **Then** adjustments are made before re-validation

---

### Edge Cases

- What if a kata step already has verification but uses non-standard phrasing? (Standardize to `**Verificación:**` format while preserving meaning)
- What if "Developer" appears in a code example context? (Preserve as-is; only replace when referring to the human role)
- What if a deprecated term is part of a proper noun or project name? (Preserve proper nouns; add clarification note if ambiguous)
- What if a kata has zero actionable steps (purely introductory)? (Flag for review; may need restructuring or reclassification)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process katas one at a time in priority order defined by `migration-roadmap.md`
- **FR-002**: System MUST add Jidoka Inline structure to each step lacking verification or correction guidance
- **FR-003**: System MUST preserve existing content while adding structural elements
- **FR-004**: System MUST replace deprecated terms with canonical equivalents per glossary v2.1:
  - DoD → Validation Gate
  - Developer → Orquestador (when referring to human role)
  - Rule → Guardrail (when referring to governance concept)
  - L0/L1/L2/L3 → principios/flujo/patrón/técnica
- **FR-005**: System MUST validate semantic coherence of kata content against its level's guiding question
- **FR-005a**: System MUST stop processing a kata and flag it for reclassification if semantic misalignment is detected (no Jidoka/terminology changes applied until Orquestador decides)
- **FR-006**: System MUST pause after each kata normalization for Orquestador validation
- **FR-007**: System MUST generate a normalization report showing changes made per kata
- **FR-008**: System MUST NOT modify katas that already fully comply with v2.1 standards
- **FR-009**: System MUST preserve kata language (Spanish/English) as-is during normalization
- **FR-010**: System MUST update kata metadata headers if present (version, date, status)

### Key Entities

- **Kata**: A structured process document in `src/katas/{level}/`
  - Attributes: file path, level, steps, Jidoka compliance status, terminology status
  - Relationships: Belongs to one semantic level

- **Step**: An actionable unit within a kata
  - Attributes: header, instructions, verification (optional), correction guidance (optional)
  - Format: `### Paso N: [Acción]` + content + `**Verificación:**` + `> **Si no puedes continuar:**`

- **Terminology Mapping**: Deprecated-to-canonical term pairs
  - Source: `20-glossary-v2.1.md` §Anti-Términos
  - Applied: During terminology update pass

- **Normalization Report**: Record of changes per kata
  - Attributes: kata path, Jidoka changes count, terminology changes count, coherence notes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of katas in `src/katas/{principios,flujo,patron}/` have Jidoka Inline structure in every step
- **SC-002**: 0 occurrences of deprecated terms (DoD, Rule as governance, Developer as role, L0-L3) in active katas
- **SC-003**: Each kata's content aligns with its semantic level's guiding question (verified by Orquestador review)
- **SC-004**: Normalization report generated for each processed kata showing all changes
- **SC-005**: Orquestador validates each kata before proceeding to the next (incremental approval)
- **SC-006**: Existing kata functionality and meaning preserved (no semantic loss during normalization)

## Assumptions

- The canonical source for terminology is `docs/framework/v2.1/model/20-glossary-v2.1.md`
- The Jidoka Inline format is: `**Verificación:**` + `> **Si no puedes continuar:**`
- Katas were correctly classified during feature 005 migration (level assignments are accurate)
- Orquestador will be available for incremental validation (not a batch operation)
- Spanish language is preferred for new structural elements (Verificación, Si no puedes continuar)
- Priority order follows `migration-roadmap.md` task IDs (MIG-RST-001 through MIG-RST-011, then MIG-TERM-*)

## Dependencies

- Completed migration from feature 005 (katas in `src/katas/{principios,flujo,patron}/`)
- Access to `specs/005-katas-ontology-audit/outputs/migration-roadmap.md` for priority order
- Access to `docs/framework/v2.1/model/20-glossary-v2.1.md` for terminology mapping
- Orquestador availability for incremental validation

## Scope

### In Scope

- Adding Jidoka Inline structure to all kata steps
- Replacing deprecated terminology with canonical equivalents
- Validating semantic coherence with kata levels
- Generating normalization reports
- Processing katas incrementally with validation gates

### Out of Scope

- Creating new katas to fill gaps (separate feature)
- Translating katas between languages
- Modifying archived/orphan katas in `archive/projects/`
- Changing kata classifications (only flagging misalignments)
- Adding new content beyond structural requirements
- Katas in `src/katas/cursor_rules/` (different governance scope)
