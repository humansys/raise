# Evidence Catalog: Pytest Best Practices

> Research ID: pytest-best-practices-20260205
> Date: 2026-02-05
> Sources: 25 (triangulation complete)

---

## Summary Statistics

- **Total Sources**: 25
- **Evidence Distribution**:
  - Very High: 6 (24%) - Official documentation, authoritative references
  - High: 11 (44%) - Expert practitioners, established engineering blogs
  - Medium: 7 (28%) - Community-validated, engaged articles
  - Low: 1 (4%) - Single-source claims
- **Temporal Coverage**: 2020-2026

---

## Sources by Topic

### Official Documentation (Very High Evidence)

**Source 1**: [pytest - How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: Fixtures are modular, explicit, and scalable; can depend on other fixtures; support multiple scopes (function, class, module, session)
- **Relevance**: Authoritative source for fixture design patterns

**Source 2**: [pytest - Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: Recommends tests outside application code with `src/` layout; use `--import-mode=importlib`; avoid `setup.py test`
- **Relevance**: Authoritative source for project organization

**Source 3**: [pytest - Anatomy of a test](https://docs.pytest.org/en/stable/explanation/anatomy.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: AAA pattern (Arrange-Act-Assert-Cleanup) is official recommendation; tests should focus on behavior
- **Relevance**: Authoritative source for test structure

**Source 4**: [pytest - How to monkeypatch/mock](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: monkeypatch provides safe patching that auto-undoes after test; use setattr for attributes, setenv for environment
- **Relevance**: Authoritative source for mocking strategies

**Source 5**: [pytest - Flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: Flaky tests indicate insufficient isolation; higher-level tests more prone to flakiness; quarantine strategy recommended
- **Relevance**: Authoritative guidance on test reliability

**Source 6**: [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (continuously updated)
- **Key Finding**: Property-based testing generates edge cases automatically; integrates seamlessly with pytest; use strategies for input generation
- **Relevance**: Authoritative source for property-based testing

---

### Expert Practitioners (High Evidence)

**Source 7**: [Python Testing with pytest, 2nd Edition - Brian Okken](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)
- **Type**: Primary (book by pytest expert)
- **Evidence Level**: High
- **Date**: 2022
- **Key Finding**: Top 3 features: fixtures, parametrization, plugins; fixtures change how you think about tests; plain assert preferred
- **Relevance**: Expert guidance from Test & Code podcast host

**Source 8**: [Real Python - Effective Python Testing With pytest](https://realpython.com/pytest-python-testing/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Write small, focused tests; use markers for organization; leverage fixtures for DRY; parametrize for coverage
- **Relevance**: Comprehensive practitioner guide

**Source 9**: [pytest-mock Documentation](https://pytest-mock.readthedocs.io/en/latest/usage.html)
- **Type**: Primary
- **Evidence Level**: High
- **Date**: 2024 (continuously updated)
- **Key Finding**: mocker.spy tracks calls without replacing logic; spy_return and spy_return_list for return tracking; MagicMock-based
- **Relevance**: Authoritative for pytest-mock patterns

**Source 10**: [NerdWallet - 5 Pytest Best Practices](https://www.nerdwallet.com/blog/engineering/5-pytest-best-practices/)
- **Type**: Secondary (established company engineering blog)
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Prefer plain assert over unittest.TestCase; use fixtures over setup/teardown; parametrize for multiple inputs
- **Relevance**: Production-validated patterns from fintech engineering

**Source 11**: [Pytest with Eric - Fixture Scopes](https://pytest-with-eric.com/fixtures/pytest-fixture-scope/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Choose scope based on isolation needs vs performance; session scope for expensive setup; function scope for maximum isolation
- **Relevance**: Detailed scope selection guidance

**Source 12**: [Pytest with Eric - Test Organization](https://pytest-with-eric.com/pytest-best-practices/pytest-organize-tests/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Mirror src/ structure in tests/; use conftest.py hierarchy; local conftest for narrow scope
- **Relevance**: Practical organization patterns

**Source 13**: [Inspired Python - Five Advanced Fixture Patterns](https://www.inspiredpython.com/article/five-advanced-pytest-fixture-patterns)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Factory as fixture for multiple instances; fixture dependency injection; parametrized fixtures for variations
- **Relevance**: Advanced fixture patterns

**Source 14**: [Fiddler AI - Advanced Pytest Patterns](https://www.fiddler.ai/blog/advanced-pytest-patterns-harnessing-the-power-of-parametrization-and-factory-methods)
- **Type**: Secondary (ML company engineering blog)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Factory methods reduce fixture complexity; parametrization covers edge cases systematically
- **Relevance**: Production patterns from AI/ML company

**Source 15**: [Semaphore - Property-Based Testing with Hypothesis](https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Test properties/invariants rather than specific values; combine with pytest parametrize; catches edge cases humans miss
- **Relevance**: Integration patterns for hypothesis

**Source 16**: [Automation Panda - Arrange Act Assert](https://automationpanda.com/2020/07/07/arrange-act-assert-a-pattern-for-writing-good-tests/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2020
- **Key Finding**: AAA forces focus on individual behaviors; separates setup from action; de facto style for pytest
- **Relevance**: Foundational test structure guidance

**Source 17**: [Kraken Engineering - Patterns of Flakey Python Tests](https://engineering.kraken.tech/news/2022/05/23/flakey-python-tests.html)
- **Type**: Secondary (established company engineering blog)
- **Evidence Level**: High
- **Date**: 2022
- **Key Finding**: State pollution from caches, environment variables, databases; external dependencies cause flakiness; isolation is key
- **Relevance**: Production flakiness patterns from energy company

---

### Community-Validated (Medium Evidence)

**Source 18**: [Trunk.io - Avoid and Detect Flaky Tests](https://trunk.io/blog/how-to-avoid-and-detect-flaky-tests-in-pytest)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: pytest.approx() for floating point; quarantine flaky tests; async operations need deterministic waits
- **Relevance**: Practical flakiness mitigation

**Source 19**: [Medium - How to Measure Code Coverage](https://medium.com/@sancharini.panda/how-to-measure-code-coverage-for-meaningful-test-quality-254c0b4cd9ef)
- **Type**: Tertiary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Coverage is vanity metric without mutation score; assertion density matters; pair coverage with behavior validation
- **Relevance**: Coverage anti-patterns and alternatives

**Source 20**: [Medium - Tips and Tricks for Unit Tests](https://medium.com/worldsensing-techblog/tips-and-tricks-for-unit-tests-b35af5ba79b1)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2022
- **Key Finding**: Tests should never depend on other tests; branching in tests is anti-pattern; avoid file fixtures
- **Relevance**: Anti-pattern documentation

**Source 21**: [Better Stack - Hypothesis Guide](https://betterstack.com/community/guides/testing/hypothesis-unit-testing/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Generate arbitrary inputs; test properties not specific outputs; complements example-based testing
- **Relevance**: Practical hypothesis patterns

**Source 22**: [James Cooke - AAA Pattern for Python](https://jamescooke.info/arrange-act-assert-pattern-for-python-developers.html)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2020
- **Key Finding**: Single Act per test; multiple Asserts OK if testing same behavior; cleanup in fixtures
- **Relevance**: Python-specific AAA guidance

**Source 23**: [Hexlet - Bad and Good Testing Practices](https://hexlet.io/courses/python-testing/lessons/bad-practice/theory_unit)
- **Type**: Tertiary (educational platform)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Anti-patterns: testing everything in one function, dependent tests, complex setup
- **Relevance**: Educational anti-pattern list

**Source 24**: [GitHub pytest Issue #4576 - monkeypatch vs mock.patch](https://github.com/pytest-dev/pytest/issues/4576)
- **Type**: Primary (project discussion)
- **Evidence Level**: Medium
- **Date**: 2019
- **Key Finding**: No clear guidelines on when to use which; mocker often less boilerplate; monkeypatch more explicit
- **Relevance**: Community discussion on mocking tradeoffs

---

### Limited/Single Source (Low Evidence)

**Source 25**: [Jakob Breu - Mutation Testing Comparison](https://jakobbr.eu/2021/10/10/comparison-of-python-mutation-testing-modules/)
- **Type**: Secondary (personal blog)
- **Evidence Level**: Low
- **Date**: 2021
- **Key Finding**: mutmut is the only recommendable tool; works out of box; cosmic-ray also viable
- **Relevance**: Mutation testing tool selection (single practitioner evaluation)

---

## Evidence Gaps

1. **Async testing patterns**: Limited coverage of pytest-asyncio best practices
2. **Large-scale test suite management**: Few sources address 10k+ test suites
3. **Performance testing integration**: Limited guidance on combining pytest with performance tools
4. **AI/ML testing specifics**: Emerging area with limited established patterns
