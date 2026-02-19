# Evidence Catalog: Pattern Reinforcement Scoring (RES-TEMPORAL-001b)

## Sources

### S13: Wilson Score Lower Bound (Wilson 1927, popularized by Evan Miller 2009)
- **Type**: Primary (foundational statistics)
- **Evidence Level**: Very High
- **Key Finding**: Lower bound of confidence interval for Bernoulli parameter. Formula: `(p̂ + z²/2n - z√((p̂(1-p̂)+z²/4n)/n)) / (1+z²/n)`. Handles small sample sizes gracefully — penalizes items with few votes while rewarding consistent positive ratios.
- **Relevance**: Direct analog to our +1/0/-1 scoring. Reddit uses this for comment ranking. Solves the "1 vote at 100% shouldn't beat 100 votes at 90%" problem.
- **URL**: https://www.evanmiller.org/how-not-to-sort-by-average-rating.html

### S14: Reddit Hot Ranking (Salihefendic 2010)
- **Type**: Secondary (practitioner, well-documented)
- **Evidence Level**: High
- **Key Finding**: `score = sign * log10(max(|ups-downs|, 1)) + seconds/45000`. Combines vote differential with temporal decay. Log scale means first 10 votes matter as much as next 100.
- **Relevance**: Demonstrates vote + time combination. Our analog: reinforcement_score + recency_decay.
- **URL**: https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9

### S15: SM-2 Spaced Repetition (Wozniak 1987)
- **Type**: Primary (foundational algorithm)
- **Evidence Level**: Very High
- **Key Finding**: Quality rating 0-5 adjusts ease factor: `EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))`. Quality ≥ 3 = success (interval grows). Quality < 3 = failure (reset to day 1). Minimum EF = 1.3.
- **Relevance**: Maps perfectly to our +1/0/-1. The ease factor adjustment is a form of Bayesian belief updating about pattern reliability.

### S16: FSRS (Free Spaced Repetition Scheduler, Ye 2022-2024)
- **Type**: Primary (state of the art, replaces SM-2 in Anki)
- **Evidence Level**: High
- **Key Finding**: Three-state model: Difficulty (D), Stability (S), Retrievability (R). R(t) = (1 + factor * t/S)^(-w20). After success: stability increases inversely with D and current S. After failure: stability drops via `S'_f = w11 * D^(-w12) * ((S+1)^w13 - 1) * e^(w14*(1-R))`.
- **Relevance**: Most sophisticated spaced repetition. But 21 parameters — too complex for our use case. SM-2's simplicity is better for ~200 patterns.
- **URL**: https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm

### S17: TrueSkill (Herbrich et al., Microsoft Research 2006)
- **Type**: Primary (NeurIPS paper)
- **Evidence Level**: Very High
- **Key Finding**: Bayesian skill estimation with explicit uncertainty. Each item has μ (skill estimate) and σ (confidence). Conservative estimate = μ - k*σ. σ shrinks with more observations. Handles small samples naturally.
- **Relevance**: The μ-σ model is elegant for patterns: μ = average validation score, σ = uncertainty. New patterns start with high σ (uncertain), converge as evaluations accumulate. But adds complexity over Wilson score.
- **URL**: https://trueskill.org/

### S18: Bayesian Knowledge Tracing (BKT, Corbett & Anderson 1995)
- **Type**: Primary (foundational educational technology)
- **Evidence Level**: Very High
- **Key Finding**: Models knowledge as latent binary state (known/not-known) with transition probabilities. Updates belief via Bayes rule after each observation. Parameters: P(L0) initial, P(T) learn, P(G) guess, P(S) slip.
- **Relevance**: Conceptually similar — we're tracking whether a pattern is "valid knowledge" or not, updating belief with each observation. But binary state is too restrictive for our use.

### S19: Stanford Generative Agents — Importance Scoring (Park et al. 2023)
- **Type**: Primary (ACM, peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: LLM rates memory importance on 1-10 scale. Combined with recency and relevance. All three normalized to [0,1].
- **Relevance**: Confirms LLM-as-evaluator approach. Our variant: Rai evaluates pattern applicability post-implementation.

### S20: Agentic RL with Implicit Step Rewards (arXiv:2509.19199, 2025)
- **Type**: Primary (preprint)
- **Evidence Level**: Medium
- **Key Finding**: Credit assignment from implicit signals during agent workflow execution. Uses outcome-level reward to infer step-level rewards without explicit labels.
- **Relevance**: Theoretical grounding for deriving pattern value from implementation outcome. The pattern wasn't "rated" — its value was implicit in whether it was followed.
