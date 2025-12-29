# RaiSE Methodology
## Flujo de Valor para Desarrollo Confiable

**Versión:** 2.1.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Documentar el flujo metodológico completo de RaiSE.

> **Nota de versión 2.1:** Actualización de niveles de Kata a nombres semánticos (Principios/Flujo/Patrón/Técnica). Jidoka inline en Katas.

---

## Filosofía

RaiSE es fundamentalmente un **framework de Lean Software Development** que integra agentes de IA como aceleradores del flujo de valor. Derivado del Toyota Production System, RaiSE aplica los principios Lean al desarrollo asistido por IA.

> Para una exploración profunda de la filosofía de aprendizaje, ver [05-learning-philosophy.md](./05-learning-philosophy.md).

### Los Cuatro Pilares

#### 1. Heutagogía
El desarrollador no es un consumidor pasivo de código generado por IA—es un **Orquestador**. RaiSE no solo entrega soluciones; **desafía** al humano para asegurar comprensión y ownership.

> El sistema enseña a pescar, no solo entrega el pescado.

#### 2. Jidoka (Calidad Construida)
Cada **Validation Gate** es un **punto Jidoka**: el proceso puede—y debe—detenerse si hay anomalías. Los cuatro pasos: Detectar → Parar → Corregir → Continuar.

```
Gate-Context   →  Stakeholders y restricciones claras
Gate-Discovery →  PRD validado
Gate-Vision    →  Solution Vision aprobada
Gate-Design    →  Tech Design completo
Gate-Backlog   →  HUs priorizadas
Gate-Plan      →  Implementation Plan verificado
Gate-Code      →  Código que pasa todas las validaciones
Gate-Deploy    →  Feature en producción
```

**Jidoka Inline [v2.1]:** Cada paso de una Kata incluye verificación y guía de corrección embebida:

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

El Orquestador ve la resolución en contexto, no en una sección separada.

#### 3. Just-In-Time Learning
Conocimiento adquirido exactamente cuando se necesita, integrado al flujo de trabajo. Opera en tres dimensiones: contexto para el agente, conocimiento para el Orquestador, mejoras para el framework.

#### 4. Kaizen (Mejora Continua)
Si un prompt falló o el código requirió muchas iteraciones, los guardrails y katas se refinan. El sistema aprende de sus errores. **Cada feature implementada mejora el framework para la siguiente.**

---

## Context Engineering: El Meta-Principio

RaiSE practica **Context Engineering**—el diseño deliberado del ambiente informacional que consume el agente. A diferencia del "prompt engineering" (tweaking de instrucciones), Context Engineering arquitecta:

| Componente | Función | Artefacto RaiSE |
|------------|---------|-----------------|
| **Principios** | Marco de decisiones inmutable | Constitution |
| **Restricciones** | Límites operacionales | Guardrails |
| **Contexto** | Información del proyecto | Golden Data, Specs |
| **Validación** | Puntos de control | Validation Gates |

> "No es prompt engineering, es **context engineering**—arquitectar todo el ambiente de información en el que opera el LLM." — Andrej Karpathy, 2025

---

## Niveles de Kata [v2.1]

Las Katas están organizadas en cuatro niveles semánticos que reflejan niveles de abstracción:

```
Principios → Flujo → Patrón → Técnica
```

| Nivel | Pregunta Guía | Conexión Lean | Ejemplos |
|-------|---------------|---------------|----------|
| **Principios** | ¿Por qué? ¿Cuándo? | Toyota Way | Rol del Orquestador, Heutagogía |
| **Flujo** | ¿Cómo fluye el trabajo? | Value Stream | Discovery, Planning, Generación de Plan |
| **Patrón** | ¿Qué estructura usar? | Standardized Work | Tech Design, Análisis de Código |
| **Técnica** | ¿Cómo ejecutar esto? | Work Instructions | Modelado de Datos, API Design |

**Ubicación:** `raise-config/katas/{nivel}/*.md`

> **Migración:** Los aliases L0-L3 se mantienen para backward compatibility.

---

## Principios Operativos

