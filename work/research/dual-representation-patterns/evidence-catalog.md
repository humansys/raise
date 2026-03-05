# Dual Representation Patterns: Structured Source + Generated Docs

**Research date:** 2026-03-03
**Confidence:** High (multiple independent sources per domain, well-documented ecosystems)
**Method:** Web search + synthesis across 6 domains

---

## 1. Infrastructure as Code: terraform-docs, Pulumi, CDK

### Source Format
- **Terraform:** HCL (HashiCorp Configuration Language) — domain-specific, declarative
- **Pulumi:** General-purpose languages (Python, TypeScript, Go, Java, .NET)
- **AWS CDK:** TypeScript/Python constructs compiled to CloudFormation JSON

### Generation Approach
- **terraform-docs** extracts variables, outputs, providers, resources from HCL and generates Markdown/JSON. Configured via `.terraform-docs.yml`. Runs as standalone binary or CI/CD step (GitHub Actions).
- **Pulumi** leverages IDE code-completion and type systems as "living docs" — the code IS the documentation via language-native mechanisms.
- **CDK** generates CloudFormation templates which can feed AWS documentation tools.

### Validation
- Terraform: `terraform validate` for HCL syntax + plan for semantic checks. terraform-docs does NOT validate — it only extracts.
- Pulumi: Language type system provides compile-time validation. Runtime validation via `pulumi preview`.
- No cross-cutting schema for "is the documentation complete?" — that's a gap.

### Strengths
- terraform-docs is battle-tested (5000+ GitHub stars), integrates into CI/CD trivially
- HCL as source of truth is unambiguous — variables HAVE types and descriptions
- Pulumi's approach eliminates the dual-representation problem entirely by using the code as the doc

### Limitations
- terraform-docs only documents what HCL declares — no semantic context, no "why"
- At 40+ stacks, drift between documentation and actual state is a real problem (Firefly analysis of 3000+ files)
- terraform-docs cannot detect resources managed outside Terraform
- Pulumi's "code is docs" only works for developers; non-technical stakeholders still need generated output

### Key Insight
**The generation is one-directional and shallow.** terraform-docs solves "what inputs does this module take?" but not "what does this system do?" The gap between machine-extractable metadata and human-meaningful documentation remains unfilled.

