# RaiSE Commons - Guía de Desarrollo

## Identidad del Proyecto

**raise-commons** es el repositorio de trabajo conceptual y ontológico del framework RaiSE (Reliable AI Software Engineering). El trabajo principal consiste en:

- Documentación del modelo ontológico
- Validación de coherencia semántica entre artefactos
- Evolución controlada de la terminología canónica
- Mantenimiento de ADRs y decisiones arquitectónicas

**Este NO es un repositorio de código de producción.** Es el "cerebro" del framework donde se define el "qué" y el "por qué".

## Plataforma y Branching

- **Git Platform**: GitLab (`gitlab.com:humansys-demos/product/raise1/raise-commons`)
- **CLI Tool**: `glab` (GitLab CLI v1.36.0+)
- **Branch Base**: `PRAISE-36-ontology-standarization` (para features de estandarización ontológica)
- **Target para MRs**: `PRAISE-36-ontology-standarization`
- **Configuración**: `.specify/config.json`

**Nota**: Este proyecto usa GitLab, no GitHub. Todos los comandos de creación de MRs usan `glab`, no `gh`.

### ⚠️ IMPORTANTE: Antes de Crear Features

**SIEMPRE verifica que estás en la branch base correcta antes de `/speckit.specify`**:

```bash
# 1. Ir a la branch base
git checkout PRAISE-36-ontology-standarization

# 2. Actualizar con cambios remotos
git pull origin PRAISE-36-ontology-standarization

# 3. Ahora sí, crear el feature
/speckit.specify <descripción>
```

El script `create-new-feature.sh` crea la nueva branch **desde donde estés actualmente**, por eso es crítico estar en la branch base correcta.

## Agente Activo: RaiSE Ontology Architect

Este proyecto utiliza el agente **RaiSE Ontology Architect** como sparring partner intelectual. El agente:

- Evalúa propuestas contra la estructura ontológica
- Aplica auditoría Lean (Muda, Mura, Muri)
- Verifica coherencia semántica con el glosario v2.1
- Facilita el aprendizaje auto-dirigido del Orquestador (Heutagogía)

**Prompt del agente:** `.raise/agents/raise-ontology-arch-agent/raise-ontology-architect-opus45.md`

## Fuentes de Verdad (Golden Data)

| Prioridad | Documento | Propósito |
|-----------|-----------|-----------|
| 1 | `.specify/memory/constitution.md` | Principios spec-kit |
| 2 | `docs/framework/v2.1/model/00-constitution-v2.md` | Constitution RaiSE completa |
| 3 | `docs/framework/v2.1/model/20-glossary-v2.1.md` | Terminología canónica |
| 4 | `docs/framework/v2.1/model/21-methodology-v2.md` | Metodología |
| 5 | `docs/framework/v2.1/adrs/*.md` | Decisiones arquitectónicas |

## Terminología Canónica (v2.1)

| Término Deprecated | Término Canónico |
|--------------------|------------------|
| DoD | Validation Gate |
| Rule | Guardrail |
| Developer | Orquestador |
| Kata levels L0-L3 | Principio/Flujo/Patrón/Técnica |

**Enforcement:** Cualquier uso de terminología deprecated debe corregirse citando el glosario.

## Validation Gates para Este Repositorio

| Gate | Criterio |
|------|----------|
| Gate-Terminología | Términos sin ambigüedad, alineados con glosario |
| Gate-Coherencia | Sin contradicciones con ontología existente |
| Gate-Trazabilidad | Cambios documentados con rationale (ADRs) |
| Gate-Estructura | Templates con secciones requeridas |

## Comandos Disponibles (spec-kit)

| Comando | Uso |
|---------|-----|
| `/speckit.specify` | Crear especificación de feature |
| `/speckit.plan` | Generar plan de implementación |
| `/speckit.tasks` | Generar lista de tareas |
| `/speckit.analyze` | Validar coherencia ontológica |
| `/speckit.constitution` | Actualizar constitution |
| `/speckit.clarify` | Clarificar requisitos ambiguos |

