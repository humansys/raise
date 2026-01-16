# Quickstart: Crear Glosario Mínimo (Seed)

**Feature**: 002-glossary-seed
**Date**: 2026-01-11
**Estimated Time**: 30-45 minutos

## Prerequisites

- [x] spec.md completado y validado
- [x] plan.md generado
- [x] research.md con decisiones de diseño
- [x] data-model.md con estructura del documento
- [ ] Acceso a `docs/framework/v2.1/model/20-glossary-v2.1.md` (glosario canónico)
- [ ] Acceso a `specs/001-heutagogy-progressive-disclosure/learning-path.md` (Stage 0 concepts)

## Execution Steps

### Step 1: Preparar Referencias

```bash
# Abrir documentos de referencia
cat docs/framework/v2.1/model/20-glossary-v2.1.md | grep -A10 "Orquestador\|Spec\|Agent\|Validation Gate\|Constitution"

# Abrir learning-path.md para confirmar 5 conceptos
cat specs/001-heutagogy-progressive-disclosure/learning-path.md | grep -A5 "Stage 0"
```

**Output esperado**: Definiciones canónicas de los 5 conceptos

---

### Step 2: Crear Archivo Seed

```bash
# Crear archivo en la ubicación correcta
touch docs/framework/v2.1/model/20a-glossary-seed.md
```

**Validation**: Verificar que el archivo se creó en la ruta correcta

---

### Step 3: Escribir Contenido del Glosario Seed

Usar el template de `data-model.md` y llenar cada sección:

1. **Introducción** (50 palabras)
   - Explicar por qué existe este glosario mínimo
   - Mencionar que cubre Stage 0 (5 conceptos esenciales)

2. **Para cada concepto** (100 palabras máx.):
   - Copiar término canónico del glosario v2.1
   - Escribir interfaz simple (<10 palabras)
   - Agregar 1-2 oraciones de contexto
   - Incluir ejemplo concreto del flujo spec-kit

3. **Cierre** (50 palabras)
   - Enlace al glosario completo v2.1
   - Invitación a profundizar cuando esté listo

**Tip**: Usar ejemplos de research.md como guía

---

### Step 4: Validar Longitud

```bash
# Contar palabras
wc -w docs/framework/v2.1/model/20a-glossary-seed.md

# Debe estar entre 400-600
```

**Expected**: Número entre 400 y 600

**Si excede 600**: Reducir detalles en secciones individuales
**Si es menor a 400**: Agregar ejemplos más descriptivos

---

### Step 5: Validar Terminología (Gate-Terminología)

```bash
# Verificar que no hay términos contradictorios
diff <(grep -oE '\b[A-Z][a-z]+\b' docs/framework/v2.1/model/20a-glossary-seed.md | sort -u) \
     <(grep -oE '\b[A-Z][a-z]+\b' docs/framework/v2.1/model/20-glossary-v2.1.md | sort -u)
```

**Manual check**:
- [ ] Orquestador (no Developer, no Orchestrator)
- [ ] Validation Gate (no DoD, no Definition of Done)
- [ ] Guardrail (no Rule) — si se menciona

---

### Step 6: Validar Coherencia (Gate-Coherencia)

**Manual review**:
- [ ] Comparar cada definición del seed con glosario v2.1 completo
- [ ] Verificar que no hay contradicciones
- [ ] Confirmar que ejemplos son consistentes con workflow spec-kit

**Cross-check**: Leer `docs/framework/v2.1/model/00-constitution-v2.md` para validar principios mencionados

---

### Step 7: Validar Success Criteria

| SC | Criterion | Verification Command | Expected |
|----|-----------|---------------------|----------|
| SC-001 | 5 secciones | `grep -c "^## " docs/framework/v2.1/model/20a-glossary-seed.md` | 5 |
| SC-002 | 400-600 palabras | `wc -w docs/framework/v2.1/model/20a-glossary-seed.md` | 400-600 |
| SC-003 | Ejemplos presentes | `grep -c "\*\*Ejemplo\*\*:" docs/framework/v2.1/model/20a-glossary-seed.md` | 5 |

**Gate**: Si algún SC falla, corregir antes de continuar

---

### Step 8: Commit

```bash
git add docs/framework/v2.1/model/20a-glossary-seed.md
git commit -m "feat: Add glossary seed for Stage 0 onboarding

Create 20a-glossary-seed.md with 5 essential concepts:
- Orquestador, Spec, Agent, Validation Gate, Constitution
- 400-600 words, simplified language
- Concrete examples from spec-kit workflow

Implements QW-03 from feature 001 improvement proposals.
Reduces onboarding complexity by 10% (35 → 5 concepts).

Success Criteria:
- SC-001: 5 sections ✅
- SC-002: 400-600 words ✅
- SC-003: 5 examples ✅
- SC-004: Canonical terminology ✅
- SC-005: Gates pass ✅
- SC-006: <5min reading time ✅

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Troubleshooting

### Issue: Longitud excede 600 palabras

**Solution**:
- Reducir ejemplos a 1-2 líneas
- Simplificar detalle mínimo a 1 oración por concepto

### Issue: Ejemplos no son concretos

**Solution**:
- Usar comandos específicos: `/speckit.specify`, `/speckit.plan`
- Referenciar archivos reales: `spec.md`, `CLAUDE.md`

### Issue: Terminología no coincide con glosario v2.1

**Solution**:
- Copiar literalmente el término del glosario v2.1
- No usar sinónimos o traducciones alternativas

---

## Expected Output

**File**: `docs/framework/v2.1/model/20a-glossary-seed.md`
**Size**: 400-600 palabras
**Sections**: 5 (Orquestador, Spec, Agent, Validation Gate, Constitution)
**Validation**: ✅ Gate-Terminología, ✅ Gate-Coherencia

---

*Quickstart completado. Proceder a /speckit.tasks para generar tareas atómicas.*
