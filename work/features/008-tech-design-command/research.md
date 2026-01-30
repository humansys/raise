# Research: Tech Design Command Generation

**Feature**: Tech Design Command Generation  
**Branch**: `001-tech-design-command`  
**Date**: 2026-01-20  
**Phase**: 0 - Research & Analysis

## Purpose

Investigar y documentar las decisiones técnicas necesarias para implementar el comando `/raise.4.tech-design`, incluyendo análisis de patrones de comandos existentes, mapeo del kata a estructura ejecutable, y estrategias de llenado del template.

## Research Areas

### 1. Análisis de Patrón de Comandos Existentes

#### Comandos Analizados
- `.raise-kit/commands/02-projects/raise.1.discovery.md`
- `.raise-kit/commands/02-projects/raise.2.vision.md`

#### Estructura Común Identificada

**Frontmatter YAML**:
```yaml
---
description: [Descripción de 1 línea del comando]
handoffs:
  - label: [Nombre del siguiente paso]
    agent: [nombre.del.siguiente.comando]
    prompt: [Texto que se enviará al siguiente comando]
    send: true
---
```

**Secciones del Comando**:
1. **## User Input**: Captura `$ARGUMENTS` del usuario
2. **## Outline**: Instrucciones paso a paso numeradas
3. **## Notas**: Contexto adicional (ej: "Para Proyectos Brownfield")
4. **## High-Signaling Guidelines**: Principios de ejecución
5. **## AI Guidance**: Guía específica para el agente

**Convenciones de Referencias**:
- ✅ Usar `.specify/templates/...` (NO `.raise-kit/templates/...`)
- ✅ Usar `.specify/gates/...` (NO `.raise-kit/gates/...` ni `src/gates/...`)
- ✅ Usar `.specify/scripts/bash/...` para scripts helper
- ✅ Rutas de output: `specs/main/[artefacto].md`

**Patrón de Pasos en Outline**:
```markdown
3. **Paso N: [Título del Paso]**:
   - [Instrucción 1]
   - [Instrucción 2]
   - **Verificación**: [Criterio de éxito]
   - > **Si no puedes continuar**: [Condición] → [Acción correctiva]
```

**Patrón de Jidoka**:
- Usar bloque `> **Si no puedes continuar**:` después de cada verificación
- Formato: `[Condición] → [Acción sugerida]`
- Ejemplos:
  - "Contexto disperso → Solicitar consolidación"
  - "Template no encontrado → Verificar ruta"
  - "Stakeholder no disponible → Documentar intento y proceder con nota"

**Patrón de Finalize & Validate**:
```markdown
11. **Finalize & Validate**:
    - Confirm file existence with `check_file "ruta" "descripción"`.
    - Ejecutar validación usando `.specify/gates/raise/gate-[nombre].md`.
    - Run `.specify/scripts/bash/update-agent-context.sh`.
    - Verificar criterios del gate: [lista de checkboxes]
```

#### Decision: Estructura del Comando

**Chosen**: Seguir exactamente el patrón de `raise.1.discovery.md`

**Rationale**:
- Consistencia con comandos existentes
- Patrón ya validado y funcional
- Facilita mantenimiento futuro
- Usuarios ya familiarizados con el formato

**Alternatives Considered**:
- Crear estructura nueva optimizada → Rechazado: rompe consistencia
- Simplificar estructura → Rechazado: pierde trazabilidad

---

### 2. Mapeo de Kata a Estructura de Comando

#### Kata Source: `src/katas-v2.1/flujo/03-tech-design.md`

**15 Pasos del Kata**:

