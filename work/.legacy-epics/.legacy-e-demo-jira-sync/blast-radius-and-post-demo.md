# E-DEMO: Blast Radius & Post-Demo Notes

> **Created:** 2026-02-15 05:50 AM (Sunday)
> **Context:** Pre-implementation review for S-DEMO.5
> **Author:** Rai (architectural review)

---

## Blast Radius — S-DEMO.5 Changes

### Files Created (NEW)

| File | Purpose | LOC Est. |
|------|---------|----------|
| `src/rai_providers/jira/sync.py` | Sync engine: `pull_epic()`, `push_stories()` | ~200 |
| `src/rai_providers/jira/sync_state.py` | Sync state management: `load/save/update state.json` | ~120 |
| `tests/providers/jira/test_sync.py` | Sync engine unit tests (mocked JIRA) | ~250 |
| `tests/providers/jira/test_sync_state.py` | Sync state tests (filesystem) | ~100 |
| `.raise/rai/sync/state.json` | Runtime: sync state (created on first sync) | N/A |

### Files Modified (EXISTING)

| File | Current LOC | Change | Impact |
|------|-------------|--------|--------|
| `src/rai_cli/cli/commands/backlog.py` | 132 | Add `pull` and `push` commands | **Medium** — adds 2 commands, imports sync engine |
| `src/rai_providers/jira/__init__.py` | ~5 | Export sync functions | **Low** — import only |

### Files NOT Modified (Intentional)

| File | Reason |
|------|--------|
| `governance/backlog.md` | Not modified programmatically (see rationale below) |
| `src/rai_cli/skills_base/rai-story-start/SKILL.md` | Authorization gate deferred to post-demo cleanup |
| `src/rai_providers/base.py` | BacklogProvider interface unchanged |
| `src/rai_providers/jira/client.py` | JIRA client used as-is (no changes needed) |
| `src/rai_providers/jira/models.py` | Models sufficient for sync (no new models needed) |
| `src/rai_providers/jira/properties.py` | Entity property functions used as-is |
| `.raise/rai/memory/index.json` | Sync state NOT in memory graph (separation of concerns) |

### Documents That Become Stale

| Document | What's Stale | When to Fix |
|----------|-------------|-------------|
| `governance/decisions/adr-027-*.md` | Says pull is "V3 deferred." Now pull is MVP. | Post-demo: update ADR with amendment |
| `work/epics/e-demo-jira-sync/scope.md` | No mention of authorization validation or sync state file | Post-demo: update scope with actuals |
| `work/epics/e-demo-jira-sync/plan.md` | Progress tracking frozen at S-DEMO.1 done | Update during implementation |
| Previous story designs (S-DEMO.3, S-DEMO.4) | Reference "memory graph" for sync state | Post-demo: clarify state.json vs graph |

---

## Post-Demo Notes & Architectural Rationale

### Decision 1: Sync State Lives in `.raise/rai/sync/`, NOT Memory Graph

**Rationale:**
The memory graph (`.raise/rai/memory/index.json`, 3.6MB) is the ontology/knowledge graph — concepts, patterns, relationships. Sync state is operational data: "which JIRA key maps to which local ID, what was the last sync timestamp."

Mixing these violates separation of concerns:
- `rai memory build` would need to preserve sync state during rebuild
- Graph queries would return operational noise alongside semantic data
- Sync state has different lifecycle (changes on every sync vs graph changes on discovery/build)

**Post-demo action:**
- Formalize `.raise/rai/sync/` as the sync state directory in documentation
- Consider whether `state.json` should be gitignored (machine-specific: cloud_id, local_path)
- Decide: should sync state be committed (shared) or local-only (per developer)?

### Decision 2: backlog.md NOT Modified Programmatically

**Rationale:**
`governance/backlog.md` is a hand-maintained markdown document with 7 numbered sections, changelog, and specific formatting. Programmatic table editing is fragile:
- Markdown table parsers are error-prone (alignment, escaping)
- Inserting rows in the right section requires understanding document structure
- Merge conflicts with manual edits are likely
- False confidence: looks "synced" but could be subtly wrong

