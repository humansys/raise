# Knowledge Cartridges — Oportunidad de Producto

**Para:** Gerardo (Ventas/BD), Eduardo (Marketing/Redes)
**De:** Emilio + Rai
**Fecha:** 2026-03-24
**Versión:** Draft para discusión interna

---

## El problema que resolvemos

Las empresas quieren usar IA (ChatGPT, Claude, agentes) para tomar mejores decisiones. Pero hay un problema fundamental: **la IA sabe mucho en general, pero no sabe nada de TU negocio**.

Un CEO que usa ChatGPT para preguntar sobre Scaling Up recibe respuestas genéricas de internet. No sabe qué decisiones tomó su equipo, qué herramientas aplican a su situación, ni cómo se conectan los conceptos de la metodología con su operación real.

**El conocimiento genérico no es confiable para decisiones de negocio.** Y el conocimiento específico de dominio no está disponible para la IA — vive en libros, en la cabeza de los expertos, en documentos dispersos.

---

## Nuestra solución: Knowledge Cartridges

Imaginen un **cartucho de conocimiento** — como un cartucho de videojuego, pero de expertise.

Un Knowledge Cartridge es un módulo que le enseña a un agente de IA todo sobre un dominio específico. No de forma genérica (como leer Wikipedia), sino de forma **estructurada, validada y confiable**:

- **Qué conceptos existen** y cómo se relacionan (ontología)
- **De dónde viene** cada pieza de conocimiento (trazabilidad)
- **Cómo buscar** respuestas dentro del dominio (no adivinando, sino navegando la estructura)
- **Cómo validar** que el conocimiento está completo y es correcto (gates de calidad)
- **Cómo mejorarlo** con feedback del experto humano (curación)

### Ejemplo concreto: Scaling Up

Eduardo ya trabajó en esto con nosotros. Tomamos el libro de Scaling Up + las metodologías de los cursos, y el agente:

1. **Extrajo** 447 conceptos estructurados: decisiones, herramientas, métricas, worksheets
2. **Organizó** las relaciones entre ellos (qué herramienta mide qué métrica, qué decisión afecta qué área)
3. **Validó** contra 23 preguntas de competencia ("¿El conocimiento cubre los 4 pilares?")
4. **Eduardo revisó** los conceptos uno por uno en una interfaz conversacional

El resultado: un agente que puede responder "¿cómo mejorar mi retención de talento según Scaling Up?" con respuestas **específicas, trazables al libro, y conectadas** — no genéricas.

---

## Por qué es diferente a lo que existe

Hicimos un análisis de 12 competidores directos y 11 plataformas de grafos de conocimiento. Nadie ofrece esto:

| Lo que otros hacen | Lo que nosotros hacemos |
| --- | --- |
| Memoria de conversaciones (Mem0, Letta) — recuerdan lo que dijiste | Conocimiento de dominio curado — saben lo que el experto sabe |
| Extracción automática sin validación (Cognee, Interloom) | Extracción + validación + curación humana |
| Grafos de conocimiento genéricos (Neo4j, Diffbot) | Módulos de dominio específicos, portables, instalables |
| Búsqueda por similitud de texto (RAG vectorial) | Navegación estructurada del conocimiento (3.4x más preciso en queries complejas) |

### La metáfora: "npm para conocimiento de dominio"

Así como los desarrolladores instalan paquetes de código (`npm install react`), las empresas podrían instalar cartuchos de conocimiento en sus agentes:

```
rai cartridge install scaling-up
rai cartridge install gtd-productivity
rai cartridge install okr-methodology
```

Y el agente inmediatamente sabe sobre ese dominio — con la calidad que un experto humano validó.

---

## Oportunidad de mercado

### Los números

- El mercado de **grafos de conocimiento para IA agéntica** vale **$1.73B hoy** y crecerá a **$4.93B en 2030** (23% anual)
- El mercado de **agentes de IA** vale **$7.84B hoy** → **$52.62B en 2030** (46% anual)
- Se invirtieron **$60M+ en los últimos 18 meses** específicamente en "memoria/conocimiento para agentes IA" — era $0 antes de 2024
- La adopción de grafos de conocimiento está **estancada en 27%** — el cuello de botella es **construir los modelos de dominio**. Eso es exactamente lo que resolvemos.

### Quién ya monetiza ontologías (y cómo)

La ontología sola no es el producto — el valor está en la **capa de enriquecimiento**:

| Vertical | Empresa | Modelo | Revenue |
| --- | --- | --- | --- |
| HR / Skills | Lightcast | Base abierta (ESCO/O*NET) + datos propietarios | $105M |
| ESG / Sustentabilidad | MSCI | Taxonomía + ratings | $344M run rate |
| Salud | Wolters Kluwer | Conocimiento médico estructurado | €1.58B |
| Legal | Westlaw/LexisNexis | Ontología legal + case law | Multi-billion |

**El patrón es claro:** base abierta + enrichment propietario + expertise de dominio = producto monetizable.

---

## Oportunidad en LATAM

### Por qué LATAM primero

1. **Mercado desatendido** — los competidores (Mem0, Cognee, Zep) están enfocados en US/EU. No hay player local.
2. **Consultoría como canal** — LATAM tiene un ecosistema fuerte de consultoras que implementan metodologías (Scaling Up, EOS, OKRs, Lean). Cada una es un cartridge potencial.
3. **El experto humano es el diferenciador** — en LATAM, las relaciones con coaches y consultores certificados son el canal de distribución. Nuestro modelo HITL (humano-en-el-loop) convierte al consultor en co-creador del producto.
4. **Costo de creación de cartridges es menor** — el expertise para crear ontologías de dominio es más accesible en LATAM que en Silicon Valley.

### Modelo de negocio propuesto

```
┌─────────────────────────────────────────────┐
│           KNOWLEDGE CARTRIDGES              │
│                                             │
│  Producto Open Core:                        │
│  ├── Motor de cartridges (OSS, gratuito)    │
│  ├── CLI + SDK para crear cartridges        │
│  └── Cartridge de ejemplo (ScaleUp)         │
│                                             │
│  Revenue streams:                           │
│  ├── 1. Cartridges premium (por dominio)    │
│  ├── 2. "Cartridge Studio" (SaaS)           │
│  │      Tool para crear/curar cartridges    │
│  ├── 3. Marketplace de cartridges           │
│  │      Expertos venden, nosotros cobramos  │
│  └── 4. Enterprise: cartridges privados     │
│         Ontologías internas de la empresa   │
└─────────────────────────────────────────────┘
```

### Primeros cartridges objetivo

| Cartridge | Mercado objetivo | Partner potencial |
| --- | --- | --- |
| Scaling Up | CEOs, coaches certificados | Gazelles International LATAM |
| OKRs | Startups, scale-ups | Comunidad OKR LATAM |
| Lean Startup | Emprendedores, aceleradoras | Techstars, 500 Global LATAM |
| ISO 9001/27001 | PyMEs en proceso de certificación | Consultoras de calidad |
| Marco Legal MX | Abogados, compliance | Despachos legales |
| NOM-035 | RRHH, salud ocupacional | Consultoras de RRHH |

---

## Qué necesitamos de cada uno

### Gerardo (Ventas/BD)

1. **Validar la propuesta de valor** con 3-5 consultores/coaches que usen metodologías estructuradas. ¿Pagarían por un agente que domine su metodología? ¿Cuánto?
2. **Identificar early adopters** — consultoras que ya tengan contenido estructurado (libros, frameworks, talleres) y quieran "digitalizarlo" como cartridge.
3. **Explorar el modelo marketplace** — ¿los consultores certificados venderían cartridges de sus metodologías? ¿Qué split esperarían?

### Eduardo (Marketing/Redes)

1. **Posicionar el concepto** — "Knowledge Cartridges" necesita un mensaje claro para audiencia no-técnica. Algo como: "Dale a tu IA el conocimiento de un experto, no de Wikipedia."
2. **Content strategy** — demos visuales del ScaleUp cartridge en acción. Antes/después: pregunta a ChatGPT genérico vs. pregunta a agente con cartridge.
3. **Comunidad** — identificar en redes dónde están los consultores y coaches que podrían ser creadores de cartridges. LinkedIn es el canal natural.

---

## Estado actual

- **El motor funciona** — ya lo probamos con ScaleUp (447 conceptos extraídos y validados)
- **La investigación nos respalda** — 90+ fuentes académicas y de mercado confirman que el concepto es novel y el mercado existe
- **Estamos en ventana** — los competidores más cercanos (Cognee, Zep) no tienen HITL ni packaging. Si se mueven, tendremos ~6-12 meses de ventaja
- **Próximo paso técnico:** refactorizar el motor para que sea framework-level (no atado a rai-agent), lo que permite que cualquier agente lo use

---

## En una frase

> **Convertimos el conocimiento de expertos en módulos instalables para agentes de IA — validados, estructurados y confiables.**

---

*Este documento es interno y confidencial. Basado en literature review de 90+ fuentes académicas y análisis de mercado de 30+ empresas. Material de soporte completo disponible para revisión.*
