# Propuestas de Mejora: Disclosure Progresivo para RaiSE v2.1

**Feature**: 001-heutagogy-progressive-disclosure
**Date**: 2026-01-11
**Status**: Complete
**User Story**: US3 (P3) — Identificación de Mejoras Pre-Avance

## Executive Summary

Este documento presenta 9 propuestas de mejora priorizadas para reducir la curva de aprendizaje de nuevos Orquestadores, basadas en el audit-report.md y learning-path.md. Las mejoras están organizadas en 3 categorías: Quick Wins (4), Estructurales (3), y Fundamentales (2).

**Meta SC-005**: Reducir conceptos expuestos en Stage 0 en ≥30%.
**Resultado proyectado**: Reducción de 86% (de ~35 a 5 conceptos en Stage 0).

---

## Propuestas de Mejora

### Quick Wins (Esfuerzo: Pequeño, Impacto: Inmediato)

---

#### QW-01: Simplificar Exposición de Jidoka

**Tipo**: quick_win
**Barrera que elimina**: B-01 (Terminológica), B-02 (Conceptual — cluster Lean/TPS)
**Prioridad**: 🔴 High

**Contexto y Problema**:
Jidoka actualmente se expone con los 4 pasos completos (Detectar → Parar → Corregir → Continuar) desde el onboarding. Esto crea sobrecarga cognitiva y requiere entender el Toyota Production System.

**Decisión Propuesta**:
En documentos de Stage 0-1, presentar Jidoka como **"Parar si algo falla"** — una frase de 4 palabras que captura la esencia sin la complejidad.

Los 4 pasos formales se revelan en Stage 3 cuando el Orquestador está preparado para contribuir al framework.

**Implementación**:
```markdown
# En docs de Stage 0-1:
**Jidoka**: Principio de parar el trabajo cuando detectas un problema,
en lugar de acumular errores.

# En docs de Stage 3:
**Jidoka (自働化)**: Automatización con toque humano.
Ciclo: Detectar → Parar → Corregir → Prevenir.
```

**Documentos Afectados**:
- `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`
- `docs/framework/v2.1/model/20-glossary-v2.1.md` (agregar nota de versión simplificada)
- Futuros docs de onboarding

**Reducción de Complejidad**: 5%

**Impacto en Constitution**: ❌ Ninguno — no modifica principios, solo presentación.

---

#### QW-02: Eliminar Aliases Históricos en Documentación Primaria

**Tipo**: quick_win
**Barrera que elimina**: B-07 (Terminológica — duplicidad Rule/Guardrail, DoD/Validation Gate)
**Prioridad**: 🟡 Medium

**Contexto y Problema**:
El glosario mantiene aliases históricos (`Rule` como alias de `Guardrail`, menciones de `DoD Fractal`) que confunden a nuevos Orquestadores sin agregar valor.

**Decisión Propuesta**:
- En docs de Stage 0-2: usar SOLO términos canónicos (Guardrail, Validation Gate)
- Mover aliases a sección "Histórico/Migración" del glosario
- En docs de Stage 3: mencionar aliases para contexto histórico

**Implementación**:
```markdown
# Antes (glosario actual):
### Guardrail (antes: Rule)
**[RENOMBRADO v2.0]** Directiva operacional...
> **Nota de migración**: El término "Rule" sigue siendo válido como alias.

# Después:
### Guardrail
Directiva operacional que gobierna el comportamiento del agente...

## Apéndice: Términos Históricos (Stage 3)
- `Rule` → Ahora: `Guardrail` (migración v2.0)
- `DoD Fractal` → Ahora: `Validation Gate` (migración v2.0)
```

