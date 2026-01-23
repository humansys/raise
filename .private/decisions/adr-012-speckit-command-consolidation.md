# ADR-012: Reestructuración de Comandos RaiSE - Developer Experience First

**Estado:** 📝 Proposed
**Fecha:** 2026-01-22
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

RaiSE es un framework **centrado en el humano**. Sin embargo, la estructura actual de comandos en `.agent/workflows/` presenta problemas significativos de Developer Experience (DX) que contradicen este principio fundamental.

### Inventario Actual: 18 Comandos

```
01-onboarding/
├── raise.1.analyze.code.md
├── raise.rules.edit.md
├── raise.rules.generate.md
└── speckit.2.constitution.md      ← Prefijo incorrecto para onboarding

02-projects/
├── raise.1.discovery.md           ← Colisión: raise.1.* también en onboarding
├── raise.2.vision.md
├── raise.3.ecosystem.md
├── raise.4.tech-design.md
├── raise.5.backlog.md
└── raise.6.estimation.md

03-feature/
├── speckit.1.specify.md
├── speckit.2.clarify.md           ← QA disfrazado de paso
├── speckit.3.plan.md
├── speckit.4.tasks.md
├── speckit.5.analyze.md           ← Gate disfrazado de paso
├── speckit.6.implement.md
├── speckit.util.checklist.md      ← Alto costo, bajo uso
└── speckit.util.issues.md
```

### Problemas Identificados

| Problema | Manifestación | Impacto en DX |
|----------|---------------|---------------|
| **Colisión de nomenclatura** | `raise.1.*` existe en onboarding Y projects | Usuario no sabe cuál es cuál |
| **Prefijos inconsistentes** | `raise.*` vs `speckit.*` mezclados sin criterio | Carga cognitiva innecesaria |
| **Numeración engañosa** | `1,2,3,4,5,6` sugiere secuencia obligatoria | Usuarios ejecutan pasos opcionales |
| **Nombres técnicos** | "discovery", "vision", "specify" | No dicen qué HACE el comando |
| **QA mezclado con flujo** | `clarify`, `analyze` numerados como pasos | Falsa equivalencia ontológica |
| **Comando huérfano** | `speckit.2.constitution` en onboarding | Rompe el patrón de su categoría |

### Evidencia de Confusión (Investigación spec-kit GitHub)

