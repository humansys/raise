# RaiSE Lean Foundation Ontology
## Upper Ontology Extraction from Toyota Production System & Lean Software Development

**Versión:** 0.1.0  
**Estado:** Draft para Revisión  
**Fecha:** 28 de Diciembre, 2025  
**Autor:** RaiSE Ontology Architect  
**Propósito:** Establecer la ontología superior (Upper Ontology) basada en Lean Manufacturing y Lean Software Development que servirá como fundamento formal para todos los conceptos de RaiSE.

---

## Prefacio: Justificación Epistemológica

### ¿Por Qué una Upper Ontology Lean?

Una ontología de dominio (RaiSE) construida sin anclaje a un cuerpo de conocimiento validado es, epistemológicamente, una **opinión estructurada**. Al derivar RaiSE de Lean—un sistema con 70+ años de validación empírica en manufactura y 20+ años en software—transformamos opinión en **extensión justificada**.

### Criterios de Inclusión

Un concepto Lean se incluye en esta Upper Ontology si:

1. **Tiene fuente canónica**: Referenciable a Ohno, Shingo, Liker, o Poppendieck
2. **Es formalizable**: Puede expresarse como clase, propiedad o relación
3. **Es relevante para RaiSE**: Tiene mapping potencial al dominio de AI-assisted development

### Fuentes Primarias

| Fuente | Autor(es) | Año | Dominio |
|--------|-----------|-----|---------|
| Toyota Production System | Taiichi Ohno | 1978 | Manufactura |
| A Study of the Toyota Production System | Shigeo Shingo | 1981 | Manufactura |
| The Toyota Way | Jeffrey Liker | 2004 | Gestión |
| Lean Software Development | Mary & Tom Poppendieck | 2003 | Software |
| Implementing Lean Software Development | Mary & Tom Poppendieck | 2006 | Software |

---

# PARTE I: Toyota Production System (TPS)

## 1. Los Dos Pilares del TPS

El Toyota Production System se sostiene sobre dos pilares fundamentales que son **co-dependientes**—ninguno funciona sin el otro.

```
                    ┌─────────────────────────────────────┐
                    │      TOYOTA PRODUCTION SYSTEM       │
                    │         (Casa del TPS)              │
                    └─────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
              ┌─────┴─────┐                   ┌──────┴──────┐
              │  JIDOKA   │                   │     JIT     │
              │  自働化    │                   │ Just-in-Time│
              │           │                   │             │
              │ Calidad   │                   │ Flujo       │
              │ Integrada │                   │ Continuo    │
              └───────────┘                   └─────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                    ┌─────────────────────────────────────┐
                    │            FUNDAMENTO               │
                    │  Heijunka (平準化) - Nivelación     │
                    │  Trabajo Estandarizado              │
                    │  Kaizen (改善) - Mejora Continua    │
                    └─────────────────────────────────────┘
```

---

### 1.1 Jidoka (自働化) — Autonomation

#### Definición Canónica

> "Automatización con toque humano. La capacidad de las máquinas y procesos de detectar anomalías y detenerse automáticamente, permitiendo que los humanos intervengan para resolver la causa raíz."
> — Taiichi Ohno, Toyota Production System (1978)

#### Etimología

El kanji 働 (dō, "movimiento/trabajo") en 自動化 (automatización estándar) fue modificado por Toyoda Sakichi para incluir el radical 人 (persona), creando 自働化—literalmente "automatización con elemento humano".

#### Los Cuatro Pasos de Jidoka

| Paso | Japonés | Descripción | Formalización |
|------|---------|-------------|---------------|
| 1. Detectar | 異常検知 | Identificar que algo está mal | `detect(anomaly) → Boolean` |
| 2. Parar | 停止 | Detener el proceso inmediatamente | `stop(process) → State.HALTED` |
| 3. Corregir | 修正 | Resolver el problema inmediato | `fix(defect) → State.RESOLVED` |
| 4. Prevenir | 再発防止 | Evitar que recurra | `prevent(rootCause) → Rule` |

#### Principios Derivados

1. **Andon (行灯)**: Sistema de señalización visual del estado del proceso
2. **Poka-yoke (ポカヨケ)**: Mecanismos a prueba de errores
3. **5 Whys (なぜなぜ分析)**: Análisis de causa raíz mediante preguntas iterativas
4. **Genchi Genbutsu (現地現物)**: Ir al lugar real, ver la cosa real

#### Formalización Ontológica

```
CLASS Jidoka
  DESCRIPTION: "Principio de calidad integrada mediante detención automática ante anomalías"
  
  PROPERTIES:
    - hasDetectionMechanism: DetectionMechanism [1..*]
    - hasStopCondition: StopCondition [1..*]
    - hasCorrectiveAction: CorrectiveAction [0..*]
    - hasPreventiveMeasure: PreventiveMeasure [0..*]
  
  INVARIANTS:
    - ∀ anomaly ∈ DetectedAnomalies: process.state = HALTED
    - ∀ defect ∈ ResolvedDefects: ∃ preventiveMeasure ∈ PreventiveMeasures
  
  AXIOM (Jidoka-Completeness):
    detect(x) ∧ ¬stop(process) → VIOLATION
    "Si se detecta una anomalía y no se detiene el proceso, hay violación de Jidoka"
```

