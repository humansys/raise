# Data Model: Katas Ontology Alignment Audit

**Date**: 2026-01-11
**Source**: spec.md §Key Entities, research.md

## Entity Overview

```
┌─────────────────┐         ┌─────────────────┐
│  OntologySlot   │ 0..1    │      Kata       │
│                 │◄────────│                 │
│  - id           │ fills   │  - path         │
│  - level        │         │  - currentName  │
│  - topic        │         │  - levelPrefix  │
│  - source       │         │  - jidokaStatus │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ 0..*                      │ 1
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  MappingResult  │────────►│  MigrationTask  │
│                 │ 0..*    │                 │
│  - type         │ has     │  - type         │
│  - rationale    │         │  - source       │
│  - slotId       │         │  - target       │
│  - kataPath     │         │  - changes      │
└─────────────────┘         └─────────────────┘
```

---

## Entity: OntologySlot

A position in the target kata ecosystem defined by the ontology.

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `id` | string | Unique slot identifier | `"FLUJO-003"` |
| `level` | enum | Semantic level | `"flujo"` |
| `topic` | string | Expected kata topic | `"Generación de Plan"` |
| `sourceReference` | string | Where defined in ontology | `"Methodology line 87"` |
| `status` | enum | Audit result | `"filled"` or `"gap"` |
| `filledBy` | string? | Path to kata filling this slot | `"/src/katas/L1-04-..."` |

### Level Enum

```
principios | flujo | patron | tecnica
```

### Status Enum

```
filled | gap
```

---

## Entity: Kata

An existing kata file being audited.

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `path` | string | Absolute file path | `"/src/katas/L1-04-generacion..."` |
| `filename` | string | File name only | `"L1-04-generacion-plan-implementacion-hu.md"` |
| `currentLevelPrefix` | string | Deprecated prefix (L0-L3) | `"L1"` |
| `targetLevel` | enum | Canonical level mapping | `"flujo"` |
| `title` | string | Kata title from content | `"Generación de Plan de Implementación"` |
| `jidokaCompliance` | object | Jidoka Inline validation result | See below |
| `deprecatedTerms` | array | List of deprecated terms found | `["DoD", "Developer"]` |
| `projectMarkers` | array | Project-specific markers found | `["Jafra"]` |
| `mappingStatus` | enum | Classification result | `"mapped"` or `"orphan"` |
| `mappedSlotId` | string? | If mapped, which slot | `"FLUJO-003"` |
| `orphanReason` | string? | If orphan, why | `"project-specific: Jafra"` |

### JidokaCompliance Object

```json
{
  "compliant": boolean,
  "totalSteps": number,
  "stepsWithVerification": number,
  "stepsWithContinueBlock": number,
  "issues": [
    {
      "step": number,
      "missing": "verification" | "continueBlock" | "both"
    }
  ]
}
```

### MappingStatus Enum

```
mapped | orphan
```

---

## Entity: MappingResult

The classification of a kata or slot against the ontology.

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `type` | enum | Result type | `"mapped"` |
| `slotId` | string? | Ontology slot (if mapped/gap) | `"FLUJO-003"` |
| `kataPath` | string? | Kata path (if mapped/orphan) | `"/src/katas/L1-04-..."` |
| `rationale` | string | Explanation for classification | `"Topic matches ontology example"` |
| `migrationTasks` | array | Required migration tasks | `[MigrationTask]` |

### Type Enum

```
mapped | gap | orphan
```

---

## Entity: MigrationTask

An actionable step to achieve ontology alignment.

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `id` | string | Unique task identifier | `"MIG-001"` |
| `type` | enum | Task type | `"rename"` |
| `source` | string | Current state | `"L1-04-generacion-plan-implementacion-hu.md"` |
| `target` | string | Target state | `"flujo/04-generacion-plan.md"` |
| `changes` | array | Specific changes required | See below |
| `priority` | enum | Execution priority | `"high"` |
| `effort` | enum | Estimated effort | `"low"` |

### Type Enum

```
rename | restructure | archive | create
```

### Priority Enum

```
high | medium | low
```

### Effort Enum

```
low | medium | high
```

### Changes Array (for type="restructure")

```json
[
  {
    "changeType": "add-jidoka-inline",
    "affectedSteps": [1, 3, 5],
    "description": "Add Verificación and Si no puedes continuar blocks"
  },
  {
    "changeType": "replace-term",
    "deprecated": "DoD",
    "canonical": "Validation Gate",
    "occurrences": 3
  }
]
```

---

## Aggregate: CoverageMatrix

The complete audit result combining all entities.

### Structure

```json
{
  "metadata": {
    "auditDate": "2026-01-11",
    "katasAnalyzed": 23,
    "ontologyVersion": "2.1.0",
    "sourceDocuments": [
      "docs/framework/v2.1/model/20-glossary-v2.1.md",
      "docs/framework/v2.1/model/21-methodology-v2.md"
    ]
  },
  "summary": {
    "totalSlots": 10,
    "filledSlots": 6,
    "gapSlots": 4,
    "totalKatas": 23,
    "mappedKatas": 8,
    "orphanKatas": 15,
    "coveragePercentage": 60.0,
    "jidokaCompliancePercentage": 25.0
  },
  "byLevel": {
    "principios": { "slots": 2, "filled": 1, "gap": 1, "katas": 2, "mapped": 1, "orphan": 1 },
    "flujo": { "slots": 3, "filled": 2, "gap": 1, "katas": 10, "mapped": 3, "orphan": 7 },
    "patron": { "slots": 3, "filled": 2, "gap": 1, "katas": 5, "mapped": 2, "orphan": 3 },
    "tecnica": { "slots": 2, "filled": 1, "gap": 1, "katas": 6, "mapped": 2, "orphan": 4 }
  },
  "slots": [ /* Array of OntologySlot */ ],
  "katas": [ /* Array of Kata */ ],
  "mappings": [ /* Array of MappingResult */ ],
  "migrationTasks": [ /* Array of MigrationTask */ ]
}
```

---

## Validation Rules

### OntologySlot

- `id` must be unique
- `id` format: `{LEVEL_PREFIX}-{NNN}` (e.g., `FLUJO-001`)
- `level` must be one of: `principios`, `flujo`, `patron`, `tecnica`
- `sourceReference` must reference a specific location in ontology docs

### Kata

- `path` must exist in filesystem
- `targetLevel` derived from `currentLevelPrefix` using mapping:
  - L0 → principios
  - L1 → flujo
  - L2 → patron
  - L3 → tecnica
- `jidokaCompliance.compliant` = true only if all steps have both verification and continueBlock

### MappingResult

- If `type` = "mapped": both `slotId` and `kataPath` required
- If `type` = "gap": `slotId` required, `kataPath` null
- If `type` = "orphan": `kataPath` required, `slotId` null

### MigrationTask

- `id` must be unique
- If `type` = "rename": `source` and `target` are filenames
- If `type` = "archive": `target` is archive location
- If `type` = "create": `source` is null, `target` is new file path

---

*Data model completed: 2026-01-11*
