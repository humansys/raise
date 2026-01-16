# RaiSE Product Vision
## Reliable AI Software Engineering Framework

**Versión:** 1.0.0  
**Fecha:** 26 de Diciembre, 2025  
**Estado:** Draft para validación

---

## Problema Central

### El Dolor
Los equipos de desarrollo adoptan herramientas de AI coding (Copilot, Cursor, Claude Code) sin governance. El resultado:

- **Inconsistencia**: Cada desarrollador usa AI de forma diferente, produciendo código heterogéneo
- **Alucinaciones no detectadas**: Sin validación estructurada, errores de AI llegan a producción
- **Pérdida de contexto**: Cada sesión con AI empieza de cero; no hay "memoria" organizacional
- **Atrofia cognitiva**: Desarrolladores aceptan código AI sin entenderlo
- **Compliance gaps**: Regulaciones como EU AI Act exigen trazabilidad que no existe

### Evidencia
- El mercado de AI Governance crece 35-50% CAGR, de $200M (2024) a $7B+ (2030)
- 84% de desarrolladores usan AI tools, pero satisfacción cayó a 60% por calidad inconsistente
- 77% de empresas iniciaron frameworks de AI governance; 90% de las que tienen deployments activos
- EU AI Act entra en vigor 2025, mandando trazabilidad y governance

---

## Solución Propuesta

**RaiSE** es un framework de governance-as-code que estructura el uso de AI en desarrollo de software.

### Cómo Funciona

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  raise-config   │───▶│   raise-kit     │───▶│   AI Agent      │
│  (Central Repo) │    │   (CLI Local)   │    │   (Copilot,     │
│                 │    │                 │    │    Cursor, etc) │
│  • Rules (.md)  │    │  • Hydrate      │    │                 │
│  • Katas        │    │  • Validate     │    │  • Contexto     │
│  • Templates    │    │  • Check DoD    │    │    Inyectado    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       Git                   Local                IDE/CLI
```

### Diferenciadores Clave

| Diferenciador | Descripción | Competidores sin esto |
|---------------|-------------|----------------------|
| **DoD Fractales** | Quality gates por fase, no solo al final | Spec Kit, OpenSpec, Kiro |
| **Katas Ejecutables** | Validaciones automáticas de specs y código | Todos |
| **Heutagogía** | Entrenamiento activo del desarrollador | Todos (focus en reemplazo) |
| **Git-Native** | Sin APIs propietarias; Git como transporte | Kiro (AWS), Tessl (SaaS) |
| **Platform Agnostic** | GitHub, GitLab, Bitbucket indistintamente | Copilot (GitHub), Kiro (AWS) |

---

## Propuesta de Valor Única (UVP)

> **"RaiSE convierte el caos del AI-assisted development en un proceso gobernable, trazable y que mejora continuamente—sin sacrificar la velocidad."**

### Value Props por Stakeholder

| Stakeholder | Value Prop |
|-------------|------------|
| **Developer** | "Mis herramientas AI producen código consistente con las reglas del proyecto" |
| **Tech Lead** | "Puedo gobernar cómo mi equipo usa AI sin micromanagement" |
| **VP Engineering** | "Tengo visibilidad y trazabilidad del AI usage para compliance" |
| **CISO** | "Las políticas de seguridad se aplican automáticamente al código AI-generated" |

---

## User Personas

### Persona A: "Elena, la Metodóloga"
**Rol:** Staff Engineer / Platform Architect  
**Contexto:** Empresa de 100+ developers, múltiples equipos  
**Goals:**
- Estandarizar prácticas de AI-assisted development
- Reducir inconsistencias entre equipos
- Preparar para auditorías de compliance

**Pain Points:**
- Cada equipo usa AI de forma diferente
- No hay forma de medir calidad del código AI-generated
- Regulaciones (EU AI Act) se acercan sin preparación

**Jobs-to-be-Done:**
- Definir reglas que todos los equipos sigan
- Distribuir actualizaciones sin fricción
- Validar cumplimiento automáticamente

### Persona B: "Devon, el Constructor"
**Rol:** Senior Developer  
**Contexto:** Trabaja en features con AI daily  
**Goals:**
- Entregar features rápido y con calidad
- No perder tiempo en setup y configuración
- Entender y poder mantener código AI-generated

**Pain Points:**
- AI genera código inconsistente con patrones del proyecto
- Tiene que "adivinar" qué contexto darle al AI
- A veces acepta código sin entenderlo completamente

**Jobs-to-be-Done:**
- Obtener contexto estructurado automáticamente
- Validar que su código cumple estándares
- Aprender de las decisiones que AI tomó

### Persona C: "Carlos, el Compliance Officer"
**Rol:** Security/Compliance Manager  
**Contexto:** Enterprise regulada (Fintech, Healthcare)  
**Goals:**
- Demostrar governance de AI a auditores
- Trazabilidad de qué código fue AI-generated
- Políticas aplicadas consistentemente

**Pain Points:**
- No sabe qué código es AI-generated
- No hay audit trail de decisiones AI
- Cada auditoría es un scramble

**Jobs-to-be-Done:**
- Generar reportes de compliance automáticos
- Tener audit logs de interacciones AI
- Demostrar políticas como código versionado

---

## Casos de Uso Primarios

### CU-1: Onboarding de Proyecto Existente
**Trigger:** Equipo quiere adoptar RaiSE en proyecto brownfield  
**Flow:**
1. `raise init` escanea el proyecto
2. Genera constitution basada en patrones detectados
3. Crea reglas iniciales respetando el legado
4. Developer usa `/raise.specify` para nueva feature

**Outcome:** Proyecto existente tiene governance sin rewrite

### CU-2: Governance Centralizada Multi-Proyecto
**Trigger:** Platform team quiere gobernar 50+ repos  
**Flow:**
1. Platform team mantiene `raise-config` central
2. Cada repo configura `RAISE_CONFIG_REPO_URL`
3. `raise hydrate` sincroniza reglas en cada repo
4. CI ejecuta `raise check` bloqueando non-compliance

**Outcome:** Una sola fuente de verdad para todos los proyectos

### CU-3: Desarrollo con DoD Fractales
**Trigger:** Developer comienza feature nueva  
**Flow:**
1. `/raise.specify` → Genera spec, valida DoD-Strategy
2. `/raise.plan` → Genera plan técnico, valida DoD-Design
3. `/raise.tasks` → Genera tareas, valida completitud
4. `/raise.implement` → Ejecuta tareas con validación continua
5. Kata final valida DoD-Code

**Outcome:** Cada fase tiene quality gate; problemas detectados temprano

### CU-4: Audit Trail para Compliance
**Trigger:** Auditor pregunta "¿cómo gobiernan AI?"  
**Flow:**
1. Mostrar `raise-config` con políticas versionadas en Git
2. Mostrar logs de `raise check` en CI
3. Mostrar reportes de katas ejecutadas
4. Demostrar trazabilidad prompt → spec → código

**Outcome:** Auditoría exitosa con evidencia concreta

---

## Anti-Casos de Uso

Lo que RaiSE **explícitamente NO hace**:

| Anti-Caso | Por qué no |
|-----------|------------|
| Reemplazar al developer | Heutagogía: empoderamos, no reemplazamos |
| Ser otro AI coding assistant | Somos governance layer, no generator |
| Funcionar solo con un IDE | Platform agnostic por principio |
| Requerir cloud/SaaS | Git-native, funciona 100% on-premise |
| Garantizar código sin bugs | Reducimos errores, no los eliminamos |

---

## Métricas de Éxito

### Métricas de Adopción

| Métrica | Baseline | Target Y1 | Target Y3 |
|---------|----------|-----------|-----------|
| Community users | 0 | 5,000 | 100,000 |
| Pro subscribers | 0 | 50 | 2,000 |
| Enterprise deals | 0 | 0 | 10 |
| GitHub stars | 0 | 5,000 | 25,000 |

### Métricas de Valor

| Métrica | Baseline | Target |
|---------|----------|--------|
| Tiempo promedio spec → código | Variable | -40% |
| Defectos post-release AI code | Variable | -50% |
| Auditorías sin hallazgos críticos | N/A | 100% |
| Adherencia a patrones definidos | N/A | >90% |

### Métricas de Engagement

| Métrica | Target |
|---------|--------|
| NPS (Pro/Enterprise) | >50 |
| Monthly active CLI users | >60% of installs |
| Community contributions | >50/quarter |

---

## Competitive Positioning

```
                    GOVERNANCE ENTERPRISE
                           ↑
                           |
    IBM Watson    ●        |        ◉ RaiSE
    Collibra      ●        |          (target position)
    OneTrust      ●        |
                           |
    ←─────────────────────────────────────────→
    DATA/MODEL             |            CODE/DEV
    FOCUSED                |            FOCUSED
                           |
    OpenSpec      ●        |        ● Cursor
    Spec Kit      ●        |        ● Copilot
    Kiro          ●        |
                           |
                           ↓
                    DEVELOPER TOOLS