---

### 1.2 Just-in-Time (JIT)

#### Definición Canónica

> "Producir solo lo que se necesita, cuando se necesita, en la cantidad que se necesita."
> — Taiichi Ohno, Toyota Production System (1978)

#### Los Tres Elementos del JIT

| Elemento | Japonés | Descripción |
|----------|---------|-------------|
| **Takt Time** | タクトタイム | Ritmo de producción basado en demanda del cliente |
| **Continuous Flow** | 連続フロー | Movimiento sin interrupciones de una pieza a la vez |
| **Pull System** | 引っ張り方式 | Producción disparada por demanda downstream |

#### Kanban (看板) como Mecanismo de Pull

```
┌──────────────┐    Señal Kanban    ┌──────────────┐
│   PROCESO    │◄───────────────────│   PROCESO    │
│   UPSTREAM   │                    │  DOWNSTREAM  │
│              │────────────────────►              │
└──────────────┘    Flujo de Valor  └──────────────┘
```

El Kanban es una **señal visual** que autoriza la producción o movimiento de materiales. Sin señal Kanban, no hay producción.

#### Formalización Ontológica

```
CLASS JustInTime
  DESCRIPTION: "Principio de flujo continuo basado en demanda real"
  
  PROPERTIES:
    - hasTaktTime: Duration [1]
    - hasFlowUnits: FlowUnit [1..*]
    - hasPullSignal: PullSignal [0..*]
    - hasInventory: Inventory [0..*]
  
  INVARIANTS:
    - inventory.quantity → MINIMIZE
    - ∀ production ∈ Productions: ∃ pullSignal ∈ PullSignals
    - flowTime ≤ taktTime
  
  AXIOM (Pull-Only):
    produce(x) ∧ ¬∃ demand(x) → WASTE.Overproduction
    "Producir sin demanda es el peor desperdicio"
```

---

## 2. Los Tres Tipos de Desperdicio

### 2.1 Taxonomía del Desperdicio

```
                         DESPERDICIO (無駄)
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
      ┌───┴───┐          ┌────┴────┐         ┌────┴────┐
      │ MUDA  │          │  MURA   │         │  MURI   │
      │  無駄  │          │   斑    │         │   無理   │
      │       │          │         │         │         │
      │ Waste │          │Unevenness│        │Overburden│
      │       │          │         │         │         │
      │Actividad│        │Variabilidad│      │Sobrecarga│
      │sin valor│        │irregular │        │excesiva │
      └───────┘          └─────────┘         └─────────┘
```

---

### 2.2 Muda (無駄) — Los 7+1 Desperdicios

| # | Desperdicio | Japonés | Descripción | Ejemplo Manufactura |
|---|-------------|---------|-------------|---------------------|
| 1 | **Sobreproducción** | 作りすぎ | Producir más de lo necesario | Lotes grandes "por si acaso" |
| 2 | **Espera** | 手待ち | Tiempo ocioso esperando | Operador esperando máquina |
| 3 | **Transporte** | 運搬 | Movimiento innecesario de materiales | Layouts ineficientes |
| 4 | **Sobreprocesamiento** | 加工 | Procesos innecesarios | Tolerancias excesivas |
| 5 | **Inventario** | 在庫 | Exceso de materiales/WIP | Stock de seguridad inflado |
| 6 | **Movimiento** | 動作 | Movimiento innecesario de personas | Buscar herramientas |
| 7 | **Defectos** | 不良 | Productos que no cumplen spec | Retrabajo, scrap |
| 8 | **Talento no utilizado** | — | Skills desaprovechados | (Añadido por Liker) |

#### Formalización Ontológica

```
CLASS Muda
  DESCRIPTION: "Actividad que consume recursos sin agregar valor al cliente"
  SUPERCLASS: Waste
  
  SUBCLASSES:
    - Overproduction (作りすぎ)
    - Waiting (手待ち)
    - Transportation (運搬)
    - OverProcessing (加工)
    - Inventory (在庫)
    - Motion (動作)
    - Defects (不良)
    - UnusedTalent
  
  PROPERTIES:
    - consumesResource: Resource [1..*]
    - addsCustomerValue: Boolean = FALSE
    - isEliminable: Boolean
  
  AXIOM (Muda-Definition):
    ∀ activity: consumesResource(activity) ∧ ¬addsValue(activity, customer) 
      → activity ∈ Muda
```

---

### 2.3 Mura (斑) — Irregularidad

