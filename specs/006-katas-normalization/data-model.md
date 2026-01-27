# Data Model: Katas Ontology Normalization

**Feature**: 006-katas-normalization
**Date**: 2026-01-11
**Purpose**: Define the structure of katas and normalization artifacts

## Overview

This feature operates on Markdown documents (katas) rather than database entities. The "data model" describes the structure of kata files and normalization reports.

---

## Entity: Kata

A structured process document that guides Orquestadores through a repeatable workflow.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file_path` | string | Absolute path to kata file (e.g., `src/katas/flujo/04-*.md`) |
| `level` | enum | Semantic level: `principios`, `flujo`, `patron`, `tecnica` |
| `title` | string | Kata title from first H1 heading |
| `steps` | Step[] | Array of actionable steps |
| `metadata` | object | Optional frontmatter (version, date, status) |

### Relationships

- **Belongs to**: One semantic level directory
- **Contains**: Multiple Steps
- **References**: Glossary terms, other katas

### Lifecycle States

```
┌──────────┐    normalize    ┌────────────┐    approve    ┌───────────┐
│  Legacy  │ ───────────────>│ Normalized │ ─────────────>│ Validated │
└──────────┘                 └────────────┘               └───────────┘
     │                             │
     │ misaligned                  │ rejected
     v                             v
┌────────────────┐          ┌──────────────┐
│ Flagged for    │          │ Pending      │
│ Reclassification│         │ Revision     │
└────────────────┘          └──────────────┘
```

---

## Entity: Step

An actionable unit within a kata that follows Jidoka Inline structure.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `number` | integer | Yes | Step sequence number (1-based) |
| `header` | string | Yes | Step title (e.g., "Analizar repositorio") |
| `instructions` | string | Yes | Main step content/instructions |
| `verification` | string | After norm | How to verify step completion |
| `correction` | string | After norm | Guidance when step fails |

### Format (Jidoka Inline)

```markdown
### Paso {number}: {header}

{instructions}

**Verificación:** {verification}

> **Si no puedes continuar:** {correction}
```

### Validation Rules

- `number` must be sequential (no gaps)
- `header` must be action-oriented (verb-noun)
- `verification` must be observable/testable
- `correction` must follow format: `[Causa] → [Resolución]`

---

## Entity: TerminologyMapping

A deprecated-to-canonical term pair used during normalization.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `deprecated` | string | Term to replace |
| `canonical` | string | Replacement term |
| `context` | string | When replacement applies |
| `pattern` | regex | Matching pattern |

### Instances (Closed Set)

```json
[
  {"deprecated": "DoD", "canonical": "Validation Gate", "context": "quality checkpoint", "pattern": "\\bDoD\\b"},
  {"deprecated": "Developer", "canonical": "Orquestador", "context": "human role", "pattern": "\\b[Dd]eveloper\\b"},
  {"deprecated": "Rule", "canonical": "Guardrail", "context": "governance", "pattern": "\\b[Rr]ule\\b"},
  {"deprecated": "L0", "canonical": "principios", "context": "kata level", "pattern": "\\bL0\\b"},
  {"deprecated": "L1", "canonical": "flujo", "context": "kata level", "pattern": "\\bL1\\b"},
  {"deprecated": "L2", "canonical": "patrón", "context": "kata level", "pattern": "\\bL2\\b"},
  {"deprecated": "L3", "canonical": "técnica", "context": "kata level", "pattern": "\\bL3\\b"}
]
```

---

## Entity: NormalizationReport

Record of changes made to a single kata during normalization.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `kata_path` | string | Path to normalized kata |
| `timestamp` | datetime | When normalization occurred |
| `jidoka_changes` | JidokaChange[] | Steps that received Jidoka structure |
| `terminology_changes` | TermChange[] | Terms that were replaced |
| `coherence_status` | enum | `aligned`, `misaligned`, `flagged` |
| `coherence_notes` | string | Notes on semantic alignment |
| `validation_status` | enum | `pending`, `approved`, `rejected`, `skipped` |

### Nested: JidokaChange

```json
{
  "step_number": 3,
  "added_verification": true,
  "added_correction": true,
  "verification_text": "El archivo existe y contiene las claves esperadas",
  "correction_text": "Archivo no encontrado → Verificar ruta y permisos"
}
```

### Nested: TermChange

```json
{
  "line_number": 45,
  "deprecated": "DoD",
  "canonical": "Validation Gate",
  "context_snippet": "...verificar que el DoD se cumple..."
}
```

### Report Format (Markdown)

```markdown
# Normalization Report: {kata_path}

**Timestamp**: {timestamp}
**Coherence**: {coherence_status}

## Jidoka Inline Changes

| Step | Verification Added | Correction Added |
|------|--------------------|------------------|
| 1    | ✅                 | ✅               |
| 2    | ✅ (existing)      | ✅               |

## Terminology Changes

| Line | Before | After |
|------|--------|-------|
| 45   | DoD    | Validation Gate |
| 78   | L1     | flujo |

## Validation

**Status**: {validation_status}
**Notes**: {coherence_notes}
```

---

## Semantic Level Mapping

| Level | Directory | Guiding Question | Content Focus |
|-------|-----------|------------------|---------------|
| Principios | `src/katas/principios/` | ¿Por qué? ¿Cuándo? | Philosophy, rationale, timing |
| Flujo | `src/katas/flujo/` | ¿Cómo fluye? | Sequences, workflows, value streams |
| Patrón | `src/katas/patron/` | ¿Qué forma? | Templates, recurring structures |
| Técnica | `src/katas/tecnica/` | ¿Cómo hacer? | Specific procedures, instructions |

---

## File Structure

```
src/katas/
├── principios/           # Level: Principios (¿Por qué?)
│   ├── 00-*.md
│   └── 01-*.md
├── flujo/                # Level: Flujo (¿Cómo fluye?)
│   ├── 04-*.md
│   ├── 06-*.md
│   └── ...
├── patron/               # Level: Patrón (¿Qué forma?)
│   ├── 01-*.md
│   ├── 02-*.md
│   └── ...
└── tecnica/              # Level: Técnica (¿Cómo hacer?)
    └── (empty - gap identified in feature 005)

specs/006-katas-normalization/outputs/
├── report-principios-00.md
├── report-principios-01.md
├── report-flujo-04.md
└── ...
```
