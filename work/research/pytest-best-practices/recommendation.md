# Recommendation: Pytest Best Practices for RaiSE

> Research ID: pytest-best-practices-20260205
> Date: 2026-02-05
> Based on: 25 sources, 10 triangulated claims

---

## Executive Recommendation

**Decision**: Adopt a tiered testing strategy that combines pytest fixtures, property-based testing, and mutation testing to ensure meaningful test coverage beyond line metrics.

**Confidence**: HIGH

**Rationale**: Convergent evidence from official documentation, expert practitioners, and production engineering blogs supports a specific set of patterns that maximize test reliability and maintainability while minimizing flakiness and false confidence from vanity metrics.

---

## Specific Recommendations

### 1. Test Structure (HIGH Confidence)

**Adopt AAA Pattern strictly**:

```python
def test_user_creation_persists_to_database(db_session, make_user):
    # Arrange
    user_data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = make_user(**user_data)

    # Assert
    assert db_session.query(User).filter_by(email=user_data["email"]).one()
```

**Key rules**:
- One Act per test (single state-changing action)
- Multiple Asserts OK if testing same behavior
- Cleanup in fixtures, not test body

---

### 2. Fixture Design (HIGH Confidence)

**Use factory-as-fixture for flexibility**:

```python
# conftest.py
@pytest.fixture
def make_user(db_session):
    created_users = []

    def _make_user(
        name: str = "Test User",
        email: str | None = None,
        role: str = "viewer"
    ) -> User:
        email = email or f"{name.lower().replace(' ', '.')}@test.com"
        user = User(name=name, email=email, role=role)
        db_session.add(user)
        db_session.commit()
        created_users.append(user)
        return user

    yield _make_user

    # Cleanup
    for user in created_users:
        db_session.delete(user)
    db_session.commit()
```

**Scope selection guidelines**:

| Scope | Use When | Example |
|-------|----------|---------|
| function | Default, maximum isolation | User factory, mock data |
| module | Expensive setup, shared in file | Database schema setup |
| session | Very expensive, immutable | Docker containers, test DB |

---

### 3. Test Organization (HIGH Confidence)

**Directory structure**:

```
project/
    src/
        mypackage/
            models/
            services/
    tests/
        conftest.py              # Session fixtures (db, containers)
        unit/
            conftest.py          # Unit mocks
            models/
                test_user.py     # Mirror src/ structure
            services/
                test_auth.py
        integration/
            conftest.py          # Integration fixtures
            test_api.py
        e2e/
            conftest.py
            test_workflows.py
```

**conftest.py hierarchy**:
- Root: Session-scoped, expensive fixtures
- Per-directory: Domain-specific fixtures
- Never import from conftest.py files

---

### 4. Mocking Strategy (MEDIUM Confidence)

**Decision matrix**:

| Need | Tool | Example |
|------|------|---------|
| Environment variables | monkeypatch | `monkeypatch.setenv("KEY", "val")` |
| Simple attribute replacement | monkeypatch | `monkeypatch.setattr(obj, "attr", value)` |
| Call tracking needed | pytest-mock | `mocker.patch().assert_called_once()` |
| Spy (real + tracking) | pytest-mock | `mocker.spy(obj, "method")` |
| Return value configuration | pytest-mock | `mocker.patch(..., return_value=x)` |

**Anti-pattern**: Don't mix monkeypatch and pytest-mock in same test.

---

### 5. Property-Based Testing (HIGH Confidence)

**When to use Hypothesis**:
- Parsers and serializers (round-trip testing)
- Mathematical/algorithmic code
- Data transformations with invariants
- Any code where edge cases are hard to enumerate

**Integration pattern**:

```python
from hypothesis import given, strategies as st, settings

@given(st.text())
@settings(max_examples=100)
def test_json_roundtrip(text):
    """Text survives JSON serialization."""
    assert json.loads(json.dumps(text)) == text

@given(st.lists(st.integers(), min_size=1))
def test_max_in_sorted_list(numbers):
    """Max element is last after sorting."""
    sorted_list = sorted(numbers)
    assert sorted_list[-1] == max(numbers)
```

