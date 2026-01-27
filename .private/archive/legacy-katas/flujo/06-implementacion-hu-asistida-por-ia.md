# RaiSE Kata: Implementación de Historia de Usuario Asistida por IA

**ID**: flujo-06
**Nombre**: Implementación de Historia de Usuario Asistida por IA con Validación Continua
**Descripción**: Esta kata guía al Asistente de IA a través del proceso de implementación de una Historia de Usuario (HU), desglosando las tareas en pasos atómicos. En cada paso crítico, el Asistente debe pausar y solicitar la validación del Orquestador. Se prioriza la adición de nuevo código y archivos, y se evita la modificación de código existente a menos que sea estrictamente necesario y aprobado por el usuario.
**Objetivo**:
    *   Asegurar que el proceso de implementación de una HU sea colaborativo y esté bajo el control granular del Orquestador.
    *   Minimizar el riesgo de "alucinaciones" o cambios no deseados en el código base existente.
    *   Promover un flujo de trabajo "add-only" para la generación de código, salvo excepción aprobada.
    *   Reforzar la adherencia a los estándares y Katas de patrón/técnica en cada componente generado.
**Dependencias**:
    *   Kata de principios: Meta-Kata de Desarrollo
    *   Kata de flujo: Generación de Plan de Implementación Detallado por HU (flujo-04)
    *   Plan de Implementación Detallado para la HU (generado por flujo-04).
    *   Katas de patrón y técnica para la guía específica de implementación.
**Guardrails Cursor Relacionados**:
    *   `001-general-coding-standards.mdc`
    *   `005-solution-project-organization.mdc`
    *   `010-raise-methodology-overview.mdc`
    *   `020-raise-design-documentation-standards.mdc`
    *   `101-dotnet-csharp-standards.mdc`
    *   `102-common-library-usage.mdc`
    *   `105-shared-extensions.mdc`
    *   `201-clean-architecture-domain-entities.mdc`
    *   `202-clean-architecture-domain-value-objects.mdc`
    *   `203-clean-architecture-domain-partials.mdc`
    *   `205-clean-architecture-domain-repository-interfaces.mdc`
    *   `206-clean-architecture-domain-events.mdc`
    *   `210-application-cqrs-commands.mdc`
    *   `211-application-cqrs-queries.mdc`
    *   `215-application-validation.mdc`
    *   `216-application-domain-event-handlers.mdc`
    *   `217-application-mapping.mdc`
    *   `220-clean-architecture-infrastructure-overview.mdc`
    *   `221-infrastructure-efcore-dbcontext.mdc`
    *   `222-infrastructure-efcore-entity-configurations.mdc`
    *   `223-infrastructure-efcore-repository-implementations.mdc`
    *   `226-infrastructure-efcore-query-strategies.mdc`
    *   `228-infrastructure-external-service-wrappers.mdc`
    *   `229-infrastructure-cron-job-implementation.mdc`
    *   `230-infrastructure-grpc-proto-files.mdc`
    *   `231-infrastructure-grpc-server-services.mdc`
    *   `232-infrastructure-grpc-client-consumption.mdc`
    *   `233-infrastructure-grpc-configuration.mdc`
    *   `234-application-grpc-client-consumption.mdc`
    *   `240-api-layer-structure-naming.mdc`
    *   `241-api-routing-verbs.mdc`
    *   `242-api-request-response-models.mdc`
    *   `243-api-error-handling.mdc`
    *   `244-api-auth.mdc`
    *   `245-api-swagger-openapi.mdc`
    *   `247-api-user-identity-access.mdc`
    *   `250-logging-serilog.mdc`
    *   `260-testing-unit-tests.mdc`
    *   `261-testing-mocking-strategy.mdc`
    *   `270-configuration-management.mdc`
    *   `280-containerization-dockerfile.mdc`
    *   `281-containerization-docker-compose.mdc`
    *   `290-cicd-pipelines.mdc`
    *   `300-csharp-project-documentation.mdc`

---

**Pasos del Kata (Asistente RaiSE):**

1.  **Inicio y Carga del Plan de Implementación (Asistente)**:
    *   **Acción**: Solicita al Orquestador la ruta al "Plan de Implementación Detallado" de la Historia de Usuario (generado por flujo-04).
    *   **Pausa para Validación**: Espera la ruta.
    *   **Acción**: Lee el contenido del plan y resume las principales tareas a realizar, con énfasis en los componentes a crear/modificar y las Katas de patrón/técnica referenciadas.
    *   **Pausa para Validación**: "He leído el plan. Estas son las tareas principales que he identificado. ¿Confirmas que esta es la interpretación correcta y el orden de ejecución que prefieres?"

    **Verificación:** El Asistente ha cargado el Plan de Implementación y el Orquestador ha confirmado la interpretación de las tareas.

    > **Si no puedes continuar:** Plan no encontrado o no legible → Solicitar al Orquestador la ruta correcta o ejecutar primero la kata flujo-04.

