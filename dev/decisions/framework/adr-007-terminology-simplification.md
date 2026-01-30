---
id: "ADR-007"
title: "Simplificación Terminológica: Eliminar SAR y CTX como Nombres de Componentes"
date: "2026-01-29"
status: "Accepted"
related_to: ["VIS-RAISE-002", "glossary-v2.2"]
---

# ADR-007: Simplificación Terminológica

## Contexto

RaiSE v2.1 utilizaba dos nombres de componentes abstractos:
- **SAR** (Software Architecture Reconstruction) - para extracción de convenciones
- **CTX** (Context) - para entrega de contexto

Estos nombres creaban una capa de abstracción entre la documentación y los comandos reales:

```
Documentación: "El SAR Component extrae convenciones"
    ↓
Usuario piensa: "¿Qué es SAR?"
    ↓
Comandos reales: /setup/analyze-codebase, /setup/generate-rules
    ↓
Usuario piensa: "¿Es esto SAR? ¿Por qué se llama 'setup'?"
```

**Problemas identificados:**
1. **Carga cognitiva**: Usuarios deben aprender términos extra que no aparecen en la CLI
2. **Desconexión**: Documentación usa SAR/CTX, CLI usa setup/context
3. **Jerga académica**: SAR viene de literatura de reverse engineering, innecesaria para usuarios
4. **Redundancia**: Los comandos ya son auto-descriptivos

## Decisión

**Eliminar SAR y CTX como nombres de componentes.** Usar únicamente los nombres de categorías de comandos:

| Antes | Después |
|-------|---------|
| "SAR Component" | "setup/ commands" |
| "CTX Component" | "context/ commands" |
| "SAR extrae reglas" | "/setup/generate-rules extrae reglas" |
| "CTX entrega MVC" | "/context/get entrega MVC" |

**Principio adoptado:** Los comandos SON la implementación. No hay capa de abstracción entre documentación y CLI.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Reducción de carga cognitiva: menos términos que aprender |
| ✅ Positivo | Consistencia: documentación y CLI usan mismos términos |
| ✅ Positivo | Auto-descriptivo: setup/ y context/ son intuitivos |
| ✅ Positivo | Onboarding más simple: usuario lee docs, ejecuta comandos, mismos nombres |
| ⚠️ Negativo | ADRs existentes usan "SAR" (ej: ADR-001, ADR-002) - no se actualizan, contexto histórico |
| ⚠️ Negativo | Los archivos sar/vision.md y ctx/vision.md mantienen nombre para continuidad |

## Artefactos Actualizados

1. **Glossary v2.2** (`docs/core/glossary.md`)
   - Añadido: `Command Category`, `context/`, `setup/`, `MVC`
   - Añadido a Anti-Términos: SAR, CTX, "SAR Component", "CTX Component"

2. **Vision v2.2** (`specs/raise/vision.md`)
   - Reemplazado todas las referencias SAR → setup/ commands
   - Reemplazado todas las referencias CTX → context/ commands
   - Layer 2 renombrado: "COMPONENTS" → "GOVERNANCE INFRASTRUCTURE"

3. **Este ADR** documenta la decisión para referencia histórica

## Alternativas Consideradas

### A1: Mantener SAR/CTX como términos internos
**Rechazado**: Crearía documentación dual (interna vs externa), aumentando complejidad.

### A2: Renombrar SAR/CTX a términos más simples (ej: "Learn"/"Guide")
**Rechazado**: Sigue siendo una capa extra. Mejor eliminar la capa completamente.

### A3: Mantener solo para arquitectura avanzada
**Rechazado**: No hay justificación para tener terminología diferente por audiencia.

## Notas de Migración

- ADRs anteriores (001-006) no se actualizan - sirven como contexto histórico
- Los directorios `specs/raise/sar/` y `specs/raise/ctx/` mantienen sus nombres por compatibilidad con enlaces existentes
- En conversaciones futuras, usar "setup commands" y "context commands" en lugar de SAR/CTX