## Principios de Trabajo

### Heutagogía (Aprendizaje Auto-Dirigido)
El Orquestador dirige su propio proceso de aprendizaje. El agente facilita proporcionando contexto, explicando el "por qué", y señalando recursos - pero no "enseña" ni dicta el camino.

### Jidoka (Parar en Defectos)
Si se detecta incoherencia semántica o violación de principios: **STOP**. No continuar acumulando errores. Ciclo: Detectar → Parar → Corregir → Continuar.

### Governance as Code
Todo lo que no está en Git, no existe oficialmente. Políticas, decisiones y estándares son artefactos versionados.

### Simplicidad sobre Completitud
Preferir documentación concisa que cubra 80% de casos. Evitar abstracciones prematuras. YAGNI aplicado a la ontología.

## Estructura del Repositorio

```
raise-commons/
├── CLAUDE.md                    # Este archivo
├── .claude/commands/            # Comandos spec-kit
├── .specify/
│   ├── memory/constitution.md   # Constitution spec-kit
│   └── templates/               # Templates de artefactos
├── .raise/agents/               # Prompts de agentes
├── docs/
│   ├── framework/v2.1/          # Modelo ontológico actual
│   │   ├── model/               # Documentos core
│   │   ├── adrs/                # Decisiones arquitectónicas
│   │   └── katas/               # Ejercicios y validaciones
│   ├── research/                # Investigación
│   └── archive/                 # Versiones anteriores
└── README.md
```

## Workflow Típico

### Workflow Conceptual

1. **Propuesta** → Articular cambio o adición a la ontología
2. **Análisis Ontológico** → Verificar coherencia con modelo existente
3. **Auditoría Lean** → Identificar desperdicio potencial
4. **Validation Gate** → Pasar Gate-Coherencia y Gate-Terminología
5. **Documentación** → Actualizar artefactos afectados
6. **ADR** (si aplica) → Documentar decisión significativa

### Workflow Técnico con spec-kit + GitLab

1. **Crear Feature Branch** (desde `PRAISE-36-ontology-standarization`)
   ```bash
   /speckit.specify <descripción del feature>
   # Esto crea branch 00N-<short-name> automáticamente
   ```

2. **Desarrollar Feature**
   ```bash
   /speckit.plan      # Generar plan
   /speckit.tasks     # Generar tareas
   /speckit.implement # Ejecutar implementación
   /speckit.analyze   # Validar coherencia
   ```

3. **Commit y Push**
   ```bash
   git add .
   git commit -m "..."
   git push origin 00N-<feature-name>
   ```

4. **Crear Merge Request**
   ```bash
   glab mr create \
     --title "Feature 00N: <título>" \
     --description "<resumen>" \
     --source-branch 00N-<feature-name> \
     --target-branch PRAISE-36-ontology-standarization \
     --label "ontology,spec-kit"
   ```

   **O crear manualmente en GitLab UI** y copiar el link que aparece después del push.

5. **Mergear y Continuar**
   ```bash
   # Después de aprobación/merge
   git checkout PRAISE-36-ontology-standarization
   git pull
   # Continuar con siguiente feature
   ```

---

*Constitution: `.specify/memory/constitution.md` v1.0.0*

## Active Technologies
- Markdown (CommonMark spec) + Text editor, Git 2.0+ (003-simplify-jidoka, 004-operation-layers)
- Git version control (plain text markdown files)
- Git repository (versioned Markdown and JSON files) (005-katas-ontology-audit)
- Git repository (versioned Markdown files) (006-katas-normalization)
- Markdown (CommonMark spec) + Git 2.0+, GitLab (platform) (007-public-repo-readiness)

## Recent Changes
- 004-operation-layers: Documento `26-work-cycles-v2.1.md` formalizando los 4 ciclos de trabajo; entrada Work Cycle en glosario
- 003-simplify-jidoka: Added Markdown (CommonMark spec) + Text editor, Git 2.0+
