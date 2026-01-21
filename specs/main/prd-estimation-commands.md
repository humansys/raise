---
document_id: "PRD-RAISE-002"
title: "Documento de Requisitos del Proyecto (PRD): Comandos para Proceso de Estimación"
project_name: "estimation-commands"
client: "RaiSE Framework"
version: "1.0"
date: "2026-01-20"
author: "Orquestador"
related_docs:
  - "L1-04-Estimar-Requerimiento.md"
  - "flujo-03-tech-design.md"
  - "flujo-05-backlog-creation.md"
status: "Draft"
---

# Documento de Requisitos del Proyecto (PRD): Comandos para Proceso de Estimación

## 1. Introducción y Metas del Proyecto

### 1.1. Resumen del Proyecto

Crear los 4 comandos faltantes para completar el flujo de estimación definido en el kata L1-04-Estimar-Requerimiento. Estos comandos permitirán ejecutar el proceso completo desde PRD hasta Statement of Work (SoW) de manera guiada y consistente.

### 1.2. Problema de Negocio / Oportunidad

**Usuarios Afectados:** Arquitectos de Preventa, Líderes Técnicos, Analistas de Estimaciones que usan el framework RaiSE.

**Impacto Actual:**
- El kata L1-04 define 8 pasos pero solo existen 2 comandos (`raise.1.discovery`, `raise.2.vision`)
- Los pasos 4-7 del kata no tienen comandos que los automaticen
- El proceso de estimación requiere trabajo manual sin guía estructurada
- Inconsistencia entre proyectos por falta de estandarización

**Urgencia:** Alta - El flujo de estimación es crítico para preventa y no está completo.

### 1.3. Metas y Objetivos del Proyecto

*   **Meta 1:** Completar el flujo de estimación del kata L1-04
    *   *Objetivo Específico:* Crear los 4 comandos faltantes que cubren los pasos 4-7 del kata

*   **Meta 2:** Estandarizar la generación de artefactos de estimación
    *   *Objetivo Específico:* Cada comando produce un artefacto específico usando templates existentes

*   **Meta 3:** Mantener trazabilidad entre artefactos
    *   *Objetivo Específico:* Cada comando referencia el artefacto anterior como input

### 1.4. Métricas de Éxito

*   **Métrica 1:** Cobertura del kata - **Objetivo:** 100% de los pasos del kata L1-04 tienen comando asociado
*   **Métrica 2:** Uso de templates - **Objetivo:** 100% de comandos usan templates existentes de `src/templates/`
*   **Métrica 3:** Consistencia de estructura - **Objetivo:** 100% de comandos siguen el patrón de `raise.1.discovery` y `raise.2.vision`

## 2. Stakeholders y Usuarios

### 2.1. Stakeholders Clave

| Rol/Nombre               | Responsabilidad/Interés Principal                              |
|--------------------------|----------------------------------------------------------------|
| Arquitecto de Preventa   | Usar comandos para generar propuestas técnicas                 |
| Líder Técnico            | Crear Tech Design y Backlog estimable                          |
| Analista de Estimaciones | Generar Estimation Roadmap y SoW                               |
| Mantenedor RaiSE         | Asegurar consistencia del framework                            |

### 2.2. Usuarios Objetivo / Personas

*   **Usuario Tipo 1: Arquitecto de Preventa**
    *   *Descripción:* Profesional que lidera el proceso de estimación para nuevos proyectos
    *   *Necesidades Clave:* Flujo guiado desde PRD hasta propuesta económica
    *   *Puntos de Dolor Actuales:* Proceso manual, inconsistente, sin plantillas estandarizadas
    *   *Beneficios Esperados:* Comandos que guían cada paso con validaciones integradas

## 3. Alcance del Proyecto

### 3.1. Dentro del Alcance (Funcionalidades Clave)

