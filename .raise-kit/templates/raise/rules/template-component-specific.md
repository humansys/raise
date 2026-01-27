---
name: "Estándares para Componente: {{component_name_pascal_case}}"
description: "Define la estructura, implementación y pruebas para el componente {{component_name_readable}}."
globs: ["{{glob_pattern_for_component}}"] # Ejemplo: ["src/components/{{component_name_pascal_case}}/**/*.tsx", "src/core/{{component_name_pascal_case}}.cs"]
alwaysApply: false
tags: ["component", "{{component_tag}}", "{{technology_tag}}"]
priority: {{priority_2xx_specific}} # Ejemplo: 250, 255, 260
category: "repo-architecture" # O podría ser una subcategoría como "component-specific"
related: [".cursor/rules/{{related_arch_pattern_if_any}}.mdc", ".cursor/rules/{{related_tech_standard}}.mdc"]
references: ["{{link_to_relevant_kata_step}}", "{{link_to_tech_design_if_any}}"]
---

# Estándares para Componente: {{component_name_readable}}

## 1. Propósito y Responsabilidad del Componente

*   **Propósito Principal**: [Describe la finalidad principal del componente {{component_name_readable}}.]
*   **Responsabilidades Clave**:
    1.  [Responsabilidad 1]
    2.  [Responsabilidad 2]
    3.  ...
*   **Contexto de Uso**: [¿En qué partes de la aplicación o flujo de trabajo se utiliza este componente? ¿Es parte de una kata específica?]

## 2. Estructura de Archivos y Nomenclatura

*   **Directorio Raíz del Componente**: `{{base_path}}/{{component_name_pascal_case}}/`
*   **Archivo Principal**: `{{component_name_pascal_case}}.{{extension}}` (ej. `UserProfile.tsx`, `OrderRepository.cs`)
*   **Archivos Relacionados (si aplica)**:
    *   Interfaz/Tipos: `{{component_name_pascal_case}}.types.{{extension}}` o `i{{component_name_pascal_case}}.interface.{{extension}}`
    *   Estilos (si aplica): `{{component_name_pascal_case}}.styles.{{extension}}`
    *   Pruebas: `{{component_name_pascal_case}}.test.{{extension}}` o `{{component_name_pascal_case}}.spec.{{extension}}`
    *   Mocks: `{{component_name_pascal_case}}.mock.{{extension}}`
    *   Archivos de soporte (helpers, utils locales): `{{component_name_pascal_case}}.utils.{{extension}}`

## 3. Definición de Interfaz/Contrato (API del Componente)

[Describe las props, métodos públicos, eventos, o la interfaz que el componente expone a otros.]

```{{language_tag}}
// Definición de la interfaz para {{component_name_readable}}
{{interface_definition_code}}
```

*   **Propiedad/Método 1 (`{{prop_method_1_name}}`)**: [Descripción, tipo, obligatoriedad]
*   **Propiedad/Método 2 (`{{prop_method_2_name}}`)**: [Descripción, tipo, obligatoriedad]

## 4. Guías de Implementación Específicas

[Detalles sobre cómo debe implementarse la lógica interna del componente.]

### 4.1. {{aspecto_implementacion_1}}

*   [Directriz específica 1]
*   [Directriz específica 2]

### 4.2. Manejo de Estado (Si aplica)

*   [Cómo debe gestionarse el estado interno del componente. ¿Usa estado local, Redux, hooks específicos?]

### 4.3. Efectos Secundarios / Interacciones Externas (Si aplica)

*   [Cómo maneja el componente las llamadas a APIs, interacciones con el DOM fuera de su control, etc.]

### 4.4. Consideraciones de Rendimiento

*   [Puntos clave para asegurar que el componente sea performante (ej. memoización, virtualización, etc.)]

## 5. Pruebas del Componente

[Describe la estrategia de pruebas para este componente.]

*   **Pruebas Unitarias**: Deben cubrir {{aspecto_a_cubrir_unitariamente_1}} y {{aspecto_a_cubrir_unitariamente_2}}.
    *   Casos de prueba clave: [Listar escenarios importantes a probar].
*   **Pruebas de Integración (si aplica)**: Cómo probar la interacción de este componente con {{otro_componente_o_servicio}}.
*   **Mocks Requeridos**: [Qué dependencias deben ser mockeadas y cómo.]

## 6. Ejemplos de Código

### Ejemplo 1: Uso Básico del Componente

```{{language_tag}}
// Cómo instanciar o utilizar {{component_name_readable}}
{{basic_usage_example}}
```

### Ejemplo 2: Implementación de {{metodo_o_logica_clave}}

```{{language_tag}}
// Fragmento de la implementación interna del componente
{{internal_logic_example}}
```

## 7. Consideraciones de Reusabilidad y Acoplamiento

*   [¿Está diseñado para ser reutilizable? ¿Cómo?]
*   [Dependencias principales y cómo gestionarlas para mantener bajo acoplamiento.]

## 8. Mantenimiento de esta Regla

*   Actualizar esta regla si la interfaz o las responsabilidades fundamentales del componente {{component_name_readable}} cambian significativamente.
*   Añadir nuevos ejemplos o refinar guías a medida que se gana más experiencia con el componente. 