```

### Competidores Directos

| Competidor | Fortaleza | Debilidad | Estrategia vs |
|------------|-----------|-----------|---------------|
| GitHub Spec Kit | 58k⭐, backing Microsoft | Experimental, sin governance | Diferenciación: DoD, Katas, Enterprise |
| AWS Kiro | Integración AWS | Vendor lock-in, overkill | Platform agnostic como ventaja |
| OpenSpec | Lightweight, TypeScript | Menos features | Más completo pero igual de simple |
| BMAD Method | Multi-agente robusto | Complejo, curva alta | Simplicidad + governance |

---

## Roadmap de Alto Nivel

### v0.1 - Foundation (Q1 2025)
- CLI básico (init, check, hydrate)
- Soporte 5 agentes principales
- Templates core
- Documentación

### v0.2 - Quality Gates (Q2 2025)
- DoD fractales completos
- Katas de validación
- raise-config centralizado
- Analytics básico

### v0.3 - Enterprise (Q3 2025)
- MCP Server para contexto unificado
- SSO/SAML integration
- Audit logging
- On-premise deployment guide

### v1.0 - Production (Q4 2025)
- Estabilidad API
- SOC2 Type I
- Integraciones Jira/Linear
- Marketplace de katas community

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| GitHub agrega governance a Spec Kit | Media | Alto | Diferenciación profunda en DoD/Heutagogía |
| Paradigma SDD no gana tracción | Baja | Alto | Pivote a governance puro |
| Competidor bien-fondeado entra | Media | Medio | First-mover en nicho específico |
| EU AI Act se diluye | Baja | Medio | Value prop existe sin regulación |

---

## Preguntas Abiertas

1. **Naming final**: ¿RaiSE es el nombre definitivo? (Trademark clearance pendiente)
2. **Pricing validation**: ¿$29/$49/custom es el punto correcto?
3. **First enterprise target**: ¿Qué vertical atacar primero?
4. **Community vs sales-led**: ¿Cuál es el GTM principal?

---

*Este documento es la fuente de verdad para decisiones de producto. Actualizar con cada pivote o aprendizaje significativo.*
