# Research: Pytest Best Practices and Patterns

> **15-minute overview of pytest testing patterns, anti-patterns, and actionable recommendations**

---

## Research Metadata

| Field | Value |
|-------|-------|
| **Research ID** | pytest-best-practices-20260205 |
| **Date** | 2026-02-05 |
| **Depth** | Standard (4-6 hours) |
| **Sources** | 25 (6 Very High, 11 High, 7 Medium, 1 Low) |
| **Tool** | WebSearch + manual synthesis |
| **Researcher** | Rai (Claude Opus 4.5) |
| **Decision Context** | RaiSE testing guardrails (>90% coverage requirement) |

---

## Quick Navigation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [synthesis.md](synthesis.md) | Triangulated claims with evidence | 20 min |
| [recommendation.md](recommendation.md) | Actionable recommendations | 15 min |
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | All 25 sources with ratings | 10 min |
| [prompt.md](prompt.md) | Research prompt used | 5 min |

---

## Key Findings (TL;DR)

### 1. Test Structure: AAA Pattern is Standard

All pytest tests should follow **Arrange-Act-Assert-Cleanup**:
- Arrange: Set up test data (fixtures)
- Act: Single state-changing action
- Assert: Verify expected outcome
- Cleanup: Handle in fixtures, not test body

**Confidence**: HIGH (4 sources, including official pytest docs)

### 2. Fixture Design: Factory Pattern Preferred

Use **factory-as-fixture** for flexible test data:

```python
@pytest.fixture
def make_user():
    def _make_user(name: str, role: str = "viewer") -> User:
        return User(name=name, role=role)
    return _make_user
```

**Confidence**: HIGH (4 sources)

### 3. Mocking: Choose Tool by Need

| Need | Tool |
|------|------|
| Environment variables | `monkeypatch` |
| Call tracking | `pytest-mock` |
| Spy (real + tracking) | `mocker.spy()` |

**Confidence**: MEDIUM (3 sources, some disagreement)

### 4. Property-Based Testing: Essential for Edge Cases

Use **Hypothesis** for:
- Parsers (round-trip testing)
- Mathematical code (invariants)
- Data transformations

**Confidence**: HIGH (4 sources)

### 5. Coverage: Metrics Are Vanity Without Mutation Testing

- Line coverage alone hides problems
- Complement with **mutation testing** (mutmut)
- Target: >90% coverage + >70% mutation score

**Confidence**: HIGH (4 sources)

### 6. Flaky Tests: Isolation is Key

Common causes:
- Shared state between tests
- External dependencies
- Floating point comparisons
- Non-deterministic timing

**Confidence**: HIGH (4 sources)

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Solution |
|--------------|---------|----------|
| Test interdependence | Order-dependent failures | Fixtures for isolation |
| Branching in tests | Multiple tests in one | Separate test functions |
| Hardcoded file fixtures | Brittle, hard to maintain | Factory functions |
| Testing implementation | Breaks on refactor | Test public behavior |
| Ignoring floating point | Flaky comparisons | `pytest.approx()` |

---

## Recommended Test Organization

```
project/
    src/mypackage/
    tests/
        conftest.py          # Session fixtures
        unit/
            conftest.py      # Unit mocks
            test_*.py        # Mirror src/ structure
        integration/
            conftest.py      # Integration fixtures
            test_*.py
```

---

## Actionable Checklist for RaiSE

- [ ] Use AAA pattern in all tests
- [ ] Factory fixtures for test data
- [ ] conftest.py hierarchy for fixture organization
- [ ] pytest-mock for call tracking needs
- [ ] Hypothesis for parsers/transformations
- [ ] >90% line + >85% branch coverage
- [ ] Mutation testing (advisory, weekly)
- [ ] Quarantine flaky tests with `@pytest.mark.flaky`

---

## Evidence Quality

| Level | Count | % | Examples |
|-------|-------|---|----------|
| Very High | 6 | 24% | pytest docs, Hypothesis docs |
| High | 11 | 44% | Brian Okken book, Real Python, NerdWallet |
| Medium | 7 | 28% | Community blogs, Medium articles |
| Low | 1 | 4% | Single-author comparison |

All major claims triangulated with 3+ sources.

---

## Gaps Identified

1. **Async testing patterns** - Limited pytest-asyncio guidance
2. **Large test suites (10k+)** - Scaling patterns undocumented
3. **AI/ML testing** - Emerging patterns not established
4. **Performance testing** - Integration with benchmarking tools

---

## Governance Linkage

This research informs:
- `governance/solution/guardrails.md` - Testing standards update
- Future ADR on testing architecture
- RaiSE project testing patterns

---

## Sources (Top 10)

1. [pytest Official - Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
2. [pytest Official - Good Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
3. [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
4. [Python Testing with pytest - Brian Okken](https://pragprog.com/titles/bopytest2/)
5. [Real Python - Effective Testing](https://realpython.com/pytest-python-testing/)
6. [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
7. [NerdWallet Engineering](https://www.nerdwallet.com/blog/engineering/5-pytest-best-practices/)
8. [Pytest with Eric - Fixture Scopes](https://pytest-with-eric.com/fixtures/pytest-fixture-scope/)
9. [Kraken Engineering - Flaky Tests](https://engineering.kraken.tech/news/2022/05/23/flakey-python-tests.html)
10. [Automation Panda - AAA Pattern](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/)

Full catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)
