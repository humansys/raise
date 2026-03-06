---
epic_id: E356
title: "Website Migration & v2.2 Update"
status: complete
started: "2026-03-05"
closed: "2026-03-06"
jira: RAISE-156
---

# Epic Retrospective: E356 — Website Migration & v2.2 Update

## Summary

Migrated the RaiSE marketing website from raise-gtm to raise-commons, updated all
content for v2.2, set up Cloudflare Pages deployment, published a release blog post,
and unified docs with the existing docs/ directory via symlink.

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 4 planned + 1 bonus (S356.5 docs unification) |
| Duration | 1 session (~4 hours) |
| Commits | ~25 across all stories |
| Pages built | 71 HTML (from 25 at migration start) |
| Files migrated | 66 from raise-gtm |
| Files deleted | 18 duplicated docs (replaced by symlink) |
| Deploy | Production at raiseframework.ai |

## What Went Well

1. **Story-run pipeline worked smoothly** — 4 stories through full 8-phase lifecycle in one session
2. **Symlink approach for docs** (S356.5) — elegant single-source-of-truth solution, zero duplication
3. **Build verification caught real issues** — QR found broken links, missing i18n labels, pricing table gap
4. **Deploy worked first try** (once we got the project name right)
5. **Build ID in footer** — simple but effective deploy verification

## What Could Improve

1. **Subagent branch drift** — plan agent for S356.2 landed on wrong branch. Need explicit branch verification in agent prompts
2. **QR false positive** (S356.1) — flagged Astro 5 output:static as incompatible with SSR. Agents may not know current framework versions
3. **Cloudflare project name mismatch** — wrangler.jsonc said "raise-website" but actual project was "raise-gtm". Discovered at deploy time
4. **Skill bug found** — rai-epic-start was editing backlog.md manually instead of using rai backlog CLI (fixed, RAISE-464)
5. **`wrangler pages deploy` without `--branch=main`** goes to preview, not production — learned the hard way

## Patterns Captured

- **PAT-E-005**: QR agents may not know current framework versions — verify critical findings against actual build/runtime before acting on them
- Content stories need source-of-truth verification — docs drift faster than expected

## Decisions Made

- D1: Use symlink for docs unification (not Astro content loader path, not copy script)
- D2: Deploy via `wrangler pages deploy` to existing `raise-gtm` project (not new project)
- D3: Build timestamp in footer for deploy verification (invisible, same-color text)

## Tickets Created During Epic

| Key | Type | Title |
|-----|------|-------|
| RAISE-464 | Bug | Skills editing backlog.md instead of rai backlog CLI |
| RAISE-465 | Bug | LogfireNotConfiguredWarning when logfire not configured |
| RAISE-466 | Story | Improve agent context for rai backlog CLI usage |
| RAISE-467 | Story | Adapter must inject Jira schema into agent context |
| RAISE-469 | Epic | Release Pipeline Streamlining (E357) |

## Open Items

- raise-gtm site/ needs to be marked as deprecated/archived (external to this repo)
- GitHub secrets (CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID) not yet configured for automated deploys
- Consider renaming Cloudflare project from "raise-gtm" to "raise-website" eventually
