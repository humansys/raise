# Gobernanza Determinista para Código Generado por IA
## Oportunidad de Investigación — Maestría en Ciencias y Tecnologías de la Información
### UAM Iztapalapa · Marzo 2026

---

# ¿Quién soy?

- **Emilio Osorio** — Fundador de HumanSys, 25+ años en ingeniería de software
- Creador de **RaiSE** (Rai Software Engineering), un framework open source de gobernanza para desarrollo asistido por IA
- Colaborador externo del **Dr. Humberto Cervantes** en esta línea de investigación
- raiseframework.ai

---

# El Boom de la IA en Desarrollo de Software

Los agentes de IA para código ya son mainstream:

- **GitHub Copilot** — 1.8M+ desarrolladores de pago
- **Cursor** — IDE completo con IA integrada
- **Claude Code** — agente autónomo de Anthropic

La promesa: **"Escribe código 55% más rápido"** (Peng et al., 2023)

---

# Pero... ¿a qué costo?

Los datos cuentan otra historia:

- **40%** del código de Copilot contiene vulnerabilidades de seguridad (Pearce et al., 2022)
- **62-69%** de tasa de mal uso de APIs con GPT-3.5/4 (AAAI 2024)
- **<14%** de código seguro sin prompting explícito (CodeSecEval, 2024)
- Desarrolladores **19% más lentos** con IA en tareas complejas — aunque *creen* ser más rápidos (METR, 2025)

---

# "Vibe Coding"

El anti-patrón dominante:

1. Le pides algo a la IA
2. Te genera código
3. Lo pegas en tu proyecto
4. "Funciona" ✓
5. No revisaste calidad, seguridad, ni arquitectura ✗

**Resultado:** código que pasa los tests superficiales pero acumula deuda técnica, vulnerabilidades y violaciones arquitectónicas invisibles.

---

# La Pregunta de Investigación

> ¿En qué medida la aplicación de gobernanza determinista reduce la tasa de defectos, vulnerabilidades y violaciones arquitectónicas en código generado por agentes de IA?

---

# Conexión Académica

Este proyecto extiende el trabajo del **Dr. Cervantes, Kazman y Cai (2025)**:

- Demostraron que dar al LLM una **descripción explícita del método ADD**, una **persona de arquitecto** y un **plan de iteración estructurado** produce artefactos de arquitectura alineados
- **Pregunta natural:** ¿puede este principio de gobernanza estructurada extenderse del diseño arquitectónico a la implementación de código?

---

# ¿Qué es Gobernanza Determinista?

Un conjunto de mecanismos que hacen que un agente de IA:

1. **Decida y actúe de la misma manera** ante la misma entrada y contexto
2. **Deje rastro verificable** de por qué actuó así
3. **Sea detenido** cuando viola las reglas del proyecto

Tres pilares: **Context Engineering · Validation Gates · Guardrails**

---

# Antes de la Demo: Marco Metodológico

Para entender RaiSE, necesitamos entender el proceso de desarrollo de software que gobierna.

---

# Desarrollo Lean de Software

Originado en el **Sistema de Producción Toyota**, adaptado al software por Mary y Tom Poppendieck (2003):

- **Eliminar desperdicio** — no producir lo que no se necesita
- **Amplificar el aprendizaje** — feedback rápido y continuo
- **Decidir lo más tarde posible** — con la mayor información
- **Entregar lo más rápido posible** — valor incremental
- **Construir calidad desde el inicio** — no inspeccionar al final

---

# Agile en 2 Minutos

Metodología que implementa principios Lean en software:

- **Trabajo iterativo:** ciclos cortos (1-4 semanas) en lugar de planes de meses
- **Épica:** objetivo grande de negocio (ej: "Sistema de pagos")
- **Historia de usuario:** unidad de trabajo entregable (ej: "Como usuario, quiero pagar con tarjeta")
- **Tarea:** paso atómico dentro de una historia (ej: "Implementar endpoint /pay")

```
Épica → Historias → Tareas → Código → Entrega
```

---

# TDD: Test-Driven Development

El código se escribe **después** del test, no antes:

```
1. RED    — Escribe un test que falla
2. GREEN  — Escribe el código mínimo para que pase
3. REFACTOR — Mejora el código sin romper el test
```

