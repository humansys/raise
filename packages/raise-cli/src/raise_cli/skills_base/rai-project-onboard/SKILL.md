---
name: rai-project-onboard
description: Discover conventions and set up governance. Use after rai init --detect on existing code.
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: "rai init --detect"
  raise.next: "session-start"
  raise.gate: "4-dimensional coverage gate"
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.inputs: |
    - project_root: path, required, argument
  raise.outputs: |
    - governance_docs: file_path[] (governance/*.md)
    - knowledge_graph: file_path (.raise/rai/memory/index.json)
  raise.visibility: public
---

# Project Onboard

## Purpose

Guide brownfield project onboarding by combining codebase discovery with conversation. Analyze what exists, ask what code can't tell us, fill 6 governance templates. Gate: 4-dimensional coverage check.

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through every step, show discovery results, confirm each doc
- **Ha**: Run discovery, present summary, collect gaps in one exchange
- **Ri**: Discovery + 1 exchange + write all docs + build graph

## Context

**When to use:** After `rai init --detect` on an existing project with source code.

**When to skip:** Greenfield project → `/rai-project-create`. Not initialized → `rai init --detect` first. Governance already filled.

**Key difference from `/rai-project-create`:** Starts from WHAT EXISTS (discovery), then asks WHY. Create starts from WHAT YOU WANT.

**Inputs:** Project with `rai init --detect` completed, existing codebase.

## Steps

### Step 1: Verify Prerequisites

```bash
ls .raise/manifest.yaml 2>/dev/null || echo "MISSING"
ls governance/prd.md governance/vision.md governance/guardrails.md 2>/dev/null | wc -l
grep -ciE "must-|should-" governance/guardrails.md 2>/dev/null || echo "0"
```

| Result | Action |
|--------|--------|
| Manifest + 6 files + conventions detected | Continue |
| No manifest | Stop: "Run `rai init --detect` first." |
| No conventions in guardrails | Suggest re-running with `--detect` flag |
| No source code | Suggest `/rai-project-create` instead |

<verification>
Manifest exists, governance templates exist, conventions detected.
</verification>

### Step 2: Verify or Run Discovery

Check if discovery data exists. If not, run it automatically — do NOT stop and ask the user to run a separate command.

```bash
ls work/discovery/components-validated.json 2>/dev/null && echo "DISCOVERY_OK" || echo "DISCOVERY_MISSING"
```

| Result | Action |
|--------|--------|
| `DISCOVERY_OK` | Continue to Step 3 |
| `DISCOVERY_MISSING` | Auto-run discovery (see below) |

**Auto-discover when missing:**

1. Detect the primary language from the project files:
   ```bash
   # Count source files by extension to detect primary language
   find . -maxdepth 4 -not -path "./.raise/*" -not -path "./.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" \) 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -1
   ```
2. Run discovery with the detected language:
   ```bash
   rai discover scan . --language {detected_language}
   ```
3. Present a brief message: "Discovery data not found. Running codebase analysis... Done — {N} components discovered."
4. Continue to Step 3.

If discover fails (non-zero exit), stop with: "Codebase analysis failed: {error}. Check that source files exist and retry, or run `rai discover scan .` manually."

Also auto-read existing project documentation (README, ARCHITECTURE, CONTRIBUTING, etc.) to pre-populate governance fields. No need to ask — always read what's available.

<verification>
Discovery artifacts exist (found or auto-generated). Existing docs read.
</verification>

### Step 3: Fill Governance Gaps

Present what discovery + docs already covered. Ask ONLY for unfilled fields:
- **Vision:** description, who uses it, why it exists
- **Capabilities:** 3-5 core things it does → 5-8 RF-XX requirements
- **Architecture gaps:** external actors/systems, interfaces, branch model

<verification>
All governance fields covered (from discovery + docs + conversation).
</verification>

### Step 4: Write 6 Governance Docs

Same parser contracts as `/rai-project-create`. Publish each doc via CLI:

Use `raise_docs_write` MCP tool for each of the following 6 calls:
1. doc_type="project-vision", title="{project}: vision", content="[outcomes table | **{Bold Name}** | {description} |]", output_path="governance/vision.md", cwd="{project_or_worktree_path}"
2. doc_type="project-prd", title="{project}: PRD", content="[requirements as ### RF-XX: Title]", output_path="governance/prd.md", cwd="{project_or_worktree_path}"
3. doc_type="project-guardrails", title="{project}: guardrails", content="[MERGE detected conventions — YAML frontmatter type: guardrails, table | ID | Level | Guardrail | Verification | Derived from |]", output_path="governance/guardrails.md", cwd="{project_or_worktree_path}"
4. doc_type="project-backlog", title="{project}: backlog", content="[# Backlog: {name}, epic rows | E{N} | ... |]", output_path="governance/backlog.md", cwd="{project_or_worktree_path}"
5. doc_type="architecture-system-context", title="{project}: system context", content="[external interfaces table]", output_path="governance/architecture/system-context.md", cwd="{project_or_worktree_path}"
6. doc_type="architecture-system-design", title="{project}: system design", content="[components from DISCOVERED modules — YAML frontmatter type: architecture_design, layers as list of dicts]", output_path="governance/architecture/system-design.md", cwd="{project_or_worktree_path}"
If MCP tools are not available, fall back to:
```bash
rai docs write project-vision --title "{project}: vision" --stdin --output-path governance/vision.md << 'EOF'
[outcomes table | **{Bold Name}** | {description} |]
EOF

rai docs write project-prd --title "{project}: PRD" --stdin --output-path governance/prd.md << 'EOF'
[requirements as ### RF-XX: Title]
EOF

rai docs write project-guardrails --title "{project}: guardrails" --stdin --output-path governance/guardrails.md << 'EOF'
[MERGE detected conventions — YAML frontmatter type: guardrails, table | ID | Level | Guardrail | Verification | Derived from |]
EOF

rai docs write project-backlog --title "{project}: backlog" --stdin --output-path governance/backlog.md << 'EOF'
[# Backlog: {name}, epic rows | E{N} | ... |]
EOF

rai docs write architecture-system-context --title "{project}: system context" --stdin --output-path governance/architecture/system-context.md << 'EOF'
[external interfaces table]
EOF

rai docs write architecture-system-design --title "{project}: system design" --stdin --output-path governance/architecture/system-design.md << 'EOF'
[components from DISCOVERED modules — YAML frontmatter type: architecture_design, layers as list of dicts]
EOF
```

Update `.raise/manifest.yaml` with branch configuration.

<verification>
All 6 docs written. Detected conventions preserved in guardrails.
</verification>

### Step 5: 4-Dimensional Coverage Gate

```bash
rai graph build
```

| Gate | Check | Pass criteria |
|------|-------|---------------|
| G1: Governance structure | Parser-extractable content per doc | ≥2 outcomes, ≥3 RF-XX, ≥3 guardrails, ≥1 epic |
| G2: Module coverage | Discovered modules in governance | ≥80% modules referenced |
| G3: Doc coverage | Docs read → governance elements | 100% of docs read contributed |
| G4: Traceability | Guardrails→RF-XX, RF-XX→body text | ≥80% linked |

Present gate results. If PARTIAL (1-2 items): fix specific items. If FAIL: fix docs, rebuild.

<verification>
All 4 gate dimensions pass (or user accepts documented exceptions).
</verification>

### Step 6: Summary

```
## Project Onboarded: {project_name}
Discovery: {N} modules, {N} components, {N} conventions
Governance: {N} outcomes, {N} requirements, {N} guardrails, {N} epics
Graph: {total} governance nodes
Next: /rai-session-start
```

## Output

| Item | Destination |
|------|-------------|
| Governance docs | `governance/` (6 files) |
| Knowledge graph | `.raise/rai/memory/index.json` |
| Next | `/rai-session-start` |

## Quality Checklist

- [ ] Discovery auto-runs if missing — never STOP asking user to run /rai-discover
- [ ] Existing docs checked before asking user (minimize redundant questions)
- [ ] Detected conventions MERGED into guardrails (not overwritten)
- [ ] Parser contracts followed exactly (same as `/rai-project-create`)
- [ ] 4-dimensional gate checked (not just node count)
- [ ] NEVER overwrite `guardrails.md` conventions from `--detect`

## References

- Prerequisite: `rai init --detect`
- Sibling: `/rai-project-create` (greenfield)
- Discovery: `/rai-discover` (unified pipeline)
- Parser sources: `src/raise_cli/governance/parsers/*.py`
- Next: `/rai-session-start`
