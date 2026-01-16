# Quickstart: Katas Ontology Normalization

**Feature**: 006-katas-normalization
**Purpose**: Step-by-step guide to normalize katas to ontology v2.1

---

## Prerequisites

Before starting normalization:

1. **Verify branch**: `git branch --show-current` → should be `006-katas-normalization`
2. **Verify katas exist**: `ls src/katas/{principios,flujo,patron}/` → 15 files total
3. **Access glossary**: `docs/framework/v2.1/model/20-glossary-v2.1.md`
4. **Access roadmap**: `specs/005-katas-ontology-audit/outputs/migration-roadmap.md`

---

## Normalization Workflow

### Step 1: Select Next Kata

Follow priority order from `plan.md` §Processing Priority:

```bash
# Current priority list (update as you complete each)
# 1. principios/00-raise-katas-documentation.md      ← START HERE
# 2. principios/01-raise-kata-execution-protocol.md
# 3. flujo/04-generacion-plan-implementacion-hu.md
# ... (see plan.md for full list)
```

**Verificación:** You have identified the next kata file to process.

> **Si no puedes continuar:** Priority list exhausted → All katas normalized; feature complete.

---

### Step 2: Read Kata Content

```bash
# Read the kata file
cat src/katas/principios/00-raise-katas-documentation.md
```

Identify:
- [ ] All step headers (look for `### Paso`, `### Step`, `##`, or bold numbering)
- [ ] Existing verification text (any format)
- [ ] Deprecated terminology (DoD, Developer, Rule, L0-L3)

**Verificación:** You understand the kata structure and can identify all steps.

> **Si no puedes continuar:** Kata has no clear steps → Flag for restructuring review.

---

### Step 3: Semantic Coherence Check

Compare kata content to its level's guiding question:

| Level | Expected Content Focus |
|-------|------------------------|
| `principios/` | Explains WHY or WHEN to do something |
| `flujo/` | Describes HOW workflows flow |
| `patron/` | Shows recurring structures/templates |

**Decision Point**:
- ✅ Content aligns → Proceed to Step 4
- ❌ Content misaligns → **STOP** and flag for reclassification

**Verificación:** Kata content primarily answers its level's guiding question.

> **Si no puedes continuar:** Content answers wrong level's question → Create issue in `outputs/flagged-misalignment.md` with kata path and recommended level.

---

### Step 4: Add Jidoka Inline Structure

For EACH step in the kata, ensure this format:

```markdown
### Paso N: [Acción]

[Existing instructions - preserve verbatim]

**Verificación:** [How to know the step succeeded]

> **Si no puedes continuar:** [Failure cause] → [Resolution action]
```

**Guidelines for verification text**:
- Observable outcome (can see/measure result)
- Specific to the step's action
- Written as statement, not question

**Guidelines for correction text**:
- Format: `[Causa] → [Resolución]`
- Most common failure mode for this step
- Actionable resolution

**Verificación:** Every step has both `**Verificación:**` and `> **Si no puedes continuar:**`.

> **Si no puedes continuar:** Can't determine appropriate verification → Review similar steps in glossary examples or ask Orquestador for guidance.

---

### Step 5: Replace Deprecated Terminology

Search and replace (with context awareness):

| Find | Replace With | Context Check |
|------|--------------|---------------|
| `DoD` | `Validation Gate` | Always replace |
| `Developer` | `Orquestador` | Only when referring to human role |
| `Rule` | `Guardrail` | Only when referring to governance |
| `L0` | `principios` | Only when referring to kata level |
| `L1` | `flujo` | Only when referring to kata level |
| `L2` | `patrón` | Only when referring to kata level |
| `L3` | `técnica` | Only when referring to kata level |

**Preserve**: Terms in code examples, proper nouns, or non-governance contexts.

**Verificación:** `grep -E 'DoD|Developer|Rule|L[0-3]' <kata-file>` returns no matches (or only preserved contexts).

> **Si no puedes continuar:** Term appears in ambiguous context → Preserve original with inline clarification note.

---

### Step 6: Generate Normalization Report

Create report in `specs/006-katas-normalization/outputs/`:

```bash
# Create report file
touch specs/006-katas-normalization/outputs/report-<level>-<number>.md
```

Report template:
```markdown
# Normalization Report: <kata-path>

**Processed**: <date>
**Coherence**: aligned

## Jidoka Inline Changes

| Step | Verification Added | Correction Added |
|------|--------------------|------------------|
| 1    | ✅                 | ✅               |

## Terminology Changes

| Line | Before | After |
|------|--------|-------|
| (none) | - | - |

## Notes

<any observations or edge cases encountered>
```

**Verificación:** Report file exists and contains all change details.

> **Si no puedes continuar:** Unable to write file → Check directory permissions.

---

### Step 7: Present for Validation

Present the normalized kata and report to the Orquestador.

**Validation options**:
- **Approve** → Commit changes, proceed to next kata
- **Request changes** → Adjust based on feedback, re-present
- **Skip** → Move to next kata without changes (document reason)

```bash
# After approval, commit with descriptive message
git add src/katas/<level>/<kata-file>.md
git add specs/006-katas-normalization/outputs/report-<level>-<number>.md
git commit -m "feat(kata): Normalize <kata-name> to ontology v2.1

- Add Jidoka Inline structure to N steps
- Replace M deprecated terms
- Verified semantic coherence with <level> level"
```

**Verificación:** Orquestador has reviewed and approved (or provided feedback).

> **Si no puedes continuar:** Orquestador unavailable → Queue kata for later review; document pending status.

---

### Step 8: Proceed to Next Kata

Update priority list in `plan.md` (mark completed) and return to Step 1.

**Verificación:** Priority list updated; next kata identified.

> **Si no puedes continuar:** All 15 katas processed → Feature complete; run `/speckit.analyze` for final validation.

---

## Quick Reference

### Jidoka Inline Format

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

### Terminology Cheatsheet

```
DoD           → Validation Gate
Developer     → Orquestador (when human role)
Rule          → Guardrail (when governance)
L0/L1/L2/L3   → principios/flujo/patrón/técnica
```

### Level Guiding Questions

```
principios  → ¿Por qué? ¿Cuándo?
flujo       → ¿Cómo fluye?
patrón      → ¿Qué forma?
técnica     → ¿Cómo hacer?
```

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Kata has no clear steps | Flag for restructuring in separate issue |
| Deprecated term in code block | Preserve - only replace prose |
| Content misaligns with level | Stop, flag for reclassification |
| Verification text unclear | Review similar katas for examples |
| Orquestador rejects normalization | Apply feedback, re-submit |