¿Por qué importa para IA? Porque el test se convierte en la **especificación verificable** de lo que el agente debe producir.

---

# Validation Gates (Compuertas)

Puntos de control automáticos que el código debe pasar antes de avanzar:

| Gate | Qué verifica |
|------|-------------|
| Tests | ¿El código hace lo que debe? |
| Type checking | ¿Los tipos son consistentes? |
| Linting | ¿El código cumple estándares? |
| Análisis estático | ¿Hay vulnerabilidades conocidas? |

Si un gate falla, el agente **no puede avanzar**. Sin excepciones.

---

# Ahora sí: RaiSE en Acción

**RaiSE** (Rai Software Engineering) operacionaliza estos conceptos como un framework de gobernanza para agentes de IA.

---

# ¿Qué es RaiSE?

Un framework open source que:

- **Estructura** el trabajo del agente en fases (diseño → plan → implementación → revisión)
- **Inyecta contexto** arquitectónico y de negocio en cada interacción con el LLM
- **Valida** cada paso con gates automáticos
- **Traza** cada decisión con artefactos verificables

No reemplaza al desarrollador — lo convierte en **supervisor informado** del agente.

---

# Ciclo de Vida RaiSE

```
ÉPICA:
  epic-start → epic-design → epic-plan → [historias] → epic-close

HISTORIA:
  story-start → story-design → story-plan → story-implement → story-review → story-close
```

Cada fase tiene:
- **Entradas** definidas (artefactos de la fase anterior)
- **Gates** de salida (validaciones automáticas)
- **Trazabilidad** (logs, commits, artefactos)

---

# Context Engineering en RaiSE

El agente no trabaja "en el vacío" — recibe contexto estructurado:

- **Grafo de conocimiento:** arquitectura, módulos, dependencias del proyecto
- **Patrones aprendidos:** decisiones previas que aplican al trabajo actual
- **Guardrails:** reglas que el agente no puede violar (ej: "siempre usar Pydantic para modelos de datos")
- **Historial de sesión:** qué se hizo antes, qué decisiones se tomaron

---

# Validation Gates en RaiSE

Antes de cada commit, el agente debe pasar:

1. **Tests** — TDD obligatorio (red-green-refactor)
2. **Type checking** — Pyright en modo estricto
3. **Linting** — Ruff con reglas del proyecto
4. **Análisis estático** — Semgrep para vulnerabilidades

Si un gate falla → el agente se detiene, diagnostica y corrige.

---

# Demo en Vivo: Una Historia Completa

Vamos a ejecutar una historia real paso a paso.

---

# 1. story-start

El agente crea la rama, el scope commit y registra el inicio en el tracker.

**Artefactos generados:**
- Rama `story/s{N}.{M}/{nombre}`
- Scope commit con contexto del trabajo

---

# 2. story-design

El agente analiza el problema y genera una especificación lean.

**Artefactos generados:**
- Documento de diseño con decisiones de integración
- Identificación de módulos afectados vía el grafo de conocimiento

---

# 3. story-plan

El agente descompone la historia en tareas atómicas con dependencias.

**Artefactos generados:**
- Plan de implementación con tareas ordenadas
- Cada tarea tiene criterio de aceptación verificable

---

# 4. story-implement

Aquí es donde pasa la magia — TDD obligatorio, gate por gate.

**Por cada tarea:**
1. Escribe el test (RED)
2. Escribe el código mínimo (GREEN)
3. Refactoriza (REFACTOR)
4. Pasa gates: tests + types + lint
5. Commit automático con trazabilidad

**Si un gate falla** → el agente se detiene, diagnostica y corrige. No puede avanzar.

---

# 5. story-review y story-close

El agente reflexiona sobre lo hecho, extrae patrones aprendidos y cierra.

**Artefactos generados:**
- Retrospectiva con decisiones y aprendizajes
- Patrones registrados para sesiones futuras
- Merge a rama de desarrollo + limpieza de rama

---

# La Oportunidad de Investigación

---

# Diseño Experimental

Estudio controlado A/B:

| | Grupo Control | Grupo Tratamiento |
|---|---|---|
| **Agente** | Claude/GPT directo | Mismo agente + RaiSE |
| **Contexto** | Prompt básico | Context engineering completo |
| **Validación** | Ninguna | Validation gates por fase |
| **Observable** | Logs de interacción | Trazas completas |

