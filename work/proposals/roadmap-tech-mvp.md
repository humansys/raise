# RaiSE - Roadmap Técnico de Comandos (MVP v0.1)

Este documento define la estrategia de implementación para el lanzamiento del MVP de RaiSE. Se establece una separación estricta entre la **Capa de Interacción (Slash Commands)** y la **Capa de Sistema (CLI Binario)**, apoyada por una arquitectura de **Ontología de Comandos (ADR-010)**.

## 1. Tabla Maestra de Versiones

Resumen ejecutivo de la disponibilidad de funcionalidades.

| Funcionalidad | Comando Slash (Prompt/IDE) | Versión | Comando CLI (Binario/Terminal) | Versión |
| :--- | :--- | :--- | :--- | :--- |
| **Inicialización** | `/init` | **v0.1** | `raise init` | **v0.1** |
| **Análisis** | `/analysis` | **v0.1** | `raise analysis` | **v0.1** |
| **Contexto** | `/pull` | **v0.1** | `raise pull` | **v0.1** |
| **Reglas** | `/guardrail` | **v0.1** | `raise guardrail` | v0.2 |
| **Ejecución (Coding)**| `/kata` | **v0.1** | `raise kata` | *Descartado* (Virtual) |
| **Auditoría/Logs** | `/audit` | v0.3 | `raise audit` | **v0.1** |
| **Validación** | `/check` | **v0.1** | `raise check` | v0.2 |
| **Aprobación** | `/gate` | v0.2 | `raise gate` | v0.2 |

> **Nota de Arquitectura:** `raise kata` no es un binario independiente en la terminal, sino un **concepto lógico** orquestado por el Agente que invoca `raise audit` para trazar el inicio y fin de procesos.

---

## 2. Desglose Detallado por Versión

### 🚀 Versión v0.1: MVP "Core Loop" (Salida a Producción)
**Objetivo:** Habilitar el ciclo *Configurar -> Entender -> Trabajar -> Fichar*.
En esta fase, confiamos en la inteligencia del LLM (Slash) y usamos el CLI solo para tareas de sistema de archivos y logging básico.

#### A. Capa de Sistema (CLI Binario)
Estos comandos deben estar programados y funcionales en el binario `raise`.

1.  **`raise init`**
    * **Propósito:** Nacer. Crea la estructura física del proyecto (**ADR-010: Comando de Creación**).
    * **Acción:** Genera la carpeta `.raise/`, crea `.raise/traces/` y un archivo `raise.yaml` plantilla.
    * **Detalle Técnico:**
        * Implementa una arquitectura de dos capas: **Capa 1 (Semántica)** guiada por la Kata `L1-init-project.md` y **Capa 2 (Determinista)** ejecutada por el CLI.
        * **Estrategia Brownfield:** Usa el flag `--skip-pull` para crear estructura sin imponer reglas inmediatamente ("Do no harm").
    * **Gap Identificado:** La estructura exacta de `raise.yaml` (repositorio de config, ramas, defaults) está pendiente de definición formal (Gap 9.1).
    * **Nota:** El flag `--template` se descarta en favor de detección automática o configuración explícita.

2.  **`raise analysis`**
    * **Propósito:** Ver. Genera el mapa del territorio (vital para Brownfield). **ADR-010: Comando de Descubrimiento**.
    * **Acción:** Escanea el directorio actual y genera:
        * `file-tree.txt`: Estructura de archivos.
        * `dependencies.txt` (básico): Lista de requirements/package.json.
    * **Detalle Técnico:** Implementa **SAR (Software Architecture Reconstruction)**. Es fundamental para proyectos iniciados con `--skip-pull`, proporcionando el contexto que falta al no descargar reglas externas.
    * **Lógica:** CLI actúa como "Proveedor de Contexto Estructural" (AST ligero), mientras el Agente realiza la reconstrucción semántica.

3.  **`raise pull`**
    * **Propósito:** Recordar. Prepara el contexto para la IA. **ADR-010: Comando de Mantenimiento**.
    * **Acción:** Empaqueta documentación clave (`.raise/docs`, reglas del IDE, `raise.yaml`) y el estado actual del código en un archivo de contexto (`context.xml` o clipboard) listo para el prompt.
    * **Detalle Técnico:** Sigue el principio "Build Once, Run Everywhere". Funciona sobre cualquier repositorio Git, independientemente del IDE (Cursor, VS Code, Windsurf, etc.).
    * **Gap Crítico:** Mecanismo de compilación de reglas (`.mdc` → `.json` o LinkML). Se debe decidir si el parseo ocurre localmente (CLI) o remotamente (CI).
    * **Solución Propuesta:** Transformación a LinkML/YAML vía flujo `raise guardrail`.

