---
id: "[BCK]-[CODE]-[SEQ]"
title: "Backlog: [Project Name]"
version: "1.0"
date: "[YYYY-MM-DD]"
status: "[Draft|Active|Frozen]"
related_docs:
  - "[VIS-XXX-001]"
  - "[SAD-XXX-001]"
  - "[TEC-XXX-001]"
template: "lean-spec-v1"
---

# Backlog: [Project Name]

## 1. Epics

| ID | Epic | Objetivo | Arch Ref | Estado |
|----|------|----------|----------|--------|
| E1 | [Nombre Epic] | [Qué logra] | [SAD sec] | 🔲 Pending |
| E2 | [Nombre Epic] | [Qué logra] | [SAD sec] | 🔲 Pending |

---

## 2. Features por Epic

### E1: [Nombre Epic]

| ID | Feature | Descripción | Tech Design | Criterios de Aceptación |
|----|---------|-------------|-------------|-------------------------|
| F1.1 | [Nombre] | [Qué hace] | [TEC-XXX] o N/A | <ul><li>[ ] AC1</li><li>[ ] AC2</li></ul> |
| F1.2 | [Nombre] | [Qué hace] | N/A | <ul><li>[ ] AC1</li></ul> |

### E2: [Nombre Epic]

| ID | Feature | Descripción | Tech Design | Criterios de Aceptación |
|----|---------|-------------|-------------|-------------------------|
| F2.1 | [Nombre] | [Qué hace] | [TEC-XXX] o N/A | <ul><li>[ ] AC1</li></ul> |

---

## 3. Dependencias Críticas

```
F1.1 ──blocks──▶ F1.2
F1.2 ──blocks──▶ F2.1
```

| Blocker | Blocked | Tipo | Nota |
|---------|---------|------|------|
| F1.1 | F1.2 | técnica | [razón] |
| [Externo X] | F2.1 | externa | [razón] |

---

<!-- Secciones opcionales -->

<details>
<summary><h2>User Stories (detalle por Feature) - Opcional</h2></summary>

Expandir solo para features que requieren desglose en stories.

### Feature F1.1: [Nombre]

| ID | User Story | AC | SP |
|----|------------|----|----|
| US-1.1.1 | Como [rol], quiero [qué] para [beneficio] | <ul><li>[ ] AC1</li></ul> | 3 |
| US-1.1.2 | Como [rol], quiero [qué] para [beneficio] | <ul><li>[ ] AC1</li></ul> | 2 |

</details>

<details>
<summary><h2>Estimaciones y Roadmap - Opcional</h2></summary>

### Resumen de Estimación

| Epic | SP Total | % Proyecto |
|------|----------|------------|
| E1 | [N] | [%] |
| E2 | [N] | [%] |
| **Total** | **[N]** | **100%** |

### Secuencia Sugerida

```
Sprint 1: F1.1, F1.2
Sprint 2: F2.1, F2.2
...
```

</details>