**Documentos Afectados**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md`
- Cualquier doc que mencione aliases

**Reducción de Complejidad**: 3%

**Impacto en Constitution**: ❌ Ninguno

---

#### QW-03: Crear "Glosario Mínimo" para Stage 0

**Tipo**: quick_win
**Barrera que elimina**: B-03 (Estructural — profundidad variable)
**Prioridad**: 🔴 High

**Contexto y Problema**:
El glosario completo tiene ~35 términos. Un nuevo Orquestador que lo lee desde el inicio experimenta sobrecarga cognitiva innecesaria.

**Decisión Propuesta**:
Crear un documento `glossary-seed.md` (~500 palabras) con SOLO los 5 conceptos de Stage 0, usando lenguaje simplificado y ejemplos concretos.

**Implementación**:
```markdown
# glossary-seed.md

# Glosario Esencial de RaiSE

Los 5 conceptos que necesitas para empezar:

## Orquestador
Tú. El humano que dirige el trabajo del agente de IA.
Defines QUÉ construir; el agente propone CÓMO hacerlo.

## Spec (Especificación)
Documento que describe lo que quieres construir.
Es tu "contrato" con el agente.

## Agent (Agente)
La IA que ejecuta tus instrucciones (Claude, Copilot, Cursor, etc.).

## Validation Gate
Checkpoint de calidad. Si no lo pasas, no avanzas.

## Constitution
Principios inmutables del proyecto. El agente nunca los viola.

---
*Para el glosario completo, ver [glossary-v2.1.md](./20-glossary-v2.1.md)*
```

**Documentos Afectados**:
- Crear: `docs/framework/v2.1/model/20a-glossary-seed.md` (NUEVO)
- Actualizar: README o onboarding que referencie glosario

**Reducción de Complejidad**: 10%

**Impacto en Constitution**: ❌ Ninguno — es documentación adicional, no modificación.

---

#### QW-04: Agregar "Interfaz Simple" a Conceptos Avanzados

**Tipo**: quick_win
**Barrera que elimina**: B-05 (Conceptual — prerequisitos no explícitos), B-08 (Terminológica — Heutagogía)
**Prioridad**: 🟡 Medium

**Contexto y Problema**:
Conceptos como "Context Engineering", "Heutagogía", "Observable Workflow" tienen definiciones técnicas que requieren conocimiento previo.

**Decisión Propuesta**:
Agregar un campo `Interfaz Simple` a cada entrada del glosario que proporcione una frase de <10 palabras accesible para cualquier desarrollador.

**Implementación**:
```markdown
### Context Engineering
**Interfaz Simple**: "Diseñar qué información tiene disponible el agente"

[Definición técnica completa...]

### Heutagogía
**Interfaz Simple**: "Aprendizaje auto-dirigido — tú diseñas cómo aprendes"

[Definición técnica completa...]

### Observable Workflow
**Interfaz Simple**: "El sistema registra todo para que puedas auditar"

[Definición técnica completa...]
```

**Documentos Afectados**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md`
- `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`

**Reducción de Complejidad**: 5%

**Impacto en Constitution**: ❌ Ninguno

---

### Mejoras Estructurales (Esfuerzo: Medio, Impacto: Significativo)

---

#### ST-01: Crear Ontology Bundle "Lite" para Stage 0-1

**Tipo**: structural
**Barrera que elimina**: B-03 (Estructural), B-01 (Terminológica — sobrecarga)
**Prioridad**: 🔴 High

**Contexto y Problema**:
El `ontology-bundle-v2_1.md` actual (~45KB) contiene la ontología completa. Nuevos Orquestadores necesitan una versión reducida.

**Decisión Propuesta**:
Crear `ontology-bundle-lite.md` (~10KB) que contenga:
- Solo los 10 conceptos de Stage 0+1
- Constitution simplificada (solo §1, §4, §5)
- Sin secciones avanzadas (MCP, Ng Patterns, Métricas AI)

