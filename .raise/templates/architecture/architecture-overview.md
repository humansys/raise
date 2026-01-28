---
id: "[SAD]-[CODE]-[SEQ]"
title: "Architecture Overview: [System Name]"
version: "1.0"
date: "[YYYY-MM-DD]"
status: "[Draft|Approved]"
related_docs:
  - "[VIS-XXX-001]"
template: "lean-spec-v1"
c4_levels: ["context", "container"]
---

# Architecture Overview: [System Name]

## 1. System Context (C4 Level 1)

**Propósito del sistema**:
[1-2 oraciones: qué hace el sistema y para quién]

```
┌─────────────────────────────────────────────────────────────┐
│                     SYSTEM CONTEXT                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [Actor 1]                         [Actor 2]               │
│       │                                 │                    │
│       │ usa                             │ usa                │
│       ▼                                 ▼                    │
│   ┌─────────────────────────────────────────┐               │
│   │          [SYSTEM NAME]                  │               │
│   │                                         │               │
│   │   [Descripción breve del sistema]      │               │
│   └─────────────────────────────────────────┘               │
│                       │                                      │
│                       │ se integra con                       │
│                       ▼                                      │
│               [Sistema Externo]                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Actor/Sistema | Tipo | Interacción |
|---------------|------|-------------|
| [Actor 1] | usuario / sistema | [cómo interactúa] |
| [Sistema Externo] | dependencia | [qué consume/provee] |

---

## 2. Container Diagram (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────┐
│                      CONTAINERS                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│   │ [Container1] │    │ [Container2] │    │ [Container3] │ │
│   │              │───▶│              │───▶│              │ │
│   │ [tech stack] │    │ [tech stack] │    │ [tech stack] │ │
│   └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| Container | Responsabilidad | Tecnología | Tipo |
|-----------|-----------------|------------|------|
| [Container 1] | [qué hace] | [stack] | CLI / API / DB / ... |
| [Container 2] | [qué hace] | [stack] | CLI / API / DB / ... |

---

## 3. Decisiones Arquitectónicas Clave

| ID | Decisión | Rationale | ADR |
|----|----------|-----------|-----|
| D1 | [Decisión 1] | [Por qué] | [ADR-001](./adrs/adr-001.md) |
| D2 | [Decisión 2] | [Por qué] | [ADR-002](./adrs/adr-002.md) |

> **Nota**: Detalle completo de cada decisión en su ADR correspondiente.

---

## 4. Quality Attributes (NFRs)

| Atributo | Requisito | Cómo se Logra |
|----------|-----------|---------------|
| **Performance** | [ej: <200ms response] | [mecanismo] |
| **Scalability** | [ej: 1000 req/s] | [mecanismo] |
| **Security** | [ej: auth required] | [mecanismo] |
| **Reliability** | [ej: 99.9% uptime] | [mecanismo] |

---

<!-- Secciones opcionales -->

<details>
<summary><h2>Component Diagram (C4 Level 3) - Opcional</h2></summary>

Solo expandir para containers que requieren detalle interno.

### Container: [Container Name]

```
┌─────────────────────────────────────────┐
│           [Container Name]              │
├─────────────────────────────────────────┤
│  ┌───────────┐      ┌───────────┐      │
│  │ Component │─────▶│ Component │      │
│  │     A     │      │     B     │      │
│  └───────────┘      └───────────┘      │
└─────────────────────────────────────────┘
```

| Component | Responsabilidad |
|-----------|-----------------|
| Component A | [qué hace] |
| Component B | [qué hace] |

</details>

<details>
<summary><h2>Deployment View - Opcional</h2></summary>

```
┌─────────────────────────────────────────┐
│            DEPLOYMENT                    │
├─────────────────────────────────────────┤
│  [Environment: Production/Dev/...]      │
│                                          │
│  ┌─────────┐    ┌─────────┐            │
│  │ Node 1  │    │ Node 2  │            │
│  │         │    │         │            │
│  └─────────┘    └─────────┘            │
└─────────────────────────────────────────┘
```

| Nodo | Containers | Specs |
|------|------------|-------|
| [Node 1] | [qué corre] | [CPU/RAM/etc] |

</details>

<details>
<summary><h2>Cross-Cutting Concerns - Opcional</h2></summary>

| Concern | Approach |
|---------|----------|
| Logging | [cómo se implementa] |
| Error Handling | [estrategia] |
| Configuration | [cómo se maneja] |
| Monitoring | [herramientas] |

</details>
