---
name: rai-discover
description: Scan codebase, extract symbols, and build knowledge graph. Use for codebase discovery.
model: sonnet

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: ""
  raise.prerequisites: "rai init --detect"
  raise.next: "project-onboard"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - project_root: path, required, argument
    - language: string, optional, argument (auto-detected if omitted)
  raise.outputs: |
    - context_yaml: file_path (work/discovery/context.yaml)
    - components_validated: file_path (work/discovery/components-validated.json)
    - module_docs: file_path[] (governance/architecture/modules/*.md)
    - system_docs: file_path[] (governance/architecture/*.md)
    - graph: side_effect (rai graph build)
---

# Discover

## Purpose

Run the full discovery pipeline in one pass: detect languages, extract and describe components, generate architecture docs, and build the knowledge graph.

## Mastery Levels (ShuHaRi)

- **Shu**: Show each phase, explain results, pause after describe + document
- **Ha**: Auto-run detect + extract, pause at describe, auto-document if <10 modules
- **Ri**: Full pipeline with inline approve, minimal pauses

## Context

**When to use:** After `rai init --detect` on an existing codebase, or when architecture changes significantly.

**When to skip:** Graph is current and no structural changes since last discovery.

**Inputs:** Project root with source code. Optionally specify language to limit scan.

| Condition | Action |
|-----------|--------|
| `rai init --detect` done | Continue |
| No `.raise/manifest.yaml` | Stop: run `rai init --detect` first |
| Only updating docs | Use `/rai-docs-update` instead |

## Steps

### Step 1: Detect (auto)

```bash
rai discover scan . --output summary
```

From summary, extract languages, source directories, entry points. Write `work/discovery/context.yaml` with project name (from `pyproject.toml` → `package.json` → directory), languages, root_dirs, entry_points, detected_at.

<verification>
`work/discovery/context.yaml` created.
</verification>

### Step 2: Extract (auto)

For each detected language and root directory:

```bash
rai discover scan {root_dir} --language {language} --output json | rai discover analyze --output human
```

Produces `work/discovery/analysis.json` with confidence scores, auto-categorization, and module grouping.

<verification>
`work/discovery/analysis.json` exists.
</verification>

### Step 3: Describe (HITL)

Handle components by confidence tier:

| Confidence | Action |
|-----------|--------|
| High (≥70) | Accept `auto_purpose` and `auto_category` silently — no human review |
| Medium (40-69) | Present by module batch with LLM-suggested descriptions |
| Low (<40) | Scale gate first, then review |

**Medium flow:** Present table per module (name, kind, category, suggested purpose, score). Ask: "Approve batch? [Approve all / Edit specific]"

**Low scale gate (all low AND >50):** Offer modes: A) by layer/namespace, B) user nominates key components + bulk-skip, C) auto-accept by naming pattern (`*Handler`, `*Repository`). Otherwise review individually.

Write `components-draft.yaml` and export to `components-validated.json` (graph node format).

<verification>
All components described. `components-validated.json` created.
</verification>

<if-blocked>
No symbols extracted → verify language is supported and path is correct.
</if-blocked>

### Step 4: Document (HITL)

**Module docs:** For each module, publish to local path and docs adapter via:

Use `raise_docs_write` MCP tool with doc_type="architecture-module", title="{name}", content="YAML frontmatter (type, name, purpose, status, depends_on, depended_by, components) plus ## Purpose, ## Architecture, ## Key Files, ## Dependencies, ## Conventions sections", output_path="governance/architecture/modules/{name}.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write architecture-module \
  --title "{name}" \
  --stdin \
  --output-path governance/architecture/modules/{name}.md << 'EOF'
---
type: module
name: {name}
purpose: {purpose}
status: active
depends_on: [{deps}]
depended_by: [{rev_deps}]
components: {count}
---

## Purpose
{why this module exists}

## Architecture
{structure, key abstractions}

## Key Files
{important files and their roles}

## Dependencies
{what it imports and why}

## Conventions
{patterns specific to this module}
EOF
```

Detect modules by language: Python (`__init__.py`), C# (`.csproj` + namespaces), PHP (`composer.json` PSR-4).

**System docs:** Generate 4 docs via CLI:

Use `raise_docs_write` MCP tool for each of the following 4 calls:
1. doc_type="architecture-system-context", title="{project}: system context", content="[what, who, why, external systems, external interfaces table]", output_path="governance/architecture/system-context.md", cwd="{project_or_worktree_path}"
2. doc_type="architecture-system-design", title="{project}: system design", content="[layers, data flows, constraints — YAML frontmatter type: architecture_design]", output_path="governance/architecture/system-design.md", cwd="{project_or_worktree_path}"
3. doc_type="architecture-domain-model", title="{project}: domain model", content="[bounded contexts, context map]", output_path="governance/architecture/domain-model.md", cwd="{project_or_worktree_path}"
4. doc_type="architecture-index", title="{project}: architecture index", content="[compact overview <2K tokens]", output_path="governance/architecture/index.md", cwd="{project_or_worktree_path}"
If MCP tools are not available, fall back to:
```bash
rai docs write architecture-system-context \
  --title "{project}: system context" \
  --stdin \
  --output-path governance/architecture/system-context.md << 'EOF'
[what, who, why, external systems, external interfaces table]
EOF

rai docs write architecture-system-design \
  --title "{project}: system design" \
  --stdin \
  --output-path governance/architecture/system-design.md << 'EOF'
[layers, data flows, constraints — YAML frontmatter type: architecture_design]
EOF

rai docs write architecture-domain-model \
  --title "{project}: domain model" \
  --stdin \
  --output-path governance/architecture/domain-model.md << 'EOF'
[bounded contexts, context map]
EOF

rai docs write architecture-index \
  --title "{project}: architecture index" \
  --stdin \
  --output-path governance/architecture/index.md << 'EOF'
[compact overview <2K tokens]
EOF
```

Present for review.

<verification>
Module docs + system docs generated. Prose explains WHY, not just WHAT.
</verification>

### Step 5: Build (auto)

```bash
rai graph build
```

Use `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, query="module dependencies".
If MCP tools are not available, fall back to: `rai graph query "module dependencies"`

Verify module nodes in graph, no stale references. Present summary: project, components by tier, modules, graph node/edge counts.

<verification>
Graph built. Module nodes present.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Context file | `work/discovery/context.yaml` |
| Component catalog | `work/discovery/components-validated.json` |
| Module docs | `governance/architecture/modules/*.md` (local) + docs adapter (type: architecture-module) |
| System docs | `governance/architecture/*.md` (local, routing pending) |
| Knowledge graph | `.raise/rai/memory/index.json` |
| Next | `/rai-project-onboard` |

## Quality Checklist

- [ ] All supported languages detected (not just primary)
- [ ] High-confidence components auto-accepted (no unnecessary HITL)
- [ ] Medium-confidence presented by module batch (not per-component)
- [ ] Scale gate applied for all-low large codebases (>50 components)
- [ ] Module frontmatter includes all required fields
- [ ] Module prose explains WHY, not just WHAT (new contributor test)
- [ ] Index under 2K tokens for session-loadable context
- [ ] Graph built and verified as final step
- [ ] NEVER include generated/build directories in root_dirs
- [ ] NEVER generate placeholder docs for modules with no real code

## References

- CLI: `rai discover scan --help`, `rai discover analyze --help`
- Graph: `rai graph build`, rai graph query
- Categories: service, model, utility, handler, parser, builder, schema, command, test
- Confidence tiers: high ≥70, medium 40-69, low <40