4.  **`raise audit`**
    * **Propósito:** Fichar. Persistencia mínima de actividad. **ADR-010: Comando de Observabilidad**.
    * **Acción:** Escribe una entrada estructurada (JSONL) con timestamp en `.raise/traces/session-[date].jsonl`.
    * **Uso:** El usuario lo ejecuta manualmente al terminar una tarea: `raise audit "Implementado login v1"`.
    * **Detalle Técnico:** Actúa como "Trace Wrapper". Se debe validar la integración con **Pydantic Logfire** para estructurar el esquema de logs (`TraceEvent`) y asegurar consistencia (Gap 9.3), aunque la implementación inicial puede ser un JSON append-only simple.
    * **Scalability Gap:** Necesidad futura de rotación de logs para evitar degradación de rendimiento.

#### B. Capa de Interacción (Slash Commands)
Estos son los **Prompts Maestros** que el usuario utiliza en el chat.

1.  **`/init`**
    * **Función:** Asistente de Configuración (Kata L1).
    * **Lógica:** Entrevista al usuario para definir el Nombre del Proyecto, Dominio y Estilo Técnico, y le pide que rellene el `raise.yaml`. Invoca `raise init` con los flags adecuados.

2.  **`/analysis`**
    * **Función:** Arquitecto de Software (SAR).
    * **Lógica:** Consume la salida de `raise analysis` y redacta el `service-overview.md` y `contracts.yaml`. Convierte listas de archivos en comprensión semántica. Invoca la Kata `L2-02`.

3.  **`/guardrail`**
    * **Función:** Legislador.
    * **Lógica:** Analiza el código o la petición del usuario y redacta un archivo `.mdc` válido. Instruye al LLM para guardar este archivo directamente en `.cursor/rules/` (o la ruta de reglas equivalente del IDE en uso).
    * **Nota:** Suple la falta del compilador CLI en v0.1. En el futuro (v0.2), este Markdown será la fuente para generar definiciones LinkML estrictas (Constitución §1).

4.  **`/kata`**
    * **Función:** Jefe de Obra.
    * **Lógica:** El prompt que orquesta la ejecución. Contiene las instrucciones paso a paso: "Lee el contexto, planifica, escribe código, verifica".
    * **Trazabilidad:** Debe instruir al Agente para llamar a `raise audit` al inicio y final de la ejecución para mantener el historial.

5.  **`/check`**
    * **Función:** Juez Semántico.
    * **Lógica:** "Analiza el código que acabas de generar. ¿Cumple con los requisitos A, B y C que te pedí? ¿Ves errores lógicos obvios?".

---

### 🛠️ Versión v0.2: Estabilidad y Calidad (Fast Follow)
**Objetivo:** Introducir automatización dura y reducir la carga cognitiva del usuario.

* **`raise check` (CLI):** Se integra con el sistema local. Ejecuta `npm test` o `pytest` y devuelve el código de salida.
    * **Evolución Arquitectónica:** Transición de validación JSON/Regex a una validación semántica basada en **RDF/SHACL** para mayor robustez (Solución al Gap 9.2).
* **`raise gate` (CLI):** Impide avanzar si no se cumplen métricas (ej. coverage < 80%). **ADR-010: Comando de Gobierno**.
    * **Gap:** Falta definir la biblioteca estándar de "Criterios" (`file_exists`, `grep_content`) para los Gates en `raise-config` (Gap 9.4).
* **`raise guardrail` (CLI):** Compilador real. Valida que los `.mdc` no se contradigan y los optimiza.
    * **Detalle Técnico:** Implementa la transformación: Markdown (Humano) → LinkML (Intermedio) → SHACL (Máquina).
* **`/gate` (Slash):** Prompt de revisión de diseño antes de escribir código.

---

### 🏢 Versión v0.3: Gobierno y Escala (Enterprise)
**Objetivo:** Gestión de equipos grandes y auditoría profunda.

* **`/audit` (Slash):** Agente Auditor.
    * **Razón del retraso:** Requiere un historial de logs (`.trace`) rico y acumulado durante v0.1 y v0.2 para ser útil. Analiza patrones de trabajo y cumplimiento de procesos.
* **Integraciones:** Conexión con Jira/Linear en los comandos CLI.

---

### Resumen de Flujo de Trabajo v0.1

1.  **Setup:** `raise init` (Terminal) -> `/init` (Chat).
2.  **Discovery:** `raise analysis` (Terminal) -> `/analysis` (Chat).
3.  **Definición:** `/guardrail` (Chat).
4.  **Desarrollo:** `raise pull` (Terminal) -> `/kata` (Chat).
5.  **Cierre:** `/check` (Chat) -> `raise audit` (Terminal).
