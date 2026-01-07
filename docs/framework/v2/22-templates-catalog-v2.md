# RaiSE Templates Catalog
## Catálogo de Plantillas Disponibles

**Versión:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Catálogo completo de templates disponibles en RaiSE.

> **Nota de versión 2.0:** Esta versión añade templates para Guardrails, Validation Gates, y Observable Workflow. Terminología actualizada según ontología v2.0.

---

## Resumen de Templates

| Categoría | Templates | Descripción | Nuevo v2.0 |
|-----------|-----------|-------------|------------|
| Backlog | 5 | Artefactos de gestión de requerimientos | — |
| Solution | 7 | Documentos de visión y estrategia | — |
| Tech | 3 | Diseño técnico y especificaciones | — |
| SAR | 8 | Software Architecture Review | — |
| **Guardrails** | 4 | Templates para barreras de protección | ✅ |
| **Gates** | 3 | Templates para Validation Gates | ✅ |
| **Observable** | 2 | Templates para auditoría y trazas | ✅ |
| Agent Rules | 5 | Templates para reglas de agentes | Renombrado |

---

## Templates Core

### Backlog Templates

Ubicación: `src/templates/backlog/`

#### user_story.md
**Propósito:** Definir historias de usuario con criterios de aceptación BDD.

**Estructura:**
- ID JIRA y enlace a Epic padre
- Formato "Como/Quiero/Para"
- Criterios de aceptación en Gherkin
- Detalles técnicos (componentes, APIs, modelo de datos)
- Consideraciones UI/UX
- Pruebas requeridas
- Dependencias y estimación

**Variables principales:**
| Variable | Descripción |
|----------|-------------|
| `{{jira_id}}` | Identificador JIRA |
| `{{user_type}}` | Tipo de usuario |
| `{{action}}` | Acción deseada |
| `{{benefit}}` | Beneficio esperado |

---

#### capability.md
**Propósito:** Definir capacidades de alto nivel del sistema.

**Uso:** Agrupar features relacionadas bajo una capacidad de negocio.

---

#### epic.md
**Propósito:** Definir épicas que agrupan user stories relacionadas.

**Uso:** Planificación de releases y sprints.

---

#### bug.md
**Propósito:** Documentar bugs con información reproducible.

**Uso:** Reporte estructurado de defectos.

---

#### project_backlog.md
**Propósito:** Vista consolidada del backlog del proyecto.

**Uso:** Gestión y priorización de trabajo pendiente.

---

### Solution Templates

Ubicación: `src/templates/solution/`

#### project_requirements.md (PRD)
**Propósito:** Documento de Requisitos del Proyecto completo.

**Estructura:**
- Introducción y metas
- Stakeholders y usuarios
- Alcance (in/out)
- Requisitos funcionales y no funcionales
- Requisitos de datos e integración
- Supuestos y restricciones
- Preguntas abiertas y riesgos

**Tamaño:** ~14KB (template más extenso)

**Gate asociado:** Gate-Discovery

---

#### solution-vision-template.md
**Propósito:** Visión de alto nivel de la solución.

**Versiones:** ES e EN

**Estructura:**
- Problem Statement
- Business Goals
- Stakeholders
- MVP Scope
- Success Criteria

**Gate asociado:** Gate-Vision

---

#### feature-prioritization-template.md
**Propósito:** Matriz de priorización de features.

**Versiones:** ES e EN

**Estructura:**
- Lista de features
- Scoring (valor, urgencia, complejidad)
- Selección de MVP

---

#### estimation_roadmap.md
**Propósito:** Roadmap con estimaciones de esfuerzo.

**Estructura:**
- Fases del proyecto
- Estimaciones por épica/feature
- Dependencias y riesgos

---

#### statement_of_work.md (SoW)
**Propósito:** Declaración de trabajo contractual.

**Estructura:**
- Alcance detallado
- Entregables
- Cronograma
- Costos

---

### Tech Templates

Ubicación: `src/templates/tech/`

#### tech_design.md
**Propósito:** Diseño técnico detallado para features.

**Estructura:**
- Arquitectura de componentes
- Flujo de datos
- Contratos de API
- Modelo de datos
- Algoritmos clave
- Consideraciones de seguridad
- Alternativas consideradas

**Gate asociado:** Gate-Design

---

#### api_spec.md
**Propósito:** Especificación de endpoints de API.

**Estructura:**
- Endpoint y método
- Request/Response schemas
- Códigos de error
- Ejemplos

---

#### component_spec.md
**Propósito:** Especificación de componentes reutilizables.

**Estructura:**
- Propósito y responsabilidades
- Interface/contrato
- Dependencias
- Comportamiento esperado

---

### SAR Templates (Software Architecture Review)

Ubicación: `src/templates/sar/`

Templates para análisis de arquitectura de sistemas existentes.