For the demo, `state.json` is the source of truth for sync operations. The CLI output shows what was synced. backlog.md remains human-maintained.

**Post-demo action:**
- Evaluate structured backlog format (YAML or JSONL) as alternative to markdown tables
- If backlog.md must be updated programmatically, create a dedicated parser with round-trip support
- Consider: is `state.json` sufficient? Or do users need backlog.md to reflect sync state?
- Likely answer: `rai backlog status` CLI command shows sync state from state.json, no need to edit markdown

### Decision 3: Authorization is Hardcoded for Demo, Configurable for Production

**Rationale:**
The demo shows the VALUE of authorization gates. But the implementation should be:
- **Demo:** `authorization.enabled = True` (hardcoded, shows the gate working)
- **Humansys team:** `authorization.enabled = False` (internal team, trust-based)
- **Coppel/corporate:** `authorization.enabled = True, required_status = "Approved"`

This means authorization is NOT a core sync engine concern — it's a policy layer on top.

**Post-demo action:**
- Add `sync/config.yaml` with authorization settings
- Implement in `/rai-story-start` as a configurable gate (Step 1.5)
- Map JIRA statuses to authorization states per project
- Consider: which JIRA statuses mean "approved"? Different per project workflow.

### Decision 4: Authorization Check is Offline (Reads state.json, Not JIRA API)

**Rationale:**
The `/rai-story-start` skill should NOT call JIRA API directly because:
- **Network dependency:** If JIRA is down, you can't start local work
- **Latency:** 200ms+ per API call adds friction to story start
- **Consistency illusion:** Real-time check pretends "this is the truth" but there's always a window between check and action
- **Offline work:** Developer should be able to work offline after a sync

The correct flow: `rai backlog pull` updates state.json with JIRA statuses. `/rai-story-start` reads state.json locally. If stale, user runs pull again.

**Post-demo action:**
- Implement authorization gate in `/rai-story-start` (reads `.raise/rai/sync/state.json`)
- Add `--force` flag to bypass authorization (for trusted contexts)
- Add staleness warning: "Sync state is 2 hours old. Run `rai backlog pull` to refresh."
- For demo: show the gate directly in CLI output (simpler than skill modification)

### Decision 5: Epic Detection is Explicit (--epic KEY), Not Auto-Detect

**Rationale:**
"Detect new epics in JIRA" sounds simple but requires:
- JQL filter: which project? which status? which labels?
- Permission: which epics does the user have access to?
- Disambiguation: multiple epics found — which one?

For demo, the PM tells the developer the epic key. This is realistic for corporate workflows.

**Post-demo action:**
- Add `rai backlog pull --source jira --discover` for auto-detect (with JQL filter)
- Config: `sync.pull_filter: "project = DEMO AND type = Epic AND status != Done"`
- Interactive selection if multiple epics found
- Consider: notification/webhook when new epic created (V3 scope)

### Decision 6: Idempotency via Local State, Not JQL on Entity Properties

**Rationale:**
JQL queries on JIRA entity properties (`issue.property[key].field = "value"`) have limitations:
- Only works for Forge/Connect apps (not personal OAuth tokens in all cases)
- Syntax varies by JIRA Cloud version
- Additional API call per check (rate limit cost)

Local state.json already knows what was synced: if `S-DEMO.1` has `jira_key: "DEMO-124"`, it was already pushed. No need to ask JIRA.

Entity properties on JIRA issues are still SET (for cross-project visibility, Forge V3), but idempotency is checked locally.

**Post-demo action:**
- Verify entity property JQL works with our OAuth scope
- If it works: use as secondary check (belt and suspenders)
- If not: local state.json is sufficient for single-developer scenarios
- Multi-developer sync (V3) will need JIRA-side idempotency check

### Decision 7: ADR-027 Needs Amendment (Pull is Now MVP)

**Rationale:**
ADR-027 explicitly defers pull to V3. But the demo workflow STARTS with pull (PM creates epic in JIRA → Rai pulls). The JiraClient already has `read_epic()` and `read_stories_for_epic()` — the capability exists. What was missing was the orchestration layer (sync engine).

