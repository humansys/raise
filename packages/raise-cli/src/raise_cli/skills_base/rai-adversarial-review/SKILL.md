---
name: rai-adversarial-review
description: Bounded single-shot adversarial red-team of an analysis or design result — fresh context attacks the findings, verifies evidence against code/state, returns holds/weak/wrong + what's missing. Use after any research/analysis/design phase, before acting on it.
model: fable

allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.prerequisites: an analysis/design artifact to review (path)
  raise.version: "1.0.0"
  raise.visibility: public
---

## Purpose

Falsify an analysis before it drives action. A **fresh-context** reviewer attacks the
findings of a research/analysis/design artifact, **spot-checks the cited evidence against
the actual code/DB/state**, and returns a per-claim verdict (`holds`/`weak`/`wrong`) plus
what the analysis missed. Single-shot and bounded — cheap in steps, spends inference only
where an adversarial lens pays (SOP `dev/sops/using-fable-5.md` §6; PAT-E-9552). Not a
research loop: it reviews a result, it does not re-derive it.

## Mastery Levels (ShuHaRi)

- **Shu**: Walk each claim; explain each verdict and the spot-check that grounds it.
- **Ha**: Batch obvious `holds`; expand only `weak`/`wrong` and the blind-spot.
- **Ri**: Verdict table + blind-spot + overreach, minimal prose.

## Context

**When to use:** After a research/analysis/design phase (spike research, architecture
proposal, audit report) — before committing to its conclusions.

**When to skip:** Reviewing code changes (use `rai-quality-review`) or design
proportionality (use `rai-architecture-review`). This skill reviews *conclusions*, not diffs.

**Inputs:** `artifact` (path to the analysis/design doc). Optional: `rubric` (what to attack
hardest) and `sources` (paths/DB the claims cite, so verification is cheap).

## Steps

### Step 0: Portfolio context — fail-open (si $JIRA_KEY disponible)

```bash
rai portfolio suggest "$JIRA_KEY" 2>/dev/null || true
```

Si produce output → usar `components_touched` para verificar si los módulos citados en el artifact coinciden con el perfil de portfolio (desalineación = candidato a `weak`/`wrong`). Usar `change_mode` para calibrar intensidad: `breaking` → escrutinio alto en contratos públicos; `evolutionary` → contexto normal. Si `$JIRA_KEY` no está disponible o no produce output → continuar sin contexto de portafolio — no bloquear.

### Step 1: Load target + extract claims
Read the `artifact`. Enumerate its load-bearing claims/findings (the ones action depends on).
Ignore prose; target assertions with consequences.

### Step 2: Attack each claim (default to skepticism)
For every load-bearing claim, try to **refute** it. Where it cites evidence (a path+symbol,
a DB row, a count, an ADR), **verify that citation yourself** with Read/Grep/Bash before
agreeing — reproduce the number, open the file at the line, run the query. Only mark `holds`
when the evidence checks out against reality. Do not be agreeable; a plausible-but-unverified
claim is `weak`, not `holds`.

```bash
# Example spot-checks (adapt to the artifact's citations)
grep -n "<cited symbol>" <cited path>
sqlite3 ~/.rai/raise.db "SELECT count(*) FROM <cited table> WHERE <cited predicate>"
```

### Step 3: Hunt the blind-spot and overreach
- **Missing:** what did every finding assume in common (groupthink), or which modality/claim
  went unverified? Name it.
- **Overreach:** does a recommendation discard a real constraint for elegance? Name the
  baby-with-bathwater risk.

### Step 4: Return the verdict (schema, JSON only)
Return **ONLY** the JSON below — no prose, no preamble. Provide justification **only** in the
`critique`/`evidence`/`fix` fields (typed content). **Never** reproduce, echo, or narrate your
internal reasoning as response text — that is content vs. transcription, and transcription
requests trigger a refusal/fallback (SOP §4).

```json
{
  "confidence": "one line: how trustworthy is the artifact, with the biggest remaining unknown",
  "claims": [
    {"target": "claim by title/id", "verdict": "holds|weak|wrong",
     "critique": "the attack", "evidence": "what you checked and found", "fix": "how to correct/strengthen"}
  ],
  "blind_spot": "what all findings share as an unstated assumption, or what went unverified",
  "overreach": "a real constraint discarded for elegance, or 'none'"
}
```

## Output

| Item | Destination |
|------|-------------|
| Adversarial verdict (JSON) | Returned to the caller; caller persists next to the artifact (e.g. `<artifact>.redteam.json`) |
| Model | `fable` (frontmatter) — override per-project via `.raise/skill_models.yaml` |

### Persistence of multi-model adversarial reviews

When running adversarial reviews across multiple models (e.g. Fable + Kimi K3 + Codex Sol),
persist all artifacts under the epic that invoked them:

```
work/epics/e{N}-{slug}/
  └── adversarial-reviews/
      └── <topic>/
          ├── prompt.md          # The review brief sent to all models
          ├── fable.md           # Fable review
          ├── kimi-k3.md         # Kimi K3 review
          ├── codex-sol.md       # Codex Sol review
          └── synthesis.md       # Optional: consolidated findings
```

These are decision-support artifacts — they document the adversarial reasoning behind
product and design choices. Persist them in the work context that invoked them, not in
the session scratchpad or in `dev/docs/`.

## Quality Checklist

- [ ] Every load-bearing claim has a verdict grounded in a spot-check, not deference
- [ ] Cited numbers/paths reproduced against real code/DB before any `holds`
- [ ] Blind-spot and overreach both stated (or explicitly "none")
- [ ] Output is JSON only; no "show your reasoning" instruction anywhere
- [ ] Reviewed the result, did not re-run the research

## References

- SOP: `dev/sops/using-fable-5.md` (§4 gotchas, §6 adversarial framing)
- Pattern: PAT-E-9552 (gather cheap → one Fable shot)
- Sibling reviews: `rai-architecture-review` (proportionality), `rai-quality-review` (diffs)
