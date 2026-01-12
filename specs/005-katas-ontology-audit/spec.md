# Feature Specification: Katas Ontology Alignment Audit

**Feature Branch**: `005-katas-ontology-audit`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Analyze and recover katas from /home/emilio/Code/raise-commons/src/katas that align with current RaiSE ontology v2.1, applying KISS DRY YAGNI principles to identify essential katas for v0 framework versus project-specific customizations"

## Core Concept: Ontology-Driven Kata Ecosystem

**Principle:** The RaiSE ontology v2.1 defines what Katas SHOULD exist. This feature audits existing katas against this ontology-defined target state, not through ad-hoc classification.

**Ontology Source of Truth:**
- `docs/framework/v2.1/model/20-glossary-v2.1.md` → Kata definition and levels
- `docs/framework/v2.1/model/21-methodology-v2.md` → Kata levels, examples, and expected coverage

### Ontology-Defined Kata Structure

The ontology defines four semantic levels, each with a specific purpose and expected coverage:

| Level | Question | Purpose | Deviation Signal | Lean Connection | Expected Coverage |
|-------|----------|---------|------------------|-----------------|-------------------|
| **Principios** | ¿Por qué? ¿Cuándo? | Apply Constitution | "Cannot justify" | Toyota Way | Orchestrator role, Heutagogy |
| **Flujo** | ¿Cómo fluye? | Value sequences | "Missing input" | Value Stream | Discovery, Planning, Plan Generation |
| **Patrón** | ¿Qué forma? | Recurring structures | "Incorrect output" | Standardized Work | Tech Design, Code Analysis |
| **Técnica** | ¿Cómo hacer? | Specific instructions | "Validation fails" | Work Instructions | Data Modeling, API Design |

**Target Location:** `raise-config/katas/{level}/*.md`

**Structural Requirement:** All katas must implement Jidoka Inline (verification + correction guidance per step).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ontology Target State Definition (Priority: P1)

Framework maintainers need to derive from the ontology what Katas SHOULD exist for v0 RaiSE. This creates the "target state" against which existing katas are audited.

**Why this priority**: Without defining what SHOULD exist (from ontology), we cannot determine what's missing, what's extra, or what needs migration. The ontology IS the source of truth.

**Independent Test**: Can be tested by producing a "Kata Coverage Matrix" document that lists each ontology-defined slot and its expected coverage, derived directly from glossary and methodology documents.

**Acceptance Scenarios**:

1. **Given** the ontology defines 4 levels (Principios/Flujo/Patrón/Técnica), **When** the target state is defined, **Then** each level has explicit expected kata topics derived from methodology examples
2. **Given** the glossary defines "Jidoka Inline" as a kata requirement, **When** the target state is defined, **Then** structural requirements for kata format are documented
3. **Given** the ontology mentions specific examples (Heutagogy, Discovery, Tech Design, API Design), **When** the target state is defined, **Then** these appear as expected kata slots

---

### User Story 2 - Kata Ontology Mapping (Priority: P1)

Framework maintainers need to map each existing kata to its ontology-defined slot (if any). This produces three classifications:
- **Mapped**: Kata fills an ontology slot (potentially needing rename/restructure)
- **Gap**: Ontology slot with no kata filling it
- **Orphan**: Kata that doesn't fit any ontology slot (project-specific or deprecated)

**Why this priority**: This is the core audit—comparing "what exists" against "what should exist" per ontology.

**Independent Test**: Can be tested by producing a mapping table where each existing kata has an assignment (mapped to slot X, or orphan with rationale).

**Acceptance Scenarios**:

1. **Given** kata `L0-00-raise-katas-documentation.md` describes kata philosophy, **When** mapping runs, **Then** it's mapped to "Principios" level (Orchestrator role / kata purpose)
2. **Given** kata `L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md` is Jafra-specific, **When** mapping runs, **Then** it's classified as "Orphan" with marker "project-specific: Jafra"
3. **Given** ontology expects a "Discovery" kata at Flujo level, **When** mapping runs, **Then** if no kata fills this slot, it's marked as "Gap"

---

### User Story 3 - Migration Roadmap Generation (Priority: P2)

Framework maintainers need a concrete roadmap showing how to align the kata ecosystem with the ontology. This includes:
- Renaming katas to ontology-aligned naming (`L1-*` → `flujo-*`)
- Restructuring to add Jidoka Inline where missing
- Archiving orphan katas
- Flagging gaps for future creation

**Why this priority**: The audit (P1) tells us the current vs. target state; the roadmap tells us how to get there.

**Independent Test**: Can be tested by validating that the roadmap lists specific migration tasks with before/after naming conventions and structural changes required.

**Acceptance Scenarios**:

1. **Given** a mapped kata uses deprecated naming (`L1-04-*`), **When** roadmap is generated, **Then** it includes rename task to ontology-aligned name (`flujo-planning-*.md`)
2. **Given** a mapped kata lacks Jidoka Inline structure, **When** roadmap is generated, **Then** it includes restructure task with format requirements
3. **Given** an orphan kata is identified, **When** roadmap is generated, **Then** it's marked for archival with rationale referencing ontology

---

### User Story 4 - Kata Coverage Report (Priority: P3)

Framework maintainers need a coverage report showing v0 framework readiness: which ontology slots are filled, which have gaps, and overall alignment percentage.

**Why this priority**: Provides executive summary of ontology alignment for stakeholders and helps prioritize gap-filling work.

**Independent Test**: Can be tested by validating report includes coverage percentage per level and overall, with clear visualization of filled vs. empty slots.

