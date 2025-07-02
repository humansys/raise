# **Guía Técnica Creación de System Prompts con Sonnet 3.5**  

## **1\. Introducción**

### **1.1 El Auge de la IA Agéntica en el Desarrollo de Software**

El desarrollo de software está experimentando una transformación significativa impulsada por los avances en la inteligencia artificial (IA). Más allá de la simple asistencia en la codificación o la finalización de código, están surgiendo sistemas de IA agénticos. Estos agentes aspiran a un mayor grado de autonomía, capaces no solo de escribir código, sino también de planificar tareas complejas, interactuar con herramientas, realizar pruebas, depurar errores y refactorizar bases de código existentes.1 Modelos como Claude 3.5 Sonnet demuestran capacidades crecientes en este dominio, permitiendo flujos de trabajo donde la IA actúa más como un colaborador proactivo que como una simple herramienta pasiva.

El corazón de la dirección de estos agentes reside en la ingeniería de "system prompts" (instrucciones de sistema). Estos prompts actúan como la constitución o el conjunto de directrices fundamentales que moldean el comportamiento, la personalidad, el enfoque y las limitaciones del agente de IA al abordar una tarea.10 Un system prompt bien diseñado es crucial para canalizar las potentes capacidades del modelo hacia resultados productivos, fiables y alineados con los objetivos del desarrollador.

### **1.2 Enfoque: Claude Sonnet 3.5 (Oct 2024\) como Socio Agéntico de Codificación**

Esta guía se centra exclusivamente en **Claude Sonnet 3.5**, específicamente en su iteración más reciente referenciada contextualmente como la versión de Octubre de 2024\. Este modelo, parte de la familia Claude 3.5 de Anthropic, se ha posicionado como una herramienta particularmente potente para el desarrollo de software agéntico. Destaca por su sólida competencia en codificación, sus avanzadas capacidades de razonamiento y su habilidad para seguir instrucciones complejas, a menudo superando a modelos anteriores como Claude 3 Opus e incluso a competidores en diversas evaluaciones relevantes para el desarrollo.1

Si bien existen otros modelos capaces (como Opus para tareas complejas de escritura o Haiku para velocidad, y competidores como Gemini o GPT 1), Sonnet 3.5 ofrece un equilibrio convincente entre inteligencia, velocidad y coste, haciéndolo ideal para tareas agénticas como la implementación de características, la depuración y la refactorización.1 Su rendimiento en evaluaciones de codificación agéntica y su capacidad para utilizar herramientas proporcionadas por el usuario lo convierten en un candidato principal para actuar como un socio de codificación autónomo.1

### **1.3 Propósito y Estructura de esta Guía**

El objetivo de esta guía es proporcionar un recurso técnico exhaustivo y práctico para desarrolladores que buscan crear system prompts agénticos efectivos específicamente para Claude Sonnet 3.5 en el dominio del desarrollo de software. Se basa en una síntesis de las mejores prácticas recomendadas por Anthropic, la documentación oficial y las experiencias prácticas, consejos y ejemplos compartidos por la comunidad de desarrolladores, con un enfoque particular en el ecosistema de herramientas como Cursor, donde estos agentes se implementan frecuentemente.

La guía se estructura de la siguiente manera:

1. **Comprensión de Claude Sonnet 3.5 para Codificación Agéntica:** Detalla las capacidades relevantes, fortalezas y matices del modelo.  
2. **Principios Fundamentales de Prompting Agéntico (Recomendaciones de Anthropic):** Explora las técnicas clave respaldadas por la documentación oficial.  
3. **Técnicas Impulsadas por la Comunidad (Ecosistema Cursor):** Analiza estructuras y enfoques prácticos desarrollados por usuarios.  
4. **Ejemplos Concretos de System Prompts:** Proporciona plantillas anotadas para tareas de implementación, depuración y refactorización.  
5. **Optimización y Mitigación de Problemas:** Ofrece estrategias para maximizar el rendimiento y abordar posibles dificultades.

## **2\. Comprensión de Claude Sonnet 3.5 para Codificación Agéntica**

Para diseñar prompts efectivos, es fundamental comprender las capacidades específicas y las particularidades de Claude Sonnet 3.5 en el contexto de tareas agénticas de software.

### **2.1 Visión General de Capacidades Relevantes**

* **Competencia en Codificación:** Claude Sonnet 3.5 ha demostrado un rendimiento sobresaliente en benchmarks de codificación estándar como HumanEval y evaluaciones más complejas orientadas a la ingeniería de software del mundo real como SWE-bench.1 Es capaz de escribir, editar, ejecutar, traducir (útil para modernizar código legacy) y solucionar problemas de código de forma independiente cuando se le proporcionan las herramientas e instrucciones adecuadas.1 Su capacidad para abordar tareas agénticas, como corregir errores o añadir funcionalidades basadas en descripciones en lenguaje natural, es una de sus fortalezas clave.1  
* **Razonamiento y Seguimiento de Instrucciones:** El modelo establece nuevos benchmarks en razonamiento a nivel de posgrado (GPQA) y conocimiento a nivel universitario (MMLU).1 Muestra una mejora notable en la comprensión de matices, humor e instrucciones complejas, y es excepcional en la ejecución de flujos de trabajo de múltiples pasos.1 Existe un modo de "pensamiento extendido" que puede activarse mediante frases específicas como "piensa", "piensa detenidamente" ("think hard"), lo que asigna más presupuesto computacional para tareas de planificación o depuración complejas.27  
* **Uso de Herramientas:** Una capacidad crucial para los agentes es interactuar con el mundo exterior. Claude puede utilizar herramientas externas (APIs, funciones locales, comandos de terminal) pero estas deben ser definidas explícitamente por el usuario en la solicitud API; el modelo no posee herramientas incorporadas.19 Sonnet 3.5 demuestra una buena capacidad para el uso complejo de herramientas y para buscar clarificaciones cuando las instrucciones o los parámetros de las herramientas son ambiguos.19 Ha mostrado mejoras en benchmarks específicos de uso de herramientas agénticas como TAU-bench.7  
* **Ventana de Contexto:** Sonnet 3.5 opera con una ventana de contexto de 200,000 tokens.1 Esta amplia ventana es ventajosa para tareas agénticas que requieren comprender grandes bases de código o mantener el contexto a lo largo de interacciones prolongadas, aunque la gestión eficaz sigue siendo importante.10  
* **Capacidades de Visión:** Aunque no es el enfoque principal de esta guía, cabe destacar que Sonnet 3.5 es el modelo de visión más potente de Anthropic hasta la fecha, superando a Opus en benchmarks de visión.1 Puede interpretar gráficos, diagramas e incluso transcribir texto de imágenes imperfectas.1 Esto puede ser relevante para tareas de desarrollo de UI, depuración de elementos visuales o comprensión de documentación gráfica.

### **2.2 Fortalezas y Matices para Tareas Agénticas de Software**

* **Fortalezas:** Resumiendo lo anterior, Sonnet 3.5 brilla en la codificación, depuración y refactorización agéntica gracias a su sólida competencia técnica, seguimiento de instrucciones complejas, razonamiento avanzado, amplia ventana de contexto y uso eficaz de herramientas (cuando están bien definidas).1 La comunidad de desarrolladores, especialmente en entornos como Cursor, a menudo lo prefiere para tareas agénticas en comparación con otros modelos disponibles en momentos similares.21  
* **Matices / Debilidades Potenciales:** A pesar de sus fortalezas, los usuarios y las evaluaciones han observado ciertos matices. El modelo puede ser verboso, tender a la sobreingeniería o realizar cambios no solicitados si las instrucciones no son lo suficientemente restrictivas.4 Puede haber pérdida ocasional de contexto o generación de "alucinaciones" en interacciones muy largas o complejas.17 Su rendimiento es sensible a la estructura y claridad del prompt.42 Pueden surgir problemas de fiabilidad, como quedarse atascado en bucles de depuración o fallar en el uso de herramientas si no están perfectamente definidas.17 El rendimiento también puede degradarse si la ventana de contexto se llena excesivamente.41

Una observación clave derivada de estos puntos es la naturaleza de doble filo de la capacidad agéntica de Sonnet 3.5. Su fortaleza radica en su capacidad para tomar la iniciativa y realizar tareas de forma autónoma: escribir, editar y ejecutar código.1 Sin embargo, esta misma proactividad puede convertirse en una debilidad si no se guía adecuadamente. Los informes de la comunidad sobre el modelo actuando como un "idiota proactivo" 30, realizando cambios no deseados 4 o complicando excesivamente las soluciones 40 sugieren que su impulso inherente para completar tareas puede llevarlo a hacer suposiciones o tomar iniciativas más allá de la intención explícita del usuario, especialmente si el prompt carece de restricciones claras. El proceso interno del modelo podría priorizar la finalización de la tarea sobre la adherencia estricta a los cambios mínimos necesarios. Esto implica que los system prompts agénticos para Sonnet 3.5 deben definir no solo el *objetivo* de la tarea, sino también establecer cuidadosamente los *límites* y *restricciones* de las acciones del agente. Técnicas como las restricciones negativas explícitas ("NO modifiques código no relacionado"), exigir planes paso a paso antes de la ejecución 27, y potencialmente el uso de agentes supervisores 45 se vuelven fundamentales para gestionar esta proactividad. Existe una tensión inherente entre empoderar al agente y mantener el control, un aspecto central para el diseño efectivo de prompts agénticos para Sonnet 3.5.

## **3\. Principios Fundamentales de Prompting Agéntico para Sonnet 3.5 (Recomendaciones de Anthropic)**

Anthropic proporciona directrices y técnicas clave para interactuar eficazmente con sus modelos Claude. Aplicar estos principios es fundamental para construir system prompts robustos para agentes Sonnet 3.5.

### **3.1 Definición de Roles: El Poder de los System Prompts**

La forma más potente de utilizar los system prompts con los modelos Claude es mediante la **definición de roles** (role prompting).11 Esto implica asignar explícitamente una personalidad, experiencia o función específica al modelo antes de presentarle la tarea concreta.

* **Uso del Parámetro system:** La práctica recomendada es definir el rol dentro del parámetro system de la API de Mensajes. Las instrucciones específicas de la tarea deben ir en el turno del user.11 Esta separación ayuda al modelo a distinguir entre su identidad/contexto general y la solicitud inmediata.  
* **Especificidad del Rol:** Es crucial definir roles específicos y relevantes para la tarea de desarrollo de software. En lugar de un genérico "Actúa como un programador", se deben usar roles más detallados que enfoquen el conocimiento y el estilo de respuesta del modelo. Ejemplos efectivos incluyen:  
  * "Eres un ingeniero de software senior con 10 años de experiencia en Python y desarrollo web, especializado en la creación de APIs RESTful seguras y escalables." 11  
  * "Eres un experto en depuración de aplicaciones React, meticuloso en la identificación de causas raíz y en la propuesta de soluciones limpias y eficientes." 11  
  * "Eres un revisor de código enfocado en la seguridad, con experiencia en identificar vulnerabilidades comunes (XSS, SQL Injection, etc.) en aplicaciones Java." 11  
  * "Eres un arquitecto técnico especializado en microservicios, responsable de diseñar sistemas resilientes y mantenibles." 11 La especificidad ayuda a Claude a activar las partes más relevantes de su entrenamiento y a adoptar el tono y nivel de detalle apropiados.

### **3.2 Estructuración de Prompts: Aprovechando las Etiquetas XML para Mayor Claridad**

Los modelos Claude, incluido Sonnet 3.5, han sido entrenados para prestar especial atención a las etiquetas XML.10 El uso de estas etiquetas para estructurar el prompt ofrece beneficios significativos:

* **Claridad:** Delimitan claramente las diferentes secciones del prompt (instrucciones, contexto, ejemplos, etc.).  
* **Precisión:** Reducen la ambigüedad y ayudan al modelo a interpretar correctamente cada parte.  
* **Flexibilidad:** Facilitan la modificación y gestión de prompts complejos.  
* **Parseabilidad:** Permiten extraer fácilmente información específica de la respuesta del modelo si se le instruye a usar etiquetas en su salida. 46

Aunque no hay etiquetas "canónicas" estrictas, se recomienda usar nombres lógicos y descriptivos. Las prácticas clave incluyen la **consistencia** en el uso de nombres de etiquetas y el **anidamiento** para contenido jerárquico.46

**Ejemplos de Etiquetas Comunes para Prompts Agénticos:**

* \<instructions\>: Para las directivas principales de la tarea.  
* \<context\>: Para proporcionar información de fondo, como fragmentos de código relevantes, descripciones de arquitectura o guías de estilo.  
* \<code\_to\_analyze\> o \<code\_to\_refactor\>: Para delimitar el código específico que el agente debe procesar.  
* \<user\_query\>: Para encerrar la solicitud específica del usuario dentro de un prompt más amplio.  
* \<example\>: Para proporcionar ejemplos de entrada/salida deseados (few-shot prompting).  
* \<output\_format\>: Para especificar el formato de salida requerido (ej. JSON, Markdown).  
* \<thinking\>: Para instruir al modelo a realizar su razonamiento paso a paso (ver 3.3).  
* \<plan\>: Para solicitar un plan de acción antes de la ejecución.  
* \<security\_review\>: Para solicitar un análisis de seguridad específico.43  
* \<tool\_definition\> / \<available\_tools\>: Para definir las herramientas que el agente puede usar (ver 3.6).  
* \<constraints\> / \<negative\_constraints\>: Para especificar límites o acciones prohibidas.

10

### **3.3 Guiando el Razonamiento: Cadena de Pensamiento (CoT) y Pensamiento Paso a Paso**

Para tareas complejas que requieren planificación, análisis o depuración, guiar el proceso de razonamiento de Sonnet 3.5 es crucial. La técnica de **Cadena de Pensamiento (Chain of Thought \- CoT)** anima al modelo a descomponer el problema en pasos intermedios antes de llegar a la respuesta final, lo que mejora la precisión y la coherencia.10

* **Métodos de Implementación de CoT:**  
  * **Instrucción Simple:** Incluir la frase "Piensa paso a paso" ("Think step-by-step") en el prompt.10  
  * **Pasos Guiados:** Delinear explícitamente los pasos que el modelo debe seguir en su razonamiento.51  
  * **Prompting Estructurado (XML):** Utilizar etiquetas como \<thinking\> para el proceso de razonamiento y \<answer\> (u otras etiquetas específicas como \<plan\>, \<fix\>) para la salida final.10 Este es a menudo el método más efectivo.  
* **Uso Efectivo de \<thinking\>:**  
  * Instruir explícitamente al modelo para que realice su razonamiento dentro de estas etiquetas.  
  * Animar a descomponer la tarea en subproblemas lógicos dentro de \<thinking\>.  
  * Para tareas numéricas o lógicas, solicitar que se muestren los cálculos o pasos intermedios.  
  * Para análisis, pedir que se articule la lógica y las consideraciones.  
  * Asegurar una clara separación entre el contenido de \<thinking\> y la salida final en \<answer\> u otras etiquetas designadas. 10  
* **Pensamiento Extendido:** Para tareas que requieren una planificación o análisis más profundos, se puede invocar un modo de "pensamiento extendido" utilizando frases específicas que asignan progresivamente más presupuesto computacional: "piensa" \< "piensa detenidamente" ("think hard") \< "piensa aún más detenidamente" ("think harder") \< "ultrapensamiento" ("ultrathink").27 Esto puede ser particularmente útil al pedirle al agente que genere un plan complejo o analice casos límite.

### **3.4 Claridad en las Instrucciones: Proporcionando Ejemplos y Directivas Efectivas**

La calidad de la salida de Sonnet 3.5 depende en gran medida de la claridad y precisión de las instrucciones proporcionadas.