> "La variabilidad en el proceso es la madre de todo desperdicio."
> — Taiichi Ohno

**Mura** es la inconsistencia o irregularidad en el flujo de trabajo. Genera Muda porque:
- Picos de demanda → Sobreproducción para "buffer"
- Valles de demanda → Espera

**Contramedida principal**: Heijunka (nivelación de producción)

```
SIN HEIJUNKA:          │████████│        │████│            │██████████████│
                       └────────┴────────┴────┴────────────┴──────────────┘
                        Pico      Valle   Pico    Valle         Pico

CON HEIJUNKA:          │████│████│████│████│████│████│████│████│████│████│
                       └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
                        Flujo nivelado y predecible
```

#### Formalización Ontológica

```
CLASS Mura
  DESCRIPTION: "Variabilidad o irregularidad en el flujo de trabajo"
  SUPERCLASS: Waste
  
  PROPERTIES:
    - hasVarianceSource: VarianceSource [1..*]
    - causesMuda: Muda [0..*]
    - measuredBy: StatisticalMeasure [1..*]
  
  INVARIANTS:
    - variance(flow) > threshold → ∃ muda ∈ GeneratedMuda
  
  AXIOM (Mura-Generates-Muda):
    ∀ irregularity ∈ Mura: ∃ waste ∈ Muda: causes(irregularity, waste)
```

---

### 2.4 Muri (無理) — Sobrecarga

> "No pidas a la máquina o al trabajador más de lo que pueden dar consistentemente."
> — Shigeo Shingo

**Muri** es imponer carga excesiva sobre personas, máquinas o procesos. Genera:
- Fatiga → Errores → Defectos
- Desgaste → Fallas → Espera
- Burnout → Rotación → Pérdida de conocimiento

#### Formalización Ontológica

```
CLASS Muri
  DESCRIPTION: "Sobrecarga irrazonable sobre recursos"
  SUPERCLASS: Waste
  
  PROPERTIES:
    - overloadsResource: Resource [1..*]
    - exceedsCapacity: Capacity [1]
    - causesDegradation: Degradation [0..*]
  
  INVARIANTS:
    - load(resource) > capacity(resource) → resource.state = STRESSED
  
  AXIOM (Muri-Causes-Failure):
    ∀ overload ∈ Muri: probability(failure) ∝ duration(overload)
```

---

## 3. Los 14 Principios del Toyota Way (Liker)

Jeffrey Liker sistematizó la filosofía Toyota en 14 principios organizados en 4 categorías (4P):

### 3.1 Taxonomía de los 14 Principios

```
┌────────────────────────────────────────────────────────────────────┐
│                     THE TOYOTA WAY - 4P MODEL                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ PHILOSOPHY (Pensamiento a Largo Plazo)                      │   │
│  │   P1: Base decisions on long-term philosophy                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ PROCESS (El Proceso Correcto Produce Resultados Correctos)  │   │
│  │   P2: Create continuous process flow                        │   │
│  │   P3: Use "pull" systems                                    │   │
│  │   P4: Level out workload (Heijunka)                        │   │
│  │   P5: Stop to fix problems (Jidoka)                        │   │
│  │   P6: Standardized tasks are foundation                    │   │
│  │   P7: Use visual control                                    │   │
│  │   P8: Use only reliable, tested technology                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ PEOPLE & PARTNERS (Desarrollar Personas y Socios)           │   │
│  │   P9: Grow leaders who live the philosophy                  │   │
│  │   P10: Develop exceptional people and teams                 │   │
│  │   P11: Respect extended network                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ PROBLEM SOLVING (Mejora Continua y Aprendizaje)             │   │
│  │   P12: Go and see for yourself (Genchi Genbutsu)           │   │
│  │   P13: Make decisions slowly, implement rapidly             │   │
│  │   P14: Become learning organization (Hansei + Kaizen)      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 Detalle de los 14 Principios

| # | Principio | Categoría | Descripción |
|---|-----------|-----------|-------------|
| 1 | Long-Term Philosophy | Philosophy | Decisiones basadas en filosofía de largo plazo, incluso a expensas de metas financieras cortoplacistas |
| 2 | Continuous Flow | Process | Crear flujo continuo para hacer los problemas visibles |
| 3 | Pull Systems | Process | Usar sistemas pull para evitar sobreproducción |
| 4 | Heijunka | Process | Nivelar la carga de trabajo (no trabajar como liebre) |
| 5 | Jidoka | Process | Parar para arreglar problemas, obtener calidad a la primera |
| 6 | Standardized Tasks | Process | Tareas estandarizadas son el fundamento de mejora continua |
| 7 | Visual Control | Process | Usar control visual para que los problemas no se oculten |
| 8 | Reliable Technology | Process | Usar solo tecnología probada que sirva a las personas y procesos |
| 9 | Grow Leaders | People | Desarrollar líderes que vivan la filosofía y la enseñen |
| 10 | Develop People | People | Desarrollar personas y equipos excepcionales |
| 11 | Respect Partners | People | Respetar la red extendida de socios y proveedores |
| 12 | Genchi Genbutsu | Problem Solving | Ir a ver por uno mismo para entender la situación |
| 13 | Nemawashi | Problem Solving | Decidir lentamente por consenso, implementar rápidamente |
| 14 | Hansei + Kaizen | Problem Solving | Reflexión incesante y mejora continua |

---

## 4. Kaizen (改善) — Mejora Continua

### 4.1 Definición Canónica

> "Kaizen significa mejora. Aplicado a la vida personal, social, o laboral, significa mejora continua involucrando a todos—gerentes y trabajadores por igual."
> — Masaaki Imai, Kaizen: The Key to Japan's Competitive Success (1986)

### 4.2 El Ciclo PDCA (Deming/Shewhart)

Kaizen se operacionaliza mediante el ciclo PDCA:

```
            ┌─────────────┐
            │    PLAN     │
            │  (計画)     │
            │             │
            │ Identificar │
            │ problema y  │
            │ planear     │
            │ solución    │
            └──────┬──────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              │              ▼
