# Experiments

Quick validation experiments before committing to architectural decisions.

## Graph MVC Validation (2026-01-31)

**Branch:** `experiment/e2/graph-mvc-validation`

**Hypothesis:** Graph-based Minimum Viable Context can reduce token usage by 20%+ while maintaining context accuracy.

**Files:**
- `graph-spike.yaml` - Sample governance graph
- `test_mvc.py` - Validation script

**Run experiment:**
```bash
cd dev/experiments
python test_mvc.py
```

**Decision criteria:**
- >20% savings: Build graph-based MVC in E2
- 10-20% savings: Marginal, consider deferring
- <10% savings: Skip, not worth complexity

**Duration:** 2 hours

**Status:** Ready to run