### Sources
- [terraform-docs GitHub](https://github.com/terraform-docs/terraform-docs)
- [Terraform-Docs Guide with Real-World Examples — DevToolHub](https://devtoolhub.com/terraform-docs-guide/)
- [Autogenerating Terraform Documentation — Thomas Thornton](https://thomasthornton.cloud/2025/01/22/autogenerating-terraform-documentation-with-terraform-docs-and-github-actions/)
- [Firefly: What 3000+ Terraform Files Reveal About Cloud Drift](https://www.firefly.ai/academy/what-3000-terraform-files-taught-us-about-cloud-drift)
- [Terraform vs Pulumi — Pulumi Docs](https://www.pulumi.com/docs/iac/comparisons/terraform/)

---

## 2. ADR Tools: adr-tools, MADR, log4brains

### Source Format
- **adr-tools:** Plain Markdown with numbered filenames, minimal structure (Nygard format)
- **MADR (v3+):** Markdown with **YAML front matter** for machine-parseable metadata (`status`, `date`, `decision-makers`). Body uses structured headings (Context, Decision, Consequences).
- **log4brains:** MADR as default template + filename conventions + draft status

### Generation Approach
- **log4brains** generates a **static site** (Next.js SSG) from Markdown ADR files. Supports search, filtering by status, timeline views.
- **MADR ADR-0013** explicitly chose YAML front matter over alternatives:
  - Rejected: metadata in headings (not machine-parseable)
  - Rejected: separate metadata files (violates colocation)
  - Chosen: YAML front matter — machine-parseable, standard across static site generators, colocated with content

### Validation
- MADR: Template-level (heading structure), but no schema enforcement
- log4brains: Validates filename format and basic structure during `adr new`
- No formal JSON Schema or runtime validation — relies on convention

### Strengths
- YAML front matter is the **sweet spot**: machine-readable, human-editable, standard
- Colocation of metadata and narrative in one file eliminates sync drift
- Immutability principle (only status changes) simplifies lifecycle
- log4brains provides discovery (search, timeline) without changing the source format

### Limitations
- No semantic validation ("is this decision complete?", "are consequences addressed?")
- MADR templates are conventions, not enforced schemas
- log4brains is effectively unmaintained (last meaningful commit ~2022)
- Scaling beyond ~100 ADRs becomes navigation-heavy even with static site

### Key Insight
**YAML front matter + Markdown body is the most successful "dual representation" pattern for documents.** It's adopted across ADRs, Hugo/Jekyll, Obsidian, and many other ecosystems. The pattern works because it separates "metadata for machines" from "narrative for humans" in a single file with clear boundaries.

### Sources
- [MADR ADR-0013: Use YAML front matter for metadata](https://adr.github.io/madr/decisions/0013-use-yaml-front-matter-for-meta-data.html)
- [About MADR](https://adr.github.io/madr/)
- [log4brains GitHub](https://github.com/thomvaill/log4brains)
- [ADR Tooling directory](https://adr.github.io/adr-tooling/)
- [Lullabot: Use Log4brains to manage ADRs](https://architecture.lullabot.com/adr/20210705-use-log4brains-to-manage-the-adrs/)

---

## 3. OpenAPI / AsyncAPI: Schema-First Generated Docs

### Source Format
- **OpenAPI:** YAML or JSON schema (v3.x). Defines paths, operations, request/response schemas, security.
- **AsyncAPI:** YAML or JSON (v3.x). Defines channels, messages, actions. Compatible with OpenAPI schemas, also supports Avro, Protobuf.
- Both use **JSON Schema** as the underlying type system.

### Generation Approach
- **Redoc, Swagger UI, Stoplight:** Parse OpenAPI spec → render interactive HTML docs
- **AsyncAPI Generator:** Schema → docs, code stubs, protocol-specific clients (Kafka, MQTT, AMQP)
- **SDK generators** (openapi-generator, Speakeasy): Schema → typed client libraries in multiple languages
- Key pattern: **one schema, many outputs** (docs, SDKs, mocks, tests, server stubs)

### Validation
- JSON Schema validation for structural correctness
- Spectral (Stoplight): Linting rules for API design quality (naming conventions, pagination patterns, etc.)
- Runtime contract testing: compare actual responses against spec (Dredd, Schemathesis)
- **Multi-layer**: syntax → schema → design rules → runtime conformance

### Strengths
- Most mature "structured source → generated everything" ecosystem
- Real-world ROI proven: 75% faster partner onboarding, 74% reduction in support tickets (fintech case study)
- Schema reuse across OpenAPI and AsyncAPI (same message schemas for REST and events)
- Spectral-style linting adds semantic validation on top of structural schema

### Limitations
- Schema drift: code-first frameworks can generate specs that diverge from intended design
- OpenAPI is verbose — complex APIs produce 10K+ line specs that are hard to review
- "Design-first" discipline requires organizational commitment, easy to regress to "code-first, generate spec"
- AsyncAPI tooling is less mature than OpenAPI's (smaller ecosystem)

### Key Insight
**The "one schema, many outputs" pattern is the gold standard** but requires organizational discipline to maintain schema-first workflow. The critical success factor is NOT the tooling — it's the team commitment to treat the schema as source of truth. Tools like Spectral that add semantic linting on top of structural schema validation are the differentiator.

### Sources
- [Treblle: Contract Definition using OpenAPI Specification](https://treblle.com/knowledgebase/design-phase/contract-definition-using-openapi-specification)
- [AsyncAPI: Coming from OpenAPI](https://www.asyncapi.com/docs/tutorials/getting-started/coming-from-openapi)
- [Bump.sh: AsyncAPI vs OpenAPI](https://bump.sh/blog/asyncapi-vs-openapi/)
- [Stoplight: OpenAPI](https://stoplight.io/openapi)
- [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/v3.2.0.html)

---

## 4. Backstage / TechDocs: Catalog + Documentation Portal

### Source Format
- **catalog-info.yaml:** Machine-readable entity descriptor. Required fields: `apiVersion`, `kind`, `metadata` (with `name`), `spec`. Uses annotations for cross-references (e.g., `backstage.io/techdocs-ref`).
- **TechDocs source:** Markdown files + `mkdocs.yml` configuration, living alongside code.
- **Two distinct files**: catalog metadata (YAML) for the service catalog + Markdown for human documentation.

### Generation Approach
- **Catalog:** YAML files harvested from repos, indexed in Backstage database, rendered in portal UI
- **TechDocs:** MkDocs generates static HTML from Markdown → stored in cloud storage (S3/GCS) → served through Backstage portal
- At Spotify: 5000+ documentation sites, ~10,000 daily hits

### Validation
- **JSON Schema** for entity descriptors (maintained in Backstage repo: `Entity.schema.json`, `EntityMeta.schema.json`)
- **backstage-entity-validator** (Roadie): CI/CD validation of catalog-info.yaml
- TechDocs: mkdocs build validates Markdown structure
- No validation bridge between catalog metadata and documentation content

### Strengths
- Clean separation: machine-dense catalog metadata vs. human-rich documentation
- catalog-info.yaml is simple enough that teams adopt it (low barrier)
- Entity relationships (owns, provides API, depends on) create a navigable graph
- TechDocs "docs-like-code" keeps docs near source, reducing drift

### Limitations
- **Two-file problem:** catalog-info.yaml and docs/ can drift independently. No validation that docs match catalog claims.
- TechDocs builds entire site on every request (MkDocs limitation) — slow at scale
- MkDocs-only: no support for other documentation formats
- CI/CD modification required for recommended deployment — friction for adoption
- ShadowDOM styling issues at scale
- Page load latency depends on cloud storage proximity

### Key Insight
**Backstage solves the "dual representation" problem by NOT trying to merge them.** Structured catalog data lives in YAML, human docs live in Markdown, and the portal stitches them together at display time. The weakness is that there's no validation that the two representations are consistent — the catalog says "this service provides API X" but nothing checks that the docs actually describe API X.

### Sources
- [Backstage TechDocs](https://backstage.io/docs/features/techdocs/)
- [Backstage Descriptor Format](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [Roadie: How TechDocs Works](https://roadie.io/blog/how-techdocs-works/)
- [Backstage Entity Validator](https://github.com/RoadieHQ/backstage-entity-validator)
- [Backstage TechDocs Architecture](https://backstage.io/docs/features/techdocs/architecture/)
- [Backstage 101](https://backstage.spotify.com/discover/backstage-101)

---

## 5. CUE / Dhall / Jsonnet: Configuration Languages

### Source Format
- **CUE:** Constraint-based, unification-based. Types and data are the same thing. Values can only be constrained further, never relaxed.
- **Dhall:** Functional, typed configuration language. Totality guarantee (programs always terminate). Imports with integrity checks.
- **Jsonnet:** Data templating (boilerplate removal). Extends JSON with variables, functions, conditionals.

### Generation Approach
- All three **evaluate to JSON/YAML** — they're source languages that compile to standard data formats
- CUE: `cue export` → JSON/YAML. Also supports `cue fmt` for canonical formatting.
- Dhall: `dhall-to-json`, `dhall-to-yaml`
- Jsonnet: `jsonnet` → JSON

### Validation
- **CUE:** Built-in constraint validation. Schema IS the validation — disjunctions, bounds, regex. "No amount of other rules can change established constraints" (monotonic). Strongest validation story.
- **Dhall:** Type system with totality checking. Catches type errors at evaluation time.
- **Jsonnet:** No built-in validation beyond JSON structure. Relies on external validators.

### Strengths
- CUE's unification model: schema, data, and policy are the SAME language. No separate validation step.
- CUE is "machine-readable AND writable, human-readable AND writable" — explicit design goal
- Dhall's totality guarantee prevents infinite loops in configuration
- All three eliminate boilerplate that makes raw JSON/YAML unreadable at scale

### Limitations
- **Adoption barrier:** All three require learning a new language. CUE and Dhall especially have steep learning curves.
- CUE is still pre-1.0 (as of 2025), with breaking changes possible
- Jsonnet lacks typing — you get boilerplate reduction without safety
- CUE's ecosystem is small compared to raw YAML tooling
- None solve the "human narrative" problem — they're for structured data, not documentation

### Key Insight
**CUE's insight is the deepest: schema and data should be the same language, with constraints that only narrow.** This eliminates the "source of truth" question entirely — there's one representation that serves both validation and data. However, CUE addresses the machine↔machine dual representation, not the machine↔human one. You still need separate documentation for humans.

### Sources
- [CUE: How CUE enables configuration](https://cuelang.org/docs/concept/how-cue-enables-configuration/)
- [CUE: How CUE enables data validation](https://cuelang.org/docs/concept/how-cue-enables-data-validation/)
- [Taming the Beast: Comparing Jsonnet, Dhall, CUE](https://pv.wtf/posts/taming-the-beast)
- [Cloudplane: Why We Use CUE](https://cloudplane.org/blog/why-cue)
- [Holos: Why CUE for Configuration](https://holos.run/blog/why-cue-for-configuration/)
- [KCL: Declarative Configuration Landscape](https://www.kcl-lang.io/blog/2022-declarative-config-overview)

---

## 6. Design Tokens: Style Dictionary, W3C DTCG

### Source Format
- **Style Dictionary:** JSON (historically). Hierarchical token tree: category → item → sub-item → state.
- **W3C DTCG (2025.10 — first stable release):** JSON with `$value`, `$type`, `$description` prefixed properties. Media type: `application/design-tokens+json`. File extension: `.tokens` or `.tokens.json`.
- Groups (objects without `$value`) vs. tokens (objects with `$value`) — presence of `$value` is the discriminator.

### Generation Approach
- **Style Dictionary:** Transforms + formats pipeline. Token JSON → platform-specific outputs:
  - CSS custom properties
  - SCSS variables
  - iOS Swift constants
  - Android XML resources
  - JavaScript/TypeScript modules
- Custom transforms and formats are extensible
- **Tokens Studio:** Figma plugin → DTCG JSON → Style Dictionary → platform outputs

### Validation
- **DTCG spec:** JSON Schema for structural validation. `$type` constrains valid `$value` shapes.
- **Design Token Validator:** Web tool validates against W3C DTCG spec
- **Semantic validation:** Token references (e.g., `button.primary` → `color.blue`) validated during resolution
- Style Dictionary v4: validates reference integrity during build

### Strengths
- **Most complete "one source, N outputs" pipeline** for a specific domain
- W3C standardization (2025.10) with backing from Adobe, Google, Microsoft, Meta, Figma, etc.
- Reference integrity: semantic tokens reference primitive tokens, changes propagate automatically
- Style Dictionary's extensibility model (custom transforms, formats, filters) handles edge cases

### Limitations
- DTCG format cannot combine with legacy Style Dictionary format in one instance
- Type conversion between formats is lossy (e.g., `size` vs `dimension`)
- Only for visual design properties — doesn't cover interaction patterns, motion specs, etc.
- Tooling ecosystem still fragmenting around DTCG adoption timing

### Key Insight
**Design tokens demonstrate the most successful domain-specific dual-representation pattern.** The key is that the source format (JSON with typed tokens) is close enough to both machine needs (typed, hierarchical, referenceable) and human needs (named, categorized, described) that one format genuinely serves both. The `$description` field in DTCG and the hierarchical naming provide human context without separate documentation. Platform-specific output is purely mechanical transformation.

### Sources
- [W3C DTCG: Design Tokens Specification 2025.10](https://www.designtokens.org/tr/drafts/format/)
- [W3C: Design Tokens Specification Reaches First Stable Version](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/)
- [Style Dictionary: DTCG support](https://styledictionary.com/info/dtcg/)
- [Style Dictionary GitHub](https://github.com/style-dictionary/style-dictionary)
- [Tokens Studio: SD-Transforms](https://docs.tokens.studio/transform-tokens/style-dictionary)

---

## Cross-Cutting Findings

### Pattern Taxonomy

| Pattern | Examples | Source Format | Human Output | Validation |
|---------|----------|--------------|--------------|------------|
| **Extract & Generate** | terraform-docs, OpenAPI → Redoc | DSL/Schema | Generated HTML/MD | Schema only |
| **Front Matter + Body** | MADR, Hugo, Obsidian | YAML header + Markdown | Static site | Convention only |
| **Separate Files, Portal Stitching** | Backstage catalog + TechDocs | YAML + Markdown | Portal UI | Schema for each, no cross-validation |
| **Schema IS Data IS Validation** | CUE, DTCG | Constraint language / Typed JSON | Evaluated output | Built into the language |
| **One Source, N Platforms** | Style Dictionary, OpenAPI generators | Typed JSON/YAML | Platform-specific code | Reference integrity + type checking |

### What Works

1. **YAML front matter + Markdown body** is the most widely adopted pattern for documents that need both machine-parseable metadata and human narrative. It's simple, standard, and survives across ecosystems.

2. **Schema-first with linting** (OpenAPI + Spectral) is the gold standard for API-like structures. The schema provides structural validation; linting rules add semantic quality checks.

3. **Typed token formats** (DTCG) work when the domain is narrow enough that one format serves both audiences. The `$description` pattern (machine property that carries human meaning) is elegant.

4. **CUE's monotonic constraints** solve the "which representation is authoritative?" problem by making schema and data the same thing. Adoption cost is high.

### What Doesn't Work

1. **Two-file separation without cross-validation** (Backstage pattern) leads to drift. The catalog says one thing, the docs say another, and nothing catches it.

2. **Generation from code without narrative** (terraform-docs) produces reference documentation but not understanding. The "why" always lives elsewhere.

3. **Convention-only validation** (MADR templates) doesn't scale. Without schema enforcement, ADRs degrade in quality as team size grows.

4. **Separate toolchains for validation and generation** create maintenance burden. CUE and DTCG avoid this by unifying them.

### Recommendations for RaiSE Context

Given the research, the most applicable patterns for a governance/documentation system:

1. **YAML front matter + Markdown body** for any document that needs both machine parsing and human reading. This is the proven pattern (MADR, Hugo, Obsidian, etc.).

2. **JSON Schema validation** for the structured portion. Not just syntax — add semantic rules like Spectral does for OpenAPI.

3. **Reference integrity checking** like Style Dictionary does for token references. If document A references document B, validate the reference resolves.

4. **Single-file colocation** over multi-file separation. MADR's ADR-0013 decision is instructive: colocating metadata and narrative in one file eliminates an entire class of drift bugs.

5. **Avoid the Backstage trap**: if you must separate structured data from docs, add cross-validation. Without it, drift is guaranteed at scale.
