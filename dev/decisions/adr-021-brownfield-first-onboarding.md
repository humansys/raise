# ADR-021: Brownfield-First Onboarding with Personal Memory

> **Status:** ACCEPTED
> **Date:** 2026-02-04
> **Decision Makers:** Emilio, Rai
> **Informs:** E7 Onboarding
> **Revision:** v2 - Added personal memory and adaptive interaction

---

## Context

We're designing the onboarding experience for F&F users (Feb 9 target). Our research identified two key insights:

1. **Target users have existing codebases** — F&F are experienced developers with brownfield projects, not greenfield.

2. **"Reliable" requires understanding** — For Rai to work reliably on an existing codebase, it must understand established conventions before making changes. Otherwise we're just "fast AI coding" not "reliable AI engineering."

### The Problem

Original E7 design (v1) focused on quick setup:
```
raise onboard → CLAUDE.md + skills → /session-start
```

This works for greenfield but fails brownfield because:
- Rai doesn't know existing conventions
- No guardrails prevent inconsistent code
- User must manually document everything
- First session risks introducing inconsistencies

### Competitor Analysis

| Tool | Approach | Gap |
|------|----------|-----|
| Aider | Auto repo-map (tree-sitter + PageRank) | Context only, no governance |
| Cursor | Auto-index on open | Context only, no rules |
| Windsurf | Auto-scan + parallel analysis | Context only, no rules |
| Claude Code | /init generates CLAUDE.md | Template-based, not detected |

**Competitors provide context but not governance.** RaiSE differentiator: we generate rules from what we find.

---

## Decision

**Default to full discovery + convention detection for brownfield projects.**

### `raise init` Behavior

```
raise init
    │
    ├── Detect: Greenfield or Brownfield?
    │   (brownfield if: >10 source files OR recognized project structure)
    │
    ├── If BROWNFIELD:
    │   ├── Run component discovery (reuse E13)
    │   ├── Detect conventions (indentation, naming, structure)
    │   ├── Detect architecture patterns (repository, service, etc.)
    │   ├── Generate governance/solution/guardrails.md
    │   ├── Generate enhanced CLAUDE.md
    │   └── Copy skills
    │
    └── If GREENFIELD:
        ├── Generate minimal CLAUDE.md
        └── Copy skills
```

### What Gets Generated (Brownfield)

**governance/solution/guardrails.md:**
- Code style rules (from detected patterns)
- Architecture patterns (from structure analysis)
- Testing conventions (from test discovery)
- Confidence scores for each rule

**CLAUDE.md:**
- Architecture overview
- Directory structure
- Key components
- Commands (from pyproject.toml, Makefile)
- Reference to guardrails

---

## Rationale

### Why Brownfield-First

1. **F&F reality:** Our F&F users have existing projects. Greenfield is secondary.

2. **Trust building:** First impression matters. If Rai violates conventions on day one, users won't trust "reliable."

3. **Hidden value:** Many teams have undocumented conventions. We surface them.

### Why Auto-Generated Governance

1. **Lower friction than manual:** Users don't have to document conventions themselves.

2. **Consistent format:** Generated guardrails follow our schema.

3. **Reviewable:** Users can edit/reject detected rules.

4. **Git-tracked:** Conventions become versioned artifacts.

### Why Not Interactive Wizard

Competitor research (RES-ONBOARD-DX-001) showed:
- 5/6 tools use config files, not wizards
- OpenClaw wizard exists because multi-channel requires choices
- We're Claude Code only — no choices needed, infer everything

---

## Alternatives Considered

### Alternative A: Minimal Setup (Original v1)

```
raise onboard → CLAUDE.md + skills → done
```

**Pros:**
- Fastest setup (~30s)
- Simplest implementation

**Cons:**
- No convention understanding
- User must document manually
- First session risks

**Rejected because:** Doesn't fulfill "reliable" promise for brownfield.

### Alternative B: Interactive Wizard

```
raise init
? Project name: my-api
? Primary language: Python
? Framework: FastAPI
? Testing framework: pytest
...
```

**Pros:**
- User confirms each choice
- No detection errors possible

**Cons:**
- Friction (10+ questions)
- Competitor research shows this isn't preferred
- We can detect most answers anyway

**Rejected because:** Research showed users prefer auto-detection over questionnaires.

### Alternative C: Discovery as Separate Step

```
raise init              # Minimal setup
raise discover          # Explicit discovery step
raise generate-rules    # Generate governance
```

**Pros:**
- User controls each step
- Can skip discovery if not wanted