┌───────┐          │          ┌───────┐
│  ACT  │          │          │  DO   │
│ (処置) │◄─────────┴─────────►│ (実施) │
│       │                     │       │
│Estandar│                    │Ejecutar│
│izar o │                     │ el    │
│ajustar│                     │ plan  │
└───┬───┘                     └───┬───┘
    │                             │
    │      ┌─────────────┐        │
    │      │    CHECK    │        │
    └─────►│   (確認)    │◄───────┘
           │             │
           │ Verificar   │
           │ resultados  │
           │ vs plan     │
           └─────────────┘
```

### 4.3 Tipos de Kaizen

| Tipo | Descripción | Escala | Frecuencia |
|------|-------------|--------|------------|
| **Point Kaizen** | Mejora rápida en un punto específico | Individual | Diaria |
| **System Kaizen** | Mejora de un sistema o proceso completo | Equipo | Semanal |
| **Kaikaku (改革)** | Mejora radical, transformación | Organización | Ocasional |

### 4.4 Formalización Ontológica

```
CLASS Kaizen
  DESCRIPTION: "Proceso de mejora continua incremental"
  
  PROPERTIES:
    - hasImprovement: Improvement [1..*]
    - followsCycle: PDCACycle [1]
    - involvesParticipants: Participant [1..*]
    - hasScope: KaizenScope {POINT, SYSTEM, KAIKAKU}
  
  SUBCLASSES:
    - PointKaizen
    - SystemKaizen
    - Kaikaku
  
  INVARIANTS:
    - ∀ cycle ∈ PDCACycles: cycle.phases = {PLAN, DO, CHECK, ACT}
    - improvement.delta > 0  // Siempre mejora positiva
  
  AXIOM (Kaizen-Continuity):
    ∀ t ∈ Time: ∃ improvement ∈ Improvements: occurs(improvement, t)
    "Siempre hay mejora ocurriendo en algún lugar"
```

---

## 5. Hansei (反省) — Reflexión

### 5.1 Definición Canónica

> "Hansei es reconocer tus propios errores y comprometerte a mejorar."
> — Toyota Way Fieldbook

### 5.2 Diferencia con Retrospectiva Occidental

| Aspecto | Retrospectiva Occidental | Hansei Japonés |
|---------|-------------------------|----------------|
| **Foco** | Proceso, sistema | Personal, individual |
| **Tono** | Neutral, analítico | Introspectivo, autocrítico |
| **Resultado** | Action items | Compromiso personal |
| **Frecuencia** | Al final del sprint | Continuo |

### 5.3 Formalización Ontológica

```
CLASS Hansei
  DESCRIPTION: "Práctica de reflexión honesta sobre errores y compromisos de mejora"
  
  PROPERTIES:
    - acknowledgesError: Error [1..*]
    - generatesCommitment: Commitment [1..*]
    - isPerformedBy: Individual [1]
  
  INVARIANTS:
    - ∀ error ∈ AcknowledgedErrors: ∃ commitment ∈ Commitments
    - commitment.owner = hansei.performer
  
  RELATIONSHIP:
    Hansei --feedsInto--> Kaizen
