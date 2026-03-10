# Synthesis: Pytest Best Practices and Patterns

> Research ID: pytest-best-practices-20260205
> Date: 2026-02-05
> Sources Triangulated: 25

---

## Major Claims (Triangulated)

### Claim 1: The AAA Pattern (Arrange-Act-Assert) is the standard test structure

**Confidence**: HIGH

**Evidence**:
1. [pytest Official Documentation](https://docs.pytest.org/en/stable/explanation/anatomy.html) - "Tests exist in four parts: Arrange, Act, Assert, Cleanup"
2. [Automation Panda](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/) - "AAA is powerful because it is simple... de facto style for pytest"
3. [Real Python](https://realpython.com/pytest-python-testing/) - Recommends AAA structure throughout
4. [James Cooke](https://jamescooke.info/arrange-act-assert-pattern-for-python-developers.html) - "Originated with Bill Wake (2001), validated by Kent Beck"

**Disagreement**: None found

**Implication**: All pytest tests should follow AAA structure. Keep Act singular (one state-changing action per test).

---

### Claim 2: Fixtures should be preferred over setup/teardown methods

**Confidence**: HIGH

**Evidence**:
1. [pytest Official Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html) - "Fixtures are modular... can be imported, depend on other fixtures"
2. [Brian Okken - Python Testing with pytest](https://pragprog.com/titles/bopytest2/) - "Fixtures will change the way you think about tests"
3. [NerdWallet Engineering](https://www.nerdwallet.com/blog/engineering/5-pytest-best-practices/) - "Use fixtures over setup/teardown"
4. [Inspired Python](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns) - "Fixtures are reusable, reduce boilerplate"

**Disagreement**: None found

**Implication**: Migrate xUnit-style setup/teardown to fixtures. Use fixture dependency injection for composed setup.

---

### Claim 3: Factory-as-fixture pattern solves multiple instance needs

**Confidence**: HIGH

**Evidence**:
1. [pytest Official Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures) - "Return a factory function when fixture result needed multiple times"
2. [Inspired Python](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns) - Factory pattern detailed with examples
3. [Fiddler AI Engineering](https://www.fiddler.ai/blog/advanced-pytest-patterns-harnessing-the-power-of-parametrization-and-factory-methods) - "Factory methods reduce fixture complexity"
4. [Pytest with Eric](https://pytest-with-eric.com/pytest-best-practices/pytest-conftest/) - Factory fixtures for dynamic data

**Disagreement**: None found

**Implication**: When a test needs multiple instances from same fixture, use factory pattern:

```python
@pytest.fixture
def make_user():
    def _make_user(name: str, role: str = "viewer") -> User:
        return User(name=name, role=role)
    return _make_user

def test_user_comparison(make_user):
    admin = make_user("Alice", role="admin")
    viewer = make_user("Bob")
    assert admin.can_view(viewer.resources)
```

---

### Claim 4: Fixture scope should balance isolation vs performance

**Confidence**: HIGH

**Evidence**:
1. [pytest Official Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session) - "Scopes: function, class, module, package, session"
2. [Pytest with Eric - Fixture Scopes](https://pytest-with-eric.com/fixtures/pytest-fixture-scope/) - "Choose based on isolation needs vs performance"
3. [Better Stack Guide](https://betterstack.com/community/guides/testing/pytest-fixtures-guide/) - "Session scope for expensive setup; function for isolation"
4. [pytest Official](https://docs.pytest.org/en/stable/reference/fixtures.html) - "Higher-scoped fixtures execute before lower-scoped"

**Disagreement**: None found

**Implication**:
- **function** (default): Maximum isolation, use for most tests
- **class**: Shared across class methods
- **module**: Expensive setup shared in module (e.g., database connection)
- **session**: Very expensive setup (e.g., Docker containers)

**Rule**: Broader fixtures CANNOT use narrower fixtures. A session fixture cannot use a function-scoped fixture.

---

### Claim 5: conftest.py hierarchy enables modular fixture organization

**Confidence**: HIGH

**Evidence**:
1. [pytest Official Documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files) - "Fixtures in conftest.py available to tests in that directory and subdirectories"
2. [Pytest with Eric](https://pytest-with-eric.com/pytest-best-practices/pytest-organize-tests/) - "Nested conftest.py for directory-specific fixtures"
3. [Pytest with Eric - conftest](https://pytest-with-eric.com/pytest-best-practices/pytest-conftest/) - "Local conftest for narrow scope keeps suite maintainable"
4. [Medium - conftest.py](https://medium.com/@BuzonXXXX/pytest-conftest-py-44903c4c5046) - "Tests search upward for fixtures, never downward"

**Disagreement**: None found

**Implication**:
```
tests/
    conftest.py          # Session-wide fixtures (db connection)
    unit/
        conftest.py      # Unit-test fixtures (mocks)
        test_models.py
    integration/
        conftest.py      # Integration fixtures (test data)
        test_api.py
```

---

### Claim 6: pytest-mock preferred over raw monkeypatch for complex mocking

**Confidence**: MEDIUM

**Evidence**:
1. [pytest-mock Documentation](https://pytest-mock.readthedocs.io/en/latest/usage.html) - "mocker fixture with call tracking"
2. [GitHub pytest #4576](https://github.com/pytest-dev/pytest/issues/4576) - "mocker often less boilerplate; monkeypatch more explicit"
3. [Neuralception Blog](https://www.neuralception.com/python-better-unittest-pytest/) - "mocker streamlines code, allows return value in single line"

**Disagreement**: Some prefer monkeypatch for simplicity; no official recommendation exists

**Implication**:
- **Use monkeypatch** for: environment variables, simple attribute replacement, explicit control
- **Use pytest-mock** for: call tracking, return value configuration, spy functionality

```python
# monkeypatch - simple and explicit
def test_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert config.get_api_key() == "test-key"

# pytest-mock - when you need call tracking
def test_notification(mocker):
    mock_send = mocker.patch("app.email.send")
    notify_user(user_id=1)
    mock_send.assert_called_once_with(to="user@example.com")
```

---

### Claim 7: Property-based testing with Hypothesis catches edge cases humans miss

**Confidence**: HIGH

**Evidence**:
1. [Hypothesis Documentation](https://hypothesis.readthedocs.io/) - "Generates edge cases you might not have thought about"
2. [Semaphore Blog](https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest) - "Catches broader range of edge cases than example-based"
3. [Better Stack Guide](https://betterstack.com/community/guides/testing/hypothesis-unit-testing/) - "Generate arbitrary inputs; test properties not specific outputs"
4. [Pytest with Eric](https://pytest-with-eric.com/pytest-advanced/hypothesis-testing-python/) - "Integrates seamlessly with pytest"

**Disagreement**: None found

**Implication**: Use Hypothesis for:
- Parsers and serializers (round-trip properties)
- Mathematical operations (commutativity, associativity)
- Data transformations (idempotence, invariants)

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_idempotent(data):
    sorted_once = sorted(data)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice

@given(st.text())
def test_json_roundtrip(text):
    assert json.loads(json.dumps(text)) == text
```

---

### Claim 8: Coverage metrics alone are vanity metrics

**Confidence**: HIGH

**Evidence**:
1. [Medium - Meaningful Test Quality](https://medium.com/@sancharini.panda/how-to-measure-code-coverage-for-meaningful-test-quality-254c0b4cd9ef) - "High coverage hides problems: tests that break easily, missing validations"
2. [Jakob Breu](https://jakobbr.eu/2021/10/10/comparison-of-python-mutation-testing-modules/) - "Mutation testing validates test effectiveness"
3. [Deployed.pl](https://deployed.pl/blog/mutation-testing-in-python/) - "If mutants survive, tests didn't catch what they should"
4. [Opensource.com - mutmut](https://opensource.com/article/20/7/mutmut-python) - "Mutation testing complements coverage"

**Disagreement**: None found

**Implication**: Pair coverage with:
- **Mutation score**: Use mutmut (`mutmut run`) to validate test effectiveness
- **Assertion density**: Tests should have meaningful assertions, not just execution
- **Behavior coverage**: Focus on testing behaviors, not just lines

---

### Claim 9: Test isolation prevents flaky tests

**Confidence**: HIGH

**Evidence**:
1. [pytest Official - Flaky Tests](https://docs.pytest.org/en/stable/explanation/flaky.html) - "Flaky test indicates insufficient isolation"
2. [Kraken Engineering](https://engineering.kraken.tech/news/2022/05/23/flakey-python-tests.html) - "State pollution from caches, env vars, databases"
3. [Trunk.io](https://trunk.io/blog/how-to-avoid-and-detect-flaky-tests-in-pytest) - "External dependencies cause flakiness; quarantine strategy"
4. [Medium](https://medium.com/worldsensing-techblog/tips-and-tricks-for-unit-tests-b35af5ba79b1) - "Tests should never depend on other tests"

**Disagreement**: None found

**Implication**:
- Each test must be independently runnable
- Reset state in fixtures (use scope=function for isolation)
- Mock external dependencies
- Use pytest.approx() for floating point
- Quarantine flaky tests: `@pytest.mark.flaky`

---

### Claim 10: Tests outside application code is preferred layout

**Confidence**: HIGH

**Evidence**:
1. [pytest Official - Good Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) - "tests/ outside src/ recommended with importlib mode"
2. [Pytest with Eric](https://pytest-with-eric.com/pytest-best-practices/pytest-organize-tests/) - "Keeps application code clean"
3. [Real Python](https://realpython.com/pytest-python-testing/) - "Separate tests directory standard"
4. [Brian Okken](https://pragprog.com/titles/bopytest2/) - Demonstrates external tests layout

**Disagreement**: Some prefer tests alongside code for cohesion (rare in Python community)

**Implication**:
```
project/
    pyproject.toml
    src/
        mypackage/
            __init__.py
            module.py
    tests/
        __init__.py
        test_module.py
```

Add to pyproject.toml:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--import-mode=importlib"]
```

---

## Patterns & Paradigm Shifts

### Pattern 1: Behavior-Driven Test Naming

Modern pytest naming focuses on **what** not **how**:

```python
# Old pattern
def test_user_save()

# Better pattern
def test_user_persists_to_database()
def test_user_raises_on_duplicate_email()
```

### Pattern 2: Parametrization for Coverage

```python
@pytest.mark.parametrize("input,expected", [
    ("", 0),
    ("hello", 5),
    ("hello world", 11),
])
def test_string_length(input, expected):
    assert len(input) == expected
```

### Pattern 3: Fixture vs Parametrize Selection

- **Use @pytest.mark.parametrize**: Simple values, single test function
- **Use fixture parametrization**: Reuse across tests, need setup/teardown

```python
# Fixture parametrization for reuse
@pytest.fixture(params=["sqlite", "postgres"])
def database(request):
    return create_connection(request.param)

def test_insert(database):
    ...

def test_query(database):
    ...
```

### Pattern 4: Integration Test Separation

```
tests/
    unit/           # Fast, isolated, mock dependencies
    integration/    # Slower, real dependencies
    e2e/            # Full system tests
```

```bash
# CI: Unit tests gate PRs
pytest tests/unit -v

# Nightly: Full suite
pytest -v
```

---

## Anti-Patterns Identified

### Anti-Pattern 1: Test Interdependence

**Bad**:
```python
class TestUser:
    user = None  # Shared state!

    def test_create_user(self):
        TestUser.user = User.create("test")

    def test_user_has_name(self):
        assert TestUser.user.name == "test"  # Depends on test_create_user!
```

**Good**: Each test creates its own data via fixtures.

### Anti-Pattern 2: Branching in Tests

**Bad**:
```python
def test_user_roles(user):
    if user.is_admin:
        assert user.can_delete()
    else:
        assert not user.can_delete()  # Two tests in one!
```

**Good**: Separate tests for each branch.

### Anti-Pattern 3: Hardcoded File Fixtures

**Bad**: JSON files in `fixtures/` directory

**Good**: Factory functions that generate data on demand

### Anti-Pattern 4: Overly Broad Tests

**Bad**:
```python
def test_user_workflow():
    user = create_user()
    user.login()
    user.update_profile()
    user.logout()
    assert user.is_logged_out  # What failed if this fails?
```

**Good**: Separate tests for each action.

### Anti-Pattern 5: Testing Implementation Details

**Bad**:
```python
def test_user_internal_state():
    user = User()
    assert user._internal_cache == {}  # Testing private state
```

**Good**: Test public behavior only.

### Anti-Pattern 6: Ignoring Floating Point

**Bad**:
```python
assert result == 0.1 + 0.2  # Flaky! 0.30000000000000004
```

**Good**:
```python
assert result == pytest.approx(0.3)
```

---

## Gaps & Unknowns

1. **Async testing patterns**: Limited authoritative guidance on pytest-asyncio organization
2. **Large test suites (10k+)**: Scaling patterns not well documented
3. **AI/ML testing**: Emerging patterns for model testing not established
4. **Performance test integration**: Combining pytest with benchmarking tools
5. **Test data generation at scale**: Factory patterns for complex domain models
