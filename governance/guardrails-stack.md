# Stack Guardrails

> Best practices for raise-cli stack: Python 3.12+, Pydantic v2, Typer, pytest.
> Synthesized from 150 sources across 6 research catalogs.

**Purpose:** Reference during implementation and review. Jidoka checkpoint in `/story-review`.

---

## Quick Reference

| Category | Key Rule |
|----------|----------|
| Pydantic | BaseModel at boundaries, not everywhere |
| CLI | Flags over positional, multi-format output |
| Security | Never eval/exec, subprocess shell=False |
| Testing | AAA pattern, factory fixtures, each test asserts behavior |
| DRY/SOLID | Rule of Three, composition over inheritance |

---

## 1. Pydantic v2

### 1.1 BaseModel at System Boundaries

**Do:** Use BaseModel for CLI inputs, config files, external data.

**Don't:** Use BaseModel for all internal classes ("Serdes debt" = 6.5x slower, 2.5x memory).

**Why:** Validation has cost. Only pay it where untrusted data enters.

```python
# GOOD: BaseModel at boundary
class ConfigFile(BaseModel):
    project_name: str
    version: str

# GOOD: Plain class internally
@dataclass
class ProcessingContext:
    config: ConfigFile
    cache: dict
```

### 1.2 Validators: Default to mode='after'

**Do:** Use `mode='after'` for type-safe validation on coerced values.

**Don't:** Use `mode='before'` unless preprocessing raw input.

```python
# GOOD
@field_validator('path', mode='after')
def validate_path(cls, v: Path) -> Path:
    if not v.exists():
        raise ValueError(f"Path does not exist: {v}")
    return v

# ONLY when normalizing input
@field_validator('tags', mode='before')
def normalize_tags(cls, v):
    if isinstance(v, str):
        return [v]  # Convert single string to list
    return v
```

### 1.3 TypeAdapter at Module Level

**Do:** Instantiate TypeAdapter once at module level.

**Don't:** Create TypeAdapter inside functions (triggers schema recompilation).

```python
# GOOD
from pydantic import TypeAdapter

PatternListAdapter = TypeAdapter(list[Pattern])  # Module level

def load_patterns(data: str) -> list[Pattern]:
    return PatternListAdapter.validate_json(data)

# BAD
def load_patterns(data: str) -> list[Pattern]:
    adapter = TypeAdapter(list[Pattern])  # Recompiles schema every call!
    return adapter.validate_json(data)
```

### 1.4 Discriminated Unions for Polymorphism

**Do:** Use discriminated unions with literal discriminator for union types.

**Don't:** Use plain Union (tries each type sequentially).

```python
# GOOD: Fast lookup via discriminator
from typing import Annotated, Literal, Union
from pydantic import Field

class PatternNode(BaseModel):
    node_type: Literal["pattern"] = "pattern"
    content: str

class SessionNode(BaseModel):
    node_type: Literal["session"] = "session"
    timestamp: datetime

NodeData = Annotated[
    Union[PatternNode, SessionNode],
    Field(discriminator='node_type')
]
```

### 1.5 Prefer model_validate_json()

**Do:** Use `model_validate_json()` for JSON input.

**Don't:** Use `json.loads()` then `model_validate()`.

```python
# GOOD: Direct JSON validation (faster, uses Rust core)
config = Config.model_validate_json(json_string)

# BAD: Intermediate dict conversion
config = Config.model_validate(json.loads(json_string))
```

### 1.6 Specific Types Over Abstractions

**Do:** Use `list`, `dict` in model fields.

**Don't:** Use `Sequence`, `Mapping` (extra isinstance checks).

```python
# GOOD
class Result(BaseModel):
    items: list[str]
    metadata: dict[str, Any]

# BAD: Slower validation
class Result(BaseModel):
    items: Sequence[str]
    metadata: Mapping[str, Any]
```

---

## 2. Typer CLI

### 2.1 Flags Over Positional Arguments

**Do:** Use flags for most parameters.

**Don't:** Use multiple positional arguments (unclear, inflexible).

```python
# GOOD: Clear, composable
@app.command()
def query(
    query: str,  # One positional is OK
    format: str = typer.Option("human", "--format", "-f"),
    limit: int = typer.Option(10, "--limit", "-l"),
):
    ...

# BAD: Unclear order
@app.command()
def query(query: str, format: str, limit: int):
    ...
```

