# RaiSE Kata: Generación de Plan de Implementación Detallado por HU

**ID**: flujo-04
**Nombre**: Generación de Plan de Implementación Detallado por Historia de Usuario
**Descripción**: Guía el proceso para crear un plan de implementación detallado (en formato checklist) para una Historia de Usuario (HU) específica, a partir de su plan técnico de alto nivel (si existe) y sus Criterios de Aceptación (ACs). Este plan detallado servirá de base para la ejecución de la HU, referenciando Katas de patrón y técnica.
**Objetivo**:
    *   Estandarizar la creación de planes de implementación detallados para HUs.
    *   Asegurar que los planes cubran todos los aspectos necesarios: preparación, diseño, desarrollo de componentes, pruebas unitarias, integración, pruebas de aceptación y documentación.
    *   Facilitar la estimación y el seguimiento del progreso de la HU.
    *   Establecer cómo el plan de implementación detallado debe referenciar Katas de patrón (Componentes) y técnica (Técnicas) para la construcción de elementos específicos.
**Dependencias**:
    *   Kata de principios: Meta-Kata de Desarrollo
    *   Historia de Usuario (HU) definida con Criterios de Aceptación (ACs) claros (idealmente en Gherkin).
    *   (Opcional pero recomendado) Plan Técnico de Alto Nivel para la HU.
**Guardrails Relacionados**:
    *   `010-raise-methodology-overview.mdc`
    *   Guardrails de documentación relevantes para planes y checklists.

### Fase 0: Verificación de Prerrequisitos y Entidades Clave

Antes de detallar la implementación, se verifica la existencia y estructura de los siguientes componentes clave en el código base:

*   **Entidad `[Nombre de la Entidad Clave]`**: [ ] Verificada. (Ej: `[Nombre de la Entidad]` se verificará si tiene propiedades relevantes a la HU, como `Status` o `Details`).
*   **Servicio gRPC `[Nombre del Servicio gRPC]`**: [ ] Verificado. (Ej: `[Nombre del Servicio gRPC]` se verificará si tiene el método `[Nombre del Método]`).
*   **Otros Componentes/Contratos**: [ ] Verificados. (Especificar cualquier otra dependencia crucial).

Esta verificación asegura que el plan se basa en el estado actual del repositorio y reduce el riesgo de retrabajo por asunciones incorrectas.

---

**Pasos del Kata (Orquestador y Asistente RaiSE):**

1. **Inicio y Contexto (Orquestador):**

   * Identifica la HU a planificar (`[ID_JIRA]`), sus Criterios de Aceptación (ACs), y cualquier Plan Técnico de Alto Nivel existente (`[Plan Técnico Alto Nivel Path]`, si lo hay).
   * **Instrucción:** "Vamos a generar el Plan de Implementación Detallado para la HU `[ID_JIRA]`. Por favor, revisa sus ACs [y su plan técnico en `[Plan Técnico Alto Nivel Path]` si existe]."

   **Verificación:** El Orquestador ha identificado claramente la HU, sus ACs, y la ubicación del plan técnico (si existe).

   > **Si no puedes continuar:** HU no identificada o ACs no disponibles → Localizar la documentación de la HU antes de proceder.

2. **Análisis de Entradas (Asistente RAISE, instruido por Orquestador):**

   * **Acción (Asistente):** Lee los ACs de la HU y el plan técnico de alto nivel (si se proporcionó). Identifica los principales componentes, funcionalidades, flujos de datos y requisitos no funcionales descritos.
   * **Instrucción (Orquestador):** "Resume los principales módulos, componentes o funcionalidades que se deben desarrollar, modificar o integrar para satisfacer los ACs de la HU `[ID_JIRA]`."
   * **Acción (Asistente):** Proporciona un resumen conciso de los elementos clave identificados.
   * **Validación (Orquestador):** Confirma el resumen y realiza ajustes si es necesario para asegurar una comprensión completa.

   **Verificación:** El Asistente ha presentado un resumen de componentes/funcionalidades y el Orquestador lo ha validado.

   > **Si no puedes continuar:** Resumen incompleto o incorrecto → El Orquestador proporciona contexto adicional sobre la HU para refinar el análisis.

3. **Estructuración del Plan de Implementación Detallado (Orquestador y Asistente):**

   * **Instrucción (Orquestador):** "Crearemos el Plan de Implementación Detallado para `[ID_JIRA]` en el archivo `[Path HU]/IMPLEMENTATION_PLAN_[ID_JIRA].md`. Este plan debe seguir un formato de checklist Markdown y organizarse en fases estándar:
     1. Preparación y Configuración
     2. Diseño Detallado (si es necesario para componentes complejos)
     3. Desarrollo de Componentes (desglosado por cada componente/módulo)
     4. Pruebas Unitarias (por componente/módulo y escenario)
     5. Integración de Componentes
     6. Pruebas de Aceptación (mapeo a ACs Gherkin)
     7. Documentación
     8. Refinamiento y Revisión Final"
   * **Acción (Asistente):** Genera una plantilla inicial para el archivo `[Path HU]/IMPLEMENTATION_PLAN_[ID_JIRA].md` con las secciones de fases mencionadas, usando formato de checklist Markdown (ej. `- [ ] Tarea`).
   * **Validación (Orquestador):** Revisa la estructura base del plan.

   **Verificación:** Existe un archivo `IMPLEMENTATION_PLAN_[ID_JIRA].md` con las 8 secciones de fases estándar en formato checklist.

   > **Si no puedes continuar:** Estructura incompleta → Agregar las secciones faltantes antes de continuar con el desglose de tareas.

