# Prior Art & Epistemological Grounding

> Research for E9/E10 signal design
> Date: 2026-02-02
> ID: RES-LINEAGE-002

---

## Purpose

Ground our local learning and collective intelligence design in:
1. **Industry standards** — OpenTelemetry, semantic conventions
2. **Epistemological frameworks** — What makes knowledge valid?
3. **Prior art** — Who's done this? What works?
4. **Integration readiness** — Multi-vendor considerations

---

## 1. OpenTelemetry: The Standard

### Signal Types

[OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/) defines four primary signals:

| Signal | Definition | Our equivalent |
|--------|------------|----------------|
| **Traces** | Path of a request through the system | Session lifecycle |
| **Metrics** | Measurement captured at runtime | Calibration data |
| **Logs** | Recording of an event | Signal events |
| **Events** | Special type of log (named occurrence) | skill_event, error_event |

### Semantic Conventions

[Semantic Conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/) provide standardized attribute naming:

> "The benefit to using Semantic Conventions is in following a common naming scheme that can be standardized across a codebase, libraries, and platforms."

**Event requirements:**
- Must have `event.name` (unique identifier)
- Optional payload (body)
- Relevant attributes for context

**Attribute namespacing:**
- Group by concept: `k8s.*`, `http.*`, etc.
- Custom attributes: use reverse domain (`com.example.*`)
- Avoid conflicts with existing namespaces

### Alignment Recommendation

Map our signals to OTel patterns:

| Our signal | OTel equivalent | Namespace |
|------------|-----------------|-----------|
| skill_event | Event (LogRecord) | `raise.skill.*` |
| session_event | Event | `raise.session.*` |
| calibration | Metric | `raise.calibration.*` |
| error_event | Event | `raise.error.*` |
| command_usage | Event | `raise.cli.*` |

**Why align?**
- Future integration with observability stacks
- Familiar patterns for developers
- Export to standard formats (OTLP)

---

## 2. Epistemological Grounding

### What Makes Knowledge Valid?

From epistemological research:

> "Epistemological frameworks provide criteria for assessing the reliability and trustworthiness of knowledge claims."

**Key principles:**

1. **Triangulation** — Multiple sources of evidence strengthen validity
2. **Confidence levels** — Explicit uncertainty acknowledgment
3. **Provenance** — Traceability to sources
4. **Falsifiability** — Claims should be testable

### Application to Our Signals

| Principle | How we apply it |
|-----------|-----------------|
| **Triangulation** | Combine signals: calibration + session outcome + skill completion |
| **Confidence** | Sample size in insights: "Based on 12 features..." |
| **Provenance** | Lineage tracks where patterns came from |
| **Falsifiability** | Insights are hypotheses: "Your S estimates may be optimistic" |

### Insight Confidence Model

```json
{
  "insight": "S estimates trending 1.5x optimistic",
  "confidence": "high",
  "evidence": {
    "sample_size": 12,
    "signal_types": ["calibration", "session_event"],
    "time_range": "30 days",
    "consistency": 0.85
  }
}
```

**Confidence levels:**
- `high` — 10+ samples, consistent pattern, triangulated
- `medium` — 5-10 samples, or single signal source
- `low` — <5 samples, or contradictory signals

### The Qualified vs Quantified Self