The ADR was correct at the time (push-first reduces complexity), but the demo workflow requires bidirectional sync to be compelling.

**Post-demo action:**
- Amend ADR-027: "Pull added to MVP scope for demo workflow (manual triggers only)"
- Clarify: pull is still manual (`rai backlog pull`), not automatic (webhooks/polling = V3)
- Document: field-level ownership during pull (JIRA status → local, local design → JIRA)

---

## Risk Assessment for Demo

### High Confidence (Will Work)
- JIRA client read/write operations (S-DEMO.3 tested)
- Entity properties storage (S-DEMO.4 tested)
- OAuth authentication (S-DEMO.2 tested)
- Sync state file management (simple JSON, no external deps)

### Medium Confidence (Needs Testing)
- End-to-end pull→design→push→status-sync workflow
- Idempotency across multiple sync cycles
- Error handling when JIRA project/issue doesn't exist
- Dry-run mode output (formatting, completeness)

### Low Confidence (May Need Workaround)
- Authorization gate in `/rai-story-start` (modifying skill is risky pre-demo)
- backlog.md reflecting sync state (explicitly NOT doing this)
- Real JIRA project permissions (test account may differ from demo account)

### Demo Fallback Plan
If sync engine has issues:
1. **Best case:** Full workflow works end-to-end
2. **Good case:** Push works, pull manual (show CLI output, narrate pull)
3. **Minimum viable:** Show JIRA client operations directly (read_epic, create_story), narrate sync
4. **Emergency:** Screenshots + recorded demo

---

## Implementation Priority (Time-Boxed)

**Available time:** ~24 hours (Sun 06:00 → Mon 06:00, minus sleep)
**S-DEMO.5 estimate:** 4 SP (~4-6 hours with TDD)

### Must-Have (Demo Blockers) — ~3 hours
1. Sync state management (state.json CRUD)
2. Pull operation (JIRA epic → state.json + CLI output)
3. Push operation (local stories → JIRA + state.json update)
4. CLI commands (`rai backlog pull`, `rai backlog push`)
5. Unit tests (mocked JIRA client)

### Should-Have (Demo Polish) — ~1.5 hours
6. Dry-run mode (`--dry-run` flag)
7. Authorization check (read state.json, print gate status)
8. Integration test script (end-to-end with live JIRA)

### Nice-to-Have (If Time Permits) — ~1 hour
9. Status sync (pull updates status from JIRA)
10. Rich CLI output (progress indicators, color)

---

## Shipping Considerations (Post-Demo → Production)

### What Ships As-Is
- OAuth flow (S-DEMO.2) — production-ready
- JIRA client (S-DEMO.3) — production-ready (rate limiting, error handling)
- Entity properties (S-DEMO.4) — production-ready (ADR-028 compliant)
- Pydantic models — production-ready (strict validation)

### What Needs Work Before Shipping
- Sync engine — needs error recovery, partial sync handling, retry logic
- Authorization gate — needs configurable per-project settings
- Sync state — needs schema versioning, migration strategy
- CLI commands — need better error messages, help text
- backlog.md integration — decide if/how to update programmatically
- Multi-developer sync — state.json is per-machine, need shared state strategy

### Architecture for Shipping

```
.raise/rai/sync/
├── config.yaml              # Provider config, authorization settings
├── state.json               # Sync mappings (epic/story → JIRA key + status)
└── history.jsonl             # Audit log (append-only)

# config.yaml (production)
provider: jira
cloud_id: "abc-123"
project_key: "DEMO"
authorization:
  enabled: true              # false for Humansys, true for Coppel
  required_status: "Approved"
  gate_on: "story-start"
  behavior: "block"          # block | warn | skip
sync:
  pull_filter: "project = DEMO AND type = Epic AND status != Done"
  push_labels: ["raise-managed"]
  dry_run_default: false
```

---

*Document created: 2026-02-15 05:50 AM*
*Purpose: Blast radius tracking + post-demo architectural decisions*
*Review: Before implementation start*
