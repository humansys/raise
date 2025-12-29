# RaiSE Methodology
## Flujo de Valor para Desarrollo Confiable

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Documentar el flujo metodológico completo de RaiSE.

---

## Filosofía

RaiSE es fundamentalmente un **framework de Lean Software Development** que integra agentes de IA como aceleradores del flujo de valor. Derivado del Toyota Production System, RaiSE aplica los principios Lean al desarrollo asistido por IA.

> Para una exploración profunda de la filosofía de aprendizaje, ver [05-learning-philosophy.md](file:///home/emilio/Code/raise-commons/docs/corpus/05-learning-philosophy.md).

### Los Cuatro Pilares

#### 1. Heutagogía
El desarrollador no es un consumidor pasivo de código generado por IA—es un **Orquestador**. RaiSE no solo entrega soluciones; **desafía** al humano para asegurar comprensión y ownership.

> El sistema enseña a pescar, no solo entrega el pescado.

#### 2. Jidoka (Calidad Construida)
Cada DoD fractal es un **punto Jidoka**: el proceso puede—y debe—detenerse si hay anomalías. Los cuatro pasos: Detectar → Parar → Corregir → Prevenir recurrencia.

```
Fase 0: DoD-Contexto   →  Stakeholders y restricciones claras
Fase 1: DoD-Discovery  →  PRD validado
Fase 2: DoD-Vision     →  Solution Vision aprobada
Fase 3: DoD-Design     →  Tech Design completo
Fase 4: DoD-Backlog    →  HUs priorizadas
Fase 5: DoD-Plan       →  Implementation Plan
Fase 6: DoD-Code       →  Código que pasa todas las validaciones
Fase 7: DoD-Deploy     →  Feature en producción
```

#### 3. Just-In-Time Learning
Conocimiento adquirido exactamente cuando se necesita, integrado al flujo de trabajo. Opera en tres dimensiones: contexto para el agente, conocimiento para el Orquestador, mejoras para el framework.

#### 4. Kaizen (Mejora Continua)
Si un prompt falló o el código requirió muchas iteraciones, las reglas y katas se refinan. El sistema aprende de sus errores. **Cada feature implementada mejora el framework para la siguiente.**

---

## Principios Operativos

| # | Principio | Implicación Práctica |
|---|-----------|---------------------|
| 1 | **Humano como Orquestador** | Define el "qué" y "por qué"; valida el "cómo" |
| 2 | **Contexto Estructurado** | Siempre proporcionar specs/diseños antes de pedir código |
| 3 | **Explicabilidad Primero** | Pedir a la IA que explique antes de generar |
| 4 | **Estructura = Confiabilidad** | Usar plantillas y reglas rigurosamente |
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

**DoD-Contexto:**
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

**DoD-Discovery:**
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

**DoD-Vision:**
- [ ] Alineación con objetivos de negocio verificada
- [ ] Componentes de alto nivel identificados
- [ ] Decisiones arquitectónicas clave documentadas
- [ ] Aprobación de stakeholders

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

**DoD-Design:**
- [ ] Arquitectura de componentes documentada
- [ ] Flujos de datos definidos
- [ ] Contratos de API especificados
- [ ] Modelo de datos diseñado
- [ ] Alternativas consideradas documentadas
- [ ] Validación técnica completada

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

**DoD-Backlog:**
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
**Kata:** `L1-04-generacion-plan-implementacion-hu.md`

**Actividades:**
1. Aplicar kata de generación de plan
2. Generar plan detallado por cada HU
3. Revisar que pasos sean lógicos y completos
4. Eliminar pasos irrelevantes

**Artefacto:** Implementation Plan por HU

**DoD-Plan:**
- [ ] Cada HU tiene plan de implementación
- [ ] Pasos son atómicos y verificables
- [ ] Dependencias identificadas
- [ ] Criterios de verificación incluidos

---

### Fase 6: Development

**Propósito:** Ejecutar implementación guiada por el plan.

**Agente:** Coder  
**Inputs:** Implementation Plan, Reglas de código

**Actividades:**
1. **Contexto primero:** Proporcionar a IA los documentos relevantes
2. **Explicabilidad:** Pedir explicación del enfoque ANTES de generar
3. **Generación guiada:** Usar reglas de `.cursor/rules/`
4. **TDD:** Generar tests antes/junto con código
5. **Validación crítica:** NUNCA aceptar código ciegamente

**Debugging Científico (Ishikawa):**
Para bugs o problemas de implementación, aplicar análisis de causa raíz antes de implementar fixes.

**Artefacto:** Código implementado y testeado

**DoD-Code:**
- [ ] Código pasa pruebas unitarias
- [ ] Código cumple estándares de estilo
- [ ] Código alineado con diseño técnico
- [ ] Código revisado por humano
- [ ] Documentación inline donde necesario

---

### Fase 7: UAT & Deploy

**Propósito:** Validación final y despliegue a producción.

**Actividades:**
1. Validación multinivel:
   - **Funcional:** ¿Cumple los AC?
   - **Estructural:** ¿Cumple reglas de estilo?
   - **Arquitectónica:** ¿Alineado con patrones?
   - **Semántica:** ¿Refleja reglas de negocio?
2. Integración continua (CI/CD)
3. Revisión humana final
4. Deploy a ambiente objetivo

**DoD-Deploy:**
- [ ] UAT aprobado
- [ ] CI pipeline verde
- [ ] Documentación actualizada
- [ ] Feature en producción
- [ ] Retrospectiva programada

---

## Sistema de Katas

Los katas son procesos estructurados que codifican estándares y patrones. Ver [20-glossary.md](file:///home/emilio/Code/raise-commons/docs/corpus/20-glossary.md) para definición.

### Jerarquía de Niveles

| Nivel | Propósito | Uso |
|-------|-----------|-----|
| **L0** | Meta-katas: filosofía fundamental | Referencia conceptual |
| **L1** | Katas de proceso: metodología | Planificación, flujos |
| **L2** | Katas de componentes: patrones | Análisis, diseño |
| **L3** | Katas técnicos: especialización | Implementación avanzada |

### Uso Correcto

> ⚠️ **No ejecutar katas directamente.** Siempre crear un Plan de Implementación específico para el contexto usando `L1-04-generacion-plan-implementacion-hu.md`.

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
- Análisis de código existente (kata L2-02)
- Descubrimiento de ecosistema (kata L2-03)
- Generación de reglas desde patrones existentes

---

## Mejora Continua

### Retrospectivas
Al finalizar features significativas:
- ¿Qué funcionó en la colaboración humano-IA?
- ¿Dónde falló la guía o el contexto?
- ¿Hubo prompts repetitivos?

### Acciones de Mejora
1. **Actualizar reglas** (`.cursor/rules/`)
2. **Refinar plantillas** (`.raise/templates/`)
3. **Evolucionar agentes** (prompts, capacidades)
4. **Documentar aprendizajes**

---

*Esta metodología es un documento vivo. Evoluciona con cada retrospectiva y aprendizaje.*
