---
name: "Estándares para {{technology_name}}"
description: "Define las mejores prácticas y convenciones para el uso de {{technology_name}} en el proyecto."
globs: ["{{glob_pattern_for_technology}}"] # Ejemplo: ["src/**/*.ts", "pom.xml", "*.java"]
alwaysApply: false
tags: ["{{technology_tag}}", "standards", "best-practices", "{{tag1}}"]
priority: {{priority_1xx}} # Ejemplo: 110, 120
category: "tech-standards"
related: [".cursor/rules/{{related_tech_rule}}.mdc"]
references: ["{{official_documentation_link}}", "{{style_guide_link}}"]
---

# Estándares para {{technology_name}}

## 1. Propósito de la Regla Tecnológica

[Establece el objetivo de esta regla: asegurar consistencia, calidad, rendimiento, seguridad, etc., en el uso de {{technology_name}}.]

## 2. Versión Principal Soportada (Si aplica)

*   **Versión Mínima/Recomendada**: {{version_number}}
*   **Justificación**: [Breve explicación de por qué se eligió esta versión, si es relevante.]

## 3. Convenciones de Codificación Específicas

[Detalla las guías de estilo, nombramiento, y formato para {{technology_name}}.]

### 3.1. Nomenclatura

*   Variables: `{{variable_naming_convention}}`
*   Funciones/Métodos: `{{function_naming_convention}}`
*   Clases/Interfaces/Tipos: `{{class_naming_convention}}`
*   Constantes: `{{constant_naming_convention}}`

### 3.2. Formato y Estilo

*   [Referencia a formateadores automáticos (ej. Prettier, Black) si se usan.]
*   [Reglas específicas de indentación, espaciado, longitud de línea no cubiertas por formateadores.]

### 3.3. Patrones de Uso Recomendados

*   [Patrón recomendado 1 para {{technology_name}}]
*   [Patrón recomendado 2 para {{technology_name}}]

### 3.4. Patrones a Evitar (Anti-patrones)

*   [Anti-patrón 1 y por qué evitarlo]
*   [Anti-patrón 2 y por qué evitarlo]

## 4. Gestión de Dependencias (Si aplica)

*   [Cómo declarar dependencias de {{technology_name}}.]
*   [Herramientas preferidas para gestión de dependencias (npm, yarn, maven, pip).]

## 5. Pruebas Específicas para {{technology_name}}

*   [Frameworks de prueba recomendados para {{technology_name}}.]
*   [Tipos de pruebas importantes (unitarias, integración) y cómo implementarlas.]

## 6. Seguridad en {{technology_name}}

*   [Prácticas de seguridad clave al usar {{technology_name}}.]
*   [Vulnerabilidades comunes a tener en cuenta.]

## 7. Ejemplos

[Proporciona ejemplos de código concisos que ilustren las convenciones y patrones.]

### Ejemplo 1: Uso Correcto de {{feature_or_pattern}}

```{{language_tag_for_technology}}
// Código que sigue las directrices
{{correct_code_example}}
```

### Ejemplo 2: Uso Incorrecto de {{feature_or_pattern}} (y cómo corregirlo)

```{{language_tag_for_technology}}
// Código incorrecto
{{incorrect_code_example}}

// Corrección o explicación
```

## 8. Herramientas y Linters

*   [Linters específicos para {{technology_name}} (ej. ESLint con plugins, Pylint, StyleCop).]
*   [Configuraciones recomendadas para estas herramientas.]

## 9. Consideraciones Adicionales

*   [Puntos sobre rendimiento, interoperabilidad, etc.]

## 10. Mantenimiento de esta Regla

*   Revisar esta regla cuando haya actualizaciones mayores de {{technology_name}} o cambios en las herramientas de desarrollo asociadas. 