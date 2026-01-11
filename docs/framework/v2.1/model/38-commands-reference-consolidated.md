# Referencia Técnica Consolidada: Comandos CLI vs Slash
# 0. Arquitectura Dual de Interacción (Contexto vs Ejecución)

RaiSE opera bajo una arquitectura estricta de separación de responsabilidades:

1.  **Capa Cognitiva (Slash Commands `/`):**
    *   **Ejecutor:** LLM (Agente).
    *   **Función:** Inyección de Contexto.
    *   **Lógica:** *"Lee este prompt y entiende qué hacer"*.
    *   **Ejemplo:** `/kata` inyecta el archivo `spec-kata.md` en el chat. El sistema CLI **no** participa aquí.

2.  **Capa Determinista (CLI `raise`):**
    *   **Ejecutor:** Binario del Sistema (`raise-kit`).
    *   **Función:** Manipulación de Archivos y Logs.
    *   **Lógica:** *"Escribe este archivo", "Valida este regex", "Guarda este log"*.
    *   **Ejemplo:** `raise audit` escribe en disco. El LLM **no** tiene memoria persistente propia, usa el CLI.

> **Regla de Oro:** Los Slash Commands **piensan** (usan contexto). Los Comandos CLI **actúan** (usan sistema de archivos). Un comando Slash (como `/kata`) orquesta múltiples llamadas a comandos CLI (como `raise audit`) durante su ejecución.

---

# 1. Comando: `raise init`

## 1.1. Definición Ontológica

En la arquitectura RaiSE, `raise init` constituye el **Punto de Génesis**. Ontológicamente, se define en el **ADR-010** como un **Comando de Creación**.

* **Categoría:** Creación (vs. Verificación).
* **Naturaleza:** Interactiva y Fundacional.
* **Dependencia:** Requiere la presencia activa de un Orquestador (humano) guiado por un Agente para definir los parámetros iniciales.
* **Propósito:** Instanciar el **Golden Data** inmutable (`.raise/`) que servirá como fuente de verdad para todas las operaciones futuras del ciclo de vida.

## 1.2. Arquitectura de Ejecución: La Kata de Inicialización

Para resolver la fricción entre la ambigüedad del lenguaje natural y la precisión determinista requerida por el sistema de archivos, la ejecución de `raise init` se orquesta mediante dos capas distintas:

### Capa 1: La Interfaz Semántica (Kata L1)

El comando slash `/init` no ejecuta código binario directamente. En su lugar, invoca la **Kata L1 de Inicialización** (`L1-init-project.md`) dentro del contexto del Agente. Esta Kata actúa como un protocolo de arranque que guía al Agente para:

1. **Evaluación de Contexto:** Analizar el directorio actual para clasificar el entorno como *Greenfield* (vacío) o *Brownfield* (código existente).
2. **Estrategia de Configuración:** Guiar al Orquestador a través de decisiones clave (arquitectura, tipo de agente, nivel de estandarización).
3. **Construcción del Comando:** Traducir las decisiones semánticas en una instrucción CLI precisa y determinista.

### Capa 2: La Interfaz Determinista (CLI `raise-kit`)

El binario CLI es el ejecutor agnóstico que materializa la configuración definida por la Kata.

1. **Conexión y Clonado:** Conecta con el repositorio central `raise-config`.
2. **Descarga de Artefactos Pre-compilados:** Descarga los recursos necesarios, incluyendo el archivo `guardrails.json`.

   * *Nota Arquitectónica:* El CLI **no compila** reglas localmente. Consume el JSON ya procesado en el repositorio central (Build Once, Run Everywhere), garantizando consistencia absoluta entre todos los desarrolladores.

   3. **Scaffolding:** Despliega la estructura de directorios `.raise/` en el disco local.
   4. **Arranque de Contexto:** Inicia el servidor MCP local para servir inmediatamente el nuevo Golden Data.

> **⚠️ Nota de Arquitectura (Definición de `raise.yaml`):** La estructura esperada del archivo `.raise/raise.yaml` (flags defaults, repos de raise-config, agentes habilitados) aún no está completamente definida en la documentación pública. Esto impide describir con rigor cómo se configura el origen de Golden Data sin consultar el repositorio de configuración real. Añadir esa definición es prioritario para cerrar el círculo entre `raise init` y el resto de comandos.

## 1.3. Referencia Técnica

**Sintaxis:**

```bash
raise init [opciones]
```

**Tabla de Mapeo: Kata (Intención) → CLI (Ejecución)**

| Flag                    | Función Técnica          | Lógica de la Kata L1                                                                                           |
| :---------------------- | :------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| `--agent <nombre>`    | Optimización de entorno   | Se agrega cuando el usuario confirma su IDE (ej. Cursor, VS Code) para generar reglas específicas del modelo.  |
| `--template <nombre>` | Arquetipo de proyecto      | Se selecciona basándose en la descripción del proyecto (ej. "Microservicio Python" →`microservice`).       |
| `--skip-pull`         | Inicio limpio (sin reglas) | Se activa automáticamente en entornos**Brownfield** para permitir análisis previo sin imponer bloqueos. |
| `--config <url>`      | Fuente de verdad custom    | Se usa cuando el usuario especifica una gobernanza privada o corporativa distinta a la default.                 |
| `--mcp`               | Control de servidor        | (Default: true) Asegura que el servidor de contexto arranque post-instalación.                                 |

