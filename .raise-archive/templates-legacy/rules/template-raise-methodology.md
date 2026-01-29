---
name: "{{rule_name}}"
description: "{{rule_description}}"
globs: ["{{glob_pattern}}"] # Ejemplo: ["docs/**/*.md", "src/**/*.kata.md"]
alwaysApply: {{always_apply_false}}
tags: ["raise", "methodology", "{{tag1}}", "{{tag2}}"]
priority: {{priority_0xx}} # Ejemplo: 10, 20, 30
category: "raise-methodology"
related: [".cursor/rules/{{related_methodology_rule}}.mdc", ".cursor/rules/910-rule-management.mdc"]
references: ["{{raise_documentation_link}}"]
---

# {{rule_name}}

## 1. Propósito de la Regla Metodológica

[Describe el aspecto específico de la metodología RaiSE que esta regla aborda. Por ejemplo, estándares de documentación, flujo de desarrollo con katas, principios de diseño, etc.]

## 2. Principios Fundamentales de RaiSE Aplicables

[Enumera y explica brevemente los principios de RaiSE (ej. Documentación Precede al Código, Explicabilidad, Desarrollo Guiado por Katas) que son particularmente relevantes para esta regla.]

*   **Principio 1**: {{explicacion_principio_1}}
*   **Principio 2**: {{explicacion_principio_2}}

## 3. Guías y Procedimientos Específicos

[Detalla las instrucciones, pasos, o estándares que los desarrolladores y el asistente de IA deben seguir en relación con este aspecto de la metodología RaiSE.]

### 3.1. {{subseccion_guia_1}}

*   Directriz 1...
*   Directriz 2...

### 3.2. {{subseccion_guia_2}}

*   Directriz 1...
*   Directriz 2...

## 4. Aplicación por el Asistente de IA

[Proporciona instrucciones claras sobre cómo el asistente de IA debe interpretar y aplicar esta regla metodológica.]

*   Al generar documentación de tipo {{tipo_documento}}, asegurar que {{requisito_especifico}}.
*   Cuando se trabaja en un archivo de kata (`*.kata.md`), seguir el formato {{formato_kata}}.
*   Antes de generar código para un paso de una kata, verificar que {{condicion_previa_kata}}.

## 5. Ejemplos

[Proporciona ejemplos concretos que ilustren la aplicación de esta regla. Pueden ser fragmentos de documentos, katas, o descripciones de procesos.]

### Ejemplo 1: {{example_1_description}}

```{{example_1_language_if_code}}
{{example_1_content}}
```

### Ejemplo 2: {{example_2_description}}

```{{example_2_language_if_code}}
{{example_2_content}}
```

## 6. Consideraciones Adicionales

*   [Consideración sobre la interacción con otras reglas metodológicas.]
*   [Impacto de esta regla en el ciclo de vida del desarrollo.]

## 7. Mantenimiento de esta Regla

*   Esta regla debe revisarse si hay cambios en los procesos fundamentales del framework RaiSE o en las plantillas de documentación asociadas. 