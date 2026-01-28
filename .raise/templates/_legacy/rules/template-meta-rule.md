---
name: "{{rule_name}}"
description: "{{rule_description}}"
globs: ["{{glob_pattern}}"]
alwaysApply: {{always_apply_false}}
tags: ["meta", "{{tag1}}", "{{tag2}}"]
priority: {{priority_9xx}} # Ejemplo: 910, 920
category: "meta-rules"
related: [".cursor/rules/{{related_rule_1}}.mdc"]
references: ["{{reference_link_1}}"]
---

# {{rule_name}}

## 1. Propósito

[Explica brevemente el objetivo de esta meta-regla. ¿Qué aspecto de la gestión o interpretación de las reglas aborda?]

## 2. Definiciones Clave (Si aplica)

[Define cualquier término específico que sea crucial para entender esta regla.]

## 3. Guías Específicas de la Meta-Regla

[Detalla las instrucciones o directrices que esta meta-regla establece.]

*   Directriz 1...
*   Directriz 2...

## 4. Aplicación e Interpretación

[Explica cómo esta meta-regla debe ser aplicada por el asistente de IA y cómo afecta la interpretación de otras reglas.]

## 5. Ejemplos (Si aplica)

[Proporciona ejemplos que ilustren la aplicación de esta meta-regla.]

### Ejemplo 1: {{example_1_description}}

```
{{example_1_code_or_scenario}}
```

## 6. Consideraciones Adicionales

*   [Consideración 1]
*   [Consideración 2]

## 7. Mantenimiento de esta Meta-Regla

*   Esta regla debe ser revisada si hay cambios fundamentales en la estructura o gestión de las reglas Cursor del proyecto. 