4. **Desglose de Tareas de Desarrollo por Componente/Funcionalidad (Orquestador y Asistente - Bucle por cada componente/funcionalidad principal):**

   * **Instrucción (Orquestador):** "Para el componente/funcionalidad `[Nombre del Componente/Funcionalidad identificado en el paso 2]`, vamos a detallar las tareas en el Plan de Implementación. Bajo 'Desarrollo de Componentes', incluye la creación/modificación de archivos, definición de interfaces/clases/funciones, implementación de la lógica central y manejo de errores. Importante: para cada tarea de desarrollo de un componente arquitectónico (entidad, caso de uso, repositorio, etc.), añade una referencia a la Kata de patrón o técnica relevante que guiará su implementación específica."
   * **Acción (Asistente):**
     * **Guía para la IA:** Antes de generar ejemplos, el asistente DEBE buscar en el repositorio actual (o en el contexto de tree-repo si está disponible) código generado previamente sobre el componente a generarse para extraer ejemplos válidos que se alineen con los estándares y el estilo existente del codebase.
     * Añade al checklist de `IMPLEMENTATION_PLAN_[ID_JIRA].md` las tareas detalladas para el componente/funcionalidad, bajo la sección "Desarrollo de Componentes".
     * **Ejemplos de tareas con referencia a Katas:**
       * `- [ ] Crear la entidad de Dominio `[NombreEntidad]` con propiedades relevantes (ej. `Id`, `Propiedad1`, `Propiedad2`). (Ref: 201-clean-architecture-domain-entities.mdc)`
       * `- [ ] Definir la interfaz `I[NombreEntidad]Repository` en la capa Application. (Ref: 205-clean-architecture-domain-repository-interfaces.mdc)`
       * `- [ ] Implementar `[Accion][NombreEntidad]Command` y `[Accion][NombreEntidad]CommandHandler` en Application. (Ref: 210-application-cqrs-commands.mdc)`
       * `- [ ] Crear `[Accion][NombreEntidad]CommandValidator` para el comando anterior. (Ref: 215-application-validation.mdc)`
       * `- [ ] Implementar `[NombreEntidad]Repository` en la capa Infrastructure usando EF Core. (Ref: 223-infrastructure-efcore-repository-implementations.mdc)`
       * `- [ ] Definir el servicio gRPC `[NombreServicio]` en Application/Protos/[nombre_servicio_vX].proto. (Ref: 230-infrastructure-grpc-proto-files.mdc)`
       * `- [ ] Implementar `[NombreServicio]V1` en Api/Services/ delegando a MediatR. (Ref: 231-infrastructure-grpc-server-services.mdc)`
       * `- [ ] Configurar el endpoint gRPC en el Program.cs o Startup.cs. (Ref: 233-infrastructure-grpc-configuration.mdc)`
       * `- [ ] Crear pruebas unitarias para `[Accion][NombreEntidad]CommandHandler`. (Ref: 260-testing-unit-tests.mdc, 261-testing-mocking-strategy.mdc)`
   * **Validación (Orquestador):** Revisa el desglose de tareas para el componente/funcionalidad actual, asegurando la correcta referenciación a las Katas de patrón/técnica.

   **Verificación:** Cada componente identificado en el Paso 2 tiene tareas detalladas con referencias a Katas de patrón o técnica.

   > **Si no puedes continuar:** Faltan referencias a Katas → Identificar la kata aplicable consultando el catálogo de katas de patrón y técnica.

5. **Desglose de Tareas de Pruebas Unitarias (Orquestador y Asistente - Bucle por cada componente/funcionalidad):**

   * **Instrucción (Orquestador):** "Para el mismo componente/funcionalidad `[Nombre del Componente/Funcionalidad]`, detalla ahora las tareas para 'Pruebas Unitarias'. Considera los escenarios clave, casos límite y la verificación de la lógica interna. Las pruebas deben seguir los lineamientos de la Kata de técnica de Testing Estratégico."
   * **Acción (Asistente):** Añade al checklist las tareas para pruebas unitarias, indicando la referencia a la kata de técnica correspondiente.
     * `- [ ] Escribir pruebas unitarias para 'NombreEntidad' (escenarios: creación válida, validación de campos) (Ref: técnica-testing-estratégico)`
   * **Validación (Orquestador):** Revisa las tareas de pruebas unitarias.

   **Verificación:** Cada componente tiene tareas de pruebas unitarias definidas con escenarios clave y casos límite.

   > **Si no puedes continuar:** Escenarios de prueba no claros → Revisar los ACs de la HU para derivar casos de prueba.

