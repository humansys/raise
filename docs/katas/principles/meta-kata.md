---
id: principios-00-meta-kata
nivel: principios
titulo: "Meta-Kata: Qué es una Kata y Cómo Usarla"
audience: beginner
template_asociado: null
validation_gate: null
prerequisites: []
tags: [meta, filosofia, onboarding, shuhari]
version: 1.0.0
---

# Meta-Kata: Qué es una Kata y Cómo Usarla

## Propósito

Establecer la comprensión fundamental de qué es una Kata en RaiSE, por qué existen, y cómo usarlas efectivamente. Esta kata responde a las preguntas fundamentales del nivel principios: **¿Por qué?** y **¿Cuándo?**

## ¿Qué es una Kata?

Una **Kata** es un proceso estructurado que hace visible la desviación del estándar, habilitando el ciclo Jidoka.

> La Kata no es documentación pasiva—es un **sensor** que detecta cuándo algo no va bien, permitiendo al Orquestador parar, corregir y continuar.

### Origen del Término

El término "Kata" (型) viene de las artes marciales japonesas, donde significa "forma" o "patrón". En artes marciales, las katas son secuencias de movimientos que se practican repetidamente hasta que se internalizan.

En RaiSE, adoptamos este concepto: las katas son secuencias de pasos que codifican las mejores prácticas, permitiendo:
- **Práctica deliberada**: Mejorar a través de repetición estructurada
- **Detección de anomalías**: Ver cuándo algo se desvía del patrón esperado
- **Transferencia de conocimiento**: Capturar experiencia en forma reproducible

---

## Los Cuatro Niveles de Kata

| Nivel | Pregunta Guía | Propósito | Ejemplo |
|-------|---------------|-----------|---------|
| **Principios** | ¿Por qué? ¿Cuándo? | Filosofía y meta-proceso | Esta kata |
| **Flujo** | ¿Cómo fluye? | Secuencias de valor por fase | Discovery, Planning |
| **Patrón** | ¿Qué forma? | Estructuras reutilizables | Code Analysis |
| **Técnica** | ¿Cómo hacer? | Instrucciones específicas | API Design |

**Verificación:** Antes de usar una kata, identificar su nivel y confirmar que responde a la pregunta que tienes.

> **Si no puedes continuar:** Kata no responde tu pregunta → Buscar en el nivel correcto. Si necesitas "cómo", busca en flujo. Si necesitas "qué estructura", busca en patrón.

---

## El Modelo Híbrido

RaiSE usa un modelo de tres capas:

```
┌─────────────────────────────────────────────────────────────┐
│   TEMPLATE              KATA                VALIDATION GATE │
│   ─────────            ─────               ──────────────── │
│   ¿QUÉ produce?        ¿CÓMO hacerlo?      ¿ESTÁ BIEN?      │
└─────────────────────────────────────────────────────────────┘
```

- **Template**: Estructura del artefacto que produces (personalizable por proyecto)
- **Kata**: Proceso para crear ese artefacto (genérico del framework)
- **Validation Gate**: Checklist que verifica la calidad (componible)

**Verificación:** Identificar los tres componentes antes de comenzar cualquier tarea de documentación o diseño.

> **Si no puedes continuar:** No encuentras el template → La kata indica qué template usar. Si no hay template, el output es ad-hoc.

---

## Jidoka Inline: El Patrón de Cada Paso

Cada paso de una kata incluye verificación y guía de corrección:

```markdown
### Paso N: [Acción]

[Instrucciones del paso]

**Verificación:** [Cómo saber si funcionó]

> **Si no puedes continuar:** [Causa] → [Resolución]
```

Este patrón implementa **Jidoka** (自働化): automatización con toque humano.

**El ciclo Jidoka:**
1. **Detectar**: La verificación identifica el problema
2. **Parar**: No continuar al siguiente paso
3. **Corregir**: Seguir la resolución sugerida
4. **Continuar**: Retomar el flujo

**Verificación:** Entiendes el patrón Jidoka inline y puedes identificarlo en cualquier kata.

> **Si no puedes continuar:** Concepto no claro → Leer un ejemplo en `flujo-01-discovery.md` y observar el patrón en cada paso.

---

## ShuHaRi: Tu Relación con las Katas