**Implementación**:
```markdown
# ontology-bundle-lite.md

# RaiSE Lite: Lo Esencial para Empezar

## 1. Tu Rol: Orquestador
[Definición simplificada]

## 2. Principios Core (3 de 8)
- §1: Humanos definen, máquinas ejecutan
- §4: Validation Gates en cada fase
- §5: Aprender, no solo ejecutar

## 3. Conceptos de Trabajo (7)
[Spec, Agent, Guardrail, Validation Gate, User Story, Implementation Plan, Kata]

## 4. Anti-Patrones Básicos
- No pidas al agente que "decida por ti"
- No ignores los Validation Gates
- No acumules errores (Jidoka: parar si falla)

---
*Para la ontología completa, ver [ontology-bundle-v2_1.md](./25-ontology-bundle-v2_1.md)*
```

**Documentos Afectados**:
- Crear: `docs/framework/v2.1/model/25a-ontology-bundle-lite.md` (NUEVO)
- Actualizar: onboarding para referenciar versión lite primero

**Reducción de Complejidad**: 15%

**Impacto en Constitution**: ❌ Ninguno — es documentación adicional.

---

#### ST-02: Reestructurar Glosario por Etapa de Aprendizaje

**Tipo**: structural
**Barrera que elimina**: B-03 (Estructural — profundidad variable)
**Prioridad**: 🟡 Medium

**Contexto y Problema**:
El glosario actual está organizado alfabéticamente, lo cual no ayuda al disclosure progresivo.

**Decisión Propuesta**:
Reorganizar el glosario con secciones por Stage:
- **Stage 0-1**: Conceptos esenciales (primero)
- **Stage 2**: Conceptos tácticos
- **Stage 3**: Conceptos avanzados
- **Histórico**: Términos deprecados/aliases

**Documentos Afectados**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md` (reestructuración mayor)

**Reducción de Complejidad**: 8%

**Impacto en Constitution**: ❌ Ninguno

---

#### ST-03: Aplicar Patrón ADR-009 a Otros Conceptos Complejos

**Tipo**: structural
**Barrera que elimina**: B-01 (Terminológica), B-02 (Conceptual — cluster Lean)
**Prioridad**: 🔴 High

**Contexto y Problema**:
ADR-009 estableció que ShuHaRi es "filosofía interna" pero el usuario ve `audience: beginner/intermediate/advanced`. Este patrón de "interfaz simple + filosofía interna" puede aplicarse a otros conceptos.

**Decisión Propuesta**:
Extender el patrón ADR-009 a:

| Concepto | Interfaz Externa | Filosofía Interna |
|----------|------------------|-------------------|
| Jidoka | "Parar si falla" | 4 pasos TPS |
| Context Engineering | "Contexto del agente" | MCP + Golden Data |
| Observable Workflow | "Registro de todo" | Framework MELT |
| Niveles de Kata | "Guías de proceso" | Principios/Flujo/Patrón/Técnica |

**Documentos Afectados**:
- Crear: `docs/framework/v2.1/adrs/adr-0XX-progressive-disclosure-pattern.md` (NUEVO ADR)
- Actualizar: `docs/framework/v2.1/model/20-glossary-v2.1.md`
- Actualizar: `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`

**Reducción de Complejidad**: 10%

**Impacto en Constitution**: ❌ Ninguno — extiende patrón existente.

---

### Mejoras Fundamentales (Esfuerzo: Grande, Impacto: Transformacional)

---

#### FN-01: Crear Sistema de Badges/Progresión Visible

**Tipo**: fundamental
**Barrera que elimina**: Todas las barreras indirectamente (hace el progreso tangible)
**Prioridad**: 🟡 Medium (largo plazo)

**Contexto y Problema**:
Los criterios de transición entre etapas existen pero no hay forma visible de saber "en qué etapa estoy".

**Decisión Propuesta**:
Diseñar un sistema de badges o indicadores de progresión que:
- Se muestren en el CLI (`raise status`)
- Indiquen Stage actual del Orquestador
- Sugieran siguiente paso de aprendizaje

**Implementación** (conceptual):
```bash
$ raise status

