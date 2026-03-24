# RAISE-634: Fix Plan

## Verification command
```bash
cd site && npm run build 2>&1 | grep -c "completed\|error" && \
grep -rh 'href="[^"]*\.md[^"]*"' dist/docs/ | grep -v "_astro\|sitemap\|pagefind" | wc -l
# Expected: 0 broken .md hrefs
```

## Tasks

### T1: Regression test — build audit script
Write a script/check that fails if any built HTML under dist/docs/ contains a body href with .md extension.
Verify it fails with current source. Commit.
```
git commit -m "test(RAISE-634): add build link audit — fails on .md body hrefs"
```

### T2: Fix docs/index.mdx
Replace 4 body links with absolute paths:
- `getting-started.md` → `/docs/getting-started/`
- `concepts/memory.md` → `/docs/concepts/memory/`
- `guides/first-story.md` → `/docs/guides/first-story/`
- `cli/README.md` → `/docs/cli/`
```
git commit -m "fix(RAISE-634): fix body links in docs/index.mdx"
```

### T3: Fix docs/getting-started.mdx
- `guides/first-story.md` → `/docs/guides/first-story/`
- `guides/setting-up.md` → `/docs/guides/setting-up/`
- `cli/README.md` → `/docs/cli/`
- `concepts/README.md` → `/docs/concepts/`
```
git commit -m "fix(RAISE-634): fix body links in docs/getting-started.mdx"
```

### T4: Fix docs/cli/index.mdx
Replace all `cli/X.md` links in the commands table with `X/` (relative, same dir) or `/docs/cli/X/`.
```
git commit -m "fix(RAISE-634): fix body links in docs/cli/index.mdx"
```

### T5: Fix remaining files
- docs/concepts/index.mdx — `concepts/X.md` and `cli/README.md`
- docs/concepts/memory.mdx — `concepts/knowledge-graph.md`, `cli/README.md`
- docs/concepts/skills.mdx — `cli/README.md`
- docs/guides/create-hook.mdx — `cli/adapter.md`, `guides/create-adapter.md`
- docs/guides/extending.mdx — `guides/create-*.md`, `guides/register-mcp.md`, `guides/create-hook.md`
```
git commit -m "fix(RAISE-634): fix body links in remaining docs files"
```

### T6: Verify regression test green + full gates
Run build audit → 0 broken hrefs. Run full site build. Confirm fix.