ShuHaRi (守破離) describe cómo evoluciona tu relación con las katas:

| Fase | Kanji | Significado | Cómo Usas las Katas |
|------|-------|-------------|---------------------|
| **Shu** | 守 | Proteger | Sigues cada paso exactamente |
| **Ha** | 破 | Romper | Adaptas pasos al contexto |
| **Ri** | 離 | Trascender | Creas variantes o nuevas katas |

**Importante:** ShuHaRi describe TU nivel de maestría, no el de la kata. La misma kata sirve a usuarios en cualquier fase.

- **Si eres nuevo**: Sigue los pasos al pie de la letra (Shu)
- **Si tienes experiencia**: Adapta según contexto, pero mantén la esencia (Ha)
- **Si eres experto**: Crea tus propias katas basadas en aprendizajes (Ri)

**Verificación:** Puedes identificar en qué fase ShuHaRi estás para una kata particular.

> **Si no puedes continuar:** No sabes tu nivel → Si tienes que pensar "¿qué sigue?", estás en Shu. Si piensas "esto no aplica aquí", estás en Ha.

---

## Cuándo Usar una Kata

### Usa una Kata Cuando:
- Inicias una fase de la metodología (Discovery, Design, etc.)
- Necesitas un proceso reproducible
- Quieres asegurar calidad consistente
- Estás transfiriendo conocimiento a otros

### NO Uses una Kata Cuando:
- La tarea es trivial (<30 min)
- Ya dominas el proceso (Ri) y no necesitas la guía
- El contexto es tan único que ninguna kata aplica

**Verificación:** Antes de comenzar trabajo significativo, preguntarte: "¿Hay una kata para esto?"

> **Si no puedes continuar:** No estás seguro si usar kata → Si el trabajo toma >2 horas o involucra múltiples pasos, probablemente hay una kata.

---

## La Regla Fundamental

> ⚠️ **Las katas no se ejecutan directamente.**
>
> Siempre crear un Plan de Implementación específico para TU contexto usando `flujo-04-implementation-plan`.

La kata es el **patrón**. El plan es la **instancia**.

- Kata: "Así se hace un Tech Design en general"
- Plan: "Así haremos el Tech Design para el proyecto X"

**Verificación:** Entiendes la diferencia entre kata (genérica) y plan (específico).

> **Si no puedes continuar:** Confusión kata vs plan → La kata es la receta del libro de cocina. El plan es la lista de compras para TU cena esta noche.

---

## Cómo Navegar las Katas

### Por Fase de Metodología
```
Fase 1: Discovery     → flujo-01-discovery
Fase 2: Vision        → flujo-02-solution-vision
Fase 3: Tech Design   → flujo-03-tech-design
Fase 4: Backlog       → flujo-05-backlog-creation
Fase 5: Planning      → flujo-04-implementation-plan
Fase 6: Development   → flujo-06-development
```

### Por Contexto
```
Brownfield (código existente):
  → patron-01-code-analysis
  → patron-02-ecosystem-discovery

Antes de cualquier implementación:
  → flujo-04-implementation-plan
```

**Verificación:** Puedes identificar qué kata usar dado un contexto de trabajo.

> **Si no puedes continuar:** No encuentras la kata correcta → Revisar el índice de katas o preguntar: "¿Qué fase de la metodología es esto?"

---

## Output de Esta Kata

Al completar esta kata, el Orquestador:
- Entiende qué es una kata y por qué existen
- Conoce los cuatro niveles semánticos
- Comprende el modelo híbrido (Template-Kata-Gate)
- Puede identificar el patrón Jidoka inline
- Sabe cuándo usar y cuándo no usar una kata
- Puede navegar el sistema de katas

---

## Referencias

- Glosario: [`20-glossary-v2.1.md`](../../../docs/framework/v2.1/model/20-glossary-v2.1.md) — Definiciones canónicas
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) — Flujo completo
- ADR-009: [`adr-009-shuhari-hybrid.md`](../../../docs/framework/v2.1/adrs/adr-009-shuhari-hybrid.md) — Decisión ShuHaRi
- ADR-011: [`adr-011-hybrid-kata-template-gate.md`](../../../docs/framework/v2.1/adrs/adr-011-hybrid-kata-template-gate.md) — Modelo Híbrido
