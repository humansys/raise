---
document_id: "[SOW]-[PROJECTCODE]-[SEQ]" # ej: SOW-XYZ-001
title: "Statement of Work (SoW): [Nombre del Proyecto]"
project_name: "[Nombre del Proyecto]"
client: "[Nombre del Cliente/Organización]"
provider: "[Nombre del Proveedor/Compañía, ej., RaiSE]"
version: "[Número de Versión, ej., 1.0]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
    - "[ID del PRD, ej., PRD-XYZ-001]" # From old PRD ref
    - "[ID_DOC_RELACIONADO_1]" # ej: TEC-XYZ-001, EST-XYZ-001
    - "[ID_DOC_RELACIONADO_2]"
status: "[Draft|In Review|Approved|Final]"
---

# Statement of Work (SoW): [Nombre del Proyecto]

## 1. Introducción y Visión General del Proyecto

*[Resumen ejecutivo del proyecto, derivado del PRD Sec 1.1. Describe brevemente el contexto, el problema a resolver y la solución propuesta a alto nivel.]*

## 2. Objetivos del Proyecto

*[Reiterar las metas y objetivos clave del proyecto tal como se definieron en el PRD Sec 1.3. Enfocarse en los resultados de negocio que el cliente espera lograr.]*

*   **Objetivo 1:** [Descripción del objetivo]
*   **Objetivo 2:** [Descripción del objetivo]
*   ...

## 3. Alcance de los Servicios

*[Esta sección detalla el trabajo específico que será realizado por el proveedor. Basado en PRD Sec 3.1 y Sec 4.]*

### 3.1. Fases del Proyecto (Opcional)
*[Si el proyecto se divide en fases, descríbalas aquí brevemente.]*
*   **Fase 1:** [Nombre/Propósito de la Fase, ej., Descubrimiento y Diseño]
*   **Fase 2:** [Nombre/Propósito de la Fase, ej., Desarrollo MVP]
*   **Fase 3:** [Nombre/Propósito de la Fase, ej., Pruebas y Despliegue]

### 3.2. Actividades Principales
*[Listar las actividades clave que el proveedor llevará a cabo. Sea específico.]*
*   Gestión de Proyecto y Comunicación.
*   Talleres de Descubrimiento y Refinamiento de Requisitos (si aplica).
*   Diseño Técnico y Arquitectura de la Solución (Ref: `tech_design.md`).
*   Desarrollo de [Funcionalidad/Epic Clave 1 - Ref PRD Sec 4.1]. *(Detalle Técnico: Tech Design Sec X)*
*   Desarrollo de [Funcionalidad/Epic Clave 2 - Ref PRD Sec 4.1]. *(Detalle Técnico: Tech Design Sec Y)*
*   ...
*   Integración con [Sistema X - Ref PRD Sec 7]. *(Detalle Técnico: Tech Design Sec Z)*
*   Pruebas Unitarias, de Integración y de Sistema.
*   Soporte para Pruebas de Aceptación de Usuario (UAT).
*   Despliegue en [Ambiente(s) Objetivo(s)].
*   Documentación Técnica y de Usuario.
*   Transferencia de Conocimiento (si aplica).

## 4. Entregables

*[Listar los resultados tangibles específicos que se entregarán al cliente al finalizar el proyecto o sus fases.]*

### 4.1. Matriz de Trazabilidad de Requisitos (Opcional)
*[Para mayor rigor, esta tabla mapea los entregables clave del SoW con los requisitos originales del PRD.]*

| Entregable/Funcionalidad Clave (SoW) | Requisito(s) PRD Vinculado(s) (ID/Sec) | Notas |
|--------------------------------------|----------------------------------------|-------|
| [Entregable Software X]              | [PRD Req 1.1, PRD Req 1.3]             |       |
| [Funcionalidad Y (parte de SoW 3.2)] | [PRD Capacidad 2, PRD Req 2.1]         |       |
| [Documento Z (Manual Usuario)]       | [PRD NFR Usabilidad]                   |       |
| ...                                  | ...                                    | ...   |

### 4.2. Listado de Entregables
*   **Documentación:**
    *   Documento de Requisitos del Proyecto (Ref PRD).
    *   Diseño Técnico Detallado (Ref: `tech_design.md`).
    *   Especificaciones de API (si aplica, Ref: `api_spec.md`).
    *   Manual de Usuario (si aplica).
    *   Manual Técnico/Operacional (si aplica).
*   **Software:**
    *   Código Fuente de la Aplicación [Nombre del Proyecto].
    *   Scripts de Despliegue.
    *   Aplicación desplegada en [Ambiente(s) Objetivo(s)].
*   **Otros:**
    *   Informes de Progreso (semanal/quincenal).
    *   Actas de Reunión.
    *   Informe Final del Proyecto.

## 5. Cronograma y Hitos Clave

*[Presentar un cronograma estimado de alto nivel con las fechas clave o hitos del proyecto. Esto puede ser más detallado en un Plan de Proyecto separado. (Estimación Detallada: Estimation Roadmap [ID Documento])]*

