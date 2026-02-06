# RaiSE Templates

> **Filosofía**: Minimum Viable Specification (MVS) + Progressive Discovery

---

## Filosofía

### El Problema: Documentation Bloat

La documentación tradicional sufre del **problema 3.7:1** — 3.7 líneas de markdown por cada línea de código. Esto genera:

- ❌ 10x más tiempo escribiendo specs que código
- ❌ Documentación que nadie lee completa
- ❌ Redundancia entre documentos
- ❌ Context window bloat para agentes LLM

### La Solución: Lean Specification

**Lean Spec** aplica los principios de Lean Manufacturing a la documentación:

| Principio Lean | Aplicación a Specs |
|----------------|-------------------|
| **Eliminar Muda** (desperdicio) | Solo secciones que agregan valor |
| **Just-in-Time** | Documentar cuando se necesita, no antes |
| **Pull vs Push** | El código "jala" la documentación necesaria |
| **Continuous Flow** | Docs evolucionan con el código |

**Métricas Target**:

| Métrica | Tradicional | Lean |
|---------|-------------|------|
| Ratio markdown:code | 3.7:1 | <1.5:1 |
| Secciones por doc | 10-15 | 4 req + opt |
| Tiempo spec vs código | 10x | ≤2x |

### Minimum Viable Specification (MVS)

Cada template tiene **4 secciones requeridas** que capturan el 80% del valor:

```
┌─────────────────────────────────────────────┐
│         MVS: 4 SECCIONES CORE               │
├─────────────────────────────────────────────┤
│  1. PROBLEMA/OBJETIVO  → Por qué existe     │
│  2. SOLUCIÓN/CÓMO      → Qué hacemos        │
│  3. CONTRATOS/SCOPE    → Interfaces         │
│  4. DECISIONES/RIESGOS → Trade-offs         │
└─────────────────────────────────────────────┘
              +
┌─────────────────────────────────────────────┐
│   SECCIONES OPCIONALES (colapsadas)         │
│  <details> expandir solo si aplica </details>│
└─────────────────────────────────────────────┘
```

### Progressive Discovery

No documentar todo upfront. Seguir el ciclo:

```
Mínimo viable → Implementar → Descubrir → Documentar lo necesario
     │                                            │
     └────────────────────────────────────────────┘
                    (iterar)
```

**Regla de oro**: Si no sabes si necesitas una sección, no la escribas.

### Minimum Viable Context (MVC)

Para agentes LLM, **menos es más**. El contexto debe ser:

| Atributo | Por qué |
|----------|---------|
| **Relevante** | Solo información que aplica a la tarea actual |
| **Denso** | Máxima información por token |
| **Estructurado** | YAML/tablas, no prosa libre |
| **Determinista** | Mismo input → mismo output |

> *"El mejor contexto es el que el agente no tiene que ignorar."*

---

## Jerarquía de Documentos

```
LEVEL 0: STRATEGY (estable, cambia raramente)
├── Solution Vision        WHY - problema, valor, propuesta
│   template: solution/solution-vision.md
│
└── Architecture Overview  WHAT - sistema completo (C4 L1-L2)
    template: architecture/architecture-overview.md
    └── genera → ADRs

LEVEL 1: DESIGN (evoluciona con decisiones mayores)
├── ADRs                   Decisiones arquitectónicas individuales
│   template: architecture/adr.md
│
└── Tech Design (System)   HOW - concerns cross-cutting
    template: tech/tech-design.md
    └── informa → Backlog

LEVEL 2: PLANNING (evoluciona con backlog)
├── Backlog                WHAT - qué construir (Epics → Features)
│   template: backlog/backlog.md
│   └── features complejos → Tech Design (Feature)
│
└── Tech Design (Feature)  HOW - diseño por feature (on-demand)
    template: tech/tech-design-story-v2.md (recommended)
    legacy: tech/tech-design-story.md

LEVEL 3: EXECUTION (transitorio)
└── Tasks                  Viven en issue tracker
```

