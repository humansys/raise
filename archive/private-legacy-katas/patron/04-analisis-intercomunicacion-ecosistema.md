---
id: L2-04-analisis-intercomunicacion-ecosistema-agnostico
nivel: 2
tags: [arquitectura, analisis, ecosistema, agnostico, dependencias, acoplamiento]
---
# L2-04: Análisis de Intercomunicación del Ecosistema Agnóstico

## Metadatos

- **Id**: L2-04-analisis-intercomunicacion-ecosistema-agnostico
- **Nivel**: 2
- **Título**: Análisis de Intercomunicación del Ecosistema Agnóstico
- **Propósito**: Realizar un análisis proactivo y tecnológicamente agnóstico de un ecosistema de software para mapear, visualizar y validar todas las interacciones entre sus componentes. El objetivo es crear una "radiografía" arquitectónica viva, utilizando el código fuente como la máxima autoridad.
- **Contexto**: Se aplica para realizar "chequeos de salud" arquitectónicos, facilitar el onboarding de nuevos desarrolladores, planificar refactorizaciones estratégicas, o simplemente para tener una comprensión clara y validada del acoplamiento y las dependencias del sistema en un momento dado. No requiere de un nuevo feature como disparador.
- **Audiencia**: Arquitecto de Software, Líder Técnico, Desarrollador Senior.

## Pre-condiciones

- **Artefactos de `L2-02` generados**: La Kata `L2-02-Analisis-Agnostico-Codigo-Fuente` ha sido ejecutada para todos los módulos o servicios que componen el ecosistema a analizar. Se debe contar con el directorio de documentación (`service-overview.md`, `dependencies.yaml`, etc.) de cada componente.

## Principio Fundamental: "El Código es la Verdad, la Documentación es el Mapa"

Los artefactos generados por `L2-02` nos proporcionan un excelente mapa inicial del ecosistema. Sin embargo, la verdad última sobre las interacciones reside únicamente en el código fuente. Esta Kata utiliza el mapa para guiar la exploración, pero confía solo en el territorio (el código) para sus conclusiones finales.

## Pasos de la Kata

### Fase 1: Consolidación y Mapeo Inicial Basado en Documentación

#### Paso 1.1: Centralizar Artefactos del Ecosistema

- **Acción**: Recopilar los artefactos `dependencies.yaml` de cada módulo analizado en un directorio de trabajo centralizado para este análisis.
- **Criterios de Aceptación**:
  - Se crea una estructura de directorios (`.raise/analysis/ecosystem-intercom/artifacts/`) que contiene una copia de los archivos `dependencies.yaml` de cada módulo.

#### Paso 1.2: Construir la Matriz de Interacción Documentada

- **Acción**: Procesar automáticamente (mediante un script o manualmente) todos los archivos `dependencies.yaml`. Para cada dependencia saliente listada en el archivo de un módulo, crear una fila en una matriz que registre la interacción documentada.
- **Criterios de Aceptación**:
  - Se genera un artefacto `interaction-matrix-documented.md`.
  - La matriz contiene las columnas: `Módulo Emisor`, `Módulo Receptor`, `Propósito (Según Documentación)`.

#### Paso 1.3: Generar el Grafo de Dependencias Inicial

- **Acción**: Utilizar la matriz de interacción documentada para generar una visualización del ecosistema. Emplear una herramienta como Mermaid para crear un grafo de dependencias que muestre qué módulos se comunican con qué otros, según la documentación.
- **Criterios de Aceptación**:
  - Se genera un artefacto `dependency-graph-initial.md` que contiene el diagrama de Mermaid.
  - El grafo proporciona una primera vista de alto nivel de las relaciones documentadas.

### Fase 2: Validación Profunda contra el Código Fuente

#### Paso 2.1: Verificación Cruzada de Interacciones (Paso Clave)

