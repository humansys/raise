# ADR-011: Modelo Híbrido - Katas, Templates y Validation Gates

**Estado:** ✅ Accepted
**Fecha:** 2026-01-12
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

Durante el proceso de normalización de katas a la ontología v2.1 (feature 006-katas-normalization), se identificó una **incoherencia estructural fundamental** entre:

1. **La metodología v2.1** (`21-methodology-v2.md`) que define 8 fases (0-7)
2. **Los templates** (`src/templates/`) que definen estructuras de artefactos
3. **Las katas existentes** (15 migradas a `src/katas/`) que mezclan procesos, checklists y estructuras

### Problema Identificado

| Problema | Manifestación | Desperdicio Lean |
|----------|---------------|------------------|
| Templates sin proceso | "Usa template X" sin guía de cómo llenarlo | Mura (inconsistencia en outputs) |
| Katas que son checklists | `flujo-15,16,17` son Validation Gates, no procesos | Muda (documentos mal clasificados) |
| Duplicación template/kata | `patron-01` duplica `tech_design.md` | Muda (esfuerzo duplicado) |
| Flujo principal sin katas | Fases 1-4 no tienen katas definidas | Mura (proceso informal) |
| Katas específicas de proyecto | `flujo-06` con 40+ guardrails .NET | Muri (sobrecarga cognitiva) |

### Análisis del Estado Actual

**Lo que la metodología prescribe:**

| Fase | Artefacto | Guía Disponible |
|------|-----------|-----------------|
| 1: Discovery | PRD | Template ✅, Kata ❌ |
| 2: Vision | Solution Vision | Template ✅, Kata ❌ |
| 3: Tech Design | Tech Design | Template ✅, Kata ⚠️ (ambigua) |
| 4: Backlog | User Stories | Template ✅, Kata ❌ |
| 5: Plan | Implementation Plan | Kata ✅ (`flujo-04`) |
| 6: Development | Código | Guardrails ✅, Kata ⚠️ |
| 7: UAT | Deploy | — |

**Las 15 katas existentes incluyen:**
- 2 meta-katas de principios (válidas)
- 1 kata core del flujo (flujo-04, válida)
- 3 katas que son Validation Gates disfrazados (flujo-15,16,17)
- 5 katas sin referencia en metodología
- 4 katas que duplican o solapan templates

---

## Decisión

Adoptar el **Modelo Híbrido** con separación clara de responsabilidades:

### Las Tres Capas

```
┌─────────────────────────────────────────────────────────────┐
│                      MODELO HÍBRIDO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   TEMPLATE              KATA                VALIDATION GATE │
│   ─────────            ─────               ──────────────── │
│   ¿QUÉ produce?        ¿CÓMO hacerlo?      ¿ESTÁ BIEN?      │
│                                                             │
│   • Estructura         • Proceso           • Checklist      │
│   • Campos/Secciones   • Pasos ordenados   • Criterios      │
│   • Formato output     • Jidoka inline     • Gate pass/fail │
│                                                             │
│   [Personalizable      [Genérico por       [Componible      │
│    por org/repo]        nivel semántico]    por contexto]   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Definiciones Formales

| Componente | Responsabilidad | Ubicación | Quién Adapta |
|------------|-----------------|-----------|--------------|
| **Template** | Estructura del artefacto de salida | `templates/{dominio}/` | Organización/Proyecto |
| **Kata** | Proceso para producir el artefacto | `katas/{nivel}/` | Framework RaiSE |
| **Validation Gate** | Criterios de aceptación por fase | `gates/` | Proyecto/Fase |

### Estructura de Katas v2.1 (desde cero)

```
katas/
├── principios/                    # ¿Por qué? ¿Cuándo?
│   ├── 00-meta-kata.md            # Qué es una kata, cómo usarla
│   └── 01-execution-protocol.md   # Protocolo de ejecución ShuHaRi
│
├── flujo/                         # ¿Cómo fluye? (una por fase)
│   ├── 01-discovery.md            # NUEVO: Fase 1 → PRD
│   ├── 02-solution-vision.md      # NUEVO: Fase 2 → Vision
│   ├── 03-tech-design.md          # NUEVO: Fase 3 → Tech Design
│   ├── 04-implementation-plan.md  # EXISTENTE (core)
│   ├── 05-backlog-creation.md     # NUEVO: Fase 4 → Backlog
│   └── 06-development.md          # NUEVO: Fase 6 → Código (genérico)
│
├── patron/                        # ¿Qué forma? (patrones reutilizables)
│   ├── 01-code-analysis.md        # Para brownfield
│   └── 02-ecosystem-discovery.md  # Para brownfield
│
└── tecnica/                       # ¿Cómo hacer? (instrucciones específicas)
    └── (según necesidad)
