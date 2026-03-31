---
id: ADR-030
title: Documentation Site Architecture
status: superseded
superseded_by: RAISE-1129
date: 2026-02-16
epic: RAISE-153
decision: Independent Starlight docs site in raise-commons, deployed to docs.raiseframework.ai
---

> **Superseded (2026-03-30):** Astro/Starlight replaced by MkDocs + Material (RAISE-1129).
> The core decision (docs in raise-commons, independent deploy to docs.raiseframework.ai) still holds.
> Only the rendering engine changed. See `governance/architecture/modules/docs-site.md`.

# ADR-030: Documentation Site Architecture

## Context

RaiSE documentation currently lives in raise-gtm (the marketing site repo) as part of an Astro + Starlight setup. This creates a problem: docs content is far from the code it documents, requiring cross-repo coordination for every CLI change.

raise-gtm has 9 bilingual docs pages (CLI reference, concepts, guides) that are well-written but use the old `raise` command name and don't cover v2.0.0a9 features (session isolation, backlog commands, publish workflow).

We need docs that:
- Update when CLI changes (same repo, same PR)
- Deploy independently from marketing site
- Maintain brand coherence (dark theme, copper accents)
- Support a single publish command that verifies everything is current

## Decision

**Independent Starlight docs site in raise-commons**, deployed to `docs.raiseframework.ai`.

- Content AND publishing config live in raise-commons (`docs/` directory)
- Starlight (Astro) for rendering — team already knows it from raise-gtm
- Deploy to Cloudflare Pages as a separate project (not the marketing site)
- Migrate existing raise-gtm docs as seed content, update for v2.0.0a9
- Single `/rai-docs-publish` skill handles verify + build + deploy

## Alternatives Considered

### A: Content in raise-commons, publish via raise-gtm
- Content close to code, but cross-repo build dependency
- Preview requires running raise-gtm locally
- Brand coherence guaranteed but coupling is high
- **Rejected:** Cross-repo sync is the same problem we're solving

### B: Keep docs in raise-gtm, update there
- Zero migration work
- Content stays far from code — every CLI change requires raise-gtm PR
- Marketing team owns developer docs
- **Rejected:** Separation of concerns violated

### C: Hosted platform (ReadTheDocs, GitBook, Mintlfy)
- Zero infrastructure setup
- Less control over theme and build
- Another service dependency and cost
- **Rejected:** We already have the toolchain knowledge

## Consequences

### Positive
- Docs update in same PR as code changes
- Independent deploy cycle from marketing
- `npm run dev` in raise-commons to preview docs locally
- Single publish skill verifies content currency before deploy
- No cross-repo coordination for doc updates

### Negative
- Duplicate Starlight setup (raise-commons + raise-gtm)
- Theme must be manually kept in sync if brand changes
- raise-gtm docs become stale (need redirect or removal)
- Initial migration effort (~1 story)

### Neutral
- Cloudflare Pages supports multiple projects on subdomains — no infra issue
- Bilingual support can be added later (start English-only, port i18n when ready)

## Implementation Notes

- Start English-only — i18n is out of scope for RAISE-153
- Replicate raise-gtm's Starlight theme (dark, copper/amber accents) for initial coherence
- raise-gtm docs pages should redirect to docs.raiseframework.ai after migration
- Publish skill should verify: CLI --help output matches docs, version string matches, all commands documented