From research on [Quantified Self](https://en.wikipedia.org/wiki/Quantified_self):

> "The quantified self provided a foundation for self-awareness, but its reliance on metrics limited its impact. Numbers revealed patterns but often failed to provide meaning."

**Evolution:** Quantified Self → Qualified Self

| Quantified | Qualified |
|------------|-----------|
| Raw metrics | Interpreted insights |
| "You spent 45min" | "This was 33% faster than typical" |
| Data collection | Meaning-making |

**Rai's role:** Bridge the gap — collect quantified signals, generate qualified insights.

---

## 3. PDCA/PDSA: The Learning Loop

### Deming's Cycle

From [The Deming Institute](https://deming.org/explore/pdsa/):

> "PDSA is a systematic process for gaining valuable learning and knowledge for the continual improvement of a product, process, or service."

```
    ┌─────────────────┐
    │      PLAN       │ ← Hypothesis: "S features take 45min"
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │       DO        │ ← Execute: Work on feature
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │     STUDY       │ ← Analyze: "Took 30min, 1.5x velocity"
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │      ACT        │ ← Adjust: Update calibration model
    └────────┴────────┘
             │
             └─────────────► (next cycle)
```

**Key insight:** Deming preferred PDSA (Study) over PDCA (Check):

> "Dr. Deming found that the focus on Check is more about the implementation of a change, with success or failure. His focus was on predicting the results of an improvement effort, studying the actual results, and comparing them to possibly revise the theory."

### Application to E9

| PDSA Phase | E9 Implementation |
|------------|-------------------|
| **Plan** | Estimate size, predict duration |
| **Do** | Execute with signals emitted |
| **Study** | Analyze signals, compare to prediction |
| **Act** | Generate insight, update calibration |

**The spiral:** Each cycle improves the model. Rai gets better at predicting *your* patterns over time.

---

## 4. Prior Art: Tools That Learn

### VSCode/Copilot Telemetry

From [VSCode Telemetry docs](https://code.visualstudio.com/docs/getstarted/telemetry):

- Opt-in/opt-out via settings
- Collects usage patterns to improve features
- Microsoft sees "more users using AI features than debugging"

**Lesson:** Telemetry reveals what actually matters to users.

### Kilo Code (Local-First Alternative)

From [Kilo Code](https://skywork.ai/blog/kilo-code-ai-review-2025-open-source-agentic-vs-copilot/):

- Local models + BYO keys
- "No lock-in" philosophy
- Privacy-first with optional telemetry

**Lesson:** Local-first with opt-in sharing is viable and valued.

### InfraNodus (PKM + AI)

From [Nodus Labs](https://support.noduslabs.com/):

- Visualizes knowledge as network graph
- Pattern identification across notes
- AI-generated insights from your knowledge

**Lesson:** Graph + AI can surface non-obvious patterns.

### Quantified Self Movement

From research:

- Privacy concerns are primary barrier
- Local-first storage preferred
- Decentralized architectures emerging
- Aggregation/visualization limited without tooling

**Lesson:** Build aggregation and insight generation locally first.

---

## 5. Privacy Considerations

### The Privacy Spectrum

| Level | What's shared | Trust required |
|-------|---------------|----------------|
| **None** | Nothing leaves device | Zero |
| **Anonymous** | Aggregate signals, no identity | Low |
| **Attributed** | Signals with user credit | Medium |
| **Team/Org** | Shared within boundary | Policy-based |

### Privacy-Respecting Patterns

From research:

1. **Local-first storage** — Data stays on device by default
2. **Opt-in sharing** — Explicit consent required
3. **Anonymization** — Strip identifying information
4. **Transparency** — User can see what's collected
5. **Deletion** — User can remove their data

### Our Commitment

```
Local (always)              Shared (opt-in only)
─────────────────           ────────────────────
Full signals                → Anonymized summaries
Full patterns               → Patterns with lineage
Identity                    → Never shared
File paths                  → Never shared
Code content                → Never shared
```

---

## 6. Integration Readiness

### Multi-Vendor Considerations

Future stack might include:
- **Observability:** Grafana, DataDog, New Relic (via OTLP)
- **Analytics:** PostHog, Amplitude (for aggregate)
- **Storage:** TimescaleDB, ClickHouse (for time-series)
- **Identity:** Auth0, Clerk (for team/org scopes)

### OTLP Export Path

If we follow OpenTelemetry conventions:

```
.rai/telemetry/signals.jsonl
         │
         ▼
  raise telemetry export --format otlp
         │
         ▼
  OpenTelemetry Collector
         │
    ┌────┴────┐
    ▼         ▼
 Grafana   DataDog
```

**Why this matters:**
- Enterprise customers have existing observability stacks
- OTLP is the lingua franca
- We don't need to build visualization — integrate with what exists

### Semantic Convention Compliance

To be integration-ready:

1. Use OTel attribute naming patterns
2. Include standard fields (timestamp, severity, etc.)
3. Support OTLP export format
4. Document our custom semantic conventions

---

## 7. Recommendations

### For E9 (Local Learning)

1. **Follow OTel patterns** — Use event/attribute structure
2. **Namespace signals** — `raise.*` prefix for all
3. **Include confidence** — Every insight has evidence
4. **PDSA loop** — Study, don't just check
5. **Local-first** — No network by default

### For E10 (Collective)

1. **Lineage always** — Every shared pattern has provenance
2. **Opt-in only** — Never share without consent
3. **Anonymize by default** — Attribution is opt-in
4. **OTLP-ready** — Export format for enterprise

### Schema Example (OTel-aligned)

```json
{
  "timestamp": "2026-02-02T14:30:00Z",
  "severity": "INFO",
  "event.name": "raise.skill.complete",
  "attributes": {
    "raise.skill.name": "story-design",
    "raise.skill.duration_sec": 1800,
    "raise.session.id": "ses-123",
    "raise.feature.id": "F8.1"
  }
}
```

---

## Sources

### Standards & Specifications
- [OpenTelemetry Signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/)
- [Semantic Conventions for Events](https://opentelemetry.io/docs/specs/semconv/general/events/)
- [OpenTelemetry Guide (Better Stack)](https://betterstack.com/community/guides/observability/opentelemetry-semantic-conventions/)

### Epistemology & Learning
- [Epistemology (Wikipedia)](https://en.wikipedia.org/wiki/Epistemology)
- [PDSA Cycle (Deming Institute)](https://deming.org/explore/pdsa/)
- [PDCA (Wikipedia)](https://en.wikipedia.org/wiki/PDCA)
- [Triangulation in Research](https://www.tandfonline.com/doi/full/10.1080/13645579.2019.1630901)

### Prior Art
- [Quantified Self (Wikipedia)](https://en.wikipedia.org/wiki/Quantified_self)
- [VSCode Telemetry](https://code.visualstudio.com/docs/getstarted/telemetry)
- [Kilo Code Review](https://skywork.ai/blog/kilo-code-ai-review-2025-open-source-agentic-vs-copilot/)
- [InfraNodus PKM](https://support.noduslabs.com/hc/en-us/articles/6455436092690--PKM-Workflow-AI-generated-Insights-for-Your-Obsidian-LogSeq-Knowledge-Graphs)
- [Best PKM Tools 2024](https://support.noduslabs.com/hc/en-us/articles/13449999219484-Best-PKM-Tools-in-2024-Obsidian-vs-Roam-Research-vs-Evernote-vs-Notion)

### Privacy
- [Copilot Privacy Configuration](https://paulsorensen.io/github-copilot-vscode-privacy/)
- [Quantified Self Privacy Concerns](https://medium.com/@ann_p/from-quantified-self-to-qualitative-self-ai-shifting-focus-in-personal-analytics-68209a851322)

---

*Research document for E9/E10 epistemological grounding*
*Contributors: Emilio Osorio, Rai*
*Session: 2026-02-02*