```

---

# PARTE II: Lean Software Development (Poppendieck)

## 6. Los 7 Principios de Lean Software Development

Mary y Tom Poppendieck tradujeron TPS al contexto de desarrollo de software en 2003.

### 6.1 Tabla de Correspondencia TPS → Software

| # | Principio Lean Software | Origen TPS | Descripción |
|---|------------------------|------------|-------------|
| 1 | **Eliminate Waste** | Muda elimination | Eliminar todo lo que no agrega valor |
| 2 | **Amplify Learning** | Kaizen, PDCA | El desarrollo es un proceso de aprendizaje |
| 3 | **Decide as Late as Possible** | Set-based design | Mantener opciones abiertas hasta el último momento responsable |
| 4 | **Deliver as Fast as Possible** | JIT, Flow | Entregar valor rápidamente para obtener feedback |
| 5 | **Empower the Team** | Respect for people | Equipos auto-organizados con autoridad |
| 6 | **Build Integrity In** | Jidoka | Calidad integrada, no inspeccionada al final |
| 7 | **See the Whole** | Systems thinking | Optimizar el sistema completo, no las partes |

---

### 6.2 Principio 1: Eliminar Desperdicio

#### Mapping de los 7 Desperdicios a Software

| Muda (Manufactura) | Equivalente en Software | Ejemplos |
|--------------------|------------------------|----------|
| Sobreproducción | Extra Features | Features que nadie usa |
| Inventario | Partially Done Work | Branches sin merge, specs sin implementar |
| Transporte | Task Switching | Cambio de contexto entre proyectos |
| Espera | Waiting | Esperando aprobaciones, builds, respuestas |
| Movimiento | Motion | Buscar información, reuniones innecesarias |
| Sobreprocesamiento | Extra Processes | Documentación excesiva, burocracia |
| Defectos | Defects | Bugs, retrabajo |

#### Formalización Ontológica

```
CLASS SoftwareWaste EXTENDS Muda
  DESCRIPTION: "Desperdicio en el contexto de desarrollo de software"
  
  SUBCLASSES:
    - ExtraFeatures (Sobreproducción)
    - PartiallyDoneWork (Inventario)
    - TaskSwitching (Transporte)
    - Waiting (Espera)
    - Motion (Movimiento)
    - ExtraProcesses (Sobreprocesamiento)
    - Defects (Defectos)
  
  PROPERTIES:
    - affectsDelivery: Boolean
    - measurableAs: Metric [1..*]
    - eliminableBy: Practice [0..*]
```

---

### 6.3 Principio 2: Amplificar el Aprendizaje

> "El desarrollo de software es un proceso de aprendizaje, no un proceso de producción."
> — Mary Poppendieck

#### Prácticas de Amplificación

| Práctica | Descripción | Mecanismo |
|----------|-------------|-----------|
| **Iterations** | Ciclos cortos de feedback | Aprender de entregas reales |
| **Set-Based Design** | Explorar múltiples opciones | Aprender antes de decidir |
| **Pair Programming** | Dos mentes en un problema | Transferencia de conocimiento |
| **Test-Driven Development** | Tests primero | Aprender requisitos profundamente |

#### Formalización Ontológica

```
CLASS LearningAmplification
  DESCRIPTION: "Prácticas que maximizan el aprendizaje durante el desarrollo"
  
  PROPERTIES:
    - hasFeedbackLoop: FeedbackLoop [1..*]
    - reducesUncertainty: UncertaintyDomain [1..*]
    - generatesKnowledge: Knowledge [0..*]
  
  INVARIANTS:
    - ∀ iteration: knowledge.postIteration > knowledge.preIteration
  
  AXIOM (Learning-Compounds):
    knowledge(t+1) = knowledge(t) + learning(iteration) - forgetting(t)
```

---

### 6.4 Principio 3: Decidir lo Más Tarde Posible

> "Retrasar decisiones irreversibles hasta el último momento responsable."
> — Mary Poppendieck

#### Concepto: Last Responsible Moment (LRM)

```
                    Conocimiento
                         │
                         │                    ╱
                         │                  ╱
                         │                ╱
                         │              ╱
                         │            ╱
                         │          ╱
                         │        ╱
                         │      ╱
                         │    ╱
                         │  ╱
                         │╱
           ──────────────┼──────────────────────────► Tiempo
                         │
                      Decisión          LRM
                      Prematura         │
                         │              │
                         │◄────────────►│
                              Zona Óptima
                            (Máximo conocimiento,
                             opciones aún abiertas)
```

#### Formalización Ontológica

```
CLASS DecisionTiming
  DESCRIPTION: "Gestión del momento óptimo para tomar decisiones"
  
  PROPERTIES:
    - hasDecision: Decision [1]
    - hasLRM: Timestamp [1]  // Last Responsible Moment
    - hasKnowledgeLevel: Float [0..1]
    - hasOptionsOpen: Integer
  
  INVARIANTS:
    - decisionTime ≤ LRM
    - knowledge(decisionTime) = MAX achievable before LRM
  
  AXIOM (LRM-Optimality):
    ∀ decision: value(decision) ∝ knowledge(decisionTime)
    "El valor de una decisión es proporcional al conocimiento disponible"
