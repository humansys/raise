# L1-10: Kata de Alineamiento con Convenciones del Repositorio

**Autor:** `raise-continuous-improvement-agent`
**Categoría:** Proceso y Cultura
**Propósito:** Instaurar el hábito fundamental de **verificar antes de codificar**. Esta Kata obliga al desarrollador (o al agente IA) a utilizar el código base existente como la única fuente de verdad para las convenciones de codificación, patrones arquitectónicos y uso de API, antes de escribir una nueva línea de código. Su objetivo es erradicar los errores basados en asunciones falsas.

---

## Principio Fundamental: El Código Existente es la Documentación Viva

En un proyecto maduro, los patrones correctos ya están implementados. Asumir cómo funciona un componente, un claim de un token o la firma de un método es la causa raíz de errores costosos y refactorizaciones innecesarias.

**Esta Kata debe ejecutarse al inicio de la implementación de cualquier nuevo componente o funcionalidad (Controlador, Handler, Servicio, Test, etc.).**

---

## Pasos de la Kata

### Paso 1: Identificar el Arquetipo

Antes de crear un nuevo archivo (ej. `NewFeatureController.cs`), identifica uno o dos archivos existentes del mismo tipo que sean representativos de la funcionalidad estándar del proyecto.

- **Para un nuevo Controlador:** `CartController.cs`, `OrderCaptureController.cs`.
- **Para un nuevo Handler de CQRS:** Cualquier `...QueryHandler.cs` o `...CommandHandler.cs` en una feature similar.
- **Para una nueva Prueba Unitaria:** Cualquier archivo `...Tests.cs` en el proyecto de pruebas.
- **Para un nuevo Servicio de Infraestructura:** `ProfileServiceAsync.cs`.

### Paso 2: Extraer las Convenciones Clave (Checklist de Verificación)

Abre el archivo arquetipo y responde a las siguientes preguntas. Esta no es una revisión superficial; es una inspección para extraer reglas concretas.

**Para Controladores (`...Controller.cs`):**
-   [ ] **Identidad del Usuario:** ¿Cómo se obtiene la identidad del usuario? ¿Se usa `User.GetUserId()` (que devuelve `int`) o se busca un claim específico con `User.FindFirstValue("claim_name")`?
    -   *Lección de HU-006: Se evitó la "alucinación" del `user_code`.*
-   [ ] **Atributos de API:** ¿Qué atributos de `[Produces(...)]` se usan a nivel de clase o método? ¿Es `[Produces(MediaTypeNames.Application.Json)]` un estándar?
    -   *Lección de HU-006: Se evitó el error `406 Not Acceptable`.*
-   [ ] **Manejo de Respuestas:** ¿Cómo se devuelven los errores? ¿Se usan `Ok(response)`, `UnauthorizedObjectResult(response)`, `BadRequest(response)`?
-   [ ] **Inyección de Dependencias:** ¿Qué se inyecta en el constructor? ¿Es solo `IMediator`?

**Para Handlers de CQRS (`...Handler.cs`):**
-   [ ] **Inyección de Dependencias:** ¿Qué dependencias se inyectan? ¿Son **interfaces** de servicio (`I...ServiceAsync`) o clientes gRPC concretos?
    -   *Lección de HU-006: Se evitó la violación catastrófica de la Clean Architecture.*
-   [ ] **Orden de Dependencias:** ¿Hay un orden estándar para los parámetros del constructor (ej. servicios de dominio, luego `IMapper`, `ILogger` al final)?

**Para Pruebas Unitarias (`...Tests.cs`):**
-   [ ] **Librería de Aserción:** ¿Se usa `Xunit.Assert` o `FluentAssertions`?
    -   *Lección de HU-006: Se evitó introducir `FluentAssertions` y se mantuvo el estándar `Xunit`.*
-   [ ] **Estructura del Test:** ¿Se sigue el patrón Arrange-Act-Assert? ¿Cómo se nombran los tests?
-   [ ] **Verificación de Respuestas:** ¿Cómo se comprueba si una operación fue exitosa? ¿Se verifica `response.Succeeded` o `response.Status == "success"`?
-   [ ] **Mocks:** ¿Cómo se configuran los mocks? ¿Qué librerías se usan (`Moq`)?

**Para Servicios (`...Service.cs`):**
-   [ ] **Contrato de Interfaz:** ¿El método de la interfaz (`I...ServiceAsync`) devuelve el objeto de respuesta gRPC (ej. `Task<GetUserDataResponse>`) o un `Response<T>` genérico?
    -   *Lección de HU-002: Se entendió que los servicios devuelven el payload crudo, y los handlers lo envuelven.*
-   [ ] **Manejo de Errores:** ¿Cómo se manejan las `RpcException`? ¿Se capturan y se relanzan como una `ApiException`?

### Paso 3: Aplicar las Convenciones Extraídas

Con las respuestas del checklist, procede a escribir el nuevo código, aplicando rigurosamente las convenciones y patrones identificados. Cualquier desviación debe ser consciente y justificada, no producto de una asunción.

---

## Resultado Esperado

Al completar esta Kata, el nuevo código estará naturalmente alineado con el resto del proyecto. Se reducirán drásticamente los errores de lógica, de convención y de arquitectura, y se eliminarán las refactorizaciones extensas causadas por suposiciones incorrectas. Esta práctica fomenta la consistencia y la mantenibilidad del código base. 