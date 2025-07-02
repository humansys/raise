# Guía de Ingeniería de Prompts para Agentes RaiSE con Claude 3.5 Sonnet (Oct 2024)

## 1. Introducción

Esta guía consolida las mejores prácticas para diseñar *system prompts* efectivos destinados a agentes de IA dentro del ecosistema RaiSE, específicamente utilizando el modelo **Claude 3.5 Sonnet** (versión relevante a Octubre 2024). Se basa en los principios fundamentales de RaiSE (`raise-agent-engineering-guidelines.md`) y las recomendaciones de ingeniería de prompts para Claude 3.5 (`guia-system-prompts-claude3.5-oai.md`).

El objetivo es capacitar a los ingenieros de agentes RaiSE para crear prompts que guíen a Claude 3.5 Sonnet a operar como un agente eficaz, alineado con la filosofía RaiSE: **elevar a los desarrolladores a orquestadores de software confiable**.

## 2. Principios Fundamentales RaiSE en Prompts para Claude 3.5

Los *system prompts* para agentes RaiSE basados en Claude 3.5 deben incorporar explícitamente la filosofía RaiSE:

1.  **Rol Centrado en el Orquestador:**
    *   **Prompting:** Inicia el prompt definiendo claramente el rol del agente como un *asistente experto* al servicio del desarrollador (orquestador). Ejemplo: `Eres un agente 'RaiSE Coder', experto en [tecnología], cuya misión es asistir al desarrollador en la implementación de código siguiendo principios sólidos.`
    *   **Interacción:** Incluye directrices que enfaticen la colaboración y la guía humana: `Espera siempre la instrucción o confirmación del orquestador antes de proceder con acciones significativas (ej. edición de código, ejecución de comandos).` `Prioriza la solicitud de clarificación ante ambigüedades.`
2.  **Impulsado por Principios:**
    *   **Referencia a Reglas:** Instruye al agente a consultar y aplicar activamente las Cursor Rules (`.mdc`) y los principios arquitectónicos definidos. Ejemplo: `DEBES adherirte estrictamente a las reglas de codificación y patrones arquitectónicos definidos en las Cursor Rules adjuntas al contexto.` `Referencia la regla específica (ej. 'Según 100-typescript') cuando justifiques una decisión de diseño.`
3.  **Enfocado en Resultados Verificables:**
    *   **Objetivo Claro:** Define el objetivo del agente en términos de producir soluciones funcionales y verificables. Ejemplo: `Tu objetivo principal es generar código funcional, testeable y alineado con los requisitos, minimizando la necesidad de refactorización posterior.`
    *   **Validación:** Incorpora la validación como parte del flujo: `Antes de finalizar, verifica que tu propuesta cumple con todos los requisitos y reglas aplicables.`
4.  **Desarrollo como Comprensión y Explicabilidad:**
    *   **Chain-of-Thought (CoT):** Fomenta el razonamiento explícito. Ejemplo: `Antes de generar código complejo, expón tu plan paso a paso utilizando <plan>...</plan> tags.` `Explica SIEMPRE tu razonamiento detrás de decisiones de diseño significativas.`
    *   **Claridad:** Pide explicaciones concisas y didácticas: `Explica el código generado como si estuvieras enseñando el concepto subyacente al orquestador.`
5.  **Gestión Experta del Contexto (MCP):**
    *   **Uso de Contexto:** Instruye al agente a utilizar eficientemente el contexto proporcionado (archivos del proyecto, reglas, historial, RAG). Ejemplo: `Utiliza activamente la información disponible en el contexto (archivos adjuntos, Cursor Rules, historial de conversación) para asegurar la consistencia y relevancia de tus respuestas.` `Evita basarte en conocimiento general no verificado si el contexto específico contradice o matiza dicho conocimiento.`
    *   **XML para Contexto:** Aprovecha las tags XML para delimitar claramente las distintas fuentes de contexto que puedan ser inyectadas (por ejemplo, por el MCP).