╭────────────────────────────────────────────╮
│  🎯 Stage 1: Operacional                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━ 60%             │
│                                            │
│  ✅ Specs creadas: 5                       │
│  ✅ Gates pasados: 12/15 (80%)             │
│  ⬜ Katas completadas: 2/5                 │
│                                            │
│  → Siguiente: Completar 3 Katas de Flujo   │
╰────────────────────────────────────────────╯
```

**Documentos Afectados**:
- Crear: ADR para sistema de progresión
- Modificar: raise-kit (CLI)
- Crear: tracking de métricas por usuario

**Reducción de Complejidad**: N/A (mejora experiencia, no reduce conceptos)

**Impacto en Constitution**: ⚠️ Posible — requiere validar contra §5 Heutagogía (no crear dependencia del sistema de badges).

---

#### FN-02: Integrar Learning Path en Documentación Oficial

**Tipo**: fundamental
**Barrera que elimina**: B-03 (Estructural)
**Prioridad**: 🔴 High (post-validación)

**Contexto y Problema**:
El Learning Path propuesto existe como artefacto de análisis, pero no está integrado en la documentación oficial del framework.

**Decisión Propuesta**:
Después de validar con Orquestadores reales:
1. Crear sección "Getting Started" en docs oficiales que siga el Learning Path
2. Agregar indicadores de Stage a cada documento
3. Crear navegación por etapa en el README

**Documentos Afectados**:
- Crear/modificar: `docs/framework/v2.1/README.md`
- Crear: `docs/framework/v2.1/getting-started/`
- Agregar headers: `<!-- Stage: 0 -->` a todos los docs

**Reducción de Complejidad**: 15% (al hacer el camino explícito)

**Impacto en Constitution**: ❌ Ninguno — es reorganización documental.

---

## Resumen de Impacto

### Por Tipo de Mejora

| Tipo | Count | Reducción Combinada |
|------|-------|---------------------|
| Quick Wins | 4 | 23% |
| Estructurales | 3 | 33% |
| Fundamentales | 2 | 15%+ (TBD) |
| **Total** | **9** | **~71%+** |

### Priorización Recomendada

| Orden | ID | Mejora | Esfuerzo | Impacto |
|-------|-----|--------|----------|---------|
| 1 | QW-03 | Glosario Mínimo | Pequeño | 10% |
| 2 | QW-01 | Simplificar Jidoka | Pequeño | 5% |
| 3 | ST-01 | Ontology Bundle Lite | Medio | 15% |
| 4 | ST-03 | Patrón ADR-009 extendido | Medio | 10% |
| 5 | QW-04 | Interfaz Simple en glosario | Pequeño | 5% |
| 6 | QW-02 | Eliminar aliases | Pequeño | 3% |
| 7 | ST-02 | Reestructurar glosario | Medio | 8% |
| 8 | FN-02 | Integrar Learning Path | Grande | 15% |
| 9 | FN-01 | Sistema de badges | Grande | TBD |

---

## Validación de Gates

### Gate-Coherencia ✅ PASS

- Ninguna mejora modifica principios §1-§8 de la Constitution
- Todas las mejoras son aditivas o de reorganización
- El patrón ADR-009 (ya aprobado) se extiende, no se cambia

### Gate-Trazabilidad ✅ PASS

- Cada mejora tiene rationale documentado
- Barreras específicas identificadas y vinculadas
- Documentos afectados listados explícitamente

### SC-005: Reducción ≥30% ✅ PASS

**Cálculo**:
- Estado actual: ~35 conceptos expuestos en onboarding
- Con Learning Path Stage 0: 5 conceptos expuestos
- Reducción: (35-5)/35 = **86%** > 30% ✅

---

## Próximos Pasos

1. **Validar con stakeholders** — Revisar propuestas antes de implementar
2. **Implementar Quick Wins** — QW-01, QW-02, QW-03, QW-04
3. **Crear ADR para patrón disclosure progresivo** — Formalizar ST-03
4. **Crear Ontology Bundle Lite** — ST-01
5. **Recolectar feedback de Orquestadores reales** — Validar Learning Path
6. **Integrar en docs oficiales** — FN-02 post-validación

---

*Improvement Proposals completado. Proceder a Phase 6: Polish & Validation.*
