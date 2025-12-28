# 00: Visión General y Principios Fundamentales de RaiSE

## Propósito

Estas convenciones guían la colaboración humano-IA bajo el framework RaiSE (Reliable AI Software Engineering). Su objetivo es asegurar un desarrollo de software consistente y confiable, enfatizando el rol evolucionado del desarrollador como **Orquestador** de la IA.

## Principios Clave de RaiSE

1.  **Humano como Orquestador:** El desarrollador guía activamente a la IA, definiendo el "qué" y el "por qué", y validando el "cómo". No es un simple receptor de código.
2.  **Contexto Estructurado es Esencial:** Proporcionar contexto claro y relevante (requisitos, diseño, especificaciones) a través de los artefactos documentales definidos es vital para la precisión de la IA.
3.  **La Explicabilidad Mejora la Calidad:** Solicitar activamente a la IA que explique su razonamiento ("Explícame cómo...") antes de generar código mejora la calidad de la solución y refuerza el entendimiento humano.
4.  **La Estructura Fomenta la Confiabilidad:** Usar rigurosamente las plantillas (`.raise/templates/`) y las reglas (`.cursor/rules/`) asegura consistencia y resultados predecibles.
5.  **Validación Rigurosa:** La validación multinivel (pruebas TDD, validación semántica contra especificaciones, revisiones humanas) es parte integral del flujo, no un paso opcional.
6.  **Aprendizaje Continuo:** Cada interacción es una oportunidad para mejorar (retrospectivas, refinamiento de reglas, prompts y plantillas).

## Documentos de Referencia

*   Visión de la Solución RaiSE (`docs/raise-work-docs/Vision/RaiSE_Solution_Vision.md`)
*   Marco Teórico RaiSE (`docs/raise-corpus/theory/marco-teorico-raise.md`) 