## 1.4. Estructura de Golden Data Resultante

Tras la ejecución, el sistema de archivos refleja el siguiente estado:

```text
.raise/
├── raise.yaml               # Configuración local (puntero al repo remoto)
├── memory/
│   ├── constitution.md      # Principios fundamentales (descargados)
│   └── guardrails.json      # Reglas pre-compiladas (Machine-readable)
├── specs/                   # (Vacío) Espacio para especificaciones vivas
├── plans/                   # (Vacío) Espacio para planes técnicos
└── traces/                  # (Iniciado) Log de auditoría de la creación
```

---

## 1.5. Casos de Uso y Patrones

### Caso de Uso A: Proyecto Greenfield (Nuevo Desarrollo)

**Contexto:** Un equipo inicia un nuevo microservicio desde cero.
**Flujo de la Kata:**

1. **Agente:** Detecta directorio vacío.
2. **Kata:** Pregunta por el tipo de arquitectura.
3. **Orquestador:** "Es una API REST en Python".
4. **Ejecución:** `raise init --template microservice --agent cursor`
   **Resultado:** El proyecto nace con la estructura de carpetas correcta, la constitución cargada y los guardrails de API activos desde el minuto cero.

### Caso de Uso B: Adopción Brownfield (Proyecto Legacy)

**Contexto:** Se quiere introducir RaiSE en un monolito existente sin romper el flujo actual.
**Flujo de la Kata:**

1. **Agente:** Detecta archivos fuente existentes.
2. **Kata:** Recomienda no imponer reglas inmediatamente ("Do no harm").
3. **Ejecución:** `raise init --skip-pull`
   **Resultado:** Se crea la estructura `.raise/` pero sin descargar `guardrails.json`.

> **⚠️ Nota de Arquitectura (Gap Detectado):**
> Al usar `--skip-pull`, el proyecto carece de Katas locales para ejecutar un análisis estructurado (SAR).
>
> * **Problema:** No existe un comando `raise analysis` nativo.
> * **Solución Propuesta:** El análisis SAR debe ser una capacidad nativa del Agente (Skill base) o `raise init` debe traer un set mínimo de "Bootstrapping Katas" incluso con `--skip-pull`.
>
> ✅ **Solución Confirmada:** Se implementará el comando `raise analysis`. Este comando permitirá ejecutar el análisis SAR de forma nativa, resolviendo la necesidad de análisis en entornos inicializados sin reglas externas.

### Caso de Uso C: Inicialización de Gobernanza (Platform Team)

**Contexto:** El equipo de plataforma crea el repositorio central de configuración.
**Flujo de la Kata:**

1. **Agente:** Identifica intención de infraestructura/gobernanza.
2. **Ejecución:** `raise init --template config-repo`
   **Resultado:** Genera la estructura de directorios necesaria para alojar los templates, guardrails (`.mdc`) y katas compartidas.

> **⚠️ Nota de Realidad (Validation Check):**
> El flag `--template` está documentado en v2.1, pero no se ha validado su uso en implementaciones manuales previas.
>
> * **Riesgo:** Posible "alucinación canonizada". Si no existe un sistema de templates real en `raise-config`, este flag es aspiracional.
> * **Acción:** Verificar existencia de carpeta `templates/` en el repo de configuración antes de implementar.
>
> ✅ **Decisión:** El flag `--template` se eliminará de la especificación final. No se utilizará un sistema de templates invocado por flag; la configuración se basará en análisis o defaults explícitos, eliminando esta opción.

---

# 2. Comando: `raise pull`

## 2.1. Definición Ontológica

`raise pull` es el **Comando de Sincronización**. Ontológicamente, se clasifica en el **ADR-010** como un comando de **Mantenimiento**.

* **Categoría:** Mantenimiento (Compatible con CI/CD).
* **Naturaleza:** Determinista y Automatizable.
* **Dependencia:** No requiere interacción humana (pipeline-friendly).
* **Propósito:** Actualizar el **Golden Data Local** (`.raise/`) alineándolo con la fuente de verdad remota, asegurando que el agente opere con las reglas más recientes.

## 2.2. Arquitectura de Ejecución: Actualización de Contexto

La ejecución es directa y unidireccional: del repositorio central al sistema local.

### Capa 1: La Interfaz Semántica (Kata L1 de Mantenimiento)

El agente puede sugerir este comando a través de la Kata de Mantenimiento (`L1-maintain-project.md`) cuando detecta:

* **Obsolescencia:** Metadatos de reglas con fechas antiguas.
* **Errores de Validación:** Fallos recurrentes que sugieren discrepancias entre la regla local y la expectativa del sistema.

### Capa 2: La Interfaz Determinista (CLI `raise-kit`)

El binario ejecuta la sincronización en tres fases críticas:

1. **Resolución de Origen:** Determina la URL del repositorio remoto.
   * Prioridad 1: Flag `--config` (si se provee).
   * Prioridad 2: Archivo `.raise/raise.yaml`.