| Template | Propósito |
|----------|-----------|
| `resumen_repositorio.md` | Overview del repo analizado |
| `descripcion_general_arquitectura.md` | Arquitectura de alto nivel |
| `informe_analisis_arquitectura_limpia.md` | Evaluación Clean Architecture |
| `informe_analisis_codigo_limpio.md` | Evaluación Clean Code |
| `informe_desglose_componentes.md` | Análisis de componentes |
| `informe_mapa_dependencias.md` | Mapa de dependencias |
| `recomendaciones_refactorizacion.md` | Propuestas de mejora |
| `README.md` | Guía de uso del análisis SAR |

---

## Templates v2.0 [NUEVOS]

### Guardrails Templates

Ubicación: `src/templates/guardrails/`

#### guardrail-code.mdc
**Propósito:** Template para guardrails de calidad de código.

**Estructura (MDC format):**
```markdown
---
id: "GR-XXX"
scope: code
severity: error | warning | info
tags: ["quality", "security", "performance"]
---

# {{guardrail_name}}

## Descripción
{{descripcion_del_guardrail}}

## Regla
{{regla_en_lenguaje_natural}}

## Ejemplos

### ✅ Correcto
```{{language}}
{{ejemplo_correcto}}
```

### ❌ Incorrecto
```{{language}}
{{ejemplo_incorrecto}}
```

## Enforcement
- [ ] Lint rule: {{linter_rule_id}}
- [ ] CI check: {{ci_check_name}}
- [ ] MCP tool: check_guardrail("GR-XXX")
```

**Variables principales:**
| Variable | Descripción |
|----------|-------------|
| `{{guardrail_name}}` | Nombre descriptivo |
| `{{scope}}` | code, architecture, process |
| `{{severity}}` | error, warning, info |

---

#### guardrail-architecture.mdc
**Propósito:** Template para guardrails de arquitectura.

**Casos de uso:**
- Restricciones de dependencias entre capas
- Patrones requeridos o prohibidos
- Límites de componentes

---

#### guardrail-process.mdc
**Propósito:** Template para guardrails de proceso.

**Casos de uso:**
- Requerimientos de documentación
- Flujos obligatorios (PR review, tests)
- Convenciones de naming

---

#### guardrails-index.json
**Propósito:** Índice JSON de todos los guardrails activos.

**Estructura:**
```json
{
  "version": "2.0.0",
  "guardrails": [
    {
      "id": "GR-001",
      "name": "Max File Length",
      "scope": "code",
      "severity": "warning",
      "file": "guardrails/gr-001-max-file-length.mdc"
    }
  ]
}
```

**Uso MCP:** Servido como `raise://guardrails`

---

### Validation Gates Templates

Ubicación: `src/templates/gates/`

#### gate-definition.md
**Propósito:** Template para definir un Validation Gate.

**Estructura:**
```markdown
# Gate-{{gate_name}}

## Fase
{{phase_name}} (Discovery | Vision | Design | Planning | Implementation | Deployment)

## Criterios de Paso

### Obligatorios
- [ ] {{criterio_1}}
- [ ] {{criterio_2}}

### Opcionales
- [ ] {{criterio_opcional}}

## Artefactos de Entrada
| Artefacto | Template | Obligatorio |
|-----------|----------|-------------|
| {{artefacto}} | {{template_link}} | Sí/No |

## Artefactos de Salida
| Artefacto | Template | Generado por |
|-----------|----------|--------------|
| {{artefacto}} | {{template_link}} | Humano/Agente |

## Escalation Triggers
Escalar a Orquestador si:
- {{trigger_1}}
- {{trigger_2}}

## Validación MCP
```json
{
  "tool": "validate_gate",
  "parameters": {
    "gate": "Gate-{{gate_name}}",
    "artifact": "{{artifact_path}}"
  }
}
```
```

---

#### gate-checklist.md
**Propósito:** Checklist ejecutable para validar un gate.

**Uso:** Generado por `raise gate check Gate-{name}`

---

#### escalation-protocol.md
**Propósito:** Template para documentar protocolo de escalación.

**Estructura:**
- Triggers de escalación por gate
- Canales de comunicación
- SLA de respuesta
- Formato de escalación

---

### Observable Workflow Templates

Ubicación: `src/templates/observable/`

#### audit-report.md
**Propósito:** Template para reportes de auditoría de sesión.

**Estructura:**
```markdown
# Audit Report: {{session_id}}

## Resumen Ejecutivo
- **Fecha:** {{date}}
- **Duración:** {{duration}}
- **Gates pasados:** {{gates_passed}}/{{gates_total}}
- **Escalaciones:** {{escalations}}

## Métricas

| Métrica | Valor | Benchmark |
|---------|-------|-----------|
| Re-prompting Rate | {{rate}} | <3 |
| Token Usage | {{tokens}} | — |
| Escalation Rate | {{esc_rate}} | 10-15% |

## Timeline de Eventos

| Timestamp | Acción | Gate | Resultado |
|-----------|--------|------|-----------|
{{events_table}}

## Guardrails Activados

| Guardrail | Ocurrencias | Severidad |
|-----------|-------------|-----------|
{{guardrails_table}}

## Recomendaciones
{{recommendations}}
```

