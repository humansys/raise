# Sequencing Strategies Deep Dive

> Reference material for `/rai-epic-plan` Step 3.
> For quick reference, see the decision matrix in the main skill.

---

## Risk-First (Primary Strategy)

**Philosophy:** Uncertainty decreases as you learn. Early features teach you about the codebase, the problem, and your velocity. Tackling risky features early means:
- More time to recover from surprises
- Learning informs later features
- Confidence grows throughout epic

**Identify risky features by:**
- New technology or unfamiliar patterns
- Integration with external systems
- Unclear requirements (even after design)
- Performance or scalability unknowns
- Team has never done something similar

**Anti-pattern:** "Let's do the easy features first to build momentum" — This feels good but front-loads certainty and back-loads risk. By the time you hit the hard features, deadline pressure is highest.

---

## Walking Skeleton

**Philosophy:** Prove the architecture works before investing heavily. A walking skeleton is the smallest end-to-end path through the system that demonstrates:
- Key architectural decisions are valid
- Integration points work
- Development environment is productive
- Deployment pipeline functions

**Walking skeleton features:**
- Minimal but complete path from input to output
- Touches all layers (UI, API, data, infrastructure)
- Can be demonstrated (not just "it compiles")
- Provides foundation for rest of features

**Example:** For a governance toolkit epic, walking skeleton might be:
- F1: Extract one concept from one file
- F2: Build minimal graph with one relationship
- F3: Query graph and return result

**Anti-pattern:** Building all of layer 1 before touching layer 2. This delays integration risk discovery.

---

## Quick Wins

**Philosophy:** Early success builds momentum and validates process. Quick wins are features that:
- Can be completed in one session
- Provide visible, demonstrable value
- Don't block other features
- Build confidence in approach

**Use quick wins when:**
- Starting a new codebase or technology
- Team morale needs boost
- Stakeholders need early visibility
- Validating development process

**Anti-pattern:** Only quick wins — avoiding hard features indefinitely. Quick wins support risk-first; they don't replace it.

---

*Reference document for /rai-epic-plan*
