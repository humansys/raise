---
epic_id: "E356"
title: "Website Migration & v2.2 Update"
status: "in_progress"
created: "2026-03-05"
jira: "RAISE-156"
---

# E356: Website Migration & v2.2 Update

## Objective

Migrate the RaiSE marketing website from raise-gtm to raise-commons and update
content to reflect v2.2 capabilities. The site in raise-gtm cannot access source
code, making accurate documentation impossible. Colocating solves this.

## Current State

- **Site location:** `raise-gtm/site/` (Astro 5 + Tailwind 4 + MDX)
- **Deploy:** Cloudflare Pages via wrangler (raiseframework.ai)
- **Content:** Landing (en/es), pricing, blog (1 post), waitlist API (D1)
- **Size:** ~1.3MB source (25 files), ~10 components

## Planned Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S356.1 | ~~Migrate site to raise-commons~~ | S | ✅ Complete — merged to dev |
| S356.2 | ~~Update website content for v2.2~~ | M | ✅ Complete — merged to dev |
| S356.3 | ~~Cloudflare Pages deployment~~ | S | ✅ Complete — merged to dev |
| S356.4 | Blog: v2.2 release post | XS | Announce v2.2 with key features |

## Done Criteria

- [x] Site builds from raise-commons (`npm run build` in site/)
- [x] Cloudflare Pages deploys from raise-commons
- [x] Website content reflects v2.2 features accurately
- [ ] raise-gtm site/ marked as deprecated/archived