**Acceptance Scenarios**:

1. **Given** the audit completes, **When** coverage report is generated, **Then** it shows percentage of ontology slots filled per level
2. **Given** gaps exist at Técnica level, **When** report is reviewed, **Then** it clearly lists which expected katas are missing
3. **Given** multiple orphans exist, **When** report is reviewed, **Then** it summarizes orphan count and primary reasons (project-specific, deprecated terminology, etc.)

---

### Edge Cases

- What if a kata partially fills multiple ontology slots? (Map to primary, note secondary coverage)
- What if ontology examples are ambiguous about expected coverage? (Use methodology as secondary source)
- What if an orphan kata has valuable generic patterns embedded? (Flag for extraction during future gap-filling)
- What if a kata uses correct level but wrong naming convention? (Map with rename-only task)

## Clarifications

### Session 2026-01-11

- Q: What format should the audit report and recovery roadmap use? → A: Multi-format output (both human-readable Markdown and machine-readable JSON versions)
- Q: How should katas be classified (essential/project-specific/hybrid)? → A: Spec rewritten to use **ontology-driven approach** instead. The ontology defines what SHOULD exist; katas are classified as Mapped (fills ontology slot), Orphan (no slot exists), or slots are marked as Gap (no kata fills it). This replaces ad-hoc classification with governance-as-code.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse ontology documents (glossary v2.1, methodology v2) to derive target kata coverage
- **FR-002**: System MUST analyze all kata files in `/home/emilio/Code/raise-commons/src/katas` directory
- **FR-003**: System MUST map each existing kata to an ontology-defined slot or classify as "Orphan"
- **FR-004**: System MUST identify "Gaps" (ontology slots with no kata filling them)
- **FR-005**: System MUST detect deprecated naming conventions (L0-L3 prefixes) and terminology (DoD, Rule, Developer)
- **FR-006**: System MUST validate kata structure against Jidoka Inline requirement (verification + correction per step)
- **FR-007**: System MUST generate a Kata Coverage Matrix showing target state vs. current state in both Markdown (human-readable) and JSON (machine-readable) formats
- **FR-008**: System MUST generate a migration roadmap with specific tasks (rename, restructure, archive) in both Markdown (human-readable) and JSON (machine-readable) formats
- **FR-009**: System MUST provide terminology migration mappings (L0→Principios, L1→Flujo, L2→Patrón, L3→Técnica, DoD→Validation Gate, etc.)
- **FR-010**: System MUST apply KISS/DRY/YAGNI to migration recommendations (minimal changes to achieve ontology alignment)

### Key Entities

- **Ontology Slot**: A position in the target kata ecosystem defined by the ontology
  - Attributes: level (Principios/Flujo/Patrón/Técnica), topic, expected coverage, source reference
  - Relationships: may be filled by zero or one Kata

- **Kata**: An existing kata file being audited
  - Attributes: file path, current name, current level prefix, content, Jidoka compliance status
  - Relationships: maps to zero or one Ontology Slot

- **Mapping Result**: The classification of a kata against the ontology
  - Types: Mapped (fills slot), Gap (no kata for slot), Orphan (no slot for kata)
  - Attributes: source kata (if Mapped/Orphan), target slot (if Mapped/Gap), rationale, migration tasks

- **Migration Task**: An actionable step to achieve ontology alignment
  - Types: Rename, Restructure (add Jidoka Inline), Archive, Create (for gaps)
  - Attributes: source, target, specific changes required

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of katas in `src/katas` are classified (Mapped, Orphan) with rationale
- **SC-002**: 100% of ontology-defined slots are identified (Filled, Gap) with source references
- **SC-003**: Kata Coverage Matrix shows clear target state derived from ontology documents
- **SC-004**: Migration roadmap includes specific tasks for each non-compliant kata (wrong naming, missing Jidoka Inline)
- **SC-005**: Orphan katas are clearly tagged with reason (project-specific marker, deprecated concept, no ontology slot)
- **SC-006**: Framework maintainers can determine v0 readiness from coverage percentages without re-reading all katas

## Assumptions

- The canonical source of truth for kata structure is `docs/framework/v2.1/model/20-glossary-v2.1.md`
- The canonical source for expected kata coverage is `docs/framework/v2.1/model/21-methodology-v2.md`
- Ontology examples (Heutagogy, Discovery, Tech Design, API Design) represent minimum expected kata topics per level
- Project-specific markers include: Jafra, SAR, PROSA PMO, specific client names, technology stacks tied to one project
- KISS/DRY/YAGNI principles favor minimal migration (rename > restructure > rewrite)
- Language (Spanish/English) is not an ontology concern; content alignment matters

## Dependencies

- Access to ontology documents in `docs/framework/v2.1/model/`
- Access to katas directory (`/home/emilio/Code/raise-commons/src/katas`)
- Clear understanding of Jidoka Inline format requirements from methodology

## Scope

### In Scope

- Parsing ontology to derive target kata ecosystem
- Auditing existing katas against ontology-defined structure
- Classifying katas as Mapped/Orphan and slots as Filled/Gap
- Generating coverage matrix and migration roadmap
- Identifying deprecated terminology and naming

### Out of Scope

- Actual migration/rename/restructure implementation (this feature only analyzes and plans)
- Translation of Spanish katas to English
- Creation of new katas to fill gaps
- Modification of existing kata files
- Validation of kata content accuracy (only structural/naming compliance)
- Katas in other directories (only `src/katas` is in scope)
