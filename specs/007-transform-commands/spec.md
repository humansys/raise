# Feature Specification: Transform Commands Script

**Feature Branch**: `001-transform-commands`
**Created**: 2026-01-20
**Status**: Draft
**Input**: Script bash para transformar comandos de estructura plana a estructura organizada

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Transformación Completa de Comandos (Priority: P1)

Como desarrollador RaiSE, quiero ejecutar un script que transforme automáticamente todos los archivos de comandos desde la estructura plana hacia la estructura organizada, para eliminar el proceso manual propenso a errores.

**Why this priority**: Es la funcionalidad core del feature. Sin esta capacidad, el script no tiene valor.

**Independent Test**: Puede probarse ejecutando el script con la carpeta origen poblada y verificando que los 9 archivos aparezcan en destino con nombres y contenido correctos.

**Acceptance Scenarios**:

1. **Given** carpeta origen con 9 archivos `speckit.*.md`, **When** ejecuto el script, **Then** se crean 9 archivos en destino con nombres transformados según el mapeo definido
2. **Given** archivos con referencias `agent: speckit.plan` en frontmatter, **When** ejecuto el script, **Then** las referencias se actualizan a `agent: speckit.3.plan`
3. **Given** carpeta destino no existe, **When** ejecuto el script, **Then** se crean las subcarpetas `01-onboarding/` y `03-feature/` automáticamente

---

### User Story 2 - Reporte de Resultado (Priority: P2)

Como desarrollador RaiSE, quiero ver un resumen de la ejecución del script indicando cuántos archivos se procesaron exitosamente y si hubo errores, para confirmar que la transformación fue completa.

**Why this priority**: Proporciona feedback esencial al usuario pero la transformación funciona sin él.

**Independent Test**: Ejecutar el script y verificar que el output incluye conteo de archivos procesados.

**Acceptance Scenarios**:

1. **Given** transformación exitosa de 9 archivos, **When** el script termina, **Then** muestra mensaje "9 archivos transformados exitosamente"
2. **Given** error en un archivo, **When** el script termina, **Then** muestra el nombre del archivo con error y el mensaje de error

---

### User Story 3 - Validación Pre-ejecución (Priority: P3)

Como desarrollador RaiSE, quiero que el script valide que la carpeta origen existe y tiene archivos antes de intentar la transformación, para evitar errores silenciosos.

**Why this priority**: Mejora la experiencia pero no es crítico para la funcionalidad core.

**Independent Test**: Ejecutar el script con carpeta origen inexistente y verificar mensaje de error claro.

**Acceptance Scenarios**:

1. **Given** carpeta origen no existe, **When** ejecuto el script, **Then** muestra error "Carpeta origen no encontrada" y termina con código de error
2. **Given** carpeta origen vacía, **When** ejecuto el script, **Then** muestra advertencia "No hay archivos para transformar"

---

### Edge Cases

- ¿Qué pasa si un archivo destino ya existe? El script debe advertir y no sobrescribir (comportamiento seguro por defecto)
- ¿Qué pasa si un archivo origen no coincide con el mapeo? El script debe ignorarlo y reportar "archivo no reconocido"
- ¿Qué pasa si el frontmatter tiene formato inesperado? El script debe copiar el archivo sin modificar y advertir

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El script DEBE leer todos los archivos `.md` de la carpeta origen especificada
- **FR-002**: El script DEBE aplicar el mapeo de nombres de archivo definido (9 transformaciones)
- **FR-003**: El script DEBE actualizar las referencias internas en el campo `agent:` del frontmatter YAML (9 patrones)
- **FR-004**: El script DEBE crear las subcarpetas destino si no existen (`01-onboarding/`, `03-feature/`)
- **FR-005**: El script DEBE escribir los archivos transformados en la carpeta destino correspondiente
- **FR-006**: El script DEBE reportar el número de archivos procesados exitosamente
- **FR-007**: El script DEBE reportar errores específicos si algún archivo falla
- **FR-008**: El script DEBE validar existencia de carpeta origen antes de procesar
- **FR-009**: El script DEBE terminar con exit code 0 en éxito y 1 en error

### Key Entities

- **Archivo Comando**: Archivo Markdown (.md) con frontmatter YAML que contiene la definición de un comando speckit
- **Mapeo de Archivo**: Relación origen→destino para nombres de archivo (ej: `speckit.specify.md` → `03-feature/speckit.1.specify.md`)
- **Mapeo de Referencia**: Relación origen→destino para referencias internas (ej: `speckit.plan` → `speckit.3.plan`)
- **Frontmatter**: Sección YAML al inicio del archivo delimitada por `---` que contiene metadatos como `agent:`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El script transforma 100% de los archivos mapeados (9/9) en una ejecución exitosa
- **SC-002**: El script completa la transformación completa en menos de 5 segundos
- **SC-003**: Post-transformación, 0 archivos contienen referencias antiguas (verificable con grep)
- **SC-004**: El script reduce el tiempo de migración manual de 15-30 minutos a menos de 10 segundos (incluyendo verificación)

## Scope

### In Scope

- Transformación de 9 archivos de comandos speckit
- Actualización de 9 patrones de referencias internas
- Creación de estructura de carpetas destino
- Reporte básico de resultado

### Out of Scope

- Transformación inversa (destino → origen)
- Validación semántica del contenido de comandos
- Modo dry-run
- Archivo de configuración externo
- Flag --force para sobrescribir

## Assumptions

- Los archivos de origen siguen la convención de nombres `speckit.*.md`
- El frontmatter YAML usa el campo `agent:` para referencias a otros comandos
- El entorno de ejecución tiene bash 4.0+ disponible (o Git Bash en Windows)
- El usuario tiene permisos de escritura en la carpeta destino
- Las carpetas origen y destino están en el mismo sistema de archivos

## Dependencies

- PRD: `specs/main/project_requirements.md` (PRD-RAISE-001)
- Vision: `specs/main/solution_vision.md` (VIS-RAISE-001)