### Relación Entre Documentos

```
Solution Vision
     │
     ▼
Architecture Overview ────────► ADR-001, ADR-002...
     │
     ▼
Tech Design (System) ─────────► ADR-003...
     │
     ▼
Backlog
  ├── Epic 1
  │   ├── Feature 1.1 ────────► Tech Design (Feature) [si complejo]
  │   └── Feature 1.2          (directo a impl si simple)
  └── Epic 2
```

---

## Templates Disponibles

```
.raise/templates/
├── README.md                     ← estás aquí
├── solution/
│   └── solution-vision.md
├── architecture/
│   ├── architecture-overview.md
│   └── adr.md
├── tech/
│   ├── tech-design.md
│   ├── tech-design-story.md        # v1 (legacy)
│   └── tech-design-story-v2.md     # v2 (lean, AI-optimized)
├── backlog/
│   └── backlog.md
├── tools/
│   ├── research-prompt.md
│   ├── evidence-catalog.md
│   └── research-report.md
└── _legacy/                      # templates anteriores
```

| Template | Secciones | ~Líneas | Propósito |
|----------|-----------|---------|-----------|
| `solution-vision.md` | 4 + 2 opt | 60 | Visión de producto |
| `architecture-overview.md` | 4 + 3 opt | 80 | Arquitectura C4 L1-L2 |
| `adr.md` | 4 | 30 | Decisión arquitectónica |
| `tech-design.md` | 4 + 4 opt | 100 | Diseño técnico sistema |
| `tech-design-story.md` | 3 + 2 opt | 50 | Diseño por feature (v1 - legacy) |
| `tech-design-story-v2.md` | 4 + 4 opt | 50-150 | **Lean story spec (v2 - recommended)** |
| `backlog.md` | 3 + 2 opt | 60 | Backlog de proyecto |
| `research-prompt.md` | 7 core | 120 | Structured AI research prompt |
| `evidence-catalog.md` | 1 | 20 | Research source tracking |
| `research-report.md` | 3 + opt | 80 | Research findings synthesis |

---

## Cuándo Crear Cada Documento

| Documento | Trigger |
|-----------|---------|
| Solution Vision | Siempre (inicio de proyecto) |
| Architecture Overview | Sistema tiene >2 componentes |
| ADR | Decisión significativa con alternativas |
| Tech Design (System) | Concerns cross-cutting |
| Backlog | Después de Architecture |
| Tech Design (Feature) | Feature complejo* |
| Research Prompt | Antes de research para ADR/tech decisions |
| Evidence Catalog | Durante research (fuentes y ratings) |
| Research Report | Después de research (findings + recommendation) |

*Feature complejo = toca >3 componentes, >2 integraciones, algoritmo no trivial, o >8 SP

---

## Convenciones

### Secciones Opcionales Colapsadas

```markdown
<details>
<summary><h2>Sección Opcional</h2></summary>
[Contenido que se expande solo si aplica]
</details>
```

### Referencias, No Duplicación

```markdown
<!-- BIEN -->
**Decisión**: Ver [ADR-003](./adrs/adr-003.md)

<!-- MAL: copiar contenido -->
**Decisión**: Usamos YAML porque... [párrafos]
```

### Tablas sobre Prosa

```markdown
<!-- BIEN -->
| Decisión | Rationale |
|----------|-----------|
| YAML | Balance densidad/legibilidad |

<!-- MAL -->
Decidimos usar YAML porque ofrece un buen balance...
```

### Diagramas Simples

```markdown
<!-- BIEN -->
A → B → C

<!-- Mermaid solo si agrega valor claro -->
```

---

## Migración desde Legacy

Templates anteriores en `_legacy/`. Ver `_legacy/README.md` para mapeo.

---

*RaiSE Framework — Lean Specification v1.0*
