---
name: rai-architecture-review
description: Evaluate design proportionality using Beck's four rules. Use after implementation.
model: opus

allowed-tools:
  - Read
  - Grep
  - Glob

license: MIT

metadata:
  raise.work_cycle: story, epic
  raise.frequency: on-demand
  raise.prerequisites: story-implement (story scope), last story complete (epic scope)
  raise.version: "1.0.0"
  raise.visibility: public
---

# Architecture Review

## Purpose

Evaluate whether code is **necessary and proportional** using Beck's four rules of simple design. Core question: "Could we achieve the same outcome with less?"

## Mastery Levels (ShuHaRi)

- **Shu**: Apply all heuristics systematically, explain each finding
- **Ha**: Focus on highest-signal heuristics for the scope, skip low-risk areas
- **Ri**: Pattern-match to known anti-patterns, minimal ceremony

## Context

| Condition | Action |
|-----------|--------|
| After `/rai-story-implement` | Run with `story` scope |
| After last story in epic | Run with `epic` scope |
| After `/rai-bugfix-plan` | Run with `bugfix` scope — input is `analysis.md` + archivos en puntos de cambio (no git diff: no hay código escrito aún) |
| Accumulated complexity feels disproportionate | Run on-demand |

**Inputs:** Scope (`story`, `epic`, or `bugfix`), design doc, changed files from git diff (story/epic) or `analysis.md` + files at change points (bugfix).

## Steps

### Step 1: Load Design Context & Patterns

Before reviewing code, load what the design intended and what the codebase has learned:

1. **Code orientation**: Load SA-ranked code symbols for the current branch:
   ```bash
   rai session context -s code_context -p .
   ```
   Returns ~20 symbols ranked by structural proximity to active work modules. Empty result is valid. Use these as starting points — not exhaustive scope.
2. **Read the design doc** (`design.md` or `scope.md`) — what was the intended approach?
3. **Query the knowledge graph** for patterns in affected modules:

   Use `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, query="patterns for {affected_modules}".
   If MCP tools are not available, fall back to: `rai graph query "patterns for {affected_modules}" --types pattern`

   Use `raise_pattern_query` MCP tool with keywords="{module_keywords}", `cwd="{project_or_worktree_path}"`.
   If MCP tools are not available, fall back to: `rai pattern query --context "{module_keywords}"`
4. **Load established patterns** (PAT-E-*) — these are proven solutions. Deviations need justification.

> **JIT**: For deeper code exploration beyond the orientation map, query the graph directly:
> ```bash
> rai graph query "symbol_name" --types symbol --limit 10
> rai graph query "module_name" --module mod-session
> rai graph query "callers of function_name" --types symbol
> ```
> Use `--file path/to/file.py` to scope results to a specific file.

This context informs every subsequent step: you can't judge proportionality without knowing intent, and you can't catch regressions without knowing established patterns.

### Step 2: Identify Scope and Changed Files

Detect the project language and filter by appropriate extensions:

1. **Check `.raise/manifest.yaml`** for `project.language` or `project.project_type`
2. **Fallback:** Scan extensions of changed files and pick the dominant language

```bash
# Story scope: files changed vs parent branch
git diff --name-only $(git merge-base HEAD <parent-branch>)..HEAD -- '<extensions>'
# Epic scope: all files changed vs development branch
git diff --name-only $(git merge-base HEAD <dev-branch>)..HEAD -- '<extensions>'
# Bugfix scope: no git diff — read analysis.md to identify the files at change points
# then read those files directly
```

Replace `<extensions>` with language-appropriate patterns (e.g., `'*.py' '*.pyi'` for Python, `'*.ts' '*.tsx'` for TypeScript, `'*.cs'` for C#).

**Bugfix scope:** No code has been written yet. Load `work/bugs/{issue_key}/analysis.md`, extract the files identified as change points, and read them. The question is: "Is the proposed fix approach proportional to the problem?"

Read every changed file and the design doc. You cannot judge proportionality without intent context.

### Step 3: Necessity Audit (YAGNI — Beck Rule 4)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H1 | Single Implementation | Protocol/ABC with exactly one concrete implementation, no documented consumer |
| H2 | Wrapper Without Logic | Class delegates all work without adding behavior |
| H3 | Unused Parameters | Parameters accepted but never used in function body |
| H4 | Test-Only Consumers | Public function/class used exclusively by test code |
| H5 | Dead Exports | Public API includes names no consumer imports (e.g., `__all__` in Python, `export` in TS, `public` in C#) |

When a heuristic triggers, check: "Does the design doc justify this?" If yes, note as Observation.

### Step 4: Proportionality Audit (KISS — Beck Rules 2+4)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H6 | Indirection Depth | >2 layers of delegation for a simple operation |
| H7 | Abstraction-to-LOC Ratio | More scaffolding than logic |
| H8 | Configuration Over Convention | Configurable with only one valid value in practice |

### Step 5: Duplication & Responsibility (Beck Rules 2-3)

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H9 | Semantic Duplication | Same concept expressed differently in multiple places |
| H10 | Pattern Duplication | Same structural problem solved differently across modules |
| H11 | Change Reason Count | Module changes for >1 unrelated reason |
| H12 | Import Fan-In | File imports from 5+ distinct packages for one function |

### Step 6: Agent-Authored Drift Audit

```bash
# Re-read manifest vars (PAT-129)
_CFG=$(rai manifest env)
DRIFT_CATALOG=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('governance',{}).get('drift_catalog',''))")
DRIFT_HOTSPOTS=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('governance',{}).get('drift_hotspots',''))")