2. **Fetch & Update:** Descarga los artefactos desde la rama especificada.
3. **Compilación de Guardrails (Parseo):**
   * El CLI toma los archivos fuente (Markdown/MDC) descargados.
   * Procesa los metadatos y reglas regex.
   * Genera/Sobrescribe el archivo `.raise/memory/guardrails.json`.
   * *Este paso es crucial: transforma documentación humana en reglas de máquina.*

## 2.3. Referencia Técnica

**Sintaxis:**

```bash
raise pull [opciones]
```

**Tabla de Mapeo: Flags**

| Flag                  | Función Técnica  | Lógica de Uso                                                                                     |
| :-------------------- | :----------------- | :------------------------------------------------------------------------------------------------- |
| `--config <url>`    | Override de Origen | Permite sincronizar desde un repo distinto al configurado en `raise.yaml` (ej. fork de pruebas). |
| `--branch <nombre>` | Cambio de Contexto | Cambia la rama de origen (ej.`develop`, `feat/new-rules`).                                     |
| `--force`           | Reinicio de Estado | Sobrescribe cambios locales no guardados en `.raise/` para restaurar la integridad.              |
| `--guardrails-only` | Optimización      | Descarga y procesa solo las reglas, ignorando templates y katas. Ideal para CI veloz.              |

## 2.4. Efecto en Golden Data

Actualiza los componentes vivos de la memoria del proyecto:

```text
.raise/
├── memory/
│   ├── guardrails.json      # (Regenerado tras el parseo)
│   └── constitution.md      # (Sincronizado)
├── katas/                   # (Actualizado)
└── raise.yaml               # (Persistente, salvo que se edite manualmente)
```

---

## 2.5. Casos de Uso

### Caso de Uso A: Rutina Diaria (Desarrollo)

**Contexto:** Inicio de jornada laboral.
**Flujo:**

1. **Desarrollador:** Ejecuta `raise pull`.
   **Resultado:** El entorno local recibe las últimas definiciones de seguridad y procesos publicadas por el equipo de plataforma.

### Caso de Uso B: Validación en Pipeline

**Contexto:** GitHub Action validando un PR.
**Flujo:**

1. **Pipeline:** `raise pull --guardrails-only`
   **Resultado:** El runner de CI obtiene la versión más reciente de las reglas en segundos, minimizando el tiempo de ejecución del job.

### Caso de Uso C: Test de Reglas Experimentales

**Contexto:** Probar un nuevo set de reglas antes de mergear.
**Flujo:**

1. **Ingeniero:** `raise pull --config <mi-fork-url> --branch test-rules`
   **Resultado:** El proyecto local se sincroniza temporalmente contra un repositorio experimental para validar el comportamiento de los nuevos guardrails.

> **⚠️ Nota de Arquitectura (Pendiente de Definición):**
> El mecanismo exacto de parseo (`.mdc` → `.json`) durante el `pull` presenta un desafío de diseño:
>
> * **Opción A (Local):** El CLI descarga Markdowns y compila localmente. (Flexible, pero lento en repos grandes).
> * **Opción B (Remoto):** El CLI descarga un JSON ya compilado por el CI del repo de config. (Rápido, pero requiere infraestructura central).
> * **Estado Actual:** Se asume **Opción A** por simplicidad en MVP, pero debe revisarse para escala Enterprise.
>
> ✅ **Solución:** La transformación de reglas será parte del flujo de creación. Se utilizará un proceso (ej. `raise guardrail-parse`) invocado por Katas para transformar definiciones en Markdown (.md) a YAML compatible con LinkML, estableciendo este último como el formato ejecutable para la máquina.

---

# 3. Comando: `/kata` (Slash) vs `raise kata` (Concepto)

## 3.1. Definición Ontológica y Diferenciación

Es crucial distinguir entre la **intención** (Slash) y el **registro** (CLI).

*   **`/kata` (Slash Command):** Es el **Motor del Proceso**. Es un prompt del sistema que carga una guía Markdown en la memoria del LLM. **Aquí reside la inteligencia.** El LLM lee la kata, entiende los pasos y decide qué hacer.
*   **`raise kata` (CLI Wrapper):** Es un **Comando Virtual**. No existe un binario `raise kata` que "ejecute" el proceso. Es una abstracción conceptual para referirse a la traza de auditoría. Técnicamente, cuando el LLM "ejecuta" una kata, lo que hace es llamar a `raise audit start` y `raise audit end`.

## 3.2. Arquitectura de Ejecución

### Capa 1: Interfaz Semántica (Slash Command `/kata`)
El usuario escribe `/kata spec`. El sistema (IDE):
1.  Busca `katas/L1-spec.md`.
2.  Inyecta el contenido en el contexto del chat.
3.  **El LLM toma el control.**

### Capa 2: Interfaz de Registro (CLI `raise audit`)
La Kata inyectada contiene instrucciones explícitas para el LLM:
> *"Al iniciar, ejecuta: `raise audit start --process kata:spec`"*
> *"Al finalizar, ejecuta: `raise audit end --artifact spec.md`"*

De esta forma, el **CLI** solo actúa como notario, mientras que el **Slash Command** maneja la complejidad variable del proceso.

## 3.3. Referencia Técnica (Uso por el Agente)

