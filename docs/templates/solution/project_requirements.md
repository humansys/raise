---
document_id: "[PRD]-[PROJECTCODE]-[SEQ]" # ej: PRD-XYZ-001
title: "Documento de Requisitos del Proyecto (PRD): [Nombre del Proyecto]"
project_name: "[Nombre del Proyecto]"
client: "[Nombre del Cliente/Organización]"
version: "[Número de Versión, ej., 0.1]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
  - "[ID_DOC_RELACIONADO_1]" # ej: VIS-XYZ-001
  - "[ID_DOC_RELACIONADO_2]"
status: "[Draft|In Review|Approved|Final]"
---

# Documento de Requisitos del Proyecto (PRD): [Nombre del Proyecto]

## 1. Introducción y Metas del Proyecto

### 1.1. Resumen del Proyecto
*[Proporcione una visión general concisa del proyecto. ¿De qué se trata a alto nivel?]*

### 1.2. Problema de Negocio / Oportunidad
*[Describa el problema específico que este proyecto busca resolver o la oportunidad de negocio que busca aprovechar. ¿Cuál es el dolor del cliente o la necesidad del mercado? Sea específico sobre el impacto actual.]*
*(**Relacionado con:** `solution-vision-template.md` - Problem Statement)*

### 1.3. Metas y Objetivos del Proyecto
*[Liste las metas de negocio claras, medibles y alcanzables (idealmente SMART) que el proyecto debe lograr. ¿Qué resultados específicos se esperan?]*
*(**Relacionado con:** `solution-vision-template.md` - Business Goals)*
*   **Meta 1:** [Descripción de la meta]
    *   *Objetivo Específico:* [Descripción del objetivo]
*   **Meta 2:** [Descripción de la meta]
    *   *Objetivo Específico:* [Descripción del objetivo]
*   ...

### 1.4. Métricas de Éxito
*[¿Cómo sabremos que el proyecto ha sido un éxito? Defina los Indicadores Clave de Rendimiento (KPIs) o métricas específicas que se rastrearán.]*
*(**Relacionado con:** RaiSE Verifiable-Results, `solution-vision-template.md` - Success Criteria, `feature-prioritization-template.md` - Success Metrics)*
*   **Métrica 1:** [Nombre de la Métrica] <!-- data type="metric" id="METRIC_ID_1" name="[Nombre Métrica]" target="[Valor Objetivo]" method="[Cómo se medirá]" --> - **Objetivo:** [Valor o Rango Objetivo] - **Método de Medición:** [Cómo se medirá]
*   **Métrica 2:** [Nombre de la Métrica] <!-- data type="metric" id="METRIC_ID_2" name="[Nombre Métrica]" target="[Valor Objetivo]" method="[Cómo se medirá]" --> - **Objetivo:** [Valor o Rango Objetivo] - **Método de Medición:** [Cómo se medirá]
*   ...

## 2. Stakeholders y Usuarios

### 2.1. Stakeholders Clave
*[Identifique a las personas o grupos clave que tienen interés o influencia en el proyecto.]*
*(**Relacionado con:** `solution-vision-template.md` - Stakeholders)*
| Rol/Nombre        | Responsabilidad/Interés Principal                         |
|-------------------|-----------------------------------------------------------|
| [ej., Sponsor]    | [ej., Aprobación de presupuesto, visión estratégica]      | <!-- data type="stakeholder" id="STAKEHOLDER_ID_1" role="[ej., Sponsor]" name="[Nombre Opcional]" interest="[Interés Principal]" -->
| [ej., SME Legal]  | [ej., Asegurar cumplimiento normativo]                   | <!-- data type="stakeholder" id="STAKEHOLDER_ID_2" role="[ej., SME Legal]" name="[Nombre Opcional]" interest="[Interés Principal]" -->
| [ej., Marketing]  | [ej., Estrategia de lanzamiento, posicionamiento]         | <!-- data type="stakeholder" id="STAKEHOLDER_ID_3" role="[ej., Marketing]" name="[Nombre Opcional]" interest="[Interés Principal]" -->
| ...               | ...                                                       | <!-- ... -->