| # | Título del Paso | Acción Principal | Verificación | Jidoka |
|---|-----------------|------------------|--------------|--------|
| 1 | Cargar Vision y Contexto | Cargar solution_vision.md, PRD, docs técnicas | Todos los documentos accesibles | Documentación faltante → Ejecutar patron-01 o documentar decisiones |
| 2 | Instanciar Template | Copiar template a specs/main/tech_design.md | Archivo existe con metadatos | Template no encontrado → Verificar ruta |
| 3 | Visión General Técnica | Completar sección "Visión General" | Comprensible sin leer PRD | Visión desconectada → Revisar Solution Vision |
| 4 | Solución Propuesta | Completar sección "Solución Propuesta" | Approach claro en 5 min | Múltiples approaches → Documentar alternativas y escalar |
| 5 | Arquitectura de Componentes | Completar sección "Arquitectura" | Diagrama + SRP por componente | Componentes mezclados → Aplicar SRP |
| 6 | Flujos de Datos | Completar sección "Flujo de Datos" | Trazabilidad de inputs a outputs | Flujos incompletos → Identificar cada entrada |
| 7 | Contratos de API | Completar sección "Contratos de API" | Ejemplos request/response | Contratos ambiguos → Definir tipos y validaciones |
| 8 | Modelo de Datos | Completar sección "Modelo de Datos" | Soporta todos los requisitos | Requisitos no mapeados → Revisar cada FR |
| 9 | Algoritmos Clave | Completar sección "Algoritmos" | Lógica compleja documentada | Lógica no clara → Preguntar casos edge |
| 10 | Seguridad | Completar sección "Seguridad" | Cada endpoint tiene authn/authz | Requisitos no claros → Asumir mínimos |
| 11 | Manejo de Errores | Completar sección "Errores" | Catálogo de códigos de error | Sin estrategia → Definir códigos estándar |
| 12 | Alternativas Consideradas | Completar sección "Alternativas" | Al menos 2 alternativas | No hubo alternativas → Documentar "hacer nada" |
| 13 | Preguntas y Riesgos | Completar sección "Preguntas Abiertas" | Cada pregunta tiene owner | Preguntas sin owner → Asignar roles |
| 14 | Estrategia de Testing | Completar sección "Estrategia de Pruebas" | Cubre camino crítico | Sin estrategia → Definir mínimos |
| 15 | Validar con Equipo | Presentar para revisión | Aprobación de Arquitecto/Tech Lead | Feedback no resuelto → Priorizar blockers |

#### Decision: Nivel de Detalle en Pasos

**Chosen**: Implementar los 15 pasos explícitamente en el comando

**Rationale**:
- Máxima trazabilidad con el kata
- Cada paso tiene verificación clara
- Facilita debugging si algo falla
- Permite Jidoka granular

**Alternatives Considered**:
- Agrupar pasos relacionados (ej: 5-8 como "Diseño Técnico") → Rechazado: pierde granularidad
- Pasos implícitos (solo instrucción general) → Rechazado: pierde trazabilidad

#### Mapping Strategy

**Paso del Kata → Paso del Comando**:
- Cada paso del kata se convierte en un paso numerado en la sección "Outline"
- La verificación del kata se convierte en bullet "**Verificación**:"
- El bloque Jidoka del kata se convierte en bullet "> **Si no puedes continuar**:"
- Las instrucciones del kata se convierten en bullets de acción

**Ejemplo de Mapeo** (Paso 3 del kata):

```markdown
3. **Paso 3: Definir Visión General Técnica**:
   - Completar sección "Visión General y Objetivo" del template
   - Resumir el objetivo desde perspectiva técnica
   - Identificar el problema técnico central a resolver
   - Conectar con los goals de la Solution Vision
   - **Verificación**: La visión técnica es comprensible para un desarrollador que no ha leído el PRD, pero está claramente alineada con los objetivos de negocio.
   - > **Si no puedes continuar**: Visión desconectada del negocio → Revisar Solution Vision y extraer los mecanismos técnicos identificados en el paso de alineamiento.
```

---

### 3. Estrategia de Llenado del Template

#### Template Analysis: `src/templates/tech/tech_design.md`

**14 Secciones Identificadas**:

1. **Frontmatter YAML**: document_id, title, project_name, feature_us_ref, client, version, date, author, related_docs, status
2. **Visión General y Objetivo**: Resumen técnico del objetivo
3. **Solución Propuesta**: Enfoque técnico de alto nivel
4. **Arquitectura y Desglose de Componentes**: Componentes nuevos/modificados/externos
5. **Flujo de Datos**: Origen, transformaciones, destino
6. **Contrato(s) de API**: Endpoints con request/response
7. **Cambios en el Modelo de Datos**: Tablas, campos, índices, migraciones
8. **Algoritmos / Lógica Clave**: Lógica de negocio no obvia
9. **Consideraciones de Seguridad**: Authn, authz, datos sensibles
10. **Estrategia de Manejo de Errores**: Tipos de errores, formato, logging
11. **Alternativas Consideradas**: Opciones evaluadas y rechazadas
12. **Preguntas Abiertas y Riesgos**: Preguntas sin resolver, riesgos potenciales
13. **Consideraciones para Estimación**: Factores de complejidad, incertidumbres
14. **Estrategia de Pruebas**: Tipos de pruebas, cobertura, ambientes

