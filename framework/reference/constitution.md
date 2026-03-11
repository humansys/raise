# RaiSE Constitution

## Principios Inmutables para Reliable AI Software Engineering

**Versión:** 2.2.0
**Estado:** Ratificada
**Fecha:** 7 de Febrero, 2026

> **Nota de versión 2.0:** Esta enmienda incorpora el principio §8 (Observable Workflow) y alinea terminología con ontología v2.0. Ver changelog al final.

---

## Identidad

**RaiSE es** un sistema operativo metodológico para gobernar agentes de IA en el desarrollo de software empresarial. Es un framework de **Context Engineering** que aplica principios Lean al desarrollo AI-asistido.

**RaiSE NO es:**

- Un reemplazo del desarrollador humano
- Un IDE o editor de código
- Una herramienta de "vibe coding" acelerado
- Un vendor lock-in a plataformas específicas
- Prompt engineering superficial

---

## Principios Innegociables

### §1. Humanos Definen, Máquinas Ejecutan

Los humanos especifican el **"Qué"** en lenguaje natural (Markdown). Las máquinas reciben el **"Cómo"** en formato estructurado (JSON). La especificación es la fuente de verdad; el código es su expresión.

**Implicación práctica:** El rol del desarrollador evoluciona a **Orquestador**—quien diseña contexto, valida outputs, y mantiene ownership del sistema.

### §2. Governance as Code

Las políticas, guardrails y estándares son artefactos versionados en Git, no documentos estáticos en wikis olvidadas. Lo que no está en el repositorio, no existe.

**Jerarquía de Governance:**

```
Constitution (Principios inmutables)
    ↓
Guardrails (Directivas operacionales)
    ↓
Specs (Contratos de implementación)
    ↓
Validation Gates (Puntos de control)
```

### §3. Platform Agnosticism

RaiSE funciona donde funciona Git. No hay dependencia de GitHub, GitLab, Bitbucket, ni ningún proveedor específico. El protocolo Git es el transporte universal.

**Extensión MCP v2.0:** Adoptamos MCP (Model Context Protocol) como estándar de integración con agentes, pero sin lock-in—el fallback a archivos estáticos (.cursorrules, .claude.md) siempre existe.

### §4. Validation Gates en Cada Fase

No existe un solo "Done". Cada fase tiene su propia **Validation Gate** que debe cruzarse antes de avanzar. La calidad no es un evento final; es un proceso continuo.

**Los 8 Validation Gates estándar:**

| Gate           | Fase           | Criterio Core                       |
| -------------- | -------------- | ----------------------------------- |
| Gate-Context   | Discovery      | Stakeholders y restricciones claras |
| Gate-Discovery | Discovery      | PRD validado                        |
| Gate-Vision    | Vision         | Solution Vision aprobada            |
| Gate-Design    | Design         | Tech Design completo                |
| Gate-Backlog   | Planning       | HUs priorizadas                     |
| Gate-Plan      | Planning       | Implementation Plan verificado      |
| Gate-Code      | Implementation | Código que pasa validaciones       |
| Gate-Deploy    | Deployment     | Feature en producción              |

### §5. Heutagogía sobre Dependencia

El sistema no solo entrega el pescado, **enseña a pescar**. Al finalizar sesiones críticas, RaiSE desafía al humano para asegurar comprensión y ownership de la solución.

**Las 4 preguntas heutagógicas:**

1. ¿Qué aprendiste que no sabías antes?
2. ¿Qué cambiarías del proceso?
3. ¿Hay mejoras para el framework?
4. ¿En qué eres más capaz ahora?

### §6. Mejora Continua (Kaizen)

Si un prompt falló o el código requirió muchas iteraciones, los guardrails y katas se refinan. El sistema aprende de sus errores y mejora para la siguiente vez.

**Ciclo Kaizen en RaiSE:**

```
Implementar → Observar → Reflexionar → Mejorar → Implementar...
```

### §7. Lean Software Development

RaiSE aplica los principios del Toyota Production System al desarrollo asistido por IA:

| Principio Lean         | Manifestación en RaiSE           |
| ---------------------- | --------------------------------- |
| Eliminar desperdicio   | Context-first (no hallucinations) |
| Amplificar aprendizaje | Checkpoints heutagógicos         |
| Decidir tarde          | Specs antes de código            |
| Entregar rápido       | Validation Gates (no batch)       |
| Empoderar al equipo    | Modelo Orquestador                |
| Construir integridad   | Jidoka (parar en defectos)        |
| Ver el todo            | Golden Data coherente             |
| Genchi Genbutsu        | Antes de diseñar, ir al Gemba (código) |

> Para desarrollo completo de la filosofía de aprendizaje, ver [05-learning-philosophy-v2.md](./05-learning-philosophy-v2.md).

### §8. Observable Workflow

Cada decisión del agente debe ser **trazable y auditable**. No hay cajas negras. La observabilidad es prerequisito para mejora continua y compliance regulatorio.

**Componentes de Observable Workflow:**

| Pilar MELT        | Función en RaiSE                           |
| ----------------- | ------------------------------------------- |
| **Metrics** | Tokens, re-prompting rate, escalation rate  |
| **Events**  | Gates pasados/fallidos, escalaciones        |
| **Logs**    | Razonamiento del agente (cuando disponible) |
| **Traces**  | Flujo completo spec → plan → código      |

**Principio operativo:** Si no puedes auditar cómo se tomó una decisión, no puedes mejorarla ni defenderla ante reguladores.

**Almacenamiento:** Local (JSONL), privacy-first, compatible con OpenTelemetry para export.

