---
task_id: TASK-RUL-001
title: "Kata: Unificación de Reglas Cursor en un Repositorio Maestro"
author: "RAISE Rules Engineer"
status: "Proposed"
created_date: "2024-08-01"
version: "1.1"
---

# Kata: Unificación de Reglas Cursor en un Repositorio Maestro (`raise-jf-ai-common`)

## 1. Objetivo

Este documento detalla el plan paso a paso para consolidar los conjuntos de reglas Cursor de los repositorios `raise-jf-backend-files`, `raise-jf-backend-orders`, `raise-jf-backend-product` y `raise-jf-backend-profile` en un único conjunto maestro dentro del repositorio `raise-jf-ai-common`.

El objetivo es establecer una **única fuente de verdad** (Single Source of Truth) para las reglas, eliminar la duplicación, resolver conflictos y facilitar el mantenimiento y la consistencia en todos los proyectos.

## 2. Contexto y Análisis Previo

Un análisis previo de los cuatro repositorios de microservicios reveló una base de reglas comunes muy sólida pero con divergencias clave:

*   **Conflictos de numeración**: Múltiples reglas con el mismo ID pero diferente propósito (ej. `105`, `212`, `227`).
*   **Reglas evolucionadas**: Patrones avanzados presentes en un repositorio (principalmente `orders`) pero ausentes en otros.
*   **Reglas específicas de dominio**: Reglas que solo aplican a un microservicio (ej. `103-gcs-standards` en `files`).

Este plan abordará sistemáticamente estos puntos para crear un sistema de reglas robusto y centralizado.

## 3. Protocolo de Ejecución (Según L0-03)

La ejecución de esta Kata se regirá estrictamente por el `L0-03-kata-execution-protocol.md`.

*   **Fase 1 (Planificación y Aprobación)**: El Agente IA (yo) analizará el "Plan Maestro de la Kata" (sección 4 de este documento) y generará un **"Plan de Implementación y Tracking"** detallado en formato de checklist. Este plan será presentado al Orquestador Humano para su aprobación explícita antes de iniciar cualquier acción. Dicho plan se registrará en la sección "Execution Tracking & Checklist" de este documento.
*   **Fase 2 (Ejecución Autónoma Supervisada)**: Una vez aprobado el plan, procederé a ejecutar las tareas de la checklist de forma autónoma, actualizando el estado de cada una. Pausaré y escalaré al Orquestador Humano solo si se cumplen las condiciones definidas en el protocolo (decisión estratégica o error no resuelto).
*   **Fase 3 (Post-Ejecución y Cierre)**: Al completar todas las tareas, notificaré para una revisión final y cierre.

## 4. Plan Maestro de la Kata (Kata-Target Body)

### Fase A: Preparación del Repositorio Maestro (`raise-jf-ai-common`)

El objetivo de esta fase es preparar la estructura del repositorio `raise-jf-ai-common` para alojar el conjunto de reglas maestro.

*   **Paso A.1: Crear Estructura de Directorios**
    *   **Objetivo**: Establecer la ubicación canónica para las reglas maestras.
    *   **Acción Propuesta**: Crear la estructura de directorios `.cursor/rules/` dentro de `raise-jf-ai-common`.
    *   **Entregable**: El directorio `.cursor/rules/` existe en el repositorio.

*   **Paso A.2: Crear el Índice Maestro de Reglas**
    *   **Objetivo**: Crear el documento de gobernanza central para todas las reglas.
    *   **Acción Propuesta**: Crear el archivo `raise-jf-ai-common/.cursor/rules/master-rules-index.md`. Este documento contendrá una tabla con `ID`, `Nombre de Regla`, `Descripción`, `Categoría` y `Notas de Migración` para resolver todos los conflictos de numeración.
    *   **Entregable**: Un archivo `master-rules-index.md` con la estructura y el contenido inicial basado en el análisis previo.

### Fase B: Migración y Armonización de Reglas

En esta fase, migraremos las reglas de los repositorios satélite al repositorio maestro, seleccionando la "mejor versión" y resolviendo conflictos.

*   **Paso B.1: Migrar Reglas del Núcleo Común**
    *   **Objetivo**: Consolidar todas las reglas comunes en el repositorio maestro.
    *   **Acción Propuesta**: Para cada regla común (ej. `001`, `210`), identificar la versión más completa, copiarla a `raise-jf-ai-common/.cursor/rules/`, y generalizar su `frontmatter`.
    *   **Entregable**: Archivos `.mdc` para todas las reglas del núcleo común en el repositorio maestro.

*   **Paso B.2: Promover y Migrar Reglas de Patrones**
    *   **Objetivo**: Integrar reglas de alto valor y patrones opcionales en el conjunto maestro.
    *   **Acción Propuesta**: Identificar, copiar y renombrar (según el índice maestro) las reglas de patrones avanzados (ej. `214-command-orchestration`) y patrones opcionales (ej. `228-cron-jobs`).
    *   **Entregable**: Archivos `.mdc` para todas las reglas de patrones en el repositorio maestro.

