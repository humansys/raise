# L2-06: Establecimiento de Meta-Reglas Fundamentales

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 detalla los pasos para crear e implementar las Meta-Reglas fundamentales que guían tanto al asistente de IA en la gestión de las propias reglas como el orden de precedencia y carga de todas las Reglas Cursor del proyecto.

## 2. Alcance y Objetivos

* Definir y generar la meta-regla para la **Gestión de Reglas por la IA** (anteriormente L2-06).
* Definir y generar la meta-regla para la **Precedencia de Reglas** (anteriormente L2-07).
* Asegurar que ambas meta-reglas tengan los `globs` apropiados para aplicarse a los archivos de reglas.
* Actualizar los documentos de gobernanza para reflejar la creación de estas meta-reglas.

## 3. Prerrequisitos

* Haber completado la Sub-Kata `L2-02-inicializacion-gobernanza-reglas.md`.
* Tener acceso a plantillas o ejemplos de estas meta-reglas (ej., las versiones previas de `jf-backend-profile` como `901-ia-rule-management.mdc` y `902-rule-precedence.mdc`).
* Agente IA configurado con la herramienta `edit_file`.
* Conocimiento del formato de las Reglas Cursor (`.mdc` con front matter YAML).
* El nombre del repositorio (`[nombre-repo]`) debe ser conocido.

## 4. Pasos Detallados para la Creación de las Meta-Reglas

### Parte A: Meta-Regla para la Gestión de Reglas por la IA

#### Paso 4.A.1: Definición del Contenido de la Meta-Regla de Gestión

* **Acción**: Adaptar el contenido de una plantilla o ejemplo existente.
* **Contenido Clave**: Identidad y rol del asistente, responsabilidades, referencia al sistema de reglas, proceso de trabajo, buenas prácticas de autoría, estilo de comunicación, auto-aplicación de la regla.
* **Observaciones a Registrar**: Contenido final para la meta-regla de gestión.

#### Paso 4.A.2: Definición del Front Matter (Gestión)

* **Acción**: Definir campos para `901-ia-rule-management.mdc` (o similar).
  * `name`: "Gestión de Reglas de IA por el Asistente (Meta-Regla)"
  * `description`: "Meta-regla que define cómo el asistente de IA debe gestionar y mantener el conjunto de Reglas Cursor del proyecto."
  * `globs`: `[".cursor/rules/**/*.mdc", ".cursor/rules/*.mdc"]`
  * `tags`: `["meta-rule", "ia-management", "governance"]`
  * `order`: `901`

#### Paso 4.A.3: Generación del Archivo de Meta-Regla (Gestión)

* **Acción**: Crear/actualizar el archivo `.cursor/rules/901-ia-rule-management.mdc`.
* **Herramienta**: `edit_file`

### Parte B: Meta-Regla para la Precedencia de Reglas

#### Paso 4.B.1: Definición del Contenido de la Meta-Regla de Precedencia

* **Acción**: Adaptar el contenido de un ejemplo existente.
* **Contenido Clave**: Propósito de la precedencia, sistema de numeración, orden de categorías, resolución de conflictos, aplicación a todas las reglas.
* **Observaciones a Registrar**: Contenido final para la meta-regla de precedencia.

#### Paso 4.B.2: Definición del Front Matter (Precedencia)

* **Acción**: Definir campos para `902-rule-precedence.mdc` (o similar).
  * `name`: "Precedencia y Orden de Carga de Reglas (Meta-Regla)"
  * `description`: "Meta-regla que define la jerarquía, el orden de carga y la resolución de conflictos para las Reglas Cursor del proyecto."
  * `globs`: `[".cursor/rules/**/*.mdc", ".cursor/rules/*.mdc"]`
  * `tags`: `["meta-rule", "precedence", "order", "governance"]`
  * `order`: `902`

#### Paso 4.B.3: Generación del Archivo de Meta-Regla (Precedencia)

* **Acción**: Crear/actualizar el archivo `.cursor/rules/902-rule-precedence.mdc`.
* **Herramienta**: `edit_file`

### Parte C: Actualización de Documentos de Gobernanza (para ambas meta-reglas)

#### Paso 4.C.1: Actualización del Documento de Razonamiento

* **Acción**: En `ai-rules-reasoning.md`, añadir entradas para `901-ia-rule-management.mdc` y `902-rule-precedence.mdc` bajo "Catálogo de Reglas Generadas y su Razonamiento", detallando su propósito e impacto.
* **Herramienta**: `edit_file`

#### Paso 4.C.2: Actualización del Índice de Reglas

* **Acción**: En `[nombre-repo]-rules-index.md`, añadir ambas reglas a la categoría "Meta-Reglas (900-999)".
* **Herramienta**: `edit_file`

#### Paso 4.C.3: Actualización del Plan de Implementación

* **Acción**: En `[nombre-repo]-implementation-plan.md`, marcar la creación de estas meta-reglas como un paso clave en la fase correspondiente (ej. "Fase 5: Establecimiento de Meta-Reglas" o la numeración que se ajuste en la Kata L0).
* **Herramienta**: `edit_file`

## 5. Entregables de esta Sub-Kata

* Archivo `.cursor/rules/901-ia-rule-management.mdc` creado/actualizado.
* Archivo `.cursor/rules/902-rule-precedence.mdc` creado/actualizado.
* Actualizaciones en `ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, y `[nombre-repo]-implementation-plan.md`.

## 6. Consideraciones Adicionales

* Estas meta-reglas son cruciales para la robustez y predictibilidad del sistema de reglas.
* El contenido debe ser claro y alineado con el funcionamiento de Cursor y los objetivos del proyecto.

## 7. Próximos Pasos (según Kata Principal Reordenada)

* Proceder con la Sub-Kata `L2-03-extraccion-generacion-regla-cursor.md` (Extracción y Generación Iterativa de Reglas Específicas del Repositorio).
