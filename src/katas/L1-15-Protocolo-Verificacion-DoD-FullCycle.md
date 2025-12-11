---
id: L1-15-Protocolo-Verificacion-DoD-FullCycle
nivel: 1
tags: [proceso, dod, calidad, full-cycle, raise-methodology]
---
# L1-15: Protocolo de Cumplimiento de DoD Full-Cycle (RaiSE)

## Metadatos

- **Id**: L1-15-Protocolo-Verificacion-DoD-FullCycle
- **Nivel**: 1 (Proceso de Flujo de Trabajo)
- **Título**: Protocolo de Cumplimiento de DoD Full-Cycle para Desarrollador Único
- **Propósito**: Establecer un flujo de trabajo estandarizado que guíe al desarrollador (asistido por IA) desde la definición de requerimientos hasta el monitoreo en producción, asegurando que se extraiga, respete y verifique la "Definition of Done" (DoD) específica de cada proyecto.
- **Contexto**: Aplicable en proyectos gestionados bajo la metodología RaiSE donde un único desarrollador asume la responsabilidad End-to-End (E2E), apoyándose en un Sistema Multi-Agente (Arquitecto, Tech Lead, Coder, DevOps).
- **Audiencia**: Desarrolladores Full-Stack, Arquitectos de Software, Ingenieros de IA.

## Pre-condiciones

- El entorno de desarrollo local está configurado y sincronizado con el repositorio remoto.
- Se tiene acceso a las herramientas de gestión del proyecto (Backlog, Jira/Linear, etc.).
- Los agentes de IA (Arquitecto, Tech Lead, Coder) están disponibles y configurados en el entorno (Cursor/IDE).
- Existe una Historia de Usuario (HU) o Tarea identificada para trabajar.

## Pasos de la Kata

### Paso 1: Extracción y Calibración de la DoD del Proyecto

*Objetivo: Definir o recuperar qué significa "Hecho" específicamente para este proyecto antes de empezar.*

- **Acción**:
  1. **Búsqueda de Definición Explícita**: El desarrollador solicita al Agente Arquitecto buscar un archivo de gobernanza existente (ej. `.raise/DOD_CHECKLIST.md`, `CONTRIBUTING.md` o documentación en `/docs`).
  2. **Inferencia de Estándares (si no hay explícitos)**: Si no existe un documento formal, el Agente Arquitecto debe analizar el repositorio (estructura, configs de linter, pipelines de CI/CD, PRs anteriores) para proponer una DoD preliminar.
  3. **Formalización**: Crear o validar el archivo `.raise/project-dod.md` que contenga la lista de chequeo acordada para este proyecto (calidad de código, cobertura de tests, documentación, seguridad).
- **Criterios de Aceptación**:
  - Existe un documento accesible y claro que lista los criterios de DoD del proyecto actual.
  - El desarrollador entiende las particularidades de calidad exigidas (ej. ¿Cobertura > 80%? ¿Documentación de API en Swagger requerida? ¿Logs en formato JSON?).

### Paso 2: Definition of Ready (DoR) - Fase de Preparación

*Objetivo: Asegurar que la tarea está lista para ser trabajada, evitando bloqueos futuros.*

- **Acción**:
  1. **Análisis de Requerimientos (Agente Arquitecto)**: Revisar la Historia de Usuario. ¿Tiene PRD (Product Requirement Document)? ¿Tiene `Solution Vision`? ¿Tiene criterios de aceptación funcionales claros?
  2. **Diseño Técnico (Agente Tech Lead)**: Generar o validar el `Tech Design` y el `Implementation Plan`. El diseño debe estar guiado por **DDD** (Domain-Driven Design) para la modelación y acotado estrictamente al **MVP** (Minimum Viable Product).
  3. **Verificación de Dependencias**: Confirmar que todos los assets, accesos o microservicios dependientes están disponibles.
- **Criterios de Aceptación**:
  - La HU tiene un plan de implementación aprobado por el Agente Tech Lead.
  - El diseño respeta los límites del dominio (DDD) y no sobre-ingenieriza la solución (MVP).
  - **Check de Calidad**: "No se escribe código hasta que el plan está claro".

