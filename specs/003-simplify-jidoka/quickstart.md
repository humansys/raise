# Quickstart: Simplificar Jidoka

**Feature**: 003-simplify-jidoka
**Date**: 2026-01-11
**Estimated Time**: 30-45 minutos

## Prerequisites

- [x] spec.md completado y validado
- [x] plan.md generado
- [x] research.md con decisiones de diseño
- [x] data-model.md con estructura del entry
- [ ] Acceso a `docs/framework/v2.1/model/20-glossary-v2.1.md`
- [ ] Acceso a `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`
- [ ] Editor de texto configurado

## Execution Steps

### Step 1: Leer Entrada Actual de Jidoka

```bash
# Leer el glosario v2.1 completo
cat docs/framework/v2.1/model/20-glossary-v2.1.md | grep -A20 "^### Jidoka"
```

**Output esperado**: Definición actual de Jidoka (probablemente incluye ciclo de 4 pasos desde el inicio)

**Action**: Tomar nota de la estructura actual para comparar después

---

### Step 2: Buscar Referencias a Jidoka en Ontology Bundle

```bash
# Buscar todas las menciones de Jidoka
grep -n "Jidoka\|jidoka" docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
```

**Output esperado**: Lista de números de línea donde aparece Jidoka

**Action**: Identificar cuáles referencias están en secciones Stage 0-1 vs Stage 3 (usar contexto del documento)

---

### Step 3: Actualizar Entrada del Glosario

**Usar el template de data-model.md**:

1. Abrir `docs/framework/v2.1/model/20-glossary-v2.1.md`
2. Localizar la entrada `### Jidoka`
3. Reemplazar con estructura staged:

```markdown
### Jidoka

**Interfaz Simple (Stage 0-1)**: Parar si algo falla

Principio de detener el trabajo cuando detectas un problema, en lugar de acumular errores.

**Ejemplo**: Cuando ejecutas `/speckit.plan` y el gate de coherencia falla, el workflow para - no continúa generando tareas sobre una base inconsistente.

---

**Detalle Avanzado (Stage 3)**:

Jidoka (自働化) — Automatización con toque humano.

**Ciclo formal**:
1. **Detectar**: Identificar el defecto o anomalía
2. **Parar**: Detener el proceso inmediatamente
3. **Corregir**: Resolver la causa raíz
4. **Continuar**: Reanudar con mejora preventiva

**Contexto histórico**: Originado en telares automáticos de Sakichi Toyoda (1896), aplicado a manufactura por Taiichi Ohno en el Toyota Production System.
```

**Validation**: Verificar que el separador `---` esté presente para delimitar secciones

---

### Step 4: Validar Definición Simplificada (SC-001, SC-002)

```bash
# SC-001: Verificar que interfaz simple ≤10 palabras
echo "Parar si algo falla" | wc -w
# Expect: 4

# SC-002: Verificar CERO términos TPS en Stage 0-1
sed -n '/^### Jidoka$/,/^---$/p' docs/framework/v2.1/model/20-glossary-v2.1.md \
  | grep -iE "TPS|Toyota|Lean|自働化"
# Expect: 0 matches (empty output)
```

**Expected**: Primera comando retorna `4`, segundo comando no retorna nada (0 matches)

**If fails**: Revisar la sección Stage 0-1 y eliminar cualquier término prohibido

---

### Step 5: Actualizar Ontology Bundle

**Para cada referencia identificada en Step 2**:

1. Determinar si la sección es Stage 0-1 o Stage 3:
   - **Stage 0-1**: Introduction, Core Principles (§1-§8), Workflow Phases
   - **Stage 3**: MCP Integration, Ng Patterns, Advanced Topics

2. **Si es Stage 0-1**, usar referencia simplificada:
   ```markdown
   Aplicamos "Parar si algo falla" (Jidoka) en cada fase. Ver [glosario](./20-glossary-v2.1.md#jidoka).
   ```

3. **Si es Stage 3**, puede usar referencia formal:
   ```markdown
   El ciclo Jidoka (Detectar → Parar → Corregir → Continuar) se aplica aquí. Ver [glosario detallado](./20-glossary-v2.1.md#jidoka).
   ```

**Tip**: No todas las referencias necesitan el ciclo completo - usar juicio según contexto

---

### Step 6: Validar Consistencia Entre Documentos

```bash
# Verificar que ambos documentos usan terminología consistente
diff \
  <(grep -i "jidoka" docs/framework/v2.1/model/20-glossary-v2.1.md | head -5) \
  <(grep -i "jidoka" docs/framework/v2.1/model/25-ontology-bundle-v2_1.md | head -5)
```

**Expected**: Diferencias mínimas (solo contexto), pero términos clave idénticos

