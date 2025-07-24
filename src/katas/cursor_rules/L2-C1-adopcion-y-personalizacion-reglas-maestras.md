---
id: L2-C1-adopcion-y-personalizacion-reglas-maestras
nivel: 2
tags: [cursor-rules, raise, governance, refactoring, setup]
status: "Revisada"
---
# L2-C1: Revisión y Personalización de un Conjunto de Reglas Locales Pre-cargado

## Metadatos

- **Id**: L2-C1-adopcion-y-personalizacion-reglas-maestras
- **Nivel**: 2
- **Título**: Revisión y Personalización de un Conjunto de Reglas Locales Pre-cargado
- **Propósito**: Formalizar un proceso sistemático para revisar un conjunto de reglas locales (pre-cargadas desde un estándar maestro), y decidir si se mantienen, personalizan (anulan) o eliminan según la aplicabilidad al proyecto.
- **Contexto**: Esta Kata se aplica a un repositorio que ha sido inicializado con un conjunto completo de reglas maestras copiadas directamente en su directorio local `.cursor/rules/`. El objetivo es adaptar este conjunto de reglas genérico a las necesidades específicas del proyecto.
- **Audiencia**: Desarrollador Backend, Arquitecto de Software, Tech Lead. **Puede ser ejecutada con la ayuda de un asistente de IA.**

## Pre-condiciones

- El directorio `.cursor/rules/` del repositorio ha sido pre-poblado con un conjunto completo de reglas de un template maestro (ej. `raise-jf-ai-common`).
- Se ha creado un archivo `local-rules-index.md` en `.cursor/rules/` para documentar el estado y las decisiones sobre cada regla.
- El desarrollador tiene un claro entendimiento de la arquitectura, patrones y necesidades específicas del proyecto.
- El desarrollador tiene la autoridad para tomar decisiones sobre qué reglas mantener, modificar o eliminar.

## Pasos de la Kata

El proceso es iterativo y se debe repetir para cada regla presente en el directorio local `.cursor/rules/`.

### Paso 1: Selección de la Regla a Revisar

- **Acción**: Listar los archivos en el directorio local `.cursor/rules/` y seleccionar la siguiente regla a evaluar (ej. `001-general-coding-standards.mdc`).
- **Criterios de Aceptación**:
  - Se ha identificado una regla local para la revisión.
  - Se comprende el propósito y las directrices de la regla seleccionada.

### Paso 2: Auditoría y Análisis de Relevancia

- **Acción**: Analizar el código base y la arquitectura del repositorio para determinar la relevancia y el grado de alineación con la regla local seleccionada.
- **Asistencia IA**: Este paso puede ser acelerado por un asistente de IA. El desarrollador puede pedir al asistente que:
    - Busque ejemplos de código que implementen (o violen) los patrones descritos en la regla.
    - Compare los principios de la regla con el código existente para identificar desviaciones.
- **Criterios de Aceptación**:
  - Se ha llegado a una conclusión clara sobre qué acción tomar:
    - **Mantener**: La regla está totalmente alineada con las prácticas deseadas para el proyecto.
    - **Personalizar (Anular)**: La regla es conceptualmente útil, pero requiere modificaciones para adaptarse a las especificidades del proyecto.
    - **Eliminar**: La regla describe un patrón o tecnología que no se utiliza o no es aplicable al proyecto.

### Paso 3: Ejecución de la Decisión Estratégica

- **Acción**: Basado en el resultado del Paso 2, ejecutar la acción correspondiente.

#### Caso 3A: Mantener la Regla

- **Acción**: El archivo de la regla se deja sin cambios. Se registra la decisión en el índice.
- **Criterios de Aceptación**:
  - El archivo `.cursor/rules/[ID-de-la-regla].mdc` permanece intacto.
  - Se ha anotado en el archivo `local-rules-index.md` que la regla `[ID-de-la-regla]` tiene el estado: **`Mantenida`**.

#### Caso 3B: Personalizar (Anular) la Regla

- **Acción**:
  1. Modificar el archivo de la regla local (`.cursor/rules/[ID-de-la-regla].mdc`) para que refleje con precisión las prácticas específicas del repositorio.
  2. **Añadir una sección `## Nota de Personalización` al final del archivo.** Esta sección es la justificación detallada. Debe explicar claramente **por qué** esta regla difiere del estándar maestro y cuál es la justificación técnica o de negocio.
  3. Registrar la personalización en `local-rules-index.md` con el estado: **`Personalizada`** y un resumen de la justificación.
- **Criterios de Aceptación**:
  - El archivo de la regla local ha sido modificado para adaptarse al proyecto.
  - El archivo de la regla contiene la sección `## Nota de Personalización` con la justificación requerida.
  - La personalización ha sido registrada correctamente en `local-rules-index.md`.

#### Caso 3C: Eliminar la Regla

- **Acción**:
  1. Eliminar el archivo de la regla del directorio local `.cursor/rules/[ID-de-la-regla].mdc`.
  2. Registrar la eliminación en `local-rules-index.md` con el estado: **`Eliminada`** y una breve justificación (ej. "No aplicable, el proyecto no usa gRPC").
- **Criterios de Aceptación**:
  - El archivo de la regla ha sido eliminado del sistema de archivos.
  - La eliminación y su justificación han sido registradas en `local-rules-index.md`.

### Paso 4: Commit y Siguiente Iteración

- **Acción**:
  - Hacer commit de los cambios realizados (modificaciones de reglas, eliminaciones y la actualización del archivo `local-rules-index.md`).
  - Volver al **Paso 1** para la siguiente regla en el directorio.
- **Criterios de Aceptación**:
  - Los cambios están versionados en Git.
  - El proceso está listo para la siguiente iteración.

## Post-condiciones

- El directorio `.cursor/rules/` del repositorio contiene únicamente las reglas que son activamente aplicables al proyecto.
- Algunas de las reglas en `.cursor/rules/` pueden haber sido personalizadas para las necesidades del proyecto.
- El archivo `local-rules-index.md` sirve como un registro de auditoría completo, detallando el estado y la justificación de cada regla del conjunto maestro original.
- El repositorio opera bajo un conjunto de reglas de gobierno explícito, curado y documentado.

## Gobernanza y Mantenimiento a Largo Plazo

- **Transparencia**: El archivo `local-rules-index.md` es el "panel de control" principal para entender rápidamente las desviaciones y el estado del conjunto de reglas del repositorio.

- **Proceso de Sincronización con Nuevas Versiones Maestras**:
  1. Obtener la nueva versión del conjunto de reglas maestro como una carpeta separada.
  2. Utilizar una herramienta de comparación de directorios (diff) para comparar la nueva carpeta maestra con el directorio local `.cursor/rules/` del proyecto.
  3. Analizar las diferencias:
      - **Reglas Nuevas**: Para cada regla que exista en el maestro pero no en el local, decidir si debe ser adoptada. Si es así, copiarla al directorio local e iniciar esta misma Kata para esa nueva regla.
      - **Reglas Modificadas**: Para las reglas que existen en ambos lugares pero tienen diferencias, revisar los cambios. Si la regla local fue `Mantenida`, se puede sobrescribir con la nueva versión. Si fue `Personalizada`, se deben fusionar manualmente los cambios relevantes de la versión maestra en la regla local, preservando la personalización.
      - **Reglas Eliminadas**: Si una regla fue eliminada en el maestro, considerar si también debe ser eliminada localmente.
  4. Actualizar el archivo `local-rules-index.md` para reflejar cualquier cambio o nueva decisión.
  5. Hacer commit de la nueva configuración de reglas.