*   **Comando 1:** `raise.4.tech-design` - Genera Tech Design desde Solution Vision
*   **Comando 2:** `raise.5.backlog` - Genera Backlog estimable desde Tech Design
*   **Comando 3:** `raise.6.estimation` - Genera Estimation Roadmap desde Backlog
*   **Comando 4:** `raise.7.sow` - Genera Statement of Work desde Estimation Roadmap

### 3.2. Fuera del Alcance

*   Modificación de templates existentes en `src/templates/`
*   Creación de nuevos templates
*   Modificación de comandos existentes (`raise.1.discovery`, `raise.2.vision`)
*   Gates de validación (ya existen o se crearán en proyecto separado)
*   Integración con herramientas externas (Jira, Confluence, etc.)

### 3.3. Consideraciones Futuras (Posibles Fases Posteriores)

*   Comando de consolidación que ejecute todo el flujo de estimación
*   Validación automática entre artefactos
*   Exportación a formatos externos (PDF, DOCX)

## 4. Requisitos Funcionales

### 4.1. Resumen de Capacidades

*   **Capacidad 1: Comando raise.4.tech-design**
    *   Requisito 1.1: El comando DEBE cargar Solution Vision como input (`specs/main/solution_vision.md`)
    *   Requisito 1.2: El comando DEBE usar template `src/templates/tech/tech_design.md`
    *   Requisito 1.3: El comando DEBE producir `specs/main/tech_design.md`
    *   Requisito 1.4: El comando DEBE seguir los 15 pasos del `flujo-03-tech-design`
    *   Requisito 1.5: El comando DEBE incluir handoff a `raise.5.backlog`

*   **Capacidad 2: Comando raise.5.backlog**
    *   Requisito 2.1: El comando DEBE cargar Tech Design como input (`specs/main/tech_design.md`)
    *   Requisito 2.2: El comando DEBE usar template `src/templates/backlog/project_backlog.md`
    *   Requisito 2.3: El comando DEBE producir `specs/main/project_backlog.md`
    *   Requisito 2.4: El comando DEBE seguir los 10 pasos del `flujo-05-backlog-creation`
    *   Requisito 2.5: El comando DEBE incluir handoff a `raise.6.estimation`

*   **Capacidad 3: Comando raise.6.estimation**
    *   Requisito 3.1: El comando DEBE cargar Backlog como input (`specs/main/project_backlog.md`)
    *   Requisito 3.2: El comando DEBE usar template `src/templates/solution/estimation_roadmap.md`
    *   Requisito 3.3: El comando DEBE producir `specs/main/estimation_roadmap.md`
    *   Requisito 3.4: El comando DEBE guiar la estimación en Story Points
    *   Requisito 3.5: El comando DEBE incluir handoff a `raise.7.sow`

*   **Capacidad 4: Comando raise.7.sow**
    *   Requisito 4.1: El comando DEBE cargar Estimation Roadmap como input (`specs/main/estimation_roadmap.md`)
    *   Requisito 4.2: El comando DEBE usar template `src/templates/solution/statement_of_work.md`
    *   Requisito 4.3: El comando DEBE producir `specs/main/statement_of_work.md`
    *   Requisito 4.4: El comando DEBE consolidar información de PRD, Vision, Tech Design y Estimation
    *   Requisito 4.5: El comando DEBE ser el cierre del flujo de estimación (sin handoff)

### 4.2. Escenarios de Usuario / Flujos de Trabajo Clave

*   **Escenario 1: Flujo Completo de Estimación**
    1.  Usuario ejecuta `/raise.1.discovery` → genera PRD
    2.  Usuario ejecuta `/raise.2.vision` → genera Solution Vision
    3.  Usuario ejecuta `/raise.4.tech-design` → genera Tech Design
    4.  Usuario ejecuta `/raise.5.backlog` → genera Backlog
    5.  Usuario ejecuta `/raise.6.estimation` → genera Estimation Roadmap
    6.  Usuario ejecuta `/raise.7.sow` → genera Statement of Work
    7.  Usuario tiene paquete completo de estimación listo

### 4.3. Mapeo a Artefactos del Kata L1-04