**Manual check**:
- [ ] Glossary tiene sección Stage 0-1 y Stage 3
- [ ] Ontology bundle usa versión apropiada según sección
- [ ] No hay contradicciones entre definiciones

---

### Step 7: Validar Gate-Terminología

```bash
# Verificar que "Jidoka" es el único término canónico (sin aliases)
grep -E "### Jidoka|Jidoka-simple|Jidoka-avanzado" docs/framework/v2.1/model/20-glossary-v2.1.md
```

**Expected**: Solo `### Jidoka` (una línea)

**Manual check**:
- [ ] Término "Jidoka" preservado (no renombrado)
- [ ] Sin nuevos aliases creados
- [ ] Entrada sigue estructura del glosario

---

### Step 8: Validar Gate-Coherencia

**Manual review**:

1. **Comparar Stage 0-1 vs Stage 3**: ¿La definición simplificada contradice la formal?
   - Expected: NO - "Parar si algo falla" es un subset del ciclo de 4 pasos

2. **Verificar alineación con Constitution §4** (Validation Gates):
   - Expected: Jidoka soporta el concepto de gates (parar ante problemas)

3. **Verificar alineación con Constitution §8** (Simplicidad):
   - Expected: Versión simplificada reduce complejidad sin perder esencia

**Cross-check**: Leer ambas secciones en voz alta - ¿suenan coherentes?

---

### Step 9: Verificar Success Criteria Completos

| Criterio | Validación | Comando/Check | Resultado Esperado |
|----------|------------|---------------|---------------------|
| SC-001 | Palabras ≤10 | `echo "Parar si algo falla" \| wc -w` | 4 |
| SC-002 | Cero TPS en 0-1 | `sed/.../grep TPS` (Step 4) | 0 matches |
| SC-003 | Gate-Term | Paso 7 manual | ✅ PASS |
| SC-004 | Gate-Coh | Paso 8 manual | ✅ PASS |
| SC-005 | 5% reducción | Prerequisitos: 1→0 (TPS eliminado) | ✅ PASS |
| SC-006 | <30s lectura | 4 palabras @ 200wpm ≈ 11s | ✅ PASS |

**Gate**: Si algún SC falla, corregir antes de continuar al commit

---

### Step 10: Commit Cambios

```bash
git add docs/framework/v2.1/model/20-glossary-v2.1.md \
        docs/framework/v2.1/model/25-ontology-bundle-v2_1.md

git commit -m "$(cat <<'EOF'
feat: Simplify Jidoka presentation for Stage 0-1

Apply ADR-009 (Simple Interface + Internal Philosophy) pattern to Jidoka:
- Stage 0-1: "Parar si algo falla" (4 words, no TPS prereqs)
- Stage 3: Formal 4-step cycle (Detectar → Parar → Corregir → Continuar)

Eliminates barriers B-01 (terminological) and B-02 (Lean/TPS cluster).
Reduces onboarding complexity by 5%.

Success Criteria:
- SC-001: Simplified definition ≤10 words ✅ (4 words)
- SC-002: Zero TPS terms in Stage 0-1 ✅
- SC-003: Gate-Terminología ✅
- SC-004: Gate-Coherencia ✅
- SC-005: 5% complexity reduction ✅
- SC-006: <30s comprehension ✅

Implements QW-01 from Feature 001 improvement proposals.

Files modified:
- docs/framework/v2.1/model/20-glossary-v2.1.md
- docs/framework/v2.1/model/25-ontology-bundle-v2_1.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Troubleshooting

### Issue: Grep encuentra "TPS" en Stage 0-1

**Solution**:
- Revisar la sección Stage 0-1 manualmente
- Mover cualquier mención de TPS, Toyota, Lean, o 自働化 a la sección "Contexto histórico" dentro de Stage 3

---

### Issue: Definición simplificada no captura la esencia

**Solution**:
- Revisar decision D2 en research.md
- Alternativas: "Detener trabajo ante problemas" o "Parar cuando detectas errores"
- Validar con Constitution §8 (Simplicidad)

---

### Issue: Ontology bundle tiene muchas referencias inconsistentes

**Solution**:
- Priorizar secciones de alta visibilidad (Introduction, Core Principles)
- Para secciones Stage 3, mantener referencias existentes si ya son formales
- Documentar cambios no realizados en commit message (out of scope)

---

## Expected Output

**Files Modified**:
- `docs/framework/v2.1/model/20-glossary-v2.1.md` (entrada Jidoka restructurada)
- `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md` (referencias actualizadas)

**Validation**: ✅ Gate-Terminología, ✅ Gate-Coherencia

**Commit**: Feature 003 branch con 1 commit descriptivo

---

*Quickstart completado. Proceder a /speckit.tasks para generar tareas atómicas.*