```

### Relación Kata → Template

Cada kata de flujo referencia su template asociado:

```yaml
# Ejemplo: flujo-03-tech-design.md
kata:
  id: flujo-03-tech-design
  nivel: flujo
  pregunta_guia: "¿Cómo fluye la creación del Tech Design?"

  template_asociado: templates/tech/tech_design.md
  validation_gate: gates/gate-design.md

  inputs:
    - artefacto: PRD
      origen: flujo-01
    - artefacto: Solution Vision
      origen: flujo-02
```

---

## Consecuencias

### Positivas

- **Separación clara**: Cada componente tiene una responsabilidad única
- **Adaptabilidad**: Templates personalizables sin modificar procesos
- **Flujo completo**: Cada fase de la metodología tiene su kata guía
- **Validation Gates explícitos**: No confundidos con katas
- **Menor carga cognitiva**: Usuario sabe qué buscar dónde
- **Reutilización**: Un template puede usarse con diferentes katas

### Negativas

- **Migración requerida**: Katas existentes deben reclasificarse o eliminarse
- **Más artefactos**: Tres tipos en lugar de uno
- **Documentación a actualizar**: Metodología, glosario, constitution

### Neutras

- **Compatible con ADR-009**: ShuHaRi sigue aplicando a katas
- **Templates existentes válidos**: Solo necesitan enlazarse a katas
- **Jidoka inline preservado**: Sigue siendo parte de cada paso de kata

---

## Alternativas Consideradas

### 1. Template-first (Templates Auto-suficientes)

Templates con instrucciones de llenado embebidas.

**Rechazado porque:**
- Pierde el concepto de kata como "sensor de desviación"
- No hay proceso estandarizado, cada quien llena diferente
- No soporta Jidoka inline

### 2. Kata-first (Todo es Kata)

Templates embebidos en katas.

**Rechazado porque:**
- Duplicación cuando múltiples katas usan mismo output
- Difícil personalizar por organización
- Katas se vuelven monolíticas

### 3. Mantener Estado Actual

Normalizar las 15 katas existentes sin reestructurar.

**Rechazado porque:**
- Perpetúa incoherencia estructural
- Katas que son Validation Gates siguen mal clasificadas
- Flujo principal (Fases 1-4) sigue sin guía

---

## Implementación

### Fase 1: Deprecación

1. Marcar katas legacy como deprecated en `src/katas/`
2. Crear `src/katas/legacy/` y mover las 15 katas actuales
3. Documentar mapeo legacy → nuevo (para migración)

### Fase 2: Estructura Base

1. Crear estructura de directorios nueva
2. Crear `gates/` con Validation Gates extraídos de flujo-15,16,17
3. Actualizar `21-methodology-v2.md` con referencias a nuevas katas

### Fase 3: Katas del Flujo Principal

1. Crear `flujo-01-discovery.md`
2. Crear `flujo-02-solution-vision.md`
3. Crear `flujo-03-tech-design.md`
4. Migrar/refinar `flujo-04-implementation-plan.md`
5. Crear `flujo-05-backlog-creation.md`
6. Crear `flujo-06-development.md` (genérico)

### Fase 4: Katas de Patrón

1. Migrar `patron-02` → `patron-01-code-analysis.md`
2. Migrar `patron-03` → `patron-02-ecosystem-discovery.md`

### Fase 5: Documentación

1. Actualizar `20-glossary-v2.1.md` con definiciones Template/Kata/Gate
2. Actualizar `21-methodology-v2.md` con estructura nueva
3. Actualizar `00-constitution-v2.md` si aplica
4. Actualizar índice ADR

---

## Referencias

- [21-methodology-v2.md](../model/21-methodology-v2.md) — Metodología RaiSE
- [20-glossary-v2.1.md](../model/20-glossary-v2.1.md) — Glosario canónico
- [ADR-006a](./adr-006a-validation-gates.md) — Validation Gates
- [ADR-009](./adr-009-shuhari-hybrid.md) — ShuHaRi implementation
- Feature 006-katas-normalization — Análisis que identificó la incoherencia

---

*Este ADR formaliza la decisión de adoptar un modelo híbrido que separa claramente Templates (estructura), Katas (proceso) y Validation Gates (verificación), creando las katas v2.1 desde cero para alinearse con la metodología.*