| Paso Kata | Artefacto              | Comando          | Template                              |
|-----------|------------------------|------------------|---------------------------------------|
| 1         | PRD (insumo)           | raise.1.discovery| solution/project_requirements.md      |
| 3         | Solution Vision        | raise.2.vision   | solution/solution-vision-template.md  |
| 4         | Tech Design            | raise.4.tech-design | tech/tech_design.md                |
| 5         | Backlog                | raise.5.backlog  | backlog/project_backlog.md            |
| 6         | Estimation Roadmap     | raise.6.estimation | solution/estimation_roadmap.md      |
| 7         | Statement of Work      | raise.7.sow      | solution/statement_of_work.md         |

## 5. Requisitos No Funcionales (NFRs)

*   **Consistencia:** Cada comando DEBE seguir la estructura de `raise.1.discovery` y `raise.2.vision`
*   **Trazabilidad:** Cada comando DEBE referenciar el kata/flujo correspondiente
*   **Idioma:** Instrucciones en inglés, contenido generado en español
*   **Jidoka:** Cada comando DEBE incluir puntos de parada si falta información crítica
*   **Handoffs:** Cada comando (excepto el último) DEBE incluir handoff al siguiente

## 6. Requisitos de Datos

*   **Entidades de Datos Principales:** Archivos Markdown con frontmatter YAML
*   **Fuentes de Datos:**
    - Templates en `src/templates/`
    - Katas/flujos en `src/katas-v2.1/flujo/`
*   **Destinos de Datos:** `specs/main/` para artefactos generados

## 7. Requisitos de Integración

*   **Sistema: Comandos existentes**
    *   *Propósito:* Los nuevos comandos se integran con `raise.1.discovery` y `raise.2.vision`
    *   *Método:* Handoffs en frontmatter YAML
    *   *Frecuencia:* Secuencial en flujo de estimación

## 8. Supuestos

*   **Supuesto 1:** Los templates en `src/templates/` están completos y listos para usar
*   **Supuesto 2:** Los flujos en `src/katas-v2.1/flujo/` definen los pasos correctamente
*   **Supuesto 3:** La estructura de comandos existente (`raise.1.discovery`, `raise.2.vision`) es el patrón a seguir
*   **Supuesto 4:** Los comandos se ubicarán en `.claude/commands/02-projects/`

## 9. Restricciones

*   **Restricción 1:** Los comandos DEBEN usar los templates existentes sin modificarlos
*   **Restricción 2:** Los comandos DEBEN seguir el patrón de estructura de los existentes
*   **Restricción 3:** Los comandos DEBEN ubicarse en `.claude/commands/02-projects/`

## 10. Preguntas Abiertas y Riesgos Identificados

*   **Preguntas Abiertas:**
    *   Ninguna - El análisis previo clarificó los gaps

*   **Riesgos Identificados:**
    *   [Riesgo 1: Templates incompletos] - **Mitigación:** Verificar cada template antes de crear el comando
    *   [Riesgo 2: Flujos desactualizados] - **Mitigación:** Validar flujos contra kata L1-04
    *   [Riesgo 3: Inconsistencia con comandos existentes] - **Mitigación:** Usar `raise.1.discovery` como referencia de estructura

## 11. Glosario Específico del Proyecto

| Término          | Definición                                                    |
|------------------|---------------------------------------------------------------|
| Kata             | Ejercicio estructurado que define un proceso paso a paso      |
| Flujo            | Tipo de kata que describe el flujo de trabajo entre artefactos|
| Handoff          | Referencia en YAML que indica el siguiente comando a ejecutar |
| Estimation Roadmap | Documento que proyecta esfuerzo y cronograma                |
| SoW              | Statement of Work - Documento contractual de alcance y costo  |

## 12. Historial del Documento

| Versión | Fecha      | Autor(es)   | Cambios Realizados                                  |
|---------|------------|-------------|-----------------------------------------------------|
| 1.0     | 2026-01-20 | Orquestador | Versión inicial basada en análisis de gaps          |
