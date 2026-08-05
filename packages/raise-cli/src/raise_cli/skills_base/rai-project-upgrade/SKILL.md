---
name: rai-project-upgrade
description: Upgrade a RaiSE project from an older version (e.g. v2.4) to the current version. Detects version, scaffolds missing structure, migrates data.
model: sonnet

allowed-tools:
  - Read
  - Bash
  - Write
  - Edit

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: "existing .raise/ directory"
  raise.next: "rai-session-start"
  raise.gate: "version detection + migration verification"
  raise.adaptable: "true"
  raise.version: "3.1.0"
  raise.inputs: |
    - project_path: path, required, argument
  raise.outputs: |
    - upgraded project with manifest, config, SQLite DB
  raise.visibility: public
---

# Project Upgrade

## Purpose

Detect a RaiSE project's current version and upgrade it to v3.1.x.
Handles the full path from v2.4 (YAML/JSONL, no manifest) through v3.0
to current. Conversational — explains what will change, asks before
destructive operations.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain each phase, show before/after, confirm each step
- **Ha**: Show summary, confirm once, execute
- **Ri**: Detect, report plan in one line, execute, report result

## Context

**When to use:** Project has `.raise/` but is on an older RaiSE version.

**When to skip:** Project already on current version. Greenfield → `rai init`.

## Steps

### Step 1: Detect current version

Run detection from the target project directory:

```bash
cd {project_path}

# Version markers
HAS_MANIFEST=$([[ -f .raise/manifest.yaml ]] && echo "yes" || echo "no")
HAS_CONFIG=$([[ -f .raise/config.toml ]] && echo "yes" || echo "no")
HAS_DB=$([[ -f .raise/rai/raise.db ]] && echo "yes" || echo "no")
HAS_GLOBAL_DB=$(ls ~/.rai/raise.db 2>/dev/null && echo "yes" || echo "no")

# Legacy data markers (v2.4)
HAS_SESSION_STATE=$([[ -f .raise/rai/personal/session-state.yaml ]] && echo "yes" || echo "no")
HAS_JSONL_SESSIONS=$(find .raise/rai/personal/sessions -name "*.jsonl" 2>/dev/null | head -1)
HAS_JSONL_SIGNALS=$(find .raise/rai/personal/telemetry -name "*.jsonl" 2>/dev/null | head -1)
HAS_PATTERNS=$([[ -f .raise/rai/memory/patterns.jsonl ]] && echo "yes" || echo "no")

# Old structure markers
HAS_AGENTS_DIR=$([[ -d .raise/agents ]] && echo "yes" || echo "no")
HAS_KATAS_DIR=$([[ -d .raise/katas ]] && echo "yes" || echo "no")
HAS_TEMPLATES_DIR=$([[ -d .raise/templates ]] && echo "yes" || echo "no")
```

Classify:

| Condition | Version | Upgrade path |
|-----------|---------|-------------|
| No manifest, no config, has JSONL/YAML personal data | **v2.4.x** | Full upgrade (scaffold + migrate) |
| No manifest, no config, agents/katas dirs only | **v2.x (minimal)** | Scaffold only |
| Has manifest, no config | **v3.0.x early** | Partial upgrade |
| Has manifest + config, no DB | **v3.0.x** | Data migration only |
| Has manifest + config + DB | **v3.1.x (current)** | Already current — report and exit |

Present the diagnosis to the developer:

```
## Version Detection: {project_name}

**Detected version:** {version}
**Upgrade path:** {description}

### What will happen:
1. {step description}
2. {step description}
...

### What will NOT be touched:
- Original files renamed to .migrated (not deleted)
- Source code unchanged
- Git history preserved
```

**Shu/Ha**: Wait for developer confirmation before proceeding.
**Ri**: Proceed immediately unless destructive operation detected.

### Step 2: Scaffold v3.x structure

Only if manifest is missing. Run from the target project directory:

```bash
cd {project_path}
rai init --detect --force
```

`--force` is needed because `.raise/` already exists.
`--detect` auto-detects installed agents.

Verify:

```bash
[[ -f .raise/manifest.yaml ]] && echo "MANIFEST OK" || echo "MANIFEST FAIL"
[[ -f .raise/config.toml ]] && echo "CONFIG OK" || echo "CONFIG FAIL"
```

If init fails, present the error and stop.

### Step 3: Migrate personal data

Only if legacy JSONL/YAML files exist. Run from the target project directory:

```bash
cd {project_path}
rai db migrate
```

This triggers `migrate_if_needed()` which:
- Converts `session-state.yaml` → SQLite `sessions` table
- Converts `sessions/index.jsonl` → SQLite `sessions` table
- Converts `sessions/*/journal.jsonl` → SQLite `journal_entries` table
- Converts `telemetry/signals.jsonl` → SQLite `signals` table
- Converts `pipeline/runs/*.json` → SQLite `pipeline_runs` table
- Converts `missions/*.yaml` → SQLite `missions` table
- Renames originals to `.migrated`