#### Mapeo: Solution Vision → Tech Design

**Información Disponible en Solution Vision**:
- Contexto de Negocio (Problema, Visión de la Solución)
- Alineación Estratégica (Metas → Mecanismos Técnicos)
- Impacto en el Usuario
- Alcance del MVP (Must Have, Nice to Have, Out of Scope)
- Métricas de Éxito (Técnicas)
- Restricciones y Supuestos
- Componentes de Alto Nivel (diagrama conceptual)

**Estrategia de Llenado por Sección**:

| Sección Tech Design | Fuente en Solution Vision | Método de Llenado |
|---------------------|---------------------------|-------------------|
| Visión General | "Visión de la Solución" | Extracción directa + reformulación técnica |
| Solución Propuesta | "Mecanismos Técnicos" + "Componentes de Alto Nivel" | Extracción + expansión |
| Arquitectura | "Componentes de Alto Nivel" | Expansión detallada (inferir responsabilidades) |
| Flujo de Datos | "Componentes" + "Impacto en Usuario" | Inferencia (trazar user actions → data flow) |
| Contratos de API | "Impacto en Usuario" + "Métricas Técnicas" | Inferencia (user actions → endpoints) |
| Modelo de Datos | "Componentes" + "Alcance MVP" | Inferencia (features → entities) |
| Algoritmos | "Restricciones" + "Métricas Técnicas" | Clarificación (marcar NEEDS CLARIFICATION si complejo) |
| Seguridad | "Restricciones de Negocio/Técnicas" | Extracción + defaults (authn requerida, PII encriptada) |
| Manejo de Errores | N/A | Defaults (códigos HTTP estándar) |
| Alternativas | "Alcance" (Out of Scope puede ser alternativa) | Inferencia + "hacer nada" como baseline |
| Preguntas/Riesgos | "Restricciones" + "Supuestos" | Extracción (supuestos → preguntas, restricciones → riesgos) |
| Estimación | "Métricas Técnicas" + "Restricciones" | Extracción directa |
| Estrategia de Pruebas | "Métricas de Éxito" | Inferencia (métricas → tipos de pruebas necesarias) |

#### Decision: Manejo de Información Faltante

**Chosen**: Jidoka Selectivo - Parar solo si información es crítica

**Criterios de Criticidad**:
- **Crítico** (STOP): Vision no existe, template no existe, información que bloquea secciones core (Visión General, Solución Propuesta, Arquitectura)
- **No crítico** (CONTINUE con defaults): Detalles de seguridad, códigos de error específicos, algoritmos complejos

**Approach para No Crítico**:
1. Usar defaults razonables basados en industria
2. Marcar con `[NEEDS CLARIFICATION: ...]` si hay ambigüedad
3. Documentar supuestos en sección "Preguntas Abiertas"

**Rationale**:
- Balance entre robustez (no generar basura) y usabilidad (no bloquear por detalles)
- Permite iteración (generar draft, refinar después)
- Consistente con principio Lean (entregar rápido, iterar)

**Alternatives Considered**:
- Parar siempre que falte info → Rechazado: demasiado restrictivo
- Continuar siempre con placeholders → Rechazado: genera documentos incompletos

---

### 4. Verificación de Gate

#### Gate Analysis: `.raise-kit/gates/gate-design.md`

**Ubicación Verificada**: ✅ Existe en `.raise-kit/gates/gate-design.md`

**Criterios del Gate** (extracto):
- [ ] Visión técnica clara y alineada con negocio
- [ ] Arquitectura de componentes definida con SRP
- [ ] Flujos de datos trazables
- [ ] Contratos de API especificados
- [ ] Modelo de datos soporta requisitos
- [ ] Seguridad considerada (authn/authz)
- [ ] Estrategia de errores definida
- [ ] Alternativas documentadas
- [ ] Riesgos identificados con mitigación
- [ ] Estrategia de testing definida

**Integración en el Comando**:
- Paso 16 (Finalize & Validate): Ejecutar `.specify/gates/raise/gate-design.md`
- Mostrar checklist del gate al usuario
- Si falla: Mostrar advertencias pero no bloquear (permitir iteración)

#### Decision: Formato de Handoff

**Chosen**: YAML frontmatter (consistente con comandos existentes)

