---
title: Gobernanza
description: El sistema de reglas que mantiene la salida de la IA confiable — desde principios hasta requisitos y guardrails ejecutables.
---

La gobernanza es cómo RaiSE asegura que tu partner de IA no se desvíe. Es un sistema por capas: principios de alto nivel fluyen hacia requisitos concretos, que se convierten en guardrails ejecutables. La IA los carga al inicio de cada sesión y los sigue durante todo el trabajo.

## Las Tres Capas

### Constitución (Principios)

El nivel más alto — principios fundacionales que no cambian frecuentemente. Expresan *valores* y *filosofía*.

Ejemplos de principios:
- "Heurísticas simples sobre ML complejo"
- "Tests junto con la implementación, no después"
- "Honestidad sobre acuerdo"

La constitución vive en `governance/constitution.md` (o equivalente). Los principios reciben IDs como `§1`, `§2`, etc.

### PRD (Requisitos)

La capa intermedia — requisitos concretos derivados de los principios. Expresan *qué debe hacer el proyecto*.

Ejemplos de requisitos:
- `RF-01`: Website de marketing con voz de artesano
- `RF-02`: Estrategia de contenido con prueba de hipótesis
- `RF-05`: Flujo de onboarding desde descubrimiento hasta productividad

Los requisitos viven en `governance/prd.md` y enlazan hacia los principios que implementan.

### Guardrails (Ejecución)

La capa inferior — reglas específicas y verificables. Expresan *qué debes y no debes hacer*.

Los guardrails tienen dos niveles:

| Nivel | Significado | Ejemplo |
|-------|-------------|---------|
| **MUST** | No negociable. Una violación es un defecto. | "Cada pieza de contenido tiene una hipótesis documentada" |
| **SHOULD** | Recomendado. Se puede omitir con justificación. | "Headings y meta descriptions optimizados para SEO" |

Los guardrails viven en `governance/guardrails.md` y cada uno enlaza al requisito que ejecuta.

## Cómo Fluye la Gobernanza

```
Principios (§)     →  "Por qué hacemos las cosas así"
     ↓
Requisitos (RF)    →  "Qué necesitamos construir"
     ↓
Guardrails (GR)    →  "Qué reglas seguir"
     ↓
Código / Contenido →  "Lo que realmente producimos"
```

Cada capa es trazable a la superior. Cuando alguien pregunta "¿por qué tenemos este guardrail?" puedes trazar: guardrail → requisito → principio.

## Gobernanza en la Práctica

Cuando ejecutas `rai session start --context`, el bundle de contexto incluye primes de gobernanza — los guardrails activos relevantes a tu trabajo actual. Tu partner de IA los ve al inicio de cada sesión y los aplica durante todo el trabajo.

Por ejemplo, si estás trabajando en contenido, el bundle de contexto podría incluir:

```
# Governance Primes
- must-content-001: Every content piece has a documented hypothesis
- must-content-002: One core idea per content piece
- must-brand-001: Consistent craftsman voice — no hype, no buzzwords
```

La IA no necesita recordar estos — se cargan frescos cada sesión desde los archivos de gobernanza.

## Estructura del Proyecto

Después de `rai init`, tu directorio de gobernanza luce así:

```
governance/
├── constitution.md    # Principios (o vision.md)
├── prd.md             # Requisitos
├── guardrails.md      # Reglas ejecutables
├── backlog.md         # Ítems de trabajo
└── architecture/
    ├── system-context.md
    └── system-design.md
```

## Detección de Convenciones

Para proyectos existentes, `rai init --detect` analiza tu codebase y genera guardrails automáticamente:

```bash
rai init --detect
```

Esto escanea en busca de patrones como:
- Convenciones de código (naming, formato, imports)
- Patrones de testing (framework, estructura de directorios)
- Patrones de arquitectura (organización de módulos, dirección de dependencias)

Los guardrails generados son un punto de partida — revísalos y ajústalos para que coincidan con los estándares reales de tu equipo.

## Idea Clave

La gobernanza no se trata de control. Se trata de **consistencia**. Cuando tu partner de IA sigue las mismas reglas cada sesión, obtienes salida predecible. Cuando las reglas son explícitas y trazables, puedes evolucionarlas deliberadamente en vez de confiar en la suerte.