2.  **Iteración de Tareas del Plan (Bucle por cada tarea en el Plan de Implementación)**:
    Para cada tarea en el Plan de Implementación Detallado:

    a.  **Análisis de Tarea y Kata Relevante (Asistente)**:
        *   **Acción**: Identifica el tipo de tarea (ej. crear entidad, definir interfaz, implementar manejador, crear validador, añadir prueba) y la Kata de patrón/técnica relevante si está referenciada.
        *   **Acción**: Lee la Kata de patrón/técnica referenciada para comprender la estructura, convenciones y ejemplos de código. Si no hay una Kata específica referenciada, se basará en los guardrails Cursor generales más relevantes.
        *   **Pausa para Validación**: "La siguiente tarea es: `[Descripción de la tarea]`. Basándome en la Kata `[ID_KATA]` (o los guardrails generales), propongo crear/modificar el siguiente componente. ¿Quieres que continúe?"

    b.  **Generación/Adición de Código (Asistente)**:
        *   **Principio Fundamental**: **Siempre que sea posible, el Asistente DEBE generar nuevo código o nuevos archivos.**
        *   **Acción**: Basándose en la Kata relevante y los estándares generales, genera el código necesario para la tarea.
            *   Si la tarea implica la creación de un nuevo archivo (ej. una nueva entidad, una interfaz de repositorio, un comando, un manejador, un validador), crea el archivo con el contenido completo.
            *   Si la tarea implica **añadir funcionalidad** a un archivo existente (ej. añadir un método a una clase, añadir una propiedad a un ViewModel existente si es un ViewModel creado previamente por el agente en esta HU), el Asistente identificará la sección adecuada y **añadirá las nuevas líneas de código sin alterar las líneas existentes no creadas por él mismo en esta HU.**
        *   **Pausa para Validación**: "He generado/añadido el código para `[Nombre del componente/archivo]`. Aquí está el diff (o el contenido si es un archivo nuevo). Por favor, revísalo."
            *   Esperar la aprobación del Orquestador. "Por favor, valida los cambios. Si no estás de acuerdo, dímelo y podremos iterar."

    c.  **Manejo de Edición de Código Existente (Asistente)**:
        *   **Principio Fundamental**: Si la tarea **inevitablemente requiere modificar líneas de código existentes** que no fueron generadas por el Asistente en el contexto de esta HU (ej. cambiar una firma de método en una clase de infraestructura ya establecida, refactorizar una dependencia central), el Asistente DEBE:
            *   **Acción**: Identificar la modificación necesaria y explicar por qué es indispensable.
            *   **Pausa para Validación**: "La tarea `[Descripción de la tarea]` requeriría modificar líneas de código existentes en el archivo `[Ruta del archivo]` que no fueron generadas por mí para esta HU. Esto es indispensable porque `[Explicación]`. ¿Me das permiso para realizar esta edición? Si prefieres, puedo indicarte exactamente qué líneas sugiero cambiar para que lo hagas manualmente, o buscar una alternativa."
            *   **Espera explícita la aprobación del Orquestador para la modificación**. Si no se da permiso, el Asistente debe informarle al usuario de la consecuencia de no realizar el cambio.

    d.  **Pruebas Unitarias/Integración (Asistente)**:
        *   **Acción**: Si la tarea incluye la creación de pruebas (unitarias o de integración), genera el archivo de prueba correspondiente y el código de prueba siguiendo los guardrails `260-testing-unit-tests.mdc` y `261-testing-mocking-strategy.mdc`.
        *   **Pausa para Validación**: "He generado las pruebas para `[Nombre del componente/funcionalidad]`. Aquí está el código de las pruebas. ¿Confirmas que cubren los escenarios clave y son correctas?"

    e.  **Actualización del Plan (Asistente)**:
        *   **Acción**: Una vez que el código y las pruebas de un paso son validados y aplicados, el Asistente marcará la tarea correspondiente como completada en el Plan de Implementación Detallado.

    **Verificación:** Cada tarea del bucle tiene: (a) kata/guardrail identificado, (b) código generado y validado por el Orquestador, (c) permiso explícito si hubo edición de código existente, (d) pruebas generadas si aplica, (e) tarea marcada como completada en el plan.

    > **Si no puedes continuar:** Orquestador rechaza el código generado → Iterar con feedback específico del Orquestador hasta obtener aprobación. Si requiere edición de código existente sin permiso → Documentar la consecuencia y buscar alternativa.

3.  **Finalización del Plan (Asistente)**:
    *   **Acción**: Una vez que todas las tareas en el Plan de Implementación Detallado han sido procesadas y validadas.
    *   **Pausa para Validación**: "Todas las tareas en el Plan de Implementación Detallado han sido procesadas. ¿Hay algo más que desees que revise o ajuste?"
    *   **Confirmación**: "La implementación de la HU ha sido completada según el plan. Si hay alguna otra tarea o un nuevo plan, házmelo saber."

    **Verificación:** Todas las tareas del Plan de Implementación están marcadas como completadas y el Orquestador ha confirmado que no hay ajustes pendientes.

    > **Si no puedes continuar:** Tareas pendientes en el plan → Regresar al paso 2 para completar las tareas faltantes antes de declarar la HU como implementada.