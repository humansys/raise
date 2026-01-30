---
id: "ADR-009"
title: "Modelo de Gobernanza Continua: Guardrails como Fuente Única de Verdad"
date: "2026-01-30"
status: "Proposed"
related_to: ["ADR-008", "ADR-007", "glossary-v2.3"]
supersedes: []
---

# ADR-009: Modelo de Gobernanza Continua - Guardrails como Fuente Única de Verdad

## Contexto

### Problema Identificado

RaiSE necesita un modelo de gobernanza que:

1. **Guíe la generación** de código y artefactos (Golden Context para agentes)
2. **Valide los resultados** contra estándares (Validation Gates)
3. **Escale a equipos enterprise** trabajando en múltiples repos
4. **Prevenga drift arquitectónico** entre equipos y proyectos

El análisis reveló una **duplicación conceptual** problemática:

```
ESTADO ACTUAL (Potencial Muda):

.raise/governance/guardrails/testing.mdc
────────────────────────────────────────
MUST: Test coverage >= 80%


.raise/gates/gate-code.md
────────────────────────────────────────
- [ ] Verificar test coverage >= 80%
```

**La misma regla definida dos veces:**
- Una vez en gobernanza (para generación)
- Una vez en gate (para validación)

Esto viola el principio DRY y crea riesgo de drift (gobernanza dice 80%, gate verifica 70%).

### Análisis Lean

| Tipo de Muda | Cómo se Manifiesta |
|--------------|-------------------|
| **Duplicación** | Misma regla en gobernanza Y en gate |
| **Movimiento** | Actualizar dos lugares cuando cambia una regla |
| **Defectos** | Drift entre gobernanza y gate |
| **Sobreprocesamiento** | Definiciones de gate separadas cuando gobernanza basta |

### Insight Fundamental

**Un Guardrail y su Gate son dos caras de la misma moneda:**

| Aspecto | Guardrail | Gate |
|---------|-----------|------|
| **Cuándo** | Antes/durante generación | Después de generación |
| **Propósito** | Guiar creación | Verificar creación |
| **Pregunta** | "¿Qué DEBE ser?" | "¿Lo HICIMOS?" |
| **Rol** | Prescriptivo | Verificativo |

**Referencian las MISMAS reglas, solo en diferentes momentos.**

### Tipos de Validación Identificados

El análisis de las katas existentes reveló **dos tipos distintos de validación**:

#### 1. Artifact Gates (Completitud Estructural)

"¿El output está estructuralmente completo?"

```
gate-discovery.md  → ¿El PRD tiene todas las secciones requeridas?
gate-vision.md     → ¿La Vision tiene alineamiento de stakeholders?
gate-design.md     → ¿El Tech Design tiene diagramas C4?
```

**Son verificaciones de adherencia a templates.** Específicos de cada kata.

#### 2. Governance Gates (Cumplimiento de Reglas)

"¿El output sigue las reglas?"

```
governance/architecture.mdc → ¿El código sigue Clean Architecture?
governance/security.mdc     → ¿La API usa auth apropiado?
governance/testing.mdc      → ¿El código tiene 80% coverage?
```

**Son verificaciones de cumplimiento de guardrails.** Derivados de gobernanza.

## Decisión

### Adoptar el Modelo de Gobernanza Continua con Guardrails como Fuente Única

