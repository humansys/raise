---
description: 'Initialize codebase discovery by detecting project type, languages,
  and key directories. Creates context file for subsequent discovery skills.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-project
  raise.gate: ''
  raise.next: discover-scan
  raise.prerequisites: ''
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: discovery
name: rai-discover-start
---

# Discovery Start

> **Deprecated:** Use `/rai-discover` instead, which runs the full pipeline (detect → extract → describe → document → build) in one pass. This skill is kept for backward compatibility.

## Purpose

Initialize codebase discovery by detecting languages, key directories, and entry points. Creates the context file that all subsequent discovery skills depend on.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, detect all languages, create complete context file
- **Ha**: Focus on primary language only for targeted discovery
- **Ri**: Integrate with monorepo structures or custom conventions

## Context

**When to use:** Starting discovery on a new or significantly changed codebase.

**When to skip:** `work/discovery/context.yaml` already exists and is current. For targeted re-scan, use `/rai-discover-scan` directly with path.

**Inputs:** Access to project root directory.

## Steps

### Step 1: Detect Languages

Scan for source files by extension (exclude `.raise/`, `node_modules/`, `.git/`, `obj/`, `bin/`):

```bash
find . -type f -name "*.py" ! -path "./.raise/*" ! -path "./node_modules/*" ! -path "./.git/*" | wc -l
# Repeat for: *.ts/*.tsx, *.js/*.jsx, *.cs/*.csproj, *.php, *.dart
```

| Language | Extensions |
|----------|-----------|
| python | `.py` |
| typescript | `.ts`, `.tsx` |
| javascript | `.js`, `.jsx` |
| csharp | `.cs`, `.csproj` |
| php | `.php` |
| dart | `.dart` |

<verification>
At least one supported language detected.
</verification>

<if-blocked>
No supported languages → discovery not applicable to this codebase.
</if-blocked>

### Step 2: Identify Directories & Entry Points

**Directories:** Check for `src/`, `lib/`, `app/`, `packages/`.

**Entry points** by language:

| Language | Entry points |
|----------|-------------|
| python | `src/*/cli/main.py`, `src/*/__main__.py`, `main.py` |
| typescript/js | `src/index.ts`, `src/main.ts`, `package.json` main field |
| csharp | `Program.cs`, `Startup.cs`, `*.sln` |
| php | `public/index.php`, `bin/console` |
| dart | `lib/main.dart` |

<verification>
At least one scannable directory identified.
</verification>

<if-blocked>
No clear source directory → ask user to specify.
</if-blocked>

### Step 3: Create Context File

Write `work/discovery/context.yaml`:

```yaml
project:
  name: {from pyproject.toml/package.json/directory name}
  languages: [python]
  root_dirs: [src/raise_cli]
  entry_points: [src/raise_cli/cli/main.py]
  detected_at: {ISO_TIMESTAMP}
status: initialized
```

Project name priority: `pyproject.toml` → `package.json` → directory name.

<verification>
File created at `work/discovery/context.yaml`.
</verification>

### Step 4: Display Summary

```markdown
## Discovery Initialized

**Project:** {name}
**Languages:** {list}
**Directories:** {list}
**Entry Points:** {list}
**Context file:** `work/discovery/context.yaml`

**Next:** `/rai-discover-scan`
```

## Output

| Item | Destination |
|------|-------------|
| Context file | `work/discovery/context.yaml` |
| Next | `/rai-discover-scan` |

## Quality Checklist

- [ ] All supported languages detected (not just primary)
- [ ] Generated directories exclude build/vendor paths
- [ ] Context file is valid YAML with all required fields
- [ ] Monorepo: each package listed as separate root_dir
- [ ] NEVER include generated/build directories in root_dirs

## References

- Next: `/rai-discover-scan`
- Pipeline: discover-start → discover-scan → discover-validate → discover-document
