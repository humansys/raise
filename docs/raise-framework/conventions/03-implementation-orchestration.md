# 03: Orquestación de la Implementación

## Rol del Desarrollador: Orquestador

*   El desarrollador **no es solo un codificador**, sino un **orquestador** que guía a los agentes de IA para producir código confiable y alineado.

## Proceso y Convenciones

1.  **Iniciar con Contexto:** Antes de solicitar generación de código, **siempre** proporcionar a la IA el contexto relevante. Esto incluye enlaces directos a los archivos de:
    *   Historia de Usuario (`<jira-id>-US-*.md`)
    *   Diseño Técnico (`<jira-id>-TechDesign-*.md`)
    *   Especificaciones de API (`<jira-id>-API-*.md`) y Componente (`<jira-id>-Component-*.md`) pertinentes.
2.  **Explicabilidad Primero:** Antes de generar bloques significativos de código, **activamente pedir a la IA que explique su enfoque:**
    *   *"Explícame paso a paso cómo implementarías [funcionalidad X] basado en [diseño Y]."*
    *   *"¿Cuál es tu razonamiento para elegir [estructura Z]?"*
    *   Este paso es **crucial** para asegurar alineación y mejorar la calidad del resultado final.
3.  **Generación Guiada por Reglas:** La IA utilizará las reglas definidas en `.cursor/rules/`. Referenciar reglas específicas en el prompt si se busca un comportamiento particular.
4.  **Fomentar TDD (Test-Driven Development):** Siempre que sea práctico, instruir a la IA para que genere las **pruebas unitarias** (basadas en Criterios de Aceptación y Especificaciones) **antes** o junto con el código de implementación.
5.  **Validación Crítica del Código Generado:** El código generado por IA **nunca** debe aceptarse ciegamente. El orquestador humano **debe**: 
    *   Revisarlo críticamente contra el Diseño Técnico, las Especificaciones y los Requisitos.
    *   Verificar su adherencia a las reglas de estilo y patrones arquitectónicos.
    *   Refinar los prompts y solicitar regeneración si el código no cumple los estándares o la intención.
6.  **Iteración:** El proceso es iterativo. Usar el feedback y las explicaciones para refinar la guía proporcionada a la IA. 