---

### 6. Coverage Strategy (HIGH Confidence)

**Beyond line coverage**:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=90"

[tool.coverage.run]
branch = true  # Branch coverage, not just line

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

**Complement with mutation testing**:

```bash
# Run mutation testing periodically
mutmut run --paths-to-mutate=src/

# Check mutation score
mutmut results
```

**Target metrics**:
- Line coverage: >90% (gate)
- Branch coverage: >85% (gate)
- Mutation score: >70% (advisory, not gate)

---

### 7. Preventing Flaky Tests (HIGH Confidence)

**Isolation checklist**:
- [ ] Each test runnable in isolation (`pytest test_file.py::test_specific -v`)
- [ ] No shared mutable state between tests
- [ ] External calls mocked in unit tests
- [ ] `pytest.approx()` for floating point
- [ ] Deterministic waits (not `time.sleep()`) for async

**Quarantine strategy**:

```python
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_external_api():
    """Known flaky - external dependency."""
    ...
```

```bash
# Exclude from CI gate
pytest -m "not flaky"

# Run flaky separately (non-blocking)
pytest -m "flaky" --continue-on-collection-errors
```

---

## Trade-offs Accepted

| Decision | Trade-off | Mitigation |
|----------|-----------|------------|
| >90% coverage gate | May slow development | Focus on meaningful coverage, not chasing numbers |
| Factory fixtures | More fixture code | Reusable, DRY, type-safe |
| Strict AAA | More test functions | Clearer failure diagnosis |
| Mutation testing | Slow, not for CI | Run nightly/weekly, advisory only |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Coverage gaming (meaningless tests) | Medium | High | Mutation testing, code review |
| Fixture complexity explosion | Medium | Medium | Factory pattern, scope discipline |
| Slow test suite | Low | Medium | Parallel execution, scope optimization |
| Flaky test accumulation | Medium | High | Quarantine policy, root cause analysis |

---

## Implementation Roadmap

### Phase 1: Foundation (Immediate)
- [ ] Establish test directory structure
- [ ] Create base conftest.py with factory patterns
- [ ] Configure pytest.ini/pyproject.toml
- [ ] Add coverage gate to CI

### Phase 2: Enhancement (Week 2-3)
- [ ] Add pytest-mock for complex mocking
- [ ] Introduce Hypothesis for parsers/transformations
- [ ] Set up quarantine workflow for flaky tests

### Phase 3: Quality Gates (Week 4+)
- [ ] Add mutation testing (advisory, nightly)
- [ ] Review coverage quality vs quantity
- [ ] Document team-specific patterns

---

## Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| unittest only | Less expressive, more boilerplate |
| nose2 | Less active ecosystem, pytest dominant |
| Ward (BDD style) | Niche, less tooling support |
| 100% coverage requirement | Encourages gaming, diminishing returns above 90% |

---

## RaiSE Guardrails Update

Based on this research, recommend updating `governance/solution/guardrails.md`:

```markdown
### Testing — REQUIRED

- **>90% line coverage** on core codebase (via pytest-cov)
- **>85% branch coverage** (via coverage.py branch mode)
- All tests must pass before commit
- Tests in `tests/` mirroring `src/` structure
- Use pytest fixtures (not setup/teardown methods)
- Mock external dependencies in unit tests
- Test edge cases with Hypothesis (RECOMMENDED for parsers/transformations)
- Verify with: `pytest --cov=src --cov-branch --cov-fail-under=90`

**RECOMMENDED:** Run mutation testing (`mutmut`) weekly; target >70% mutation score.
```

---

## Sources

Primary sources informing this recommendation:
- [pytest Official Documentation](https://docs.pytest.org/en/stable/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Python Testing with pytest, 2nd Ed. - Brian Okken](https://pragprog.com/titles/bopytest2/)
- [Real Python - Effective Python Testing](https://realpython.com/pytest-python-testing/)
- [NerdWallet Engineering Blog](https://www.nerdwallet.com/blog/engineering/)
- [Kraken Engineering - Flaky Tests](https://engineering.kraken.tech/)

Full evidence catalog: `sources/evidence-catalog.md`