### 2.2 Multi-Format Output

**Do:** Support `--format` with human (default), json, table.

**Don't:** Only support one output format.

```python
class OutputFormat(str, Enum):
    human = "human"
    json = "json"
    table = "table"

@app.command()
def status(format: OutputFormat = OutputFormat.human):
    if format == OutputFormat.json:
        print_json(result)
    else:
        print_human(result)
```

### 2.3 Exit Codes with Exception Hierarchy

**Do:** Map exceptions to distinct exit codes; catch at CLI boundary.

**Don't:** Use generic exit code 1 for all errors.

```python
# Exception hierarchy
class RaiseError(Exception):
    exit_code: int = 1

class ConfigurationError(RaiseError):
    exit_code: int = 2

class ResourceNotFoundError(RaiseError):
    exit_code: int = 3

# Catch at boundary
@app.command()
def main():
    try:
        run_logic()
    except RaiseError as e:
        console.print_error(e)
        raise typer.Exit(e.exit_code)
```

### 2.4 Helpful Error Messages

**Do:** Explain what failed, why, and how to fix.

**Don't:** Show raw exception messages.

```python
# GOOD
"Cannot read config file: ~/.rai/config.yaml
 File does not exist.
 Hint: Run 'raise init' to create default configuration."

# BAD
"FileNotFoundError: [Errno 2] No such file or directory"
```

### 2.5 Thin Commands

**Do:** Commands orchestrate (parse → call service → format output).

**Don't:** Put business logic in command functions.

```python
# GOOD: Thin command
@app.command()
def build(path: Path):
    result = graph_service.build(path)  # Service has logic
    console.print_result(result)

# BAD: Fat command
@app.command()
def build(path: Path):
    files = list(path.glob("**/*.md"))
    concepts = []
    for f in files:
        # 50 lines of parsing logic...
```

### 2.6 One File Per Command Group

**Do:** Organize with one module per command group, use `add_typer()`.

```
cli/commands/
├── __init__.py
├── discover.py   # rai discover ...
├── init.py       # rai init ...
├── memory.py     # rai memory ...
├── profile.py    # raise profile ...
└── session.py    # rai session ...
```

---

## 3. Security

### 3.1 Never eval/exec with Untrusted Input

**Do:** Use safe alternatives (AST for analysis, dispatch tables for selection).

**Don't:** Use eval(), exec(), compile() on any user-influenced data.

```python
# NEVER
result = eval(user_input)

# SAFE: Dispatch table
OPERATIONS = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
}
result = OPERATIONS[operation](a, b)
```

### 3.2 Subprocess: shell=False Always

**Do:** Use argument lists with shell=False.

**Don't:** Use shell=True or f-strings in commands.

```python
# GOOD
import shlex
subprocess.run(["git", "log", "--oneline", shlex.quote(branch)])

# NEVER
subprocess.run(f"git log --oneline {branch}", shell=True)
```

### 3.3 Safe Deserialization

**Do:** Use yaml.safe_load(), JSON for serialization.

**Don't:** Use pickle.load() or yaml.load() with untrusted data.

```python
# GOOD
import yaml
data = yaml.safe_load(file_content)

# NEVER with untrusted data
import pickle
data = pickle.load(file)  # RCE vulnerability
```

### 3.4 Path Traversal Prevention

**Do:** Resolve paths and verify ancestry.

**Don't:** Trust user-provided paths directly.

```python
def safe_path(base: Path, user_input: str) -> Path:
    """Resolve and verify path is within base directory."""
    resolved = (base / user_input).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError("Path traversal detected")
    return resolved
```

### 3.5 Secrets Management

**Do:** Use environment variables, keyring, or secrets managers.

**Don't:** Hardcode secrets in source code.

```python
# GOOD
api_key = os.environ.get("API_KEY")

# With pydantic-settings
class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")

# NEVER
api_key = "sk-1234567890"  # Hardcoded!
```

### 3.6 Use secrets Module for Tokens

**Do:** Use `secrets` module for security tokens.

**Don't:** Use `random` module (predictable).