| # | Principio | Implicación Práctica |
|---|-----------|---------------------|
| 1 | **Humano como Orquestador** | Define el "qué" y "por qué"; valida el "cómo" |
| 2 | **Context Engineering** | Diseñar ambiente informacional antes de pedir código |
| 3 | **Explicabilidad Primero** | Pedir a la IA que explique antes de generar |
| 4 | **Estructura = Confiabilidad** | Usar plantillas y guardrails rigurosamente |
| 5 | **Validación Multinivel** | Funcional, estructural, arquitectónica, semántica |
| 6 | **Aprendizaje Continuo** | Cada interacción mejora el sistema |

---

## El Flujo de Valor

### Fase 0: Contexto

**Propósito:** Establecer comprensión inicial del problema y el ambiente.

**Actividades:**
- Reuniones de descubrimiento con stakeholders
- Identificación de tecnologías y restricciones
- Exploración de proyecto (brownfield) o definición (greenfield)

**Artefacto:** Notas de exploración, contexto inicial

**Validation Gate: Context**
- [ ] Stakeholders identificados
- [ ] Tecnologías principales definidas
- [ ] Restricciones documentadas

---

### Fase 1: Discovery

**Propósito:** Formalizar los requisitos del proyecto desde la perspectiva de negocio.

**Agente:** —  
**Inputs:** Notas de reuniones, contexto inicial

**Actividades:**
1. Consolidar información de descubrimiento
2. Usar plantilla estándar: `templates/solution/project_requirements.md`
3. Documentar: problema, metas, stakeholders, alcance, requisitos

**Artefacto:** PRD (Product Requirements Document)

**Validation Gate: Discovery**
- [ ] Problema de negocio articulado claramente
- [ ] Metas y métricas de éxito definidas
- [ ] Alcance (in/out) explícito
- [ ] Requisitos funcionales y no funcionales listados
- [ ] Supuestos y riesgos documentados

---

### Fase 2: Solution Vision

**Propósito:** Desarrollar visión de alto nivel que alinee negocio con diseño técnico.

**Agente:** Arquitecto  
**Inputs:** PRD

**Actividades:**
1. Instanciar Agente Arquitecto con PRD como contexto
2. Usar plantilla: `templates/solution/solution-vision-template.md`
3. Generar visión de solución

**Artefacto:** Solution Vision Document

**Validation Gate: Vision**
- [ ] Alineación con objetivos de negocio verificada
- [ ] Componentes de alto nivel identificados
- [ ] Decisiones arquitectónicas clave documentadas
- [ ] Aprobación de stakeholders

**Escalation Gate:** Si hay ambigüedad en requisitos de negocio → escalar a stakeholders antes de continuar.

---

### Fase 3: Technical Design

**Propósito:** Traducir la visión a arquitectura técnica detallada.

**Agente:** Tech Lead  
**Inputs:** PRD, Solution Vision

**Actividades:**
1. Instanciar Agente Tech Lead
2. Usar plantilla: `templates/tech/tech_design.md`
3. Proporcionar documentación técnica adicional (APIs, schemas)
4. Validar endpoints y contratos

**Artefacto:** Technical Design Document

**Validation Gate: Design**
- [ ] Arquitectura de componentes documentada
- [ ] Flujos de datos definidos
- [ ] Contratos de API especificados
- [ ] Modelo de datos diseñado
- [ ] Alternativas consideradas documentadas
- [ ] Validación técnica completada

**Escalation Gate:** Si hay trade-offs significativos de arquitectura → escalar a Tech Lead/Arquitecto humano.

---

### Fase 4: Backlog

**Propósito:** Desglosar diseño en features y user stories priorizadas.

**Agente:** Tech Lead → Coder  
**Inputs:** Tech Design, PRD, Solution Vision

**Actividades:**
1. **Features:** Usar plantilla de priorización para evaluar features
2. **Priorización:** Evaluar valor de negocio, necesidad de usuario, complejidad
3. **MVP:** Seleccionar features para Fase 1
4. **User Stories:** Desglosar features en HUs usando plantilla `backlog/user_story.md`
5. **Refinamiento:** Fusionar HUs pequeñas, eliminar redundancias

**Artefactos:** 
- Feature Prioritization Matrix
- User Stories (individuales)

**Validation Gate: Backlog**
- [ ] Features priorizadas con scoring
- [ ] MVP definido
- [ ] HUs siguen formato estándar
- [ ] Criterios de aceptación en BDD (Dado/Cuando/Entonces)
- [ ] Secuencia de implementación establecida

---

### Fase 5: Implementation Plan

**Propósito:** Crear plan paso a paso determinista para cada HU.

