# Propuesta de Reestructuración de Comandos (Work Cycles) v2

Basado en `docs/framework/v2.1/model/26-work-cycles-v2.1.md` y la corrección sobre la naturaleza de `analyze`.

## Estructura Propuesta

```text
.specify-raise/commands/
├── 01-onboarding/           # Ciclo de Onboarding (Setup & Gobierno)
│   ├── speckit.constitution.md
│   ├── speckit.raise.analyze-code.md
│   ├── speckit.raise.rules-generate.md
│   └── speckit.raise.rules-edit.md
│
├── 02-project/              # Ciclo de Proyecto (Definición Macro)
│   ├── speckit.raise.discovery.md
│   ├── speckit.raise.vision.md
│   └── speckit.raise.map-ecosystem.md
│
├── 03-feature/              # Ciclo de Feature (Desarrollo Diario & Calidad)
│   ├── speckit.specify.md
│   ├── speckit.clarify.md
│   ├── speckit.plan.md
│   ├── speckit.tasks.md
│   ├── speckit.analyze.md       <-- MOVIDO AQUÍ (Validación de consistencia)
│   ├── speckit.implement.md
│   ├── speckit.checklist.md
│   └── speckit.taskstoissues.md
│
└── 04-improve/              # Ciclo de Mejora (Aprendizaje & Retrospectiva)
    └── (Pendiente de implementación: retrospective, kaizen, etc.)
```

## Cambios Clave

1.  **`speckit.analyze` en Feature**: Se agrupa con las herramientas de construcción porque su función principal es validar la coherencia de los artefactos generados (Spec, Plan, Tasks) antes de la implementación. Es el "Quality Check" del ciclo de feature.
2.  **`04-improve` Placeholder**: Se mantiene la carpeta conceptualmente para futuros comandos de *raise-kit* orientados a la retrospectiva y mejora del framework, pero por ahora estará vacía de comandos estándar.

## Beneficios UX

*   **Flujo Lineal en Feature**: El dev tiene todo lo necesario para sacar una HU en una sola carpeta: Definir -> Planear -> Tareas -> **Analizar/Validar** -> Implementar.
*   **Claridad de Propósito**: Evita la confusión de pensar que `analyze` es para "analizar el proyecto" (Discovery) o "analizar mejoras" (Improve), acotándolo a su función real de consistencia operativa.
