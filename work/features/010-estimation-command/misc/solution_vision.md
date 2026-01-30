---
document_id: "VIS-RAISE-001"
title: "Transform Commands Script - Documento RaiSEVision"
project_name: "transform-commands-script"
client: "RaiSE Framework"
version: "1.0"
date: "2026-01-20"
author: "Orquestador"
related_docs:
  - "PRD-RAISE-001"
status: "Draft"
---

# Transform Commands Script - Documento RaiSEVision

## Contexto de Negocio

### Declaración del Problema
*(Fuente: PRD Sec 1.2)*

El framework RaiSE mantiene comandos en una estructura plana (`.claude/commands/`) que necesita migrarse a una estructura organizada por categorías (`.specify-raise/commands/`). Esta migración requiere:
- **Renombrar archivos** siguiendo una nueva convención con prefijos numéricos
- **Actualizar referencias internas** en el frontmatter YAML de cada archivo

**¿Quién se ve afectado?** Desarrolladores y mantenedores del framework RaiSE.
**¿Cuál es el impacto?** Proceso manual de ~15-30 minutos propenso a errores de consistencia.
**¿Cuándo ocurre?** Cada vez que se sincroniza o actualiza la estructura de comandos.
**¿Por qué es importante?** La inconsistencia entre nombres de archivo y referencias internas rompe los handoffs entre comandos.

### Visión de la Solución
*(Fuente: PRD Sec 1.1, 3.1)*

Un **script bash autónomo** que automatiza completamente la transformación de comandos en una sola ejecución.

**Propuesta de valor central:**
- Eliminar el proceso manual de migración de comandos
- Garantizar consistencia 100% entre nombres de archivo y referencias internas

**Diferenciadores clave:**
- Sin dependencias externas (solo bash 4.0+)
- Mapeos configurables al inicio del script
- Compatible con Git Bash en Windows

**Resultados objetivo:**
- Transformación completa en < 5 segundos
- 0 errores de referencias huérfanas

## Alineación Estratégica

### Metas de Negocio → Mecanismos Técnicos
*(Fuente: PRD Sec 1.3)*

| Meta de Negocio | Mecanismo Técnico |
|-----------------|-------------------|
| **Meta 1:** Automatizar transformación | Script bash con loop sobre archivos origen, aplicando mapeo de nombres |
| **Meta 2:** Garantizar consistencia | Función `sed` para reemplazar referencias en frontmatter YAML |
| **Meta 3:** Mantener trazabilidad | Arrays asociativos con mapeo explícito origen→destino documentado |

### Métricas de Negocio → Métricas Técnicas

| Métrica de Negocio | Métrica Técnica | Cómo se Mide |
|--------------------|-----------------|--------------|
| Tasa transformación 100% | Exit code 0 + conteo archivos | `$?` + comparar count origen vs destino |
| 0 referencias huérfanas | Grep post-transformación | `grep -r "speckit\." destino` sin matches antiguos |
| < 5 segundos ejecución | Tiempo wall-clock | `time script.sh` |

## Impacto en el Usuario
*(Fuente: PRD Sec 2.2)*

| Stakeholder | Puntos de Dolor Actuales | Beneficios Esperados |
|-------------|--------------------------|----------------------|
| Desarrollador RaiSE | Proceso manual tedioso, 15-30 min por migración | Ejecutar 1 comando, < 5 segundos |
| Mantenedor RaiSE | Inconsistencias entre archivos y referencias | Consistencia garantizada automáticamente |

## Alcance del MVP

### Imprescindible (Must Have)
*(Fuente: PRD Sec 3.1)*

1. **Transformación de nombres de archivo** - 9 archivos con mapeo definido
2. **Actualización de referencias internas** - 9 patrones de reemplazo en campo `agent:`
3. **Creación de subcarpetas destino** - `01-onboarding/`, `03-feature/`
4. **Reporte de resultado** - Conteo de archivos procesados y errores

### Deseable (Futuro / Nice to Have)
- Modo `--dry-run` para previsualizar cambios sin ejecutar
- Archivo de configuración externo para mapeos personalizados
- Flag `--force` para sobrescribir archivos existentes

### Fuera del Alcance
- Transformación inversa (destino → origen)
- Validación semántica del contenido de comandos
- Integración con CI/CD
- Interfaz gráfica

## Métricas de Éxito

### Métricas Técnicas
- **Exit code:** 0 en ejecución exitosa
- **Archivos procesados:** 9/9 transformados
- **Referencias actualizadas:** 9/9 patrones reemplazados
- **Tiempo ejecución:** < 5 segundos

### Métricas de Usuario
- **Reducción tiempo migración:** De 15-30 min a < 10 segundos (incluyendo verificación)
- **Errores de consistencia:** 0 post-transformación

## Restricciones y Supuestos

### Restricciones de Negocio
- El script debe ser un único archivo `.sh` sin dependencias
- Ubicación fija: `template/.specify/scripts/bash/raise/`

### Restricciones Técnicas
- Requiere bash 4.0+ (para arrays asociativos)
- Compatible con Git Bash en Windows (MINGW64)
- No usar herramientas externas (solo `sed`, `mkdir`, `cp`)

### Supuestos
- Los archivos origen siguen convención `speckit.*.md`
- El frontmatter YAML usa `agent:` para referencias
- Las subcarpetas destino pueden no existir inicialmente
- El usuario tiene permisos de escritura en carpeta destino

## Componentes de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    transform-commands.sh                     │
├─────────────────────────────────────────────────────────────┤
│  1. CONFIGURACIÓN                                            │
│     - Array FILE_MAP: origen → destino                       │
│     - Array REF_MAP: referencia_antigua → referencia_nueva   │
│     - Variables: SRC_DIR, DEST_DIR                           │
├─────────────────────────────────────────────────────────────┤
│  2. VALIDACIÓN                                               │
│     - Verificar existencia carpeta origen                    │
│     - Verificar permisos escritura destino                   │
├─────────────────────────────────────────────────────────────┤
│  3. TRANSFORMACIÓN                                           │
│     - Crear subcarpetas destino (mkdir -p)                   │
│     - Para cada archivo en FILE_MAP:                         │
│       - Leer contenido                                       │
│       - Aplicar REF_MAP con sed                              │
│       - Escribir a destino con nuevo nombre                  │
├─────────────────────────────────────────────────────────────┤
│  4. REPORTE                                                  │
│     - Conteo archivos procesados                             │
│     - Lista de errores (si los hay)                          │
│     - Exit code: 0 éxito, 1 error                            │
└─────────────────────────────────────────────────────────────┘
```

**Componentes (4 total):**
1. **Configuración** - Mapeos y variables
2. **Validación** - Pre-checks
3. **Transformación** - Lógica principal
4. **Reporte** - Output y exit code

## Stakeholders

### Tomadores de Decisiones Clave
- **Orquestador:** Define requisitos y valida resultado final

### Equipo Central
- **Desarrollador:** Implementa y prueba el script

---

## Historial del Documento

| Versión | Fecha      | Autor(es)   | Cambios Realizados |
|---------|------------|-------------|--------------------|
| 1.0     | 2026-01-20 | Orquestador | Versión inicial basada en PRD-RAISE-001 |
