# Research: Ciclos de Trabajo RaiSE

**Feature**: 004-operation-layers
**Date**: 2026-01-11
**Purpose**: Consolidar análisis de katas existentes y validar mapeo de ciclos

---

## 1. Análisis de Katas de Onboarding

### Pregunta
¿Las katas existentes en `src/katas/cursor_rules/` cubren completamente el Ciclo de Onboarding?

### Hallazgos

| Kata | Fase que cubre | Propósito |
|------|----------------|-----------|
| `L0-01-gestion-integral-reglas-cursor.md` | Orquestación completa | Kata principal que coordina todas las fases |
| `L2-01-analisis-exploratorio-repositorio.md` | Fase 1: Discovery | Análisis de tecnologías, estructura, patrones |
| `L2-02-inicializacion-gobernanza-reglas.md` | Fase 2: Gobernanza | Crear estructura de documentos de gobernanza |
| `L2-03-extraccion-generacion-regla-cursor.md` | Fase 5: Iterativo | Extraer y generar reglas específicas |
| `L2-04-establecimiento-reglas-estandares-generales.md` | Fase 3.1: Fundacionales | Estándares de codificación |
| `L2-05-establecimiento-reglas-metodologia-raise.md` | Fase 3.2: Metodología | Reglas de metodología RaiSE |
| `L2-06-establecimiento-meta-reglas-fundamentales.md` | Fase 4: Meta-reglas | Reglas de gestión y precedencia |

### Decisión
**Sí, las katas cubren el Ciclo de Onboarding completo.** La kata L0-01 define 7 fases (0-6) más una fase 7 de mantenimiento. El ciclo incluye:
- Preparación del agente
- Análisis exploratorio (software architecture reconstruction)
- Inicialización de gobernanza
- Reglas fundacionales
- Meta-reglas
- Generación iterativa
- Validación

### Rationale
Las katas fueron diseñadas específicamente para el onboarding de repositorios a RaiSE, con énfasis en la extracción de patrones existentes y establecimiento de gobernanza.

---

## 2. Mapeo Fases RaiSE → Ciclos de Trabajo

### Pregunta
¿El mapeo propuesto de Fases (0-7) a Ciclos es coherente con la metodología?

### Análisis de 21-methodology-v2.md

| Fase RaiSE | Nombre | Artefacto Principal |
|------------|--------|---------------------|
| Fase 0 | Context | Notas de exploración |
| Fase 1 | Discovery | PRD |
| Fase 2 | Solution Vision | Solution Vision Document |
| Fase 3 | Technical Design | Tech Design Document |
| Fase 4 | Backlog | User Stories |
| Fase 5 | Implementation Plan | Plan por HU |
| Fase 6 | Development | Código |
| Fase 7 | UAT & Deploy | Feature en producción |

### Mapeo Propuesto

| Ciclo | Fases RaiSE | Justificación |
|-------|-------------|---------------|
| **Onboarding** | Fase 0 (parcial) | Establece contexto técnico del repo, no del proyecto |
| **Proyecto** | Fases 1-3 | PRD, Vision, Design son a nivel épica/iniciativa |
| **Feature** | Fases 4-6 | Backlog → Plan → Dev son a nivel feature individual |
| **Mejora** | Fase 7+ | Deploy, retrospectiva, Kaizen |

### Decisión
**El mapeo es coherente pero requiere clarificación.**

- **Fase 0 (Context)** tiene dos interpretaciones:
  - Context de repositorio → Ciclo de Onboarding
  - Context de proyecto/épica → Ciclo de Proyecto

### Rationale
La metodología describe Fase 0 como "Establecer comprensión inicial del problema y el ambiente", que puede ser tanto técnico (repo) como de negocio (proyecto).

**Resolución**: El documento 26-work-cycles debe clarificar que Fase 0 puede ocurrir en Onboarding (técnico) o Proyecto (negocio).

---

## 3. Cobertura spec-kit → Ciclos

### Pregunta
¿Qué comandos de spec-kit cubren qué ciclos?

### Análisis

| Comando spec-kit | Función | Ciclo que cubre |
|------------------|---------|-----------------|
| `/speckit.specify` | Genera spec de feature | Feature (Fase 4 parcial) |
| `/speckit.plan` | Genera plan de implementación | Feature (Fase 5) |
| `/speckit.tasks` | Genera lista de tareas | Feature (Fase 5-6) |
| `/speckit.implement` | Ejecuta implementación | Feature (Fase 6) |
| `/speckit.analyze` | Valida coherencia | Mejora (parcial) |
| `/speckit.clarify` | Clarifica requisitos | Feature (Fase 4) |
| `/speckit.constitution` | Actualiza constitution | Mejora (parcial) |

### Decisión
**spec-kit cubre principalmente el Ciclo de Feature**, con cobertura parcial del Ciclo de Mejora.

| Ciclo | Cobertura spec-kit |
|-------|-------------------|
| Onboarding | ❌ No cubre |
| Proyecto | ❌ No cubre |
| Feature | ✅ Cubre completamente |
| Mejora | ⚠️ Parcial (analyze, constitution) |

### Rationale
spec-kit fue diseñado como herramienta de desarrollo specification-driven a nivel feature. No tiene comandos para:
- Análisis de repositorio existente (Onboarding)
- PRD/Vision/Design a nivel épica (Proyecto)
- Retrospectivas estructuradas (Mejora completa)

---

## 4. Katas Faltantes por Ciclo

### Análisis de Gaps

| Ciclo | Katas Existentes | Gap |
|-------|-----------------|-----|
| Onboarding | L0-01, L2-01 a L2-06 | ✅ Completo |
| Proyecto | (ninguna formal) | ❌ No hay katas de PRD/Vision/Design |
| Feature | flujo/04-generacion-plan | ⚠️ Parcial (spec-kit cubre) |
| Mejora | L0-01 Fase 7 | ⚠️ Solo mantenimiento, no retrospectiva |

### Decisión
**Documentar gaps sin crear katas nuevas (YAGNI).**

El documento 26-work-cycles debe:
1. Indicar que Ciclo de Onboarding está cubierto por katas
2. Indicar que Ciclo de Proyecto no tiene katas formales (uso ad-hoc)
3. Indicar que Ciclo de Feature usa spec-kit
4. Indicar que Ciclo de Mejora tiene cobertura parcial

### Rationale
Crear nuevas katas ahora sería especulativo. Primero documentar la estructura, luego iterar según necesidad real.

---

## Resumen de Decisiones

| # | Decisión | Rationale |
|---|----------|-----------|
| D1 | Katas L0-01/L2-* cubren Ciclo Onboarding | Análisis confirmó 7 fases completas |
| D2 | Fase 0 puede ser Onboarding o Proyecto | Contexto técnico vs negocio |
| D3 | spec-kit cubre Ciclo Feature | Comandos mapean a Fases 4-6 |
| D4 | Documentar gaps sin crear katas (YAGNI) | Iterar según necesidad real |
