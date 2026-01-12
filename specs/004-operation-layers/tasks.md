# Tasks: Ciclos de Trabajo RaiSE

**Input**: Design documents from `/specs/004-operation-layers/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Project Type**: Documentación ontológica (Markdown + Git)
**Tests**: Validation Gates (Gate-Terminología, Gate-Coherencia, Gate-Estructura)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Verificar estructura y preparar archivos base

- [x] T001 Verificar que existe directorio `docs/framework/v2.1/model/`
- [x] T002 [P] Revisar formato de documentos existentes en `docs/framework/v2.1/model/` para consistencia

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Leer documentos de referencia necesarios para todos los user stories

**⚠️ CRITICAL**: No se puede redactar sin entender la ontología existente

- [x] T003 Leer `docs/framework/v2.1/model/21-methodology-v2.md` para validar fases
- [x] T004 [P] Leer `docs/framework/v2.1/model/20-glossary-v2.1.md` para entender formato de entradas
- [x] T005 [P] Leer `src/katas/cursor_rules/L0-01-gestion-integral-reglas-cursor.md` para referencias de Onboarding

**Checkpoint**: Contexto ontológico cargado - redacción puede comenzar

---

## Phase 3: User Story 1 - Orquestador Identifica Ciclo (Priority: P1) 🎯 MVP

**Goal**: Crear documento principal con definiciones de los 4 ciclos y tabla resumen

**Independent Test**: Un Orquestador puede responder "¿Qué ciclo aplica para X?" consultando el documento

### Implementation for User Story 1

- [x] T006 [US1] Crear estructura base de `docs/framework/v2.1/model/26-work-cycles-v2.1.md` con frontmatter y secciones
- [x] T007 [US1] Escribir sección "Definición de Work Cycle" siguiendo data-model.md
- [x] T008 [US1] Escribir sección "Ciclo de Onboarding" con trigger, unidad, fases, katas referenciadas
- [x] T009 [P] [US1] Escribir sección "Ciclo de Proyecto" con trigger, unidad, fases, nota de "sin katas formales"
- [x] T010 [P] [US1] Escribir sección "Ciclo de Feature" con trigger, unidad, fases, cobertura spec-kit
- [x] T011 [P] [US1] Escribir sección "Ciclo de Mejora" con trigger, unidad, fases, cobertura parcial
- [x] T012 [US1] Crear tabla resumen de ciclos (Ciclo, Trigger, Unidad, Fases, Katas, spec-kit)
- [x] T013 [US1] Añadir diagrama de relaciones entre ciclos (ASCII art de data-model.md)
- [x] T014 [US1] Añadir sección "Edge Cases" (proyectos pequeños, repos sin onboarding)

**Checkpoint**: User Story 1 completado - documento principal listo para consulta

---

## Phase 4: User Story 2 - Contributor Diseña raise-kit (Priority: P2)

**Goal**: Añadir columna/sección que muestre cobertura spec-kit vs gaps para raise-kit

**Independent Test**: Un contributor puede listar qué comandos nuevos necesita raise-kit

### Implementation for User Story 2

- [x] T015 [US2] Añadir columna "Cobertura spec-kit" a tabla resumen en `26-work-cycles-v2.1.md`
- [x] T016 [US2] Añadir sección "Implicaciones para Tooling" indicando qué ciclos no tienen herramienta
- [x] T017 [US2] Listar comandos spec-kit que aplican por ciclo (de data-model.md)

**Checkpoint**: User Story 2 completado - blueprint para raise-kit visible

---

## Phase 5: User Story 3 - Orquestador Consulta Glosario (Priority: P3)

**Goal**: Actualizar glosario con entrada "Work Cycle" y definiciones de los 4 ciclos

**Independent Test**: El término "Work Cycle" existe en el glosario con definición completa

### Implementation for User Story 3

- [x] T018 [US3] Leer estructura actual de `docs/framework/v2.1/model/20-glossary-v2.1.md`
- [x] T019 [US3] Añadir entrada "Work Cycle (Ciclo de Trabajo)" al glosario siguiendo formato existente
- [x] T020 [US3] Incluir tabla resumen de ciclos dentro de la entrada del glosario
- [x] T021 [US3] Añadir nota sobre relación Ciclos ↔ Fases (no son secuenciales)

**Checkpoint**: User Story 3 completado - glosario actualizado

---

## Phase 6: Validation & Polish

**Purpose**: Pasar Validation Gates y preparar para MR

- [x] T022 Gate-Terminología: Verificar que todos los términos nuevos están en glosario
- [x] T023 [P] Gate-Coherencia: Verificar que no hay contradicciones con `21-methodology-v2.md`
- [x] T024 [P] Gate-Estructura: Verificar que el documento sigue formato de v2.1
- [x] T025 Revisar referencias cruzadas entre `26-work-cycles-v2.1.md` y katas en `src/katas/cursor_rules/`
- [x] T026 Actualizar `CLAUDE.md` si hay cambios a Active Technologies

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Creates main document
- **User Story 2 (Phase 4)**: Depends on US1 (adds to existing document)
- **User Story 3 (Phase 5)**: Can run parallel to US2 (different file)
- **Validation (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

| Story | Depends On | File Modified |
|-------|------------|---------------|
| US1 | Foundational | `26-work-cycles-v2.1.md` (create) |
| US2 | US1 | `26-work-cycles-v2.1.md` (extend) |
| US3 | Foundational | `20-glossary-v2.1.md` (update) |

### Parallel Opportunities

```
Phase 2 (Foundational):
  T003 ─┬─ T004 ─┬─ T005  (all can run in parallel)

Phase 3 (US1):
  T006 → T007 → T008 → [T009, T010, T011 in parallel] → T012 → T013 → T014

Phase 4 + Phase 5 (US2 + US3):
  [T015, T016, T017] can run parallel to [T018, T019, T020, T021]
  (different files: 26-work-cycles vs 20-glossary)

Phase 6 (Validation):
  T022 ─┬─ T023 ─┬─ T024  (gates can run in parallel)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Documento principal creado y consultable
5. Puede mergearse como MVP si tiempo limitado

### Incremental Delivery

1. Setup + Foundational → Contexto listo
2. User Story 1 → Documento principal → **MVP entregable**
3. User Story 2 → Blueprint para raise-kit → Valor añadido
4. User Story 3 → Glosario actualizado → Coherencia terminológica
5. Validation → Gates passed → Ready for MR

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 26 |
| **Setup Tasks** | 2 |
| **Foundational Tasks** | 3 |
| **US1 Tasks** | 9 |
| **US2 Tasks** | 3 |
| **US3 Tasks** | 4 |
| **Validation Tasks** | 5 |
| **Parallel Opportunities** | 12 tasks marked [P] |
| **MVP Scope** | US1 only (12 tasks: T001-T014) |

---

## Notes

- [P] tasks = different sections or different files, no conflicts
- [Story] label maps task to specific user story
- Validation Gates replace traditional tests for documentation projects
- Commit after each phase or logical group
- References: `data-model.md` for schema, `quickstart.md` for user guidance
