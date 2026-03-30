---
title: Knowledge Graph
description: El grafo de contexto unificado que conecta memoria, gobernanza, skills y trabajo en una estructura consultable.
---

El Knowledge Graph es la columna vertebral del sistema de contexto de RaiSE. Fusiona todo — patrones de memoria, documentos de gobernanza, metadatos de skills, seguimiento de trabajo y componentes descubiertos — en un solo grafo de conceptos conectados.

## Qué Es

Un grafo dirigido donde:
- **Nodos** son conceptos — patrones, principios, requisitos, skills, stories, componentes, módulos
- **Edges** son relaciones — "aprendido de", "gobernado por", "depende de", "restringido por"

Cuando ejecutas `rai graph build`, el CLI recorre todas las fuentes del proyecto y ensambla este grafo. Cuando consultas con `rai graph query` o `rai graph context`, estás buscando en este grafo.

## Tipos de Nodos

| Tipo | Patrón de ID | Fuente | Ejemplo |
|------|-------------|--------|---------|
| Pattern | `PAT-*`, `BASE-*` | Archivos JSONL de memoria | "Usar fixtures para tests de BD" |
| Calibration | `CAL-*` | Registros de calibración | Story S3.5: talla M, 45 min reales |
| Session | `SES-*` | Historial de sesiones | "Implementé módulo de auth" |
| Principle | `§N` | Constitución | "Heurísticas simples sobre ML complejo" |
| Requirement | `RF-*` | PRD | "Website de marketing con voz de artesano" |
| Guardrail | `GR-*` | Guardrails | "MUST: No vanity metrics como goals" |
| Skill | `/name` | Archivos SKILL.md | `/rai-story-plan` — descomponer en tareas |
| Story | `S*.*` | Seguimiento de trabajo | S8.6: Docs Getting Started |
| Epic | `E*` | Scope de epics | E8: Website v1 + Docs |
| Component | `comp-*` | Discovery scan | Clase `SessionManager` |
| Module | `mod-*` | Discovery analysis | `mod-memory` — subsistema de memoria |
| Decision | `ADR-*` | Decisiones de arquitectura | ADR-019: Grafo de contexto unificado |

## Tipos de Edges

Los edges expresan cómo se relacionan los conceptos:

| Edge | Significado | Ejemplo |
|------|-------------|---------|
| `learned_from` | El patrón vino de esta sesión | PAT-042 → SES-015 |
| `governed_by` | El requisito implementa un principio | RF-01 → §2 |
| `implements` | La story implementa un requisito | S8.6 → RF-05 |
| `part_of` | La story pertenece a un epic | S8.6 → E8 |
| `depends_on` | El módulo depende de otro | mod-session → mod-memory |
| `belongs_to` | El módulo pertenece a un dominio | mod-memory → bc-core |
| `constrained_by` | El dominio está restringido por un guardrail | bc-core → GR-015 |
| `applies_to` | El patrón aplica a un skill | PAT-001 → /rai-story-implement |

## Construir el Grafo

```bash
rai graph build
```

Esto fusiona todas las fuentes:
1. **Gobernanza**: principios, requisitos, guardrails de `governance/`
2. **Memoria**: patrones, calibración, sesiones de `.raise/rai/memory/`
3. **Trabajo**: scopes de epics y stories de `work/epics/`
4. **Skills**: metadatos de `.claude/skills/*/SKILL.md`
5. **Componentes**: código descubierto de `work/discovery/`

La salida es `.raise/rai/memory/index.json`.

## Consultar el Grafo

### Búsqueda por Palabras Clave

Encontrar conceptos por contenido:

```bash
rai graph query "testing patterns"
```

### Búsqueda por Concepto

Encontrar un concepto específico por ID:

```bash
rai graph query "PAT-001" --strategy concept_lookup
```

### Contexto de Módulo

Obtener el contexto arquitectónico completo de un módulo — su dominio, capa, restricciones y dependencias:

```bash
rai graph context mod-memory
```

Esto retorna:
- **Bounded context**: a qué dominio pertenece el módulo
- **Layer**: su posición en la arquitectura (leaf, domain, integration, orchestration)
- **Constraints**: guardrails aplicables (MUST y SHOULD)
- **Dependencies**: de qué depende y qué depende de él

### Validación

Verificar el grafo por problemas estructurales:

```bash
rai graph validate
```

Esto detecta ciclos en relaciones de dependencia, tipos de edge inválidos y referencias colgantes.

## Por Qué un Grafo

La estructura de grafo habilita **consultas contextuales** — no solo "buscar esta palabra clave" sino "muéstrame todo lo relacionado con este módulo, incluyendo las reglas que lo restringen y los patrones aprendidos al construirlo."

Cuando tu partner de IA ejecuta `rai session start --context`, el CLI ensambla un bundle de contexto recorriendo este grafo. El resultado es una vista comprimida de todo lo relevante a tu trabajo actual — no un dump de todos los archivos, sino una selección curada de los nodos más importantes y sus relaciones.
