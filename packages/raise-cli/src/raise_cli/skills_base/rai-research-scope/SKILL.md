---
name: rai-research-scope
description: Decompose research question into 3-5 divergent search angles. Skipped for quick depth.
allowed-tools:
  - Read
  - Write
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Scope

## Purpose

Decompose the research question into 3-5 divergent search angles to prevent search bias from a single framing. Each angle produces independent queries that will fan out in the Search phase.

## Steps

### Step 1: Read Frame

Read `work/research/{topic}/frame.md` for question, secondary questions, and depth.

### Step 2: Generate Angles

Create 3-5 angles that approach the question from fundamentally different perspectives. Principles:
- **Diverge** — each angle must find sources the others wouldn't
- **Cover modalities** — mix: academic, practitioner, vendor, community, contrarian
- **Include a contrarian angle** — at least one angle that seeks disconfirming evidence

Example angles for "best observability framework for AI agents":
1. **Academic/standards** — IEEE, NIST, MLOps papers on agent observability
2. **Practitioner** — engineering blogs, production case studies, conference talks
3. **Vendor landscape** — commercial tools, feature matrices, pricing
4. **Community** — GitHub stars/issues, Reddit/HN discussions, adoption signals
5. **Contrarian** — "observability is overrated" or alternative approaches

### Step 3: Define Queries Per Angle

For each angle, write 2-4 specific search queries optimized for different tools:
- `tavily:` — natural language, detail-oriented
- `brave:` — keyword-focused, broad coverage
- `ddgr:` — quick validation queries

### Step 4: Write Scope Document

Write `work/research/{topic}/scope.md`:

```markdown
# Search Angles: {topic}

## Angle 1: {name}
Perspective: {what this angle seeks}
Queries:
- tavily: "{query}"
- brave: "{query}"
- ddgr: "{query}"

## Angle 2: {name}
...

## Angle N: {name} [CONTRARIAN]
...
```

### Step 5: Emit phase_result

```yaml
phase_result:
  status: done
  angle_count: {N}
  artifacts:
    - work/research/{topic}/scope.md
```

## Output

| Item | Destination |
|------|-------------|
| Scope with angles | `work/research/{topic}/scope.md` |
| Angle count | phase_result → Search phase scales fan-out |