6. **Desglose de Tareas de Integración (Orquestador y Asistente):**

   * **Instrucción (Orquestador):** "Identifiquemos los puntos de integración entre los componentes desarrollados (ej. Caso de Uso llamando a Repositorio, ViewModel usando Caso de Uso). Añade las tareas correspondientes en la sección 'Integración de Componentes' del plan."
   * **Acción (Asistente):** Añade las tareas de integración al checklist.
   * **Validación (Orquestador):** Revisa y valida las tareas de integración.

   **Verificación:** Existen tareas de integración que conectan los componentes desarrollados en el Paso 4.

   > **Si no puedes continuar:** Puntos de integración no identificados → Revisar el diagrama de dependencias entre componentes.

7. **Mapeo de Criterios de Aceptación a Tareas de Prueba de Aceptación (Orquestador y Asistente):**

   * **Instrucción (Orquestador):** "Para cada Criterio de Aceptación (AC) Gherkin de la HU `[ID_JIRA]`, añade una tarea de alto nivel en la sección 'Pruebas de Aceptación' del plan. Esta tarea indicará la necesidad de verificar dicho AC. La estrategia detallada para estas pruebas se guiará por la Kata de técnica de Testing Estratégico."
   * **Acción (Asistente):** Añade ítems al checklist para cada AC Gherkin, ej. `- [ ] Verificar AC: [Given/When/Then del AC] (Estrategia guiada por técnica-testing-estratégico)`.
   * **Validación (Orquestador):** Confirma que todos los ACs estén cubiertos.

   **Verificación:** Cada AC Gherkin de la HU tiene una tarea correspondiente en la sección 'Pruebas de Aceptación'.

   > **Si no puedes continuar:** ACs sin mapear → Verificar que los ACs de la HU estén completos y bien definidos antes de continuar.

8. **Definición de Tareas Generales (Orquestador y Asistente):**

   * **Instrucción (Orquestador):** "Completemos el plan añadiendo tareas generales a las secciones de 'Preparación y Configuración' (ej. creación de rama, revisión de dependencias), 'Documentación' (ej. docstrings, README de módulo si aplica), y 'Refinamiento y Revisión Final' (ej. limpieza de código, revisión de pares)."
   * **Acción (Asistente):** Añade estas tareas generales a las secciones correspondientes del checklist.
   * **Validación (Orquestador):** Revisa la completitud de las tareas generales.

   **Verificación:** Las secciones 'Preparación', 'Documentación' y 'Refinamiento' contienen tareas relevantes para el ciclo completo.

   > **Si no puedes continuar:** Secciones vacías → Añadir al menos las tareas mínimas de preparación (rama, dependencias) y cierre (revisión de código).

9. **Revisión y Finalización del Plan de Implementación Detallado (Orquestador y Asistente):**

   * **Instrucción (Orquestador):** "Por favor, muéstrame el contenido completo del archivo `[Path HU]/IMPLEMENTATION_PLAN_[ID_JIRA].md` para una revisión final."
   * **Acción (Asistente):** Presenta el plan de implementación detallado completo.
   * **Validación (Orquestador):** Revisa la claridad, completitud, consistencia y correcta referenciación a otras Katas. Realiza los ajustes finales necesarios.
   * **Confirmación (Orquestador):** "El Plan de Implementación Detallado para la HU `[ID_JIRA]` está completo y aprobado. Este plan ahora será la guía principal para la ejecución de la HU, utilizando la Kata de flujo de Implementación de HU y las Katas de patrón/técnica referenciadas para cada tarea específica."

   **Verificación:** El plan completo ha sido revisado y aprobado explícitamente por el Orquestador.

   > **Si no puedes continuar:** Plan no aprobado → Incorporar el feedback del Orquestador y presentar el plan revisado para nueva validación.

---

**Resultado Esperado:**

* Un archivo `IMPLEMENTATION_PLAN_[ID_JIRA].md` creado en la ruta especificada, conteniendo un plan detallado en formato checklist.
* El plan debe estar estructurado por fases y desglosar las tareas de desarrollo, pruebas, integración y documentación para la HU.
* Las tareas de desarrollo de componentes deben incluir referencias explícitas a las Katas de patrón y técnica relevantes que guiarán su implementación.
* El plan está listo para ser utilizado como entrada para la Kata de flujo de Implementación de HU.

**Principios RaiSE Reforzados:**

* **Documentación Precede al Código (Documentation First):** El plan detallado es un artefacto de diseño clave.
* **Desarrollo Guiado por Katas (Kata-Driven Development):** Esta kata guía la creación de un plan que, a su vez, referencia otras katas.
* **Explicabilidad Inherente (Inherent Explicability):** El plan detallado hace explícito el proceso de implementación.
* **Orquestación Humana, Asistencia IA:** El practicante define la estrategia y valida, mientras el asistente ayuda en la generación y estructuración del plan.