---

# Sub-preguntas de Investigación

- **RQ1.1:** ¿Cuál es el efecto de validation gates sobre la tasa de alucinaciones del LLM?
- **RQ1.2:** ¿Qué impacto tiene la inyección de contexto estructurado sobre las actividades de diseño?
- **RQ1.3:** ¿Existe una penalización significativa en tiempo al aplicar gobernanza determinista?

---

# Hipótesis

- **H1:** La gobernanza determinista reduce alucinaciones en al menos 50% (de ~10-15% a <5%)
- **H2:** La inyección de contexto arquitectónico eleva adherencia a patrones de ~60% a >90%
- **H3:** El overhead de tiempo no excede 20% respecto a desarrollo sin gobernanza

---

# Métricas

| Métrica | Qué mide | Target |
|---------|----------|--------|
| Tasa de alucinaciones | % de outputs con información fabricada | <5% |
| Adherencia a patrones | % de código que cumple guardrails | >90% |
| Tasa de re-prompting | Iteraciones para output aceptable | <2 |
| Defectos escapados | Bugs que pasan todos los gates | <10% |
| Tasa de rework | Código modificado en 14 días post-merge | <3% |

---

# ¿Qué haría el estudiante?

| Trimestre | Actividades | Entregable |
|-----------|-------------|------------|
| **T1** (Meses 1-3) | Revisión sistemática de literatura + diseño del protocolo | Marco teórico + protocolo |
| **T2** (Meses 4-6) | Implementar infraestructura de benchmark + piloto | Infraestructura funcional |
| **T3** (Meses 7-9) | Ejecutar experimento (40 sesiones) + análisis estadístico | Datos + análisis |
| **T4** (Meses 10-15) | Redacción de tesis + artículo para conferencia | Tesis + artículo enviado |

---

# Resultados Esperados

1. **Dataset público** de tareas de desarrollo con ground truth
2. **Evidencia cuantitativa** del efecto de gobernanza sobre calidad de código AI-generado
3. **Framework de evaluación** reproducible
4. **Artículo académico** en conferencia internacional
5. **Primer estudio controlado** que evalúa gobernanza determinista vs. desarrollo AI sin restricciones

---

# Perfil del Candidato

- Conocimientos de ingeniería de software (patrones, arquitectura, testing)
- Programación en Python (intermedio-avanzado)
- Familiaridad con herramientas de IA generativa
- Interés en métodos empíricos y análisis estadístico
- Redacción académica en español e inglés
- Deseable: análisis estático, DevOps/CI-CD

---

# ¿Por qué esta investigación importa?

- **Relevancia industrial:** toda la industria está adoptando IA sin gobernanza
- **Gap académico:** casi nadie está midiendo el efecto de la gobernanza — espacio para ser pioneros
- **Impacto real:** los resultados influirán en cómo se desarrolla software con IA
- **Open source:** contribución a un proyecto vivo, no a un prototipo de tesis

---

# ¿Qué gana el estudiante?

- **Tema de frontera** — AI-assisted software engineering es una de las áreas más activas
- **Acceso directo** al framework y al equipo que lo construye
- **Asesoría dual:** Dr. Cervantes (rigor académico) + Emilio Osorio (experiencia industrial)
- **Publicación:** objetivo concreto de artículo en conferencia internacional
- **Red profesional:** conexión con la comunidad de AI + software engineering

---

# Referencias

- Peng et al. (2023) — Impact of AI on Developer Productivity. Microsoft Research.
- Pearce et al. (2022) — Security of Copilot's Code. IEEE S&P.
- Zhong & Wang (2024) — Can LLM Replace Stack Overflow? AAAI.
- Wang et al. (2024) — CodeSecEval. arXiv.
- Becker et al. (2025) — AI Impact on Developer Productivity. METR.
- Cervantes, Kazman & Cai (2025) — LLM-assisted Architecture Design with ADD. arXiv.

---

# Contacto

**Dr. Humberto Cervantes Maceda**
UAM Iztapalapa — hcm@xanum.uam.mx

**Emilio Osorio**
HumanSys / RaiSE Framework — emilio@humansys.io

**RaiSE Framework**
raiseframework.ai · github.com/humansys-io/raise-commons

---

# ¿Preguntas?