### 2.2. Usuarios Objetivo / Personas
*[Describa los diferentes tipos de usuarios finales que interactuarán con la solución. Incluya sus roles, necesidades principales, frustraciones actuales y cómo se espera que esta solución los beneficie.]*
*(**Relacionado con:** RaiSE Human-Centric, `solution-vision-template.md` - User Impact)*
*   **Usuario Tipo 1: [Nombre del Rol/Persona]**
    *   *Descripción:* [Breve descripción del usuario]
    *   *Necesidades Clave:* [Qué necesitan lograr]
    *   *Puntos de Dolor Actuales:* [Qué les frustra ahora]
    *   *Beneficios Esperados:* [Cómo les ayudará la solución]
*   **Usuario Tipo 2: [Nombre del Rol/Persona]**
    *   ...
*   ...

## 3. Alcance del Proyecto

### 3.1. Dentro del Alcance (Funcionalidades Clave)
*[Liste las principales funcionalidades, capacidades o módulos que se incluirán en la versión inicial o fase definida del proyecto. Sea lo más específico posible en esta etapa.]*
*(**Alimenta a:** `solution-vision-template.md` - MVP Scope, `feature-prioritization-template.md` - Feature List)*
*   Funcionalidad/Capacidad 1: [Descripción concisa]
*   Funcionalidad/Capacidad 2: [Descripción concisa]
*   ...

### 3.2. Fuera del Alcance
*[Declare explícitamente qué funcionalidades o características *no* se incluirán en este proyecto o fase para evitar la deriva del alcance.]*
*(**Relacionado con:** `solution-vision-template.md` - Out of Scope)*
*   [Funcionalidad explícitamente excluida 1]
*   [Funcionalidad explícitamente excluida 2]
*   ...

### 3.3. Consideraciones Futuras (Posibles Fases Posteriores)
*[Mencione funcionalidades o mejoras que podrían considerarse para futuras versiones o fases, pero que no forman parte del alcance actual.]*
*(**Relacionado con:** `solution-vision-template.md` - Nice to Have)*
*   [Mejora futura 1]
*   [Mejora futura 2]
*   ...

## 4. Requisitos Funcionales

### 4.1. Resumen de Capacidades
*[Describa con más detalle las funcionalidades clave listadas en "Dentro del Alcance". Puede agrupar requisitos relacionados.]*
*(**Alimenta a:** Creación de Epics/Features/User Stories, `tech_design.md`)*
*   **Capacidad: [Nombre de la Capacidad 1]** <!-- data type="capability" id="CAP_ID_1" name="[Nombre Capacidad 1]" -->
    *   Requisito 1.1: [El sistema debe permitir a los usuarios...] <!-- data type="requirement" id="REQ_ID_1.1" capability_id="CAP_ID_1" type="Functional" description="[Descripción corta del requisito]" -->
    *   Requisito 1.2: [El sistema debe calcular/validar...] <!-- data type="requirement" id="REQ_ID_1.2" capability_id="CAP_ID_1" type="Functional" description="[Descripción corta del requisito]" -->
    *   ...
*   **Capacidad: [Nombre de la Capacidad 2]** <!-- data type="capability" id="CAP_ID_2" name="[Nombre Capacidad 2]" -->
    *   Requisito 2.1: [...] <!-- data type="requirement" id="REQ_ID_2.1" capability_id="CAP_ID_2" type="Functional" description="[Descripción corta del requisito]" -->
    *   ...

### 4.2. Escenarios de Usuario / Flujos de Trabajo Clave
*[Describa los pasos o interacciones principales que los usuarios realizarán para lograr sus objetivos utilizando la solución.]*
*   **Escenario 1: [Nombre del Escenario, ej., Crear Nueva Cuenta]**
    1.  Usuario navega a la página de registro.
    2.  Usuario ingresa [datos requeridos].
    3.  Sistema valida los datos.
    4.  Sistema crea la cuenta y envía correo de bienvenida.
    5.  ...