```
┌─────────────────────────────────────────────────────────────────────┐
│  GUARDRAIL (Definición Única)                                        │
│  ═══════════════════════════                                        │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  id: MUST-TEST-001                                           │    │
│  │  level: MUST                                                 │    │
│  │  rule: "Test coverage >= 80%"                                │    │
│  │                                                              │    │
│  │  context:     # Para generación (Golden Context)             │    │
│  │    "Al escribir código, asegurar tests para cada función"    │    │
│  │                                                              │    │
│  │  verification: # Para validación (Gate)                      │    │
│  │    check: coverage                                           │    │
│  │    command: npm run test:coverage                            │    │
│  │    threshold: 80                                             │    │
│  │    blocking: true                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│           │                                    │                     │
│           │ usado como                         │ usado como          │
│           ↓                                    ↓                     │
│  ┌─────────────────┐                  ┌─────────────────┐           │
│  │ GOLDEN CONTEXT  │                  │ GOVERNANCE GATE │           │
│  │ (input a agent) │                  │ (validación)    │           │
│  └─────────────────┘                  └─────────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Una definición, dos usos:**
1. **Durante generación:** Agente lee sección `context` como Golden Context
2. **Durante validación:** Gate ejecuta sección `verification` como check

### Estructura de Dos Capas de Gobernanza

```
┌─────────────────────────────────────────────────────────────────────┐
│  GOVERNANCE (Producto/Sistema - Compartida)                          │
│  ═══════════════════════════════════════════                        │
│  • Patrones de arquitectura                                         │
│  • Estándares de seguridad                                          │
│  • Requisitos de testing                                            │
│  • Convenciones de API                                              │
│  • Manejo de errores                                                │
│                                                                      │
│  Ubicación: .raise/governance/                                      │
│  Frecuencia: Una vez por producto, evoluciona via ADR               │
│  Alcance: TODOS los codebases del producto                          │
└─────────────────────────────────────────────────────────────────────┘
                              │ hereda
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  CODEBASE RULES (Repo-específicas)                                   │
│  ═════════════════════════════════                                  │
│  • Convenciones de estructura de archivos                           │
│  • Patrones tech-específicos (React hooks, Node middleware)         │
│  • Convenciones de build/deploy                                     │
│                                                                      │
│  Ubicación: .cursor/rules/                                          │
│  Frecuencia: Una vez por repo, extiende Governance                  │
│  Alcance: Solo este repo                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │ gobierna
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  PROJECT WORK (Sin gobernanza propia, solo sigue)                    │
│  ════════════════════════════════════════════════                   │
│  Discovery → Vision → Design → Backlog                              │
│                                                                      │
│  ¿Excepción necesaria? → ADR → Actualiza Governance                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Solo dos capas (KISS/YAGNI):**
- **Governance**: Política producto-wide (WHAT)
- **Codebase Rules**: Patrones repo-específicos (HOW)
- **No hay PRD-level governance**: Excepciones via proceso ADR

### Severidad de Guardrail = Comportamiento de Gate

Los niveles MUST/SHOULD/MAY mapean directamente al comportamiento del gate:

| Nivel | Durante Generación | Durante Validación |
|-------|-------------------|-------------------|
| **MUST** | "Debes hacer esto" | Gate bloqueante (falla la kata) |
| **SHOULD** | "Deberías hacer esto" | Gate de advertencia (flag el issue) |
| **MAY** | "Puedes hacer esto" | Sin gate (opcional) |

**No se necesita definición de gate separada.** El nivel del guardrail define el comportamiento del gate.

### Katas de Setup para Gobernanza

#### `setup/governance` (Nueva)

```yaml
---
id: governance
titulo: "Governance: Definir Guardrails de Producto"
work_cycle: setup
frequency: once-per-product

prerequisites:
  greenfield: [project/vision]  # Necesita dirección técnica
  brownfield: []                 # Puede comenzar inmediatamente

outputs:
  - .raise/governance/governance.md
  - .raise/governance/guardrails/*.mdc

next_kata: setup/rules
---
```

**Propósito:** Definir guardrails producto-wide (MUST/SHOULD/MAY).

#### `setup/rules` (Renombrada desde `setup/analyze`)

```yaml
---
id: rules
titulo: "Rules: Definir Patrones de Codebase"
work_cycle: setup
frequency: once-per-codebase

prerequisites:
  - setup/governance  # Siempre requiere gobernanza primero

outputs:
  - .cursor/rules/*.mdc

next_kata: setup/ecosystem
---
```

**Propósito:** Definir/extraer patrones repo-específicos que implementan la gobernanza.

### Estructura de Directorios