> **Nota:** Este comando no tiene sintaxis CLI directa. Se invoca semánticamente desde el IDE y se apoya en `raise audit` para la persistencia.

## 3.4. Efecto en Golden Data

* **Principal:** Generación de logs en `traces/` que vinculan el proceso ejecutado con los archivos resultantes.
* **Secundario:** Los artefactos que la propia Kata instruye crear (specs, código, etc.).

---

## 3.5. Casos de Uso

### Caso de Uso A: Ejecución de Proceso Core

**Contexto:** Crear una especificación.
**Flujo:**

1. **Orquestador:** `/spec` (que por debajo invoca `raise kata spec`).
2. **CLI:** Registra inicio de trace. Carga `L1-spec.md`.
3. **Agente:** Ejecuta la lógica interactiva.
4. **CLI:** Cierra trace vinculando la spec creada.

### Caso de Uso B: Ejecución de Proceso Custom

**Contexto:** Un equipo crea una Kata específica para "Migración de Base de Datos".
**Flujo:**

1. **Orquestador:** `raise kata db:migrate`
2. **CLI:** Busca `katas/db/migrate.md`. Lo carga.
3. **Agente:** Guía al usuario en la migración segura.
   **Resultado:** El sistema auditó que se corrió una migración, aunque el CLI no sepa de SQL.

> **⚠️ Nota de Arquitectura (Interacción IDE-CLI):**
> Falta definir cómo el IDE (Cursor/VSCode) pasa el control al CLI para el "wrapping" de trazas y luego le devuelve el control al Agente para la ejecución interactiva. Es posible que `raise kata` sea solo un comando lógico que el Agente invoca internamente para marcar el inicio/fin ("Tool Call"), en lugar de algo que el humano escribe en la terminal.
>
> ✅ **Clarificación:** No existe un mecanismo de traspaso "mágico". La interacción es explícita: el Agente (LLM) invoca comandos CLI (`raise kata`, etc.) porque la propia Kata (Markdown) se lo instruye como un paso del proceso. El Agente opera el CLI como una herramienta estándar.

---

# 4. Comando: `raise check`

## 4.1. Definición Ontológica

`raise check` es el **Motor de Validación**. Ontológicamente, se define en el **ADR-010** como un comando de **Verificación y Mantenimiento**.

* **Categoría:** Verificación (CI/CD Nativo).
* **Naturaleza:** Determinista y Automatizable.
* **Propósito:** Asegurar que el código fuente cumpla estrictamente con los **Guardrails Activos** definidos en el Golden Data.

## 4.2. Arquitectura de Ejecución: Validación Híbrida

### Capa 1: La Interfaz Semántica (Kata de Validación)

Para el Agente, la validación es un proceso cognitivo guiado por una **Kata de Calidad** (ej. `L2-code-quality.md`).

* **El Comando:** `/check` (Slash Command).
* **La Kata:** Instruye al Agente para realizar un razonamiento semántico sobre el código (ej. principios SOLID, legibilidad) que va más allá de lo sintáctico.

### Capa 2: La Interfaz Determinista (CLI `raise-kit`)

El binario ejecuta la validación sintáctica rígida y el **Registro de Auditoría**.

1. **Carga de Reglas:** Lee `.raise/memory/guardrails.json`.
2. **Evaluación:** Aplica patrones definidos.
3. **Trazabilidad (Wrapper):** Si se activa `--trace`, genera un log estructurado en `traces/` con el resultado (Pass/Fail) y las violaciones encontradas, garantizando auditoría tanto para ejecuciones manuales como automatizadas.

## 4.3. Referencia Técnica

**Sintaxis:**

```bash
raise check [path] [opciones]
```

**Tabla de Mapeo: Flags**

| Flag                   | Función Técnica | Caso de Uso                                                                     |
| :--------------------- | :---------------- | :------------------------------------------------------------------------------ |
| `[path]`             | Alcance           | Limitar la revisión a un archivo/carpeta.                                      |
| `--guardrails <ids>` | Filtro            | Verificar solo reglas específicas.                                             |
| `--strict`           | Tolerancia Cero   | Warnings = Error (Exit Code 1).                                                 |
| `--format <fmt>`     | Salida            | JSON para consumo de dashboards CI/CD.                                          |
| `--trace`            | Auditoría        | Registra el evento en `traces/`. (Consolidado con diseño de `raise kata`). |

## 4.4. Efecto en Golden Data

* Genera logs de validación en `traces/` (si `--trace` está activo).

---

## 4.5. Casos de Uso

### Caso de Uso A: Agente Auto-Correctivo (Capa 1)

**Contexto:** Agente generando código.
**Flujo:**

1. **Agente:** Termina código.
2. **Kata:** "Revisa tu propio código".
3. **Agente:** Detecta violación semántica y corrige.
4. **Agente (Opcional):** Invoca `raise check --trace` para confirmar cumplimiento sintáctico y dejar evidencia.

### Caso de Uso B: Pipeline de Bloqueo (Capa 2)

**Contexto:** CI/CD.
**Flujo:**

1. **CI:** `raise check --strict --trace`
   **Resultado:** Bloqueo automático ante errores y generación de artefacto de auditoría para Compliance.