* **Instrucciones Claras y Directas:** Evitar la ambigüedad. Ser explícito sobre los requisitos, el alcance y las expectativas.10  
* **Ejemplos (Few-Shot Prompting):** Proporcionar ejemplos concretos del comportamiento, formato o estilo de salida deseado es una forma poderosa de guiar al modelo.10 Los ejemplos deben ser relevantes, claros y diversos. Comenzar con 3-5 ejemplos suele ser un buen punto de partida.10  
* **Especificación de Formato:** Indicar explícitamente el formato de salida deseado (ej. JSON, Markdown, lista de pasos).10  
* **Prellenado de Respuesta:** Para guiar la estructura inicial de la respuesta y evitar introducciones innecesarias, se puede proporcionar el comienzo de la respuesta esperada en el turno del assistant.10  
* **Restricciones (Positivas y Negativas):** Definir claramente lo que el agente *debe* hacer y, crucialmente, lo que *no debe* hacer. Ejemplos: "Implementa la función usando TDD", "NO modifiques los archivos de prueba existentes", "NUNCA expongas claves de API en el código", "Utiliza únicamente las funciones definidas en \<allowed\_functions\>".10

### **3.5 El Contexto es Clave: Técnicas para una Gestión Eficaz del Contexto**

Proporcionar el contexto adecuado es vital para que un agente de software funcione eficazmente. Sonnet 3.5 necesita comprender la estructura del código base, las dependencias relevantes, las guías de estilo y otros detalles del proyecto.

* **Provisión de Contexto Relevante:** Incluir información esencial como la estructura del proyecto, archivos clave, dependencias, guías de estilo, etc., en el prompt o a través de mecanismos de carga de contexto.12  
* **CLAUDE.md (Mejor Práctica):** Inspirado en la herramienta claude-code de Anthropic, crear un archivo CLAUDE.md en la raíz del proyecto (o en subdirectorios) es una excelente práctica para proporcionar contexto persistente. Este archivo puede contener comandos bash comunes, descripción de archivos/utilidades centrales, guías de estilo, instrucciones de prueba, configuración del entorno, etc..27 Se recomienda iterar y refinar el contenido de CLAUDE.md como si fuera un prompt en sí mismo.27  
* **Gestión de Conversaciones Largas:** En interacciones prolongadas o flujos de trabajo complejos, la ventana de contexto de 200K tokens 1 puede llenarse. Estrategias para mitigar esto incluyen:  
  * Usar comandos como /clear (si la herramienta lo soporta) para reiniciar el contexto.27  
  * Descomponer tareas grandes en subtareas más pequeñas y manejarlas en interacciones separadas.  
  * Utilizar archivos externos (como Markdown o issues de GitHub) como "checklists" o "scratchpads" para que el agente rastree el progreso en lugar de depender únicamente del historial de conversación.27  
  * Ser consciente de las acciones que pueden invalidar la caché de contexto en algunas herramientas (ediciones manuales, pausas largas).39

### **3.6 Dominio del Uso de Herramientas: Definición, Invocación y Mejores Prácticas**

La capacidad de un agente para interactuar con el mundo exterior depende de su habilidad para usar herramientas (funciones, APIs, comandos).

* **Definición Explícita:** Reiterar que todas las herramientas deben definirse explícitamente en la solicitud API, incluyendo name (identificador único), description (descripción detallada) e input\_schema (esquema JSON para parámetros).19  
* **Descripciones Detalladas (CRÍTICO):** Este es el factor más importante para el rendimiento de las herramientas.19 La descripción debe explicar exhaustivamente:  
  * Qué hace la herramienta.  
  * Cuándo debe (y no debe) usarse.  
  * El significado de cada parámetro y su efecto.  
  * Advertencias o limitaciones importantes (qué información *no* devuelve).  
  * Se recomiendan al menos 3-4 frases por descripción, más si es compleja.19 La claridad aquí es primordial; pensar en ello como escribir una excelente docstring para un desarrollador junior.56  
* **Parámetro tool\_choice:** Comprender las opciones (auto, any, tool, none) y sus implicaciones.19  
  * auto (predeterminado con herramientas): Permite a Claude decidir si usar o no una herramienta.  
  * any: Obliga a Claude a usar *alguna* de las herramientas proporcionadas.  
  * tool: Obliga a Claude a usar una herramienta *específica*.  
  * none (predeterminado sin herramientas): Impide el uso de herramientas.  
  * Nota: Forzar el uso (any o tool) puede suprimir la salida de la cadena de pensamiento (\<thinking\>) antes del bloque tool\_use. Para mantener CoT mientras se sugiere una herramienta específica, usar auto y guiar en el prompt del usuario.19  
* **Diseño de Herramientas "a Prueba de Errores" (Poka-yoke):** Modificar los argumentos o el comportamiento de la herramienta para hacer más difícil que el modelo cometa errores.56 Ejemplos: exigir rutas absolutas en lugar de relativas para herramientas de edición de archivos 17, o usar métodos de reemplazo de cadenas específicos y seguros para ediciones.17  
* **Pruebas Exhaustivas:** Es fundamental probar cómo el modelo utiliza las herramientas con diversas entradas para identificar y corregir errores o ambigüedades en la definición o descripción.56

## **4\. Técnicas Impulsadas por la Comunidad para Desarrollo de Software con Sonnet 3.5 (Perspectivas del Ecosistema Cursor)**

Mientras que Anthropic proporciona los principios fundamentales, la comunidad de desarrolladores, especialmente dentro de ecosistemas como Cursor (un editor de código enfocado en IA), ha desarrollado y compartido estructuras de prompts, reglas y flujos de trabajo prácticos para aplicar estos principios a tareas de desarrollo de software con modelos como Sonnet 3.5.

### **4.1 Estructuras de Prompt Fiables (ej. patrones core.md, request.md)**

La comunidad ha experimentado con plantillas de prompts estructuradas para guiar consistentemente el comportamiento del agente. Un ejemplo notable es el conjunto de plantillas core.md, refresh.md y request.md 57:

* **core.md (Reglas Fundamentales):** Actúa como el system prompt base persistente. Define la personalidad central del agente (ej. "colega senior meticuloso"), su enfoque (comprensión profunda, planificación estratégica, ejecución diligente, verificación rigurosa), directrices de seguridad (integridad del sistema, aprobación para acciones de riesgo), estilo de comunicación (conciso, enfocado en resultados) y principios de aprendizaje continuo.57 Estas reglas fundamentales buscan establecer un comportamiento consistente, cauteloso y efectivo.  
* **request.md (Implementación de Características/Modificaciones):** Es una plantilla específica para tareas de implementación. Comienza con la solicitud del usuario y luego enfatiza aspectos clave de core.md relevantes para la implementación: análisis profundo, evaluación de impacto/dependencias, estrategia óptima, validación exhaustiva, ejecución segura e informes concisos.57 Guía al agente a través de los pasos de planificación, validación, implementación y verificación para nuevas características o refactorizaciones.  
* **refresh.md (Diagnóstico de Problemas Persistentes):** Se utiliza cuando intentos previos de depuración han fallado. Guía al agente a través de un proceso riguroso de re-diagnóstico: dar un paso atrás, redefinir el alcance, mapear la estructura del sistema, hipotetizar causas raíz (ampliamente), investigar sistemáticamente con herramientas, identificar la causa raíz confirmada (basada en evidencia, no suposiciones), proponer una solución específica, planificar una verificación completa, ejecutar y verificar, e informar el resultado.57

Estas estructuras implementan principios de Anthropic como la definición de roles (persona central), el pensamiento paso a paso (planificación, diagnóstico sistemático), la importancia de la verificación y la necesidad de instrucciones claras. Otros ejemplos compartidos por la comunidad 58 a menudo siguen patrones similares, definiendo roles, estándares de codificación, procesos de pensamiento y formatos de salida deseados.

### **4.2 Aprovechamiento de las Reglas de Cursor para Contexto y Barreras de Seguridad**

Cursor ofrece un sistema de reglas sofisticado que permite a los desarrolladores guiar el comportamiento de la IA y proporcionar contexto específico del proyecto, complementando o implementando el system prompt principal.

* **Tipos de Reglas:**  
  * **Reglas Globales (User Rules):** Definidas en la configuración de Cursor, se aplican a todos los proyectos. Son texto plano y actúan como un system prompt global base.62  
  * **Reglas de Proyecto (.cursorrules / .cursor/rules/\*.mdc):** Específicas de un repositorio. El formato .cursorrules (un solo archivo en la raíz) parece estar siendo reemplazado por el sistema más granular de archivos .mdc dentro del directorio .cursor/rules/.64 Estas reglas de proyecto suelen tener prioridad sobre las reglas globales.57  
* **Estructura de Reglas de Proyecto (.mdc):** Estos archivos utilizan un formato llamado MDC (Markdown Content) que combina metadatos YAML en un bloque frontal (---) con el contenido de la regla en Markdown.64  
  * **Metadatos:** Definen cómo y cuándo se aplica la regla. Campos clave incluyen description (para que el agente entienda el propósito de la regla), globs (patrones de archivo tipo gitignore para activar la regla) y alwaysApply (booleano, relevante para Auto Attached).69  
  * **Cuerpo Markdown:** Contiene las instrucciones, directrices o contexto. Puede incluir referencias a otros archivos del proyecto usando la sintaxis @nombre\_archivo.ext, lo que permite incluir contexto adicional dinámicamente.64  
* **Tipos de Activación de Reglas de Proyecto:** Los metadatos determinan cómo se activa una regla .mdc:

| Tipo de Regla | Metadatos Clave Requeridos | Mecanismo de Activación | Caso de Uso Ejemplo | Snippets Relevantes |
| :---- | :---- | :---- | :---- | :---- |
| Always | Ninguno (implícito) | Siempre incluido en el contexto del modelo para todas las solicitudes en el proyecto. | Definir estándares de codificación globales del proyecto, personalidad base del agente. | 69 |
| Auto Attached | globs | Incluido automáticamente cuando se hace referencia a archivos que coinciden con globs. | Aplicar guías de estilo específicas (ej. Tailwind) a componentes React (components/\*\*/\*). | 64 |
| Agent Requested | description | Disponible para el agente; decide si incluirlo basándose en la descripción y el contexto. | Proporcionar una plantilla opcional para crear nuevos servicios Express. | 69 |
| Manual | Ninguno | Solo incluido si el usuario lo menciona explícitamente en el chat (ej. @mi\_regla). | Aplicar un conjunto específico de directrices de refactorización bajo demanda. | 69 |

Comprender estos tipos permite a los desarrolladores elegir la estrategia adecuada para proporcionar contexto o directrices: aplicar siempre, automáticamente según el archivo, permitir que el agente decida, o solo bajo demanda explícita. Esto ofrece un control granular sobre el contexto y el comportamiento del agente Sonnet 3.5 dentro de Cursor.

* **Uso Práctico:** Las reglas se utilizan para una variedad de propósitos:  
  * **Estándares de Codificación:** "Usar tipos estrictos en TypeScript", "Seguir las directrices de RuboCop".62  
  * **Contexto Específico:** "Este proyecto usa SolidJS, no React, para archivos.tsx" 65, "Usar objetos de servicio para lógica de negocio (ver @docs/architecture/services.md)".64  
  * **Definición de Comportamiento:** "Siempre explica la solución primero", "Pide aclaraciones si la tarea no está clara".65  
  * **Restricciones:** "Prohibir consultas SQL en las vistas" 64, "Requerir aprobación explícita para operaciones destructivas".71

### **4.3 Aprovechamiento del Modo Agente y Modos Personalizados de Cursor para Tareas Especializadas**

Cursor ha evolucionado para ofrecer modos de interacción específicos, permitiendo a los usuarios invocar diferentes niveles de autonomía y conjuntos de herramientas.

* **Modo Agente:** Es el modo predeterminado y más autónomo. Está diseñado para manejar tareas complejas con mínima supervisión.77  
  * **Capacidades:** Tiene acceso completo a herramientas (búsqueda en el código base, lectura/escritura de archivos, ejecución de terminal, búsqueda web), realiza razonamiento multi-paso, y puede explorar y modificar el código base de forma independiente.77 Puede realizar hasta 25 llamadas a herramientas antes de necesitar una continuación.78  
  * **Flujo de Trabajo:** Sigue un proceso sistemático: 1\) Comprender la solicitud y el contexto, 2\) Explorar el código base/web, 3\) Planificar los cambios, 4\) Ejecutar los cambios (código, archivos, comandos), 5\) Verificar los resultados (aplicando cambios, intentando arreglar errores de linter).77  
  * **Configuración:** Permite habilitar el modo "Yolo" para ejecución automática de comandos (útil para tests), definir barreras de seguridad para comandos de terminal, y se guía por las Reglas de Cursor.77  
* **Modos Personalizados (Beta):** Permiten a los usuarios crear sus propios modos con combinaciones específicas de herramientas habilitadas y prompts/instrucciones personalizadas, adaptados a flujos de trabajo particulares.79  
  * **Configuración:** Se definen a través de la interfaz de usuario (nombre, icono, atajo, herramientas, instrucciones).79 Se está considerando un archivo modes.json o similar (.cursor/agents/\*.mdc) para definirlos y compartirlos dentro del repositorio.74  
  * **Ejemplos Relevantes:** La documentación y la comunidad sugieren modos como:  
    * Learn: Enfocado en explicaciones detalladas, sin edición automática.79  
    * Refactor: Solo mejora código existente, sin añadir funcionalidad.79  
    * Plan: Genera planes detallados (ej. en plan.md) sin modificar código.79  
    * Research: Recopila información de múltiples fuentes antes de sugerir.79  
    * Debug: Investiga a fondo (archivos, terminal) antes de proponer arreglos.79  
    * TDD Assistant: Podría guiar a través de los pasos de TDD.  
    * Security Auditor: Enfocado en identificar vulnerabilidades.

La aparición y el énfasis en los Modos Personalizados 74 y los flujos de trabajo estructurados (como el flujo Agile 82 o patrones Supervisor/Trabajador 45) en la comunidad de Cursor sugieren una tendencia clara: descomponer el complejo ciclo de vida del desarrollo de software en tareas manejadas por agentes especializados (definidos a través de modos o prompts específicos) es una estrategia clave para lograr resultados fiables y efectivos con modelos potentes pero a veces impredecibles como Sonnet 3.5. Confiar en un único prompt de agente de propósito general para todo el proceso parece ser menos robusto que emplear múltiples prompts/agentes especializados adaptados a fases específicas (planificación, codificación, pruebas, depuración, refactorización) o dominios (frontend, backend, seguridad). Esto se alinea con las recomendaciones de Anthropic sobre el uso de subagentes 27 y la descomposición de tareas complejas 10, pero representa un patrón de implementación más concreto dentro de la herramienta Cursor. Por lo tanto, el prompting agéntico eficaz para Sonnet 3.5 en Cursor implica diseñar no solo prompts individuales, sino *flujos de trabajo* que aprovechen estos agentes especializados. Esto requiere una cuidadosa consideración de la descomposición de tareas, la definición de roles para cada agente/modo y, potencialmente, cómo se gestiona el estado/contexto entre pasos (por ejemplo, utilizando archivos compartidos como workflow\_state.md 83 o plan.md 79).

La siguiente tabla ofrece ejemplos de configuración para modos personalizados orientados a tareas comunes de desarrollo, sirviendo como plantillas prácticas:

| Nombre del Modo | Propósito | Instrucciones Clave (Resumen) | Herramientas Habilitadas (Ejemplos) | Auto-Aplicar/Ejecutar |
| :---- | :---- | :---- | :---- | :---- |
| Planner | Generar planes de implementación detallados sin modificar código. | "Analiza la solicitud. Investiga el código base. Crea un plan paso a paso detallado en plan.md. No edites código." | Búsqueda (Codebase, Web), Leer Archivo, Terminal (solo lectura) | No |
| Implementer (TDD) | Implementar código siguiendo un plan y principios TDD. | "Sigue el plan de plan.md. Escribe pruebas primero (si no existen). Implementa código para pasar pruebas. No modifiques pruebas." | Edición (Edit & Reapply), Terminal (para tests), Búsqueda (Codebase) | Opcional (Tests) |
| Debugger | Investigar y solucionar errores, priorizando la causa raíz. | "Analiza el error/síntoma. Investiga logs/código relacionado. Hipotetiza causas. Verifica con herramientas. Propón arreglo específico." | Búsqueda (Todas), Terminal, Edición (Edit & Reapply) | No (revisar arreglo) |
| Refactorer | Mejorar la estructura/calidad del código sin cambiar la lógica funcional. | "Enfócate únicamente en mejorar \[readability/performance/etc.\]. No añadas funcionalidad. Verifica con pruebas existentes." | Edición (Edit & Reapply), Búsqueda (Codebase), Terminal (para tests) | No (revisar cambios) |
| Security Auditor | Identificar posibles vulnerabilidades de seguridad en el código. | "Revisa el código en busca de vulnerabilidades comunes (OWASP Top 10, etc.). Explica los riesgos y sugiere mitigaciones seguras." | Búsqueda (Codebase), Leer Archivo | No |

