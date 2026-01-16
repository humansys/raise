# L2-02: Inicialización de Documentos de Gobernanza para Reglas Cursor

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 detalla los pasos para crear o inicializar los documentos fundamentales de gobernanza para el sistema de Reglas Cursor de un proyecto. Estos documentos son esenciales para mantener un registro del razonamiento, la estructura y el plan de desarrollo de las reglas.

## 2. Alcance y Objetivos

*   Crear la estructura de directorios necesaria para los documentos de gobernanza si no existe.
*   Inicializar el archivo `ai-rules-reasoning.md` con una introducción y las observaciones preliminares del análisis exploratorio.
*   Inicializar el archivo `[nombre-repo]-rules-index.md` con una estructura de categorías base.
*   Inicializar el archivo `[nombre-repo]-implementation-plan.md` con las fases generales del plan de establecimiento de reglas.

## 3. Prerrequisitos

*   Haber completado la Sub-Kata `L2-01-analisis-exploratorio-repositorio.md` y tener disponible su entregable (Informe de Análisis Exploratorio).
*   Agente IA configurado con la herramienta `edit_file`.
*   Conocimiento de la estructura estándar y propósito de los documentos de gobernanza (o acceso a plantillas genéricas para ellos).
*   El nombre del repositorio (`[nombre-repo]`) debe ser conocido para nombrar los archivos correctamente.

## 4. Pasos Detallados para la Inicialización

### Paso 4.1: Preparación de Directorios

*   **Acción**: Verificar la existencia del directorio `.raise/docs/[nombre-repo]/`. Si no existe, créarlo.
    *   El `[nombre-repo]` debe ser reemplazado por el nombre real del repositorio que se está analizando (ej. `jf-backend-profile`).
*   **Herramienta**: Implícito (el agente debe ser capaz de crear archivos en rutas especificadas, lo que puede implicar la creación de directorios si la herramienta `edit_file` lo soporta o si se usa una herramienta `create_dir` si estuviera disponible).

### Paso 4.2: Inicialización del Documento de Razonamiento (`ai-rules-reasoning.md`)

*   **Acción**: Crear el archivo `.raise/docs/[nombre-repo]/ai-rules-reasoning.md`.
*   **Contenido Inicial**:
    *   **Título**: `Documentación de Razonamiento de Reglas de IA para el Proyecto [nombre-repo]`
    *   **Sección: Introducción**
        *   Párrafo breve explicando el propósito del documento (explicar el "por qué" de las reglas, el proceso de descubrimiento, etc., similar a lo que hemos hecho para `jf-backend-profile`).
    *   **Sección: Estado Inicial del Repositorio y Observaciones Preliminares**
        *   Incorporar el contenido del "Informe de Análisis Exploratorio del Repositorio" (entregable de `L2-01-analisis-exploratorio-repositorio.md`).
        *   Este incluye: Tecnologías principales, estructura general, patrones arquitectónicos preliminares, y otras observaciones relevantes.
    *   **Sección: Catálogo de Reglas Generadas y su Razonamiento**
        *   Dejar esta sección vacía inicialmente, con un comentario indicando que se poblará a medida que se creen las reglas.
*   **Herramienta**: `edit_file`

### Paso 4.3: Inicialización del Índice de Reglas (`[nombre-repo]-rules-index.md`)

*   **Acción**: Crear el archivo `.raise/docs/[nombre-repo]/[nombre-repo]-rules-index.md`.
*   **Contenido Inicial**:
    *   **Título**: `Índice de Reglas de IA para [nombre-repo]`
    *   **Sección: ¿Qué son las Reglas de IA?** (Explicación breve).
    *   **Sección: Cómo Usar este Índice**.
    *   **Sección: Estructura de Categorías y Reglas**
        *   Definir las categorías base que se usarán (ej. las que definimos en `902-rule-precedence.mdc` para `jf-backend-profile`):
            *   Principios Fundamentales y Metodología (000-099)
            *   Estándares Tecnológicos Generales (100-199)
            *   Patrones de Arquitectura y Diseño de Componentes (200-399)
            *   (Otras categorías específicas si se prevén, ej. Pruebas 400-499)
            *   Meta-Reglas (900-999)
        *   Para cada categoría, mostrar una tabla vacía (o con un placeholder `*Por definir*`) lista para ser poblada con las reglas.
    *   **Sección: Guía para Desarrolladores y Usuarios de IA** (Placeholder).
    *   **Sección: Recursos Adicionales** (Enlaces al plan de implementación y al documento de razonamiento).
*   **Herramienta**: `edit_file`

### Paso 4.4: Inicialización del Plan de Implementación (`[nombre-repo]-implementation-plan.md`)

*   **Acción**: Crear el archivo `.raise/docs/[nombre-repo]/[nombre-repo]-implementation-plan.md`.
*   **Contenido Inicial**:
    *   **Título**: `Plan de Implementación de Reglas de IA para [nombre-repo]`
    *   **Sección: Resumen Ejecutivo** (Propósito del plan).
    *   **Sección: Fases de Implementación**
        *   **Fase 1: Preparación y Fundamentos** (Detallar los pasos iniciales que esta Kata y la L2-01 cubren, marcándolos como en progreso o completados).
            *   Análisis de Estructura y Categorización de Reglas.
            *   Disponibilidad y Análisis de Plantillas de Reglas.
            *   Análisis de Código Existente y Prácticas Actuales (resultado de L2-01).
            *   Creación de un Conjunto Inicial de Documentación de Gobernanza (esta misma sub-kata L2-02).
        *   **Fase 2: Desarrollo Iterativo y Expansión de Reglas** (Placeholder para listar las reglas a crear).
        *   **Fase 3: Establecimiento de Reglas Fundacionales y Meta-Reglas** (Placeholder).
        *   **Fase 4: Mantenimiento, Refinamiento y Evolución Continua** (Placeholder).
    *   **Sección: Próximos Pasos Inmediatos** (Apuntar a la Fase 3 de la Kata Principal: `L2-04-establecimiento-reglas-estandares-generales.md`).
    *   **Sección: Conclusión**.
*   **Herramienta**: `edit_file`

## 5. Entregables de esta Sub-Kata

*   Archivo `.raise/docs/[nombre-repo]/ai-rules-reasoning.md` creado e inicializado.
*   Archivo `.raise/docs/[nombre-repo]/[nombre-repo]-rules-index.md` creado e inicializado.
*   Archivo `.raise/docs/[nombre-repo]/[nombre-repo]-implementation-plan.md` creado e inicializado.

## 6. Consideraciones Adicionales

*   Si el proyecto ya tiene alguno de estos documentos, esta Kata debe enfocarse en actualizarlos con la información más reciente del análisis exploratorio, en lugar de sobrescribirlos.
*   Los placeholders `[nombre-repo]` deben ser sustituidos por el nombre real del repositorio.
*   Se pueden usar plantillas genéricas para estos documentos si están disponibles, adaptándolas según sea necesario.

## 7. Próximos Pasos (según Kata Principal)

*   Proceder con la Fase 3 de `L0-01-gestion-integral-reglas-cursor.md`: `L2-04-establecimiento-reglas-estandares-generales.md` (Establecimiento de Reglas Fundacionales). 