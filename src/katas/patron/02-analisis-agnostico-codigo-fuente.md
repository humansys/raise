---
id: L2-02-analisis-agnostico-codigo-fuente
nivel: 2
tags: [arquitectura, documentacion, analisis-estatico, agnostico]
---
# L2-02: Análisis de Código Fuente para Documentación Esencial Agnóstico a la Pila Tecnológica

## Metadatos
- **Id**: L2-02-analisis-agnostico-codigo-fuente
- **Nivel**: 2
- **Título**: Análisis de Código Fuente para Documentación Esencial Agnóstico a la Pila Tecnológica
- **Propósito**: Formalizar un proceso genérico para analizar cualquier base de código, independientemente de la tecnología, con el fin de extraer la información crítica necesaria para generar una documentación de arquitectura, resiliencia y diseño que sea accionable y esté siempre actualizada.
- **Contexto**: Se aplica al incorporar un nuevo repositorio al ecosistema, antes de iniciar un refactor importante, o como paso previo a Katas de diseño de features (como L1-08 o L1-09) cuando la documentación esencial no existe.
- **Audiencia**: Arquitecto de Software, Líder Técnico, Desarrollador Senior.

## Pre-condiciones
- Acceso completo al código fuente del repositorio o servicio a analizar.
- Comprensión del paradigma arquitectónico general del sistema (ej. microservicios, monolito, serverless).
- Un objetivo definido para la documentación a generar (ej. "preparar para un nuevo feature", "evaluar la deuda técnica", "facilitar el onboarding").

## Pasos de la Kata

Esta Kata se estructura en fases que van desde una vista de alto nivel hasta los detalles de implementación, asegurando una comprensión completa y estructurada del código.

### Fase 1: Descubrimiento de la Superficie de la API (API Surface Discovery)

El objetivo de esta fase es identificar cómo el servicio se comunica con el mundo exterior.

#### Paso 1.1: Identificar Puntos de Entrada (Endpoints)
- **Acción**: Analizar el código para localizar todos los puntos de entrada públicos que exponen la funcionalidad del servicio. Esto incluye, pero no se limita a, controladores REST, definiciones de servicios gRPC, suscriptores a colas de mensajes, funciones serverless, sockets, etc.
- **Criterios de Aceptación**:
  - Se genera una lista completa de todos los puntos de entrada.
  - Cada entrada especifica su tipo (ej. `REST`, `gRPC`, `MessageConsumer`), ruta/nombre y los métodos/operaciones que soporta.

#### Paso 1.2: Definir Contratos de Datos (Data Contracts)
- **Acción**: Para cada punto de entrada, identificar los objetos de solicitud (request) y respuesta (response). Documentar la estructura de estos objetos, sus campos, tipos de datos y las validaciones aplicadas (ej. opcionalidad, rangos, patrones).
- **Criterios de Aceptación**:
  - Se produce un documento (`contracts.md` o `contracts.yaml`) que define formalmente los modelos de datos de la API pública.
  - Se identifican y documentan los modelos de datos que se reutilizan en múltiples endpoints.

### Fase 2: Análisis de Dependencias y Colaboraciones

Esta fase se enfoca en entender cómo el servicio interactúa con otros componentes del ecosistema.

#### Paso 2.1: Mapear Dependencias Salientes (Egress Dependencies)
- **Acción**: Rastrear el código para identificar todas las llamadas a servicios externos. Buscar el uso de clientes HTTP, clientes gRPC, SDKs de servicios de terceros, publicadores de mensajes y cualquier otro mecanismo de comunicación saliente.
- **Criterios de Aceptación**:
  - Se genera un mapa de dependencias (`dependencies.yaml`) que lista cada servicio externo contactado.
  - Para cada dependencia, se especifica el tipo de comunicación, el propósito de la interacción y la criticidad percibida (ej. `ALTA`, `MEDIA`, `BAJA`).

#### Paso 2.2: Identificar Dependencias de Infraestructura
- **Acción**: Analizar los archivos de configuración (`appsettings.json`, `docker-compose.yml`, etc.) y el código de inicialización para identificar las dependencias de infraestructura. Esto incluye bases de datos, sistemas de caché, proveedores de almacenamiento de objetos, message brokers, etc.
- **Criterios de Aceptación**:
  - La sección de dependencias se completa con una lista de todos los componentes de infraestructura requeridos.
  - Se documenta el propósito de cada componente de infraestructura (ej. "persistencia principal", "caché de sesión").

### Fase 3: Análisis de Lógica de Negocio y Resiliencia

El núcleo de la Kata: entender qué hace el servicio y cómo sobrevive a fallos.

