# RFC-001: Extensibility Architecture for raise-core

> **Status:** Draft — Requesting Comments
> **Authors:** Emilio Osorio (humansys.ai)
> **Date:** 2026-02-20
> **Audience:** Community contributors, adapter developers, enterprise evaluators
> **Canonical:** [Confluence](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3071606785)
> **Feedback:** [open an issue](https://github.com/humansys-ai/raise-commons/issues) or comment on the shared document

---

## Summary

This RFC describes how raise-core exposes extension points so that anyone can extend the CLI — integrations with project management tools, governance sources, documentation platforms, code analysis engines, workflow validation, context enrichment, output formatting, and project scaffolding — without modifying the core codebase.

The architecture defines four extension mechanisms: **adapters** (implement a protocol to provide a capability), **lifecycle hooks** (react to CLI events), **workflow gates** (validate and guard transitions), and **providers** (supply context, format output, scaffold projects). All share the same discovery, security, and enablement model.

We want your feedback on the model before we finalize the implementation.

---

## Motivation

raise-core is the open-source CLI (`rai`) that powers the RaiSE methodology for AI-assisted software development. It provides session management, a knowledge graph, governance extraction, code discovery, and a process-embedded skill system.

Today, every integration (Jira, Confluence, Azure DevOps, specific programming languages) requires changes inside raise-core itself. This creates three problems:

1. **Bottleneck.** Every integration goes through the core maintainers, regardless of who builds it.
2. **Coupling.** Adding a Jira dependency to an open-source CLI pollutes the core for users who don't use Jira.
3. **Ecosystem limits.** Contributors who want to support their own tools (Linear, Notion, GitLab) have to fork or wait.

The extensibility architecture solves this by defining **stable contracts** that adapters implement as separate Python packages. Installing an adapter is enough — `pip install raise-jira-adapter` makes Jira available to `rai` with no configuration changes in the core.

---

## Design Principles

### 1. Contracts in core, implementations outside

raise-core publishes Python `Protocol` classes (PEP 544) that define the interface for each extension point. Core never contains concrete integrations — only the contracts and a default local implementation.

### 2. Zero-config discovery

Adapters register themselves using Python's standard `importlib.metadata` entry points (declared in `pyproject.toml`). The `rai` CLI discovers installed adapters at startup automatically. No manual registration, no configuration files to edit.

### 3. Explicit consent for loading

Despite auto-discovery, adapters are **not loaded automatically**. Users must explicitly enable each adapter:

```
rai adapter enable raise-jira-adapter
```

This is a security decision. Python cannot sandbox third-party code — any loaded adapter has full access to the user's environment. Explicit enablement ensures informed consent and prevents supply-chain attacks through entry point impersonation.

### 4. Structural typing over inheritance

Using `typing.Protocol` (structural subtyping) instead of abstract base classes means adapter authors have **zero dependency on raise-core** to satisfy a contract. An existing class that happens to implement the right methods works without modification. This is critical for wrapping third-party libraries.

### 5. Progressive enrichment

When a more capable adapter is available, the same CLI commands produce richer results — without changing the user's workflow:

```
# Without a PM adapter:
rai memory build → builds graph from local .raise/ files

# With raise-jira-adapter enabled:
rai memory build → builds graph from local files + Jira issues
```

Commands never fail because an adapter isn't installed. They work with what's available and get better as adapters are added.

---

## Extension Points

raise-core defines contracts for several adapter categories. Each category has its own entry point group.

### Project Management — `rai.adapters.pm`

Connects `rai` to project management tools for issue creation, status transitions, and work logging.

```python
@runtime_checkable
class ProjectManagementAdapter(Protocol):
    priority: ClassVar[int]

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    def update_issue(self, ref: IssueRef, fields: dict) -> IssueRef: ...
    def transition_issue(self, ref: IssueRef, transition: str) -> IssueRef: ...
    def get_issue(self, ref: IssueRef) -> Issue: ...
    def link_issues(self, source: IssueRef, target: IssueRef, link_type: str) -> None: ...
    def search(self, query: str, project_key: str | None = None) -> list[Issue]: ...
```

**Example adapters:** Jira, Azure DevOps, Linear, GitHub Issues, GitLab Issues

### Governance Sources — `rai.governance.schemas`

Declares what governance artifacts (decisions, backlogs, architecture docs) exist in an organization and where to find them.

```python
@runtime_checkable
class GovernanceSchemaProvider(Protocol):
    priority: ClassVar[int]

    def list_artifact_types(self) -> list[str]: ...
    def locate(self, artifact_type: str) -> list[ArtifactLocator]: ...
```

**Built-in default:** `RaiSEDefaultSchema` — reads from the local `.raise/` directory structure.

**Example adapters:** Confluence spaces, Notion databases, SharePoint document libraries

### Governance Parsers — `rai.governance.parsers`

Extracts structured knowledge graph data from governance artifacts.

```python
@runtime_checkable
class GovernanceParser(Protocol):
    priority: ClassVar[int]

    def can_parse(self, locator: ArtifactLocator) -> bool: ...
    def parse(self, locator: ArtifactLocator) -> list[GraphNode]: ...
```

**Built-in defaults:** Markdown ADR parser, markdown backlog parser, JSONL pattern parser.

**Example adapters:** Jira backlog parser, Confluence architecture doc parser, Notion decision log parser

### Documentation Targets — `rai.docs.targets`

Publishes governance documents to a destination.

```python
@runtime_checkable
class DocumentationTarget(Protocol):
    priority: ClassVar[int]

    def can_publish(self, doc_type: str, metadata: dict) -> bool: ...
    def publish(self, doc_type: str, content: str, metadata: dict) -> PublishResult: ...
```

**Built-in default:** `LocalMarkdownTarget` — writes to the local `.raise/` directory.

**Example adapters:** Confluence publisher, MkDocs site generator, Notion page creator

### Language Extractors — `rai.discovery.languages`

Extracts code symbols (classes, functions, interfaces) from source files for the code discovery system.

```python
@runtime_checkable
class LanguageExtractor(Protocol):
    language: str
    extensions: list[str]

    def extract(self, source: str, file_path: Path) -> list[Symbol]: ...
```

**Built-in defaults:** Python, TypeScript, JavaScript, PHP, C#, Dart, Svelte

**Example community adapters:** Ruby, Go, Rust, Kotlin, Swift, Elixir

### Query Strategies — `rai.query.strategies`

Defines how the knowledge graph is searched when the user runs `rai memory query`.

```python
@runtime_checkable
class QueryStrategy(Protocol):
    strategy_id: str

    def search(self, query: str, concepts: list[MemoryConcept], limit: int) -> list[ScoredConcept]: ...
```

**Built-in defaults:** `keyword_search`, `concept_lookup`

**Example adapters:** Semantic/embedding search, BM25 ranking, hybrid search

### Workflow Gates — `rai.gates`

Defines validation rules that must pass at specific workflow points. Gates are declarative and composable — they answer "is this operation allowed?" before the core proceeds.

Gates are distinct from lifecycle hooks. Hooks *react* to events (observe, log, notify). Gates *guard* transitions (validate, block, explain). A gate that fails prevents the operation; a hook that fails is logged and skipped.

```python
@runtime_checkable
class WorkflowGate(Protocol):
    gate_id: str
    workflow_point: str  # e.g., "before:commit", "before:merge", "before:release"

    def evaluate(self, context: GateContext) -> GateResult: ...
```

```python
@dataclass
class GateResult:
    passed: bool
    reason: str | None = None
    details: dict | None = None
```

**Built-in defaults:** Tests pass, types check, lint clean (the existing `rai` gate checks).

**Example adapters:**
- Coverage threshold gate: "no commit if coverage drops below 80%"
- ADR-required gate: "no merge touching `/core` without a linked ADR"
- Security scan gate: "no release with known CVEs"
- Jira-linked gate: "no commit without a JIRA issue reference in the branch name"

**Gate composition:** Multiple gates at the same workflow point are evaluated in priority order. All must pass — a single failure blocks the operation. The failure message tells the user exactly what to fix.

```
GATE FAILED: adr-required (before:merge)
  Changes to src/rai_cli/core/ require a linked ADR.
  Create one with: rai governance add-adr --title "..."
```

### Context Providers — `rai.context`

Supplies information to the AI context on demand, answering "what does the agent need to know about X?" from any source.

Context providers are distinct from governance parsers. Parsers feed the knowledge graph at build time (`rai memory build`). Context providers respond in real time to queries without rebuilding the graph — they are read-through, not batch.

```python
@runtime_checkable
class ContextProvider(Protocol):
    provider_id: str
    priority: ClassVar[int]

    def can_provide(self, query: str, scope: str | None = None) -> bool: ...
    def provide(self, query: str, scope: str | None = None) -> list[ContextItem]: ...
```

```python
@dataclass
class ContextItem:
    source: str          # e.g., "confluence", "notion", "local"
    title: str
    content: str
    relevance: float     # 0.0 to 1.0
    url: str | None = None
```

**Built-in default:** `LocalContextProvider` — reads from the knowledge graph and `.raise/` files.

**Example adapters:**
- Confluence context provider: searches Confluence spaces for relevant pages
- Notion context provider: queries Notion databases
- Internal wiki provider: fetches from custom knowledge bases
- Stack Overflow/internal Q&A provider

**Usage:** `rai memory context mod-memory` already exists. With providers, the same command queries all enabled sources and merges results by relevance.

### Output Formatters — `rai.formatters`

Transforms CLI output into different representations for different destinations. Formatters don't produce data (that's adapters) or react to events (that's hooks) — they control *how results are presented*.

```python
@runtime_checkable
class OutputFormatter(Protocol):
    formatter_id: str
    output_types: ClassVar[list[str]]  # e.g., ["retrospective", "session_summary", "report"]

    def can_format(self, output_type: str, target: str) -> bool: ...
    def format(self, output_type: str, data: dict, target: str) -> FormattedOutput: ...
```

```python
@dataclass
class FormattedOutput:
    content: str
    media_type: str      # e.g., "text/markdown", "text/html", "application/json"
    metadata: dict | None = None
```

**Built-in default:** `MarkdownFormatter` — renders everything as local markdown (current behavior).

**Example adapters:**
- Jira comment formatter: renders retrospectives as Jira-compatible markup
- Confluence page formatter: renders architecture docs as Confluence storage format
- Slack formatter: renders session summaries as Slack Block Kit JSON
- JSON formatter: renders any output as structured JSON for CI/CD pipelines

**Usage:** Formatters are selected by target, not by command. When a documentation target adapter publishes to Confluence, it uses the Confluence formatter automatically. The formatter is the bridge between data and destination.

### Scaffold Providers — `rai.scaffolds`

Defines project initialization templates for specific technology stacks. When a user runs `rai init`, scaffold providers contribute stack-specific governance structure, skill configurations, and conventions.

```python
@runtime_checkable
class ScaffoldProvider(Protocol):
    stack_id: str           # e.g., "fastapi", "flutter", "dotnet", "symfony"
    languages: list[str]    # e.g., ["python"], ["dart"], ["csharp"]

    def detect(self, project_path: Path) -> float: ...  # confidence 0.0 to 1.0
    def scaffold(self, project_path: Path, options: ScaffoldOptions) -> ScaffoldResult: ...
```

```python
@dataclass
class ScaffoldResult:
    files_created: list[Path]
    conventions_detected: dict
    recommendations: list[str]
```

**Built-in defaults:** Generic Python, TypeScript, PHP, C#, Dart scaffolds (from current `rai init --detect` logic).

**Example community adapters:**
- `raise-scaffold-fastapi`: FastAPI project structure, pytest conventions, API-specific governance templates
- `raise-scaffold-flutter`: Flutter project structure, widget testing patterns, mobile-specific skills
- `raise-scaffold-symfony`: Symfony project structure, PHP conventions, doctrine patterns
- `raise-scaffold-nextjs`: Next.js app router structure, React testing patterns

**Detection:** When `rai init --detect` runs, all enabled scaffold providers score their confidence against the project. The highest-confidence provider generates the scaffold. Multiple providers can contribute if they detect different aspects (e.g., a Python provider + a Docker provider).

---

## Lifecycle Hooks — `rai.hooks`

Adapters solve *invocation*: the core calls an adapter when it needs something done (create an issue, parse a document, extract symbols). Hooks solve a different problem: *reaction*. External code that runs when something happens in the CLI, without the core knowing or caring what that code does.

This is the observer pattern applied to a CLI. The core emits events at well-defined points in its lifecycle. Hooks listen to those events and run their own logic — telemetry, notifications, compliance checks, audit logging — as side effects.

### Why hooks matter

Today, cross-cutting concerns like telemetry live inside raise-core's skill implementations. This creates coupling: every skill that wants to emit metrics needs to know about the telemetry system. Adding a new cross-cutting concern (audit logging, team notifications) means modifying skills.

With hooks, cross-cutting concerns move outside the core entirely:

```
# Without hooks:
rai session close → skill writes JSONL telemetry (hardcoded in skill)

# With hooks:
rai session close → emits "session:close" event
  → community hook writes JSONL locally
  → pro hook sends metrics to hosted backend
  → enterprise hook posts summary to Slack
```

The core doesn't know what hooks are installed. It emits events and moves on.

### Event catalog

raise-core emits events at the boundaries of commands that produce side effects. Read-only commands (`rai memory list`, `rai skill list`, `rai memory viz`) do not emit events.

| Event | Emitted when | Context payload |
|-------|-------------|-----------------|
| `session:start` | Session begins | session_id, project, agent |
| `session:close` | Session ends | session_id, summary, duration, patterns |
| `memory:build` | Knowledge graph rebuilt | project_path, node_count, edge_count |
| `memory:pattern_added` | New pattern recorded | pattern_id, content, context |
| `memory:work_emitted` | Work event recorded | work_type, work_id, event, phase |
| `discover:scan` | Code scan completes | language, file_count, symbol_count |
| `discover:build` | Discovery graph built | module_count, component_count |
| `init:complete` | Project initialized | project_path, detected_conventions |
| `publish:release` | Release published | version, channel |
| `adapter:loaded` | Adapter passes validation | adapter_name, extension_point |
| `adapter:failed` | Adapter fails validation | adapter_name, error |

Events always include a `timestamp` and `project_path` in addition to their specific payload. The payload is a typed `dataclass` — not a loose `dict`.

```python
@dataclass(frozen=True)
class SessionCloseEvent:
    event: Literal["session:close"]
    timestamp: datetime
    project_path: Path
    session_id: str
    summary: str
    duration_seconds: float
    patterns: list[str]
```

### Hook Protocol

```python
@runtime_checkable
class LifecycleHook(Protocol):
    events: ClassVar[list[str]]

    def handle(self, event: HookEvent) -> HookResult: ...
```

`HookResult` signals whether the hook succeeded, failed, or wants to abort the operation:

```python
@dataclass
class HookResult:
    status: Literal["ok", "error", "abort"]
    message: str | None = None
```

- `ok` — hook ran successfully, continue.
- `error` — hook failed, log warning, continue. Hooks never crash the CLI.
- `abort` — hook requests cancellation of the current operation. Only honored for `before:*` events (see below).

### Before and after events

Each event in the catalog has a `before:` and `after:` variant:

```
before:session:close → core executes session close → after:session:close
```

- **`before:*`** hooks can inspect and abort. A compliance hook returning `abort` from `before:publish:release` prevents the release.
- **`after:*`** hooks can only observe. They receive the result of the operation but cannot change it.

A hook declares which variants it listens to:

```python
class MyTelemetryHook:
    events = ["after:session:close", "after:memory:build"]

    def handle(self, event):
        # record metrics
        return HookResult(status="ok")
```

### Registration and discovery

Hooks use the same entry point mechanism as adapters:

```toml
# pyproject.toml
[project.entry-points."rai.hooks"]
my-telemetry = "my_package.hooks:MyTelemetryHook"
```

They follow the same security model: discovered automatically, but loaded only after explicit enablement with `rai adapter enable`.

### Execution guarantees

1. **Hooks are synchronous.** They run in the CLI process, sequentially, in priority order. We don't introduce async complexity.
2. **Hooks have a timeout.** Default: 5 seconds per hook. A hung hook is killed and logged as an error. Configurable per-hook.
3. **Hooks never break the CLI.** An exception in a hook is caught, logged, and skipped. The operation continues.
4. **`before:*` abort is advisory.** The core honors it, but logs the reason. The user sees why their command didn't execute.
5. **No hook-to-hook communication.** Hooks don't see each other's results. This prevents ordering dependencies and keeps the system simple.

### Telemetry as a hook — worked example

Today, raise-core writes session telemetry as JSONL files. With hooks, this becomes a built-in hook instead of hardcoded logic:

```python
class LocalTelemetryHook:
    """Built-in hook. Writes session and work events to .raise/telemetry/."""

    events = [
        "after:session:start",
        "after:session:close",
        "after:memory:work_emitted",
    ]

    def handle(self, event: HookEvent) -> HookResult:
        path = event.project_path / ".raise" / "telemetry" / f"{event.timestamp:%Y-%m}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(json.dumps(asdict(event)) + "\n")
        return HookResult(status="ok")
```

A commercial adapter replaces this with a richer implementation — same events, different destination:

```python
class ProTelemetryHook:
    """Commercial hook. Sends metrics to RaiSE hosted backend."""

    events = [
        "after:session:start",
        "after:session:close",
        "after:memory:work_emitted",
        "after:memory:build",
        "after:discover:scan",
    ]
    priority = 20  # takes precedence over built-in

    def handle(self, event: HookEvent) -> HookResult:
        self.client.send(event)
        return HookResult(status="ok")
```

The user's workflow doesn't change. `rai session close` works the same way — it just produces richer telemetry when the pro hook is installed.

---

## How to Build an Adapter

### 1. Implement the Protocol

```python
# my_adapter/adapter.py

class MyLinearAdapter:
    priority = 0  # default; higher values take precedence

    def create_issue(self, project_key, issue):
        # your implementation
        ...
```

No import from raise-core needed. Your class just needs to have the right methods with the right signatures.

### 2. Register the entry point

```toml
# pyproject.toml
[project.entry-points."rai.adapters.pm"]
linear = "my_adapter.adapter:MyLinearAdapter"
```

### 3. Install and enable

```
pip install my-linear-adapter
rai adapter enable my-linear-adapter
```

That's it. `rai` discovers your adapter, validates its signature against the Protocol at load time, and uses it.

---

## Priority and Conflict Resolution

When multiple adapters can handle the same operation, raise-core uses a priority-based dispatch:

* Each adapter declares `priority: ClassVar[int]` (default: `0`)
* Higher priority wins
* Equal priority: alphabetical by package name (deterministic, no randomness)
* A warning is logged when multiple adapters match with equal priority

**Suggested conventions:**
- `0` — community adapters (default)
- `10` — raise-core built-in defaults
- `20` — commercial/enterprise adapters

This means installing a commercial adapter automatically takes precedence over the built-in default, without the user needing to configure anything.

---

## Adapter Validation

When an adapter is loaded, raise-core validates it against the Protocol using `inspect.signature()`. This catches:

* Missing methods
* Wrong parameter names
* Wrong return type annotations

Validation happens at load time (when `rai` starts), not at call time. A malformed adapter produces a clear warning and is skipped — it never causes a runtime crash.

```
WARNING: Adapter 'my-broken-adapter' failed validation:
  Missing method 'create_issue' required by ProjectManagementAdapter
  Skipping adapter.
```

---

## Security Model

### The fundamental constraint

Python cannot sandbox third-party code. Every adapter that is loaded has full access to:
- The filesystem
- Network access
- Environment variables
- Subprocess execution
- Everything the user's process can do

There is no technical barrier we can erect inside the Python process. Our defense is therefore **reducing the probability that malicious code reaches a user's environment.**

### How we reduce that probability

1. **Explicit allowlist.** Adapters are not loaded automatically. `rai adapter enable` is required. This prevents "command-jacking" attacks where a malicious package registers an entry point and gets loaded silently.
2. **Provenance display.** When you run `rai adapter enable`, raise-core queries PyPI and shows you: publisher identity, download count, first published date, and attestation status (PEP 740). You make an informed decision.
3. **Version pinning.** The allowlist records the specific version you enabled. Upgrading to a new version requires explicit `rai adapter upgrade` — a compromised update doesn't reach you automatically.
4. **Clear documentation.** We tell you exactly what access adapters have. No surprises.

### What we don't do (yet)

* We don't sandbox adapters in subprocesses (significant complexity, planned for future)
* We don't scan adapter code for malicious patterns (unreliable for Python)
* We don't maintain a curated marketplace (planned when the ecosystem is large enough)

---

## Extensible Type Registry

Governance artifacts, document types, and other categorical values use an open string registry instead of Python Enums.

**Why not Enum?** Python's Enum metaclass raises `TypeError` when you try to subclass an Enum that has members. This is a language-level constraint — a third-party adapter literally cannot add new artifact types to an Enum defined in raise-core.

**The registry pattern:**

```python
# raise-core defines the base types
ArtifactTypeRegistry.register("backlog", BacklogDescriptor())
ArtifactTypeRegistry.register("decision", DecisionDescriptor())

# Your adapter registers new types
ArtifactTypeRegistry.register("kanban_card", KanbanCardDescriptor())
```

For type safety, raise-core also provides string constants with IDE autocomplete:

```python
class ArtifactTypes:
    BACKLOG = "backlog"
    DECISION = "decision"
    # your adapter adds its own constants in its own namespace
```

---

## Protocol Versioning

Protocol contracts are versioned with raise-core's semver:

* **Patch** (Z in X.Y.Z): No Protocol changes. Bug fixes only.
* **Minor** (Y): Additive changes only. New optional methods with default implementations. Existing adapters continue to work.
* **Major** (X): Breaking changes — method removals, renames, or signature changes. Adapter maintainers must update.

We will document every Protocol change in `CHANGELOG.md` under a dedicated **Protocol Changes** section with migration guides.

---

## Tier Architecture

raise-core supports a tier system that allows commercial extensions to enrich the same CLI experience:

* **COMMUNITY** — the default. Everything works locally, offline, with no backend. This is a complete, first-class experience — not a degraded version of anything.
* **PRO / ENTERPRISE** — commercial tiers that add capabilities (team memory, enterprise governance, hosted services). Same commands, richer results. Details are outside the scope of this RFC.

The tier system is relevant to adapter authors because:
1. Your adapter can declare which tier it requires (most community adapters require no specific tier)
2. The `TierContext` object is available if your adapter needs to check capabilities
3. Built-in adapters that detect a higher tier will enrich their output accordingly

---

## Open Questions

We'd appreciate community input on these:

### 1. Credential storage

Currently, adapter credentials live in `.raise/adapters/<name>.yaml` (gitignored). Should we support system keyring integration (macOS Keychain, Windows Credential Manager, Linux Secret Service) as an alternative?

### 2. Adapter testing utilities

Should raise-core ship a `raise-adapter-testing` package with test helpers? For example:

```python
from raise_testing import assert_satisfies_protocol

def test_my_adapter():
    assert_satisfies_protocol(MyAdapter, ProjectManagementAdapter)
```

### 3. Adapter configuration format

Adapters need configuration (API URLs, project keys, etc.). Should we standardize on YAML in `.raise/adapters/<name>.yaml`, or let each adapter define its own config format?

### 4. Runtime adapter switching

Should users be able to switch between adapters at runtime (`rai adapter use jira` vs `rai adapter use linear`), or is install-time selection sufficient?

### 5. Language extractor packaging

For language extractors specifically — should they be separate packages (`raise-ruby-extractor`) or contributed directly to raise-core? Language extractors are typically small (200-500 lines) and benefit from being tested together.

### 6. Hook event granularity

Should hooks receive fine-grained events (one per command) or coarse-grained lifecycle events (session, build, release)? More events mean more flexibility but also more surface area to maintain. Which events would you subscribe to?

### 7. Gate composition model

When multiple gates guard the same workflow point, should they all run (report all failures at once) or fail-fast (stop at the first failure)? All-run gives better UX (fix everything in one pass), fail-fast is simpler and faster.

### 8. Context provider caching

Context providers may query external services (Confluence, Notion). Should raise-core provide a caching layer (TTL-based, invalidated on `rai memory build`), or should each provider manage its own cache?

### 9. Capability bundles

Should raise-core define a packaging convention for bundles that combine adapters + hooks + gates + scaffold templates into a single installable unit? For example, `raise-jira-bundle` could include a PM adapter, telemetry hooks, Jira-linked gates, and Jira workflow templates — all enabled with one `rai adapter enable`.

---

## How to Give Feedback

* **GitHub Issues:** Open an issue with the tag `rfc-001` at [github.com/humansys-ai/raise-commons](https://github.com/humansys-ai/raise-commons/issues)
* **Comments:** Comment directly on the shared document
* **Email:** [emilio@humansys.ai](mailto:emilio@humansys.ai)

We're especially interested in:
- Extension point types we haven't considered
- Security concerns we've missed
- UX friction points in the enable/disable flow
- Protocol methods that seem missing or unnecessary
- Hook events you'd want to subscribe to and why
- Gate rules you'd want to enforce in your workflow
- Context sources you'd want to plug in
- Technology stacks that need scaffold providers
- Your experience building plugins for other Python tools

---

## References

* [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
* [PyPA — Creating and discovering plugins](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
* [PEP 740 — Index attestations](https://peps.python.org/pep-0740/)
* [Checkmarx — "command-jacking" via entry points](https://checkmarx.com/blog/surprise-when-dormant-packages-wake-up-as-command-jacking-attacks-on-pypi/)
* [dbt adapter architecture](https://docs.getdbt.com/docs/contributing/building-a-new-adapter)
* [OpenClaw hooks system](https://docs.openclaw.ai/cli/hooks)

---

*This is a living document. We will update it based on community feedback before finalizing the implementation.*

*RaiSE is developed by [humansys.ai](https://humansys.ai) — AI-assisted software development methodology and tooling.*