```

---

### 6.5 Principio 4: Entregar lo Más Rápido Posible

> "La velocidad reduce el riesgo."
> — Tom Poppendieck

#### Relación Velocidad-Aprendizaje

Entregas rápidas permiten:
1. **Feedback temprano**: Validar supuestos antes de invertir más
2. **Reducir inventario**: Menos WIP, menos riesgo
3. **Satisfacción del cliente**: Valor antes que después

#### Formalización Ontológica

```
CLASS DeliverySpeed
  DESCRIPTION: "Optimización del tiempo de entrega de valor"
  
  PROPERTIES:
    - hasCycleTime: Duration [1]
    - hasLeadTime: Duration [1]
    - hasThroughput: Rate [1]
    - hasWIPLimit: Integer [0..1]
  
  INVARIANTS:
    - cycleTime ≤ leadTime
    - WIP * cycleTime ≈ throughput  // Little's Law
  
  RELATIONSHIP:
    DeliverySpeed --enables--> LearningAmplification
```

---

### 6.6 Principio 5: Empoderar al Equipo

> "El conocimiento está en la gente que hace el trabajo."
> — Mary Poppendieck

#### Manifestaciones

| Práctica | Descripción |
|----------|-------------|
| **Self-organizing teams** | Equipos deciden cómo trabajar |
| **Pull commitment** | Equipo elige qué trabajo tomar |
| **Skill development** | Inversión en crecimiento individual |
| **Information transparency** | Acceso a toda información relevante |

#### Formalización Ontológica

```
CLASS TeamEmpowerment
  DESCRIPTION: "Estructuras que dan autoridad y responsabilidad a los equipos"
  
  PROPERTIES:
    - hasAutonomy: AutonomyLevel {LOW, MEDIUM, HIGH, FULL}
    - hasPullAuthority: Boolean
    - hasInformationAccess: InformationScope
    - hasSkillDevelopment: DevelopmentProgram [0..*]
  
  INVARIANTS:
    - autonomy = HIGH ∨ autonomy = FULL → pullAuthority = TRUE
  
  AXIOM (Empowerment-Expertise):
    ∀ decision ∈ TechnicalDecisions: 
      authority(decision) ∈ experts(decision.domain)
```

---

### 6.7 Principio 6: Construir Integridad

#### Dos Tipos de Integridad

| Tipo | Descripción | Cómo se logra |
|------|-------------|---------------|
| **Perceived Integrity** | El producto hace lo que el cliente espera | Customer involvement, feedback loops |
| **Conceptual Integrity** | El sistema tiene coherencia interna | Architecture, design patterns |

Este principio es la traducción directa de **Jidoka** al software.

#### Formalización Ontológica

```
CLASS Integrity
  DESCRIPTION: "Calidad integrada en el producto y proceso"
  
  SUBCLASSES:
    - PerceivedIntegrity  // Customer perspective
    - ConceptualIntegrity  // Technical perspective
  
  PROPERTIES:
    - hasQualityGates: QualityGate [1..*]
    - hasAutomatedTests: TestSuite [0..*]
    - hasDesignStandards: Standard [0..*]
  
  INVARIANTS:
    - ∀ defect ∈ DetectedDefects: defect.fixedBefore(release)
  
  RELATIONSHIP:
    Integrity --isManifestationOf--> Jidoka
```

---

### 6.8 Principio 7: Ver el Todo

> "Optimizar partes sub-optimiza el todo."
> — Tom Poppendieck

#### El Problema de la Optimización Local

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA COMPLETO                             │
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│   │ Equipo  │───►│ Equipo  │───►│ Equipo  │───►│ Equipo  │    │
│   │    A    │    │    B    │    │    C    │    │    D    │    │
│   │         │    │         │    │         │    │         │    │
│   │ ████    │    │ ██      │    │ ████████│    │ ██████  │    │
│   │Optimizado│   │Bottleneck│   │Optimizado│    │Optimizado│   │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    │
│                       ▲                                         │
│                       │                                         │
│              El sistema está limitado                           │
│              por su eslabón más débil                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Formalización Ontológica

```
CLASS SystemsThinking
  DESCRIPTION: "Perspectiva holística que optimiza el sistema completo"
  
  PROPERTIES:
    - hasComponents: Component [2..*]
    - hasBottleneck: Component [0..1]
    - hasThroughput: Rate [1]
    - hasGlobalOptimum: Optimum [1]
  
  INVARIANTS:
    - throughput(system) ≤ MIN(throughput(component) ∀ component)
  
  AXIOM (Local-vs-Global):
    ∑ optimize(component) ≠ optimize(system)
    "La suma de óptimos locales no es el óptimo global"
