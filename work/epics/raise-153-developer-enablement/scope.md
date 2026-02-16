## Epic Scope: RAISE-153 Developer Enablement

**JIRA:** [RAISE-153](https://humansys.atlassian.net/browse/RAISE-153)
**Objective:** Enable developers to adopt RaiSE with proper documentation, a getting started guide, and training materials.

**In Scope:**
- Starlight docs site setup in raise-commons (docs.raiseframework.ai)
- CLI Reference — full command documentation with examples for v2.0.0a9
- Getting Started Guide — RaiSE methodology, first principles, rai-cli lifecycle walkthrough
- Training Slide Deck — distilled content for 1h Kurigage training sessions

**Out of Scope:**
- Bilingual (i18n) support → future story, after English content stabilizes
- API/SDK documentation → no public API yet
- Video tutorials → future enablement
- raise-gtm migration/redirect wiring → separate story in raise-gtm repo

**Architecture Decision:**
- Docs content lives in raise-commons (close to the code it documents)
- Starlight (Astro) for publishing — team already knows it from raise-gtm
- Deploy to docs.raiseframework.ai (Cloudflare Pages subdomain)
- Existing raise-gtm docs pages serve as seed content
- raise-gtm marketing site links to docs subdomain

**Stories (planned):**
- S1: Set up Starlight docs site + migrate seed content from raise-gtm
- S2: CLI Reference — document all `rai` commands with examples
- S3: Getting Started Guide — methodology + first principles + CLI lifecycle
- S4: Training Slide Deck — distilled for 1h sessions (Gamma or Markdown)

**Done when:**
- [ ] Docs site deployed to docs.raiseframework.ai
- [ ] All `rai` CLI commands documented with usage examples
- [ ] Getting started guide covers full story lifecycle
- [ ] Training deck supports Kurigage 1h sessions
- [ ] Epic retrospective done
- [ ] Merged to v2