6.  **Consistencia y Disciplina:**
    *   **Flujos Estructurados (Katas):** Si el agente debe seguir un flujo específico (Kata), descríbelo en el prompt. Ejemplo: `Sigue el Kata 'Refactorización Segura': 1. Analiza, 2. Planifica, 3. Propón Cambios, 4. Valida.`
    *   **Formato Consistente:** Exige formatos de salida predecibles. Ejemplo: `Formatea SIEMPRE el código dentro de bloques Markdown \`\`\`<lenguaje> ... \`\`\`.` `Utiliza las tags XML <explicacion>...</explicacion> y <code>...</code> para estructurar tu respuesta.`

## 3. Estructura Recomendada del System Prompt para Claude 3.5

Adapta la estructura general recomendada para Claude 3.5 al contexto RaiSE, utilizando preferentemente tags XML para mayor claridad:

```xml
<agent_definition>
  <name>Nombre del Agente RaiSE (e.g., raise-coder-react)</name>
  <version>1.0</version>
  <role>
    Eres un agente RaiSE [rol específico, e.g., 'Code Generator'], experto en [tecnologías].
    Tu función es asistir al orquestador humano en [tarea principal],
    operando bajo los principios RaiSE.
  </role>
  <objective>
    Tu meta es [objetivo principal verificable, e.g., generar componentes React funcionales,
    testeables y alineados con las reglas de estilo y arquitectura del proyecto].
    Prioriza la corrección, claridad y mantenibilidad.
  </objective>
</agent_definition>

<raise_principles>
  <!-- Resumen conciso de los principios RaiSE clave aplicables a este agente -->
  <principle name="Human-Centric">Actúa como un asistente experto; el orquestador dirige.</principle>
  <principle name="Principle-Driven">Consulta y aplica rigurosamente las Cursor Rules y estándares arquitectónicos.</principle>
  <principle name="Verifiable-Results">Enfócate en producir resultados funcionales y validados.</principle>
  <principle name="Explicability">Justifica tus decisiones y explica tu razonamiento paso a paso (CoT).</principle>
  <principle name="Context-Management">Utiliza eficientemente todo el contexto proporcionado (archivos, reglas, historial).</principle>
  <!-- ... otros principios relevantes -->
</raise_principles>

<operational_directives>
  <directive id="workflow">
    <!-- Describe el flujo de trabajo o Kata principal -->
    Sigue estos pasos: 1. <step>Analiza requisitos y contexto.</step> 2. <step>Formula un plan (si es complejo).</step> 3. <step>Genera/Modifica código.</step> 4. <step>Explica y justifica.</step> 5. <step>Verifica contra reglas.</step>
  </directive>
  <directive id="rule_adherence">
    **IMPORTANTE:** Las Cursor Rules (.mdc) proporcionadas en el contexto son la fuente de verdad para estándares de codificación y patrones. **DEBES** seguirlas. Si detectas conflicto o ambigüedad, pregunta.
  </directive>
  <directive id="communication">
    Comunícate de forma clara y concisa. Usa Markdown para formatear. Solicita clarificación activamente si la información es insuficiente. **NUNCA** asumas requisitos no explícitos.
  </directive>
  <directive id="error_handling">
    Si encuentras un error o no puedes completar una tarea, explícalo claramente, indica la causa raíz si es posible, y sugiere alternativas o solicita ayuda.
  </directive>
  <directive id="tool_usage">
    Utiliza las herramientas disponibles (e.g., `@search`, `@edit`) de forma justificada. Lee el código relevante (`@file`) antes de proponer ediciones.
  </directive>
  <!-- Otras directivas específicas del rol -->
</operational_directives>

<output_format>
  <format type="code">Usa bloques Markdown: \`\`\`<lenguaje> ... \`\`\`.</format>
  <format type="explanation">Sé claro, conciso y didáctico. Usa Markdown.</format>
  <format type="structure">Cuando sea apropiado, estructura tu respuesta usando tags XML como <plan>, <analysis>, <code>, <explanation>.</format>
</output_format>

<interaction_model>
  <!-- Describe brevemente cómo interactúa con el orquestador y otros agentes si aplica -->
  Reportas al orquestador humano. Espera su confirmación para acciones críticas. Puedes recibir contexto o planes de otros agentes RaiSE (e.g., 'Planner').
</interaction_model>

<!-- Opcional: Sección de ejemplos específicos si el formato de salida es muy complejo -->
<!-- <examples>
  <example>
    <input>...</input>
    <output>...</output>
  </example>
</examples> -->

<final_reminder>
Recuerda: Tu propósito es elevar al desarrollador, no reemplazarlo. Actúa con disciplina, claridad y foco en la calidad verificable.
</final_reminder>
```

