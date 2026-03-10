# Structured Process Artifacts: Evidence Catalog

> Research: How development frameworks model process artifacts as structured, verifiable data.
> Date: 2026-03-03
> Status: Complete

---

## 1. DORA / SPACE Metrics

### Format & Structure

**DORA** defines 5 metrics (originally 4) as structured event streams:
- Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore, Reliability (new in 2025)
- Data is collected as **timestamped events** (deployments, incidents, commits) rather than free-form text
- Tools like Datadog expose DORA via a **REST API** accepting JSON events with typed fields and up to 100 custom key:value tags
- LeanIX VSM uses **CloudEvents format** for DORA event ingestion (change, release, incident event types)
- Apache DevLake collects raw data from Git, CI/CD, issue trackers and computes DORA metrics from structured event logs

**SPACE** (Satisfaction, Performance, Activity, Communication, Efficiency) is a multi-dimensional framework:
- Combines quantitative signals (from systems) with qualitative signals (surveys)
- No single standard format; implementation varies by tooling
- Key insight: "only by examining a constellation of metrics in tension" can you understand productivity

### Schema / Validation

- DORA metrics have **implicit schemas** — each metric has a defined calculation formula
- Datadog's API enforces typed fields: `started_at` (int64 timestamp), `finished_at`, `git.repository_url`, `git.commit.sha`, `env`, `service`
- The 2025 DORA report moved from 4-level classification (low/medium/high/elite) to **7 team archetypes** — more nuanced structured taxonomy

### Structure vs Expressiveness Balance

- Metrics themselves are **purely structural** — no free-form content
- The interpretive layer (team context, organizational factors) remains unstructured
- Key pattern: **structured events in, structured metrics out, human interpretation on top**

### Scale Challenges

- Automated collection via CI/CD integrations is the recommended practice
- Manual reporting creates measurement bias
- Cross-team comparisons require normalized event schemas