*   **Escenario 2: [Nombre del Escenario]**
    *   ...

### 4.3. Mapeo a Artefactos Posteriores
*[Esta sección vincula los requisitos funcionales definidos anteriormente con los artefactos que se crearán en fases posteriores, facilitando la trazabilidad.]*
*(**Alimenta a:** `statement_of_work.md`, `estimation_roadmap.md`, `tech_design.md`)*

| Requisito ID (o Grupo) | Artefacto Vinculado (Tipo e ID/Sección) | Notas Adicionales |
|------------------------|-----------------------------------------|-------------------|
| [Req 1.1]              | [ej., SoW Sec 3.2 - Actividad X]        |                   |
| [Req 1.2]              | [ej., Tech Design Componente Y]         |                   |
| [Capacidad 2]          | [ej., Estimation Roadmap - Epic Z]      |                   |
| ...                    | ...                                     | ...               |

### 4.4. Criterios Preliminares de Priorización
*[Esta sección captura información inicial relevante para la priorización de funcionalidades, sirviendo como input para el documento de priorización.]*
*(**Alimenta a:** `feature-prioritization-template.md`)*

| Requisito/Capacidad ID | Valor de Negocio Estimado (Alto/Medio/Bajo) | Urgencia Percibida (Alta/Media/Baja) | Dependencias Conocidas | Notas |
|------------------------|---------------------------------------------|------------------------------------|------------------------|-------|
| [Req 1.1]              | [ej., Alto]                                 | [ej., Alta]                        | [Req 1.2]              |       |
| [Capacidad 2]          | [ej., Medio]                                | [ej., Media]                       |                        |       |
| ...                    | ...                                         | ...                                | ...                    | ...   |

## 5. Requisitos No Funcionales (NFRs)

*[Especifique las restricciones de calidad y operación del sistema. Estos son cruciales para el diseño técnico y la arquitectura.]*
*(**Alimenta a:** `tech_design.md` - Sección de NFRs, Arquitectura)*

*   **Rendimiento:** [ej., Tiempo de respuesta de la API < 500ms bajo X carga, Carga de página inicial < 3s]
*   **Escalabilidad:** [ej., Soportar N usuarios concurrentes, Capacidad de procesar M transacciones por hora, Crecimiento de datos esperado]
*   **Disponibilidad/Fiabilidad:** [ej., Uptime del 99.9%, Tiempo máximo de inactividad permitido por mes]
*   **Seguridad:** [ej., Cumplimiento con [Normativa], Autenticación [Método], Autorización basada en roles, Encriptación de datos sensibles en reposo y tránsito] (Ref: `800-security.mdc`)
*   **Usabilidad:** [ej., Adherencia a guías de estilo específicas, Simplicidad en flujos clave, Feedback claro al usuario]
*   **Accesibilidad (a11y):** [ej., Cumplimiento con WCAG 2.1 Nivel AA]
*   **Mantenibilidad:** [ej., Código documentado, Uso de patrones de diseño estándar, Facilidad para desplegar actualizaciones]
*   **Compatibilidad:** [ej., Navegadores soportados (versiones), Sistemas Operativos]
*   **Gestión de Datos:** [ej., Políticas de retención de datos, Requisitos de copia de seguridad y restauración]

## 6. Requisitos de Datos

*[Describa los aspectos clave relacionados con los datos que manejará el sistema.]*
*(**Alimenta a:** `tech_design.md` - Modelo de Datos)*

*   **Entidades de Datos Principales:** [ej., Cliente, Producto, Pedido, Transacción]
*   **Fuentes de Datos:** [ej., Formularios de usuario, API externa X, Base de datos existente Y]
*   **Destinos de Datos:** [ej., Base de datos principal, Sistema de BI, API externa Z]
*   **Volumen Estimado de Datos:** [ej., N registros iniciales, crecimiento estimado de M por mes]
*   **Requisitos de Calidad de Datos:** [ej., Validación de formatos, Reglas de integridad]
*   **Datos Sensibles / PII:** [Identificar si existen datos personales o sensibles y cualquier requisito específico de manejo (ej., GDPR, HIPAA)]

