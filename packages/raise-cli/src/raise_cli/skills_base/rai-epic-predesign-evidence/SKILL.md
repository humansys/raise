---
name: rai-epic-predesign-evidence
description: "PDCV evidence gathering: gemba walk + backlog scan → predesign.json + capability-map.md. Runs before epic design to prevent reimplementation."
model: sonnet

allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - "Bash(rai:*)"
  - "Bash(grep *)"
  - "Bash(find *)"
  - "Bash(vulture *)"
  - "Bash(sha256sum *)"
  - "Bash(git *)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - brief_md: file_path, required, previous_skill
    - epic_dir: string, required, config
    - jira_key: string, optional, argument
  raise.outputs: |
    - predesign_json: file_path, next_skill
    - capability_map_md: file_path, next_skill
---

## Purpose

Walk existing code and backlog for the epic's domain(s) BEFORE design starts. Produces `evidence/predesign.json` (machine-verifiable by `gate-predesign`) and `capability-map.md` (human-readable). Prevents reimplementation — 74.4% of RCAs trace to drift.

## Mastery Levels

- **Shu**: Explain each step, show what was found and why it matters.
- **Ha**: Batch obvious findings; expand only gaps and overlaps.
- **Ri**: Capability tables + gaps + predesign.json, minimal prose.

## Context

**When to use:** As `evidence` phase in `epic-design-pdcv` sub-pipeline, after `discovery` (graph build). **When to skip:** Epic brief doesn't touch existing code (pure greenfield — rare). **Protocol:** `references/gemba-protocol.md` v1.2.

## Steps

### 0. Portfolio grounding — fail-open

```bash
rai portfolio suggest "$JIRA_KEY" 2>/dev/null || true
```

Si produce output → usar `components_touched` como dominios primarios en Step 1 y orientar las queries de Step 6 con `change_mode`. Si no produce output → continuar sin contexto de portafolio — no bloquear.

### 1. Identify domains (§1.1)
Read brief.md. Extract primary domain + up to 3 secondary domains.
```bash
rai graph query "{primary_domain} {epic_name}" --types module --limit 20
find packages/ -type f -name "*.py" | xargs grep -l "{domain_keyword}" | head -30
```

### 2. Read entry points + call graph (§1.2–1.3)
For each entry point: read full file, note activation kind (`caller_required|http_route|decorator|registry`), run `vulture packages/{domain}/ --min-confidence 80` for zero-caller detection. Follow call graph one level for functions called by 3+ places.

### 3. Find incomplete work (§1.4)
```bash
vulture packages/{domain}/ --min-confidence 80
grep -rn "TODO\|FIXME\|RAISE-" packages/{domain}/ --include="*.py"
grep -n "pass$\|raise NotImplementedError" packages/{domain}/ -r
```
Filter vulture output against HTTP route decorators before recording GAPs.

### 4. Read domain ADRs (§1.5)
```bash
find governance/adrs/ -name "*.md" | xargs grep -l "{domain}" 2>/dev/null
```

### 5. Sufficiency gate (§1.6)
Answer all four or go back: capabilities exist? partial/broken? dead/stubs? ADRs + deferrals?

### 6. Semantic overlap discovery (§2.1–2.2)
Extract capability intents from brief. Per intent, 2+ query variants:
```bash
rai graph query "{intent_variant}" --types module --limit 5
```

### 7. Backlog scan (§2.3)
Run ≤5 JQL queries. Verify every cited Jira key.
```bash
rai backlog search 'project = RAISE AND summary ~ "{keyword}" AND status in ("In Progress", "Committed")' -n 10
rai backlog search 'project = RAISE AND summary ~ "{keyword}" AND status = Done AND updated >= -365d' -n 10
rai backlog search 'project = RAISE AND summary ~ "{keyword}" AND issuetype = Bug' -n 10
rai backlog get {KEY}
```

### 8. Classify + emit (§2.4–2.5)
Classify each hit: `reuse|extend|new|approved_overlap`. Write:
- `work/epics/{epic_dir}/evidence/predesign.json` — schema_version "2", registry_hash, graph_revision, source_commit, claims array with queries/hits/disposition/jira_refs
- `work/epics/{epic_dir}/capability-map.md` — Part 1 (gemba findings), Part 2 (backlog scan), Part 3 (scope validation if scope.md exists)

### 9. Emit outcome
```yaml
outcome:
  verdict: PASS
  route: standard
  blocked_reason: null
```
**STOP.** Return: predesign.json path, capability-map.md path, gap count, claim count.

## Output

| Item | Destination |
|------|-------------|
| `evidence/predesign.json` | `work/epics/{epic_dir}/evidence/` — consumed by `gate-predesign` |
| `capability-map.md` | `work/epics/{epic_dir}/` — consumed by `rai-epic-design` |

## Quality Checklist

- [ ] Every entry point module read in full (not excerpts)
- [ ] vulture ran for zero-caller detection (not grep alone)
- [ ] Semantic queries ran with 2+ variants per intent
- [ ] Every Jira key in evidence resolves via `rai backlog get`
- [ ] `disposition: new` has rejection reasons for all top-5 hits
- [ ] predesign.json is valid JSON with schema_version "2"
- [ ] capability-map.md has all 3 parts

## References

- Protocol: `references/gemba-protocol.md` (v1.2)
- Gate: `gate-predesign` (design→plan transition, replay verification)
- ADR: ADR-132 (Capability Registry schema)
- Validated example: RAISE-13995 capability map
