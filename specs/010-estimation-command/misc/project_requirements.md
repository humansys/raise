---
document_id: "PRD-RAISE-001"
title: "Documento de Requisitos del Proyecto (PRD): Script de Transformación de Comandos"
project_name: "transform-commands-script"
client: "RaiSE Framework"
version: "1.0"
date: "2026-01-20"
author: "Orquestador"
related_docs:
  - "COMMAND_STRUCTURE_PROPOSAL.md"
  - "WORKFLOW_MAP.md"
status: "Draft"
---

# Documento de Requisitos del Proyecto (PRD): Script de Transformación de Comandos

## 1. Introducción y Metas del Proyecto

### 1.1. Resumen del Proyecto
Script bash que automatiza la transformación de archivos de comandos desde la estructura plana de `.claude/commands` hacia la nueva estructura organizada de `.specify-raise/commands`, aplicando el renombramiento de archivos y actualizando las referencias internas en el contenido.

### 1.2. Problema de Negocio / Oportunidad

**Usuarios Afectados:** Desarrolladores y mantenedores del framework RaiSE que necesitan migrar comandos entre estructuras de carpetas.

**Impacto Actual:**
- Proceso manual propenso a errores
- Inconsistencia entre nombres de archivos y referencias internas
- Tiempo perdido en transformaciones repetitivas

**Urgencia:** Media - Se requiere para estandarizar la distribución de comandos en el template.

### 1.3. Metas y Objetivos del Proyecto

*   **Meta 1:** Automatizar la transformación de estructura de comandos
    *   *Objetivo Específico:* Ejecutar un solo comando para transformar todos los archivos
*   **Meta 2:** Garantizar consistencia entre nombres de archivo y contenido
    *   *Objetivo Específico:* Actualizar todas las referencias internas automáticamente
*   **Meta 3:** Mantener trazabilidad del mapeo de transformación
    *   *Objetivo Específico:* Documentar el mapeo de nombres origen → destino

### 1.4. Métricas de Éxito

*   **Métrica 1:** Tasa de transformación exitosa - **Objetivo:** 100% de archivos transformados sin errores
*   **Métrica 2:** Consistencia de referencias - **Objetivo:** 0 referencias huérfanas post-transformación
*   **Métrica 3:** Tiempo de ejecución - **Objetivo:** < 5 segundos para el conjunto completo

## 2. Stakeholders y Usuarios

### 2.1. Stakeholders Clave

| Rol/Nombre        | Responsabilidad/Interés Principal                         |
|-------------------|-----------------------------------------------------------|
| Orquestador       | Usar el script para migrar comandos en proyectos          |
| Mantenedor RaiSE  | Mantener consistencia del template de comandos            |

### 2.2. Usuarios Objetivo / Personas

*   **Usuario Tipo 1: Desarrollador RaiSE**
    *   *Descripción:* Desarrollador que trabaja con el framework RaiSE
    *   *Necesidades Clave:* Migrar comandos de estructura antigua a nueva
    *   *Puntos de Dolor Actuales:* Proceso manual tedioso y propenso a errores
    *   *Beneficios Esperados:* Automatización completa con un solo comando

## 3. Alcance del Proyecto

### 3.1. Dentro del Alcance (Funcionalidades Clave)

*   Lectura de archivos `.md` desde carpeta origen
*   Renombramiento de archivos según mapeo definido
*   Creación de subcarpetas destino (01-onboarding, 02-projects, 03-feature)
*   Actualización de referencias internas (handoffs/agent)
*   Copia de archivos transformados a destino

### 3.2. Fuera del Alcance

*   Transformación inversa (destino → origen)
*   Validación semántica del contenido de comandos
*   Integración con sistemas de CI/CD
*   Interfaz gráfica

### 3.3. Consideraciones Futuras (Posibles Fases Posteriores)

*   Script de validación post-transformación
*   Modo dry-run para previsualizar cambios
*   Soporte para transformaciones personalizadas vía archivo de configuración

## 4. Requisitos Funcionales

### 4.1. Resumen de Capacidades

*   **Capacidad: Mapeo de Nombres de Archivos**
    *   Requisito 1.1: El script DEBE transformar los nombres de archivo según el mapeo definido:
        - `speckit.specify.md` → `03-feature/speckit.1.specify.md`
        - `speckit.clarify.md` → `03-feature/speckit.2.clarify.md`
        - `speckit.plan.md` → `03-feature/speckit.3.plan.md`
        - `speckit.tasks.md` → `03-feature/speckit.4.tasks.md`
        - `speckit.analyze.md` → `03-feature/speckit.5.analyze.md`
        - `speckit.implement.md` → `03-feature/speckit.6.implement.md`
        - `speckit.checklist.md` → `03-feature/speckit.util.checklist.md`
        - `speckit.taskstoissues.md` → `03-feature/speckit.util.issues.md`
        - `speckit.constitution.md` → `01-onboarding/speckit.2.constitution.md`