**Agente:** Coder (con kata de planificación)  
**Inputs:** User Stories, Tech Design  
**Kata:** `flujo/04-generacion-plan.md` (antes: L1-04)

**Actividades:**
1. Aplicar kata de generación de plan
2. Generar plan detallado por cada HU
3. Revisar que pasos sean lógicos y completos
4. Eliminar pasos irrelevantes

**Artefacto:** Implementation Plan por HU

**Validation Gate: Plan**
- [ ] Cada HU tiene plan de implementación
- [ ] Pasos son atómicos y verificables
- [ ] Dependencias identificadas
- [ ] Criterios de verificación incluidos

---

### Fase 6: Development

**Propósito:** Ejecutar implementación guiada por el plan.

**Agente:** Coder  
**Inputs:** Implementation Plan, Guardrails de código

**Actividades:**
1. **Context Engineering:** Proporcionar a IA los documentos relevantes (specs, design, guardrails)
2. **Explicabilidad:** Pedir explicación del enfoque ANTES de generar
3. **Generación guiada:** Usar guardrails de `.cursor/rules/`
4. **TDD:** Generar tests antes/junto con código
5. **Validación crítica:** NUNCA aceptar código ciegamente

**Debugging Científico (Ishikawa):**
Para bugs o problemas de implementación, aplicar análisis de causa raíz antes de implementar fixes.

**Artefacto:** Código implementado y testeado

**Validation Gate: Code**
- [ ] Código pasa pruebas unitarias
- [ ] Código cumple estándares de estilo
- [ ] Código alineado con diseño técnico
- [ ] Código revisado por humano
- [ ] Documentación inline donde necesario

**Escalation Gate:** Si el agente genera código que no entiende el Orquestador → escalar explicación antes de aceptar.

---

### Fase 7: UAT & Deploy

**Propósito:** Validación final y despliegue a producción.

**Actividades:**
1. Validación multinivel:
   - **Funcional:** ¿Cumple los AC?
   - **Estructural:** ¿Cumple guardrails de estilo?
   - **Arquitectónica:** ¿Alineado con patrones?
   - **Semántica:** ¿Refleja reglas de negocio?
2. Integración continua (CI/CD)
3. Revisión humana final
4. Deploy a ambiente objetivo

**Validation Gate: Deploy**
- [ ] UAT aprobado
- [ ] CI pipeline verde
- [ ] Documentación actualizada
- [ ] Feature en producción
- [ ] Retrospectiva programada

---

## Sistema de Katas [v2.1]

Los katas son procesos estructurados que codifican estándares y patrones. Ver [20-glossary.md](./20-glossary.md) para definición.

> **Diferenciador estratégico:** Ningún framework de agentes AI usa el término "Kata". RaiSE lo mantiene como conexión explícita con Lean y práctica deliberada.

### Jerarquía de Niveles Semánticos

| Nivel | Pregunta Guía | Propósito | Desviación Visible |
|-------|---------------|-----------|-------------------|
| **Principios** | ¿Por qué? ¿Cuándo? | Aplicar §1-§8 de Constitution | "No puedo justificar esta decisión" |
| **Flujo** | ¿Cómo fluye el trabajo? | Secuencias de valor estandarizadas | "No tengo el input requerido" |
| **Patrón** | ¿Qué estructura usar? | Formas recurrentes y templates | "El output no cumple la estructura" |
| **Técnica** | ¿Cómo ejecutar esto? | Instrucciones específicas | "La validación técnica falla" |

### Migración L0-L3 → Niveles Semánticos

| Antes | Después | Alias |
|-------|---------|-------|
| `L0` | `principios` | `L0`, `meta` |
| `L1` | `flujo` | `L1`, `proceso` |
| `L2` | `patron` | `L2`, `componente` |
| `L3` | `tecnica` | `L3`, `tecnico` |

### Estructura de Directorios

```
raise-config/
└── katas/
    ├── principios/     # ¿Por qué? ¿Cuándo?
    ├── flujo/          # ¿Cómo fluye?
    ├── patron/         # ¿Qué forma?
    └── tecnica/        # ¿Cómo hacer?
```

### Uso Correcto

> ⚠️ **No ejecutar katas directamente.** Siempre crear un Plan de Implementación específico para el contexto usando `flujo/04-generacion-plan.md`.

---

## Escalation Gates: Human-in-the-Loop