- **Acción**: Iterar sobre cada fila de la `interaction-matrix-documented.md`. Para cada interacción `Emisor -> Receptor`, realizar una búsqueda dirigida dentro del código fuente del `Módulo Emisor`. El objetivo es encontrar la implementación real de la llamada (ej. uso de un cliente HTTP, una llamada gRPC, un SDK específico). Las pistas para la búsqueda se encuentran en los archivos de configuración y en el propio código del emisor.
- **Criterios de Aceptación**:
  - Se crea una nueva matriz, `interaction-matrix-validated.md`.
  - Esta matriz incluye una columna adicional: `Estado de Validación`, con posibles valores:
    - `VALIDADO`: La interacción documentada fue encontrada en el código.
    - `NO ENCONTRADO`: La interacción está en la documentación (`dependencies.yaml`) pero no se encontró una llamada correspondiente en el código (indica posible configuración obsoleta o código muerto).
  - Durante la búsqueda, si se encuentran llamadas a otros módulos que **no** estaban en la documentación, se añaden nuevas filas a la matriz con el estado `NO DOCUMENTADO`.

### Fase 3: Síntesis y Análisis Arquitectónico

#### Paso 3.1: Generar Artefactos Finales y Visualización Validada

- **Acción**: Utilizar la `interaction-matrix-validated.md` como la fuente de verdad final para generar los artefactos de salida. Actualizar el grafo de dependencias de Mermaid para que refleje únicamente las interacciones validadas y las no documentadas que se descubrieron.
- **Criterios de Aceptación**:
  - Se produce el `dependency-graph-final.md`, que representa el estado real de las intercomunicaciones.
  - La matriz `interaction-matrix-validated.md` se considera un entregable clave, detallando cada interacción y su estado de validación.

#### Paso 3.2: Producir el Informe de Análisis Arquitectónico

- **Acción**: Con los artefactos validados en mano, el arquitecto o líder técnico debe analizar los resultados y redactar un informe que resuma la salud y estructura del ecosistema.
- **Criterios de Aceptación**:
  - Se genera un documento `architectural-analysis.md` que contiene:
    - **Resumen Ejecutivo**: Principales hallazgos en pocas líneas.
    - **Hallazgos Arquitectónicos Clave**:
      - **Módulos "Hub"**: Identificación de componentes centrales con un alto grado de entrada/salida de llamadas.
      - **Cadenas de Llamadas Críticas**: Secuencias de llamadas (A -> B -> C...) que pueden representar puntos de fragilidad o alta latencia.
      - **Dependencias Circulares**: Detección de patrones de acoplamiento problemáticos (ej. A llama a B y B a su vez llama a A, directa o indirectamente).
      - **Módulos Aislados**: Componentes con baja o nula interacción.
    - **Informe de Discrepancias**: Una lista de todas las interacciones con estado `NO ENCONTRADO` o `NO DOCUMENTADO`, que deben ser investigadas para limpiar la configuración o mejorar la documentación base de `L2-02`.
    - **Recomendaciones Accionables**: Sugerencias concretas basadas en los hallazgos (ej. "Evaluar la posibilidad de desacoplar el Módulo X usando eventos", "Investigar la dependencia circular entre A y B").

## Post-condiciones

- Un conjunto de artefactos que representan el estado real y validado de las intercomunicaciones del ecosistema: un grafo visual (`dependency-graph-final.md`) y una matriz detallada (`interaction-matrix-validated.md`).
- Un informe de análisis (`architectural-analysis.md`) que no solo describe el estado actual, sino que también identifica riesgos, patrones problemáticos y oportunidades de mejora arquitectónica.
- Un punto de partida fiable y basado en evidencia para tomar decisiones de diseño, refactorización y estrategia técnica a largo plazo.

## Notas Adicionales

- **Iteración**: Este proceso no es de una sola vez. Se recomienda ejecutar esta Kata periódicamente (ej. cada trimestre o antes de un ciclo de planificación importante) para detectar derivas arquitectónicas.
- **Automatización Parcial**: Mientras que el análisis final requiere juicio humano, la generación de la matriz documentada y el grafo inicial (Fase 1) pueden y deben ser automatizados mediante scripts para acelerar el proceso.
- **Valor Cultural**: La ejecución regular de esta Kata fomenta una cultura de conciencia arquitectónica en el equipo, haciendo que el acoplamiento y las dependencias sean visibles y un tema de conversación constante.