**Estructura**:
```yaml
handoffs:
  - label: Generate Project Backlog
    agent: raise.5.backlog
    prompt: Create the project backlog from this Tech Design
    send: true
```

**Rationale**:
- Consistencia con `raise.1.discovery` y `raise.2.vision`
- Permite automatización futura (agente puede auto-ejecutar siguiente comando)
- Trazabilidad clara del flujo

**Alternatives Considered**:
- Solo mensaje al final → Rechazado: no estructurado
- Ambos (YAML + mensaje) → Rechazado: redundante

---

## Key Decisions Summary

| Decision Area | Chosen Approach | Rationale |
|---------------|-----------------|-----------|
| Estructura del comando | Seguir patrón de raise.1.discovery | Consistencia, patrón validado |
| Nivel de detalle | 15 pasos explícitos | Máxima trazabilidad con kata |
| Manejo de info faltante | Jidoka selectivo (parar solo si crítico) | Balance robustez/usabilidad |
| Llenado de template | Extracción + Inferencia + Defaults | Maximizar completitud sin bloquear |
| Formato de handoff | YAML frontmatter | Consistencia con comandos existentes |
| Referencias de paths | Usar .specify/ (no .raise-kit/) | Portabilidad cuando se inyecta |

## Implementation Implications

### Comando a Crear

**Archivo**: `.raise-kit/commands/02-projects/raise.4.tech-design.md`

**Tamaño estimado**: ~150-200 líneas (similar a raise.1.discovery que tiene 113 líneas)

**Secciones**:
1. Frontmatter YAML (5-10 líneas)
2. User Input (3 líneas)
3. Outline con 16 pasos (100-120 líneas)
   - Paso 1: Initialize Environment
   - Pasos 2-15: Los 15 pasos del kata
   - Paso 16: Finalize & Validate
4. Notas (10-15 líneas)
5. High-Signaling Guidelines (10-15 líneas)
6. AI Guidance (15-20 líneas)

### Template a Copiar

**Source**: `src/templates/tech/tech_design.md`  
**Destination**: `.raise-kit/templates/raise/tech/tech_design.md`  
**Action**: `cp src/templates/tech/tech_design.md .raise-kit/templates/raise/tech/tech_design.md`

**Prerequisito**: Crear directorio `mkdir -p .raise-kit/templates/raise/tech`

### Gate a Verificar

**Ubicación**: `.raise-kit/gates/gate-design.md`  
**Status**: ✅ Ya existe (copiado previamente desde `src/gates/gate-design.md`)  
**Action**: Solo verificar existencia, no copiar

---

## Testing Strategy

### Test Scenarios

1. **Happy Path**: 
   - Proyecto con Solution Vision completa
   - Ejecutar `/raise.4.tech-design`
   - Verificar: Tech Design generado con todas las secciones completadas

2. **Jidoka - Vision Faltante**:
   - Proyecto sin `specs/main/solution_vision.md`
   - Ejecutar `/raise.4.tech-design`
   - Verificar: Comando se detiene con mensaje "Ejecutar `/raise.2.vision` primero"

3. **Jidoka - Vision Incompleta**:
   - Proyecto con Vision vacía o con solo frontmatter
   - Ejecutar `/raise.4.tech-design`
   - Verificar: Comando continúa pero marca secciones con [NEEDS CLARIFICATION]

4. **Gate Validation**:
   - Ejecutar comando completo
   - Verificar: Gate se ejecuta y muestra checklist
   - Verificar: Handoff a `/raise.5.backlog` se muestra

### Test Project Setup

```bash
# Crear proyecto test
mkdir -p /tmp/test-tech-design
cd /tmp/test-tech-design

# Inicializar con raise-kit
# (simular inyección: copiar .raise-kit → .specify)

# Crear Solution Vision de prueba
mkdir -p specs/main
# ... copiar vision de ejemplo

# Ejecutar comando
/raise.4.tech-design

# Verificar output
ls -la specs/main/tech_design.md
cat specs/main/tech_design.md | grep -c "##"  # Debe ser 14 (secciones)
```

---

## Next Steps

1. ✅ **Research Complete**: Este documento
2. **Phase 1**: Usar este research para crear el comando en `plan.md`
3. **Phase 2**: Generar tasks con `/speckit.4.tasks`
4. **Implementation**: Ejecutar tasks
5. **Testing**: Validar con test scenarios documentados arriba

---

**Research Status**: ✅ Complete - All NEEDS CLARIFICATION resolved