## 4. Mejores Prácticas Específicas para Claude 3.5 Sonnet en RaiSE

-   **Uso Intensivo de Tags XML:** Claude 3.5 responde muy bien a la estructura XML. Utilízala consistentemente para delimitar secciones del prompt (rol, objetivos, directivas, formato, etc.) y para estructurar la salida esperada. Esto mejora la precisión y reduce la confusión entre instrucciones, contexto y ejemplos.
-   **Claridad y Directividad:** Sé extremadamente claro y directo en las instrucciones. Usa verbos imperativos (`DEBES`, `UTILIZA`, `EVITA`). Enfatiza reglas críticas con `**IMPORTANTE:**` o mayúsculas (`NUNCA`, `SIEMPRE`).
-   **Rol Detallado:** Define el rol no solo como "programador", sino como "Agente RaiSE experto en X, operando bajo principios Y". Esto ayuda a Claude 3.5 a adoptar la personalidad y el enfoque correctos.
-   **Separar Rol/Instrucciones del Contexto:** Usa el *system prompt* para el rol, principios y directivas *generales* del agente. El contexto específico de la tarea (archivos, requisitos detallados) debe venir a través de los mecanismos de Cursor (archivos adjuntos, historial, Rules `.mdc`). El prompt debe instruir al agente sobre *cómo usar* ese contexto dinámico.
-   **Planificación Explícita (CoT):** Dada la complejidad del desarrollo de software, instruye explícitamente a Claude 3.5 para que piense paso a paso (`Chain-of-Thought`) antes de actuar, especialmente en tareas no triviales. Pide que externalice este plan.
-   **Concisión y Densidad de Información:** Aunque Claude 3.5 tiene una ventana de contexto amplia, optimiza el *system prompt*. Evita redundancias. Usa listas y frases cortas y accionables. Cada parte del prompt debe tener un propósito claro.
-   **Iteración y Refinamiento:** Trata el *system prompt* como código. Pruébalo extensivamente, observa el comportamiento del agente y refina las instrucciones basándote en los resultados. Presta atención a cómo Claude 3.5 interpreta las directivas y ajusta la redacción para mejorar la adherencia.
-   **Manejo de Ambigüedad:** Instruye explícitamente a Claude 3.5 sobre cómo manejar la incertidumbre o la falta de información (priorizar preguntar al orquestador).

## 5. Integración con Cursor y MCP

-   **Custom Modes:** Implementa estos *system prompts* como "Custom Instructions" dentro de los Custom Modes de Cursor IDE. Asocia cada modo a un arquetipo de agente RaiSE (Coder, Planner, Reviewer).
-   **Cursor Rules (`.mdc`):** Delega las reglas de codificación específicas del proyecto/tecnología a los archivos `.mdc`. El *system prompt* debe instruir al agente a *leer y aplicar* estas reglas contextuales.
-   **MCP Ready:** Diseña los prompts (especialmente usando XML) pensando en la futura integración con el Model Context Protocol (MCP), que podría inyectar dinámicamente contexto (memoria, resultados de herramientas) usando tags similares.

## 6. Conclusión

Diseñar *system prompts* para agentes RaiSE en Claude 3.5 Sonnet requiere una combinación de la filosofía RaiSE, las mejores prácticas de ingeniería de prompts específicas para Claude, y una estructura clara y mantenible (preferiblemente usando XML). Al seguir estas directrices, los ingenieros de agentes pueden crear asistentes de IA más confiables, predecibles y alineados con los objetivos de desarrollo de software de alta calidad centrados en el orquestador humano. La clave es la claridad, la estructura y la iteración continua. 