**Cons:**
- More commands to learn
- Users might skip discovery, defeating purpose
- Extra friction

**Rejected because:** For brownfield, discovery should be default, not opt-in.

---

## Consequences

### Positive

- Rai understands codebase from first session
- Conventions documented (even if team never did)
- "Reliable" is demonstrated, not just claimed
- Differentiator vs competitors (governance, not just context)
- Foundation for future drift detection

### Negative

- Longer init time for brownfield (~2-5 min vs ~30s)
- More code to build (convention detection is new)
- Detection accuracy won't be 100%
- Risk of noisy guardrails if detection is too aggressive

### Neutral

- Greenfield experience unchanged (fast, minimal)
- `--quick` flag provides escape hatch
- Users can edit generated files

---

## Implementation Notes

### Reuse from E13

- Component extraction: `discover/extraction.py`
- Symbol parsing: tree-sitter integration
- Tech stack detection: framework detection logic

### New Modules

- `onboarding/detector.py` — Greenfield/brownfield detection
- `onboarding/conventions.py` — Convention detection (indentation, naming, patterns)
- `onboarding/generator.py` — Artifact generation

### Confidence Scoring

Each detected rule includes confidence:
- **HIGH (>90%):** Strong pattern, consistent across codebase
- **MEDIUM (70-90%):** Clear pattern, some exceptions
- **LOW (<70%):** Weak signal, user should verify

All rules included in guardrails.md with confidence tags. User reviews and adjusts.

---

## Validation Plan

1. **Test on raise-commons itself** — Does it detect our conventions correctly?
2. **Test on 2-3 F&F projects** — Before release, validate on real brownfield
3. **User feedback** — Ask F&F: "Were the generated guardrails useful?"

---

## Decision 2: Personal Memory (Added v2)

### Context

Rai is about to meet multiple developers (F&F). Each relationship should be personal:
- Experience level varies (Emilio: Ri, Fer: Shu)
- Communication preferences differ
- Skill mastery grows over time

Without personal memory, every project starts cold — experienced users get beginner explanations.

### Decision

**Implement `~/.rai/developer.yaml` for cross-project developer memory.**

```yaml
# ~/.rai/developer.yaml
name: Fer
experience_level: shu        # shu | ha | ri
communication:
  style: explanatory         # explanatory | balanced | direct
skills_mastered: []
universal_patterns: []
sessions_total: 1
```

### Rationale

1. **Separation of concerns:**
   - Project memory (`.rai/`) = conventions, components, calibration
   - Personal memory (`~/.rai/`) = relationship, experience, preferences

2. **Adaptive interaction:**
   - Shu users get full explanations
   - Ri users get efficient, minimal interaction
   - Skills mastered → less explanation needed

3. **Relationship continuity:**
   - Rai "knows" the developer across projects
   - Experience grows over time
   - Universal patterns apply everywhere

### Consequences

**Positive:**
- Experienced users don't re-learn basics
- New users get proper education
- Relationship feels personal, not transactional

**Negative:**
- Two memory locations to manage
- Migration needed for existing users (Emilio)
- Privacy considerations (user data in home directory)

**Neutral:**
- File is user-visible and editable
- Can be deleted to "reset" relationship

---

## Decision 3: Onboarding as Education (Added v2)

### Context

F&F users need to understand RaiSE, not just use it. The setup process is their first encounter with the methodology.

### Decision

**The onboarding process teaches RaiSE concepts, not just configures files.**

For Shu users, explain:
1. The RaiSE Triad (human intuition + AI execution)
2. Why conventions matter (reliability, not just speed)
3. What guardrails are (our contract)
4. How memory works (project vs personal)

For Ha/Ri users, be efficient but still explain new concepts.

### Rationale

1. **Understanding builds trust** — Users who understand "why" trust the "what"
2. **First impression matters** — Confused first session → abandoned tool
3. **Heutagogía principle** — Teach to fish, don't just deliver fish

### Consequences

**Positive:**
- F&F users become advocates (they understand the value)
- Fewer support questions ("why did Rai do X?")
- Alignment between methodology and practice

**Negative:**
- Longer first session for Shu users (~10 min vs ~2 min)
- More content to maintain (explanations)

---

## References

- E7 Scope v2: `dev/epic-e7-scope-v2.md`
- Competitor Research: `work/research/onboarding-dx-competitors/`
- OpenClaw Research: `work/research/openclaw-onboarding/`
- E13 Discovery: `dev/epic-e13-scope.md`

---

*ADR-021 | Proposed: 2026-02-04*
