# Guión de Demo — RaiSE en Vivo

> Ejecutar en la terminal de raise-commons. Cada sección es ~2-3 minutos.
> Total: ~15 minutos. Intercalar entre slides o al final del bloque "En Práctica".

---

## 1. "Esto es un proyecto real" (~2 min)

**Narración:** "Este es el repo donde construimos RaiSE — usando RaiSE. Dogfooding desde el día uno."

```bash
# Mostrar la versión
rai --version
```

```bash
# Mostrar la estructura del proyecto
ls .raise/
```

> **Decir:** "Todo proyecto RaiSE tiene este directorio `.raise/`. Aquí vive la memoria, la identidad del partner IA, y el estado de sesión."

```bash
# Mostrar gobernanza
ls governance/
```

> **Decir:** "Y un directorio `governance/` con las reglas de su proyecto. Constitución, PRD, guardrails, arquitectura. Su IA lee esto al inicio de cada sesión."

```bash
# Mostrar un guardrail real
head -20 governance/guardrails.md
```

> **Decir:** "Estas no son sugerencias. Son reglas ejecutables que la IA verifica antes de cada commit."

---

## 2. "Skills: Flujos Estructurados" (~2 min)

**Narración:** "En lugar de decirle 'haz algo', hay skills — flujos de trabajo con pasos verificables."

```bash
rai skill list
```

> **Decir:** "23 skills. Ciclo de sesión, ciclo de epic, ciclo de story, discovery para repos existentes, onboarding. Cada uno tiene pasos, verificaciones, y produce artefactos."

> **Señalar:** "Noten los grupos: Session, Epic, Story, Discovery, Onboarding, Utility. El miércoles van a usar los de Onboarding en sus repos."

---

## 3. "Memoria: 326 Patrones Aprendidos" (~3 min)

**Narración:** "Esto es lo que hace a RaiSE diferente. El sistema aprende."

```bash
# Cuántos patrones tenemos
wc -l .raise/rai/memory/patterns.jsonl
```

> **Decir:** "326 patrones acumulados en semanas de desarrollo. Cada retrospectiva alimenta esto."

```bash
# Consultar memoria
rai memory query "testing patterns"
```

> **Decir:** "Puedo preguntarle a la memoria sobre cualquier tema. Esto devuelve patrones, requisitos, stories — todo lo relevante, consultable por keyword."

```bash
# Consultar algo más específico
rai memory query "governance guardrails"
```

> **Decir:** "Cuando la IA empieza una sesión, carga automáticamente los patrones más relevantes para lo que está haciendo. No empieza de cero."

---

## 4. "El Knowledge Graph" (~2 min)

**Narración:** "Todo se conecta en un grafo unificado."

```bash
rai memory build
```

> **Decir:** "Un comando. Escanea gobernanza, código, patrones, calibración — y construye el índice."

> **Señalar el output:** "Noten: X nodos, Y relaciones. Esto es el mapa completo del proyecto."

```bash
rai memory viz
```

> **Decir:** "Y lo pueden visualizar." *(Se abre el browser con el grafo interactivo)*

> **En el browser:** Navegar el grafo. Mostrar cómo los módulos se conectan con guardrails, con requisitos, con patrones. "Este es el mapa que la IA usa para entender su proyecto."

---

## 5. "Una Sesión Real" (~3 min)

**Narración:** "Así empieza un día de trabajo con RaiSE."

```bash
rai session start --project . --context
```

> **Leer el output en voz alta, señalando:**
> - "Sabe quién soy"
> - "Sabe en qué sesión estamos — SES-194"
> - "Sabe qué hice ayer" *(señalar Last y Recent)*
> - "Carga las decisiones de la sesión anterior" *(señalar Narrative)*
> - "Y las reglas de gobernanza" *(señalar Governance Primes)*

> **Decir:** "~150 tokens. Esto es lo que recibe la IA cuando empiezo a trabajar. Contexto completo, comprimido, listo para usar."

---

## 6. "Lo Que Estamos Construyendo Ahora" (~2 min)

**Narración:** "Incluso esta presentación se construyó con RaiSE."

```bash
# Mostrar el epic actual
cat work/epics/raise-153-developer-enablement/scope.md | head -30
```

> **Decir:** "Este es el epic RAISE-153: Developer Enablement. 5 stories. 3 ya completadas hoy — el sitio de docs, la referencia CLI, y la guía de getting started."

```bash
# Mostrar las stories
ls work/epics/raise-153-developer-enablement/stories/
```

> **Decir:** "Cada story tiene scope, plan, retrospectiva. Artefactos que alimentan la memoria."

```bash
# Mostrar una retrospectiva real
head -25 work/epics/raise-153-developer-enablement/stories/s2-retrospective.md
```

> **Decir:** "Esta retrospectiva de hace 30 minutos generó PAT-T-005 — aprendimos que la documentación pública no debe incluir comandos internos. Ese patrón ya está en memoria. La próxima vez que alguien documente el CLI, la IA lo sabe."

---

## 7. Cierre del Demo

> **Decir:** "Lo que acaban de ver no es un demo preparado. Es el estado real del repo donde construimos el framework. Cada sesión, cada story, cada patrón — todo trazable, todo acumulando."

> **Transición a homework:** "Mañana, esto va a ser *su* repo."

---

## Notas para el Presentador

- **Si algo falla:** Es un repo real, no un demo sanitizado. Si algo falla, es una oportunidad para mostrar cómo se maneja — Jidoka en acción.
- **Ritmo:** No leer los comandos. Escribirlos en vivo (o tenerlos en clipboard). La magia es que funciona en vivo.
- **Grafo:** El viz del knowledge graph es el momento "wow". Darle tiempo. Dejar que lo exploren visualmente.
- **Preguntas:** Si preguntan por su stack específico — "RaiSE es agnostico al lenguaje. Funciona donde funciona Git. El miércoles lo configuramos en su repo."
