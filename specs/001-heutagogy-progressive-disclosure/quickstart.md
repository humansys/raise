# Quickstart: Evaluación Ontológica para Disclosure Progresivo

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Purpose**: Guía de ejecución para producir los artefactos de esta feature

---

## Prerequisites

- Acceso al repositorio `raise-commons`
- Branch: `001-heutagogy-progressive-disclosure`
- Contexto cargado: Constitution v2.0, Glosario v2.1, Metodología v2.1

---

## Workflow Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│  AUDITORÍA  │────▶│LEARNING PATH│────▶│MEJORAS PROPUESTAS   │
│  (P1)       │     │  (P2)       │     │  (P3)               │
└─────────────┘     └─────────────┘     └─────────────────────┘
      │                   │                      │
      ▼                   ▼                      ▼
 audit-report.md    learning-path.md    improvement-proposals.md
```

---

## Step-by-Step Execution

### Step 1: Auditoría de Complejidad (P1)

**Input**: Documentos de ontología v2.1
**Output**: `audit-report.md`

1. **Listar todos los conceptos** del glosario v2.1 (~35 términos)

2. **Clasificar cada concepto** usando el modelo de data-model.md:
   - Complejidad: `basic` / `intermediate` / `advanced`
   - Dependencias: listar conceptos prerequisito
   - Utilidad para novatos: `high` / `medium` / `low`
   - Fase ShuHaRi: `shu` / `ha` / `ri`

3. **Identificar conceptos semilla** (máximo 7±2):
   - Alta utilidad para novatos
   - Baja complejidad
   - Pocas o ninguna dependencia

4. **Mapear barreras de entrada**:
   - Tipo: conceptual / terminológica / estructural
   - Desperdicio Lean: Muda / Mura / Muri
   - Severidad: high / medium / low

5. **Generar grafo de dependencias** para visualizar clusters de complejidad

**Validation Gate**: audit-report.md pasa Gate-Terminología y Gate-Coherencia

---

### Step 2: Diseño del Learning Path (P2)

**Input**: audit-report.md
**Output**: `learning-path.md`

1. **Definir 4 etapas** basadas en:
   - Fase ShuHaRi (Shu para etapas 0-1, Ha para 2, Ri para 3)
   - Niveles de competencia del Orquestador (Pre-Op, L1, L2, L3)

2. **Asignar conceptos a etapas**:
   - Stage 0: Solo conceptos semilla (máximo 5)
   - Stage 1: Completar conceptos básicos (hasta 10)
   - Stage 2: Conceptos intermedios (hasta 20)
   - Stage 3: Ontología completa (~35)

3. **Definir criterios de transición** entre etapas:
   - Qué debe poder hacer el Orquestador para avanzar
   - Indicadores observables (no subjetivos)

4. **Incluir checkpoint heutagógico** por etapa:
   - Pregunta reflexiva alineada con §5

5. **Mapear Katas accesibles** por etapa:
   - Stage 0: Ninguna (solo templates)
   - Stage 1: Solo nivel Flujo
   - Stage 2: Flujo + Patrón
   - Stage 3: Todos los niveles

**Validation Gate**: Cada etapa expone máximo 7 conceptos nuevos (Ley de Miller)

---

### Step 3: Propuestas de Mejora (P3)

**Input**: audit-report.md, learning-path.md
**Output**: `improvement-proposals.md`

1. **Identificar Quick Wins**:
   - Cambios que reducen complejidad con esfuerzo mínimo
   - No requieren modificar Constitution
   - Ejemplo: Simplificar exposición de Jidoka en docs de onboarding

2. **Identificar Mejoras Estructurales**:
   - Requieren modificar múltiples documentos
   - Esfuerzo medio
   - Ejemplo: Crear versión "lite" del ontology-bundle para Stage 0

3. **Identificar Mejoras Fundamentales**:
   - Podrían requerir ADR nuevo
   - Esfuerzo alto pero impacto significativo
   - Ejemplo: Aplicar patrón ADR-009 a todos los conceptos complejos

4. **Para cada mejora documentar** (formato ADR-lite):
   - Título
   - Contexto y problema
   - Decisión propuesta
   - Impacto en documentos
   - Reducción estimada de complejidad

5. **Validar contra Constitution**:
   - Ninguna mejora viola principios §1-§8
   - Gate-Coherencia pasa

**Validation Gate**: Mejoras propuestas reducen conceptos en Stage 0 en ≥30%

---

## Artefactos Finales

| Artefacto | Contenido | Validation Gate |
|-----------|-----------|-----------------|
| `audit-report.md` | Inventario de conceptos con clasificaciones | Gate-Terminología |
| `learning-path.md` | 4 etapas con conceptos, criterios, checkpoints | Gate-Coherencia |
| `improvement-proposals.md` | Lista priorizada de mejoras con formato ADR-lite | Gate-Coherencia |

---

## Checklist de Completitud

- [ ] Todos los conceptos del glosario v2.1 clasificados
- [ ] 5-9 conceptos semilla identificados
- [ ] Learning Path con 3-5 etapas definidas
- [ ] Cada etapa con criterio de transición explícito
- [ ] Cada etapa con checkpoint heutagógico
- [ ] Al menos 3 Quick Wins identificados
- [ ] Ninguna mejora viola Constitution
- [ ] Gate-Terminología pasa (terminología canónica)
- [ ] Gate-Coherencia pasa (sin contradicciones)
- [ ] Gate-Trazabilidad pasa (cambios documentados)

---

## Next Steps After Completion

1. Revisar artefactos con stakeholders
2. Crear ADRs formales para mejoras fundamentales
3. Integrar learning-path.md a documentación oficial
4. Actualizar ontology-bundle con versión "lite" para Stage 0
5. Medir adopción con feedback de nuevos Orquestadores

---

*Quickstart completado. Ejecutar `/speckit.tasks` para generar tareas atómicas.*