> **⚠️ Nota de Arquitectura (Integración CI/CD y Reglas JSON):**
> Existe una brecha de definición en cómo el CI/CD consume las reglas dinámicas.
>
> * **Problema:** Si las reglas vienen en un `guardrails.json` generado dinámicamente desde Markdowns (`.mdc`), el pipeline de CI necesita un mecanismo fiable para interpretar ese JSON (Regex engine vs AST engine).
> * **Riesgo:** Inconsistencia entre lo que el Agente "entiende" del Markdown y lo que el CLI "valida" del JSON.
> * **Dependencia:** Esta definición está bloqueada por la decisión de diseño sobre el mecanismo de parseo `.mdc` -> `.json` (mencionado en `raise pull`).
>
> ✅ **Solución:** La validación se resolverá generando una representación RDF del código y validándola mediante SHACL. Esto sustituye la dependencia de JSON/Regex por un modelo de gobernanza semántica robusto.

---

# 5. Comando: `raise gate`

## 5.1. Definición Ontológica

`raise gate` es el **Verificador de Definition of Done (DoD)**. Ontológicamente, se define en el **ADR-010** como un comando de **Verificación y Gobierno**.

* **Categoría:** Verificación (CI/CD Nativo).
* **Naturaleza:** Checklist Binario (Cumple/No Cumple).
* **Propósito:** Validar formalmente que se han cumplido los criterios necesarios (DoD) para transicionar de una fase del ciclo de vida a la siguiente.

## 5.2. Arquitectura de Ejecución: Validación de Entregables

### Capa 1: La Interfaz Semántica (Evaluación de Calidad)

El Agente utiliza la Kata asociada al Gate para realizar una evaluación cualitativa sobre el contenido de los entregables (ej. "¿Es el análisis de stakeholders suficiente?").

### Capa 2: La Interfaz Determinista (CLI - Validación de Existencia)

El CLI ejecuta la validación objetiva de "Definition of Done":

* **Existencia de Artefactos:** Verifica que los documentos requeridos (Specs, Plans) existan.
* **Trazabilidad:** Verifica que los pasos previos (ej. `raise check`) se hayan ejecutado exitosamente.
* **Estado:** Verifica metadatos de aprobación en los archivos (Frontmatter).

## 5.3. Referencia Técnica

**Sintaxis:**

```bash
raise gate <gate-id> [opciones]
```

**Gates Estándar (Definidos en v2.1):**

| Gate ID            | Fase           | Pregunta Clave (DoD)                                 |
| :----------------- | :------------- | :--------------------------------------------------- |
| `Gate-Context`   | Discovery      | ¿Stakeholders claros y problema definido?           |
| `Gate-Discovery` | Discovery      | ¿PRD validado y requisitos completos?               |
| `Gate-Vision`    | Vision         | ¿Alineación entre negocio y solución técnica?    |
| `Gate-Design`    | Design         | ¿Arquitectura consistente y contratos definidos?    |
| `Gate-Backlog`   | Planning       | ¿Historias de Usuario (HUs) bien formadas (INVEST)? |
| `Gate-Plan`      | Planning       | ¿Pasos de implementación verificables?             |
| `Gate-Code`      | Implementation | ¿Código validado, testeado y sin deuda técnica?   |
| `Gate-Deploy`    | Deployment     | ¿Feature estable y lista para producción?          |

**Tabla de Mapeo: Flags**

| Flag                  | Función Técnica      | Lógica de Uso                                                                      |
| :-------------------- | :--------------------- | :---------------------------------------------------------------------------------- |
| `--artifact <ruta>` | Validación Focalizada | Valida el Gate contra un archivo específico en lugar de auto-detectar el contexto. |
| `--format <fmt>`    | Reporte                | `text` (humano) o `json` (máquina). Crucial para integración CI/CD.           |

## 5.4. Efecto en Golden Data

* **Trace de Aprobación:** Si el Gate pasa, genera un registro en `traces/` certificando que el proyecto cumplió el DoD de esa fase en ese momento específico.

---

## 5.5. Casos de Uso

### Caso de Uso A: Bloqueo de Pull Request (CI/CD)

**Contexto:** Validación de código antes de merge.
**Flujo:**

1. **CI Pipeline:** `raise gate Gate-Code --format json`
2. **CLI:** Verifica:
   * Tests existentes y pasando.
   * Linter (`raise check`) exitoso.
   * Spec aprobada vinculada.
     **Resultado:** Éxito (0) o Fallo (1) con lista de criterios incumplidos.

### Caso de Uso B: Aprobación de Diseño

**Contexto:** Transición de Diseño a Código.
**Flujo:**

1. **Orquestador:** `raise gate Gate-Design`.
2. **CLI:** Verifica existencia de `specs/*.md` con estado aprobado.
   **Resultado:** Confirmación visual de que la fase de diseño está cerrada.

> **⚠️ Nota de Arquitectura (Implementación de Criterios):**
> Falta definir la biblioteca estándar de "Criterios" (`file_exists`, `grep_content`, `metric`) que soportará el CLI para definir los Gates en `raise-config`.
>
> * **Riesgo:** Si los criterios son muy complejos, el CLI se vuelve un motor de reglas pesado.
> * **Mitigación:** Mantener los criterios primitivos y delegar lógica compleja a scripts externos invocados por `command_success`.