Los Escalation Gates son puntos específicos donde el agente DEBE escalar al Orquestador humano.

### Criterios de Escalación

| Criterio | Descripción | Ejemplo |
|----------|-------------|---------|
| **Confianza baja** | Agente expresa incertidumbre | "No estoy seguro si esto viola el patrón X" |
| **Alto impacto** | Decisión afecta arquitectura o seguridad | Cambio de modelo de datos |
| **Ambigüedad** | Spec o contexto incompleto | Requisito con múltiples interpretaciones |
| **Patrón nuevo** | Primera vez usando una técnica | Nuevo framework o librería |
| **Ownership** | Código que el Orquestador no entiende | Lógica compleja de negocio |

### Métricas de Escalación

| Métrica | Target | Señal de problema |
|---------|--------|-------------------|
| **Escalation Rate** | 10-15% | <5% = agente muy autónomo (riesgo); >25% = contexto insuficiente |
| **Escalation Resolution Time** | <30 min | >1 hora = proceso ineficiente |
| **Re-escalation Rate** | <10% | >20% = resolución insuficiente |

---

## Adaptación por Contexto

### Para Features Pequeñas
```
Fase 1 (Discovery) → Fase 5 (Plan) → Fase 6 (Dev)
```
Omitir creación formal de Solution Vision y Tech Design general si el cambio es menor.

### Para Proyectos Greenfield
Ejecutar flujo completo, dedicando tiempo extra a Fases 0-3.

### Para Brownfield/Legacy
Agregar paso de **escaneo de legado** antes de Fase 1:
- Análisis de código existente (kata `patron/02-analisis-codigo.md`)
- Descubrimiento de ecosistema (kata `patron/03-discovery-ecosistema.md`)
- Generación de guardrails desde patrones existentes

---

## Observable Workflow: Trazabilidad

RaiSE implementa Observable Workflow—cada decisión del agente es trazable.

### Qué se observa

| Evento | Datos capturados | Uso |
|--------|------------------|-----|
| Validation Gate pasado | Gate, timestamp, criterios | Auditoría de calidad |
| Escalation Gate activado | Criterio, resolución | Mejora de contexto |
| Kata ejecutado | Kata ID, inputs, outputs | Métricas de proceso |
| Código generado | Hash, agente, spec source | Trazabilidad AI |

### Métricas de Calidad AI

| Métrica | Descripción | Target |
|---------|-------------|--------|
| **Re-prompting Rate** | Iteraciones para output aceptable | <3 |
| **Context Adherence** | Alineamiento con spec | >85% |
| **Hallucination Rate** | Información fabricada | <10% |
| **Rework Rate** | Código modificado post-merge | Monitorear tendencia |

---

## Mejora Continua

### Retrospectivas
Al finalizar features significativas:
- ¿Qué funcionó en la colaboración humano-IA?
- ¿Dónde falló la guía o el contexto?
- ¿Hubo prompts repetitivos?

### Acciones de Mejora
1. **Actualizar guardrails** (`.cursor/rules/`)
2. **Refinar plantillas** (`.raise/templates/`)
3. **Evolucionar agentes** (prompts, capacidades)
4. **Documentar aprendizajes**

### Checkpoint Heutagógico
Al finalizar cada feature significativa:
1. ¿Qué aprendiste que no sabías antes?
2. ¿Qué cambiarías del proceso?
3. ¿Hay mejoras para el framework?
4. ¿En qué eres más capaz ahora?

---

## Changelog

### v2.1.0 (2025-12-28)
- NUEVO: Sección "Niveles de Kata" con nombres semánticos
- NUEVO: Jidoka inline en descripción de Katas
- ACTUALIZADO: Sistema de Katas con jerarquía semántica
- ACTUALIZADO: Referencias de L0-L3 → Principios/Flujo/Patrón/Técnica
- ACTUALIZADO: Estructura de directorios de katas

### v2.0.0 (2025-12-28)
- **Renombrado**: DoD-X → Validation Gate: X
- **Nuevo**: Sección Context Engineering
- **Nuevo**: Escalation Gates con métricas
- **Nuevo**: Observable Workflow
- **Nuevo**: Métricas de Calidad AI
- Terminología actualizada: Rule → Guardrail

---

*Esta metodología es un documento vivo. Evoluciona con cada retrospectiva y aprendizaje.*
