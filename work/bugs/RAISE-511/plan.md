# RAISE-511: Fix Plan

## Tasks

### Task 1 — Fix EN getting-started.mdx
Replace all `rai-cli` with `raise-cli` in `docs/src/content/docs/docs/getting-started.mdx`
Verification: `grep "rai-cli" docs/src/content/docs/docs/getting-started.mdx` → no output
Commit: `fix(RAISE-511): update install commands to raise-cli in EN getting-started`

### Task 2 — Fix EN index.mdx
Replace `rai-cli` with `raise-cli` in `docs/src/content/docs/docs/index.mdx`
Verification: `grep "rai-cli" docs/src/content/docs/docs/index.mdx` → no output
Commit: `fix(RAISE-511): update install command to raise-cli in EN index`

### Task 3 — Fix ES getting-started.mdx
Replace `rai-cli` with `raise-cli` in `docs/src/content/docs/es/docs/getting-started.mdx`
Verification: `grep "rai-cli" docs/src/content/docs/es/docs/getting-started.mdx` → no output
Commit: `fix(RAISE-511): update install command to raise-cli in ES getting-started`

### Task 4 — Fix ES index.mdx
Replace `rai-cli` with `raise-cli` in `docs/src/content/docs/es/docs/index.mdx`
Verification: `grep "rai-cli" docs/src/content/docs/es/docs/index.mdx` → no output
Commit: combined with Task 3 or separate

### Task 5 — Commit scope artifacts
Commit: `chore(RAISE-511): add bug scope, analysis, and plan artifacts`

## Final verification
`grep -rn "rai-cli" docs/src/` → no output