### Fase C: Refactorización de los Repositorios Satélite

Esta fase se debe realizar para cada uno de los cuatro repositorios (`files`, `orders`, `product`, `profile`).

*   **Paso C.1: Eliminar Reglas Heredadas**
    *   **Objetivo**: Eliminar la duplicación y la fuente de verdad antigua en los repositorios satélite.
    *   **Acción Propuesta**: En una nueva rama, eliminar todos los archivos `.mdc` de `.cursor/rules/` que han sido migrados al conjunto maestro.
    *   **Entregable**: Un directorio `.cursor/rules/` limpio en cada repo satélite, conteniendo solo reglas específicas de dominio (si las hay).

*   **Paso C.2: Integrar el Conjunto Maestro vía Git Submodule**
    *   **Objetivo**: Establecer la nueva dependencia hacia las reglas maestras de forma explícita y versionada.
    *   **Acción Propuesta**: Ejecutar `git submodule add <URL_del_repo_raise-jf-ai-common> .cursor/rules/main` en cada repositorio satélite.
    *   **Entregable**: Un archivo `.gitmodules` y un directorio `.cursor/rules/main` en cada repo satélite.

*   **Paso C.3: Gestionar Reglas Específicas del Dominio**
    *   **Objetivo**: Asegurar que las reglas que no son maestras permanezcan y no entren en conflicto.
    *   **Acción Propuesta**: Revisar las reglas restantes en los repositorios satélite (ej. `103-gcs-standards.mdc`). Si su numeración choca con el nuevo índice, reasignarles un ID en un rango reservado (ej. `5xx`).
    *   **Entregable**: Reglas específicas de dominio correctamente numeradas y conservadas en sus respectivos repositorios.

### Fase D: Validación y Finalización

*   **Paso D.1: Validación y Cierre**
    *   **Objetivo**: Asegurar que la nueva estructura funciona y finalizar el proceso.
    *   **Acción Propuesta**: Validar localmente que Cursor carga el conjunto de reglas combinado. Hacer commit y merge de los cambios en todos los repositorios. Actualizar la documentación `README.md` de `raise-jf-ai-common`.
    *   **Entregable**: Todos los repositorios actualizados y la documentación de soporte creada.

## 5. Execution Tracking & Checklist

*Esta sección será completada por el Agente IA durante la Fase 1 (Planificación) del protocolo L0-03 y presentada para aprobación del Orquestador Humano.*

**[Borrador Inicial - Pendiente de Aprobación]**

### Fase A: Preparación
- [ ] **A.1**: Crear directorio `.cursor/rules/` en `raise-jf-ai-common`.
- [ ] **A.2**: Generar el borrador del `master-rules-index.md` y solicitar aprobación de su contenido.

### Fase B: Migración
- [ ] **B.1**: Migrar las 20+ reglas del núcleo común (ej. `001`, `005`, `210`...).
- [ ] **B.2**: Migrar y renombrar las ~5-7 reglas de patrones avanzados y opcionales.

### Fase C: Refactorización de Satélites (Ciclo a repetir por cada repo)
- **Repo: `raise-jf-backend-files`**
    - [ ] **C.1.files**: Eliminar ~25 reglas heredadas.
    - [ ] **C.2.files**: Añadir submódulo `raise-jf-ai-common`.
    - [ ] **C.3.files**: Revisar y renombrar la regla `103-gcs-standards.mdc` si es necesario.
- **Repo: `raise-jf-backend-orders`**
    - [ ] **C.1.orders**: Eliminar ~25 reglas heredadas.
    - [ ] **C.2.orders**: Añadir submódulo `raise-jf-ai-common`.
    - [ ] **C.3.orders**: Revisar si quedan reglas específicas.
- **Repo: `raise-jf-backend-product`**
    - [ ] **C.1.product**: Eliminar ~25 reglas heredadas.
    - [ ] **C.2.product**: Añadir submódulo `raise-jf-ai-common`.
    - [ ] **C.3.product**: Revisar si quedan reglas específicas.
- **Repo: `raise-jf-backend-profile`**
    - [ ] **C.1.profile**: Eliminar ~25 reglas heredadas.
    *   **Acción Propuesta**: Validar localmente que Cursor carga el conjunto de reglas combinado. Hacer commit y merge de los cambios en todos los repositorios. Actualizar la documentación `README.md` de `raise-jf-ai-common`.
    *   **Entregable**: Todos los repositorios actualizados y la documentación de soporte creada.

## 6. Plan de Rollback

En caso de problemas imprevistos, el plan de rollback consiste en revertir los commits en la rama `feature/unify-cursor-rules` de cada repositorio satélite. Dado que la mayor parte del trabajo se realiza en un repositorio central, el riesgo para los proyectos satélite es bajo hasta el momento del merge final. 