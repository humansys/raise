# 05: Mejora Continua

## Objetivo

*   Mejorar sistemáticamente la efectividad del proceso RaiSE, los artefactos de documentación, las reglas de IA y las definiciones de agentes basados en la experiencia práctica.

## Proceso y Convenciones

1.  **Retrospectivas Ágiles:** Realizar retrospectivas (formales o informales) al finalizar hitos significativos (ej. completar una Feature). Foco: ¿Qué funcionó bien en la colaboración humano-IA? ¿Qué fue difícil? ¿Dónde falló la guía o el contexto?
2.  **Identificar Fricciones:** Analizar las interacciones con la IA. ¿Hubo prompts repetitivos? ¿La IA malinterpretó consistentemente algún concepto? ¿Faltaron reglas o contexto?
3.  **Refinar Artefactos:** Basado en las retrospectivas, actualizar y mejorar:
    *   **Reglas Cursor (`.cursor/rules/`):** Añadir, eliminar o modificar reglas para mejorar la calidad o consistencia del código generado.
    *   **Plantillas (`.raise/templates/`):** Ajustar las plantillas si se detectan secciones faltantes o confusas.
    *   **Convenciones (`.raise/conventions/`):** Clarificar o añadir convenciones si el proceso actual es ambiguo (¡este mismo directorio!).
4.  **Evolucionar Agentes:** Sugerir mejoras a las definiciones de los agentes (prompts, capacidades) si su desempeño fue subóptimo.
5.  **Compartir Aprendizajes:** Documentar brevemente los cambios realizados y compartir los aprendizajes clave con el resto del equipo para fomentar una mejora colectiva.
6.  **Archivado:** Recordar aplicar el proceso de archivado definido en la regla `500-documentation-standards.mdc` para mantener limpios los directorios activos. 