> Este principio habilita compliance con EU AI Act y es fundamento para Kaizen basado en datos.

---

## Valores de Diseño

| Valor                    | Sobre          | Explicación                                        |
| ------------------------ | -------------- | --------------------------------------------------- |
| **Simplicidad**    | Completitud    | Preferir soluciones simples que cubran 80% de casos |
| **Composabilidad** | Monolitos      | Componentes pequeños que se combinan               |
| **Transparencia**  | Magia          | Todo debe ser inspeccionable y explicable           |
| **Convención**    | Configuración | Defaults sensatos, override cuando necesario        |
| **Evolución**     | Revolución    | Cambios incrementales sobre rewrites totales        |
| **Observabilidad** | Opacidad       | [NUEVO v2.0] Trazabilidad por defecto               |

---

## Restricciones Absolutas

### Nunca:

- Procesar código sin contexto estructurado previo
- Guardar secretos, tokens o PII en archivos de configuración
- Crear dependencia de APIs propietarias cuando existe alternativa Git-native
- Sacrificar trazabilidad por velocidad
- Generar código sin plan de implementación documentado
- **Ejecutar sin Observable Workflow activo** [NUEVO v2.0]
- **Ignorar Escalation Gates cuando el agente tiene baja confianza** [NUEVO v2.0]

### Siempre:

- Validar specs contra la constitution antes de planificar
- Documentar decisiones arquitectónicas (ADRs)
- Mantener backward compatibility en schemas
- Proveer escape hatches para usuarios avanzados
- Incluir atribución a proyectos upstream (MIT compliance)
- **Registrar trace de cada interacción MCP** [NUEVO v2.0]
- **Escalar al Orquestador ante ambigüedad** [NUEVO v2.0]
- **Dogfooding: cuando construyas RaiSE, sigue RaiSE** [NUEVO v2.1] — Saltarse el proceso = saltarse la validación = entregar metodología no probada
- **Genchi Genbutsu: antes de diseñar, ir al Gemba** [NUEVO v2.2] — Leer el código que se va a modificar. La documentación deriva; el código es la verdad. Diseñar desde observación, no desde memoria

---

## Compromisos con Stakeholders

### Con Desarrolladores (Orquestadores)

- Nunca aumentar fricción sin valor demostrable
- Respetar sus herramientas existentes (IDE, VCS, CI)
- Proveer feedback inmediato y accionable
- **Enseñar, no solo ejecutar** (Heutagogía)

### Con Organizaciones

- Ofrecer path claro de Community → Enterprise
- Mantener datos dentro de infraestructura del cliente (on-premise option)
- Soportar compliance frameworks estándar (SOC2, ISO 27001, EU AI Act)
- **Observable Workflow como evidencia de compliance** [NUEVO v2.0]

### Con la Comunidad Open Source

- Core siempre open source (MIT)
- Contribuciones upstream cuando sea apropiado
- Documentación pública y completa

### Con Reguladores

- Trazabilidad completa de decisiones AI
- Audit trails exportables
- Documentación de guardrails como controles

---

## Proceso de Enmienda

Esta Constitution puede ser modificada bajo las siguientes condiciones:

1. **Propuesta documentada** con rationale claro
2. **Período de revisión** de 7 días
3. **Aprobación** del Founder + consenso del Core Team
4. **Evaluación de impacto** en backward compatibility
5. **Comunicación** a la comunidad con changelog
6. **ADR asociado** para cambios significativos [NUEVO v2.0]

---

## Historial de Enmiendas

| Versión | Fecha      | Cambio                                  | ADR      |
| -------- | ---------- | --------------------------------------- | -------- |
| 1.0.0    | 2025-12-26 | Ratificación inicial                   | —       |
| 2.0.0    | 2025-12-28 | §4 renombrado: DoD → Validation Gates | ADR-006a |
| 2.0.0    | 2025-12-28 | §8 añadido: Observable Workflow       | ADR-008  |
| 2.0.0    | 2025-12-28 | Terminología: rules → guardrails      | ADR-007  |
| 2.0.0    | 2025-12-28 | Valor añadido: Observabilidad          | —       |
| 2.0.0    | 2025-12-28 | Restricciones Observable Workflow       | —       |
| 2.0.0    | 2025-12-28 | Compromisos con Reguladores             | —       |
| 2.1.0    | 2026-02-02 | Restricción añadida: Dogfooding        | —       |
| 2.2.0    | 2026-02-07 | §7 Lean: Genchi Genbutsu añadido       | —       |
| 2.2.0    | 2026-02-07 | Restricción: Ir al Gemba antes de diseñar | —   |

---

## Glosario de Términos Constitucionales

| Término                      | Definición                                  |
| ----------------------------- | -------------------------------------------- |
| **Orquestador**         | Humano que diseña contexto y valida outputs |
| **Guardrail**           | Directiva operacional enforceable            |
| **Validation Gate**     | Punto de control de calidad por fase         |
| **Escalation Gate**     | Trigger para intervención humana            |
| **Observable Workflow** | Sistema de trazabilidad de decisiones        |
| **Golden Data**         | Información verificada y canónica          |
| **Context Engineering** | Diseño del ambiente informacional del LLM   |
| **Genchi Genbutsu**     | "Ve y observa tú mismo" — leer el código antes de diseñar cambios |

> Para definiciones completas, ver [20-glossary-v2.md](./20-glossary-v2.md).

---

*"Los humanos definen el Qué en Markdown. Las máquinas reciben el Cómo en JSON. El protocolo Git es el transporte universal. Cada decisión es observable."*