```
.raise/
├── governance/                    # PRODUCTO-WIDE (compartida)
│   ├── governance.md              # Por qué estos guardrails
│   └── guardrails/
│       ├── architecture.mdc       # MUST: Clean Architecture
│       ├── security.mdc           # MUST: JWT, RBAC
│       ├── testing.mdc            # SHOULD: 80% coverage
│       └── api.mdc                # MUST: Versionado, OpenAPI
│
├── katas/
│   └── setup/
│       ├── governance.md          # NUEVA
│       ├── rules.md               # Renombrada desde analyze.md
│       └── ecosystem.md
│
├── gates/                         # Solo Artifact Gates aquí
│   ├── gate-discovery.md          # Completitud estructural de PRD
│   ├── gate-vision.md             # Completitud estructural de Vision
│   └── gate-design.md             # Completitud estructural de Design
│
└── context/
    └── glossary.md

.cursor/rules/                     # CODEBASE-ESPECÍFICO (este repo)
├── 010-react-components.mdc       # Funcional, solo hooks
├── 020-file-structure.mdc         # src/features/{name}/
├── 030-error-handling.mdc         # Clase ApiError
└── 040-database.mdc               # Patrones Prisma
```

### Schema de Guardrail (Fuente Única)

```yaml
# .raise/governance/guardrails/testing.mdc
---
id: MUST-TEST-001
level: MUST                        # MUST | SHOULD | MAY
scope: "**/*.ts"                   # Glob pattern de aplicabilidad
version: 1.0.0
---

# Test Coverage Threshold

## Regla

Todo código TypeScript debe tener >= 80% de cobertura de tests.

## Contexto (Golden Context para Agentes)

Al generar código:
- Crear archivo de test correspondiente para cada módulo
- Cubrir happy path y casos de error
- Mockear dependencias externas
- Usar patrón describe/it para estructura

## Verificación (Criterios de Gate)

```yaml
check: coverage
command: npm run test:coverage
threshold: 80
blocking: true  # Derivado de level: MUST
on_failure:
  message: "Coverage below 80% threshold"
  recovery: "Add tests for uncovered functions"
```

## Ejemplos

### Correcto
```typescript
// user.service.ts
export function createUser(data: UserInput): User { ... }

// user.service.test.ts
describe('createUser', () => {
  it('should create user with valid data', () => { ... });
  it('should throw on invalid email', () => { ... });
});
```

### Incorrecto
```typescript
// user.service.ts - Sin tests correspondientes
export function createUser(data: UserInput): User { ... }
```
```

### Flujo de Ejecución Unificado

