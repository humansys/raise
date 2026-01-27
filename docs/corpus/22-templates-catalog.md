# RaiSE Templates Catalog
## Catálogo de Plantillas Disponibles

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Catálogo completo de templates disponibles en RaiSE.

---

## Resumen de Templates

| Categoría | Templates | Descripción |
|-----------|-----------|-------------|
| Backlog | 5 | Artefactos de gestión de requerimientos |
| Solution | 7 | Documentos de visión y estrategia |
| Tech | 3 | Diseño técnico y especificaciones |
| SAR | 8 | Software Architecture Review |
| Cursor Rules | 5 | Templates para reglas de agentes |

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

### Cursor Rules Templates

Ubicación: `src/templates/cursor-rules/`

Templates para crear reglas de comportamiento de agentes.

| Template | Propósito |
|----------|-----------|
| `core-rules-template.yaml` | Estructura base de reglas |
| Otros 4 templates | Reglas específicas por contexto |

---

## Uso de Templates

### Proceso de Uso

1. **Identificar** el tipo de documento necesario
2. **Copiar** template a ubicación del proyecto
3. **Renombrar** con convención: `{JIRA-ID}-{tipo}-{nombre}.md`
4. **Completar** placeholders (`{{variable}}`)
5. **Validar** contra kata correspondiente

### Convención de Ubicación

```
proyecto/
├── docs/
│   ├── capabilities/
│   │   └── CAP-001-nombre.md
│   ├── features/
│   │   └── FEAT-123-nombre/
│   │       ├── FEAT-123-TechDesign.md
│   │       └── US-456-historia.md
│   └── api/
│       └── API-spec.md
```

---

## Creación de Templates Personalizados

### Criterios para Nuevo Template

1. **Frecuencia:** ¿Se usará más de 3 veces?
2. **Estructura estable:** ¿Las secciones son predecibles?
3. **Valor de consistencia:** ¿Importa que sean uniformes?

### Estructura de un Template

```markdown
---
# Frontmatter con metadata
type: "[tipo_documento]"
version: "[versión]"
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
3. Actualizar kata de validación si aplica
4. Comunicar al equipo

---

## Mapeo Templates → Katas

| Template | Kata de Validación |
|----------|-------------------|
| user_story.md | L1-16-DoD-Historias-Usuario-kata |
| tech_design.md | zc-kata-tech-design |
| project_requirements.md | (pendiente) |

---

*Este catálogo se actualiza con cada nuevo template añadido al sistema.*
