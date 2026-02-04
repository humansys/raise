# Gates

> Validation checkpoints that ensure quality

---

## What is a Gate?

A **gate** is a validation checkpoint that must pass before work proceeds to the next phase. Gates prevent defects from compounding by catching issues early.

```
   Work          Gate           Next Phase
────────────→ [Validation] ───────────────→
                  │
                  ↓ (if fails)
              Fix Issues
```

## Why Gates Matter

Without gates:
- Defects accumulate
- Late discovery = expensive fixes
- Quality is hoped for, not verified
- AI assistants may proceed with flawed work

With gates:
- Issues caught early
- Clear quality criteria
- Explicit checkpoints
- AI knows when to stop

## Gate Structure

Every gate has:

```markdown
# Gate: {Name}

## Criterios de Validación

### Obligatorios (Must Pass)
- [ ] Criterion 1
- [ ] Criterion 2

### Recomendados (Should Pass)
- [ ] Criterion 3

## Cómo Validar
Instructions for checking each criterion.

## Si Falla
What to do when the gate fails.
```

## Gate Types

### By Severity

| Type | Meaning | On Failure |
|------|---------|------------|
| **Blocking** | Cannot proceed | Must fix before continuing |
| **Warning** | Should fix | Document why proceeding anyway |
| **Info** | Awareness only | Note for future reference |

### By Work Cycle

| Gate | After | Validates |
|------|-------|-----------|
| `gate-discovery` | PRD creation | Requirements complete and clear |
| `gate-vision` | Vision document | Technical approach sound |
| `gate-design` | Technical design | Architecture viable |
| `gate-backlog` | Backlog creation | Stories well-formed |
| `gate-plan` | Implementation plan | Plan is executable |
| `gate-code` | Implementation | Code meets standards |

## Using Gates

### Automatic (with AI)

When running katas, gates are checked automatically:

```
AI: Completing project/design kata...

Running gate-design validation...
✓ C4 Context diagram present
✓ Container diagram present
✓ Data model documented
✗ API contracts incomplete

Gate FAILED. Fix API contracts before proceeding.
```

### Manual (as human)

1. Open the gate document (`.raise/gates/gate-{name}.md`)
2. Check each criterion
3. Mark pass/fail
4. Fix failures or document exceptions

## Gate Criteria Examples

### gate-vision

```markdown
### Obligatorios
- [ ] Problem statement is clear and specific
- [ ] Success metrics have numeric targets
- [ ] Scope (in/out) is explicitly defined
- [ ] Technical approach is justified
```

### gate-design

```markdown
### Obligatorios
- [ ] C4 Context diagram exists
- [ ] C4 Container diagram exists
- [ ] Data model documented
- [ ] API contracts specified
- [ ] Security considerations addressed
```

### gate-code

```markdown
### Obligatorios
- [ ] All tests pass
- [ ] Coverage ≥ threshold (per guardrails)
- [ ] No linting errors
- [ ] PR approved by required reviewers
```

## Gates and Guardrails

Gates **enforce** guardrails:

```
Guardrail (rule):          Gate (enforcement):
─────────────────          ──────────────────────
"MUST have ≥80%     →      gate-code checks coverage
 test coverage"            and blocks if <80%
```

## Handling Failures

When a gate fails:

1. **Identify** — Which criterion failed?
2. **Assess** — Is it fixable now or blocking?
3. **Fix** — Address the issue
4. **Re-validate** — Run gate again
5. **Document** — If exception needed, document why

---

## Key Takeaways

1. **Quality checkpoints** — Gates catch issues early
2. **Clear criteria** — Know exactly what must pass
3. **Blocking by default** — Must pass to proceed
4. **Enforce guardrails** — Gates make rules real

---

*Next: [Artifacts](./artifacts.md) | See also: [Guardrails in Governance](./governance.md)*