| Hito Clave                           | Fecha Estimada de Finalización |
|--------------------------------------|--------------------------------|
| Kick-off del Proyecto                | [YYYY-MM-DD]                   |
| Finalización Diseño Técnico          | [YYYY-MM-DD]                   |
| Finalización Desarrollo [Func. 1]    | [YYYY-MM-DD]                   |
| Inicio Pruebas UAT                   | [YYYY-MM-DD]                   |
| Despliegue a Producción (Go-live)    | [YYYY-MM-DD]                   |
| Cierre del Proyecto                  | [YYYY-MM-DD]                   |

*Nota: Las fechas son estimadas y pueden estar sujetas a cambios según el progreso del proyecto y la gestión de dependencias.*

## 6. Supuestos del Proyecto

*[Reiterar los supuestos clave del PRD Sec 8 que son fundamentales para la ejecución exitosa del proyecto y la estimación.]*

*   [Supuesto 1 del PRD]
*   [Supuesto 2 del PRD]
*   Disponibilidad oportuna del personal clave del Cliente para talleres, feedback y aprobaciones.
*   Acceso a los sistemas y documentación necesarios del Cliente.
*   El alcance definido en la Sección 3 no cambiará significativamente sin un proceso formal de gestión de cambios.
*   ...

## 7. Responsabilidades del Cliente

*[Definir claramente las tareas, recursos o información que el Cliente debe proporcionar para facilitar el éxito del proyecto.]*

*   Designar un Punto de Contacto Principal (Project Manager/Sponsor) con autoridad para tomar decisiones.
*   Proporcionar acceso oportuno a los stakeholders y SMEs necesarios.
*   Proporcionar toda la documentación relevante sobre sistemas existentes, APIs, etc.
*   Proporcionar acceso a los entornos de prueba y producción necesarios.
*   Realizar las Pruebas de Aceptación de Usuario (UAT) dentro de los plazos acordados.
*   Aprobar los entregables de manera oportuna.
*   Proporcionar feedback constructivo y a tiempo.
*   Gestionar cualquier software/hardware/licencia de terceros requerida por el Cliente.
*   ...

## 8. Exclusiones del Alcance

*[Reiterar explícitamente lo que *no* está incluido en este SoW, basado en PRD Sec 3.2.]*

*   [Exclusión 1 del PRD]
*   [Exclusión 2 del PRD]
*   Migración de datos históricos más allá de [Alcance específico definido, si lo hay].
*   Soporte post-implementación más allá de [Período de garantía específico, si lo hay].
*   Personalización o desarrollo de funcionalidades no especificadas en la Sección 3.
*   Costos de licencias de software de terceros.
*   ...

## 9. Precio y Condiciones de Pago

*[Esta sección detallará la estructura de costos y el calendario de pagos. Usar placeholders en la plantilla.]*

*   **Modelo de Precios:** [ej., Precio Fijo, Tiempo y Materiales (T&M), Híbrido]
*   **Precio Total Estimado (si aplica):** [Moneda y Monto]
*   **Tarifas (si T&M):** [Detalle de tarifas por rol/hora]
*   **Calendario de Pagos:**
    *   [ej., XX% al firmar el SoW]
    *   [ej., XX% al completar el Hito Y]
    *   [ej., Facturación mensual para T&M]
*   **Condiciones de Pago:** [ej., Net 30 días]
*   **Impuestos:** [Indicar si los precios incluyen o excluyen impuestos aplicables]

## 10. Criterios de Aceptación

*[Describir cómo se considerarán completados y aceptados los entregables.]*

*   Los entregables se considerarán aceptados cuando cumplan con los requisitos funcionales y no funcionales definidos en el PRD y este SoW.
*   El Cliente tendrá [Número] días hábiles para revisar los entregables clave y proporcionar feedback o aprobación formal (ej., UAT).
*   La aceptación final del proyecto se basará en la finalización exitosa de todos los entregables y el cumplimiento de los objetivos del proyecto definidos.

## 11. Gestión de Cambios

*[Describir el proceso para manejar solicitudes de cambio al alcance, cronograma o presupuesto definidos.]*

*   Cualquier cambio solicitado al alcance definido en este SoW deberá seguir un proceso formal de Solicitud de Cambio (Change Request - CR).
*   Cada CR será evaluado por el Proveedor en términos de impacto en el cronograma, esfuerzo y costo.
*   Los CRs aprobados por ambas partes se documentarán en una enmienda a este SoW.

## 12. Términos y Condiciones

*[Referencia a los términos contractuales estándar que rigen la relación, como confidencialidad, propiedad intelectual, garantías, limitación de responsabilidad, ley aplicable, etc. Esto podría ser una sección detallada o una referencia a un Anexo o Acuerdo Maestro de Servicios (MSA).]*

*   Este Statement of Work está sujeto a los términos y condiciones del Acuerdo Maestro de Servicios (MSA) firmado entre [Nombre del Cliente] y [Nombre del Proveedor] con fecha [Fecha del MSA], si existe. / O bien, detallar términos clave aquí o en un anexo.*

## 13. Aprobaciones

*Las firmas a continuación indican la aceptación de este Statement of Work.*

**Por [Nombre del Cliente]:**

Nombre:

Cargo:

Firma:

Fecha:

**Por [Nombre del Proveedor]:**

Nombre:

Cargo:

Firma:

Fecha: 