```python
# GOOD
import secrets
token = secrets.token_urlsafe(32)

# BAD: Predictable
import random
token = ''.join(random.choices(string.ascii_letters, k=32))
```

### 3.7 No Assert for Security Validation

**Do:** Raise explicit exceptions for validation.

**Don't:** Use assert (removed with python -O).

```python
# GOOD
if not user.is_authorized:
    raise PermissionError("Unauthorized access")

# BAD: Removed in optimized mode
assert user.is_authorized, "Unauthorized"
```

---

## 4. Testing (pytest)

### 4.1 AAA Pattern

**Do:** Structure tests as Arrange-Act-Assert with single Act.

**Don't:** Multiple actions or assertions testing different things.

```python
# GOOD
def test_user_creation():
    # Arrange
    name = "Alice"

    # Act
    user = User.create(name)

    # Assert
    assert user.name == name
    assert user.is_active

# BAD: Multiple acts
def test_user_workflow():
    user = User.create("Alice")  # Act 1
    user.activate()               # Act 2
    user.update_profile()         # Act 3
    assert user.is_complete       # What failed?
```

### 4.2 Fixtures Over Setup/Teardown

**Do:** Use pytest fixtures with dependency injection.

**Don't:** Use xUnit-style setup_method/teardown_method.

```python
# GOOD
@pytest.fixture
def user():
    return User.create("test")

def test_user_name(user):
    assert user.name == "test"

# AVOID
class TestUser:
    def setup_method(self):
        self.user = User.create("test")
```

### 4.3 Factory Fixtures for Multiple Instances

**Do:** Use factory pattern when tests need multiple instances.

```python
@pytest.fixture
def make_user():
    def _make_user(name: str, role: str = "viewer") -> User:
        return User(name=name, role=role)
    return _make_user

def test_permissions(make_user):
    admin = make_user("Alice", role="admin")
    viewer = make_user("Bob", role="viewer")
    assert admin.can_edit(viewer.profile)
```

### 4.4 Fixture Scope Selection

| Scope | Use Case |
|-------|----------|
| function | Default. Maximum isolation. |
| class | Shared across class methods |
| module | Expensive setup (DB connection) |
| session | Very expensive (Docker containers) |

**Rule:** Broader fixtures cannot use narrower fixtures.

### 4.5 conftest.py Hierarchy

```
tests/
    conftest.py          # Session-wide (db, app)
    unit/
        conftest.py      # Unit fixtures (mocks)
    integration/
        conftest.py      # Integration fixtures
```

### 4.6 Mocking Strategy

| Tool | Use When |
|------|----------|
| monkeypatch | Env vars, simple attributes |
| pytest-mock | Call tracking, return values |

```python
# monkeypatch: Simple
def test_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")

# pytest-mock: Call tracking
def test_notify(mocker):
    mock_send = mocker.patch("app.email.send")
    notify_user(1)
    mock_send.assert_called_once()
```

### 4.7 Test Quality Over Coverage

**Do:** Write tests that catch real defects. Each test must assert observable behavior.

**Coverage:** Diagnostic only — no fixed target. Floor: if coverage drops below 70%, investigate gaps in domain logic.

**Anti-patterns (muda):**
- Constant assertions: `assert "x" == "x"` (always passes, catches nothing)
- Mock-implementation tests: only verify an internal method was called, not the outcome
- Magic-number counts: `assert len(items) == 21` (brittle, not behavioral)
- Happy-path-only: no boundary tests (empty, one, many, error cases)

**Don't:** Write tests to hit a coverage number. If a test doesn't catch a real bug, it's waste.

---

## 5. DRY/SOLID

### 5.1 Rule of Three

**Do:** Wait for 3 occurrences before abstracting.

**Don't:** Abstract on first or second duplication.

**Why:** First two instances reveal different aspects. Third shows true pattern.

```python
# After seeing this THREE times:
def sanitize_id(text: str) -> str:
    return text.lower().replace(" ", "-").strip("-")

# THEN extract. Not before.
```

### 5.2 Semantic Over Syntactic Duplication

**Do:** Abstract only when code represents the SAME concept.

**Don't:** Abstract just because code looks similar.

```python
# These look similar but serve different purposes - DON'T unify
def validate_kata_path(path): ...
def validate_component_path(path): ...

# These represent the same concept - DO unify
def sanitize_id(text): ...  # Used in vision.py AND constitution.py
```

