---
id: "ADR-016"
title: "Architecture Reconstruction como práctica de discovery"
date: "2026-04-01"
status: "Accepted"
---

# ADR-016: Architecture Reconstruction como práctica de discovery

## Contexto

RaiSE necesita entender repos externos (Claude Code, dependencias, competidores) de forma sistemática para tomar decisiones de diseño informadas. Hasta ahora esto se hacía ad-hoc: leer archivos sueltos, grep por patrones, intuición. La filtración del source code de Claude Code (512K LOC) es la primera oportunidad de hacer esto a escala, y expone la necesidad de un método reproducible.

La práctica de Software Architecture Reconstruction (SAR) del SEI/CMU establece un marco formal, pero es pesado para nuestro contexto. Necesitamos una versión lean que se integre con las herramientas que ya tenemos (rai-discover, graph, skills).

## Decisión

Adoptar un método de Architecture Reconstruction en 4 fases como práctica formal de RaiSE, aplicable a cualquier codebase externo o heredado:

### Fase 1: Reconnaissance (barrido amplio, timeboxed)

Objetivo: producir un **mapa arquitectónico** — catálogo de módulos, dependencias, entry points, patrones dominantes.

Técnicas:
- Análisis estructural: árbol de directorios, tamaños, conteos
- Análisis de dependencias: imports/exports entre módulos
- Análisis de superficie: interfaces públicas, types exportados, schemas
- Señales de complejidad: archivos grandes, TODOs, feature flags, code smells

Salida: Module Catalog + Dependency Map + lista de Áreas de Interés priorizadas.

### Fase 2: Hypothesis Formation

Objetivo: convertir observaciones de reconnaissance en **preguntas concretas** con impacto en nuestro diseño.

Formato por hipótesis:
- Pregunta: "¿Cómo implementa X el sistema Y?"
- Relevancia para RaiSE: "Porque nosotros dependemos de / extendemos / competimos con Y"
- Archivos candidatos: [lista de archivos a investigar]

Salida: lista priorizada de hipótesis agrupadas en waves por valor de negocio.

### Fase 3: Targeted Deep Dives (por waves)

Objetivo: investigar cada hipótesis, producir **hallazgos documentados**.

Formato por hallazgo:
- Pregunta original
- Lo que encontramos (con referencias a archivos/líneas)
- Implicaciones para RaiSE (accionable: validar, corregir, adoptar, diferir)
- Confianza (Alta/Media/Baja) y limitaciones

Waves se priorizan por impacto de negocio. Cada wave es independiente.

### Fase 4: Synthesis

Objetivo: consolidar hallazgos en **decisiones y backlog items**.

- Hallazgos → backlog items en Jira (stories, bugs, improvements)
- Patrones descubiertos → candidates para adopción en RaiSE
- Asunciones corregidas → actualizar docs de arquitectura
- Meta-proceso → refinar este mismo ADR y alimentar rai-discover

## Consecuencias

| Tipo | Impacto |
|------|---------|
| Positivo | Método reproducible para entender cualquier codebase externo |
| Positivo | Decisiones de diseño informadas por evidencia, no intuición |
| Positivo | Alimenta rai-discover con un caso real de 512K LOC |
| Positivo | Hallazgos trazables a backlog items accionables |
| Negativo | Overhead de documentación por hallazgo (mitigado: formato lean) |
| Negativo | Hallazgos son snapshots — el código fuente evoluciona (mitigado: documentar versión, enfocarse en patrones estables) |

## Alternativas Consideradas

| Alternativa | Razon de Rechazo |
|-------------|------------------|
| Ad-hoc exploration | No reproducible, no trazable, se dispersa |
| SAR completo (SEI/CMU) | Demasiado pesado para nuestro contexto lean |
| Solo leer README/docs | Claude Code no tiene docs de arquitectura pública |
| Ignorar el leak | Oportunidad unica de entender nuestro runtime — inaceptable no aprovecharla |

---

<details>
<summary><strong>Referencias</strong></summary>

- SEI/CMU Software Architecture Reconstruction: https://insights.sei.cmu.edu/library/software-architecture-reconstruction/
- Epic: RAISE-1162 (E1132)
- Fuente: Claude Code source leak 2026-03-31 via npm source map

</details>