Estas configuraciones son puntos de partida. Los desarrolladores deben ajustarlas según las especificidades de su proyecto, las herramientas disponibles (incluyendo servidores MCP personalizados 75) y el comportamiento observado de Sonnet 3.5.

### **4.4 Consejos Comunitarios para Flujos de Trabajo Específicos**

La comunidad ha compartido enfoques para tareas recurrentes:

* **Desarrollo Guiado por Pruebas (TDD):** Combinar el flujo de trabajo TDD recomendado por Anthropic (Escribir pruebas \-\> Confirmar fallo \-\> Commit \-\> Codificar \-\> Iterar hasta pasar \-\> Commit) 27 con prácticas comunitarias. Esto puede implicar el uso de prompts o modos personalizados distintos para la generación de pruebas y la implementación del código.82 Es crucial instruir al agente para que *no modifique* las pruebas durante la fase de implementación del código.27 La capacidad de Sonnet 3.5 para escribir pruebas y luego el código para pasarlas se ha demostrado.84  
* **Bucles de Depuración:** Utilizar estructuras como la plantilla refresh.md para un re-diagnóstico sistemático cuando los arreglos iniciales fallan.57 Pedir al agente que inserte declaraciones de registro descriptivas para rastrear el estado.85 Emplear Modos Personalizados de Debugger.79 Un enfoque estructurado puede ser pedirle al agente que genere una lista de verificación de errores (basada en la salida del linter o stack traces) y los aborde secuencialmente, verificando cada arreglo.27 Proporcionar mensajes de error claros y contexto de código relevante es fundamental. Recordar que el agente puede intentar arreglar errores de linter automáticamente, pero con un límite de intentos antes de pedir ayuda.12  
* **Patrones de Refactorización:** Usar Modos Refactor dedicados 79 o prompts que especifiquen claramente el objetivo (ej. "Refactoriza esta función para reducir la complejidad ciclomática", "Mejora la legibilidad de este módulo aplicando el principio SOLID", "Optimiza esta consulta para mejorar el rendimiento").76 Es vital proporcionar el objetivo de la refactorización y, si es posible, ejemplos del estilo deseado. La verificación (ej. ejecutar el conjunto de pruebas) después de la refactorización es indispensable.  
* **Planificación y Arquitectura:** Incorporar fases de planificación explícitas en el flujo de trabajo.82 Utilizar Modos Plan 79 que generen documentos de diseño (ej. en plan.md) antes de comenzar la implementación. Invocar el "pensamiento extendido" ("think hard", "ultrathink") para tareas de diseño arquitectónico complejas.27

## **5\. Creación de System Prompts Agénticos Efectivos: Ejemplos para Sonnet 3.5**

A continuación, se presentan ejemplos concretos de system prompts diseñados para Claude Sonnet 3.5 en tareas agénticas de desarrollo de software. Estos ejemplos integran los principios de Anthropic y las técnicas comunitarias discutidas anteriormente, utilizando etiquetas XML para la estructura.

*(Nota: Estos prompts asumen un entorno como Cursor donde el agente tiene acceso a herramientas para interactuar con el código base y potencialmente ejecutar comandos. Los nombres y capacidades exactas de las herramientas (codebase\_search, edit\_file, run\_terminal) deben adaptarse al entorno específico.)*

### **5.1 Ejemplo 1: Prompt de Agente para Implementación de Funcionalidad (Enfoque TDD)**