### Confidence: High
### Sources
- [Atlassian DORA Metrics](https://www.atlassian.com/devops/frameworks/dora-metrics)
- [DORA 2025 Measurement Frameworks](https://dora.dev/research/2025/measurement-frameworks/)
- [DORA 5th Metric - CD Foundation](https://cd.foundation/blog/2025/10/16/dora-5-metrics/)
- [Datadog DORA API](https://docs.datadoghq.com/api/latest/dora-metrics/)
- [SPACE Framework - ACM Queue](https://queue.acm.org/detail.cfm?id=3454124)
- [Nicole Forsgren on AI Developer Productivity](https://www.lennysnewsletter.com/p/how-to-measure-ai-developer-productivity)

---

## 2. CI/CD Typed Artifact Reports (GitHub Actions / GitLab CI)

### Format & Structure

**GitLab CI** defines a comprehensive **typed artifact report system** in YAML pipeline config:

| Report Type | Format | Purpose |
|---|---|---|
| `junit` | JUnit XML | Test results |
| `codequality` | JSON (Code Climate) | Code quality issues |
| `sast` | JSON (SARIF-like) | Security vulnerabilities |
| `dast` | JSON | Dynamic security scanning |
| `container_scanning` | JSON | Container vulnerabilities |
| `dependency_scanning` | JSON | Dependency vulnerabilities |
| `coverage_report` | Cobertura/JaCoCo XML | Test coverage |
| `terraform` | JSON (tfplan.json) | Infrastructure plan |
| `accessibility` | JSON (pa11y) | Accessibility issues |
| `dotenv` | KEY=VALUE | Environment variables |
| `requirements` | JSON | Requirements satisfaction |
| `metrics` | Custom | Custom metrics |
| `repository_xray` | JSON | Repository analysis for AI |

Key design: artifacts are declared as **typed** in pipeline YAML, GitLab knows how to render each type in the MR UI.

**GitHub Actions** artifacts are more generic:
- `upload-artifact` / `download-artifact` with digest validation (v4+, 2025)
- No built-in typed report system — relies on third-party Actions for schema validation
- Integrity via SHA-256 digest comparison between upload and download

### Schema / Validation

- GitLab: Each report type has an **expected format** (JUnit XML, Code Climate JSON, etc.)
- GitLab: "Artifacts created for `artifacts: reports` are always uploaded, regardless of job results"
- GitHub: Community actions provide JSON Schema validation (e.g., `schema-validation-action`, `json-schema-validate`)
- GitHub: Workflow YAML itself has a schema validated by tools like `action-validator`

### Structure vs Expressiveness Balance

- **Brilliant pattern**: Pipeline config (YAML) declares artifact type; artifact content follows type-specific schema; CI system renders appropriately in UI
- The pipeline author doesn't define the schema — they declare the artifact type, and the system knows the rest
- This is **type declaration, not schema definition** — much simpler for users

### Scale Challenges

- GitLab's approach scales well because adding new report types is a platform concern, not a user concern
- GitHub's generic approach requires more ecosystem coordination but is more flexible
- Multiple JUnit XML files can be concatenated; Cobertura/JaCoCo reports are automatically aggregated

### Confidence: High
### Sources
- [GitLab CI Artifacts Reports Types](https://docs.gitlab.com/ci/yaml/artifacts_reports/)
- [GitHub Actions Artifact Digest Validation](https://github.blog/changelog/2025-03-18-github-actions-now-supports-a-digest-for-validating-your-artifacts-at-runtime/)
- [GitHub upload-artifact](https://github.com/actions/upload-artifact)

---

## 3. SARIF (Static Analysis Results Interchange Format)

### Format & Structure

- **JSON** format, OASIS standard (v2.1.0)
- Hierarchical structure: `$schema` > `version` > `runs[]` > `tool` + `results[]` + `artifacts[]`
- Each `run` contains:
  - `tool.driver`: name, version, semantic version, rules definitions
  - `results[]`: individual findings with severity, location, rule ID, message, suggested fixes
  - `artifacts[]`: files scanned/referenced with location URIs
  - `invocations[]`: how the tool was invoked

Key structural elements:
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "ToolName",
        "rules": [{ "id": "RULE001", "shortDescription": {...} }]
      }
    },
    "results": [{
      "ruleId": "RULE001",
      "level": "error",
      "message": { "text": "..." },
      "locations": [{ "physicalLocation": { "artifactLocation": { "uri": "..." } } }]
    }]
  }]
}
```

### Schema / Validation

- Full JSON Schema published by OASIS TC: `sarif-schema-2.1.0.json`
- Schema enforces required fields, enum values (e.g., `level`: error/warning/note/none)
- Tools like GitHub Code Scanning consume SARIF and validate against schema
- Extensibility via `properties` bags on most objects — structured extension point

### Structure vs Expressiveness Balance

- **Rules are defined once, referenced many times** — deduplication pattern
- Messages can use markdown for human readability within structured containers
- `properties` bags allow tool-specific extensions without breaking schema validation
- This is the **"structured envelope with free-form payload"** pattern

### Scale Challenges

- Multiple tools producing SARIF can be aggregated (same schema)
- Large codebases produce large SARIF files — streaming/pagination not part of spec
- Rule ID namespacing across tools requires conventions

### Key Insight
SARIF's success comes from separating **tool metadata** (who found it), **rule definitions** (what was looked for), and **results** (what was found) into distinct, cross-referenced structures. This separation of concerns enables aggregation across tools.

### Confidence: Very High
### Sources
- [SARIF v2.1.0 OASIS Standard](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [SARIF JSON Schema](https://github.com/oasis-tcs/sarif-spec/blob/main/sarif-2.1/schema/sarif-schema-2.1.0.json)
- [Sonar Complete Guide to SARIF](https://www.sonarsource.com/resources/library/sarif/)
- [SARIF Home](https://sarifweb.azurewebsites.net/)

---

## 4. JUnit/xUnit XML

### Format & Structure

- **XML** format, originally from JUnit ANT task (no official spec — de facto standard)
- Hierarchy: `<testsuites>` > `<testsuite>` > `<testcase>` > result elements

```xml
<testsuites disabled="" errors="" failures="" name="" tests="" time="">
  <testsuite disabled="" errors="" failures="" hostname="" id=""
             name="" package="" skipped="" tests="" time="" timestamp="">
    <testcase assertions="" classname="" name="" status="" time="">
      <failure message="" type="">stacktrace</failure>
      <error message="" type="">stacktrace</error>
      <skipped message=""/>
      <system-out>stdout capture</system-out>
      <system-err>stderr capture</system-err>
    </testcase>
    <properties>
      <property name="" value=""/>
    </properties>
  </testsuite>
</testsuites>
```

- Test passes **by absence** — no child elements = pass (elegant simplicity)
- `<failure>` = assertion failed (expected behavior); `<error>` = unexpected exception
- `<properties>` enable extensibility without breaking schema

### Schema / Validation

- Community-maintained XSD schemas exist (e.g., `windyroad/JUnit-Schema`)
- No single authoritative schema — evolved organically from Ant/JUnit
- Most CI tools (Jenkins, GitLab, GitHub) are **lenient parsers** — accept variations
- The lack of strict schema was actually a feature for adoption

### Structure vs Expressiveness Balance

- **Minimal required structure**: name + time per test case; everything else optional
- Free-form text only in stdout/stderr captures and failure messages
- The format succeeds because it captures **just enough** — name, timing, pass/fail, error details
- No attempt to capture test logic, only test outcomes

### Scale Challenges

- File size grows linearly with test count — simple concatenation works
- Multiple files can be aggregated (GitLab supports glob patterns)
- No built-in pagination or streaming
- Timestamp format varies across implementations (ISO 8601 vs epoch)

### Key Insight
JUnit XML's success formula: **low barrier to produce + universal consumption + pass-by-absence simplicity**. The lack of an official schema paradoxically helped adoption — tools could emit "close enough" XML and consumers would parse it. This is the **"tolerant reader"** pattern at format level.

### Confidence: Very High
### Sources
- [JUnit XML Format Specification (testmoapp)](https://github.com/testmoapp/junitxml)
- [JUnit XSD Schema](https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd)
- [JUnit XML definition and best practices](https://theembeddedkit.io/blog/junit-xml/)
- [JUnit XML for Jenkins](https://llg.cubic.org/docs/junit/)

---

## 5. SPDX / CycloneDX (SBOMs)

### Format & Structure

**CycloneDX** (OWASP):
- Formats: JSON, XML, Protocol Buffers
- Current: v1.7 (October 2025)
- Scope: SBOM, SaaSBOM, HBOM, AI/ML-BOM, CBOM, OBOM, MBOM, VDR, VEX
- Structure: `bomFormat` + `specVersion` + `components[]` + `dependencies[]` + `vulnerabilities[]` + `services[]`
- Extensibility via **properties** (key-value pairs at any level: BOM, component, service)

**SPDX** (Linux Foundation, ISO/IEC 5962:2021):
- Formats: JSON, XML, YAML, tag-value, Excel spreadsheets, RDF
- Current: v3.0
- Originally designed for **license compliance** — broader than security focus
- Richer vocabulary for licenses, copyrights, relationships between packages
- Structure: `SPDXDocument` > `packages[]` + `relationships[]` + `files[]` + `snippets[]`

### Schema / Validation

- Both have **official JSON Schemas** published by their standards bodies
- CycloneDX provides a **hardened JSON schema** for high-assurance environments
- `sbom-utility` tool validates against both CycloneDX and SPDX schemas
- Both support version-specific schema validation

### Structure vs Expressiveness Balance

- CycloneDX: **security-first**, lean, easy to produce — lower barrier to entry
- SPDX: **compliance-first**, comprehensive, richer expressiveness — higher complexity
- Both approved under US Executive Order 14028 (2021) — regulatory requirement drove adoption
- CycloneDX v1.7 added "Citations" — trace where BOM data originated (provenance metadata)

### Scale Challenges

- Large monorepos generate massive SBOMs — need for hierarchical/compositional BOMs
- Cross-format conversion exists but is lossy (SPDX <-> CycloneDX)
- Automated generation from package managers (npm, pip, maven) is mature
- Manual curation doesn't scale — automation is essential

### Key Insight
Two competing standards emerged because **different stakeholders have different primary concerns** (security vs. compliance). Both succeeded by having: official schemas, tooling ecosystems, regulatory backing, and automation-first generation. The **regulatory mandate** was the adoption forcing function — not technical superiority.

### Confidence: High
### Sources
- [CycloneDX Specification Overview](https://cyclonedx.org/specification/overview/)
- [SPDX vs CycloneDX Comparison (Harness)](https://developer.harness.io/docs/software-supply-chain-assurance/how-to-guides/spdx-vs-cyclonedx/)
- [SBOM Formats Comparison](https://sbomgenerator.com/learn/sbom-formats)
- [CycloneDX sbom-utility](https://github.com/CycloneDX/sbom-utility)
- [Sonatype SBOM Standards Comparison](https://www.sonatype.com/blog/comparing-sbom-standards-spdx-vs.-cyclonedx-vs.-swid)

---

## 6. Architectural Decision Records (MADR)

### Format & Structure

**MADR** (Markdown Any Decision Records) uses **YAML frontmatter + structured Markdown sections**:

```yaml
---
status: "{proposed | rejected | accepted | deprecated | superseded by ADR-0123}"
date: 2026-03-03
decision-makers: [list of people]
consulted: [subject matter experts]
informed: [stakeholders kept up to date]
---
# {short title, present tense verb phrase}

## Context and Problem Statement
{free-form, 2-3 sentences or illustrative story}

## Decision Drivers
* {driver 1}
* {driver 2}

## Considered Options
* {option 1}
* {option 2}

## Decision Outcome
Chosen option: "{option N}", because {justification}

### Consequences
* Good, because {positive consequence}
* Bad, because {negative consequence}

## Pros and Cons of the Options
### {option 1}
* Good, because {argument a}
* Bad, because {argument b}
```

Template variants: full annotated, full bare, minimal annotated, minimal bare.

**Decision Reasoning Format (DRF)**: An emerging vendor-neutral YAML/JSON format for decisions with explicit reasoning, assumptions, cognitive state, and trade-offs. Designed to complement ADRs with structured, validatable reasoning.

### Schema / Validation

- MADR has **no formal schema** — relies on template structure and convention
- YAML frontmatter is parseable by any YAML parser
- Markdown sections follow naming convention but aren't machine-enforced
- DRF aims to be **schema-validated** — machine-readable decisions
- Tools like `adr-tools` enforce file naming conventions (sequential numbering)

### Structure vs Expressiveness Balance

- **YAML frontmatter** = machine-readable metadata (status, date, people)
- **Markdown body** = human-readable reasoning (context, options, consequences)
- This **hybrid pattern** is widely successful: structured header + expressive body
- The "minimal" template variant strips to just: Context, Decision Outcome — recognizing that teams need different levels of formality

### Scale Challenges

- Discoverability becomes hard with many ADRs — tools needed for search
- Cross-referencing between ADRs is manual (superseded by links)
- Status tracking requires discipline — stale ADRs accumulate
- Recent trend: making ADRs machine-readable for AI code assistants to parse and apply

### Key Insight
MADR's adoption pattern: **start with the lightest version that works, add structure when needed**. The 4 template variants (full/minimal x annotated/bare) explicitly acknowledge that different contexts need different formality levels. The frontmatter+markdown hybrid is the dominant pattern for "structured enough" documents.

### Confidence: High
### Sources
- [MADR Official Site](https://adr.github.io/madr/)
- [MADR GitHub](https://github.com/adr/madr)
- [MADR YAML Frontmatter Decision](https://adr.github.io/madr/decisions/0013-use-yaml-front-matter-for-meta-data.html)
- [MADR Template Primer (Ozimmer)](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html)
- [ADR as AI Guidance](https://daily-devops.net/posts/instruction-by-design/)

---

## 7. RFC Processes at Scale

### Format & Structure

**Uber:**
- Evolved from DUCK format to RFC documents
- Built a centralized **engineering planning tool** (searchable, with approvers, JIRA integration)
- Two template weights: **lightweight** (team-scope changes) and **heavyweight** (org/company-wide)
- Templates include mandatory fields: reliability, scale, security, SLAs, load/performance testing
- No machine-readable format — structured Markdown/Google Docs with required sections

**Google:**
- "Design Docs" with a typical structure (not publicly detailed)
- Reviewed via internal tools with structured review/approval workflows

**Meta/Facebook:**
- Notably **least formal** — some teams use 1-pagers, but no company-wide RFC process
- "Least emphasis on documentation across all of Big Tech" (Pragmatic Engineer)

**Common patterns across companies (from Pragmatic Engineer survey):**
- Companies using RFCs: Uber, Spotify, HashiCorp, Rust (open source), Artsy, Oxide, Flutter, Gatsby
- Most use structured Markdown templates with required sections
- None found to use machine-readable formats — all are human-readable with workflow tooling on top

### Schema / Validation

- No formal schemas — validation is **social** (peer review, required approvals)
- Workflow tooling enforces **process** (who must approve) rather than **content structure**
- Uber integrated approval requirements into their task/project management system
- The closest to "validation" is template compliance — did you fill in all required sections?

### Structure vs Expressiveness Balance

- Templates provide **section structure** (required headings) but sections contain free-form text
- The heaviest structure is in **metadata** (author, reviewers, status, date) not content
- Multiple template weights address the "one size doesn't fit all" problem
- Design docs need to **persuade**, not just inform — this inherently requires expressiveness

### Scale Challenges

- Discoverability: centralized tools (Uber's planning tool) vs scattered docs
- Stale documents: no automated status tracking
- Cross-referencing: manual links between related RFCs
- Template compliance: manual review, no automated validation

### Key Insight
At scale, RFC processes solve a **coordination problem**, not a documentation problem. The value is in the **social workflow** (who reviews, who approves, who is notified) more than the document format. Machine-readable components are limited to metadata (author, status, approvers) — the reasoning content remains free-form by necessity, because its purpose is persuasion and context-sharing.

### Confidence: Medium-High
### Sources
- [Scaling Engineering Teams via RFCs (Pragmatic Engineer)](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- [Engineering Planning with RFCs, Design Docs and ADRs](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)
- [RFC and Design Doc Examples and Templates](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design)
- [Uber H3 RFC Template](https://github.com/uber/h3/blob/master/dev-docs/RFCs/rfc-template.md)
- [Planning for Change with RFCs (Increment)](https://increment.com/planning/planning-with-requests-for-comments/)

---

## 8. Poka-Yoke in Software Development Workflows

### Format & Structure

Poka-yoke (mistake-proofing) in software manifests as **structural constraints** rather than document formats:

**Pre-commit hooks** — prevent errors before they enter the repository:
- Schema validation (JSON Schema, YAML Yamale)
- Linting, formatting, type checking
- Secret detection (prevent credential leaks)
- Convention enforcement (commit message format, file naming)

**CI/CD quality gates** — prevent errors from progressing through the pipeline:
- Required status checks before merge
- Coverage thresholds
- Security scan pass requirements
- Approval requirements

**Type systems as poka-yoke:**
- TypeScript, Pydantic, mypy — make invalid states unrepresentable
- Schema-first API design (OpenAPI) — contract before implementation
- Database migrations with validation (Alembic, Flyway)

**Process poka-yoke patterns:**
- Branch protection rules (require reviews, passing CI)
- Semantic versioning with automated enforcement
- Conventional Commits format (parseable commit messages)
- PR templates with required checklists

### Schema / Validation

- Pre-commit hooks use tool-specific validation (each hook defines its own rules)
- CI gates use declarative configuration (YAML in pipeline files)
- Type systems use language-specific schemas (TypeScript interfaces, Pydantic models, JSON Schema)
- The key pattern: **make the wrong thing hard, make the right thing easy**

### Structure vs Expressiveness Balance

- Poka-yoke mechanisms are **purely structural** — they constrain, they don't express
- Two modes: **control** (block the action) vs **warning** (alert but allow)
- Best practice: fast checks locally (pre-commit), thorough checks in CI
- Over-constraining leads to workaround culture (e.g., `--no-verify`)

### Scale Challenges

- Hook proliferation: too many pre-commit hooks slow development
- Gate fatigue: too many required checks create friction
- Balance: "fail-fast for cheap checks, delay-expensive checks to CI"
- Configuration drift between local and CI environments

### Key Insight
The most effective poka-yoke mechanisms in software are **invisible when things are right** — they only surface when there's a problem. Pre-commit hooks, type systems, and branch protection rules all share this property. The structured artifact formats (JUnit, SARIF, SBOM) are themselves poka-yoke mechanisms: they make it impossible to report results without including required fields.

### Confidence: High
### Sources
- [Poka-Yoke in Software Engineering (STH)](https://www.softwaretestinghelp.com/poka-yoke/")
- [Poka-Yoke via Functional Programming](https://github.com/bryanhunter/poka-yoke)
- [Pre-Commit: First Line of Defense](https://xnok.github.io/infra-bootstrap-tools/docs/tools/pre-commit/)
- [Ultimate Pre-Commit Hooks Guide 2025](https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835)
- [ASQ Mistake-Proofing](https://asq.org/quality-resources/mistake-proofing)

---

## Cross-Cutting Patterns

### Pattern 1: The Structure Spectrum

Artifacts exist on a spectrum from fully structured to fully expressive:

```
Fully Structured          Hybrid                    Fully Expressive
|                         |                         |
DORA events    SARIF      MADR         RFC docs     Design narratives
JUnit XML      SBOM       (frontmatter  (structured  (free-form)
CI metrics     CycloneDX   + markdown)   sections,
                                         free content)
```

**Finding**: The most successful formats cluster in the **structured** or **hybrid** zones. Purely expressive formats (design narratives) don't scale and aren't verifiable.

### Pattern 2: Schema Validation Approaches

| Approach | Examples | Trade-off |
|---|---|---|
| Formal JSON/XML Schema | SARIF, CycloneDX, SPDX | Strictest validation, highest adoption barrier |
| De facto standard (lenient) | JUnit XML | Easy adoption, format drift over time |
| Template convention | MADR, RFCs | Flexible, requires social enforcement |
| Type declaration | GitLab CI report types | User declares type, system knows schema |
| Implicit (event schema) | DORA metrics APIs | Schema in API contract, not in artifact |

### Pattern 3: The Hybrid Document Pattern

The most adopted approach for documents that need both machine and human consumption:

```
+---------------------------+
| YAML/TOML Frontmatter     |  <-- Machine-readable metadata
| (status, date, author,    |      (parseable, queryable, validatable)
|  tags, relationships)     |
+---------------------------+
| Markdown Body              |  <-- Human-readable content
| (context, reasoning,      |      (expressive, persuasive, nuanced)
|  decisions, consequences)  |
+---------------------------+
```

Used by: MADR, Hugo, Jekyll, Docusaurus, Astro, Quarto, countless documentation systems.

### Pattern 4: Adoption Forcing Functions

| Forcing Function | Examples | Effect |
|---|---|---|
| Regulatory mandate | SBOM (EO 14028), SARIF (GitHub required) | Fastest adoption, grudging compliance |
| CI/CD integration | JUnit XML, Cobertura | Adoption via toolchain |
| De facto standard | JUnit XML (no spec needed) | Organic, slow, fragmented |
| Template tooling | MADR (adr-tools) | Voluntary, community-driven |

### Pattern 5: Separation of Concerns in Structured Artifacts

SARIF's architecture is the gold standard:
1. **Tool metadata** — who found it (driver, version, rules)
2. **Rule definitions** — what was looked for (defined once, referenced many times)
3. **Results** — what was found (location, severity, message)
4. **Artifacts** — what was examined (files, URIs)

This separation enables: cross-tool aggregation, rule deduplication, result filtering, and trend analysis.

---

## Key Takeaways for Process Artifact Design

1. **Start structured, allow escape hatches** — Pydantic models with optional free-text fields beat free-form documents with optional structure

2. **Frontmatter + body hybrid** is the proven pattern for documents needing both machine and human consumption

3. **Type declaration > schema definition** for user-facing systems — GitLab's "declare the report type, we know the schema" is more usable than "write to this JSON Schema"

4. **Pass-by-absence** (JUnit) and **define-once-reference-many** (SARIF rules) are elegant structural patterns worth adopting

5. **Validation levels matter**: strict schema for interchange formats (SARIF, SBOM), lenient parsing for adoption-phase formats (JUnit), template convention for human documents (MADR, RFC)

6. **Regulatory mandates and CI/CD integration** are the strongest adoption forcing functions — technical elegance alone is insufficient

7. **The social workflow matters more than the format** for persuasive documents (RFCs, design docs) — structure the metadata, free the content

8. **Poka-yoke principle applies to formats themselves** — required fields in a schema ARE error-proofing; the format prevents incomplete reporting
