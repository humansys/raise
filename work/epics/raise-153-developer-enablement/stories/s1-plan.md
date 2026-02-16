# Implementation Plan: RAISE-153.1 Starlight Site Setup

## Overview
- **Story:** RAISE-153.1 / RAISE-154
- **Size:** M
- **Created:** 2026-02-16

## Tasks

### Task 1: Scaffold Starlight project
- **Description:** Initialize Astro + Starlight in `docs/` directory. Create package.json, astro.config.mjs, tsconfig.json. No Cloudflare adapter (static output only for now). No i18n (English only). No Tailwind (Starlight handles styling via CSS variables).
- **Files:** `docs/package.json`, `docs/astro.config.mjs`, `docs/tsconfig.json`
- **Verification:** `cd docs && npm install && npm run build` succeeds
- **Size:** S
- **Dependencies:** None

### Task 2: Replicate theme
- **Description:** Copy starlight.css from raise-gtm, adapt for standalone (remove fonts.css import — use Starlight defaults or copy font files). Copy logo.svg. Copy font files (Inter woff2) if self-hosting, otherwise use @fontsource package.
- **Files:** `docs/src/styles/starlight.css`, `docs/public/logo.svg`, `docs/public/fonts/`, `docs/src/styles/fonts.css`
- **Verification:** `npm run dev` shows dark theme with copper accents
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Migrate docs content (9 pages)
- **Description:** Copy all 9 English docs from raise-gtm. Rename `raise` → `rai` across all content. Update any stale references (version numbers, package names). Configure sidebar in astro.config.mjs matching raise-gtm structure.
- **Files:**
  - `docs/src/content/docs/index.mdx`
  - `docs/src/content/docs/getting-started.mdx`
  - `docs/src/content/docs/concepts/memory.mdx`
  - `docs/src/content/docs/concepts/skills.mdx`
  - `docs/src/content/docs/concepts/governance.mdx`
  - `docs/src/content/docs/concepts/knowledge-graph.mdx`
  - `docs/src/content/docs/guides/first-story.mdx`
  - `docs/src/content/docs/guides/setting-up.mdx`
  - `docs/src/content/docs/cli/index.mdx`
- **Verification:** `npm run build` succeeds, all 9 pages render, sidebar navigation works
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Manual integration test
- **Description:** Run `npm run dev`, navigate all 9 pages, verify: theme matches raise-gtm, sidebar works, code blocks render, `rai` command references are correct (no stale `raise` references), links between pages work.
- **Verification:** All pages render correctly, no broken links, no stale `raise` references
- **Size:** XS
- **Dependencies:** Task 3

## Execution Order
1. Task 1 — scaffold (foundation)
2. Task 2 — theme (depends on 1)
3. Task 3 — content migration (depends on 2)
4. Task 4 — manual integration test (final)

## Risks
- Starlight version mismatch between raise-gtm and new install: use same version (`^0.37.6`)
- Font self-hosting may have path issues: fallback to @fontsource if needed

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | M | -- | |
| 4 | XS | -- | |