| Fuente | Hallazgo |
|--------|----------|
| [Discussion #447](https://github.com/github/spec-kit/discussions/447) | "The agent just starts coding...I don't get to use /specify, /plan, /tasks" |
| [Discussion #468](https://github.com/github/spec-kit/discussions/468) | Usuarios "just started to prompt the AI directly...instead of breaking out into specs/" |
| [Issue #614](https://github.com/github/spec-kit/issues/614) | "Documentation does not provide clear descriptions for each command" |
| [Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html) | "Workflow slow, heavy, and less effective than iterative prompting" |

### Principio Violado

> **RaiSE es centrado en el humano.** La nomenclatura actual está centrada en la implementación técnica, no en el modelo mental del usuario.

---

## Decisión

### Principios de Diseño para Nueva Nomenclatura

| Principio | Aplicación |
|-----------|------------|
| **1. Verbo + Sustantivo** | El nombre dice qué HACE: `create-prd`, no `discovery` |
| **2. Sin prefijos de marca** | No `raise.*` ni `speckit.*` — son ruido cognitivo |
| **3. Sin numeración secuencial** | El flujo se infiere del contexto, no de 1-2-3-4-5-6 |
| **4. Agrupación por fase** | Setup → Project → Feature → Tools |
| **5. Inglés consistente** | Convención de la industria |
| **6. Dash-case** | Legible y convencional para CLI |
| **7. Jidoka built-in** | Validación integrada, no como paso separado |

### Nueva Estructura: 14 Comandos (de 18)

```
.agent/workflows/

# ══════════════════════════════════════════════════════════════════
# SETUP - Una vez por proyecto (configuración inicial)
# ══════════════════════════════════════════════════════════════════
setup/
├── init-project.md           # Crear/actualizar constitution
├── analyze-codebase.md       # Análisis de codebase brownfield
├── generate-rules.md         # Generar guardrails desde patrones
└── edit-rule.md              # Editar guardrail específico

# ══════════════════════════════════════════════════════════════════
# PROJECT - Planificación de alto nivel (una vez por proyecto/milestone)
# ══════════════════════════════════════════════════════════════════
project/
├── create-prd.md             # Crear Product Requirements Document
├── define-vision.md          # Crear Solution Vision
├── map-ecosystem.md          # Mapear dependencias e integraciones
├── design-architecture.md    # Crear Technical Design
├── create-backlog.md         # Crear backlog con user stories
└── estimate-effort.md        # Estimar esfuerzo y roadmap

# ══════════════════════════════════════════════════════════════════
# FEATURE - Por cada feature (ciclo iterativo)
# ══════════════════════════════════════════════════════════════════
feature/
├── create-spec.md            # Crear especificación (+ clarificación inline)
├── plan-implementation.md    # Crear plan técnico
├── generate-tasks.md         # Generar tareas (+ validación cross-artifact)
└── implement.md              # Implementar código

# ══════════════════════════════════════════════════════════════════
# TOOLS - Herramientas auxiliares (uso ad-hoc)
# ══════════════════════════════════════════════════════════════════
tools/
└── export-issues.md          # Exportar tasks a GitHub Issues

# ══════════════════════════════════════════════════════════════════
# DEPRECATED - Comandos absorbidos o de bajo valor
# ══════════════════════════════════════════════════════════════════
deprecated/
├── clarify.md                # → Absorbido en create-spec
├── analyze.md                # → Absorbido en generate-tasks
└── create-checklist.md       # → Deprecado (4.2k tokens, bajo uso)
```

### Tabla de Migración Completa

| Comando Actual | Nuevo Comando | Categoría | Cambio |
|----------------|---------------|-----------|--------|
| `raise.1.analyze.code` | `setup/analyze-codebase` | Setup | Renombrado |
| `raise.rules.generate` | `setup/generate-rules` | Setup | Renombrado |
| `raise.rules.edit` | `setup/edit-rule` | Setup | Renombrado |
| `speckit.2.constitution` | `setup/init-project` | Setup | Renombrado + reubicado |
| `raise.1.discovery` | `project/create-prd` | Project | Renombrado |
| `raise.2.vision` | `project/define-vision` | Project | Renombrado |
| `raise.3.ecosystem` | `project/map-ecosystem` | Project | Renombrado |
| `raise.4.tech-design` | `project/design-architecture` | Project | Renombrado |
| `raise.5.backlog` | `project/create-backlog` | Project | Renombrado |
| `raise.6.estimation` | `project/estimate-effort` | Project | Renombrado |
| `speckit.1.specify` | `feature/create-spec` | Feature | Renombrado + absorbe clarify |
| `speckit.2.clarify` | — | Deprecated | Absorbido en create-spec |
| `speckit.3.plan` | `feature/plan-implementation` | Feature | Renombrado |
| `speckit.4.tasks` | `feature/generate-tasks` | Feature | Renombrado + absorbe analyze |
| `speckit.5.analyze` | — | Deprecated | Absorbido en generate-tasks |
| `speckit.6.implement` | `feature/implement` | Feature | Renombrado |
| `speckit.util.checklist` | — | Deprecated | Eliminado (alto costo, bajo uso) |
| `speckit.util.issues` | `tools/export-issues` | Tools | Renombrado |

### Invocación: Antes vs Después

**ANTES** (confuso):
```bash
/raise.1.discovery           # ¿Qué es "discovery"?
/raise.2.vision              # ¿Qué tipo de "vision"?
/speckit.1.specify           # ¿"Specify" qué?
/speckit.2.clarify           # ¿Es obligatorio?
/speckit.3.plan              # ¿Otro plan además de vision?
/speckit.5.analyze           # ¿Tengo que correr esto?
```

**DESPUÉS** (claro):
```bash
/project/create-prd          # Crear PRD ✓
/project/define-vision       # Definir visión de solución ✓
/feature/create-spec         # Crear spec de feature ✓
/feature/plan-implementation # Planificar implementación ✓
/feature/generate-tasks      # Generar tareas ✓
/feature/implement           # Implementar ✓
```

### Flujos de Usuario Claros

#### Flujo 1: Proyecto Nuevo (Greenfield)

```
/setup/init-project "Mi Proyecto"
    ↓
/project/create-prd "Sistema de reservas..."
    ↓
/project/define-vision
    ↓
/project/design-architecture
    ↓
/project/create-backlog
    ↓
/project/estimate-effort
    ↓
[Por cada feature del backlog:]
    /feature/create-spec "Feature X"
    /feature/plan-implementation
    /feature/generate-tasks
    /feature/implement
```

#### Flujo 2: Proyecto Existente (Brownfield)

```
/setup/init-project "Mi Proyecto Legacy"
    ↓
/setup/analyze-codebase       # Análisis del código existente
    ↓
/setup/generate-rules         # Extraer guardrails de patrones
    ↓
/project/map-ecosystem        # Mapear integraciones existentes
    ↓
/project/create-prd "Nueva funcionalidad..."
    ↓
[Continúa como greenfield...]
```

#### Flujo 3: Feature Rápido (lo más común)

```
/feature/create-spec "Add dark mode toggle"
    ↓
/feature/plan-implementation
    ↓
/feature/generate-tasks
    ↓
/feature/implement
```

### Jidoka Built-in: Comportamiento de Comandos Consolidados

#### `feature/create-spec` (absorbe `clarify`)

```markdown
## Comportamiento

1. Crear spec desde descripción del usuario
2. **Ambiguity Detection** (integrado):
   - Escanear spec buscando gaps críticos
   - Si ≤3 ambigüedades: preguntar inline, actualizar spec
   - Si >3: marcar [NEEDS CLARIFICATION], advertir
3. Gate-Spec: Validar completitud
4. Handoff → plan-implementation
```

#### `feature/generate-tasks` (absorbe `analyze`)

```markdown
## Comportamiento

1. Generar tasks.md desde spec + plan
2. **Cross-Artifact Validation** (integrado):
   - Verificar consistencia spec ↔ plan ↔ tasks
   - Detectar: coverage gaps, contradicciones, terminology drift
   - Si CRITICAL: PARAR (Jidoka), reportar issues
   - Si WARNING: Continuar con advertencias
3. Gate-Tasks: Validar completitud
4. Handoff → implement
```

---

## Consecuencias

### Positivas

| Beneficio | Impacto |
|-----------|---------|
| **Claridad inmediata** | El nombre del comando dice qué hace |
| **Menos comandos** | 14 vs 18 (reducción 22%) |
| **Sin colisiones** | Cada comando tiene nombre único |
| **Sin numeración engañosa** | No hay falsa secuencia obligatoria |
| **Agrupación intuitiva** | setup/ → project/ → feature/ → tools/ |
| **Menor carga de tokens** | ~7k tokens menos (sin clarify, analyze, checklist) |
| **Jidoka built-in** | Validación automática, no manual |
| **Discoverability** | Usuario puede explorar categorías |

### Negativas

| Trade-off | Mitigación |
|-----------|------------|
| **Breaking change** | Documentar migración clara |
| **Memorización nueva** | Nombres más intuitivos compensan |
| **Pierde granularidad** | Flags opcionales si hay demanda futura |
| **Handoffs a actualizar** | Script de migración automatizado |

### Neutras

- Compatible con ADR-011 (Modelo Híbrido)
- Mantiene estructura de directorios existente
- Los comandos internamente no cambian (solo nomenclatura externa)

---

## Alternativas Consideradas

### 1. Mantener Prefijos pero Corregir Inconsistencias

`raise.setup.*`, `raise.project.*`, `raise.feature.*`

**Rechazado porque:**
- El prefijo `raise.` no aporta información
- Añade 6 caracteres sin valor semántico
- La agrupación por directorio es suficiente

### 2. Usar Números pero sin Obligatoriedad

`project/1-create-prd`, `project/2-define-vision`

**Rechazado porque:**
- Los números siguen sugiriendo secuencia
- No todos los pasos son secuenciales (ej: map-ecosystem es opcional)
- Viola el principio de claridad

### 3. Esquema Flat sin Categorías

`/create-prd`, `/define-vision`, `/create-spec`

**Rechazado porque:**
- 14 comandos sin agrupación es difícil de descubrir
- Pierde contexto de fase del ciclo de vida
- No escala si se añaden más comandos

### 4. Mantener clarify y analyze Separados

Como comandos opcionales en `tools/`

**Parcialmente aceptado:**
- La funcionalidad se preserva (integrada)
- Si hay demanda futura, pueden exponerse como flags:
  - `/feature/create-spec --skip-clarify`
  - `/feature/generate-tasks --skip-validate`

---

## Implementación

### Fase 1: Crear Nueva Estructura (sin romper la actual)

```bash
# Crear nuevos directorios
mkdir -p .agent/workflows/{setup,project,feature,tools,deprecated}

# Copiar comandos a nueva ubicación (preservando originales)
```

### Fase 2: Actualizar Contenido de Comandos

1. **Renombrar referencias internas** en cada comando:
   - Actualizar handoffs para usar nuevos nombres
   - Actualizar scripts que referencian comandos

2. **Integrar lógica de clarify → create-spec**:
   - Añadir sección "Ambiguity Detection"
   - Preservar lógica de preguntas interactivas

3. **Integrar lógica de analyze → generate-tasks**:
   - Añadir sección "Cross-Artifact Validation"
   - Preservar lógica de detección de inconsistencias

### Fase 3: Mover Comandos Deprecados

```bash
# Mover a deprecated/ con nota explicativa
mv speckit.2.clarify.md deprecated/clarify.md
mv speckit.5.analyze.md deprecated/analyze.md
mv speckit.util.checklist.md deprecated/create-checklist.md
```

### Fase 4: Eliminar Estructura Antigua

```bash
# Solo después de validar que todo funciona
rm -rf .agent/workflows/01-onboarding/
rm -rf .agent/workflows/02-projects/
rm -rf .agent/workflows/03-feature/
```

### Fase 5: Actualizar Documentación

1. `CLAUDE.md` - Nueva tabla de comandos
2. `README.md` - Guía de inicio rápido
3. Constitution - Referencias a comandos
4. Cualquier tutorial existente

---

## Guía de Migración para Usuarios

### Tabla de Referencia Rápida

| Si usabas... | Ahora usa... |
|--------------|--------------|
| `/raise.1.analyze.code` | `/setup/analyze-codebase` |
| `/raise.rules.generate` | `/setup/generate-rules` |
| `/raise.rules.edit` | `/setup/edit-rule` |
| `/speckit.2.constitution` | `/setup/init-project` |
| `/raise.1.discovery` | `/project/create-prd` |
| `/raise.2.vision` | `/project/define-vision` |
| `/raise.3.ecosystem` | `/project/map-ecosystem` |
| `/raise.4.tech-design` | `/project/design-architecture` |
| `/raise.5.backlog` | `/project/create-backlog` |
| `/raise.6.estimation` | `/project/estimate-effort` |
| `/speckit.1.specify` | `/feature/create-spec` |
| `/speckit.2.clarify` | *(integrado en create-spec)* |
| `/speckit.3.plan` | `/feature/plan-implementation` |
| `/speckit.4.tasks` | `/feature/generate-tasks` |
| `/speckit.5.analyze` | *(integrado en generate-tasks)* |
| `/speckit.6.implement` | `/feature/implement` |
| `/speckit.util.checklist` | *(deprecado)* |
| `/speckit.util.issues` | `/tools/export-issues` |

---

## Métricas de Éxito

| Métrica | Antes | Después (Target) |
|---------|-------|------------------|
| Comandos totales | 18 | 14 |
| Prefijos diferentes | 3 (`raise`, `speckit`, `util`) | 0 |
| Colisiones de nombre | 1 (`raise.1.*`) | 0 |
| Tokens por sesión | ~18.6k | ~11k |
| Tiempo para entender estructura | Alto (requiere docs) | Bajo (auto-explicativo) |

---

## Visualización Final

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RaiSE Command Structure                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────┐ │
│  │   SETUP     │   │   PROJECT   │   │   FEATURE   │   │  TOOLS  │ │
│  │  (once)     │──▶│  (planning) │──▶│  (iterate)  │   │  (any)  │ │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────┘ │
│        │                 │                 │                │      │
│        ▼                 ▼                 ▼                ▼      │
│  init-project      create-prd        create-spec      export-     │
│  analyze-codebase  define-vision     plan-impl        issues      │
│  generate-rules    map-ecosystem     generate-tasks               │
│  edit-rule         design-arch       implement                    │
│                    create-backlog                                  │
│                    estimate-effort                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Flujo típico:  setup/ ──▶ project/ ──▶ feature/ ──▶ feature/ ──▶ ...
                                          ▲            │
                                          └────────────┘
                                         (ciclo por feature)
```

---

## Referencias

- [ADR-011](./adr-011-hybrid-kata-template-gate.md) — Modelo Híbrido (Template/Kata/Gate)
- [ADR-006a](./adr-006a-validation-gates.md) — Validation Gates
- [GitHub spec-kit](https://github.com/github/spec-kit) — Proyecto original
- [RaiSE Methodology](../../docs/core/methodology.md) — Metodología v2.1
- [Issue #1401](https://github.com/github/spec-kit/issues/1401) — Token consumption analysis
- [Scott Logic Review](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html) — Crítica del workflow

---

*Este ADR formaliza la reestructuración completa de comandos RaiSE siguiendo el principio "Developer Experience First". La nomenclatura nueva prioriza claridad cognitiva sobre convención técnica, alineándose con la filosofía de RaiSE como framework centrado en el humano.*