> ℹ️ **Nota de Diseño (DoD Gates):**
> Existe un gap pendiente sobre la biblioteca de aserciones soportada (ej. `file_exists`). No es bloqueante, pero se requiere definir un conjunto mínimo de validaciones deterministas. Ver detalle en sección 9.4.

---

# 6. Comando: `raise audit`

## 6.1. Definición Ontológica

`raise audit` es el **Motor de Observabilidad**. Ontológicamente, se define en el **ADR-010** como un comando de **Verificación y Mantenimiento**.

* **Categoría:** Verificación (CI/CD Nativo).
* **Naturaleza:** Lectura y Escritura (Logging/Querying).
* **Propósito:** Registra eventos en el sistema. Se utiliza manualmente para 'fichar' el inicio y fin de una sesión de trabajo (Kata), generando la entrada en `.raise/traces/`. Además, permite consultar el historial.

## 6.2. Arquitectura de Ejecución: Registro y Minería de Logs

A diferencia de los comandos anteriores que actúan sobre el código o la configuración, `raise audit` actúa sobre la **historia del proyecto**.

### Capa 1: La Interfaz Semántica (Reflexión y Métricas)

El Agente utiliza este comando para obtener autoconsciencia sobre su desempeño o el del equipo.

* **Consulta:** *"Dame un resumen de las sesiones de hoy"*.
* **Registro:** *"Inicia sesión de análisis"*.
* **Análisis:** El Agente procesa el JSON de salida para responder preguntas complejas: *"¿Cuál es la tasa de fallo en el Gate de Diseño esta semana?"*.

### Capa 2: La Interfaz Determinista (CLI - Query & Log Engine)

El binario funciona como una base de datos analítica ligera sobre archivos planos:

1. **Registro:** Escribe nuevas entradas en `.raise/traces/` cuando se usa para marcar eventos.
2. **Ingestión:** Lee los archivos `.jsonl` existentes.
3. **Filtrado:** Aplica filtros de tiempo (`--period`) o sesión (`--session`).
4. **Agregación:** Calcula métricas derivadas (tiempo promedio de Kata, tasa de éxito de Gates).
5. **Renderizado:** Genera el output en el formato solicitado (Tabla CLI, JSON, CSV, Markdown).

## 6.3. Referencia Técnica

**Sintaxis:**

```bash
raise audit [opciones]
```

**Tabla de Mapeo: Flags**

| Flag                 | Función Técnica | Lógica de Uso                                                                                                                |
| :------------------- | :---------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| `--period <range>` | Filtro Temporal   | Define la ventana de análisis:`today`, `week`, `month`, `all`. (Default: `today`).                                 |
| `--session <id>`   | Filtro de Sesión | Aísla los eventos de una interacción específica (útil para debug de un error del agente).                                 |
| `--format <fmt>`   | Formato de Salida | `text` (humano/terminal), `json` (máquina/dashboard), `csv` (análisis en Excel), `md` (reportes de documentación). |
| `--output <file>`  | Persistencia      | Guarda el reporte en un archivo en lugar de imprimirlo en stdout.                                                             |
| `--metrics`        | Agregación       | Incluye estadísticas calculadas (Success Rate, Duration) en el reporte.                                                      |

## 6.4. Efecto en Golden Data

* **Lectura:** Consume masivamente `.raise/traces/`.
* **Escritura:** Genera entradas en `traces/` (cuando se usa para logging) y puede generar reportes en otros directorios (si se usa `--output`).

---

## 6.5. Casos de Uso

### Caso de Uso A: Auditoría de Compliance (CI/CD)

**Contexto:** Requisito de trazabilidad para certificación (ej. ISO/SOC2).
**Flujo:**

1. **CI Pipeline:** Al final del build, ejecuta:
   ```bash
   raise audit --period today --format json --output artifacts/audit-log.json
   ```
2. **Artifact Upload:** Sube el JSON a un bucket de almacenamiento seguro.
   **Resultado:** Evidencia inmutable de qué Gates y Checks se ejecutaron para cada release.

### Caso de Uso B: Retrospectiva Diaria (Agente/Humano)

**Contexto:** Revisar el trabajo del día.
**Flujo:**

1. **Desarrollador:** `raise audit --period today`
2. **CLI:** Muestra una tabla en terminal con el resumen de actividad.
   **Resultado:** Visibilidad rápida del progreso y bloqueos.

> **⚠️ Nota de Arquitectura (Volumen de Datos):**
> El sistema de archivos local (`.jsonl`) no escala indefinidamente.
>
> * **Riesgo:** En proyectos longevos, `raise audit` puede volverse lento al procesar GBs de logs.
> * **Solución Futura:** Se necesitará un mecanismo de **Rotación de Logs** o archivado (ej. mover logs viejos a `.raise/traces/archive/` que el comando ignore por defecto).

> ℹ️ **Nota de Diseño (Audit Schema):**
> Existe un gap pendiente sobre el esquema exacto de los logs (`TraceEvent`). No es bloqueante para el MVP, pero se apunta a usar **Pydantic Logfire** como estándar de estructuración y persistencia. Ver detalle en sección 9.3.

---

# 7. Comando: `raise analysis`

## 7.1. Definición Ontológica

