# Research: Glosario Mínimo (Seed) para Stage 0

**Feature**: 002-glossary-seed
**Date**: 2026-01-11
**Phase**: 0 (Research & Decision Making)

## Objective

Investigar cómo crear definiciones simplificadas y ejemplos concretos para los 5 conceptos semilla del Stage 0, manteniendo coherencia semántica con el glosario v2.1 canónico.

## Research Questions

### Q1: ¿Cuáles son las definiciones canónicas de los 5 conceptos en glosario v2.1?

**Source**: `docs/framework/v2.1/model/20-glossary-v2.1.md`

**Findings**:
1. **Orquestador**: Humano que diseña contexto y valida outputs del agente
2. **Spec**: Documento que describe QUÉ construir (contrato con el agente)
3. **Agent**: IA que ejecuta instrucciones (Claude, Copilot, etc.)
4. **Validation Gate**: Punto de control de calidad por fase
5. **Constitution**: Principios inmutables del proyecto

**Decision**: Usar estas definiciones como base, simplificándolas sin perder precisión conceptual.

---

### Q2: ¿Qué ejemplos concretos resuenan con desarrolladores nuevos al framework?

**Approach**: Usar casos de uso reales del workflow spec-kit como ejemplos.

**Findings**:

| Concepto | Ejemplo Concreto Propuesto |
|----------|---------------------------|
| Orquestador | "Tú eres el Orquestador cuando ejecutas `/speckit.specify` y defines QUÉ quieres construir" |
| Spec | "El archivo `spec.md` que describe tu feature es la Spec" |
| Agent | "Claude Code ejecutando los comandos de spec-kit es el Agent" |
| Validation Gate | "Antes de hacer `/speckit.plan` debes pasar el gate de spec completo" |
| Constitution | "CLAUDE.md y `.specify/memory/constitution.md` contienen las reglas inmutables" |

**Decision**: Usar ejemplos del flujo spec-kit que el usuario ya está experimentando.

---

### Q3: ¿Cómo simplificar definiciones sin perder coherencia semántica?

**Pattern Identified**: "Interfaz Simple + Filosofía Interna" (patrón ADR-009)

**Strategy**:
- **Interfaz Simple**: Frase de <10 palabras accesible para cualquier desarrollador
- **Detalle Mínimo**: 1-2 oraciones adicionales de contexto
- **Ejemplo Concreto**: Caso de uso del framework

**Template Propuesto**:
```markdown
## [Concepto]

[Frase simple de 1 línea]

[1-2 oraciones de contexto]

**Ejemplo**: [Caso de uso concreto del framework]
```

**Decision**: Adoptar este template para los 5 conceptos.

---

### Q4: ¿Cómo asegurar que la longitud quede en 400-600 palabras?

**Calculation**:
- 5 conceptos × ~100 palabras por concepto = 500 palabras
- Introducción: ~50 palabras
- Cierre con referencia a glosario completo: ~50 palabras
- **Total**: ~600 palabras (dentro del rango)

**Decision**:
- Introducción breve (2-3 líneas)
- Cada concepto: máximo 100 palabras
- Cierre con enlace al glosario v2.1

---

## Decisions Summary

| Decision | Rationale |
|----------|-----------|
| **D1**: Usar definiciones del glosario v2.1 como base | Mantiene coherencia semántica (Constitution §I) |
| **D2**: Ejemplos del flujo spec-kit | Resuena con experiencia inmediata del Orquestador |
| **D3**: Patrón "Interfaz Simple + Detalle Mínimo" | Alineado con ADR-009 y principio de simplicidad |
| **D4**: Template estandarizado para 5 conceptos | Asegura consistencia y longitud controlada |

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Definiciones completamente nuevas | Violaría coherencia semántica con glosario v2.1 |
| Ejemplos genéricos de software | No contextualizan al framework RaiSE específicamente |
| Formato de tabla | Menos legible que secciones narrativas |
| Incluir 7 conceptos (Stage 0+1) | Excedería 600 palabras y diluiría el "mínimo" |

## Next Steps

1. Crear `data-model.md` con estructura detallada del documento seed
2. Crear `quickstart.md` con guía de ejecución
3. Implementar en `/speckit.tasks` → `/speckit.implement`

---

*Research completado. Proceder a Phase 1 (data-model.md, quickstart.md).*