*   **Capacidad: Actualización de Referencias Internas**
    *   Requisito 2.1: El script DEBE actualizar las referencias en el frontmatter YAML (campo `agent:`) según el mapeo:
        - `speckit.specify` → `speckit.1.specify`
        - `speckit.clarify` → `speckit.2.clarify`
        - `speckit.plan` → `speckit.3.plan`
        - `speckit.tasks` → `speckit.4.tasks`
        - `speckit.analyze` → `speckit.5.analyze`
        - `speckit.implement` → `speckit.6.implement`
        - `speckit.checklist` → `speckit.util.checklist`
        - `speckit.taskstoissues` → `speckit.util.issues`
        - `speckit.constitution` → `speckit.2.constitution`

*   **Capacidad: Gestión de Estructura de Carpetas**
    *   Requisito 3.1: El script DEBE crear las subcarpetas destino si no existen
    *   Requisito 3.2: El script DEBE preservar los archivos existentes en destino (no sobrescribir sin confirmación)

### 4.2. Escenarios de Usuario / Flujos de Trabajo Clave

*   **Escenario 1: Transformación Completa**
    1.  Usuario ejecuta el script desde la raíz del repositorio template
    2.  Script lee todos los archivos `.md` de la carpeta origen
    3.  Script aplica el mapeo de nombres y referencias
    4.  Script crea las subcarpetas necesarias en destino
    5.  Script escribe los archivos transformados
    6.  Script reporta el resultado (archivos procesados, errores si los hay)

## 5. Requisitos No Funcionales (NFRs)

*   **Rendimiento:** Tiempo de ejecución < 5 segundos para 10 archivos
*   **Compatibilidad:** Compatible con bash 4.0+ en entornos Unix/Linux/Git Bash (Windows)
*   **Mantenibilidad:** Mapeos definidos como variables al inicio del script para fácil modificación
*   **Usabilidad:** Mensajes de salida claros indicando progreso y resultado

## 6. Requisitos de Datos

*   **Entidades de Datos Principales:** Archivos Markdown (.md) con frontmatter YAML
*   **Fuentes de Datos:** Carpeta origen `template/.claude/commands/`
*   **Destinos de Datos:** Carpeta destino `.specify-raise/commands/` con subcarpetas

## 7. Requisitos de Integración

*   **Sistema: Git Bash (Windows)**
    *   *Propósito de la Integración:* Ejecución del script en entorno Windows
    *   *Método de Integración:* Script bash ejecutable
    *   *Frecuencia:* Bajo demanda

## 8. Supuestos

*   **Supuesto Técnico 1:** Los archivos de origen siguen la convención de nombres `speckit.*.md`
*   **Supuesto Técnico 2:** El frontmatter YAML usa el campo `agent:` para referencias a otros comandos
*   **Supuesto Técnico 3:** El entorno de ejecución tiene bash 4.0+ disponible (o Git Bash en Windows)

## 9. Restricciones

*   **Restricción Técnica 1:** El script debe ser un único archivo `.sh` sin dependencias externas
*   **Restricción de Ubicación:** El script debe ubicarse en `template/.specify/scripts/bash/raise/`

## 10. Preguntas Abiertas y Riesgos Identificados

*   **Riesgos Identificados:**
    *   [Riesgo 1 (Técnico): Archivos con formato inesperado] - **Mitigación:** Validar existencia de archivos antes de procesar
    *   [Riesgo 2 (Datos): Pérdida de archivos destino existentes] - **Mitigación:** No sobrescribir sin confirmación o usar flag --force

## 11. Glosario Específico del Proyecto

| Término     | Definición                                               |
|-------------|----------------------------------------------------------|
| Handoff     | Referencia en YAML que indica el siguiente comando a ejecutar |
| Frontmatter | Sección YAML al inicio del archivo Markdown delimitada por `---` |

## 12. Historial del Documento

| Versión | Fecha      | Autor(es)   | Cambios Realizados                                  |
|---------|------------|-------------|-----------------------------------------------------|
| 1.0     | 2026-01-20 | Orquestador | Versión inicial basada en análisis de estructuras   |