### Paso 3: Ejecución del Desarrollo y Calidad Continua

*Objetivo: Implementar la solución cumpliendo los estándares técnicos en tiempo real.*

- **Acción**:
  1. **Implementación Guiada (Agente Coder)**: Escribir el código siguiendo el plan, aplicando TDD si la DoD lo exige.
  2. **Revisión Continua (Agente Tech Lead)**: El desarrollador invoca al Tech Lead periódicamente para revisiones de código incrementales. La revisión se centra estrictamente en:
     - **KISS** (Keep It Simple, Stupid): ¿Es la solución más simple posible?
     - **YAGNI** (You Aren't Gonna Need It): ¿Se ha eliminado código especulativo o innecesario?
     - **DRY** (Don't Repeat Yourself): ¿Hay duplicidad lógica?
  3. **Generación de Documentación**: Actualizar la documentación técnica y de usuario simultáneamente al código (La documentación precede o acompaña al código).
- **Criterios de Aceptación**:
  - El código compila y pasa los tests unitarios locales.
  - Los linters y formateadores no reportan errores.
  - La documentación (código y externa) está actualizada conforme a los cambios.

### Paso 4: Verificación Pre-Deployment (La "DoD Técnica")

*Objetivo: Validar que el incremento cumple todos los requisitos de calidad antes de intentar desplegar.*

- **Acción**:
  1. **Auditoría Automatizada**: Ejecutar suite completa de tests (unitarios, integración).
  2. **Validación de Seguridad**: Verificar que no se introducen vulnerabilidades (dependencias, secretos expuestos).
  3. **Checklist DoD**: El Agente Tech Lead repasa el archivo `.raise/project-dod.md` generado en el Paso 1 contra el estado actual de la rama.
  4. **Validación Final de Principios RaiSE**: Realizar un barrido final confirmando que no se han degradado los principios durante la implementación:
     - **DDD**: ¿El modelo de dominio sigue puro y aislado?
     - **MVP**: ¿Se implementó solo lo necesario para la historia?
     - **KISS/YAGNI**: ¿La solución final es simple y sin código muerto?
- **Criterios de Aceptación**:
  - Todos los items de la DoD técnica (Tests, Security, Style) están marcados como OK.
  - Se confirma explícitamente el cumplimiento de DDD, MVP, KISS y YAGNI.
  - La rama está lista para Merge.

### Paso 5: Despliegue y Validación en Producción

*Objetivo: Llevar el valor al usuario y asegurar su funcionamiento.*

- **Acción**:
  1. **Estrategia de Despliegue (Agente DevOps / Colaboración)**:
     - *Escenario Automático*: El Agente genera/ejecuta scripts de despliegue (CI/CD, Terraform, etc.).
     - *Escenario Colaborativo*: El desarrollador prepara los artefactos y guía al equipo del cliente para la subida a producción.
  2. **Smoke Test en Producción**: Verificar las funcionalidades críticas inmediatamente después del despliegue.
  3. **Configuración de Observabilidad**: Asegurar que los logs, métricas y alertas están activos para la nueva funcionalidad.
- **Criterios de Aceptación**:
  - La funcionalidad está activa en el entorno productivo.
  - Los sistemas de monitoreo están recibiendo datos.
  - No hay regresiones críticas reportadas post-deploy inmediato.

## Post-condiciones

- La Historia de Usuario se marca oficialmente como "Done" en el sistema de gestión.
- El código está fusionado en la rama principal.
- La documentación del proyecto refleja el nuevo estado del sistema.
- Existe evidencia (logs, capturas, métricas) de que la funcionalidad opera correctamente en producción.

## Notas Adicionales

- **Adaptabilidad**: Esta Kata es un marco general. Si el proyecto es un MVP rápido, la DoD (Paso 1) será más laxa. Si es un sistema bancario, la DoD (Paso 1) será estricta en seguridad y logs. El proceso (Pasos 2-5) se mantiene igual.
- **Rol del Desarrollador**: En RaiSE, el desarrollador es el orquestador. Los agentes ejecutan y aconsejan, pero el desarrollador tiene la responsabilidad final de validar el "Done".