Capture and report the migration result.

### Step 4: Verify

```bash
cd {project_path}

# Structure check
echo "=== Structure ==="
[[ -f .raise/manifest.yaml ]] && echo "✓ manifest.yaml" || echo "✗ manifest.yaml"
[[ -f .raise/config.toml ]] && echo "✓ config.toml" || echo "✗ config.toml"

# DB check
echo "=== Database ==="
if [[ -f ~/.rai/raise.db ]]; then
  echo "✓ Global DB exists"
  sqlite3 ~/.rai/raise.db "SELECT COUNT(*) FROM sessions WHERE project_id LIKE '%{project_slug}%';" 2>/dev/null && echo "  Sessions migrated" || echo "  No sessions found"
fi

# Legacy files check
echo "=== Legacy files ==="
find .raise/rai/personal -name "*.migrated" 2>/dev/null | while read f; do
  echo "  ✓ $f (archived)"
done

# Remaining legacy (not migrated)
REMAINING=$(find .raise/rai/personal -name "*.yaml" -o -name "*.jsonl" 2>/dev/null | grep -v ".migrated" | head -5)
if [[ -n "$REMAINING" ]]; then
  echo "  ⚠ Remaining legacy files:"
  echo "$REMAINING"
fi
```

### Step 5: Discover & build governance cartridge from repo docs

Many clients arrive with their OWN governance documents — far more than the
templates RaiSE scaffolds. This phase turns those existing documents into a
Knowledge Cartridge so the client's governance becomes queryable knowledge,
not just files. The extraction engine already exists; this skill only
orchestrates discovery → init → build → review → extract.

**Skip this phase if:** the project has no governance documents beyond the
empty RaiSE templates, OR a `governance` cartridge already exists with a
populated `extractors/config.yaml`.

#### 5a. Discover candidate documents (no LLM, cheap)

```bash
cd {project_path}

echo "=== Candidate governance documents ==="
# Prune vendored + agent-tooling dirs at ANY depth (node_modules can be nested,
# e.g. api/node_modules/), then match real doc locations by path prefix.
# NOTE: do NOT use a loose substring match like grep 'docs/' — it false-matches
# agent skill dirs such as rai-epic-docs/. Anchor the location prefixes.
classify_doc() {
  f="$1"
  LINES=$(grep -cvE '^\s*$' "$f" 2>/dev/null || echo 0)
  if grep -qE 'fill with /rai-project-(create|onboard)' "$f" 2>/dev/null && [ "$LINES" -lt 60 ]; then
    echo "  (skip RaiSE template) $f"
  else
    echo "  $f  [$LINES lines]"
  fi
}

# (a) Current-layout docs at the project root.
find . \( -name node_modules -o -name .venv -o -name .git \
       -o -name .raise -o -name .claude -o -name .hermes -o -name .agent \
       -o -name .roo -o -name .windsurf -o -name .cursor -o -name .github \) -prune \
  -o -type f -name "*.md" -print 2>/dev/null \
| grep -E "^\./(governance|docs|architecture|work/docs)/" \
| while read -r f; do classify_doc "$f"; done

# (b) v2.x LEGACY location: docs lived INSIDE .raise/docs/ (not at the root).
# A v2.x→v3.1 upgrade MUST scan here — these are the client's richest docs
# (PRD, SOW, tech design, vision) and the root-level scan above prunes .raise.
# Verified in SP-project-upgrade gemba against 49bis (6.2k lines under .raise/docs/).
if [ -d .raise/docs ]; then
  echo "  --- legacy v2.x docs (.raise/docs/) ---"
  find .raise/docs -type f -name "*.md" 2>/dev/null \
    | while read -r f; do classify_doc "$f"; done
fi
```

Watch for accidental duplicates in legacy doc dirs (e.g. `... copy.md`) —
flag them to the developer rather than ingesting both.

Present the discovered documents to the developer, grouped by location. This
is a **HITL gate** — building a cartridge invokes the LLM (cost). Confirm the
corpus selection before proceeding.

**Shu/Ha/Ri all pause here** — LLM cost + schema quality justify a human
glance even at Ri level.

#### 5b. Scaffold the cartridge

Create one cartridge from the confirmed document set. Pass each confirmed doc
(or its glob) as a `--corpus` path:

```bash
cd {project_path}
rai cartridge init {project_slug}-governance \
  -c "governance/*.md" \
  -c "governance/architecture/*.md" \
  -c "docs/*.md" \
  -c "governance/adrs/*.md" \
  # ...one -c per confirmed source glob...
```

**Two post-init fixes are REQUIRED** (verified against a real client repo —
la-aldea-erp). `rai cartridge init` leaves the manifest in a state that fails
`build`:

1. **Corpus paths are resolved relative to the cartridge directory**
   (`.raise/cartridges/{name}/`), NOT the project root. The init command
   stores the `-c` paths verbatim, so `build` then reports
   *"No files matched corpus patterns"*. Prefix every corpus glob with
   `../../../` to climb back to the project root:

   ```bash
   # In .raise/cartridges/{project_slug}-governance/CARTRIDGE.yaml,
   # each corpus entry  `- governance/*.md`  becomes  `- ../../../governance/*.md`
   ```

2. **Schema is scaffolded as `TODO`.** Set it to the canonical graph node so
   build/extract can construct nodes:

   ```yaml
   schema:
     module: raise_core.graph.models
     class_name: GraphNode
   ```

> These two are product papercuts in `rai cartridge init` (see Known Issues).
> Until fixed upstream, the skill performs both edits before `build`.

#### 5c. Build seed schema (LLM)

```bash
cd {project_path}
rai cartridge build {project_slug}-governance
```

This analyzes the corpus and generates `extractors/config.yaml` +
`extractors/schemas/relationships.yaml` with proposed node/relationship types.

**Present the proposed schema to the developer** (node types, relationship
types, competency questions). Let them adjust before extracting — this is the
quality loop that `rai-kc-build` enforces and we honor here.

#### 5d. Extract instances

After schema confirmation:

```bash
cd {project_path}
rai cartridge extract {project_slug}-governance --embed
```

Report the extraction summary: nodes created, by type, any warnings.

<verification>
`rai cartridge list` shows `{project_slug}-governance` with instances.
`.raise/cartridges/{project_slug}-governance/instances/*.json` populated.
</verification>

### Step 6: Summary

```
## Upgrade Complete: {project_name}

**From:** v{detected_version}
**To:** v3.1.x

### Changes:
- {what was scaffolded}
- {what was migrated}
- {files archived as .migrated}
- Governance cartridge: {N} nodes from {M} documents (or "skipped — no client docs")

### Next steps:
1. Run `/rai-session-start` to begin working
2. Review `.raise/manifest.yaml` for project settings
3. Query your governance with: rai cartridge query {project_slug}-governance "..."
4. Consider `/rai-project-onboard` for full governance authoring
```

## Output

| Item | Destination |
|------|-------------|
| Upgraded structure | `.raise/` in target project |
| Migrated data | `~/.rai/raise.db` (global) or `.raise/rai/raise.db` (project) |
| Archived originals | `.raise/rai/personal/*.migrated` |
| Governance cartridge | `.raise/cartridges/{project_slug}-governance/` |

## Quality Checklist

- [ ] Version correctly detected before any changes
- [ ] Developer informed of what will change
- [ ] Original data preserved (renamed, not deleted)
- [ ] Structure verification passes after upgrade
- [ ] Data migration verified (counts reported)
- [ ] No source code modified
- [ ] Governance cartridge: corpus confirmed with developer before LLM build (cost gate)
- [ ] Governance cartridge: proposed schema reviewed before extraction (quality loop)

## Known Issues (found in SP-project-upgrade gemba)

Found while running the full flow against a real client repo (la-aldea-erp,
29 docs / 190 KB → 266 nodes):

1. **`rai cartridge init` corpus paths not project-root-relative** — stored
   verbatim, resolved against the cartridge dir, so `build` finds no files.
   Workaround: prefix corpus globs with `../../../` (Step 5b). _Open._
2. **`rai cartridge init` schema = `TODO`** — `build`/`extract` need a real
   node class. Workaround: set `raise_core.graph.models:GraphNode` (Step 5b).
   _Open._
3. **`build` wrote `competency_questions` as a string, not a CQ file path** —
   cartridge query then treated the string as a path and crashed with
   `OSError: File name too long`. **FIXED** (this branch): build now writes the
   questions to `competency_questions.md` and stores the filename.
4. **`extract` dropped chunks on `created: null`** — the LLM returns
   `created: null`; `setdefault` left it, failing Pydantic and losing the whole
   chunk. **FIXED** (this branch): `validate_and_enrich` coerces falsy `created`.
5. **Relationship-extraction coverage is low (~28%)** — NOT an edge-materialization
   bug. Reproduction falsified the original "0 edges" claim: `materialize_edges`
   resolves 79/79 relationship targets and creates 79 edges. The real finding is
   that only 74/266 nodes (28%) carry relationships, likely because extraction is
   per-node-type (each LLM pass sees one type) with a restrictive "both entities
   in this section" prompt rule. Tracked as a coverage spike (RAISE-11565), not a
   defect.

## References

- CLI: `rai init --help`, `rai upgrade --help`, `rai db migrate --help`
- CLI: `rai cartridge init|build|extract|query --help`
- Migration: `raise_cli/storage/migrate.py`
- Init: `raise_cli/cli/commands/init.py`
- Cartridge extraction: `raise_core/cartridges/extract.py`, `corpus_analyzer.py`
- Sibling skill (manual cartridge flow): `/rai-kc-build`
- Next: `/rai-session-start`, `/rai-project-onboard`