```

---

## 7. Las 22 Herramientas de Lean Software Development

Poppendieck organizó 22 herramientas prácticas agrupadas por principio:

### 7.1 Herramientas por Principio

| Principio | Herramientas |
|-----------|--------------|
| **Eliminate Waste** | Seeing Waste, Value Stream Mapping |
| **Amplify Learning** | Feedback, Iterations, Synchronization, Set-Based Development |
| **Decide Late** | Options Thinking, Last Responsible Moment, Making Decisions |
| **Deliver Fast** | Pull Systems, Queuing Theory, Cost of Delay |
| **Empower Team** | Self-Determination, Motivation, Leadership, Expertise |
| **Build Integrity** | Perceived Integrity, Conceptual Integrity, Refactoring, Testing |
| **See Whole** | Measurements, Contracts |

### 7.2 Formalización como Taxonomía

```
CLASS LeanTool
  DESCRIPTION: "Herramienta práctica de Lean Software Development"
  
  PROPERTIES:
    - supportssPrinciple: LeanPrinciple [1..*]
    - hasApplication: Application [1..*]
    - requiresSkill: Skill [0..*]
  
  SUBCLASSES:
    - WasteSeeing
    - ValueStreamMapping
    - FeedbackLoop
    - Iteration
    - SetBasedDevelopment
    - OptionsThinking
    - PullSystem
    - QueuingTheory
    - CostOfDelay
    - SelfDetermination
    - PerceivedIntegrityTool
    - ConceptualIntegrityTool
    - Refactoring
    - Testing
    - Measurement
```

---

# PARTE III: Ontología Formal Consolidada

## 8. Clases Fundamentales

### 8.1 Jerarquía de Clases

```
Thing
├── Principle
│   ├── TPSPrinciple
│   │   ├── Jidoka
│   │   ├── JustInTime
│   │   └── Kaizen
│   └── LeanSoftwarePrinciple
│       ├── EliminateWaste
│       ├── AmplifyLearning
│       ├── DecideLate
│       ├── DeliverFast
│       ├── EmpowerTeam
│       ├── BuildIntegrity
│       └── SeeWhole
│
├── Waste
│   ├── Muda
│   │   ├── Overproduction
│   │   ├── Waiting
│   │   ├── Transportation
│   │   ├── OverProcessing
│   │   ├── Inventory
│   │   ├── Motion
│   │   ├── Defects
│   │   └── UnusedTalent
│   ├── Mura
│   └── Muri
│
├── Practice
│   ├── Hansei
│   ├── Genchi Genbutsu
│   ├── Nemawashi
│   ├── Poka-yoke
│   └── Andon
│
├── Process
│   ├── PDCACycle
│   ├── ValueStream
│   └── Flow
│
├── Artifact
│   ├── Kanban
│   ├── Standard
│   └── VisualControl
│
└── Tool
    └── LeanTool (22 subclasses)
```

---

## 9. Propiedades (Properties)

### 9.1 Object Properties (Relaciones)

| Propiedad | Dominio | Rango | Descripción |
|-----------|---------|-------|-------------|
| `implements` | Practice | Principle | Una práctica implementa un principio |
| `eliminates` | Practice | Waste | Una práctica elimina un tipo de desperdicio |
| `causes` | Mura | Muda | Mura genera Muda |
| `feedsInto` | Hansei | Kaizen | Reflexión alimenta mejora |
| `enables` | Flow | DeliverySpeed | Flujo habilita velocidad |
| `manifests` | Integrity | Jidoka | Integridad manifiesta Jidoka |
| `supports` | LeanTool | LeanPrinciple | Herramienta soporta principio |
| `detects` | Jidoka | Defect | Jidoka detecta defectos |
| `signals` | Kanban | Production | Kanban señala producción |
| `limits` | Bottleneck | Throughput | Cuello de botella limita throughput |

### 9.2 Data Properties (Atributos)

| Propiedad | Dominio | Tipo | Descripción |
|-----------|---------|------|-------------|
| `hasCycleTime` | Process | Duration | Tiempo de ciclo |
| `hasLeadTime` | Process | Duration | Tiempo de entrega |
| `hasTaktTime` | JIT | Duration | Ritmo de producción |
| `hasWIPLimit` | Flow | Integer | Límite de trabajo en proceso |
| `hasVariance` | Mura | Float | Medida de variabilidad |
| `hasCapacity` | Resource | Float | Capacidad del recurso |
| `hasLoad` | Resource | Float | Carga actual |
| `isEliminable` | Muda | Boolean | Si el desperdicio es eliminable |

---

## 10. Axiomas y Constraints

### 10.1 Axiomas Fundamentales

```
AXIOM TPS-Foundation
  "Los dos pilares del TPS son co-dependientes"
  Jidoka ∧ JIT → TPS
  ¬Jidoka ∨ ¬JIT → ¬TPS.complete

AXIOM Waste-Hierarchy
  "Mura genera Muda, Muri genera ambos"
  Mura → ∃ Muda
  Muri → ∃ Muda ∧ ∃ Mura

AXIOM Flow-Integrity
  "Sin Jidoka no hay flujo sostenible"
  Flow.sustainable → Jidoka.active

AXIOM Pull-Only-Production
  "Producción sin demanda es el peor desperdicio"
  produce(x) ∧ ¬demand(x) → Waste.Overproduction

