## Implementation Plan

> Added by `/rai-epic-plan` — YYYY-MM-DD

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S{N}.1 | S | None | M1 | {Why first?} |
| 2 | S{N}.2 | M | S{N}.1 | M1 | {Why second?} |
| 3 | S{N}.3 | S | S{N}.2 | M2 | {Why here?} |

### Milestones

| Milestone | Stories | Target | Success Criteria |
|-----------|---------|--------|------------------|
| **M1: Walking Skeleton** | S{N}.1, S{N}.2 | {Day} | {What proves it works?} |
| **M2: Core MVP** | +S{N}.3, S{N}.4 | {Day} | {What proves value?} |
| **M3: Feature Complete** | +S{N}.5... | {Day} | All planned stories done |
| **M4: Epic Complete** | — | {Day} | Done criteria met, retro done |

### Parallel Work Streams

```
Time →
Stream 1 (Critical): S{N}.1 ─► S{N}.2 ─► S{N}.5
                              ↓
Stream 2 (Parallel):        S{N}.3 ─► merge
                                       ↑
Stream 3 (Parallel):        S{N}.4 ───┘
```

**Merge points:**
- After S{N}.1: split into parallel streams
- Before S{N}.5: merge parallel streams

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S{N}.1 | S | Pending | — | — | |
| S{N}.2 | M | Pending | — | — | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| {Risk 1} | H/M | {Strategy} |
| {Risk 2} | M/L | {Strategy} |
