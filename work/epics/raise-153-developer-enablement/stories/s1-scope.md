## Story Scope: RAISE-153.1 — Starlight Site Setup + Content Migration

**Epic:** RAISE-153 Developer Enablement
**Size:** M

**In Scope:**
- Starlight (Astro) project setup in `docs/` directory
- Replicate raise-gtm dark theme (copper/amber accents)
- Migrate 9 English docs from raise-gtm as seed content
- Rename `raise` → `rai` across all migrated content
- Sidebar structure: Start Here, Concepts, Guides, Reference
- Local dev works (`npm run dev`)
- Build succeeds (`npm run build`)

**Out of Scope:**
- Bilingual (i18n) → future story
- Cloudflare Pages deployment config → S5 (publish skill)
- Content updates/rewrites → S2, S3
- Custom components beyond Starlight defaults
- LLM-friendly output plugin (starlight-llms-txt) → nice-to-have, defer

**Done Criteria:**
- [ ] `docs/` directory with working Starlight project
- [ ] 9 docs migrated from raise-gtm with `raise` → `rai` rename
- [ ] Dark theme with copper accents matches raise-gtm
- [ ] `npm run dev` serves docs locally
- [ ] `npm run build` produces static output
- [ ] Sidebar navigation works correctly
- [ ] Tests pass (existing raise-commons tests unaffected)