# tier-3: print top-10 hotspot module ranks for cross-reference with changed modules (skipped if key absent)
if [ -n "$DRIFT_HOTSPOTS" ]; then
  python3 -c "
import json
hs = json.load(open('$DRIFT_HOTSPOTS'))
for e in hs.get('ranked_modules', [])[:10]:
    print(f\"  rank={e['rank']} id={e['id']} signals={e.get('signal_count','?')}\")
" 2>/dev/null || echo '⚠ Could not read hotspots file'
fi
```

Check for agent-specific drift patterns at both story and epic scope. If `$DRIFT_CATALOG` is declared in manifest, reference it §1 for full definitions — do not copy inline. If absent, use the inline AG1–AG6 table below as the sole reference (tier-3: silent skip). If `$DRIFT_HOTSPOTS` output was printed above, note which changed modules (if any) match top-ranked entries.

| # | Heuristic | Signal |
|---|-----------|--------|
| AG1 | Authorization fan-out | Auth-related changes touching ≥3 downstream modules without a consolidating aggregator |
| AG2 | Clone amplification | Duplicate logic blocks in ≥2 new locations relative to surrounding modules |
| AG3 | Hallucinated-API residue | Symbol references that don't resolve; persistent across ≥2 commits |
| AG4 | Context-window planning | Fan-out of modified set has orphan edges — modules touched but not reconciled |
| AG5 | Vulnerability density | CWE-class patterns in agent-authored hunks (auth, injection, secrets) |
| AG6 | Over-specification | Conditionals keyed on literal constants from prompt examples; re-implementation of existing capability |

"No agent-authored drift detected" is always valid — do not invent findings.

**Migration integrity check** — runs once for every Alembic configuration whose
configured `script_location/versions/` contains a changed migration. Preserve
the changed-path → configuration association: hybrid repositories may require
more than one check.

```bash
BASE=$(git merge-base HEAD <parent-branch>)
mapfile -d '' CHANGED_FILES < <(git diff --name-only -z "$BASE"..HEAD)
declare -A VERIFIED_ROOTS=()

while IFS= read -r -d '' CONFIG; do
  CONFIG=${CONFIG#./}
  SCRIPT_ROOT=$(
    python3 - "$CONFIG" "$PWD" <<'PY'
from configparser import ConfigParser
from pathlib import Path
import sys

config = Path(sys.argv[1]).resolve()
repo = Path(sys.argv[2]).resolve()
parser = ConfigParser(defaults={"here": str(config.parent)})
parser.read(config, encoding="utf-8")
location = parser.get("alembic", "script_location", fallback="").strip()
if location and ":" not in location:
    root = Path(location)
    root = root if root.is_absolute() else config.parent / root
    try:
        print(root.resolve().relative_to(repo))
    except ValueError:
        pass
PY
  )
  [ -n "$SCRIPT_ROOT" ] || continue

  for CHANGED in "${CHANGED_FILES[@]}"; do
    case "$CHANGED" in
      "$SCRIPT_ROOT"/versions/*.py)
        CONFIG_DIR=$(dirname "$CONFIG")
        CONFIG_NAME=$(basename "$CONFIG")
        (cd "$CONFIG_DIR" && alembic -c "$CONFIG_NAME" heads)
        VERIFIED_ROOTS["$SCRIPT_ROOT"]=1
        break
        ;;
    esac
  done
done < <(find . -type f -name alembic.ini \
  -not -path './.git/*' -not -path './.venv/*' -print0)

# Any changed versions file not associated with a discovered configuration is
# an explicit unverified outcome, never a silent success.
for CHANGED in "${CHANGED_FILES[@]}"; do
  case "$CHANGED" in
    versions/*.py|*/versions/*.py)
      VERIFIED=0
      for SCRIPT_ROOT in "${!VERIFIED_ROOTS[@]}"; do
        case "$CHANGED" in
          "$SCRIPT_ROOT"/versions/*.py) VERIFIED=1; break ;;
        esac
      done
      if [ "$VERIFIED" -eq 0 ]; then
        echo "⚠ Migration '$CHANGED' changed but no applicable Alembic configuration was found; migration integrity cannot be verified."
      fi
      ;;
  esac
done
```

| Result | Action |
|--------|--------|
| 0 migration files changed | Skip silently |
| 1 head | ✓ Continue |
| >1 heads | **BLOCK** — create merge migration before proceeding |
| Changed migration has no applicable config | Record the warning in the review output; do not claim migration integrity was verified |

### Step 7: Portfolio Impact Check

Using the modules already identified in Step 6 drift analysis, cross-reference against the portfolio cartridge to detect concurrent initiatives that may conflict.

For each touched module, run:

```bash
rai graph context mod-{module} --format json 2>/dev/null || true
```

Extract the `portfolio_impact` field from the JSON output. Handle each case:

| Result | Action |
|--------|--------|
| `change_mode: breaking` initiative in same module | Add `## Portfolio Impact` section to AR report with severity **HIGH**; list initiative key, module, and nature of conflict |
| `change_mode: evolutionary` initiative in same module | Mention as informative context in the AR report; do NOT block |
| Command fails or returns no portfolio nodes | Print advisory: `portfolio cartridge no disponible — run \`rai portfolio cartridge generate\``; continue (fail-open, do NOT block the AR) |
| No concurrent initiatives | Note: "No concurrent portfolio initiatives detected" |

**Fail-open rule:** A missing or unavailable portfolio cartridge must never block the AR. This check is informative, not a gate.

### Step 8: Systemic Audit (Epic Scope Only)

Skip for story scope. Cross-module heuristics:

| # | Heuristic | Red Flag |
|---|-----------|----------|
| H13 | Orphaned Abstractions | Protocol from early story still has ≤1 implementor at epic end |
| H14 | Coupling Direction | Stable core imports from volatile/new module |
| H15 | Cyclic Dependencies | Circular import paths between modules |
| H16 | Shotgun Surgery | One logical change touches 5+ files across 3+ directories |

### Step 9: Lean Compliance Audit

Verify the implementation follows the lean principles established in design:

| # | Check | Red Flag |
|---|-------|----------|
| L1 | **MVP delivered** | Implementation exceeds what design specified — gold-plating |
| L2 | **Design followed** | Implementation diverges from design without documented ADR |
| L3 | **Pattern compliance** | Known patterns (PAT-E-*) exist for this problem but weren't used |
| L4 | **No speculative code** | Features built for hypothetical future requirements (YAGNI) |
| L5 | **Simplest approach** | A simpler implementation would achieve the same outcome (KISS) |

For each L-finding: cite the pattern or design decision that was violated.

### Step 10: Present Findings

```markdown
## Architecture Review: {id} (scope: {story|epic})

### Critical (fix before merge)
### Recommended (simplify before next cycle)
### Questions (require human judgment)
### Observations (patterns noted)
### Verdict
- [ ] PASS / PASS WITH QUESTIONS / SIMPLIFY
```

Every finding: specific file:line, heuristic ID, proportionality concern, concrete simplification.

<verification>
Verdict rendered (PASS / PASS WITH QUESTIONS / SIMPLIFY). All critical findings addressed or acknowledged by developer. Signal emitted.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Review findings | Presented inline, saved if requested |
| Verdict | PASS, PASS WITH QUESTIONS, or SIMPLIFY |
| Next | `/rai-story-review` (story) or `/rai-epic-close` (epic) |

## Quality Checklist

- [ ] Design doc and graph patterns loaded before reviewing (Step 1)
- [ ] Project language detected before filtering files
- [ ] All changed files for detected language read before reviewing
- [ ] Every finding cites specific file:line and heuristic ID (AG1-AG6, H1-H16, L1-L5)
- [ ] Portfolio Impact Check run; breaking conflicts flagged HIGH or cartridge advisory emitted (Step 7)
- [ ] Lean compliance verified: MVP, pattern adherence, no gold-plating
- [ ] Known patterns (PAT-E-*) checked against implementation
- [ ] Questions ratio >30% of findings (humility signal)
- [ ] "No issues found" is a valid outcome — do not invent findings

## References

- Evidence: `work/research/architecture-review/`
- Complements: `/rai-quality-review` (correctness), `/rai-story-review` (retrospective)
- Framework: Beck's Simple Design Rules, Fowler's Code Smells, Silva et al. (ESEM 2024)
