# L2-07 - Kata de Validación Técnica de Dependencias

## 1. Propósito

Esta Kata de Nivel 2 (L2) define el proceso para realizar un **Spike Técnico** o **Análisis de Viabilidad Arquitectónica** sobre las dependencias de una nueva Historia de Usuario (HU).

El objetivo es moverse más allá de la documentación de alto nivel y utilizar el **código fuente y los contratos de servicio como la fuente de verdad absoluta**. Esto permite validar suposiciones, identificar riesgos (como latencia en cascada o dependencias ocultas) y definir con precisión cómo se interactuará con los servicios existentes antes de escribir una sola línea de código de la nueva funcionalidad.

## 2. ¿Cuándo Usar esta Kata?

Se debe utilizar esta Kata durante la fase de **Planificación y Diseño** de una HU, específicamente cuando la nueva funcionalidad dependa de la comunicación con uno o más microservicios o APIs externas existentes.

## 3. Principios Estratégicos

- **No Asumir, Descubrir:** Nunca asumas que la estructura de un repositorio es idéntica a otra. Cada servicio debe ser tratado como un sistema a explorar.
- **Búsqueda Directa sobre Navegación:** Prioriza el uso de herramientas de búsqueda (`file_search`, `grep_search`) para localizar archivos y artefactos clave. Usa `list_dir` solo como último recurso o para exploración general.
- **El Código como Fuente de Verdad:** Los contratos documentales son el punto de partida, pero el código fuente es la autoridad final sobre el comportamiento y las dependencias internas.

## 4. Entradas

- **ID de la HU:** El identificador de la Historia de Usuario a analizar (ej. `HU-006`).
- **Documentación de Diseño Inicial:** Diagramas de arquitectura, `tech-design.md`, `ecosystem-analysis.md`, etc.
- **Lista de Dependencias Sospechadas:** Una lista de los servicios que se cree que la nueva HU necesita consumir (ej. `raise-jf-backend-profile`).

## 5. Proceso de Validación (Por cada Dependencia)

Este proceso debe repetirse para cada servicio externo identificado como una dependencia.

### Fase 1: Validación Documental y de Contratos

**Paso 5.1: Validar la Responsabilidad del Servicio**

- **Acción:** Localiza y analiza el archivo `service-overview.md` de la dependencia.
- **Objetivo:** Confirmar que el propósito declarado del servicio se alinea con las necesidades de nuestra HU. ¿Es realmente el "dueño" de la funcionalidad que buscamos?

**Paso 5.2: Validar el Contrato de Comunicación**

- **Acción:** Localiza y analiza el archivo de contrato del servicio (ej. `inter-service-contracts.yaml`, o los archivos `.proto` en la carpeta `/Protos`).
- **Objetivo:** Identificar los métodos exactos (gRPC/REST) que se deben consumir, junto con sus parámetros de solicitud y los objetos de respuesta.

### Fase 2: Validación de Código Fuente (Análisis Forense)

**Paso 5.3: Realizar Análisis de Dependencia Inversa**

- **Acción:**
  1. **Localizar el Punto de Entrada (Controlador/Servicio gRPC):**
     - Utiliza `file_search` para encontrar el archivo que implementa el contrato. Patrones comunes: `*ServiceV1.cs`, `*Controller.cs`.
     - Si falla, usa `grep_search` para buscar el nombre de un método del contrato (ej. `GetCreditCode`) en todos los archivos `.cs` de la capa de Presentación/API.
  2. **Identificar el CQRS Trigger:**
     - Lee el archivo del controlador/servicio. Localiza el método del contrato y busca la línea `mediator.Send(new TheQueryOrCommand(...))`. Anota el nombre de `TheQueryOrCommand`.
  3. **Localizar el Handler de CQRS:**
     - Utiliza `file_search` para encontrar el archivo del handler correspondiente: `TheQueryOrCommandHandler.cs`.
  4. **Analizar las Dependencias del Handler:**
     - Lee el archivo del handler e inspecciona las dependencias inyectadas en su constructor.
- **Objetivo:** Responder a la pregunta crítica: "**Cuando llamamos a este servicio, ¿él a su vez llama a otros microservicios?**".
- **Veredicto:**
  - **Operación Autocontenida:** Si las dependencias son solo Repositorios (`IRepository`) y Mappers (`IMapper`). La cadena de llamadas termina en la base de datos local.
  - **Dependencia Oculta:** Si las dependencias incluyen Clientes gRPC o HTTP (`SomeServiceClient`, `HttpClient`). Esto es un riesgo que debe ser documentado.

**Paso 5.4: (Opcional) Validar la Implementación de Persistencia**

- **Acción:**
  1. Si el handler depende de una interfaz de repositorio (ej. `ICreditDataRepositoryAsync`), busca su implementación (`CreditDataRepositoryAsync.cs`) usando `file_search`.
  2. Lee la implementación y busca la entidad del dominio sobre la que opera (ej. `GenericRepositoryAsync<CreditData>`).
- **Objetivo:** Confirmar la **tabla exacta** (`CreditData`) y los **campos** que se consultan en la base de datos para facilitar la validación manual por parte del desarrollador.

### Fase 3: Verificación Manual en Base de Datos (Paso Humano)

**Paso 5.5: Verificación Manual de Esquema y Datos**
- **Rol:** Desarrollador Humano.
- **Acción:**
    1.  Tomar la información de `tabla` y `campos` identificada en el `Paso 5.4`.
    2.  Conectarse directamente a la base de datos del servicio analizado.
    3.  Ejecutar consultas (`SELECT`, `DESCRIBE TABLE`, etc.) para confirmar que la tabla y los campos existen.
    4.  Inspeccionar los datos de ejemplo para validar que su contenido y formato coinciden con las expectativas del análisis.
- **Objetivo:** Confirmar que la "fuente de verdad" (la base de datos) se corresponde con lo que se ha deducido del código fuente. Esto valida la corrección del análisis del agente y previene errores debidos a desajustes entre el código y el estado real de la base de datos.

## 6. Salidas (Artefactos Generados)

- **Actualización del Documento de Descripción de la HU:** La sección de `Dependencias` y `Contratos de Comunicación` del documento principal de la HU (ej. `HU-006_description.md`) debe ser enriquecida con los hallazgos:
  - Nombres reales y completos de los servicios a consumir.
  - Métodos gRPC/REST específicos que se utilizarán, validados desde los contratos.
  - Un resumen del análisis de dependencia inversa, incluyendo la **cadena de archivos analizada (Controlador -> Handler -> Repositorio)** y confirmando si las llamadas son autocontenidas.
- **Veredicto de Viabilidad:** Una conclusión clara sobre si las dependencias existentes soportan los requisitos de la HU.
