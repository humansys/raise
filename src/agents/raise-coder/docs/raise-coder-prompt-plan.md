# Plan: Creación del System Prompt para el Agente "raise-coder"

## 1. Objetivo

Definir un System Prompt robusto y efectivo para el agente `raise-coder`. Este agente tendrá la responsabilidad de:
- Implementar historias de usuario.
- Resolver bugs.
- Realizar tareas de codificación general dentro del monorepo `raise-roome-poc`.
- Adherirse estrictamente a los **principios RaiSE** (requiere definición detallada).
- Seguir las **normas y reglas organizacionales** definidas (como las reglas `001` a `400`).
- Operar de manera autónoma y colaborativa, utilizando las herramientas disponibles de forma eficiente.

## 2. Componentes del Prompt (Basado en Best Practices)

El prompt se estructurará siguiendo las mejores prácticas para prompts agénticos:

1.  **Rol:** Definir la persona del agente (e.g., "Eres `raise-coder`, un asistente experto en desarrollo full-stack especializado en el stack tecnológico de RaiSE...")
2.  **Objetivo:** Especificar claramente las metas principales (implementación de features, corrección de bugs, refactoring) alineadas con los principios RaiSE y las reglas.
3.  **Contexto:** Proveer información sobre el entorno:
    - Proyecto: Monorepo `raise-roome-poc`.
    - Stack tecnológico principal: React, Next.js (App Router), TypeScript, Redux Toolkit, Styled Components, Nx.
    - Metodología: Principios RaiSE.
    - Herramientas disponibles: Acceso al código, búsqueda semántica, lectura de archivos, ejecución de comandos, edición de código, etc.
4.  **Directrices (Guidelines):** Instrucciones detalladas y restricciones:
    - **Principios RaiSE:** Incorporar los principios fundamentales una vez definidos.
    - **Reglas de Codificación:** Integrar o referenciar explícitamente las reglas clave de:
        - `001-core-setup`: Formato, Nomenclatura, Importaciones, Comentarios.
        - `100-typescript`: Tipado fuerte, `unknown` vs `any`, `interface` vs `type`, Enums.
        - `200-react-next`: Componentes funcionales, Hooks, Props (prefijo `i`), State (Redux/Local), App Router, Accesibilidad, Error Boundaries.
        - `210-use-redux-toolkit-primary`: Uso de Redux Toolkit como gestor de estado global.
        - `300-nx-monorepo`: Límites entre libs/apps, Alias, Gestión de dependencias, Comandos Nx.
        - `400-styling`: Styled Components (`.styled.tsx`), Props transitorias (`$`), Theming.
    - **Comportamiento Agéntico:**
        - Descomposición de tareas complejas.
        - Solicitud de clarificaciones cuando sea necesario.
        - Explicación del razonamiento (Chain-of-Thought implícito o explícito).
        - Uso adecuado y justificado de las herramientas disponibles (e.g., leer antes de editar).
        - Manejo de errores y auto-corrección (si es posible).
        - Estilo de comunicación (proactivo, claro, conciso).
5.  **Conocimiento (Knowledge):** Indicar las fuentes de información primarias:
    - Contenido de los archivos del workspace.
    - Reglas proporcionadas (y la capacidad de usar `fetch_rules`).
    - Historial de la conversación.
    - *Evitar depender de conocimiento externo no verificable.*
6.  **Formato de Salida:** Especificar cómo debe presentar la información:
    - Explicaciones claras.
    - Uso de bloques de código para sugerencias (cuando no se usa `edit_file`).
    - Formato específico para planes de acción.
    - Confirmación de aplicación de cambios (`edit_file`).

## 3. Técnicas Avanzadas a Considerar

- **Chain-of-Thought (CoT):** Instruir al agente para que "piense paso a paso" o explique su razonamiento antes de actuar, especialmente para tareas complejas.
- **ReAct (Reason + Act):** Si se requiere interacción compleja con herramientas o planificación dinámica, estructurar el prompt para facilitar ciclos de razonamiento y acción.
- **Salidas Estructuradas:** Definir formatos (quizás JSON implícito o markdown estructurado) para planes o resúmenes complejos.

## 4. Recopilación de Información Específica

- **Definir Principios RaiSE:** Es crucial obtener una definición clara y accionable de estos principios para incorporarlos en las `Directrices`.
- **Confirmar Herramientas:** Asegurarse de que la lista de herramientas disponibles para el agente es correcta y que el prompt instruye sobre su uso adecuado.
- **Refinar Reglas:** Revisar si las reglas `001-400` son exhaustivas o si necesitan ajustes para el contexto del agente.

## 5. Estrategia de Iteración y Evaluación

1.  **Versión Inicial (Draft):** Crear una primera versión del prompt basada en este plan.
2.  **Pruebas Funcionales:** Evaluar el prompt con casos de uso típicos:
    - Implementar una historia de usuario simple.
    - Corregir un bug conocido.
    - Realizar un refactor pequeño siguiendo una regla específica.
    - Responder a una pregunta sobre el código.
3.  **Análisis de Resultados:** Revisar las respuestas, el uso de herramientas y la adherencia a las reglas.
4.  **Refinamiento:** Ajustar el prompt basándose en los resultados de las pruebas (claridad, especificidad, directrices).
5.  **Pruebas de Estrés:** Evaluar con tareas más complejas o ambiguas.
6.  **Feedback Continuo:** Recopilar feedback de los usuarios una vez el agente esté en uso.

## 6. Estructura del Documento del Prompt

El prompt final debe ser un documento de texto claro y bien estructurado, preferiblemente en Markdown, siguiendo la estructura definida en el punto 2. 