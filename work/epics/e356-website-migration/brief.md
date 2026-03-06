---
epic_id: "E356"
title: "Website Migration & v2.2 Update"
status: "draft"
created: "2026-03-05"
jira: "RAISE-156"
---

# Epic Brief: Website Migration & v2.2 Update

## Hypothesis
For the RaiSE team who needs the website to reflect actual framework capabilities,
migrating the site from raise-gtm to raise-commons is a consolidation
that enables accurate, source-aware documentation and website content.
Unlike the current setup (website in raise-gtm without source access), our solution
colocates the site with the codebase it documents.

## Success Metrics
- **Leading:** Site builds successfully from raise-commons after migration
- **Lagging:** Website content reflects v2.2 features accurately; single repo for all site updates

## Appetite
S — 3-4 stories

## Scope Boundaries
### In (MUST)
- Migrate site/ directory from raise-gtm to raise-commons
- Update website content to reflect v2.2 capabilities (skills, CLI, features)
- Verify Cloudflare Pages deployment works from new repo
- Update .gitignore for node_modules/dist

### In (SHOULD)
- Update pricing page if model has changed
- Refresh blog with v2.2 release post
- Update i18n (Spanish) content to match English updates

### No-Gos
- No redesign or stack migration (keep Astro + Tailwind + Cloudflare)
- No new features on the site (waitlist, analytics, etc.)
- No documentation site (separate concern — that's Confluence/docs)

### Rabbit Holes
- Perfectionism on copy — ship accurate content, iterate later
- Trying to auto-generate site content from source code
- Monorepo tooling (turborepo, nx) — just a directory, keep it simple
