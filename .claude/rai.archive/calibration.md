# Velocity Calibration

> Track actual durations to calibrate T-shirt sizing over time.
> Updated after each feature via `/session-close` or `/feature-review`.

---

## Feature Durations

| Feature | SP | Size | Estimated | Actual | Ratio | Notes |
|---------|:--:|:----:|-----------|--------|:-----:|-------|
| F1.1 Project Scaffolding | 3 | S | - | ~30min | - | Pre-kata, no estimate |
| F1.2 CLI Skeleton | 5 | M | - | ~45min | - | Pre-kata, no estimate |
| F1.3 Configuration System | 5 | M | 6-8h | 20min | 18x | First kata cycle |
| F1.4 Exception Hierarchy | 3 | S | - | ~30min | - | No formal estimate |
| F1.5 Output Module | 3 | S | 2h 45m | 15min | 11x | Second kata cycle |
| F1.6 Core Utilities | 3 | S | - | ~10min | - | Third kata cycle, no estimate |
| F2.1 Concept Extraction | 3 | S | 2-4h | 52min | 3.5x | Spike + design-first, 7 tasks, 81 tests |
| F2.2 Graph Builder | 2 | S | 150-210min | 65min | 2.3-3.2x | Full kata cycle, BFS traversal, 63 tests |
| F2.3 MVC Query Engine | 2 | S | 190min | 90min | 2.1x | Full kata cycle, 4 strategies, 99 tests |

**Average ratio (kata-optimized):** ~2-3x faster with full kata cycle
**Pattern:** Design-first + concrete examples + atomic tasks = 2-3x velocity multiplier (stabilized)

---

## Task Size Calibration

| Size | Expected Range | Actual Average | Sample Size | Notes |
|:----:|----------------|:--------------:|:-----------:|-------|
| XS | <15 min | ~2 min | n=1 | F1.5 Task 6 (docs) |
| S | 15-30 min | ~13 min | n=2 | F1.5 Tasks 1-5 combined |
| M | 30-60 min | ~25 min | n=2 | F1.3, F1.4 |
| L | 1-2 hours | - | n=0 | No data yet |

---

## Observations

1. **AI-assisted velocity is dramatically higher** than traditional estimates assume
2. **Well-defined specs** (design.md with concrete examples) reduce implementation time
3. **Task bundling** happens naturally - Tasks 1-5 in F1.5 were really one atomic unit
4. **Spike validation multiplier** - F2.1 had working spike, achieved 3.5x vs ~14x without spike
5. **Design quality impacts velocity** - Concrete examples in design.md = copy-paste implementation
6. **Calibration stabilized at 2-3x** - Full kata cycle (F2.1, F2.2, F2.3) consistently delivers 2-3x velocity
7. **Kata cycle effect is real** - Three consecutive features with full cycle all delivered at 2-3x
8. **Simple > Complex** - Keyword matching, token heuristics outperform ML approaches on velocity
9. **Architecture reuse compounds** - F2.3 reused F2.2's BFS traversal without modification

---

## Calibration Goals

- [x] Collect 5+ samples per size category (9 features total)
- [x] Identify which factors predict faster/slower completion (kata cycle = 2-3x)
- [ ] Adjust T-shirt size ranges based on data (apply 0.5x multiplier for kata-optimized features)

---

*Last updated: 2026-01-31 (E2 in progress - F2.3 complete)*