## 7. Requisitos de Integración

*[Liste los sistemas internos o externos con los que la solución necesita interactuar.]*
*(**Alimenta a:** `tech_design.md` - Arquitectura, Flujo de Datos, APIs)*

*   **Sistema Interno 1: [Nombre del Sistema]**
    *   *Propósito de la Integración:* [ej., Obtener datos de clientes]
    *   *Método de Integración:* [ej., API REST, Acceso directo a BD, Archivos Batch]
    *   *Frecuencia:* [ej., Tiempo real, Diaria]
*   **Sistema Externo 1 (API de Terceros): [Nombre del Servicio]**
    *   *Propósito:* [ej., Procesar pagos, Enviar notificaciones SMS]
    *   *Detalles:* [ej., Endpoint específico, Autenticación requerida]
*   ...

## 8. Supuestos

*[Liste los supuestos clave (de negocio, técnicos, de usuario) en los que se basa el proyecto. Si un supuesto resulta ser falso, podría impactar significativamente el proyecto.]*
*(**Relacionado con:** `solution-vision-template.md` - Assumptions)*

*   **Supuesto de Negocio 1:** [ej., Existe demanda de mercado para esta funcionalidad]
*   **Supuesto Técnico 1:** [ej., La API externa X estará disponible y cumplirá con el SLA acordado]
*   **Supuesto de Usuario 1:** [ej., Los usuarios estarán dispuestos a adoptar el nuevo flujo de trabajo]
*   ...

## 9. Restricciones

*[Liste las limitaciones o restricciones conocidas que afectan al proyecto.]*
*(**Relacionado con:** `solution-vision-template.md` - Constraints)*

*   **Restricción de Negocio 1:** [ej., Presupuesto máximo de X, Fecha límite de lanzamiento Y]
*   **Restricción Técnica 1:** [ej., Debe usar la infraestructura Cloud Z, Compatibilidad requerida con sistema legado W]
*   **Restricción Regulatoria 1:** [ej., Cumplimiento obligatorio con la normativa Q]
*   ...

## 10. Preguntas Abiertas y Riesgos Identificados

*[Documente cualquier pregunta que necesite aclaración por parte del cliente o stakeholders, y cualquier riesgo potencial identificado en esta etapa inicial.]*
*(**Relacionado con:** RaiSE Clarity-Seeking)*

*   **Preguntas Abiertas:**
    *   [Pregunta 1: Necesita aclaración sobre el flujo exacto para...]
    *   [Pregunta 2: ¿Cuál es la política de retención de datos para...]
*   **Riesgos Identificados:**
    *   [Riesgo 1 (Técnico): Posible cuello de botella de rendimiento en...] - **Mitigación Inicial:** [Prueba de carga temprana]
    *   [Riesgo 2 (Negocio): Baja adopción por parte de los usuarios] - **Mitigación Inicial:** [Involucrar a usuarios clave en el diseño]
    *   [Riesgo 3 (Recursos): Disponibilidad limitada del SME X] - **Mitigación Inicial:** [Planificar sesiones con anticipación]
*   ...

## 11. Glosario Específico del Proyecto (Opcional)

*[Para términos comunes de RaiSE, consulte el glosario central: [path/to/RaiSE-terminology.md - **AJUSTAR RUTA RELATIVA**].]*
*[Defina aquí **únicamente** términos o acrónimos específicos de este proyecto o dominio que no estén en el glosario central.]*

| Término     | Definición                               |
|-------------|------------------------------------------|
| [Acrónimo]  | [Expansión y breve descripción]          |
| [Término]   | [Definición clara y concisa]             |
| ...         | ...                                      |

## 12. Historial del Documento

| Versión | Fecha      | Autor(es)      | Cambios Realizados                                  |
|---------|------------|----------------|-----------------------------------------------------|
| 0.1     | YYYY-MM-DD | [Nombre(s)]    | Versión inicial basada en conversaciones con cliente |
| ...     | ...        | ...            | ...                                                 |


</rewritten_file> 