### 5.3 Composition Over Inheritance

**Do:** Compose behaviors via injection.

**Don't:** Create deep inheritance hierarchies.

```python
# GOOD: Composition
class GraphBuilder:
    def __init__(self, extractor: Extractor, formatter: Formatter):
        self.extractor = extractor
        self.formatter = formatter

# AVOID: Deep inheritance
class BaseExtractor: ...
class ConceptExtractor(BaseExtractor): ...
class EnhancedConceptExtractor(ConceptExtractor): ...
```

### 5.4 Protocols Over ABCs

**Do:** Use Protocol for type hints (structural subtyping).

**Don't:** Create ABCs just for interface definition.

```python
# GOOD: Protocol
from typing import Protocol

class Extractor(Protocol):
    def extract(self, content: str) -> list[Concept]: ...

# AVOID unless runtime enforcement needed
from abc import ABC, abstractmethod

class Extractor(ABC):
    @abstractmethod
    def extract(self, content: str) -> list[Concept]: ...
```

### 5.5 Simple Dependency Injection

**Do:** Constructor injection, wire in main/CLI entry points.

**Don't:** Use DI frameworks for CLI tools.

```python
# GOOD: Simple DI
def main():
    extractor = ConceptExtractor()
    builder = GraphBuilder(extractor)
    app.run(builder)

# OVERKILL for CLI
from dependency_injector import containers
```

### 5.6 Functions Are Fine

**Do:** Use functions for single-purpose operations.

**Don't:** Create classes just to have a class.

```python
# GOOD: Simple function
def load_config(path: Path) -> Config:
    return Config.model_validate_json(path.read_text())

# OVERKILL
class ConfigLoader:
    def load(self, path: Path) -> Config:
        return Config.model_validate_json(path.read_text())
```

### 5.7 Avoid Wrong Abstraction Debt

**Do:** Remove abstractions that accumulate special cases.

**Don't:** Keep bending wrong abstractions to fit new cases.

**Signal:** Abstraction has multiple if/elif branches for "type".

```python
# SMELL: Wrong abstraction
def process_node(node):
    if node.type == "concept":
        # 20 lines
    elif node.type == "pattern":
        # 20 different lines
    elif node.type == "session":
        # 20 more different lines

# BETTER: Separate functions, possibly polymorphism
def process_concept(node): ...
def process_pattern(node): ...
def process_session(node): ...
```

---

## Jidoka Checklist

Quick validation during `/story-review`:

### Pydantic
- [ ] BaseModel only at system boundaries?
- [ ] Validators use mode='after' by default?
- [ ] TypeAdapters at module level?
- [ ] Discriminated unions for polymorphic types?

### CLI
- [ ] Flags over positional arguments?
- [ ] Multi-format output supported?
- [ ] Helpful error messages (what, why, fix)?
- [ ] Commands thin (orchestrate, don't contain logic)?

### Security
- [ ] No eval/exec on untrusted data?
- [ ] subprocess uses shell=False?
- [ ] Paths validated against traversal?
- [ ] No hardcoded secrets?
- [ ] secrets module for tokens?

### Testing
- [ ] AAA pattern with single Act?
- [ ] Fixtures over setup/teardown?
- [ ] Factory fixtures for multiple instances?
- [ ] Each test asserts observable behavior (not implementation details)?
- [ ] No muda: no constant assertions, no mock-implementation tests, no magic counts?

### DRY/SOLID
- [ ] Rule of Three applied (not premature abstraction)?
- [ ] Semantic duplication, not syntactic?
- [ ] Composition over inheritance?
- [ ] Functions used where classes unnecessary?

---

## References

| Topic | Research Location |
|-------|-------------------|
| Pydantic v2 | `work/research/pydantic-v2-best-practices/` |
| Typer CLI | `work/research/typer-cli-best-practices/` |
| Security | `work/research/python-security/` |
| Pytest | `work/research/pytest-best-practices/` |
| DRY/SOLID | `work/research/dry-solid-python/` |
| Python Structure | `work/research/python-project-structure-2025/` |

---

*Synthesized: 2026-02-05*
*Sources: 150 across 6 research catalogs*
*Version: 1.0.0*
