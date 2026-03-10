# Fer's First Pull Checklist

> What Fer needs to do after `git pull origin v2` to start working with Rai.
> Assumes S-MULTIDEV implementation is complete (gitignore changes, personal/ migrations, prefixed IDs).

---

## Prerequisites

- [ ] Python 3.12+ installed
- [ ] `uv` or `pip` available
- [ ] Claude Code installed and configured

## Steps

### 1. Clone/pull the repo

```bash
git pull origin v2
# or if fresh:
git clone <repo> && cd raise-commons && git checkout v2
```

### 2. Install rai-cli

```bash
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

### 3. Create developer profile

```bash
rai session start --name "Fer" --project "$(pwd)" --context
```

This creates `~/.rai/developer.yaml` with:
- Name: Fer
- Session count: 1
- Pattern prefix: F (set manually if not auto-assigned)

**Manual step (until auto-prefix is implemented):**
Edit `~/.rai/developer.yaml` and add:
```yaml
pattern_prefix: F
```

### 4. Build the knowledge graph

```bash
rai memory build
```

This generates `.raise/rai/memory/index.json` locally (gitignored — each dev rebuilds).

### 5. Verify setup

```bash
rai session start --project "$(pwd)" --context
```

Should output the context bundle with Fer's name, session count, and loaded patterns.

### 6. Create personal CLAUDE.local.md (optional)

```bash
cat > CLAUDE.local.md << 'EOF'
# RaiSE Project — raise-cli
Run `/rai-session-start` for context.
EOF
```

Already gitignored — personal instructions for Claude Code.

---

## What Fer Gets Automatically

- **Shared:** patterns.jsonl, governance docs, methodology, work/stories/
- **Personal (auto-created):** session-state.yaml, calibration.jsonl, sessions/
- **Gitignored:** index.json (rebuilt), personal/, CLAUDE.local.md

## What Fer Does NOT Get

- Emilio's session history (in personal/)
- Emilio's calibration/coaching profile (in personal/)
- Emilio's session-state (in personal/)

These are per-developer. Fer builds his own through working sessions.

---

## Branch Workflow

```
v2 (shared development)
  └── epic/eN/fer-feature    ← Fer's epic branch
        └── story/sN.M/name  ← Fer's story branches
```

Fer creates his own epic/story branches. Standard RaiSE lifecycle applies:
`/rai-epic-start` → stories → `/rai-epic-close`

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| `index.json not found` | Run `rai memory build` |
| No session state | Run `rai session start` — creates fresh state in personal/ |
| Pattern ID conflict on merge | Renumber the conflicting pattern (shouldn't happen with prefixes) |
| Missing `~/.rai/developer.yaml` | Run `rai session start --name "Fer"` |
