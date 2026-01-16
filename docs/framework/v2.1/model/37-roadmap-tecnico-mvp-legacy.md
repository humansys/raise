# RaiSE - Roadmap Técnico de Comandos (MVP v0.1)

Este documento define la estrategia de implementación para el lanzamiento del MVP de RaiSE. Se establece una separación estricta entre la **Capa de Interacción (Slash Commands)** y la **Capa de Sistema (CLI Binario)**.

## 1. Tabla Maestra de Versiones

Resumen ejecutivo de la disponibilidad de funcionalidades.

| Funcionalidad | Comando Slash (Prompt/IDE) | Versión | Comando CLI (Binario/Terminal) | Versión |
| :--- | :--- | :--- | :--- | :--- |
| **Inicialización** | `/init` | **v0.1** | `raise init` | **v0.1** |
| **Análisis** | `/analysis` | **v0.1** | `raise analysis` | **v0.1** |
| **Contexto** | `/pull` | **v0.1** | `raise pull` | **v0.1** |
| **Reglas** | `/rule` | **v0.1** | `raise rule` | v0.2 |
| **Ejecución (Coding)**| `/kata` | **v0.1** | `raise kata` | *Descartado* |
| **Auditoría/Logs** | `/audit` | v0.3 | `raise audit` | **v0.1** |
| **Validación** | `/check` | **v0.1** | `raise check` | v0.2 |
| **Aprobación** | `/gate` | v0.2 | `raise gate` | v0.2 |

---

## 2. Desglose Detallado por Versión

### 🚀 Versión v0.1: MVP "Core Loop" (Salida a Producción)
**Objetivo:** Habilitar el ciclo *Configurar -> Entender -> Trabajar -> Fichar*.
En esta fase, confiamos en la inteligencia del LLM (Slash) y usamos el CLI solo para tareas de sistema de archivos y logging básico.

#### A. Capa de Sistema (CLI Binario)
Estos comandos deben estar programados y funcionales en el binario `raise`.

1.  **`raise init`**
    * **Propósito:** Nacer. Crea la estructura física del proyecto.
    * **Acción:** Genera la carpeta `.raise/`, crea `.raise/trace/` y un archivo `raise.yaml` plantilla.

2.  **`raise analysis`**
    * **Propósito:** Ver. Genera el mapa del territorio (vital para Brownfield).
    * **Acción:** Escanea el directorio actual y genera:
        * `file-tree.txt`: Estructura de archivos.
        * `dependencies.txt` (básico): Lista de requirements/package.json.

3.  **`raise pull`**
    * **Propósito:** Recordar. Prepara el contexto para la IA.
    * **Acción:** Empaqueta documentación clave (`.raise/docs`, `.cursor/rules`, `raise.yaml`) y el estado actual del código en un archivo de contexto (`context.xml` o clipboard) listo para el prompt.

4.  **`raise audit`**
    * **Propósito:** Fichar. Persistencia mínima de actividad.
    * **Acción:** Escribe una entrada de texto simple con timestamp en `.raise/trace/session-[date].log`.
    * **Uso:** El usuario lo ejecuta manualmente al terminar una tarea: `raise audit "Implementado login v1"`.

#### B. Capa de Interacción (Slash Commands)
Estos son los **Prompts Maestros** que el usuario utiliza en el chat.

1.  **`/init`**
    * **Función:** Asistente de Configuración.
    * **Lógica:** Entrevista al usuario para definir el Nombre del Proyecto, Dominio y Estilo Técnico, y le pide que rellene el `raise.yaml`.

2.  **`/analysis`**
    * **Función:** Arquitecto de Software.
    * **Lógica:** Consume la salida de `raise analysis` y redacta el `service-overview.md` y `contracts.yaml`. Convierte listas de archivos en comprensión semántica.

3.  **`/rule`**
    * **Función:** Legislador.
    * **Lógica:** Analiza el código o la petición del usuario y redacta un archivo `.mdc` válido. Instruye al LLM para guardar este archivo directamente en `.cursor/rules/`.
    * **Nota:** Suple la falta del compilador CLI en v0.1.

4.  **`/kata`**
    * **Función:** Jefe de Obra.
    * **Lógica:** El prompt que orquesta la ejecución. Contiene las instrucciones paso a paso: "Lee el contexto, planifica, escribe código, verifica".

5.  **`/check`**
    * **Función:** Juez Semántico.
    * **Lógica:** "Analiza el código que acabas de generar. ¿Cumple con los requisitos A, B y C que te pedí? ¿Ves errores lógicos obvios?".

---

### 🛠️ Versión v0.2: Estabilidad y Calidad (Fast Follow)
**Objetivo:** Introducir automatización dura y reducir la carga cognitiva del usuario.

* **`raise check` (CLI):** Se integra con el sistema local. Ejecuta `npm test` o `pytest` y devuelve el código de salida.
* **`raise gate` (CLI):** Impide avanzar si no se cumplen métricas (ej. coverage < 80%).
* **`raise rule` (CLI):** Compilador real. Valida que los `.mdc` no se contradigan y los optimiza.
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
3.  **Definición:** `/rule` (Chat).
4.  **Desarrollo:** `raise pull` (Terminal) -> `/kata` (Chat).
5.  **Cierre:** `/check` (Chat) -> `raise audit` (Terminal).