# Epic RAISE-153: Developer Enablement — Scope

> **Status:** IN PROGRESS
> **JIRA:** [RAISE-153](https://humansys.atlassian.net/browse/RAISE-153)
> **Branch:** `epic/raise-153/developer-enablement`
> **Created:** 2026-02-16

---

## Objective

Enable developers to adopt RaiSE by providing accurate, up-to-date documentation deployed as an independent docs site, a methodology-first getting started guide, and training materials for team onboarding.

**Value proposition:** Kurigage tech leaders (and future adopters) get a self-serve path from "what is RaiSE?" to "first story delivered" without requiring Emilio to walk them through everything 1:1.

---

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S1 | Starlight site + content migration | M | ✅ Done | Set up Starlight in raise-commons, migrate 18 docs (9 EN + 9 ES) from raise-gtm, update `raise` → `rai`, theme replication |
| S2 | CLI Reference update | M | ✅ Done | Updated EN + ES docs against v2.0.0a9 --help, added memory viz, release list, --agent, --session flags. PAT-T-005: core/PRO boundary |
| S3 | Getting Started Guide | M | Pending | Methodology-first tutorial: RaiSE principles → Triad → first story lifecycle, not just "how to install" |
| S4 | Training Slide Deck | S | Pending | Distill from guide + reference for 1h Kurigage sessions |
| S5 | Publish skill | S | Pending | `/rai-docs-publish`: verify content currency + build + deploy to Cloudflare Pages |

---

## In Scope

**MUST:**
- Independent Starlight docs site in raise-commons (`docs/` directory)
- All `rai` CLI commands documented with flags, descriptions, and examples
- Getting started guide covering methodology + first story lifecycle
- Deploy to docs.raiseframework.ai (Cloudflare Pages)
- Single publish skill that verifies + builds + deploys

**SHOULD:**
- Training slide deck for 1h sessions
- Content poka-yoke: publish skill verifies CLI --help matches docs

---

## Out of Scope

- ~~Bilingual (i18n)~~ → Pulled into S1 (low incremental cost)
- API/SDK documentation → no public API yet
- Video tutorials → future enablement
- raise-gtm redirect wiring → separate story in raise-gtm repo
- Marketing site content updates → raise-gtm team

---

## Architecture

**Decision:** ADR-030 — Independent Starlight docs site in raise-commons

- Content AND Starlight config live in `docs/` directory
- Replicate raise-gtm theme (dark, copper/amber) for initial brand coherence
- Deploy as separate Cloudflare Pages project to `docs.raiseframework.ai`
- raise-gtm docs become stale after migration (redirects are raise-gtm scope)
- Bilingual (EN/ES) from S1 — low incremental cost

**Seed content from raise-gtm** (9 pages to migrate):
- `index.mdx` — docs homepage
- `getting-started.mdx` — quick start
- `concepts/memory.mdx`, `skills.mdx`, `governance.mdx`, `knowledge-graph.mdx`
- `guides/first-story.mdx`, `setting-up.mdx`
- `cli/index.mdx` — CLI reference (540 lines)

---

## Dependencies

```
S1 (site setup + migration)
  ↓
S2 (CLI reference update) ──┐
  ↓                          │ (parallel possible after S1)
S3 (getting started guide) ◄─┘
  ↓
S4 (training deck — depends on S2+S3 content)

S5 (publish skill — can start after S1, independent of content)
```

**External:** Cloudflare Pages project creation (manual, Emilio has access)

---

## Done Criteria

### Per Story
- [ ] Content accurate against v2.0.0a9 CLI
- [ ] Builds without errors (`npm run build`)
- [ ] Renders correctly in local preview (`npm run dev`)

### Epic Complete
- [ ] Docs site deployed to docs.raiseframework.ai
- [ ] All `rai` commands documented with usage examples
- [ ] Getting started guide covers full story lifecycle
- [ ] Training deck ready for 1h sessions
- [ ] Publish skill operational
- [ ] Epic retrospective done
- [ ] Merged to v2

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Cloudflare subdomain config issues | Low | Medium | Team has done this before for raiseframework.ai |
| Theme divergence from marketing site | Medium | Low | Accept for now; brand changes are infrequent |
| CLI changes during epic | Medium | Low | Publish skill verifies currency — catches drift |

---

## Notes

- raise-gtm docs are higher quality than expected — migration, not rewrite
- Main update work: `raise` → `rai` command rename, new a9 features
- Kurigage training starts today (2026-02-16) — deck is last story, first sessions run from Emilio's knowledge

---

*Created: 2026-02-16*