`raise analysis` es el **Motor de Descubrimiento**. Ontológicamente, se define en el **ADR-010** como un comando de **Descubrimiento y Reconstrucción**.

* **Categoría:** Descubrimiento (SAR - Software Architecture Reconstruction).
* **Naturaleza:** Exploratoria y Reconstructiva.
* **Propósito:** Escanear una base de código existente (Brownfield) para inferir su arquitectura, contratos y reglas de negocio, generando documentación viva donde no existía.

## 7.2. Arquitectura de Ejecución: SAR (Software Architecture Reconstruction)

### Capa 1: La Interfaz Semántica (Kata de Reconstrucción)

El comando `/analysis` invoca la Kata `L2-02-Analisis-Agnostico-Codigo-Fuente.md`. Esta Kata guía al Agente a través de cuatro fases cognitivas:

1. **Descubrimiento de Superficie:** Identificación de Endpoints y Contratos.
2. **Análisis de Dependencias:** Mapeo de llamadas salientes e infraestructura.
3. **Lógica de Negocio:** Extracción de entidades de dominio y patrones de resiliencia.
4. **Síntesis:** Generación de artefactos documentales (`service-overview.md`, etc.).

### Capa 2: La Interfaz Determinista (CLI - Structural Scanner)

El binario `raise-kit` actúa como un **Proveedor de Contexto Estructural**. Dado que leer todo el código crudo es costoso e ineficiente para el LLM, el CLI pre-procesa el repositorio:

1. **Generación de Árbol:** Crea una representación textual de la estructura de carpetas (respetando `.gitignore`).
2. **Análisis Estático Ligero:** Identifica lenguajes y puede extraer firmas (AST simplificado) si se requiere, permitiendo al Agente "ver" el bosque antes de inspeccionar los árboles.

## 7.3. Referencia Técnica

**Sintaxis:**

```bash
raise analysis [opciones]
```

**Tabla de Mapeo: Flags**

| Flag               | Función Técnica     | Lógica de Uso                                                                        |
| :----------------- | :-------------------- | :------------------------------------------------------------------------------------ |
| `--depth <n>`    | Límite de Recursión | Controla qué tan profundo explora el árbol de archivos el CLI (útil en monorepos). |
| `--focus <path>` | Ámbito Reducido      | Centra el análisis SAR en un módulo o directorio específico.                       |
| `--output <dir>` | Destino               | (Opcional) Define dónde volcar los artefactos (Default:`.raise/memory/context`).   |

## 7.4. Efecto en Golden Data

Puebla la carpeta de contexto con documentación estructurada derivada del código:

```text
.raise/
├── memory/
│   ├── context/
│   │   ├── service-overview.md  # Visión 360 del servicio
│   │   ├── contracts.md         # API Surface
│   │   ├── dependencies.yaml    # Grafo de dependencias
│   │   ├── domain-model.md      # Entidades de negocio
│   │   └── resilience-guide.md  # Patrones de fallos
```

## 7.5. Casos de Uso

### Caso de Uso A: Onboarding de Proyecto Legacy (Brownfield)

**Contexto:** Se inicializa RaiSE en un monolito sin documentación.
**Flujo:**

1. **Ingeniero:** `raise init --skip-pull` (Crea estructura vacía).
2. **Ingeniero:** `raise analysis`
3. **Agente:** Lee la estructura, selecciona archivos clave, infiere la arquitectura y genera `service-overview.md`.
   **Resultado:** El proyecto ahora tiene documentación basal para empezar a trabajar con reglas.

---

# 8. Comando: `raise guardrail`

## 8.1. Definición Ontológica

`raise guardrail` es el **Gestor del Ciclo de Vida de Reglas**. Ontológicamente, se define en el **ADR-010** como un comando de **Creación y Mantenimiento**.

* **Categoría:** Gobernanza y Estandarización.
* **Naturaleza:** Interactiva y Compiladora.
* **Propósito:** Facilitar la creación, edición y transformación de reglas humanas (Markdown) en guardrails ejecutables por máquina (YAML/SHACL), sustituyendo la gestión manual de archivos JSON.

## 8.2. Arquitectura de Ejecución: De Documento a Código

### Capa 1: La Interfaz Semántica (Kata de Definición y Compilación)

La inteligencia de RaiSE reside en el Agente. Por tanto, la transformación de lenguaje natural a estructurado ocurre aquí:

1. **Definición (`new`):** El Agente entrevista al usuario y genera el archivo `.md` con la intención y ejemplos.
2. **Compilación Ontológica (`compile`):** El Agente (guiado por una Kata técnica) lee el Markdown, lo valida contra la ontología LinkML del sistema y genera el archivo `.yaml` intermedio.
   * *Por qué en Capa 1:* Porque mapear "prohibir prints" a una estructura LinkML válida requiere comprensión semántica, no solo parsing sintáctico.

### Capa 2: La Interfaz Determinista (CLI - Rule Engine)

El binario `raise-kit` se encarga de la materialización final en el motor de validación:

1. **Ingestión (`apply`):** Toma el `.yaml` (LinkML) generado por el Agente.
2. **Generación de Artefactos de Validación:** Transforma la definición LinkML en las formas ("Shapes") SHACL o scripts de validación específicos que consumirá `raise check`.
3. **Registro:** Actualiza el índice de reglas activas en `.raise/memory/rules/`.

