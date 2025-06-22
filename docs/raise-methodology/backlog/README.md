# Guía de Documentación del Backlog para el Componente `raise-methodology`

Este documento describe cómo aplicar las reglas generales de documentación del backlog de RaiSE, específicamente la **Regla 600-python-project-documentation**, dentro del contexto del componente `raise-methodology`. El objetivo es mantener un backlog estructurado y consistente para los elementos centrales de la metodología.

## Contexto del Componente

El componente `raise-methodology` alberga los elementos fundacionales de la metodología RaiSE, incluyendo:

*   Definiciones de Agentes Core
*   Plantillas Estándar (Documentos, Código)
*   Reglas del Framework (Cursor Rules)
*   Conceptos y Documentación Metodológica General

## Aplicación de Reglas de Backlog (Regla 600)

Para documentar los elementos del backlog en este componente, se seguirá **estrictamente** la **Regla 600-python-project-documentation**. Los puntos clave son:

1.  **Jerarquía Obligatoria:** Se DEBE crear una estructura de directorios jerárquica basada en la relación padre-hijo de los issues:
    *   **Capabilities:** `RAISE-<id>-CA-<nombre-capability>/` directamente bajo `raise-methodology/backlog/`.
    *   **Epics/Funcionalidades:** `RAISE-<id>-EP-<nombre-epic>/` dentro del directorio de su Capability padre.
    *   **User Stories/Historias:** `RAISE-<id>-HU-<nombre-historia>/` dentro del directorio de su Epic padre.
2.  **Nomenclatura Estricta:** Los nombres de los directorios deben seguir el formato `<jira-id>-TIPO-<nombre>` (donde TIPO es CA, EP, HU) usando identificadores de Jira del proyecto `RAISE` y nombres concisos en minúsculas separados por guiones.
3.  **Ubicación de Archivos:** TODOS los archivos relacionados con una Capability, Epic o Historia (documento principal, diagramas, notas, etc.) DEBEN residir DENTRO de su directorio correspondiente.
4.  **Prefijo de Archivos:** TODOS los archivos dentro de un directorio `CA`, `EP` o `HU` DEBEN comenzar con el prefijo `<jira-id>-TIPO-` (ej., `RAISE-117-HU-harmonizar-templates.md`, `RAISE-117-HU-diagrama-flujo.png`).
5.  **Documento Principal:** Se recomienda crear un archivo Markdown principal dentro de cada directorio (ej., `RAISE-90-CA-metodologia-raise.md`, `RAISE-118-EP-plantillas.md`, `RAISE-117-HU-harmonizar-templates.md`).
6.  **Plantillas:** Se deben usar las plantillas estándar de `.raise/templates/{lang}/` correspondientes al tipo de artefacto (capability.md, epic.md, user_story.md).

## Ejemplo de Estructura Resultante

```
raise-methodology/backlog/
└── RAISE-90-CA-metodologia-raise/
    ├── RAISE-90-CA-metodologia-raise.md  # Documento principal de la Capacidad
    ├── RAISE-90-CA-principios-diagrama.png
    ├── RAISE-118-EP-plantillas/          # Directorio del Epic/Funcionalidad hijo
    │   ├── RAISE-118-EP-plantillas.md      # Documento principal del Epic
    │   ├── RAISE-118-EP-tipos-plantilla.md
    │   └── RAISE-117-HU-harmonizar-templates/ # Directorio de la Historia hija
    │       └── RAISE-117-HU-harmonizar-templates.md # Documento principal de la Historia
    │       └── RAISE-117-HU-plan-implementacion.md
    └── RAISE-86-EP-reglas/               # Otro Epic/Funcionalidad hijo
        └── RAISE-86-EP-reglas.md
```

## Proceso (Resumen Regla 600)

1.  Identificar tipo de artefacto (CA, EP, HU), idioma y JIRA ID.
2.  Localizar plantilla en `.raise/templates/{lang}/`.
3.  Recopilar contexto y nombre descriptivo.
4.  Construir ruta y nombre de directorio/archivo según Regla 600.
5.  Poblar plantilla.
6.  Crear directorio y archivo(s) en la ubicación correcta.
7.  Asegurar que todos los archivos relacionados estén dentro del directorio y usen el prefijo correcto.

**Nota:** Este README refleja la estructura obligatoria definida por la Regla 600. Cualquier desviación debe ser justificada y documentada. 