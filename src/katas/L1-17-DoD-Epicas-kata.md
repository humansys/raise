---
id: L1-17-DoD-Epicas-kata
nivel: 1
tags: [dod, epicas, proceso, calidad, raiSE, agentes-ia, gestion]
---

## L1-17: Definición y Uso del DoD para Épicas en Proyectos RaiSE

## Metadatos
- **Id**: L1-17-DoD-Epicas-kata
- **Nivel**: 1
- **Título**: Definición y Uso del DoD para Épicas en Proyectos RaiSE
- **Propósito**: Establecer un marco de trabajo estandarizado para definir, verificar y cerrar la Definition of Done (DoD) a nivel de Épica, asegurando la coherencia, integridad y calidad del entregable completo compuesto por múltiples Historias de Usuario (HUs).
- **Contexto**: Proyectos orquestados por un humano (RaiSE Dev) donde la ejecución técnica es realizada mayoritariamente por agentes de IA. Las Épicas representan funcionalidades completas o hitos significativos. **El DoD de la Épica se define PRIMERO**, estableciendo los requisitos y restricciones que heredarán las HUs.
- **Principios Rectores**: DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid), YAGNI (You Aren't Gonna Need It) y DDD (Domain-Driven Design) como base para todas las decisiones de alcance, diseño y validación de la Épica.
- **Audiencia**: RaiSE Dev (Orquestador), Product Owner, Arquitecto de Solución (Agente/Humano), Tech Lead (Agente/Humano) y agentes de gestión de proyecto.

## Pre-condiciones
- El proyecto tiene una **Visión de Solución**, un **Diseño Técnico General** y un **PRD** definidos y accesibles.
- Existe una **Épica candidata** identificada en el backlog.
- Se ha identificado preliminarmente el backlog de **Historias de Usuario (HUs)** que componen la Épica.
- Se tiene acceso a la `L1-16-DoD-Historias-Usuario-kata`.
- El RaiSE Dev tiene autoridad para orquestar agentes de IA en roles de Arquitectura, QA y Desarrollo.

## Pasos de la Kata

### Paso 1: Validar el Alcance y Contexto de la Épica
- **Acción**:
  - Revisar y validar la Épica contrastándola con los artefactos de referencia existentes: **PRD (Product Requirements Document)** y **Visión de Solución**.
  - Asegurar que el alcance descrito en la Épica cubre las necesidades de negocio documentadas en el PRD.
  - Verificar que la solución técnica propuesta en la Épica es consistente con la Arquitectura y Visión de Solución.
- **Criterios de Aceptación**:
  - Confirmación explícita de que la Épica está alineada con el PRD y la Visión.
  - Identificación de cualquier desviación o necesidad de actualización en los documentos base.

### Paso 2: Establecer la Estructura y Categorías del DoD
- **Acción**:
  - Definir las categorías de calidad de alto nivel para la Épica.
  - Incluir categorías críticas para el cierre de un hito:
    - **Cobertura Funcional**: Completitud del backlog.
    - **Calidad de Integración**: Pruebas E2E.
    - **Gestión de Versiones y Despliegue**: Merge a `main`, release, tags.
    - **Documentación y Transferencia**.
- **Criterios de Aceptación**:
  - Checklist de DoD estructurado y listo para poblar con ítems específicos.

### Paso 3: Validar la Completitud del Backlog de HUs
- **Acción**:
  - Analizar el conjunto de HUs propuestas para la Épica.
  - Verificar si la suma de todas las HUs **completa totalmente** el alcance funcional y no funcional de la Épica (Principio MECE: Mutuamente Excluyentes, Colectivamente Exhaustivas).
  - Si faltan piezas (ej. configuración, scripts de migración, tests de integración), crear las HUs o Tareas faltantes.
- **Criterios de Aceptación**:
  - Declaración validada de que "El backlog de HUs actual es suficiente para completar la Épica".
  - No existen requerimientos de la Épica que no estén asignados a una HU o Tarea.

### Paso 4: Definir los Ítems del DoD de la Épica (Fuente de Verdad)
- **Acción**:
  - Redactar los criterios de "Hecho" específicos para la Épica (ej. "Tiempos de respuesta < 200ms en flujo principal", "Aprobación de Seguridad", "Manual de Usuario actualizado").
  - Establecer estos criterios **ANTES** de refinar las HUs individuales.
  - Publicar estos criterios para que las HUs los "hereden" o adopten como parte de sus propios requisitos o DoDs.
- **Criterios de Aceptación**:
  - Lista de ítems de DoD de Épica documentada.
  - Los criterios son claros y verificables.
  - Mecanismo definido para que las HUs referencien estos criterios (ej. link al DoD de la Épica en cada ticket de HU).

### Paso 5: Definir Estrategia de Pruebas de Integración y E2E
- **Acción**:
  - Diseñar los escenarios de prueba que validan el flujo completo a través de las múltiples HUs.
  - Definir qué pruebas de regresión son obligatorias.
- **Criterios de Aceptación**:
  - Plan de pruebas de integración documentado en el DoD.

### Paso 6: Congelar el DoD de la Épica
- **Acción**:
  - Revisar y aprobar el DoD con el PO y Arquitecto.
  - Marcar el DoD como la referencia autoritativa para el desarrollo de las HUs.
- **Criterios de Aceptación**:
  - DoD aprobado y visible para todos los agentes y humanos.

### Paso 7: Ejecución y Verificación Continua
- **Acción**:
  - A medida que se desarrollan las HUs, verificar que cumplen su parte del "contrato" del DoD de la Épica.
  - Mantener actualizado el estado de los ítems de integración.

### Paso 8: Integración, Merge y Release (Cierre Técnico)
- **Acción**:
  - Verificar que todas las ramas de HUs han sido integradas en la rama de la Épica.
  - Ejecutar la suite completa de pruebas (unitarias, integración, E2E) en la rama de la Épica.
  - **Gestión de Git**:
    - Crear un **Merge Request (MR) / Pull Request** de la rama de la Épica hacia `main` (o la rama de release correspondiente).
    - Revisar y aprobar el MR (Code Review humano + reporte de agentes).
    - Realizar el merge.
  - **Despliegue**:
    - Acordar con el Cliente los pasos específicos de despliegue según su entorno y restricciones.
    - Documentar explícitamente el procedimiento de despliegue acordado e incluirlo como ítem verificable en el DoD.
    - Generar el artefacto de despliegue o tag de versión.
    - Desplegar a entorno de Producción (o Pre-producción/Staging según política) siguiendo los pasos documentados.
    - Verificar la funcionalidad en el entorno destino (Smoke Tests).
- **Criterios de Aceptación**:
  - Código integrado en `main` sin conflictos.
  - Pipeline de CI/CD ejecutado exitosamente.
  - Procedimiento de despliegue validado con el cliente y documentado.
  - Funcionalidad operativa en el entorno objetivo según lo acordado.

### Paso 9: Cierre Administrativo y Reflexión
- **Acción**:
  - Cerrar formalmente la Épica en el sistema de gestión.
  - Realizar la retrospectiva de aprendizaje.
- **Criterios de Aceptación**:
  - Épica marcada como Done.
  - Documento de lecciones aprendidas generado.

## Post-condiciones
- La funcionalidad completa de la Épica está en producción (o lista para release).
- El código está integrado en la rama principal.
- La documentación está actualizada y consistente con lo desplegado.

## Notas Adicionales
- El DoD de la Épica es el "padre" de los criterios de calidad de las HUs. Cualquier cambio en el DoD de la Épica debe propagarse a las HUs en curso.
