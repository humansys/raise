# ADR-010 Impact Analysis
## Documentos que Requieren Actualización

**Fecha:** 2025-12-29  
**ADR:** ADR-010 - Ontología de Comandos CLI  
**Cambios:** `hydrate` → `pull`, `validate` → `kata`

---

## Resumen de Impacto

| Documento | Menciones `hydrate` | Menciones `validate` | Prioridad | Estado |
|-----------|:-------------------:|:--------------------:|:---------:|:------:|
| 23-commands-reference-v2.md | 7 | 6 | 🔴 P0 | ✅ Completado |
| 10-system-architecture-v2.md | 5 | 1 | 🔴 P0 | ⬜ Pendiente |
| 30-roadmap-v2.md | 3 | 0 | 🟡 P1 | ✅ Completado |
| 11-data-architecture-v2.md | 3 | 0 | 🟡 P1 | ✅ Completado |
| 24-examples-library-v2.md | 2 | 0 | 🟡 P1 | ✅ Completado |
| 15-tech-stack-v2.md | 2 | 0 | 🟡 P1 | ✅ Completado |
| 01-product-vision-v2.md | 2 | 0 | 🟢 P2 | ⬜ Pendiente |
| 12-integration-patterns-v2.md | 0 | 1 | 🟢 P2 | ⬜ Pendiente |
| 13-security-compliance-v2.md | 1 | 0 | 🟢 P2 | ⬜ Pendiente |
| 20-glossary-v2.md | 1 | 0 | 🟢 P2 | ⬜ Pendiente |
| 14-adr-index-v2.md | 1 | 0 | ⚪ N/A | Reemplazado por raise-adr/ |

**Progreso:** 5/10 documentos completados (50%)

---

## Detalle por Documento

### 🔴 P0 - Críticos (Actualizar Inmediatamente)

#### 23-commands-reference-v2.md
**Impacto:** ALTO - Es la referencia principal de comandos

| Sección | Cambio Requerido |
|---------|------------------|
| Tabla de comandos core | `raise hydrate` → `raise pull` |
| Sección `raise hydrate` | Renombrar a `raise pull`, actualizar descripción |
| Flag `--skip-hydrate` | Renombrar a `--skip-pull` |
| Flag `--guardrails-only` | Mantener (aplica a `pull`) |
| Sección `raise validate` | Renombrar a `raise kata`, reescribir como proceso |
| Ejemplos CI/CD | Actualizar comandos |
| Pre-commit hooks | Actualizar comandos |

**Acción:** Reescribir completamente este documento con nueva ontología.

---

#### 10-system-architecture-v2.md
**Impacto:** MEDIO - Diagramas de flujo y descripción de CLI

| Sección | Cambio Requerido |
|---------|------------------|
| Diagrama "Flujo 2: Sincronización" | `raise hydrate` → `raise pull` |
| Tabla de comandos raise-kit | Actualizar lista |
| Descripción de flujos | Actualizar menciones |

**Acción:** Buscar/reemplazar + verificar diagramas Mermaid.

---

### 🟡 P1 - Importantes (Actualizar Esta Sesión)

#### 30-roadmap-v2.md
| Línea | Cambio |
|-------|--------|
| Backlog P0 | `raise hydrate` → `raise pull` |
| v0.1.0 checklist | Actualizar comando |

---

#### 11-data-architecture-v2.md
| Línea | Cambio |
|-------|--------|
| Flujo de transformación | `raise hydrate` → `raise pull` |
| Migración scripts | Actualizar referencias |

---

#### 24-examples-library-v2.md
| Línea | Cambio |
|-------|--------|
| Ejemplos de uso | `raise hydrate` → `raise pull` |

---

#### 15-tech-stack-v2.md
| Línea | Cambio |
|-------|--------|
| CLI commands list | Actualizar |

---

### 🟢 P2 - Menores (Pueden Esperar)

#### 01-product-vision-v2.md
- 2 menciones de `hydrate` en contexto de features

#### 12-integration-patterns-v2.md
- 1 mención de `validate` en patrón de integración

#### 13-security-compliance-v2.md
- 1 mención de `hydrate` en flujo de seguridad

#### 20-glossary-v2.md
- Añadir entrada para `raise pull`
- Añadir entrada para `raise kata`
- Marcar `hydrate` como deprecated

---

## Cambios Específicos

### Tabla de Reemplazo Global

| Buscar | Reemplazar por |
|--------|----------------|
| `raise hydrate` | `raise pull` |
| `raise validate` | `raise kata` |
| `--skip-hydrate` | `--skip-pull` |
| `hydrate command` | `pull command` |
| `hydrate guardrails` | `pull Golden Data` |

### Nuevas Secciones Requeridas

En **23-commands-reference-v2.md**:
- Añadir sección "Contextos de Uso: Desarrollo vs CI/CD"
- Añadir tabla de clasificación de comandos
- Añadir sección `raise kata` completa con aliases

En **20-glossary-v2.md**:
- Entrada: `pull` (comando)
- Entrada: `kata` (comando vs concepto)
- Deprecar: `hydrate`

---

## Plan de Ejecución

### Fase 1: Sesión 2025-12-29 ✅ COMPLETADA
1. ✅ Crear ADR-010
2. ✅ Crear 23-commands-reference-v2.1.md (reescritura completa)
3. ⬜ Actualizar 10-system-architecture (pendiente - encoding issues)
4. ✅ Actualizar 30-roadmap-v2.1.md
5. ✅ Actualizar 24-examples-library-v2.1.md
6. ✅ Actualizar 15-tech-stack-v2.1.md
7. ✅ Actualizar 11-data-architecture-v2.1.md

### Fase 2: Siguiente Sesión
1. ⬜ Actualizar 10-system-architecture-v2.md
2. ⬜ Actualizar documentos P2 (vision, integration, security, glossary)
3. ⬜ Validación de coherencia inter-documentos

---

## Verificación Post-Actualización

```bash
# Verificar que no queden menciones legacy
grep -r "raise hydrate" *.md
grep -r "raise validate" *.md  # Excepto donde sea concepto, no comando
grep -r "skip-hydrate" *.md
```

---

*Este documento guía la migración de ADR-010. Actualizar conforme se completen cambios.*
