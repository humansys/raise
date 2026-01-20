# Implementation Plan: Transform Commands Script

**Branch**: `007-transform-commands` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-transform-commands/spec.md`

## Summary

Script bash que automatiza la transformación de 9 archivos de comandos desde estructura plana (`.claude/commands/`) hacia estructura organizada (`.specify-raise/commands/`), renombrando archivos y actualizando referencias internas en el frontmatter YAML.

## Technical Context

**Language/Version**: Bash 4.0+ (requerido para arrays asociativos)
**Primary Dependencies**: Ninguna (solo utilidades estándar: sed, mkdir, cp)
**Storage**: N/A (operaciones de archivo)
**Testing**: Manual - verificación de archivos y grep de referencias
**Target Platform**: Unix/Linux/Git Bash (Windows MINGW64)
**Project Type**: Single script
**Performance Goals**: < 5 segundos para 9 archivos
**Constraints**: Sin dependencias externas, único archivo .sh
**Scale/Scope**: 9 archivos de entrada, 9 patrones de reemplazo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Términos alineados con glosario (Mapeo, Frontmatter) | [x] |
| II. Governance como Código | Script versionado en Git, mapeos declarativos | [x] |
| III. Validación en Cada Fase | Exit codes, mensajes de error, verificación post-ejecución | [x] |
| IV. Simplicidad | Un solo script, sin abstracciones innecesarias | [x] |
| V. Mejora Continua | Mapeos configurables al inicio para futuras modificaciones | [x] |

## Project Structure

### Documentation (this feature)

```text
specs/007-transform-commands/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical decisions
├── quickstart.md        # Usage guide and test scenarios
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
template/.specify/scripts/bash/raise/
└── transform-commands.sh    # Main script (único archivo)
```

**Structure Decision**: Single script sin estructura de directorios adicional. El script es autocontenido con mapeos declarativos al inicio.

## Implementation Design

### Componentes del Script

```
┌─────────────────────────────────────────────────────────────┐
│                    transform-commands.sh                     │
├─────────────────────────────────────────────────────────────┤
│  SECCIÓN 1: CONFIGURACIÓN (líneas 1-50)                     │
│  ├── FILE_MAP: array asociativo origen→destino              │
│  ├── REF_MAP: array asociativo referencia_antigua→nueva     │
│  ├── SRC_DIR: ruta carpeta origen                           │
│  └── DEST_DIR: ruta carpeta destino                         │
├─────────────────────────────────────────────────────────────┤
│  SECCIÓN 2: FUNCIONES HELPER (líneas 51-80)                 │
│  ├── error(): mensaje a stderr + exit 1                     │
│  ├── warn(): mensaje a stderr (continúa)                    │
│  └── info(): mensaje a stdout                               │
├─────────────────────────────────────────────────────────────┤
│  SECCIÓN 3: VALIDACIÓN (líneas 81-100)                      │
│  ├── Verificar existencia carpeta origen                    │
│  └── Verificar permisos escritura destino                   │
├─────────────────────────────────────────────────────────────┤
│  SECCIÓN 4: TRANSFORMACIÓN (líneas 101-150)                 │
│  ├── Crear subcarpetas destino (mkdir -p)                   │
│  ├── Loop: para cada archivo en FILE_MAP                    │
│  │   ├── Verificar archivo origen existe                    │
│  │   ├── Verificar archivo destino no existe                │
│  │   ├── Leer contenido                                     │
│  │   ├── Aplicar REF_MAP con sed                            │
│  │   └── Escribir a destino                                 │
│  └── Incrementar contador de éxitos/errores                 │
├─────────────────────────────────────────────────────────────┤
│  SECCIÓN 5: REPORTE (líneas 151-170)                        │
│  ├── Mostrar conteo de archivos procesados                  │
│  ├── Mostrar lista de errores (si los hay)                  │
│  └── Exit code: 0 si todos OK, 1 si hubo errores            │
└─────────────────────────────────────────────────────────────┘
```

### Mapeo de Archivos (FILE_MAP)

| Archivo Origen | Archivo Destino |
|----------------|-----------------|
| `speckit.specify.md` | `03-feature/speckit.1.specify.md` |
| `speckit.clarify.md` | `03-feature/speckit.2.clarify.md` |
| `speckit.plan.md` | `03-feature/speckit.3.plan.md` |
| `speckit.tasks.md` | `03-feature/speckit.4.tasks.md` |
| `speckit.analyze.md` | `03-feature/speckit.5.analyze.md` |
| `speckit.implement.md` | `03-feature/speckit.6.implement.md` |
| `speckit.checklist.md` | `03-feature/speckit.util.checklist.md` |
| `speckit.taskstoissues.md` | `03-feature/speckit.util.issues.md` |
| `speckit.constitution.md` | `01-onboarding/speckit.2.constitution.md` |

### Mapeo de Referencias (REF_MAP)

| Referencia Antigua | Referencia Nueva |
|--------------------|------------------|
| `speckit.specify` | `speckit.1.specify` |
| `speckit.clarify` | `speckit.2.clarify` |
| `speckit.plan` | `speckit.3.plan` |
| `speckit.tasks` | `speckit.4.tasks` |
| `speckit.analyze` | `speckit.5.analyze` |
| `speckit.implement` | `speckit.6.implement` |
| `speckit.checklist` | `speckit.util.checklist` |
| `speckit.taskstoissues` | `speckit.util.issues` |
| `speckit.constitution` | `speckit.2.constitution` |

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Research | `specs/007-transform-commands/research.md` | Complete |
| Quickstart | `specs/007-transform-commands/quickstart.md` | Complete |
| Data Model | N/A (no aplica para CLI script) | N/A |
| Contracts | N/A (no aplica para CLI script) | N/A |

## Next Steps

1. Ejecutar `/speckit.4.tasks` para generar lista de tareas de implementación
2. Implementar el script según el diseño
3. Verificar con escenarios de test del quickstart.md

## Complexity Tracking

> No hay violaciones de Constitution que justificar. El diseño es simple y directo.