**Generado por:** `raise audit --session {{session_id}} --format md`

---

#### metrics-dashboard.md
**Propósito:** Template para dashboard de métricas agregadas.

**Uso:** Reportes semanales/mensuales

---

## Agent Rules Templates

Ubicación: `src/templates/agent-rules/`

> **Nota v2.0:** Renombrado de "cursor-rules" a "agent-rules" para reflejar soporte multi-agente.

| Template | Propósito | Formato |
|----------|-----------|---------|
| `claude.md.template` | Reglas para Claude | Markdown |
| `cursorrules.template` | Reglas para Cursor | .cursorrules |
| `agents.md.template` | Reglas genéricas | AGENTS.md |
| `windsurf.yaml.template` | Reglas para Windsurf | YAML |
| `mcp-context.json.template` | Contexto MCP | JSON |

---

## Uso de Templates

### Proceso de Uso

1. **Identificar** el tipo de documento necesario
2. **Copiar** template a ubicación del proyecto
3. **Renombrar** con convención: `{JIRA-ID}-{tipo}-{nombre}.md`
4. **Completar** placeholders (`{{variable}}`)
5. **Validar** contra Validation Gate correspondiente
6. **Registrar** en Observable Workflow si aplica

### Convención de Ubicación

```
proyecto/
├── .raise/
│   ├── memory/
│   │   ├── constitution.md
│   │   └── guardrails.json
│   ├── traces/
│   │   └── 2025-12-28.jsonl
│   └── raise.yaml
├── docs/
│   ├── capabilities/
│   │   └── CAP-001-nombre.md
│   ├── features/
│   │   └── FEAT-123-nombre/
│   │       ├── FEAT-123-TechDesign.md
│   │       └── US-456-historia.md
│   ├── gates/
│   │   └── Gate-Design-checklist.md
│   └── api/
│       └── API-spec.md
```

---

## Creación de Templates Personalizados

### Criterios para Nuevo Template

1. **Frecuencia:** ¿Se usará más de 3 veces?
2. **Estructura estable:** ¿Las secciones son predecibles?
3. **Valor de consistencia:** ¿Importa que sean uniformes?
4. **Gate asociado:** ¿Existe un Validation Gate que lo requiera?

### Estructura de un Template

```markdown
---
# Frontmatter con metadata
type: "[tipo_documento]"
version: "[versión]"
gate: "[Gate-XXX]"  # [NUEVO v2.0]
---

# Título con {{placeholder}}

## Sección 1
*[Instrucciones en itálica para el usuario]*

{{variable_placeholder}}

## Sección 2
| Campo | Valor |
|-------|-------|
| {{campo}} | {{valor}} |
```

### Registro de Nuevo Template

1. Crear archivo en categoría apropiada
2. Documentar en este catálogo
3. **Asociar con Validation Gate si aplica** [NUEVO v2.0]
4. Actualizar kata de validación
5. Comunicar al equipo

---

## Mapeo Templates → Gates → Katas

| Template | Validation Gate | Kata de Validación |
|----------|-----------------|-------------------|
| user_story.md | Gate-Backlog | L1-16-DoD-Historias-Usuario-kata |
| tech_design.md | Gate-Design | zc-kata-tech-design |
| project_requirements.md | Gate-Discovery | (pendiente) |
| solution-vision-template.md | Gate-Vision | (pendiente) |
| guardrail-code.mdc | Gate-Code | kata-guardrail-validation |
| gate-definition.md | — | kata-gate-definition |

---

## MCP Resources Mapping [NUEVO v2.0]

| Template Category | MCP Resource | Descripción |
|-------------------|--------------|-------------|
| Constitution | `raise://constitution` | Principios inmutables |
| Guardrails | `raise://guardrails` | JSON de guardrails activos |
| Gates | `raise://gates/{gate_name}` | Definición de gate |
| Specs | `raise://specs/{spec_name}` | Especificaciones del proyecto |

---

## Changelog

### v2.0.0 (2025-12-28)
- **NUEVO**: Categoría Guardrails Templates (4 templates)
- **NUEVO**: Categoría Validation Gates Templates (3 templates)
- **NUEVO**: Categoría Observable Workflow Templates (2 templates)
- **RENOMBRADO**: cursor-rules → agent-rules
- **ACTUALIZADO**: Mapeo Templates → Gates → Katas
- **NUEVO**: MCP Resources Mapping
- **ACTUALIZADO**: Convención de ubicación con .raise/

### v1.0.0 (2025-12-27)
- Release inicial

---

*Este catálogo se actualiza con cada nuevo template añadido al sistema. Referencias: [20-glossary-v2.md](./20-glossary-v2.md), [21-methodology-v2.md](./21-methodology-v2.md)*