```
┌─────────────────────────────────────────────────────────────────────┐
│  EJECUCIÓN DE KATA                                                   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  PASO N: Generar artefacto                                     │  │
│  │                                                                │  │
│  │  Contexto cargado:                                             │  │
│  │  ├── Template (estructura)                                     │  │
│  │  └── Governance Guardrails ←── Golden Context                  │  │
│  │      (sección "Contexto" de cada guardrail)                    │  │
│  │                                                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                            │                                         │
│                            ↓                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  VALIDACIÓN                                                    │  │
│  │                                                                │  │
│  │  1. Artifact Gate (per kata):                                  │  │
│  │     └── "¿El output está estructuralmente completo?"           │  │
│  │         └── Definido en: gates/gate-{kata}.md                  │  │
│  │                                                                │  │
│  │  2. Governance Gate (de guardrails):                           │  │
│  │     └── "¿El output sigue las reglas?"                         │  │
│  │         └── Derivado de: governance/guardrails/*.mdc           │  │
│  │             (sección "Verificación" de cada guardrail)         │  │
│  │                                                                │  │
│  │  3. Jidoka:                                                    │  │
│  │     └── MUST falla → Stop (bloqueante)                         │  │
│  │     └── SHOULD falla → Warning (continúa con flag)             │  │
│  │                                                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Multi-Repo: Gobernanza Compartida, Reglas Por-Repo

```
producto/
├── .raise/governance/            # COMPARTIDA (symlink o submodule)
│   └── guardrails/*.mdc
│
├── frontend-repo/
│   ├── .raise/governance → ../   # Apunta a compartida
│   └── .cursor/rules/            # Patrones React-específicos
│
├── backend-repo/
│   ├── .raise/governance → ../   # Apunta a compartida
│   └── .cursor/rules/            # Patrones Node-específicos
│
└── mobile-repo/
    ├── .raise/governance → ../   # Apunta a compartida
    └── .cursor/rules/            # Patrones RN-específicos
```

**Mecanismo de herencia:** Symlink simple o git submodule (KISS).

## Consecuencias

### Positivas

| Aspecto | Beneficio |
|---------|-----------|
| **DRY** | Una definición de regla, dos usos (context + validation) |
| **Consistencia** | Imposible drift entre governance y gate |
| **Mantenibilidad** | Un lugar para actualizar reglas |
| **Claridad** | Separación clara: Artifact Gates (estructura) vs Governance Gates (reglas) |
| **Escalabilidad** | Gobernanza compartida entre repos previene drift |
| **Lean** | Elimina duplicación (Muda de movimiento y defectos) |
| **Alineamiento ADR-008** | Guardrails son Context que informan ejecución de Katas |

### Negativas

| Aspecto | Impacto | Mitigación |
|---------|---------|------------|
| **Schema más complejo** | Guardrails tienen más secciones | Proporcionar templates y validación |
| **Migración requerida** | Gates existentes deben consolidarse | Plan de migración incremental |
| **Curva de aprendizaje** | Nuevo concepto de guardrail unificado | Documentación clara, ejemplos |

### Impacto en Kata Harness

El Kata Harness (ADR-008) debe:

1. **Cargar guardrails** como Golden Context antes de ejecución
2. **Extraer verificaciones** de guardrails para validación post-step
3. **Aplicar Jidoka** según nivel (MUST=block, SHOULD=warn)
4. **Distinguir** entre Artifact Gates (per-kata) y Governance Gates (de guardrails)

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| **Mantener gates separados** | Viola DRY, riesgo de drift |
| **Solo artifact gates** | Pierde validación de reglas de negocio |
| **Gates generados automáticamente** | Complejidad de compilación innecesaria |
| **3+ capas de gobernanza (Portfolio/Solution/Repo/PRD)** | YAGNI - 2 capas suficientes para 90% de casos |
| **Gobernanza a nivel de PRD** | Fragmentación, drift entre proyectos |

## Glosario de Términos (Extensión v2.3)

| Término | Definición |
|---------|------------|
| **Governance** | Guardrails producto-wide que definen WHAT enforced. Compartida entre codebases. |
| **Guardrail** | Regla individual con nivel (MUST/SHOULD/MAY), contexto (para generación), y verificación (para validación). Fuente única de verdad. |
| **Codebase Rules** | Patrones repo-específicos que implementan y extienden Governance. |
| **Artifact Gate** | Validación de completitud estructural de un artefacto (adherencia a template). Per-kata. |
| **Governance Gate** | Validación de cumplimiento de reglas. Derivado de guardrails, no definido separadamente. |
| **Golden Context** | Guardrails cargados como contexto para guiar generación de código/artefactos. |

## Plan de Implementación

### Fase 1: Schema de Guardrail Unificado

- [ ] Definir schema YAML completo para guardrails
- [ ] Crear template `.raise/templates/guardrail.mdc`
- [ ] Documentar secciones: Regla, Contexto, Verificación, Ejemplos

### Fase 2: Migración de Gates Existentes

- [ ] Identificar gates que son Governance (deben moverse a guardrails)
- [ ] Identificar gates que son Artifact (permanecen en gates/)
- [ ] Migrar gate-code.md → governance/guardrails/*.mdc
- [ ] Consolidar verificaciones duplicadas

### Fase 3: Katas de Setup

- [ ] Crear `setup/governance.md`
- [ ] Renombrar `setup/analyze.md` → `setup/rules.md`
- [ ] Actualizar flujo: governance → rules → ecosystem

### Fase 4: Actualización de Kata Harness

- [ ] Implementar carga de guardrails como Golden Context
- [ ] Implementar extracción de verificaciones de guardrails
- [ ] Implementar Jidoka basado en nivel (MUST/SHOULD/MAY)

### Fase 5: Documentación

- [ ] Actualizar glossary v2.3
- [ ] Crear guía "Writing Effective Guardrails"
- [ ] Documentar flujo de herencia multi-repo

---

<details>
<summary><strong>Referencias</strong></summary>

- **ADR-008**: Context/Kata/Skill Simplification
- **ADR-007**: Terminology Simplification
- **Research**: `specs/main/research/outputs/kata-harness-execution-model-comparison.md`
- **Toyota Production System**: Jidoka (止めると), Muda (無駄)
- **DRY Principle**: "Every piece of knowledge must have a single, unambiguous, authoritative representation"

</details>

---

*Propuesto: 2026-01-30*
*Autor: Kata Harness Design Session*