AXIOM Kaizen-Continuity
  "Siempre debe haber mejora en progreso"
  ∀ t: ∃ improvement: active(improvement, t)

AXIOM System-Throughput
  "El throughput del sistema está limitado por su bottleneck"
  throughput(system) = MIN(throughput(component) ∀ component ∈ system)

AXIOM Learning-Compounds
  "El conocimiento se acumula con cada iteración"
  knowledge(t+1) ≥ knowledge(t) if iteration.completed

AXIOM LRM-Optimality
  "Decidir en el LRM maximiza valor de la decisión"
  value(decision) ∝ knowledge(decisionTime)
  decisionTime = LRM → value = MAX
```

### 10.2 Constraints de Integridad

```
CONSTRAINT Jidoka-Stop-Required
  detect(anomaly) → process.state = HALTED
  VIOLATION: "Anomalía detectada sin detener el proceso"

CONSTRAINT Kaizen-Requires-Hansei
  ∀ kaizen: ∃ hansei: precedes(hansei, kaizen)
  VIOLATION: "Mejora sin reflexión previa"

CONSTRAINT WIP-Limit-Enforced
  count(workInProgress) ≤ WIPLimit
  VIOLATION: "Límite de WIP excedido"

CONSTRAINT Pull-Before-Push
  ∀ production: ∃ demand: triggers(demand, production)
  VIOLATION: "Producción sin demanda (push)"
```

---

## 11. Tabla de Trazabilidad Completa

### 11.1 TPS → Lean Software

| Concepto TPS | Concepto Lean Software | Tipo de Relación |
|--------------|----------------------|------------------|
| Jidoka | Build Integrity In | Equivalencia |
| JIT | Deliver Fast | Derivación |
| Kaizen | Amplify Learning | Extensión |
| Muda | Software Waste | Especialización |
| Heijunka | Level Workload | Equivalencia |
| Kanban | Pull System | Instanciación |
| Andon | Visual Control | Equivalencia |
| Genchi Genbutsu | Go See | Equivalencia |
| Hansei | Retrospective | Adaptación |
| Nemawashi | Consensus Decision | Equivalencia |
| Takt Time | Iteration Cadence | Adaptación |
| Flow | Continuous Flow | Equivalencia |
| Poka-yoke | Automated Testing | Derivación |
| 5 Whys | Root Cause Analysis | Equivalencia |

### 11.2 Lean Software → Prácticas Modernas

| Principio Lean Software | Prácticas Modernas |
|------------------------|-------------------|
| Eliminate Waste | Value Stream Mapping, Kanban |
| Amplify Learning | TDD, Pair Programming, Iterations |
| Decide Late | Set-Based Design, Spike Solutions |
| Deliver Fast | CI/CD, Feature Flags |
| Empower Team | Self-organizing Teams, Mob Programming |
| Build Integrity | TDD, Refactoring, Code Review |
| See Whole | OKRs, System Metrics |

---

# PARTE IV: Apéndices

## A. Glosario Japonés-Español

| Término | Kanji | Romaji | Traducción |
|---------|-------|--------|------------|
| Jidoka | 自働化 | Jidōka | Autonomación |
| Kaizen | 改善 | Kaizen | Mejora continua |
| Muda | 無駄 | Muda | Desperdicio |
| Mura | 斑 | Mura | Irregularidad |
| Muri | 無理 | Muri | Sobrecarga |
| Kanban | 看板 | Kanban | Señal visual |
| Andon | 行灯 | Andon | Lámpara/señal |
| Heijunka | 平準化 | Heijunka | Nivelación |
| Hansei | 反省 | Hansei | Reflexión |
| Genchi Genbutsu | 現地現物 | Genchi Genbutsu | Ir y ver |
| Nemawashi | 根回し | Nemawashi | Consenso previo |
| Poka-yoke | ポカヨケ | Poka-yoke | A prueba de errores |

## B. Bibliografía Canónica

1. Ohno, T. (1978). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press.
2. Shingo, S. (1981). *A Study of the Toyota Production System*. Productivity Press.
3. Liker, J. (2004). *The Toyota Way: 14 Management Principles*. McGraw-Hill.
4. Poppendieck, M. & T. (2003). *Lean Software Development: An Agile Toolkit*. Addison-Wesley.
5. Poppendieck, M. & T. (2006). *Implementing Lean Software Development*. Addison-Wesley.
6. Imai, M. (1986). *Kaizen: The Key to Japan's Competitive Success*. McGraw-Hill.
7. Womack, J. & Jones, D. (1996). *Lean Thinking*. Simon & Schuster.

## C. Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 0.1.0 | 2025-12-28 | Documento inicial |

---

*Este documento es la Upper Ontology canónica para RaiSE. Toda extensión debe trazarse a conceptos aquí definidos.*
