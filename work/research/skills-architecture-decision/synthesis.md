# Synthesis: Skills Architecture Decision

> Research ID: skills-architecture-20260131
> Date: 2026-01-31

---

## Triangulated Claims

### Claim 1: Skills Format Can Represent All RaiSE Kata Metadata

**Confidence**: HIGH

**Evidence**:
1. [Agent Skills Specification](https://agentskills.io/specification) - `metadata` field is "a map from string keys to string values for additional properties not defined by the Agent Skills spec"
2. [Anthropic Skills Repository](https://github.com/anthropics/skills) - Examples show metadata for author, version, compatibility
3. [Spring AI Implementation](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/) - Successfully uses Skills with custom metadata without issues

**Disagreement**: Spec says "string→string" but RaiSE's `shuhari` is nested object. **Mitigation**: Can serialize as JSON string or flatten keys (`shuhari.shu`, `shuhari.ha`, `shuhari.ri`).

**Implication**: Technical barrier to migration is LOW.

---

### Claim 2: Skills Already Have Workflow Control Similar to RaiSE Gates

**Confidence**: HIGH

**Evidence**:
1. [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) - `disable-model-invocation` prevents automatic execution (like gates!)
2. [Agent Skills Spec](https://agentskills.io/specification) - `allowed-tools` scopes permissions
3. [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - `user-invocable: false` for background knowledge only

**Disagreement**: None found.

**Implication**: RaiSE gates can map to Skills' existing control mechanisms.

---

### Claim 3: Dual Format Creates Maintenance Burden

**Confidence**: HIGH

**Evidence**:
1. [SSOT Principles](https://strapi.io/blog/what-is-single-source-of-truth) - Multiple representations require synchronization mechanisms
2. [Wrapper Library Analysis](https://dev.to/rogeliogamez92/using-the-adapter-pattern-to-migrate-to-a-new-library-434a) - "The real challenge is knowing when a wrapper solves a problem and when it simply adds another"
3. [Red Hat Enterprise Architecture](https://www.redhat.com/en/blog/single-source-truth-architecture) - Dual sources require explicit sync processes

**Disagreement**: Wrappers CAN provide flexibility for technology swaps. But in this case, Skills isn't going away (Linux Foundation governance).

**Implication**: Option 2 (dual format) introduces maintenance cost that Option 3 avoids.

---

### Claim 4: Skills is a Long-Term Safe Bet (Industry Standard)

**Confidence**: HIGH

**Evidence**:
1. [Agentic AI Foundation](https://intuitionlabs.ai/articles/agentic-ai-foundation-open-standards) - Skills donated to Linux Foundation, governed by AAIF
2. [SkillsMP Marketplace](https://skillsmp.com/) - 71,000+ skills in ecosystem
3. [Spring AI Adoption](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/) - Major framework adopted Skills natively

**Disagreement**: Standards can still fragment or be superseded. **Mitigation**: Skills' governance model and broad adoption reduce this risk.

**Implication**: Migrating to Skills doesn't create vendor lock-in risk.

---

### Claim 5: RaiSE's Unique Value is Methodology, Not Format

**Confidence**: MEDIUM

**Evidence**:
1. [TOGAF on Open Standards](https://www.opengroup.org/togaf) - "Commercial contributors define scope of what they contribute and what they keep private"
2. [Skills vs MCP Guide](https://www.cometapi.com/claude-skills-vs-mcp-the-2026-guide-to-agentic-architecture/) - "Skills provide procedural knowledge" - methodology, not connectivity
3. Internal: RaiSE constitution values transparency and platform agnosticism

**Disagreement**: Some value may be in unique format semantics (shuhari). **Mitigation**: Shuhari can be represented in metadata; philosophy remains in content.

**Implication**: Format migration doesn't dilute RaiSE's value proposition.

---

## Patterns & Paradigm Shifts

### Pattern 1: "Specification as Interface, Methodology as Content"

Multiple sources emphasize that **format is infrastructure, content is value**:
- MCP provides connectivity, Skills provide methodology
- Spring AI provides framework, Skills provide capabilities
- RaiSE provides governance philosophy, format should be standard

**Paradigm Shift**: The era of proprietary AI workflow formats is ending. Standards consolidation is happening (Skills, MCP, A2A). Proprietary value must come from CONTENT, not FORMAT.

### Pattern 2: "Progressive Disclosure = Context Economy"

Skills' three-level loading (metadata → instructions → resources) aligns perfectly with RaiSE's inference economy principle:
- Load only what's needed
- Scripts execute without context cost
- References loaded on demand

This is not accidental - it's convergent evolution toward efficient agent architecture.

### Pattern 3: "Extensible Core, Domain-Specific Metadata"

The Skills spec's `metadata` field is intentionally minimal yet extensible:
- Core fields for universal discovery (name, description)
- Metadata for domain-specific needs (RaiSE: gates, shuhari, workflow)
- Body content for actual methodology

This matches how successful standards work (HTML, OpenAPI, etc.).

---

## Gaps & Unknowns

### Gap 1: Structured Metadata Representation

Skills spec says `metadata` is "string→string" but RaiSE's `shuhari` is:
```yaml
shuhari:
  shu: "Follow template completely"
  ha: "Adapt to context"
  ri: "Create new patterns"
```

**Options**:
1. Flatten: `shuhari.shu`, `shuhari.ha`, `shuhari.ri`
2. Serialize: `shuhari: '{"shu":"...", "ha":"...", "ri":"..."}'`
3. Move to body: Put shuhari guidance in markdown content

**Recommendation**: Option 3 - shuhari is instructional, belongs in body.

### Gap 2: Kata Chaining (next_kata, prerequisites)

Skills don't have native workflow chaining. RaiSE katas chain:
```yaml
prerequisites:
  - feature/plan
next_kata: feature/review
```

**Options**:
1. Metadata: `metadata.next_kata: feature-review`
2. Body instructions: "After completing, run `/feature-review`"
3. RaiSE Engine: Engine handles workflow, Skills are atoms

**Recommendation**: Option 3 - workflow orchestration is engine responsibility, not format responsibility.

### Gap 3: No Migration Case Studies

This is novel territory. No prior art found for migrating internal methodology formats to Skills.

**Mitigation**: Incremental migration. Start with one kata, validate, iterate.

---

## Mapping: Kata Fields → Skills Format

| Kata Field | Skills Mapping | Notes |
|------------|---------------|-------|
| `id` | `name` | Required, direct mapping |
| `titulo` | First line of body | Or `metadata.title` |
| `work_cycle` | `metadata.work_cycle` | Custom metadata |
| `frequency` | `metadata.frequency` | Custom metadata |
| `fase_metodologia` | `metadata.fase` | Custom metadata |
| `prerequisites` | `metadata.prerequisites` | Or body instructions |
| `template` | `references/` directory | Or `assets/` |
| `gate` | `metadata.gate` + body section | Gate instructions in body |
| `next_kata` | `metadata.next_kata` | Engine handles orchestration |
| `adaptable` | `metadata.adaptable` | Custom metadata |
| `shuhari` | Body section "## Mastery Levels" | Instructional content |
| `version` | `metadata.version` | Standard practice |
| (body) | Body content | Direct mapping |

**Conclusion**: All kata fields can map to Skills format.

---

*Synthesis complete - proceed to recommendation*
