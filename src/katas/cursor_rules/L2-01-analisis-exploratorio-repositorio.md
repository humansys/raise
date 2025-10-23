# L2-01: Análisis Exploratorio del Repositorio para Reglas Cursor

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 detalla los pasos para realizar un análisis exploratorio inicial de un repositorio de código fuente. El objetivo es obtener una comprensión de alto nivel de las tecnologías utilizadas, la estructura del proyecto, y los patrones arquitectónicos o de codificación más evidentes. Esta información servirá como base para la creación de Reglas Cursor y la documentación de razonamiento.

## 2. Alcance y Objetivos

*   Identificar los principales lenguajes de programación, frameworks y librerías significativas.
*   Describir la estructura general de directorios y la organización del proyecto.
*   Detectar patrones arquitectónicos de alto nivel (ej. Monolito, Microservicios, Arquitectura Limpia, MVC).
*   Identificar convenciones de nomenclatura de archivos y directorios si son obvias.
*   Producir un resumen inicial que alimentará el documento `ai-rules-reasoning.md`.

## 3. Prerrequisitos

*   Acceso completo de lectura al repositorio de código fuente.
*   Agente IA configurado con herramientas de introspección de código: `list_dir`, `read_file`, `grep_search`.
*   Conocimiento de la Fase 0 de la Kata Principal `L0-01-gestion-integral-reglas-cursor.md` (Preparación del Agente).

## 4. Pasos Detallados de la Exploración

### Paso 4.1: Listado Inicial y Exploración de la Raíz del Repositorio

*   **Acción**: Ejecutar `list_dir` en el directorio raíz del repositorio.
*   **Observaciones a Registrar**:
    *   Presencia de archivos de gestión de dependencias (ej. `package.json`, `pom.xml`, `requirements.txt`, `*.csproj`, `*.sln`).
    *   Presencia de archivos de configuración de Docker (ej. `Dockerfile`, `docker-compose.yml`).
    *   Presencia de archivos de CI/CD (ej. `.github/workflows/`, `Jenkinsfile`, `azure-pipelines.yml`).
    *   Directorios principales comunes (ej. `src/`, `source/`, `app/`, `tests/`, `docs/`, `scripts/`, `database/`).
    *   Archivos de README o documentación principal en la raíz.
*   **Herramienta**: `list_dir`

### Paso 4.2: Identificación de Tecnologías Principales

*   **Acción**: Basado en los archivos identificados en el Paso 4.1 (y re-lectura de algunos si es necesario), determinar los lenguajes y frameworks principales.
    *   Leer el contenido de archivos de gestión de dependencias para identificar librerías clave.
    *   Ejecutar `grep_search` para buscar palabras clave de tecnologías comunes si no es obvio (ej. `React`, `Spring Boot`, `Django`, `ASP.NET Core`, `Entity Framework`).
*   **Observaciones a Registrar**:
    *   Lenguaje(s) de programación principal(es).
    *   Framework(s) principal(es) (backend, frontend, etc.).
    *   Motores de base de datos (si se infiere de ORMs o scripts).
    *   Tecnologías de testing principales.
*   **Herramientas**: `read_file`, `grep_search`

### Paso 4.3: Análisis de la Estructura de Directorios Clave (`src/`, `source/`, `app/`, etc.)

*   **Acción**: Ejecutar `list_dir` dentro de los directorios de código fuente principales identificados.
*   **Observaciones a Registrar**:
    *   ¿Cómo se organiza el código? (ej. por feature, por capa, por módulo técnico).
    *   Identificar nombres de directorios recurrentes que sugieran patrones (ej. `Controllers/`, `Services/`, `Repositories/`, `Domain/`, `Application/`, `Infrastructure/`, `Components/`, `Handlers/`).
    *   Convenciones de nomenclatura para subdirectorios y archivos (ej. `PascalCase`, `kebab-case`).
*   **Herramienta**: `list_dir`

### Paso 4.4: Inspección de Archivos de Configuración y Entrypoints

*   **Acción**: Leer archivos clave que suelen definir la configuración y el inicio de la aplicación.
    *   Ejemplos: `Startup.cs`, `Program.cs` (para .NET); `main.ts`, `App.tsx` (para frontend); `settings.py` (para Django); `application.properties` o `application.yml` (para Spring Boot).
    *   Buscar configuración de logging, ORM, inyección de dependencias, middleware, enrutamiento.
*   **Observaciones a Registrar**:
    *   Patrones de configuración (ej. Options Pattern en .NET).
    *   Configuración de servicios principales.
    *   Definición de pipeline de request/response (si aplica).
*   **Herramienta**: `read_file`

### Paso 4.5: Búsqueda de Patrones Arquitectónicos Evidentes

*   **Acción**: Utilizando la información de los pasos anteriores y `grep_search` si es necesario, buscar indicadores de patrones arquitectónicos.
    *   Para Arquitectura Limpia: Buscar directorios como `Domain`, `Application`, `Infrastructure` y el flujo de dependencias.
    *   Para CQRS/MediatR: Buscar uso de `IRequest`, `IRequestHandler`, `MediatR`, o nombres de archivo como `*Command.cs`, `*QueryHandler.cs`.
    *   Para Repositorio: Buscar interfaces `I*Repository` e implementaciones `*Repository`.
*   **Observaciones a Registrar**:
    *   Hipótesis sobre el patrón o patrones arquitectónicos principales utilizados.
    *   Evidencia que soporta estas hipótesis.
*   **Herramientas**: `grep_search`, `read_file` (para confirmar dependencias)

### Paso 4.6: Consolidación del Análisis Preliminar

*   **Acción**: Agrupar todas las observaciones registradas en un informe estructurado.
*   **Contenido del Informe (Borrador para `ai-rules-reasoning.md`)**:
    1.  **Introducción**: Breve descripción del repositorio y el propósito del análisis.
    2.  **Tecnologías Principales Identificadas**.
    3.  **Estructura General del Proyecto**: Descripción de la organización de directorios.
    4.  **Patrones Arquitectónicos Preliminares Observados**: Con justificación breve.
    5.  **Observaciones Adicionales Relevantes**: (ej. uso de Docker, CI/CD, convenciones de nombrado muy evidentes).
    6.  **Áreas Potenciales para Reglas Cursor**: Primeras ideas sobre qué aspectos podrían beneficiarse de una regla (sin detallar la regla aún).

## 5. Entregables de esta Sub-Kata

*   Un documento Markdown (o una sección dentro de un documento más grande) que contenga el "Informe de Análisis Exploratorio del Repositorio". Este informe servirá como la base para la sección de "Observaciones Preliminares" del archivo `ai-rules-reasoning.md` del proyecto.

## 6. Consideraciones Adicionales

*   Este es un análisis de alto nivel. No se espera una comprensión profunda de cada detalle del código en esta etapa.
*   El objetivo es obtener suficiente contexto para planificar la creación de reglas más específicas.
*   Si el repositorio es muy grande o complejo, esta Kata podría dividirse o enfocarse en un módulo principal inicialmente.

## 7. Próximos Pasos (según Kata Principal)

*   Proceder con la Fase 2 de `L0-01-gestion-integral-reglas-cursor.md`: `L2-02-inicializacion-gobernanza-reglas.md` (Creación/Actualización de Documentos de Gobernanza Iniciales), utilizando el entregable de esta Kata. 