# Retrospective: RAISE-200 — /rai-problem-shape

## Summary
- **Story:** RAISE-200
- **Started:** 2026-02-19
- **Completed:** 2026-02-19
- **Size:** M
- **Estimated:** ~150 min (T1:30 + T2:30 + T3:60 + T4:15 + T5:15)
- **Actual:** ~90 min (puro Markdown — sin Python, sin tests de código)
- **Velocity factor:** ~1.67x (más rápido de lo esperado)

## Commits
- `44cf922` scope init
- `19ce3e4` design (3 decisiones interactivas)
- `a81374d` plan (5 tareas, dependencies)
- `215751c` T1: scaffold + Steps 0-2
- `0b59c99` T2+T3: Steps 3-7 + Problem Brief output
- `3623eb5` T4: /rai-epic-design Step 0.7
- `5a0c4d2` rename: problem-shape → rai-problem-shape

## What Went Well

- **Diseño interactivo funcionó**: Las 3 preguntas en rai-story-design alinearon decisiones clave (rai-cli gate, lite mode deferral, Step 0.7) antes de escribir una línea. Cero retrabajo de diseño.
- **Anti-solution gate**: El protocolo de desafío único quedó bien calibrado — curiosidad, no confrontación, con aceptación en segunda instancia + nota ⚠.
- **rai skill validate** detectó las secciones faltantes (Context + Output) en el primer intento — el ciclo detect→fix fue rápido.
- **Reflog recovery**: La branch ref perdida se recuperó limpiamente desde el reflog sin perder ningún commit.
- **Rename quirúrgico**: El rename de `problem-shape` → `rai-problem-shape` tocó exactamente los 3 lugares necesarios: directorio, frontmatter, y referencia en rai-epic-design.

## What Could Improve

- **Branch drift × 2**: El commit T1 cayó en v2 por error; después la branch ref desapareció. Dos incidentes de branch context en la misma sesión → PAT-E-371.
- **SKILL.md scaffold incompleto**: La primera escritura no incluyó Context ni Output — el validador los exigió → PAT-E-370.
- **`rai skill validate` sintaxis**: Se intentó `rai skill validate problem-shape` (falla) antes de descubrir que necesita path completo → PAT-E-369.

## Heutagogical Checkpoint

### ¿Qué aprendí?
- Que los skills de portafolio tienen un perfil de velocidad diferente al de código Python: más rápido de implementar (~1.67x), pero el riesgo de branch drift es mayor porque no hay red de seguridad de tests.
- Que el gate `rai session start --context` como inicio de un skill no-técnico es el patrón correcto: el stakeholder no necesita saber que hay un CLI detrás.
- Que el diseño interactivo (AskUserQuestion) tiene ROI claro en skills conversacionales — las 3 decisiones que se tomaron en design hubieran requerido retrabajo si se hubieran descubierto durante implement.

### ¿Qué cambiaría del proceso?
- Añadir `git branch --show-current` como check explícito en rai-story-implement Step 3 (antes de ejecutar cada tarea), especialmente para stories sin Python.
- El scaffold de un nuevo skill debería tener Context + Output como secciones obligatorias desde el template inicial (no descubrir el requerimiento por validación).

### ¿Hay mejoras para el framework?
- **PAT-E-369**: `rai skill validate` requiere path, no nombre.
- **PAT-E-370**: SKILL.md scaffold siempre incluye Context + Output desde el inicio.
- **PAT-E-371**: Verificar branch antes de cada commit en trabajo de contenido.
- **rai-story-implement**: Considerar añadir Step 2.5 "verify branch" para stories de contenido (SKILL.md, docs).

### ¿En qué soy más capaz ahora?
- Diseño de skills conversacionales con gates de validación epistemológica (anti-solution, 3 Whys).
- Integración entre skills en pipeline (output de uno → input de otro vía archivo).
- Recuperación de branches perdidas desde reflog.

## Improvements Applied

- **PAT-E-369** añadido: sintaxis correcta de `rai skill validate`
- **PAT-E-370** añadido: SKILL.md scaffold con Context + Output
- **PAT-E-371** añadido: verificar branch antes de commit en content work
- **Reinforcements**: PAT-E-151 ×1, PAT-E-154 ×1, PAT-E-183 ×1, PAT-E-186 ×1

## Action Items

- [ ] Añadir Step 2.5 "verify branch" en rai-story-implement para stories de contenido (backlog, baja prioridad)
- [ ] Actualizar scaffold template de nuevos skills (`.raise/templates/`) con secciones Context + Output precargadas — si existe el template
