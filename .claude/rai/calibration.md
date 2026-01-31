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

**Average ratio:** ~14x faster than traditional estimates

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
4. **Calibration needs more data** - sample sizes too small for confidence

---

## Calibration Goals

- [ ] Collect 5+ samples per size category
- [ ] Identify which factors predict faster/slower completion
- [ ] Adjust T-shirt size ranges based on data

---

*Last updated: 2026-01-31 (F1.5 completion)*
