## Story Scope: RAISE-166

**Summary:** Memory query semantic density: compact format, concept_lookup fix, truncation indicator
**Size:** S
**Epic:** RAISE-168 (Neurosymbolic Memory Density)
**Branch:** `epic/raise-168/neurosymbolic-memory-density` (working on epic branch — S-sized)

**In Scope:**
- `--format compact` option for `rai memory query` — one-line per result: `[type] ID: summary` (~15-20 tokens vs ~80 today)
- Fix concept_lookup: keyword_search as reliable default, concept_lookup only via explicit `--strategy concept_lookup`
- Truncation footer: `[N more results — use --limit to see more]`

**Out of Scope:**
- Changes to graph schema or backend
- Context bundle redesign (RAISE-169)
- Session startup changes (RAISE-165)
- Temporal decay (RAISE-170)

**Done Criteria:**
- [ ] `--format compact` produces ~15-20 tokens per result
- [ ] Default strategy uses keyword_search reliably
- [ ] `--strategy concept_lookup` uses BFS explicitly
- [ ] Truncation footer appears when results are clipped
- [ ] Tests pass (unit + integration)
- [ ] Type checks pass (pyright)
- [ ] Retrospective complete
