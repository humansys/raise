---
name: "Patrón Arquitectónico: {{pattern_name}}"
description: "Describe la implementación estándar del patrón {{pattern_name}} en este repositorio."
globs: ["{{glob_pattern_for_architecture}}"] # Ejemplo: ["src/services/**/*.ts", "src/repositories/**/*.cs"]
alwaysApply: false
tags: ["architecture", "pattern", "{{pattern_tag}}", "{{tag1}}"]
priority: {{priority_2xx}} # Ejemplo: 210, 220
category: "repo-architecture"
related: [".cursor/rules/{{related_arch_rule_1}}.mdc", ".cursor/rules/{{related_arch_rule_2}}.mdc"]
references: ["{{design_document_link}}", "{{external_pattern_link}}"]
---

# Patrón Arquitectónico: {{pattern_name}}

## 1. Propósito del Patrón en este Repositorio

[Explica por qué se utiliza el patrón {{pattern_name}} en este proyecto y qué problemas resuelve. Describe su rol dentro de la arquitectura general.]

## 2. Estructura y Componentes Clave del Patrón

[Detalla los elementos principales que conforman este patrón en el contexto del repositorio.]

*   **Componente A ({{component_A_role}})**: [Descripción y responsabilidades]
*   **Componente B ({{component_B_role}})**: [Descripción y responsabilidades]
*   **Interacciones**: [Cómo interactúan los componentes A y B]

### Diagrama (Opcional)

[Si es útil, incluye un diagrama simple (texto o enlace a imagen) que ilustre la estructura del patrón.]

## 3. Guías de Implementación Específicas

[Proporciona directrices concretas sobre cómo implementar este patrón.]

### 3.1. Nomenclatura y Ubicación de Archivos

*   Archivos relacionados con `{{pattern_name}}` deben ubicarse en `{{recommended_directory_path}}`.
*   Nombres de clases/interfaces deben seguir el formato `{{ClassName}}{{PatternSuffix}}` (ej. `User{{PatternSuffix}}`).

### 3.2. Responsabilidades y Contratos

*   [Responsabilidad clave 1 del patrón]
*   [Contrato o interfaz principal que deben implementar los componentes del patrón]

### 3.3. Interacción con Otros Patrones/Capas

*   Cómo `{{pattern_name}}` interactúa con la capa de {{otra_capa_ej_servicio}}.
*   Cómo `{{pattern_name}}` interactúa con el patrón {{otro_patron_ej_repositorio}}.

## 4. Aplicación por el Asistente de IA

[Instrucciones para la IA al generar o modificar código relacionado con este patrón.]

*   Al crear un nuevo `{{pattern_name}}`, asegurar que la estructura de archivos y la nomenclatura sean consistentes con esta regla.
*   Verificar que las responsabilidades de cada componente del patrón se respeten.
*   Asegurar que las interacciones con {{otro_patron_ej_servicio}} se realicen a través de {{metodo_interaccion_definido}}.

## 5. Ejemplos de Implementación

[Proporciona ejemplos de código específicos del proyecto que ilustren la correcta implementación del patrón {{pattern_name}}.]

### Ejemplo 1: Implementación de {{component_A_role}}

```{{language_tag}}
// {{path_to_example_component_A}}
{{example_code_component_A}}
```

### Ejemplo 2: Interacción entre {{component_A_role}} y {{component_B_role}}

```{{language_tag}}
// {{path_to_example_interaction}}
{{example_code_interaction}}
```

### Ejemplo 3: Anti-Patrón (Uso Incorrecto y Cómo Evitarlo)

```{{language_tag}}
// {{path_to_antipattern_example}}
{{antipattern_code_example}}
// Explicación: Este enfoque es incorrecto porque {{reason}}. 
// Se debe {{correct_approach}} en su lugar.
```

## 6. Pruebas para el Patrón {{pattern_name}}

*   [Estrategias de prueba específicas para componentes que implementan este patrón.]
*   [Consideraciones sobre mocks y dependencias al probar.]

## 7. Consideraciones Adicionales

*   [Ventajas de usar este patrón en el contexto del proyecto.]
*   [Posibles desventajas o tradeoffs a tener en cuenta.]
*   [Cuándo NO usar este patrón.]

## 8. Mantenimiento de esta Regla

*   Revisar esta regla si hay cambios significativos en la arquitectura del repositorio o en cómo se aplica el patrón {{pattern_name}}.
*   Actualizar ejemplos si las implementaciones de referencia evolucionan. 