## 8.3. Referencia Técnica

**Sintaxis:**

```bash
raise guardrail <subcomando> [opciones]
```

**Subcomandos:**

* `new`: Inicia la Kata de creación (MD).
* `compile`: Inicia la Kata de transformación (MD -> YAML).
* `apply`: Ejecuta la integración del YAML en el motor SHACL.

**Tabla de Mapeo: Flags**

| Flag          | Función Técnica      | Lógica de Uso                                                                               |
| :------------ | :--------------------- | :------------------------------------------------------------------------------------------- |
| `--dry-run` | Simulación            | Muestra qué reglas se generarían sin escribir en disco (útil para debug).                 |
| `--strict`  | Validación de Esquema | Falla si el Markdown de la regla no cumple con la estructura requerida para la compilación. |

## 8.4. Efecto en Golden Data

Transforma la especificación viva en reglas de máquina:

```text
.raise/
├── specs/
│   └── rules/
│       └── no-print.md          # Definición Humana (Source)
├── memory/
│   └── rules/
│       └── no-print.yaml        # Definición Máquina (Compiled Target)
```

## 8.5. Casos de Uso

### Caso de Uso A: Creación de Nueva Regla (Gobernanza)

**Contexto:** El equipo decide prohibir funciones cíclicas.
**Flujo:**

1. **Arquitecto:** `raise guardrail new`
2. **Agente:** "¿Cómo se llama la regla?". Genera `no-cyclic-deps.md`.
3. **Arquitecto:** Revisa el MD.
4. **Arquitecto:** `raise guardrail apply`
   **Resultado:** Se genera `no-cyclic-deps.yaml` y la regla ya es ejecutable por `raise check`.

---

# 9. Gaps y Definiciones Pendientes

## 9.1. Definición de `raise.yaml` (Deuda de Configuración)

La estructura del archivo `.raise/raise.yaml` no está formalizada, lo que impide implementar la lógica de conexión entre `init` y `pull`.

* **Gap Detectado:** No existe un esquema documentado para este archivo crítico.
* **Requerimiento de Definición:** Se debe especificar la sintaxis exacta para:
  * `config.repo`: URL del repositorio remoto de Golden Data.
  * `config.branch`: Rama por defecto para sincronización.
  * `agent.defaults`: Flags predeterminados por agente.
  * `project.type`: Metadatos del arquetipo seleccionado en `init`.

## 9.2. Pipeline de Compilación de Reglas (.mdc → .json)

Existe una ambigüedad arquitectónica crítica sobre *dónde* y *cómo* se transforman las reglas humanas (`.mdc`) en reglas de máquina (`.json`).

* **Gap Detectado:** No está definido si la compilación ocurre en el cliente (CLI durante `pull`) o en el servidor (CI del repo `raise-config`).
* **Impacto:** Riesgo de inconsistencia entre la validación "blanda" del Agente (que lee Markdown) y la validación "dura" del CLI (que ejecuta JSON).
* **Requerimiento de Definición:** Especificar el motor de regex/AST que consumirá `raise check` y cómo se mapea desde el Markdown original.

## 9.3. Esquema Unificado de Trazabilidad (Audit Schema)

Para que `raise audit` funcione como un Query Engine fiable, todos los comandos productores (`init`, `kata`, `check`, `gate`) deben escribir en `traces/` bajo un esquema estricto y común.

* **Gap Detectado:** Falta la definición de la estructura JSON de los logs.
* **Requerimiento de Definición:** Diseñar el esquema del objeto `TraceEvent`, incluyendo campos obligatorios como:
  * `trace_id`: UUID de la sesión.
  * `timestamp`: ISO 8601.
  * `actor`: Usuario o Agente (ID).
  * `command`: Comando ejecutado (`check`, `gate`).
  * `input_context`: Archivos o argumentos.
  * `outcome`: Resultado (Pass/Fail, Artifacts Created).

> ℹ️ **Nota de Prioridad (Non-Blocker):**
> Este gap no bloquea el MVP. La solución técnica candidata más fuerte es utilizar **Pydantic Logfire** para estructurar y persistir los eventos de traza de forma nativa y estandarizada. La implementación final seguirá ese estándar.

## 9.4. Biblioteca de Criterios de DoD (Gate Definitions)

Para que `raise gate` sea funcional, se necesita estandarizar el lenguaje de aserciones que define un "Definition of Done".

* **Gap Detectado:** No existe especificación de qué tipos de validaciones soporta el CLI.
* **Requerimiento de Definición:** Definir la lista de primitivas soportadas en la configuración de un Gate, tales como:
  * `file_exists(pattern)`: Validación estructural.
  * `content_contains(pattern)`: Validación de contenido simple.
  * `command_pass(cmd)`: Delegación a scripts externos.
  * `metric_threshold(name, min/max)`: Validación numérica (coverage, performance).

> ℹ️ **Nota de Prioridad (Non-Blocker):**
> Este gap no bloquea el desarrollo inicial. Se requiere definir una biblioteca de aserciones deterministas para validar los entregables, pero esto puede iterarse a medida que se definen los primeros Gates reales.