* **Título:** Agente de Implementación Python TDD para Autenticación JWT  
* **Objetivo:** Implementar un nuevo endpoint de autenticación de usuarios (/login) y generación de tokens JWT en una aplicación backend Python Flask, siguiendo estrictamente el flujo de trabajo TDD.  
* **Contexto Asumido:** Acceso a herramientas edit\_file (para leer/escribir archivos), run\_terminal (para ejecutar pytest), codebase\_search. El proyecto utiliza Flask, PyJWT y Pytest. Existe una guía de estilo PEP 8\.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Ingeniero de Software Python Senior experto en desarrollo backend con Flask y un firme practicante del Desarrollo Guiado por Pruebas (TDD). Tu objetivo es implementar nuevas funcionalidades de manera robusta y bien probada. Eres meticuloso, sigues las instrucciones al pie de la letra y priorizas la calidad y la mantenibilidad del código.

  \</role\>

  \<instructions\>  
    La tarea del usuario será implementar una nueva funcionalidad. Debes seguir estrictamente el siguiente flujo de trabajo TDD:  
    1\.  \*\*Análisis y Planificación:\*\* Basado en la \<user\_query\>, analiza los requisitos. Identifica los archivos relevantes (modelos, rutas, utilidades) usando \`codebase\_search\` si es necesario. Formula un plan detallado para la implementación dentro de etiquetas \<plan\>. El plan debe incluir qué pruebas se escribirán. Pide confirmación del plan al usuario antes de proceder.  
    2\.  \*\*Escritura de Pruebas:\*\* Una vez confirmado el plan, escribe las pruebas unitarias y/o de integración necesarias usando Pytest para la nueva funcionalidad. Coloca las pruebas en el archivo/directorio apropiado (ej. \`tests/test\_auth.py\`). Usa \`edit\_file\` para crear/modificar el archivo de prueba. NO escribas ninguna implementación de código fuente en este paso.  
    3\.  \*\*Ejecución y Confirmación de Fallo de Pruebas:\*\* Usa \`run\_terminal\` para ejecutar \`pytest\`. Confirma que las nuevas pruebas fallan como se espera (y que las pruebas existentes pasan). Muestra la salida relevante al usuario.  
    4\.  \*\*Implementación del Código:\*\* Escribe el código mínimo necesario en los archivos fuente apropiados (ej. \`app/routes.py\`, \`app/utils.py\`) para hacer que las nuevas pruebas pasen. Usa \`edit\_file\` para modificar los archivos fuente.  
    5\.  \*\*Restricción Crítica:\*\* NO modifiques los archivos de prueba escritos en el paso 2 durante este paso de implementación.  
    6\.  \*\*Ejecución y Confirmación de Éxito de Pruebas:\*\* Usa \`run\_terminal\` para ejecutar \`pytest\` nuevamente. Itera sobre los pasos 4 y 6 si las pruebas no pasan, explicando los errores y tus correcciones en cada iteración dentro de etiquetas \<thinking\>. Continúa hasta que todas las pruebas (nuevas y existentes) pasen. Muestra la salida exitosa al usuario.  
    7\.  \*\*Refactorización (Opcional):\*\* Una vez que las pruebas pasen, revisa el código implementado. Si identificas oportunidades claras de refactorización para mejorar la legibilidad o eficiencia sin cambiar la funcionalidad, proponlas al usuario dentro de etiquetas \<refactoring\_suggestion\>. Solo aplica la refactorización si el usuario lo aprueba explícitamente.  
    8\.  \*\*Finalización:\*\* Informa al usuario que la implementación está completa y probada.  
  \</instructions\>

  \<context\>  
    \<tech\_stack\>Python, Flask, PyJWT, Pytest\</tech\_stack\>  
    \<coding\_standards\>Adherirse estrictamente a PEP 8\. Usar type hints.\</coding\_standards\>  
    \<project\_structure\>El código de la aplicación reside en \`app/\`, las pruebas en \`tests/\`.\</project\_structure\>  
  \</context\>

  \<output\_format\>  
    Comunícate de forma clara y concisa. Usa etiquetas \<plan\>, \<thinking\>, \<refactoring\_suggestion\> según se indica en las instrucciones. Muestra la salida relevante del terminal cuando ejecutes pruebas.  
  \</output\_format\>

  \<user\_query\>  
    {{USER\_QUERY\_PLACEHOLDER}}  
  \</user\_query\>  
\</system\_prompt\>

* **Anotaciones:**  
  * \<role\>: Define una personalidad experta y orientada a TDD.  
  * \<instructions\>: Delinea el flujo TDD paso a paso de forma explícita, incluyendo la planificación inicial y la restricción crítica de no modificar pruebas.  
  * \<context\>: Proporciona información clave sobre la tecnología y estándares.  
  * \<output\_format\>: Guía el estilo de comunicación y el uso de etiquetas específicas.  
  * {{USER\_QUERY\_PLACEHOLDER}}: Indica dónde se insertará la solicitud específica del usuario.

### **5.2 Ejemplo 2: Prompt de Agente para Depuración (Análisis de Causa Raíz)**

* **Título:** Agente de Depuración Java Spring Boot para NullPointerException  
* **Objetivo:** Diagnosticar la causa raíz de una NullPointerException reportada en una aplicación Java Spring Boot, basándose en el stack trace y el código proporcionado.  
* **Contexto Asumido:** Acceso a read\_file, codebase\_search. El usuario proporciona el stack trace y fragmentos de código relevantes. Potencialmente run\_terminal si se necesita inspeccionar logs específicos.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Ingeniero de Software Java Senior especializado en depurar aplicaciones Spring Boot complejas. Tu fortaleza es el análisis metódico para encontrar la causa raíz de los errores, no solo tratar los síntomas. Eres cauteloso al proponer cambios y priorizas la comprensión completa del problema.  
  \</role\>

  \<instructions\>  
    El usuario ha reportado una \`NullPointerException\` y proporcionará un stack trace y código relevante. Tu tarea es diagnosticar la causa raíz. Sigue estos pasos:  
    1\.  \*\*Análisis Inicial:\*\* Revisa cuidadosamente el \`\<stack\_trace\>\` y el \`\<relevant\_code\>\` proporcionados por el usuario. Identifica la línea exacta donde ocurre la excepción y las variables involucradas.  
    2\.  \*\*Razonamiento (CoT):\*\* Dentro de etiquetas \`\<thinking\>\`, realiza un análisis paso a paso:  
        \*   Formula hipótesis sobre qué variable específica podría ser \`null\` y por qué podría serlo en ese punto del código (ej. no inicializada, retorno inesperado de una llamada, estado incorrecto).  
        \*   Considera el flujo de ejecución que lleva a la línea problemática.  
        \*   Si la información proporcionada es insuficiente, identifica qué información adicional se necesita (ej. valor de una variable específica antes de la excepción, contenido de un log particular, código de una función llamada). Explica \*por qué\* necesitas esa información antes de solicitarla al usuario o intentar obtenerla con herramientas (si están disponibles y permitidas).  
    3\.  \*\*Solicitud de Información / Uso de Herramientas (si es necesario):\*\* Si necesitas más información, pídesela claramente al usuario o usa las herramientas disponibles (\`read\_file\`, \`codebase\_search\`, \`run\_terminal\` para logs específicos) para obtenerla, explicando tu intención.  
    4\.  \*\*Identificación de Causa Raíz:\*\* Basándote en el análisis y la información recopilada, determina la causa raíz más probable de la \`NullPointerException\`. Explica claramente tu conclusión al usuario.  
    5\.  \*\*Sugerencia de Solución:\*\*  
        \*   Si estás \*muy seguro\* de la causa raíz y la solución es un cambio de código directo y seguro (ej. añadir una comprobación de nulidad, inicializar una variable), propón el cambio usando la herramienta \`edit\_file\`, explicando la corrección.  
        \*   Si no estás completamente seguro, o si la solución requiere cambios más complejos o podría tener efectos secundarios, NO propongas un cambio de código directo. En su lugar, explica la causa raíz identificada y sugiere pasos para confirmar el diagnóstico (ej. añadir sentencias de logging específicas antes de la línea problemática, escribir un test unitario que reproduzca el error) o discute posibles enfoques de solución con el usuario. Prioriza la adición de logging o pruebas sobre cambios de código especulativos.\[85\]  
  \</instructions\>

  \<input\_data\>  
    \<stack\_trace\>  
      {{STACK\_TRACE\_PLACEHOLDER}}  
    \</stack\_trace\>  
    \<relevant\_code\>  
      {{RELEVANT\_CODE\_PLACEHOLDER}}  
    \</relevant\_code\>  
  \</input\_data\>

  \<output\_format\>  
    Usa etiquetas \`\<thinking\>\` para tu análisis detallado. Comunica tus hallazgos y recomendaciones de forma clara y profesional. Sé explícito sobre tu nivel de confianza al proponer soluciones de código.  
  \</output\_format\>

  \<user\_query\>  
    Ayúdame a depurar esta NullPointerException.  
  \</user\_query\>  
\</system\_prompt\>

* **Anotaciones:**  
  * \<role\>: Establece experiencia en Java/Spring y enfoque en causa raíz.  
  * \<instructions\>: Define un proceso de diagnóstico metódico, enfatizando el CoT (\<thinking\>) y la precaución al proponer arreglos.85  
  * \<input\_data\>: Estructura la información proporcionada por el usuario.  
  * \<output\_format\>: Refuerza el uso de \<thinking\> y la comunicación clara.  
  * Condicionalidad en la Solución: Instruye al agente a proponer cambios de código solo con alta confianza, priorizando el logging/pruebas en caso contrario.85

### **5.3 Ejemplo 3: Prompt de Agente para Refactorización de Código (Enfoque en Legibilidad)**

* **Título:** Agente de Refactorización JavaScript para Legibilidad  
* **Objetivo:** Refactorizar una función JavaScript compleja para mejorar su legibilidad y mantenibilidad, sin alterar su comportamiento lógico fundamental.  
* **Contexto Asumido:** Acceso a edit\_file, codebase\_search. El usuario proporciona la función a refactorizar. El proyecto sigue la guía de estilo de Airbnb JavaScript. Se asume la existencia de un conjunto de pruebas que cubren la función.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Desarrollador JavaScript experto con una pasión por escribir código limpio, legible y mantenible. Te especializas en refactorización segura y sigues las mejores prácticas y guías de estilo modernas, particularmente la guía de estilo de Airbnb JavaScript.  
  \</role\>

  \<instructions\>  
    La tarea del usuario es refactorizar el código proporcionado en \`\<code\_to\_refactor\>\` para mejorar significativamente su legibilidad y mantenibilidad. Sigue estos pasos:  
    1\.  \*\*Análisis del Código:\*\* Estudia detenidamente el \`\<code\_to\_refactor\>\` para comprender su lógica y funcionamiento actual.  
    2\.  \*\*Plan de Refactorización:\*\* Dentro de etiquetas \`\<refactoring\_plan\>\`, describe los cambios específicos que propones para mejorar la legibilidad. Esto podría incluir:  
        \*   Renombrar variables/funciones para mayor claridad.  
        \*   Descomponer la función en subfunciones más pequeñas y enfocadas.  
        \*   Simplificar expresiones complejas o lógica anidada.  
        \*   Añadir comentarios explicativos donde sea necesario.  
        \*   Mejorar la estructura general o el flujo.  
        Explica brevemente el razonamiento detrás de cada cambio propuesto.  
    3\.  \*\*Confirmación del Plan:\*\* Presenta el \`\<refactoring\_plan\>\` al usuario y espera su aprobación antes de aplicar cualquier cambio.  
    4\.  \*\*Aplicación de Cambios:\*\* Una vez aprobado el plan, aplica los cambios de refactorización al código usando la herramienta \`edit\_file\`.  
    5\.  \*\*Restricciones:\*\*  
        \*   \*\*Lógica Inalterada:\*\* Es CRUCIAL que la refactorización NO cambie el comportamiento lógico fundamental de la función. La salida debe ser idéntica para las mismas entradas.  
        \*   \*\*Guía de Estilo:\*\* Todos los cambios deben adherirse estrictamente a la guía de estilo de Airbnb JavaScript.  
        \*   \*\*Pruebas:\*\* Asume que existen pruebas unitarias para esta función. La versión refactorizada debe pasar todas las pruebas existentes (aunque no ejecutarás las pruebas directamente, diseña los cambios teniéndolo en cuenta).  
    6\.  \*\*Justificación (CoT):\*\* Dentro de etiquetas \`\<thinking\>\` al presentar el código refactorizado, explica brevemente cómo los cambios aplicados mejoran la legibilidad/mantenibilidad, haciendo referencia al plan aprobado.  
  \</instructions\>

  \<input\_data\>  
    \<code\_to\_refactor\>  
      {{CODE\_TO\_REFACTOR\_PLACEHOLDER}}  
    \</code\_to\_refactor\>  
    \<style\_guide\_reference\>Guía de Estilo Airbnb JavaScript\</style\_guide\_reference\>  
  \</input\_data\>

  \<output\_format\>  
    Usa etiquetas \`\<refactoring\_plan\>\` y \`\<thinking\>\` como se especifica. Presenta el código refactorizado final de forma clara.  
  \</output\_format\>

  \<user\_query\>  
    Por favor, refactoriza esta función para que sea más legible y mantenible.  
  \</user\_query\>  
\</system\_prompt\>

* **Anotaciones:**  
  * \<role\>: Define experiencia en JS y enfoque en calidad/legibilidad.  
  * \<instructions\>: Establece un flujo claro: Análisis \-\> Plan \-\> Confirmación \-\> Aplicación. Incluye restricciones críticas sobre la lógica y la guía de estilo. Requiere un plan explícito antes de la edición.  
  * \<input\_data\>: Estructura el código de entrada y la referencia a la guía de estilo.  
  * \<output\_format\>: Guía la presentación de la salida.  
  * Justificación (CoT): Requiere explicación del razonamiento en \<thinking\> para los cambios.

Estos ejemplos ilustran cómo estructurar prompts agénticos para Sonnet 3.5 combinando roles, instrucciones paso a paso, CoT, XML y contexto específico para guiar al modelo hacia la realización exitosa de tareas complejas de desarrollo de software.

## **6\. Optimización del Rendimiento y Mitigación de Problemas con Sonnet 3.5**

Aunque Claude Sonnet 3.5 es un modelo potente para tareas agénticas de codificación, optimizar su rendimiento y anticipar posibles problemas es clave para una colaboración eficaz.

### **6.1 Gestión de la Verbosidad y Prevención de la Sobreingeniería**

* **Problema:** Sonnet 3.5 puede tender a ser verboso en sus explicaciones o proponer soluciones más complejas de lo necesario ("sobreingeniería").4 Esto puede dificultar la extracción de la información clave o llevar a implementaciones innecesariamente complicadas.  
* **Soluciones:**  
  * **Instrucciones de Concisión:** Incluir directivas explícitas en el system prompt como "Sé conciso", "Evita explicaciones innecesarias", "Prioriza la claridad sobre la exhaustividad", o incluso "Usa la menor cantidad de líneas de código posible" puede ayudar a controlar la verbosidad.14  
  * **Formatos de Salida Específicos:** Solicitar la salida en formatos estructurados (ej. JSON, solo bloques de código) puede limitar la prosa adicional.10  
  * **Planificación Previa:** Exigir un plan detallado (\<plan\>) antes de la implementación permite al desarrollador revisar y simplificar el enfoque antes de que el agente genere código complejo.27  
  * **Ejemplos de Simplicidad:** Proporcionar ejemplos (few-shot) que demuestren el nivel deseado de simplicidad o complejidad en la solución.10  
  * **Restricciones Claras:** Definir explícitamente qué *no* debe hacer el agente (ej. "No introduzcas nuevas dependencias", "No refactorices código no relacionado") ayuda a limitar el alcance y prevenir la sobreingeniería.44

### **6.2 Mejora de la Fiabilidad y el Seguimiento de Instrucciones**

* **Problema:** Los agentes pueden malinterpretar instrucciones, omitir pasos, quedarse atascados en bucles, o fallar al usar herramientas correctamente, especialmente en tareas largas o complejas.17  
* **Soluciones:**  
  * **Claridad Extrema:** Usar lenguaje preciso y sin ambigüedades. Descomponer solicitudes complejas en pasos más simples y claros.10  
  * **Estructura XML:** Utilizar etiquetas XML de forma consistente para separar instrucciones, contexto, ejemplos y otros componentes del prompt, mejorando la capacidad de análisis del modelo.10  
  * **Pensamiento Paso a Paso (CoT):** Forzar un procesamiento metódico instruyendo al modelo a pensar paso a paso, idealmente dentro de etiquetas \<thinking\>.10  
  * **Descripciones Detalladas de Herramientas:** Asegurar que las descripciones de las herramientas sean exhaustivas, explicando su propósito, parámetros, comportamiento y limitaciones de forma inequívoca.56  
  * **Herramientas "a Prueba de Errores":** Diseñar las herramientas (si es posible) para minimizar errores comunes, como exigir rutas absolutas.56  
  * **Refinamiento Iterativo:** Probar los prompts y las reglas rigurosamente. Analizar los fallos y refinar las instrucciones, la estructura o las definiciones de herramientas basándose en las observaciones.56 Considerar el uso de meta-prompts o análisis estructurados para mejorar los prompts.87  
  * **Pasos de Verificación Explícitos:** Incluir en el prompt instrucciones para que el agente verifique su propio trabajo o plan en puntos clave.27 Por ejemplo, "Después de escribir el código, verifica que cumple todos los requisitos listados en \<requisitos\>".  
  * **Patrones Supervisores:** Para flujos de trabajo muy complejos o propensos a errores, considerar arquitecturas de múltiples agentes donde un agente "supervisor" monitoriza y guía a un agente "trabajador", proporcionando correcciones o recordatorios simples.45

### **6.3 Estrategias Eficaces de Gestión del Contexto para Tareas Largas/Complejas**

* **Problema:** En interacciones prolongadas o al procesar grandes cantidades de información, el rendimiento puede degradarse, el modelo puede perder contexto relevante, o se puede exceder la ventana de 200K tokens.17  
* **Soluciones:**  
  * **Descomposición de Tareas:** Dividir tareas grandes en subtareas más pequeñas e independientes que puedan manejarse en interacciones separadas o asignarse a agentes/modos especializados.10 Esto se alinea con la tendencia de especialización observada en la comunidad \[Insight 4.3.1\].  
  * **Contexto Enfocado:** Proporcionar únicamente la información estrictamente necesaria para la tarea actual. Utilizar mecanismos como las referencias @ de Cursor, el contexto de editores abiertos, o referencias explícitas a archivos (CLAUDE.md, @nombre\_archivo en reglas).27 Evitar incluir archivos o información irrelevante.  
  * **Limpieza de Contexto:** Utilizar funciones de la herramienta (como /clear en claude-code) o iniciar nuevas sesiones/pestañas para tareas distintas para evitar la acumulación de contexto irrelevante.27  
  * **Gestión Externa del Estado:** Para flujos de trabajo de múltiples pasos, no depender únicamente del historial de conversación para mantener el estado. Hacer que el agente escriba planes, estados intermedios o resultados en archivos externos (ej. workflow\_state.md 83, plan.md 79, issues de GitHub 27) que puedan ser releídos en pasos posteriores.  
  * **Conciencia de Caché (si aplica):** En herramientas que implementan caché de contexto (como claude-code), ser consciente de que ciertas acciones (ediciones manuales fuera del agente, pausas largas) pueden invalidar la caché, potencialmente aumentando el coste o afectando el rendimiento.39

### **6.4 Trabajo con las Fortalezas de Sonnet 3.5 y Navegación por Debilidades Potenciales**

* **Aprovechar Fortalezas:** Diseñar prompts que explícitamente hagan uso de sus puntos fuertes:  
  * **Codificación:** Asignar tareas directas de escritura, depuración, traducción de código.1  
  * **Razonamiento:** Utilizarlo para planificación (invocando "think" 27), análisis de requisitos o diseño de pruebas.  
  * **Uso de Herramientas:** Integrarlo con herramientas bien definidas para extender sus capacidades al sistema de archivos, terminal, APIs externas, etc..19  
  * **Flujos TDD:** Aprovechar su buen rendimiento en flujos de trabajo de Desarrollo Guiado por Pruebas.27  
* **Mitigar Debilidades:** Aplicar las estrategias de las secciones 6.1-6.3 para gestionar la verbosidad, mejorar la fiabilidad y manejar el contexto.  
  * **Corrección Temprana:** Estar preparado para intervenir y corregir el rumbo del agente si empieza a desviarse o a cometer errores ("course correct early and often").27  
  * **Restricciones Negativas:** Usar directivas claras sobre lo que *no* hacer para controlar su proactividad inherente (ver sección 2.2).  
  * **Combinación Estratégica (Avanzado):** Aunque esta guía se centra en Sonnet 3.5, algunos usuarios avanzados en la comunidad experimentan combinando modelos: usando un modelo potencialmente más fuerte en planificación abstracta o análisis (como Opus, o competidores como o3-mini o R1 según algunas discusiones 21) para generar un plan detallado, y luego usando Sonnet 3.5 (con su fuerte capacidad de implementación agéntica) para ejecutar ese plan paso a paso. Esto requiere flujos de trabajo más complejos pero puede ser una estrategia para tareas muy difíciles.

## **7\. Conclusión**

### **7.1 Resumen de Claves para el Prompting de Agentes Sonnet 3.5**

Claude Sonnet 3.5 representa una herramienta formidable para el desarrollo de software agéntico, capaz de realizar tareas complejas de codificación, depuración y refactorización con un grado notable de autonomía. Sin embargo, desbloquear todo su potencial requiere un enfoque cuidadoso y deliberado en el diseño de system prompts. Los principios clave derivados tanto de las recomendaciones de Anthropic como de las prácticas de la comunidad incluyen:

* **Definición Clara de Roles:** Asignar roles específicos y detallados mediante el system prompt es fundamental para enfocar las capacidades del modelo.  
* **Estructura Robusta (XML):** El uso de etiquetas XML para delinear instrucciones, contexto, ejemplos y pasos de razonamiento mejora drásticamente la comprensión y el seguimiento por parte del modelo.  
* **Razonamiento Guiado (CoT):** Fomentar el pensamiento paso a paso, especialmente para tareas complejas, a través de instrucciones explícitas o etiquetas \<thinking\>, mejora la calidad y transparencia de la salida.  
* **Instrucciones Explícitas y Ejemplos:** La claridad, la especificidad, las restricciones (positivas y negativas) y el uso de ejemplos concretos son vitales para guiar el comportamiento del agente.  
* **Gestión Cuidadosa del Contexto:** Proporcionar contexto relevante (usando CLAUDE.md o referencias específicas) y gestionar activamente la ventana de contexto en tareas largas es crucial para mantener el rendimiento.  
* **Herramientas Bien Definidas:** El uso efectivo de herramientas depende críticamente de descripciones exhaustivas y un diseño robusto.  
* **Aprovechar Técnicas Comunitarias:** Estructuras de prompt probadas, el sistema de reglas de Cursor y los modos personalizados ofrecen mecanismos prácticos para implementar estos principios en entornos de desarrollo reales.  
* **Especialización y Descomposición:** Dividir tareas complejas y utilizar agentes/modos especializados para cada subtarea es una estrategia emergente clave para la fiabilidad.

### **7.2 La Importancia de la Iteración y la Experimentación**

Es fundamental reconocer que la ingeniería de prompts, especialmente para agentes complejos como los basados en Sonnet 3.5, es un proceso inherentemente **iterativo**.10 Rara vez se consigue el prompt perfecto en el primer intento. Los desarrolladores deben:

* **Experimentar:** Probar diferentes roles, estructuras de prompt (XML), formulaciones de instrucciones, definiciones de herramientas y estrategias de gestión de contexto.  
* **Observar y Analizar:** Evaluar cuidadosamente el comportamiento del agente en respuesta a diferentes prompts. Identificar patrones de fallo, malentendidos o comportamientos no deseados.  
* **Refinar:** Ajustar y mejorar iterativamente los prompts basándose en las observaciones y en los criterios de éxito definidos para la tarea.48  
* **Compartir y Aprender:** Participar en la comunidad (como los foros de Cursor o subreddits relevantes) para compartir experiencias, aprender de otros y descubrir nuevas técnicas.

Al adoptar un enfoque metódico, aplicar los principios y técnicas descritos en esta guía, y comprometerse con la experimentación y el refinamiento continuo, los equipos de desarrollo pueden aprovechar eficazmente las potentes capacidades agénticas de Claude Sonnet 3.5 para acelerar y mejorar sus flujos de trabajo de software. El potencial para aumentar la productividad y abordar problemas complejos es significativo, pero requiere una guía cuidadosa y experta a través de system prompts bien diseñados.\# Guía Técnica Detallada: Creación de System Prompts Agénticos para Desarrollo de Software con Claude Sonnet 3.5 (Oct 2024\)

## **1\. Introducción**

### **1.1 El Auge de la IA Agéntica en el Desarrollo de Software**

El desarrollo de software está experimentando una transformación significativa impulsada por los avances en la inteligencia artificial (IA). Más allá de la simple asistencia en la codificación o la finalización de código, están surgiendo sistemas de IA agénticos. Estos agentes aspiran a un mayor grado de autonomía, capaces no solo de escribir código, sino también de planificar tareas complejas, interactuar con herramientas, realizar pruebas, depurar errores y refactorizar bases de código existentes.1 Modelos como Claude 3.5 Sonnet demuestran capacidades crecientes en este dominio, permitiendo flujos de trabajo donde la IA actúa más como un colaborador proactivo que como una simple herramienta pasiva.

El corazón de la dirección de estos agentes reside en la ingeniería de "system prompts" (instrucciones de sistema). Estos prompts actúan como la constitución o el conjunto de directrices fundamentales que moldean el comportamiento, la personalidad, el enfoque y las limitaciones del agente de IA al abordar una tarea.10 Un system prompt bien diseñado es crucial para canalizar las potentes capacidades del modelo hacia resultados productivos, fiables y alineados con los objetivos del desarrollador.

### **1.2 Enfoque: Claude Sonnet 3.5 (Oct 2024\) como Socio Agéntico de Codificación**

Esta guía se centra exclusivamente en **Claude Sonnet 3.5**, específicamente en su iteración más reciente referenciada contextualmente como la versión de Octubre de 2024 (refiriéndose a la versión más avanzada disponible y discutida en las fuentes hacia finales de 2024 y principios de 2025). Este modelo, parte de la familia Claude 3.5 de Anthropic, se ha posicionado como una herramienta particularmente potente para el desarrollo de software agéntico. Destaca por su sólida competencia en codificación, sus avanzadas capacidades de razonamiento y su habilidad para seguir instrucciones complejas, a menudo superando a modelos anteriores como Claude 3 Opus e incluso a competidores en diversas evaluaciones relevantes para el desarrollo.1

Si bien existen otros modelos capaces (como Opus para tareas complejas de escritura o Haiku para velocidad, y competidores como Gemini o GPT 1), Sonnet 3.5 ofrece un equilibrio convincente entre inteligencia, velocidad y coste, haciéndolo ideal para tareas agénticas como la implementación de características, la depuración y la refactorización.1 Su rendimiento en evaluaciones de codificación agéntica y su capacidad para utilizar herramientas proporcionadas por el usuario lo convierten en un candidato principal para actuar como un socio de codificación autónomo.1

### **1.3 Propósito y Estructura de esta Guía**

El objetivo de esta guía es proporcionar un recurso técnico exhaustivo y práctico para desarrolladores que buscan crear system prompts agénticos efectivos específicamente para Claude Sonnet 3.5 en el dominio del desarrollo de software. Se basa en una síntesis de las mejores prácticas recomendadas por Anthropic, la documentación oficial y las experiencias prácticas, consejos y ejemplos compartidos por la comunidad de desarrolladores, con un enfoque particular en el ecosistema de herramientas como Cursor, donde estos agentes se implementan frecuentemente.

La guía se estructura de la siguiente manera:

1. **Comprensión de Claude Sonnet 3.5 para Codificación Agéntica:** Detalla las capacidades relevantes, fortalezas y matices del modelo.  
2. **Principios Fundamentales de Prompting Agéntico (Recomendaciones de Anthropic):** Explora las técnicas clave respaldadas por la documentación oficial.  
3. **Técnicas Impulsadas por la Comunidad (Ecosistema Cursor):** Analiza estructuras y enfoques prácticos desarrollados por usuarios.  
4. **Ejemplos Concretos de System Prompts:** Proporciona plantillas anotadas para tareas de implementación, depuración y refactorización.  
5. **Optimización y Mitigación de Problemas:** Ofrece estrategias para maximizar el rendimiento y abordar posibles dificultades.

## **2\. Comprensión de Claude Sonnet 3.5 para Codificación Agéntica**

Para diseñar prompts efectivos, es fundamental comprender las capacidades específicas y las particularidades de Claude Sonnet 3.5 en el contexto de tareas agénticas de software.

### **2.1 Visión General de Capacidades Relevantes**

* **Competencia en Codificación:** Claude Sonnet 3.5 ha demostrado un rendimiento sobresaliente en benchmarks de codificación estándar como HumanEval y evaluaciones más complejas orientadas a la ingeniería de software del mundo real como SWE-bench.1 Es capaz de escribir, editar, ejecutar, traducir (útil para modernizar código legacy) y solucionar problemas de código de forma independiente cuando se le proporcionan las herramientas e instrucciones adecuadas.1 Su capacidad para abordar tareas agénticas, como corregir errores o añadir funcionalidades basadas en descripciones en lenguaje natural, es una de sus fortalezas clave.1  
* **Razonamiento y Seguimiento de Instrucciones:** El modelo establece nuevos benchmarks en razonamiento a nivel de posgrado (GPQA) y conocimiento a nivel universitario (MMLU).1 Muestra una mejora notable en la comprensión de matices, humor e instrucciones complejas, y es excepcional en la ejecución de flujos de trabajo de múltiples pasos.1 Existe un modo de "pensamiento extendido" que puede activarse mediante frases específicas como "piensa", "piensa detenidamente" ("think hard"), lo que asigna más presupuesto computacional para tareas de planificación o depuración complejas.27  
* **Uso de Herramientas:** Una capacidad crucial para los agentes es interactuar con el mundo exterior. Claude puede utilizar herramientas externas (APIs, funciones locales, comandos de terminal) pero estas deben ser definidas explícitamente por el usuario en la solicitud API; el modelo no posee herramientas incorporadas.19 Sonnet 3.5 demuestra una buena capacidad para el uso complejo de herramientas y para buscar clarificaciones cuando las instrucciones o los parámetros de las herramientas son ambiguos.19 Ha mostrado mejoras en benchmarks específicos de uso de herramientas agénticas como TAU-bench.7  
* **Ventana de Contexto:** Sonnet 3.5 opera con una ventana de contexto de 200,000 tokens.1 Esta amplia ventana es ventajosa para tareas agénticas que requieren comprender grandes bases de código o mantener el contexto a lo largo de interacciones prolongadas, aunque la gestión eficaz sigue siendo importante.10  
* **Capacidades de Visión:** Aunque no es el enfoque principal de esta guía, cabe destacar que Sonnet 3.5 es el modelo de visión más potente de Anthropic hasta la fecha, superando a Opus en benchmarks de visión.1 Puede interpretar gráficos, diagramas e incluso transcribir texto de imágenes imperfectas.1 Esto puede ser relevante para tareas de desarrollo de UI, depuración de elementos visuales o comprensión de documentación gráfica.

### **2.2 Fortalezas y Matices para Tareas Agénticas de Software**

* **Fortalezas:** Resumiendo lo anterior, Sonnet 3.5 brilla en la codificación, depuración y refactorización agéntica gracias a su sólida competencia técnica, seguimiento de instrucciones complejas, razonamiento avanzado, amplia ventana de contexto y uso eficaz de herramientas (cuando están bien definidas).1 La comunidad de desarrolladores, especialmente en entornos como Cursor, a menudo lo prefiere para tareas agénticas en comparación con otros modelos disponibles en momentos similares.21  
* **Matices / Debilidades Potenciales:** A pesar de sus fortalezas, los usuarios y las evaluaciones han observado ciertos matices. El modelo puede ser verboso, tender a la sobreingeniería o realizar cambios no solicitados si las instrucciones no son lo suficientemente restrictivas.4 Puede haber pérdida ocasional de contexto o generación de "alucinaciones" en interacciones muy largas o complejas.17 Su rendimiento es sensible a la estructura y claridad del prompt.42 Pueden surgir problemas de fiabilidad, como quedarse atascado en bucles de depuración o fallar en el uso de herramientas si no están perfectamente definidas.17 El rendimiento también puede degradarse si la ventana de contexto se llena excesivamente.41

Una observación clave derivada de estos puntos es la naturaleza de doble filo de la capacidad agéntica de Sonnet 3.5. Su fortaleza radica en su capacidad para tomar la iniciativa y realizar tareas de forma autónoma: escribir, editar y ejecutar código.1 Sin embargo, esta misma proactividad puede convertirse en una debilidad si no se guía adecuadamente. Los informes de la comunidad sobre el modelo actuando como un "idiota proactivo" 30, realizando cambios no deseados 4 o complicando excesivamente las soluciones 40 sugieren que su impulso inherente para completar tareas puede llevarlo a hacer suposiciones o tomar iniciativas más allá de la intención explícita del usuario, especialmente si el prompt carece de restricciones claras. El proceso interno del modelo podría priorizar la finalización de la tarea sobre la adherencia estricta a los cambios mínimos necesarios. Esto implica que los system prompts agénticos para Sonnet 3.5 deben definir no solo el *objetivo* de la tarea, sino también establecer cuidadosamente los *límites* y *restricciones* de las acciones del agente. Técnicas como las restricciones negativas explícitas ("NO modifiques código no relacionado"), exigir planes paso a paso antes de la ejecución 27, y potencialmente el uso de agentes supervisores 45 se vuelven fundamentales para gestionar esta proactividad. Existe una tensión inherente entre empoderar al agente y mantener el control, un aspecto central para el diseño efectivo de prompts agénticos para Sonnet 3.5.

## **3\. Principios Fundamentales de Prompting Agéntico para Sonnet 3.5 (Recomendaciones de Anthropic)**

Anthropic proporciona directrices y técnicas clave para interactuar eficazmente con sus modelos Claude. Aplicar estos principios es fundamental para construir system prompts robustos para agentes Sonnet 3.5.

### **3.1 Definición de Roles: El Poder de los System Prompts**

La forma más potente de utilizar los system prompts con los modelos Claude es mediante la **definición de roles** (role prompting).11 Esto implica asignar explícitamente una personalidad, experiencia o función específica al modelo antes de presentarle la tarea concreta.

* **Uso del Parámetro system:** La práctica recomendada es definir el rol dentro del parámetro system de la API de Mensajes. Las instrucciones específicas de la tarea deben ir en el turno del user.11 Esta separación ayuda al modelo a distinguir entre su identidad/contexto general y la solicitud inmediata.  
* **Especificidad del Rol:** Es crucial definir roles específicos y relevantes para la tarea de desarrollo de software. En lugar de un genérico "Actúa como un programador", se deben usar roles más detallados que enfoquen el conocimiento y el estilo de respuesta del modelo. Ejemplos efectivos incluyen:  
  * "Eres un ingeniero de software senior con 10 años de experiencia en Python y desarrollo web, especializado en la creación de APIs RESTful seguras y escalables." 11  
  * "Eres un experto en depuración de aplicaciones React, meticuloso en la identificación de causas raíz y en la propuesta de soluciones limpias y eficientes." 11  
  * "Eres un revisor de código enfocado en la seguridad, con experiencia en identificar vulnerabilidades comunes (XSS, SQL Injection, etc.) en aplicaciones Java." 11  
  * "Eres un arquitecto técnico especializado en microservicios, responsable de diseñar sistemas resilientes y mantenibles." 11 La especificidad ayuda a Claude a activar las partes más relevantes de su entrenamiento y a adoptar el tono y nivel de detalle apropiados.

### **3.2 Estructuración de Prompts: Aprovechando las Etiquetas XML para Mayor Claridad**

Los modelos Claude, incluido Sonnet 3.5, han sido entrenados para prestar especial atención a las etiquetas XML.10 El uso de estas etiquetas para estructurar el prompt ofrece beneficios significativos:

* **Claridad:** Delimitan claramente las diferentes secciones del prompt (instrucciones, contexto, ejemplos, etc.).  
* **Precisión:** Reducen la ambigüedad y ayudan al modelo a interpretar correctamente cada parte.  
* **Flexibilidad:** Facilitan la modificación y gestión de prompts complejos.  
* **Parseabilidad:** Permiten extraer fácilmente información específica de la respuesta del modelo si se le instruye a usar etiquetas en su salida. 46

Aunque no hay etiquetas "canónicas" estrictas, se recomienda usar nombres lógicos y descriptivos. Las prácticas clave incluyen la **consistencia** en el uso de nombres de etiquetas y el **anidamiento** para contenido jerárquico.46

**Ejemplos de Etiquetas Comunes para Prompts Agénticos:**

* \<instructions\>: Para las directivas principales de la tarea.  
* \<context\>: Para proporcionar información de fondo, como fragmentos de código relevantes, descripciones de arquitectura o guías de estilo.  
* \<code\_to\_analyze\> o \<code\_to\_refactor\>: Para delimitar el código específico que el agente debe procesar.  
* \<user\_query\>: Para encerrar la solicitud específica del usuario dentro de un prompt más amplio.  
* \<example\>: Para proporcionar ejemplos de entrada/salida deseados (few-shot prompting).  
* \<output\_format\>: Para especificar el formato de salida requerido (ej. JSON, Markdown).  
* \<thinking\>: Para instruir al modelo a realizar su razonamiento paso a paso (ver 3.3).  
* \<plan\>: Para solicitar un plan de acción antes de la ejecución.  
* \<security\_review\>: Para solicitar un análisis de seguridad específico.43  
* \<tool\_definition\> / \<available\_tools\>: Para definir las herramientas que el agente puede usar (ver 3.6).  
* \<constraints\> / \<negative\_constraints\>: Para especificar límites o acciones prohibidas.

10

### **3.3 Guiando el Razonamiento: Cadena de Pensamiento (CoT) y Pensamiento Paso a Paso**

Para tareas complejas que requieren planificación, análisis o depuración, guiar el proceso de razonamiento de Sonnet 3.5 es crucial. La técnica de **Cadena de Pensamiento (Chain of Thought \- CoT)** anima al modelo a descomponer el problema en pasos intermedios antes de llegar a la respuesta final, lo que mejora la precisión y la coherencia.10

* **Métodos de Implementación de CoT:**  
  * **Instrucción Simple:** Incluir la frase "Piensa paso a paso" ("Think step-by-step") en el prompt.10  
  * **Pasos Guiados:** Delinear explícitamente los pasos que el modelo debe seguir en su razonamiento.51  
  * **Prompting Estructurado (XML):** Utilizar etiquetas como \<thinking\> para el proceso de razonamiento y \<answer\> (u otras etiquetas específicas como \<plan\>, \<fix\>) para la salida final.10 Este es a menudo el método más efectivo.  
* **Uso Efectivo de \<thinking\>:**  
  * Instruir explícitamente al modelo para que realice su razonamiento dentro de estas etiquetas.  
  * Animar a descomponer la tarea en subproblemas lógicos dentro de \<thinking\>.  
  * Para tareas numéricas o lógicas, solicitar que se muestren los cálculos o pasos intermedios.  
  * Para análisis, pedir que se articule la lógica y las consideraciones.  
  * Asegurar una clara separación entre el contenido de \<thinking\> y la salida final en \<answer\> u otras etiquetas designadas. 10  
* **Pensamiento Extendido:** Para tareas que requieren una planificación o análisis más profundos, se puede invocar un modo de "pensamiento extendido" utilizando frases específicas que asignan progresivamente más presupuesto computacional: "piensa" \< "piensa detenidamente" ("think hard") \< "piensa aún más detenidamente" ("think harder") \< "ultrapensamiento" ("ultrathink").27 Esto puede ser particularmente útil al pedirle al agente que genere un plan complejo o analice casos límite.

### **3.4 Claridad en las Instrucciones: Proporcionando Ejemplos y Directivas Efectivas**

La calidad de la salida de Sonnet 3.5 depende en gran medida de la claridad y precisión de las instrucciones proporcionadas.

* **Instrucciones Claras y Directas:** Evitar la ambigüedad. Ser explícito sobre los requisitos, el alcance y las expectativas.10  
* **Ejemplos (Few-Shot Prompting):** Proporcionar ejemplos concretos del comportamiento, formato o estilo de salida deseado es una forma poderosa de guiar al modelo.10 Los ejemplos deben ser relevantes, claros y diversos. Comenzar con 3-5 ejemplos suele ser un buen punto de partida.10  
* **Especificación de Formato:** Indicar explícitamente el formato de salida deseado (ej. JSON, Markdown, lista de pasos).10  
* **Prellenado de Respuesta:** Para guiar la estructura inicial de la respuesta y evitar introducciones innecesarias, se puede proporcionar el comienzo de la respuesta esperada en el turno del assistant.10  
* **Restricciones (Positivas y Negativas):** Definir claramente lo que el agente *debe* hacer y, crucialmente, lo que *no debe* hacer. Ejemplos: "Implementa la función usando TDD", "NO modifiques los archivos de prueba existentes", "NUNCA expongas claves de API en el código", "Utiliza únicamente las funciones definidas en \<allowed\_functions\>".10

### **3.5 El Contexto es Clave: Técnicas para una Gestión Eficaz del Contexto**

Proporcionar el contexto adecuado es vital para que un agente de software funcione eficazmente. Sonnet 3.5 necesita comprender la estructura del código base, las dependencias relevantes, las guías de estilo y otros detalles del proyecto.

* **Provisión de Contexto Relevante:** Incluir información esencial como la estructura del proyecto, archivos clave, dependencias, guías de estilo, etc., en el prompt o a través de mecanismos de carga de contexto.12  
* **CLAUDE.md (Mejor Práctica):** Inspirado en la herramienta claude-code de Anthropic, crear un archivo CLAUDE.md en la raíz del proyecto (o en subdirectorios) es una excelente práctica para proporcionar contexto persistente. Este archivo puede contener comandos bash comunes, descripción de archivos/utilidades centrales, guías de estilo, instrucciones de prueba, configuración del entorno, etc..27 Se recomienda iterar y refinar el contenido de CLAUDE.md como si fuera un prompt en sí mismo.27  
* **Gestión de Conversaciones Largas:** En interacciones prolongadas o flujos de trabajo complejos, la ventana de contexto de 200K tokens 1 puede llenarse. Estrategias para mitigar esto incluyen:  
  * Usar comandos como /clear (si la herramienta lo soporta) para reiniciar el contexto.27  
  * Descomponer tareas grandes en subtareas más pequeñas y manejarlas en interacciones separadas.  
  * Utilizar archivos externos (como Markdown o issues de GitHub) como "checklists" o "scratchpads" para que el agente rastree el progreso en lugar de depender únicamente del historial de conversación.27  
  * Ser consciente de las acciones que pueden invalidar la caché de contexto en algunas herramientas (ediciones manuales, pausas largas).39

### **3.6 Dominio del Uso de Herramientas: Definición, Invocación y Mejores Prácticas**

La capacidad de un agente para interactuar con el mundo exterior depende de su habilidad para usar herramientas (funciones, APIs, comandos).

* **Definición Explícita:** Reiterar que todas las herramientas deben definirse explícitamente en la solicitud API, incluyendo name (identificador único), description (descripción detallada) e input\_schema (esquema JSON para parámetros).19  
* **Descripciones Detalladas (CRÍTICO):** Este es el factor más importante para el rendimiento de las herramientas.19 La descripción debe explicar exhaustivamente:  
  * Qué hace la herramienta.  
  * Cuándo debe (y no debe) usarse.  
  * El significado de cada parámetro y su efecto.  
  * Advertencias o limitaciones importantes (qué información *no* devuelve).  
  * Se recomiendan al menos 3-4 frases por descripción, más si es compleja.19 La claridad aquí es primordial; pensar en ello como escribir una excelente docstring para un desarrollador junior.56  
* **Parámetro tool\_choice:** Comprender las opciones (auto, any, tool, none) y sus implicaciones.19  
  * auto (predeterminado con herramientas): Permite a Claude decidir si usar o no una herramienta.  
  * any: Obliga a Claude a usar *alguna* de las herramientas proporcionadas.  
  * tool: Obliga a Claude a usar una herramienta *específica*.  
  * none (predeterminado sin herramientas): Impide el uso de herramientas.  
  * Nota: Forzar el uso (any o tool) puede suprimir la salida de la cadena de pensamiento (\<thinking\>) antes del bloque tool\_use. Para mantener CoT mientras se sugiere una herramienta específica, usar auto y guiar en el prompt del usuario.19  
* **Diseño de Herramientas "a Prueba de Errores" (Poka-yoke):** Modificar los argumentos o el comportamiento de la herramienta para hacer más difícil que el modelo cometa errores.56 Ejemplos: exigir rutas absolutas en lugar de relativas para herramientas de edición de archivos 17, o usar métodos de reemplazo de cadenas específicos y seguros para ediciones.17  
* **Pruebas Exhaustivas:** Es fundamental probar cómo el modelo utiliza las herramientas con diversas entradas para identificar y corregir errores o ambigüedades en la definición o descripción.56

## **4\. Técnicas Impulsadas por la Comunidad para Desarrollo de Software con Sonnet 3.5 (Perspectivas del Ecosistema Cursor)**

Mientras que Anthropic proporciona los principios fundamentales, la comunidad de desarrolladores, especialmente dentro de ecosistemas como Cursor (un editor de código enfocado en IA), ha desarrollado y compartido estructuras de prompts, reglas y flujos de trabajo prácticos para aplicar estos principios a tareas de desarrollo de software con modelos como Sonnet 3.5.

### **4.1 Estructuras de Prompt Fiables (ej. patrones core.md, request.md)**

La comunidad ha experimentado con plantillas de prompts estructuradas para guiar consistentemente el comportamiento del agente. Un ejemplo notable es el conjunto de plantillas core.md, refresh.md y request.md 57:

* **core.md (Reglas Fundamentales):** Actúa como el system prompt base persistente. Define la personalidad central del agente (ej. "colega senior meticuloso"), su enfoque (comprensión profunda, planificación estratégica, ejecución diligente, verificación rigurosa), directrices de seguridad (integridad del sistema, aprobación para acciones de riesgo), estilo de comunicación (conciso, enfocado en resultados) y principios de aprendizaje continuo.57 Estas reglas fundamentales buscan establecer un comportamiento consistente, cauteloso y efectivo.  
* **request.md (Implementación de Características/Modificaciones):** Es una plantilla específica para tareas de implementación. Comienza con la solicitud del usuario y luego enfatiza aspectos clave de core.md relevantes para la implementación: análisis profundo, evaluación de impacto/dependencias, estrategia óptima, validación exhaustiva, ejecución segura e informes concisos.57 Guía al agente a través de los pasos de planificación, validación, implementación y verificación para nuevas características o refactorizaciones.  
* **refresh.md (Diagnóstico de Problemas Persistentes):** Se utiliza cuando intentos previos de depuración han fallado. Guía al agente a través de un proceso riguroso de re-diagnóstico: dar un paso atrás, redefinir el alcance, mapear la estructura del sistema, hipotetizar causas raíz (ampliamente), investigar sistemáticamente con herramientas, identificar la causa raíz confirmada (basada en evidencia, no suposiciones), proponer una solución específica, planificar una verificación completa, ejecutar y verificar, e informar el resultado.57

Estas estructuras implementan principios de Anthropic como la definición de roles (persona central), el pensamiento paso a paso (planificación, diagnóstico sistemático), la importancia de la verificación y la necesidad de instrucciones claras. Otros ejemplos compartidos por la comunidad 58 a menudo siguen patrones similares, definiendo roles, estándares de codificación, procesos de pensamiento y formatos de salida deseados.

### **4.2 Aprovechamiento de las Reglas de Cursor para Contexto y Barreras de Seguridad**

Cursor ofrece un sistema de reglas sofisticado que permite a los desarrolladores guiar el comportamiento de la IA y proporcionar contexto específico del proyecto, complementando o implementando el system prompt principal.

* **Tipos de Reglas:**  
  * **Reglas Globales (User Rules):** Definidas en la configuración de Cursor, se aplican a todos los proyectos. Son texto plano y actúan como un system prompt global base.62  
  * **Reglas de Proyecto (.cursorrules / .cursor/rules/\*.mdc):** Específicas de un repositorio. El formato .cursorrules (un solo archivo en la raíz) parece estar siendo reemplazado por el sistema más granular de archivos .mdc dentro del directorio .cursor/rules/.64 Estas reglas de proyecto suelen tener prioridad sobre las reglas globales.57  
* **Estructura de Reglas de Proyecto (.mdc):** Estos archivos utilizan un formato llamado MDC (Markdown Content) que combina metadatos YAML en un bloque frontal (---) con el contenido de la regla en Markdown.64  
  * **Metadatos:** Definen cómo y cuándo se aplica la regla. Campos clave incluyen description (para que el agente entienda el propósito de la regla), globs (patrones de archivo tipo gitignore para activar la regla) y alwaysApply (booleano, relevante para Auto Attached).69  
  * **Cuerpo Markdown:** Contiene las instrucciones, directrices o contexto. Puede incluir referencias a otros archivos del proyecto usando la sintaxis @nombre\_archivo.ext, lo que permite incluir contexto adicional dinámicamente.64  
* **Tipos de Activación de Reglas de Proyecto:** Los metadatos determinan cómo se activa una regla .mdc:

| Tipo de Regla | Metadatos Clave Requeridos | Mecanismo de Activación | Caso de Uso Ejemplo | Snippets Relevantes |
| :---- | :---- | :---- | :---- | :---- |
| Always | Ninguno (implícito) | Siempre incluido en el contexto del modelo para todas las solicitudes en el proyecto. | Definir estándares de codificación globales del proyecto, personalidad base del agente. | 69 |
| Auto Attached | globs | Incluido automáticamente cuando se hace referencia a archivos que coinciden con globs. | Aplicar guías de estilo específicas (ej. Tailwind) a componentes React (components/\*\*/\*). | 64 |
| Agent Requested | description | Disponible para el agente; decide si incluirlo basándose en la descripción y el contexto. | Proporcionar una plantilla opcional para crear nuevos servicios Express. | 69 |
| Manual | Ninguno | Solo incluido si el usuario lo menciona explícitamente en el chat (ej. @mi\_regla). | Aplicar un conjunto específico de directrices de refactorización bajo demanda. | 69 |

Comprender estos tipos permite a los desarrolladores elegir la estrategia adecuada para proporcionar contexto o directrices: aplicar siempre, automáticamente según el archivo, permitir que el agente decida, o solo bajo demanda explícita. Esto ofrece un control granular sobre el contexto y el comportamiento del agente Sonnet 3.5 dentro de Cursor.

* **Uso Práctico:** Las reglas se utilizan para una variedad de propósitos:  
  * **Estándares de Codificación:** "Usar tipos estrictos en TypeScript", "Seguir las directrices de RuboCop".62  
  * **Contexto Específico:** "Este proyecto usa SolidJS, no React, para archivos.tsx" 65, "Usar objetos de servicio para lógica de negocio (ver @docs/architecture/services.md)".64  
  * **Definición de Comportamiento:** "Siempre explica la solución primero", "Pide aclaraciones si la tarea no está clara".65  
  * **Restricciones:** "Prohibir consultas SQL en las vistas" 64, "Requerir aprobación explícita para operaciones destructivas".71

### **4.3 Aprovechamiento del Modo Agente y Modos Personalizados de Cursor para Tareas Especializadas**

Cursor ha evolucionado para ofrecer modos de interacción específicos, permitiendo a los usuarios invocar diferentes niveles de autonomía y conjuntos de herramientas.

* **Modo Agente:** Es el modo predeterminado y más autónomo. Está diseñado para manejar tareas complejas con mínima supervisión.77  
  * **Capacidades:** Tiene acceso completo a herramientas (búsqueda en el código base, lectura/escritura de archivos, ejecución de terminal, búsqueda web), realiza razonamiento multi-paso, y puede explorar y modificar el código base de forma independiente.77 Puede realizar hasta 25 llamadas a herramientas antes de necesitar una continuación.78  
  * **Flujo de Trabajo:** Sigue un proceso sistemático: 1\) Comprender la solicitud y el contexto, 2\) Explorar el código base/web, 3\) Planificar los cambios, 4\) Ejecutar los cambios (código, archivos, comandos), 5\) Verificar los resultados (aplicando cambios, intentando arreglar errores de linter).77  
  * **Configuración:** Permite habilitar el modo "Yolo" para ejecución automática de comandos (útil para tests), definir barreras de seguridad para comandos de terminal, y se guía por las Reglas de Cursor.77  
* **Modos Personalizados (Beta):** Permiten a los usuarios crear sus propios modos con combinaciones específicas de herramientas habilitadas y prompts/instrucciones personalizadas, adaptados a flujos de trabajo particulares.79  
  * **Configuración:** Se definen a través de la interfaz de usuario (nombre, icono, atajo, herramientas, instrucciones).79 Se está considerando un archivo modes.json o similar (.cursor/agents/\*.mdc) para definirlos y compartirlos dentro del repositorio.74  
  * **Ejemplos Relevantes:** La documentación y la comunidad sugieren modos como:  
    * Learn: Enfocado en explicaciones detalladas, sin edición automática.79  
    * Refactor: Solo mejora código existente, sin añadir funcionalidad.79  
    * Plan: Genera planes detallados (ej. en plan.md) sin modificar código.79  
    * Research: Recopila información de múltiples fuentes antes de sugerir.79  
    * Debug: Investiga a fondo (archivos, terminal) antes de proponer arreglos.79  
    * TDD Assistant: Podría guiar a través de los pasos de TDD.  
    * Security Auditor: Enfocado en identificar vulnerabilidades.

La aparición y el énfasis en los Modos Personalizados 74 y los flujos de trabajo estructurados (como el flujo Agile 82 o patrones Supervisor/Trabajador 45) en la comunidad de Cursor sugieren una tendencia clara: descomponer el complejo ciclo de vida del desarrollo de software en tareas manejadas por agentes especializados (definidos a través de modos o prompts específicos) es una estrategia clave para lograr resultados fiables y efectivos con modelos potentes pero a veces impredecibles como Sonnet 3.5. Confiar en un único prompt de agente de propósito general para todo el proceso parece ser menos robusto que emplear múltiples prompts/agentes especializados adaptados a fases específicas (planificación, codificación, pruebas, depuración, refactorización) o dominios (frontend, backend, seguridad). Esto se alinea con las recomendaciones de Anthropic sobre el uso de subagentes 27 y la descomposición de tareas complejas 10, pero representa un patrón de implementación más concreto dentro de la herramienta Cursor. Por lo tanto, el prompting agéntico eficaz para Sonnet 3.5 en Cursor implica diseñar no solo prompts individuales, sino *flujos de trabajo* que aprovechen estos agentes especializados. Esto requiere una cuidadosa consideración de la descomposición de tareas, la definición de roles para cada agente/modo y, potencialmente, cómo se gestiona el estado/contexto entre pasos (por ejemplo, utilizando archivos compartidos como workflow\_state.md 83 o plan.md 79).

La siguiente tabla ofrece ejemplos de configuración para modos personalizados orientados a tareas comunes de desarrollo, sirviendo como plantillas prácticas:

| Nombre del Modo | Propósito | Instrucciones Clave (Resumen) | Herramientas Habilitadas (Ejemplos) | Auto-Aplicar/Ejecutar |
| :---- | :---- | :---- | :---- | :---- |
| Planner | Generar planes de implementación detallados sin modificar código. | "Analiza la solicitud. Investiga el código base. Crea un plan paso a paso detallado en plan.md. No edites código." | Búsqueda (Codebase, Web), Leer Archivo, Terminal (solo lectura) | No |
| Implementer (TDD) | Implementar código siguiendo un plan y principios TDD. | "Sigue el plan de plan.md. Escribe pruebas primero (si no existen). Implementa código para pasar pruebas. No modifiques pruebas." | Edición (Edit & Reapply), Terminal (para tests), Búsqueda (Codebase) | Opcional (Tests) |
| Debugger | Investigar y solucionar errores, priorizando la causa raíz. | "Analiza el error/síntoma. Investiga logs/código relacionado. Hipotetiza causas. Verifica con herramientas. Propón arreglo específico." | Búsqueda (Todas), Terminal, Edición (Edit & Reapply) | No (revisar arreglo) |
| Refactorer | Mejorar la estructura/calidad del código sin cambiar la lógica funcional. | "Enfócate únicamente en mejorar \[readability/performance/etc.\]. No añadas funcionalidad. Verifica con pruebas existentes." | Edición (Edit & Reapply), Búsqueda (Codebase), Terminal (para tests) | No (revisar cambios) |
| Security Auditor | Identificar posibles vulnerabilidades de seguridad en el código. | "Revisa el código en busca de vulnerabilidades comunes (OWASP Top 10, etc.). Explica los riesgos y sugiere mitigaciones seguras." | Búsqueda (Codebase), Leer Archivo | No |

Estas configuraciones son puntos de partida. Los desarrolladores deben ajustarlas según las especificidades de su proyecto, las herramientas disponibles (incluyendo servidores MCP personalizados 75) y el comportamiento observado de Sonnet 3.5.

### **4.4 Consejos Comunitarios para Flujos de Trabajo Específicos**

La comunidad ha compartido enfoques para tareas recurrentes:

* **Desarrollo Guiado por Pruebas (TDD):** Combinar el flujo de trabajo TDD recomendado por Anthropic (Escribir pruebas \-\> Confirmar fallo \-\> Commit \-\> Codificar \-\> Iterar hasta pasar \-\> Commit) 27 con prácticas comunitarias. Esto puede implicar el uso de prompts o modos personalizados distintos para la generación de pruebas y la implementación del código.82 Es crucial instruir al agente para que *no modifique* las pruebas durante la fase de implementación del código.27 La capacidad de Sonnet 3.5 para escribir pruebas y luego el código para pasarlas se ha demostrado.84  
* **Bucles de Depuración:** Utilizar estructuras como la plantilla refresh.md para un re-diagnóstico sistemático cuando los arreglos iniciales fallan.57 Pedir al agente que inserte declaraciones de registro descriptivas para rastrear el estado.85 Emplear Modos Personalizados de Debugger.79 Un enfoque estructurado puede ser pedirle al agente que genere una lista de verificación de errores (basada en la salida del linter o stack traces) y los aborde secuencialmente, verificando cada arreglo.27 Proporcionar mensajes de error claros y contexto de código relevante es fundamental. Recordar que el agente puede intentar arreglar errores de linter automáticamente, pero con un límite de intentos antes de pedir ayuda.12  
* **Patrones de Refactorización:** Usar Modos Refactor dedicados 79 o prompts que especifiquen claramente el objetivo (ej. "Refactoriza esta función para reducir la complejidad ciclomática", "Mejora la legibilidad de este módulo aplicando el principio SOLID", "Optimiza esta consulta para mejorar el rendimiento").76 Es vital proporcionar el objetivo de la refactorización y, si es posible, ejemplos del estilo deseado. La verificación (ej. ejecutar el conjunto de pruebas) después de la refactorización es indispensable.  
* **Planificación y Arquitectura:** Incorporar fases de planificación explícitas en el flujo de trabajo.82 Utilizar Modos Plan 79 que generen documentos de diseño (ej. en plan.md) antes de comenzar la implementación. Invocar el "pensamiento extendido" ("think hard", "ultrathink") para tareas de diseño arquitectónico complejas.27

## **5\. Creación de System Prompts Agénticos Efectivos: Ejemplos para Sonnet 3.5**

A continuación, se presentan ejemplos concretos de system prompts diseñados para Claude Sonnet 3.5 en tareas agénticas de desarrollo de software. Estos ejemplos integran los principios de Anthropic y las técnicas comunitarias discutidas anteriormente, utilizando etiquetas XML para la estructura.

*(Nota: Estos prompts asumen un entorno como Cursor donde el agente tiene acceso a herramientas para interactuar con el código base y potencialmente ejecutar comandos. Los nombres y capacidades exactas de las herramientas (codebase\_search, edit\_file, run\_terminal) deben adaptarse al entorno específico.)*

### **5.1 Ejemplo 1: Prompt de Agente para Implementación de Funcionalidad (Enfoque TDD)**

* **Título:** Agente de Implementación Python TDD para Autenticación JWT  
* **Objetivo:** Implementar un nuevo endpoint de autenticación de usuarios (/login) y generación de tokens JWT en una aplicación backend Python Flask, siguiendo estrictamente el flujo de trabajo TDD.  
* **Contexto Asumido:** Acceso a herramientas edit\_file (para leer/escribir archivos), run\_terminal (para ejecutar pytest), codebase\_search. El proyecto utiliza Flask, PyJWT y Pytest. Existe una guía de estilo PEP 8\.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Ingeniero de Software Python Senior experto en desarrollo backend con Flask y un firme practicante del Desarrollo Guiado por Pruebas (TDD). Tu objetivo es implementar nuevas funcionalidades de manera robusta y bien probada. Eres meticuloso, sigues las instrucciones al pie de la letra y priorizas la calidad y la mantenibilidad del código.  
  \</role\>

  \<instructions\>  
    La tarea del usuario será implementar una nueva funcionalidad. Debes seguir estrictamente el siguiente flujo de trabajo TDD:  
    1\.  \*\*Análisis y Planificación:\*\* Basado en la \<user\_query\>, analiza los requisitos. Identifica los archivos relevantes (modelos, rutas, utilidades) usando \`codebase\_search\` si es necesario. Formula un plan detallado para la implementación dentro de etiquetas \<plan\>. El plan debe incluir qué pruebas se escribirán. Pide confirmación del plan al usuario antes de proceder.  
    2\.  \*\*Escritura de Pruebas:\*\* Una vez confirmado el plan, escribe las pruebas unitarias y/o de integración necesarias usando Pytest para la nueva funcionalidad. Coloca las pruebas en el archivo/directorio apropiado (ej. \`tests/test\_auth.py\`). Usa \`edit\_file\` para crear/modificar el archivo de prueba. NO escribas ninguna implementación de código fuente en este paso.  
    3\.  \*\*Ejecución y Confirmación de Fallo de Pruebas:\*\* Usa \`run\_terminal\` para ejecutar \`pytest\`. Confirma que las nuevas pruebas fallan como se espera (y que las pruebas existentes pasan). Muestra la salida relevante al usuario.  
    4\.  \*\*Implementación del Código:\*\* Escribe el código mínimo necesario en los archivos fuente apropiados (ej. \`app/routes.py\`, \`app/utils.py\`) para hacer que las nuevas pruebas pasen. Usa \`edit\_file\` para modificar los archivos fuente.  
    5\.  \*\*Restricción Crítica:\*\* NO modifiques los archivos de prueba escritos en el paso 2 durante este paso de implementación.  
    6\.  \*\*Ejecución y Confirmación de Éxito de Pruebas:\*\* Usa \`run\_terminal\` para ejecutar \`pytest\` nuevamente. Itera sobre los pasos 4 y 6 si las pruebas no pasan, explicando los errores y tus correcciones en cada iteración dentro de etiquetas \<thinking\>. Continúa hasta que todas las pruebas (nuevas y existentes) pasen. Muestra la salida exitosa al usuario.  
    7\.  \*\*Refactorización (Opcional):\*\* Una vez que las pruebas pasen, revisa el código implementado. Si identificas oportunidades claras de refactorización para mejorar la legibilidad o eficiencia sin cambiar la funcionalidad, proponlas al usuario dentro de etiquetas \<refactoring\_suggestion\>. Solo aplica la refactorización si el usuario lo aprueba explícitamente.  
    8\.  \*\*Finalización:\*\* Informa al usuario que la implementación está completa y probada.  
  \</instructions\>

  \<context\>  
    \<tech\_stack\>Python, Flask, PyJWT, Pytest\</tech\_stack\>  
    \<coding\_standards\>Adherirse estrictamente a PEP 8\. Usar type hints.\</coding\_standards\>  
    \<project\_structure\>El código de la aplicación reside en \`app/\`, las pruebas en \`tests/\`.\</project\_structure\>  
  \</context\>

  \<output\_format\>  
    Comunícate de forma clara y concisa. Usa etiquetas \<plan\>, \<thinking\>, \<refactoring\_suggestion\> según se indica en las instrucciones. Muestra la salida relevante del terminal cuando ejecutes pruebas.  
  \</output\_format\>

  \<user\_query\>  
    {{USER\_QUERY\_PLACEHOLDER}}  
  \</user\_query\>  
\</system\_prompt\>

* **Anotaciones:**  
  * \<role\>: Define una personalidad experta y orientada a TDD.  
  * \<instructions\>: Delinea el flujo TDD paso a paso de forma explícita, incluyendo la planificación inicial y la restricción crítica de no modificar pruebas.  
  * \<context\>: Proporciona información clave sobre la tecnología y estándares.  
  * \<output\_format\>: Guía el estilo de comunicación y el uso de etiquetas específicas.  
  * {{USER\_QUERY\_PLACEHOLDER}}: Indica dónde se insertará la solicitud específica del usuario.

### **5.2 Ejemplo 2: Prompt de Agente para Depuración (Análisis de Causa Raíz)**

* **Título:** Agente de Depuración Java Spring Boot para NullPointerException  
* **Objetivo:** Diagnosticar la causa raíz de una NullPointerException reportada en una aplicación Java Spring Boot, basándose en el stack trace y el código proporcionado.  
* **Contexto Asumido:** Acceso a read\_file, codebase\_search. El usuario proporciona el stack trace y fragmentos de código relevantes. Potencialmente run\_terminal si se necesita inspeccionar logs específicos.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Ingeniero de Software Java Senior especializado en depurar aplicaciones Spring Boot complejas. Tu fortaleza es el análisis metódico para encontrar la causa raíz de los errores, no solo tratar los síntomas. Eres cauteloso al proponer cambios y priorizas la comprensión completa del problema.  
  \</role\>

  \<instructions\>  
    El usuario ha reportado una \`NullPointerException\` y proporcionará un stack trace y código relevante. Tu tarea es diagnosticar la causa raíz. Sigue estos pasos:  
    1\.  \*\*Análisis Inicial:\*\* Revisa cuidadosamente el \`\<stack\_trace\>\` y el \`\<relevant\_code\>\` proporcionados por el usuario. Identifica la línea exacta donde ocurre la excepción y las variables involucradas.  
    2\.  \*\*Razonamiento (CoT):\*\* Dentro de etiquetas \`\<thinking\>\`, realiza un análisis paso a paso:  
        \*   Formula hipótesis sobre qué variable específica podría ser \`null\` y por qué podría serlo en ese punto del código (ej. no inicializada, retorno inesperado de una llamada, estado incorrecto).  
        \*   Considera el flujo de ejecución que lleva a la línea problemática.  
        \*   Si la información proporcionada es insuficiente, identifica qué información adicional se necesita (ej. valor de una variable específica antes de la excepción, contenido de un log particular, código de una función llamada). Explica \*por qué\* necesitas esa información antes de solicitarla al usuario o intentar obtenerla con herramientas (si están disponibles y permitidas).  
    3\.  \*\*Solicitud de Información / Uso de Herramientas (si es necesario):\*\* Si necesitas más información, pídesela claramente al usuario o usa las herramientas disponibles (\`read\_file\`, \`codebase\_search\`, \`run\_terminal\` para logs específicos) para obtenerla, explicando tu intención.  
    4\.  \*\*Identificación de Causa Raíz:\*\* Basándote en el análisis y la información recopilada, determina la causa raíz más probable de la \`NullPointerException\`. Explica claramente tu conclusión al usuario.  
    5\.  \*\*Sugerencia de Solución:\*\*  
        \*   Si estás \*muy seguro\* de la causa raíz y la solución es un cambio de código directo y seguro (ej. añadir una comprobación de nulidad, inicializar una variable), propón el cambio usando la herramienta \`edit\_file\`, explicando la corrección.  
        \*   Si no estás completamente seguro, o si la solución requiere cambios más complejos o podría tener efectos secundarios, NO propongas un cambio de código directo. En su lugar, explica la causa raíz identificada y sugiere pasos para confirmar el diagnóstico (ej. añadir sentencias de logging específicas antes de la línea problemática, escribir un test unitario que reproduzca el error) o discute posibles enfoques de solución con el usuario. Prioriza la adición de logging o pruebas sobre cambios de código especulativos.\[85\]  
  \</instructions\>

  \<input\_data\>  
    \<stack\_trace\>  
      {{STACK\_TRACE\_PLACEHOLDER}}  
    \</stack\_trace\>  
    \<relevant\_code\>  
      {{RELEVANT\_CODE\_PLACEHOLDER}}  
    \</relevant\_code\>  
  \</input\_data\>

  \<output\_format\>  
    Usa etiquetas \`\<thinking\>\` para tu análisis detallado. Comunica tus hallazgos y recomendaciones de forma clara y profesional. Sé explícito sobre tu nivel de confianza al proponer soluciones de código.  
  \</output\_format\>

  \<user\_query\>  
    Ayúdame a depurar esta NullPointerException.  
  \</user\_query\>  
\</system\_prompt\>

* **Anotaciones:**  
  * \<role\>: Establece experiencia en Java/Spring y enfoque en causa raíz.  
  * \<instructions\>: Define un proceso de diagnóstico metódico, enfatizando el CoT (\<thinking\>) y la precaución al proponer arreglos.85  
  * \<input\_data\>: Estructura la información proporcionada por el usuario.  
  * \<output\_format\>: Refuerza el uso de \<thinking\> y la comunicación clara.  
  * Condicionalidad en la Solución: Instruye al agente a proponer cambios de código solo con alta confianza, priorizando el logging/pruebas en caso contrario.85

### **5.3 Ejemplo 3: Prompt de Agente para Refactorización de Código (Enfoque en Legibilidad)**

* **Título:** Agente de Refactorización JavaScript para Legibilidad  
* **Objetivo:** Refactorizar una función JavaScript compleja para mejorar su legibilidad y mantenibilidad, sin alterar su comportamiento lógico fundamental.  
* **Contexto Asumido:** Acceso a edit\_file, codebase\_search. El usuario proporciona la función a refactorizar. El proyecto sigue la guía de estilo de Airbnb JavaScript. Se asume la existencia de un conjunto de pruebas que cubren la función.  
* **System Prompt Completo:**

XML

\<system\_prompt\>  
  \<role\>  
    Eres un Desarrollador JavaScript experto con una pasión por escribir código

#### **Works cited**

1. Introducing Claude 3.5 Sonnet \- Anthropic, accessed April 21, 2025, [https://www.anthropic.com/news/claude-3-5-sonnet](https://www.anthropic.com/news/claude-3-5-sonnet)  
2. Introducing computer use, a new Claude 3.5 Sonnet, and Claude 3.5 Haiku \- Anthropic, accessed April 21, 2025, [https://www.anthropic.com/news/3-5-models-and-computer-use](https://www.anthropic.com/news/3-5-models-and-computer-use)  
3. Anthropic's Claude 3.5 Sonnet now available in Snowflake Cortex AI, accessed April 21, 2025, [https://www.snowflake.com/en/blog/anthropic-claude-sonnet-cortex-ai/](https://www.snowflake.com/en/blog/anthropic-claude-sonnet-cortex-ai/)  
4. Claude 3.5 Sonnet and Haiku: The New Frontier in Artificial Intelligence and Coding, accessed April 21, 2025, [https://www.codescrum.com/blog/claude-3-5-sonnet-and-haiku-the-new-frontier-in-artificial-intelligence-and-coding](https://www.codescrum.com/blog/claude-3-5-sonnet-and-haiku-the-new-frontier-in-artificial-intelligence-and-coding)  
5. Gemini 2.0 vs Claude 3.5 Sonnet: Which is Better for Coding? \- Analytics Vidhya, accessed April 21, 2025, [https://www.analyticsvidhya.com/blog/2025/02/gemini-2-0-vs-claude-3-5-sonnet/](https://www.analyticsvidhya.com/blog/2025/02/gemini-2-0-vs-claude-3-5-sonnet/)  
6. Claude 3.5 Sonnet: The New Benchmark in AI Capabilities \- Amity Solutions, accessed April 21, 2025, [https://www.amitysolutions.com/blog/claude-3-5-sonnet-redefining-ai](https://www.amitysolutions.com/blog/claude-3-5-sonnet-redefining-ai)  
7. Announcing three new capabilities for the Claude 3.5 model family in Amazon Bedrock, accessed April 21, 2025, [https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/)  
8. Use Anthropic's Claude models | Generative AI on Vertex AI \- Google Cloud, accessed April 21, 2025, [https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude)  
9. 10 Things to Know About Claude 3.5 Sonnet \- Unite.AI, accessed April 21, 2025, [https://www.unite.ai/10-things-to-know-about-claude-3-5-sonnet/](https://www.unite.ai/10-things-to-know-about-claude-3-5-sonnet/)  
10. Prompt engineering techniques and best practices: Learn by doing with Anthropic's Claude 3 on Amazon Bedrock | AWS Machine Learning Blog, accessed April 21, 2025, [https://aws.amazon.com/blogs/machine-learning/prompt-engineering-techniques-and-best-practices-learn-by-doing-with-anthropics-claude-3-on-amazon-bedrock/](https://aws.amazon.com/blogs/machine-learning/prompt-engineering-techniques-and-best-practices-learn-by-doing-with-anthropics-claude-3-on-amazon-bedrock/)  
11. Giving Claude a role with a system prompt \- Anthropic, accessed April 21, 2025, [https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts)  
12. Cursor Agent mode System Prompt \- 宝玉的分享, accessed April 21, 2025, [https://baoyu.io/blog/cursor-agent-system-prompt](https://baoyu.io/blog/cursor-agent-system-prompt)  
13. leaked-system-prompts/cursor-ide-agent-claude-sonnet-3.7\_20250309.md at main \- GitHub, accessed April 21, 2025, [https://github.com/jujumilk3/leaked-system-prompts/blob/main/cursor-ide-agent-claude-sonnet-3.7\_20250309.md](https://github.com/jujumilk3/leaked-system-prompts/blob/main/cursor-ide-agent-claude-sonnet-3.7_20250309.md)  
14. Claude Sonnet 3.5's actual initial system prompt : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1e3p427/claude\_sonnet\_35s\_actual\_initial\_system\_prompt/](https://www.reddit.com/r/ClaudeAI/comments/1e3p427/claude_sonnet_35s_actual_initial_system_prompt/)  
15. Sonnet 3.5 system prompt : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1dkdmt8/sonnet\_35\_system\_prompt/](https://www.reddit.com/r/ClaudeAI/comments/1dkdmt8/sonnet_35_system_prompt/)  
16. Claude 3.5 Haiku and Upgraded Sonnet \- Learn Prompting, accessed April 21, 2025, [https://learnprompting.org/docs/models/claude](https://learnprompting.org/docs/models/claude)  
17. Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet \- Anthropic, accessed April 21, 2025, [https://www.anthropic.com/research/swe-bench-sonnet](https://www.anthropic.com/research/swe-bench-sonnet)  
18. Claude 3.5 Sonnet significantly outperforms GPT-4o (and all other models) on LiveBench : r/singularity \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/singularity/comments/1dkqlx0/claude\_35\_sonnet\_significantly\_outperforms\_gpt4o/](https://www.reddit.com/r/singularity/comments/1dkqlx0/claude_35_sonnet_significantly_outperforms_gpt4o/)  
19. Tool use with Claude \- Anthropic, accessed April 21, 2025, [https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)  
20. System Prompts \- Anthropic API, accessed April 21, 2025, [https://docs.anthropic.com/en/release-notes/system-prompts](https://docs.anthropic.com/en/release-notes/system-prompts)  
21. Claude Sonnet 3.5 Agent is sooo much better than o3 mini high \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/claude-sonnet-3-5-agent-is-sooo-much-better-than-o3-mini-high/51608](https://forum.cursor.com/t/claude-sonnet-3-5-agent-is-sooo-much-better-than-o3-mini-high/51608)  
22. Windsurf vs Cursor: using o3-mini vs DeepSeek R1 (Claude 3.5 Sonnet as judge) \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/Codeium/comments/1ii4ltb/windsurf\_vs\_cursor\_using\_o3mini\_vs\_deepseek\_r1/](https://www.reddit.com/r/Codeium/comments/1ii4ltb/windsurf_vs_cursor_using_o3mini_vs_deepseek_r1/)  
23. Sonnet 3.5 \>\>\> Sonnet 3.7 for programming : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1j0oya8/sonnet\_35\_sonnet\_37\_for\_programming/](https://www.reddit.com/r/ClaudeAI/comments/1j0oya8/sonnet_35_sonnet_37_for_programming/)  
24. Agentic Showdown: Claude Code vs Codex vs Cursor \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1k3uffy/agentic\_showdown\_claude\_code\_vs\_codex\_vs\_cursor/](https://www.reddit.com/r/cursor/comments/1k3uffy/agentic_showdown_claude_code_vs_codex_vs_cursor/)  
25. Claude Sonnet 3.5 for coding : r/PromptEngineering \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/PromptEngineering/comments/1dkw3oa/claude\_sonnet\_35\_for\_coding/](https://www.reddit.com/r/PromptEngineering/comments/1dkw3oa/claude_sonnet_35_for_coding/)  
26. Claude 3.5 Sonnet, Full Artifacts System Prompt \- GitHub Gist, accessed April 21, 2025, [https://gist.github.com/dedlim/6bf6d81f77c19e20cd40594aa09e3ecd](https://gist.github.com/dedlim/6bf6d81f77c19e20cd40594aa09e3ecd)  
27. Claude Code: Best practices for agentic coding \- Anthropic, accessed April 21, 2025, [https://www.anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)  
28. OpenAI o3-mini vs Claude 3.5 Sonnet \- Analytics Vidhya, accessed April 21, 2025, [https://www.analyticsvidhya.com/blog/2025/02/openai-o3-mini-vs-claude-3-5-sonnet/](https://www.analyticsvidhya.com/blog/2025/02/openai-o3-mini-vs-claude-3-5-sonnet/)  
29. langgptai/awesome-claude-prompts \- GitHub, accessed April 21, 2025, [https://github.com/langgptai/awesome-claude-prompts](https://github.com/langgptai/awesome-claude-prompts)  
30. Gemini 2.5 vs Sonnet 3.7 vs Grok 3 vs GPT-4.1 vs GPT-o3 \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/gemini-2-5-vs-sonnet-3-7-vs-grok-3-vs-gpt-4-1-vs-gpt-o3/79699](https://forum.cursor.com/t/gemini-2-5-vs-sonnet-3-7-vs-grok-3-vs-gpt-4-1-vs-gpt-o3/79699)  
31. Details about METR's preliminary evaluation of Claude 3.5 Sonnet, accessed April 21, 2025, [https://metr.github.io/autonomy-evals-guide/claude-3-5-sonnet-report/](https://metr.github.io/autonomy-evals-guide/claude-3-5-sonnet-report/)  
32. Claude 3.7 Sonnet and Claude Code \- Anthropic, accessed April 21, 2025, [https://www.anthropic.com/news/claude-3-7-sonnet](https://www.anthropic.com/news/claude-3-7-sonnet)  
33. How to use Claude 3.5 Sonnet: A tutorial to develop a game from scratch \- YouTube, accessed April 21, 2025, [https://www.youtube.com/watch?v=3tO9jfUP9Xw](https://www.youtube.com/watch?v=3tO9jfUP9Xw)  
34. Claude 3.7 vs 3.5 Sonnet for Coding \- Which One Should You Use? | 16x Prompt, accessed April 21, 2025, [https://prompt.16x.engineer/blog/claude-37-vs-35-sonnet-coding](https://prompt.16x.engineer/blog/claude-37-vs-35-sonnet-coding)  
35. Is GPT-4o better to use or is Claude 3.5 sonnet better to use? \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/is-gpt-4o-better-to-use-or-is-claude-3-5-sonnet-better-to-use/51766](https://forum.cursor.com/t/is-gpt-4o-better-to-use-or-is-claude-3-5-sonnet-better-to-use/51766)  
36. Which performance benchmark makes Claude 3.5 sonnet , the best at Coding ? : r/ClaudeAI, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1fpnsqd/which\_performance\_benchmark\_makes\_claude\_35/](https://www.reddit.com/r/ClaudeAI/comments/1fpnsqd/which_performance_benchmark_makes_claude_35/)  
37. Meet the New Claude 3.5 Sonnet: An AI That Uses Computers \- Kommunicate, accessed April 21, 2025, [https://www.kommunicate.io/blog/new-claude-3-5-sonnet/](https://www.kommunicate.io/blog/new-claude-3-5-sonnet/)  
38. Claude Code overview \- Anthropic API, accessed April 21, 2025, [https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)  
39. Claude Code: Best practices for agentic coding \- Hacker News, accessed April 21, 2025, [https://news.ycombinator.com/item?id=43735550](https://news.ycombinator.com/item?id=43735550)  
40. Claude AI Review: How is Version 3.7 Better Than 3.5? \- Unite.AI, accessed April 21, 2025, [https://www.unite.ai/claude-ai-review/](https://www.unite.ai/claude-ai-review/)  
41. Claude 3.5 Sonnet does many mistakes since last update \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1h205rk/claude\_35\_sonnet\_does\_many\_mistakes\_since\_last/](https://www.reddit.com/r/ClaudeAI/comments/1h205rk/claude_35_sonnet_does_many_mistakes_since_last/)  
42. Maximize Your Coding with Claude 3.5 Sonnet: Essential Tips and Tricks \- Arsturn, accessed April 21, 2025, [https://www.arsturn.com/blog/coding-with-claude-3-5-sonnet-tips-and-tricks](https://www.arsturn.com/blog/coding-with-claude-3-5-sonnet-tips-and-tricks)  
43. Sonnet 3.5 Coding System Prompt (v2 with explainer) : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1e39tvj/sonnet\_35\_coding\_system\_prompt\_v2\_with\_explainer/](https://www.reddit.com/r/ClaudeAI/comments/1e39tvj/sonnet_35_coding_system_prompt_v2_with_explainer/)  
44. Sonnet 3.5 for Coding \- System Prompt : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1dwra38/sonnet\_35\_for\_coding\_system\_prompt/](https://www.reddit.com/r/ClaudeAI/comments/1dwra38/sonnet_35_for_coding_system_prompt/)  
45. "Supervisory" agent to guide "worker" agent \- Feature Requests \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/supervisory-agent-to-guide-worker-agent/49395](https://forum.cursor.com/t/supervisory-agent-to-guide-worker-agent/49395)  
46. Use XML tags to structure your prompts \- Anthropic, accessed April 21, 2025, [https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)  
47. Anthropic Claude 3.5 Sonnet \- Amazon Bedrock, accessed April 21, 2025, [https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt-claude-sonnet.html](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt-claude-sonnet.html)  
48. Prompt engineering overview \- Anthropic API, accessed April 21, 2025, [https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)  
49. Anthropic Claude models \- Amazon Bedrock \- AWS Documentation, accessed April 21, 2025, [https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html)  
50. Secret Claude AI System Prompts Revealed–What Can We Learn From Them? \- Decrypt, accessed April 21, 2025, [https://decrypt.co/246695/claude-ai-system-prompts-anthropic-tips](https://decrypt.co/246695/claude-ai-system-prompts-anthropic-tips)  
51. Let Claude think (chain of thought prompting) to increase ..., accessed April 21, 2025, [https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)  
52. I made claude 3.5 sonnet to outperform openai o1 in terms of reasoning : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1fx51z4/i\_made\_claude\_35\_sonnet\_to\_outperform\_openai\_o1/](https://www.reddit.com/r/ClaudeAI/comments/1fx51z4/i_made_claude_35_sonnet_to_outperform_openai_o1/)  
53. Anthropic Release Notes: System Prompts \- Simon Willison's Weblog, accessed April 21, 2025, [https://simonwillison.net/2024/Aug/26/anthropic-system-prompts/](https://simonwillison.net/2024/Aug/26/anthropic-system-prompts/)  
54. aws-samples/prompt-engineering-with-anthropic-claude-v-3 \- GitHub, accessed April 21, 2025, [https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3)  
55. The People Who Are Having Amazing Results With Claude, Prompt Engineer Like This: : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1exy6re/the\_people\_who\_are\_having\_amazing\_results\_with/](https://www.reddit.com/r/ClaudeAI/comments/1exy6re/the_people_who_are_having_amazing_results_with/)  
56. Building Effective AI Agents \\ Anthropic, accessed April 21, 2025, [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)  
57. Cursor AI Prompting Rules \- This gist provides structured prompting ..., accessed April 21, 2025, [https://gist.github.com/aashari/07cc9c1b6c0debbeb4f4d94a3a81339e](https://gist.github.com/aashari/07cc9c1b6c0debbeb4f4d94a3a81339e)  
58. A curated list of awesome .cursorrules files \- GitHub, accessed April 21, 2025, [https://github.com/PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)  
59. Subreddit for CursorRules discussions?? : r/cursor, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1j0edub/subreddit\_for\_cursorrules\_discussions/](https://www.reddit.com/r/cursor/comments/1j0edub/subreddit_for_cursorrules_discussions/)  
60. Create the Perfect System Prompt for New Coders on Cursor AI (AKA Rules for AI), accessed April 21, 2025, [https://www.youtube.com/watch?v=0b-Up2JDqgc](https://www.youtube.com/watch?v=0b-Up2JDqgc)  
61. Cursor Rules \- GitHub Gist, accessed April 21, 2025, [https://gist.github.com/Shpigford/b3c2abe5e631f3edc4eac919ed31eaeb](https://gist.github.com/Shpigford/b3c2abe5e631f3edc4eac919ed31eaeb)  
62. Cursor Rules: Customizing AI Behavior for Personalized Coding. | cursor101.com, accessed April 21, 2025, [https://cursor101.com/article/cursor-rules-customizing-ai-behavior](https://cursor101.com/article/cursor-rules-customizing-ai-behavior)  
63. Sharing my .cursorrules after several successful projects with thousands of users : r/cursor \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1jplf6u/sharing\_my\_cursorrules\_after\_several\_successful/](https://www.reddit.com/r/cursor/comments/1jplf6u/sharing_my_cursorrules_after_several_successful/)  
64. Mastering Cursor Rules: A Developer's Guide to Smart AI Integration \- DEV Community, accessed April 21, 2025, [https://dev.to/dpaluy/mastering-cursor-rules-a-developers-guide-to-smart-ai-integration-1k65](https://dev.to/dpaluy/mastering-cursor-rules-a-developers-guide-to-smart-ai-integration-1k65)  
65. Cursorrules, Rules for AI, or Project Rules : r/cursor \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1icmmb0/cursorrules\_rules\_for\_ai\_or\_project\_rules/](https://www.reddit.com/r/cursor/comments/1icmmb0/cursorrules_rules_for_ai_or_project_rules/)  
66. Cursor AI: A Guide With 10 Practical Examples \- DataCamp, accessed April 21, 2025, [https://www.datacamp.com/tutorial/cursor-ai-code-editor](https://www.datacamp.com/tutorial/cursor-ai-code-editor)  
67. Good examples of .cursorrules file? \- Discussion \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/good-examples-of-cursorrules-file/4346](https://forum.cursor.com/t/good-examples-of-cursorrules-file/4346)  
68. My experience with Cursor \+ attached .cursorrules \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1hgzk5e/my\_experience\_with\_cursor\_attached\_cursorrules/](https://www.reddit.com/r/cursor/comments/1hgzk5e/my_experience_with_cursor_attached_cursorrules/)  
69. Rules \- Cursor, accessed April 21, 2025, [https://docs.cursor.com/context/rules-for-ai](https://docs.cursor.com/context/rules-for-ai)  
70. How to Use Cursor More Efficiently\! : r/ChatGPTCoding \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ChatGPTCoding/comments/1hu276s/how\_to\_use\_cursor\_more\_efficiently/](https://www.reddit.com/r/ChatGPTCoding/comments/1hu276s/how_to_use_cursor_more_efficiently/)  
71. AI Rule that ACTUALLY works vs. cursorrules : r/cursor \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/cursor/comments/1hxi68d/ai\_rule\_that\_actually\_works\_vs\_cursorrules/](https://www.reddit.com/r/cursor/comments/1hxi68d/ai_rule_that_actually_works_vs_cursorrules/)  
72. How to Use Cursor AI Agents \- Apidog, accessed April 21, 2025, [https://apidog.com/blog/cursor-ai-agents/](https://apidog.com/blog/cursor-ai-agents/)  
73. Discussion \- Cursor Forum, accessed April 21, 2025, [https://forum.cursor.com/c/general/4?page=41](https://forum.cursor.com/c/general/4?page=41)  
74. Repository-Defined Custom Agents \- Feature Requests \- Cursor ..., accessed April 21, 2025, [https://forum.cursor.com/t/repository-defined-custom-agents/80004](https://forum.cursor.com/t/repository-defined-custom-agents/80004)  
75. cursor-custom-agents-rules-generator/readme.md at main \- GitHub, accessed April 21, 2025, [https://github.com/bmadcode/cursor-custom-agents-rules-generator/blob/main/readme.md](https://github.com/bmadcode/cursor-custom-agents-rules-generator/blob/main/readme.md)  
76. Cursor AI for Software Development: A Beginner's Guide | Pragmatic Coders, accessed April 21, 2025, [https://www.pragmaticcoders.com/blog/cursor-ai-for-software-development](https://www.pragmaticcoders.com/blog/cursor-ai-for-software-development)  
77. Agent Mode \- Cursor, accessed April 21, 2025, [https://docs.cursor.com/chat/agent](https://docs.cursor.com/chat/agent)  
78. Agent \- Cursor, accessed April 21, 2025, [https://docs.cursor.com/agent](https://docs.cursor.com/agent)  
79. Custom Modes \- Cursor, accessed April 21, 2025, [https://docs.cursor.com/chat/custom-modes](https://docs.cursor.com/chat/custom-modes)  
80. Changelog \- Mar 23, 2025 | Cursor \- The AI Code Editor, accessed April 21, 2025, [https://www.cursor.com/changelog/chat-tabs-custom-modes-sound-notification](https://www.cursor.com/changelog/chat-tabs-custom-modes-sound-notification)  
81. Custom chats are amazing (Tips) 0.47.x \- Page 2 \- Showcase \- Cursor \- Community Forum, accessed April 21, 2025, [https://forum.cursor.com/t/custom-chats-are-amazing-tips-0-47-x/62270?page=2](https://forum.cursor.com/t/custom-chats-are-amazing-tips-0-47-x/62270?page=2)  
82. cursor-custom-agents-rules-generator/docs/agile-readme.md at main \- GitHub, accessed April 21, 2025, [https://github.com/bmadcode/cursor-custom-agents-rules-generator/blob/main/docs/agile-readme.md](https://github.com/bmadcode/cursor-custom-agents-rules-generator/blob/main/docs/agile-readme.md)  
83. \[Guide\] A Simpler, More Autonomous AI Workflow for Cursor \[New ..., accessed April 21, 2025, [https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688](https://forum.cursor.com/t/guide-a-simpler-more-autonomous-ai-workflow-for-cursor/70688)  
84. Claude 3.5 Sonnet for agentic coding \- YouTube, accessed April 21, 2025, [https://www.youtube.com/watch?v=A598ESCoC70](https://www.youtube.com/watch?v=A598ESCoC70)  
85. Cursor Agent System Prompt (March 2025\) \- GitHub Gist, accessed April 21, 2025, [https://gist.github.com/sshh12/25ad2e40529b269a88b80e7cf1c38084](https://gist.github.com/sshh12/25ad2e40529b269a88b80e7cf1c38084)  
86. Way Enough \- Claude 3.5 Sonnet Codes Really Well \- Dan Corin, accessed April 21, 2025, [https://danielcorin.com/posts/2024/claude-3.5-sonnet-codes/](https://danielcorin.com/posts/2024/claude-3.5-sonnet-codes/)  
87. The Only Prompt You Need : r/ClaudeAI \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1gds696/the\_only\_prompt\_you\_need/](https://www.reddit.com/r/ClaudeAI/comments/1gds696/the_only_prompt_you_need/)  
88. Cline+Claude 3.5 Sonnet \= Awesome : r/ChatGPTCoding \- Reddit, accessed April 21, 2025, [https://www.reddit.com/r/ChatGPTCoding/comments/1hrhb2m/clineclaude\_35\_sonnet\_awesome/](https://www.reddit.com/r/ChatGPTCoding/comments/1hrhb2m/clineclaude_35_sonnet_awesome/)  
89. Overview \- Cursor, accessed April 21, 2025, [https://docs.cursor.com/chat/overview](https://docs.cursor.com/chat/overview)