#### Paso 3.1: Extraer Conceptos del Dominio (Domain Concepts)
- **Acción**: Analizar las capas de negocio o dominio del código para identificar las entidades, agregados y objetos de valor que modelan el problema de negocio. Buscar las clases o estructuras de datos que representan el corazón de la lógica de negocio.
- **Criterios de Aceptación**:
  - Se genera un resumen del modelo de dominio (`domain-model.md`) que lista y describe los conceptos clave.
  - Se identifican y documentan las "invariantes" o reglas de negocio críticas encontradas en el código.

#### Paso 3.2: Detectar Patrones de Resiliencia y Manejo de Errores
- **Acción**: Realizar una búsqueda sistemática de patrones de manejo de errores y resiliencia. Esto incluye bloques `try/catch`, políticas de reintento (`retry`), patrones `circuit breaker`, `timeouts` configurados y manejo de transacciones. Identificar tanto buenas prácticas como anti-patrones (ej. "exception swallowing", logs genéricos).
- **Criterios de Aceptación**:
  - Se crea una `resilience-guide.md` que documenta los patrones de resiliencia implementados.
  - Se lista cualquier anti-patrón detectado, idealmente con una referencia a su ubicación en el código.

#### Paso 3.3: Mapear Casos de Uso de Negocio
- **Acción**: Conectar los puntos de entrada (Paso 1.1) con la lógica de negocio que orquestan. El objetivo es traducir cada endpoint técnico a una capacidad de negocio clara y concisa.
- **Criterios de Aceptación**:
  - Se genera un documento de casos de uso (`use-cases.md`) que describe en lenguaje de negocio lo que hace cada endpoint.
  - Se establece una trazabilidad clara entre la API pública y la lógica de dominio que la soporta.

### Fase 4: Síntesis y Generación de Documentación

En esta fase final, se consolida toda la información recopilada en artefactos de documentación accionables.

#### Paso 4.1: Ensamblar el Documento de Visión General del Servicio (`service-overview.md`)
- **Acción**: Consolidar la información de las fases anteriores en un único documento de alto nivel. Este documento debe responder de forma concisa: ¿qué es este servicio?, ¿qué hace?, ¿con quién habla? y ¿cuáles son sus responsabilidades principales?
- **Criterios de Aceptación**:
  - Se produce el `service-overview.md` final, que sirve como el principal punto de entrada para entender el servicio en menos de 5 minutos.
  - El documento incluye un resumen del propósito, el bounded context, las dependencias críticas y el modelo de dominio.

#### Paso 4.2: Formalizar y Versionar los Artefactos de Documentación
- **Acción**: Generar los artefactos detallados finales (`contracts.md`, `dependencies.yaml`, `resilience-guide.md`, etc.) en un formato limpio y estructurado. Añadir metadatos como la fecha de generación y el commit de código analizado.
- **Criterios de Aceptación**:
  - Todos los documentos de salida están completos, son consistentes y están listos para ser almacenados en un sistema de control de versiones junto al código.

#### Paso 4.3: Crear un README para la Documentación Generada
- **Acción**: Crear un archivo `README.md` en el directorio raíz donde se almacena la documentación generada. Este archivo debe explicar brevemente el propósito de la Kata y describir qué información contiene cada uno de los artefactos generados (`service-overview.md`, `contracts.md`, etc.), proporcionando una guía para el lector.
- **Criterios de Aceptación**:
  - Se genera un archivo `README.md` en la carpeta de la documentación.
  - El `README.md` incluye una tabla de contenidos o lista que describe cada documento y enlaza a él.

## Post-condiciones
- Un conjunto de documentos estructurados y un `README.md` guía que describen los aspectos clave del código analizado (API, dependencias, dominio, resiliencia).
- Una base de conocimiento "viva" que puede ser regenerada para reflejar los cambios en el código fuente.
- Información de alta calidad lista para ser consumida por otras Katas de diseño, para alimentar un sistema RAG (Retrieval-Augmented Generation) o para facilitar el onboarding de nuevos miembros al equipo.

## Notas Adicionales
- **Automatización**: Este proceso está diseñado para ser automatizado. Se deben favorecer herramientas de análisis estático de código (linters, parsers de AST, etc.) sobre la inspección manual para garantizar la consistencia y la capacidad de regeneración.
- **Contexto vs. Código**: La documentación generada debe ser un reflejo fiel del código. Evitar añadir interpretaciones o funcionalidades "deseadas" que no estén presentes en la implementación actual.
- **Minimalismo Estratégico**: Al igual que en `L1-07`, la documentación debe ser ultra-compacta pero técnicamente precisa. El objetivo no es generar cientos de páginas, sino la mínima información viable para prevenir errores y facilitar el desarrollo.
- **Planes de Implementación**: Al crear un plan de implementación para ejecutar esta Kata en un proyecto específico, se recomienda un enfoque de análisis archivo por archivo, especialmente para proyectos de tamaño pequeño a mediano. Sin embargo, el método debe ser flexible y adaptarse al tamaño y complejidad del proyecto.

