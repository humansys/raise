## Story Scope: S-RELEASE-WIRING

**Type:** Bugfix (integration gap)
**Parent:** Standalone (branchless, off v2)
**Related:** S-RELEASE-ONTOLOGY (introduced the ontology layer)

**Problem:** S-RELEASE-ONTOLOGY added release as a first-class ontology concept (models, parser, graph edges, tests) but never propagated it to the workflow surface. The CLI, session context, query engine, and skills don't know releases exist. Classic PAT-194 — infrastructure without wiring.

---

**In Scope:**

Tier 1 — CLI/Schema (code changes):
- Add `release` field to `CurrentWork` schema
- Add release to session context bundle output
- Add `find_release_for()` query helper
- Add `rai release list` CLI command
- Add release count to `rai memory validate` expected types

Tier 2 — Skills (SKILL.md updates):
- `/rai-session-start` — display release context
- `/rai-session-close` — capture release in current_work
- `/rai-epic-start` — verify/display release linkage
- `/rai-epic-design` — cross-epic release awareness
- `/rai-epic-plan` — release timeline context
- `/rai-epic-close` — release progress update
- `/rai-story-start` — release deadline pressure

**Out of Scope:**
- `rai release show` / `rai release progress` (future)
- `rai epic` command group (future)
- Jira Fix Version sync (E21)
- Release-specific CLI management commands (create, update)

**Done Criteria:**
- [ ] `CurrentWork` schema has `release` field
- [ ] `rai session start --context` includes release info
- [ ] `find_release_for()` works in query engine
- [ ] `rai release list` displays releases from roadmap
- [ ] `rai memory validate` checks for release nodes
- [ ] 7 skills updated with release awareness
- [ ] All tests pass
- [ ] Type checks pass
