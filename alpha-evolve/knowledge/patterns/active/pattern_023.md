---
type: pattern
id: pattern_023
name: "CD improvement rate at 1e-13 shows no convergence over 70+ rounds"
lifecycle: active
confidence: 0.7
first_seen: generation_10
last_updated: generation_10
evidence: [gen010_exploit_1_sol01]
related_ideas: [idea_019]
tags: [coordinate-descent, convergence, 1e-13, sustained-improvements, float64]
---

At the 1e-13 delta scale, coordinate descent on the TTT-Discover 30k array maintains
a stable improvement rate of ~5000 improvements/round over 70+ rounds with NO decay.

**Gen 10 evidence (exploit_1):**

| Delta Scale | Total Improvements | Status |
|---|---|---|
| ≥ 1e-9 | 0 | Dead — fully converged |
| 1e-10 | 5 | Essentially dead |
| 1e-11 | 85 | Rare, declining |
| 1e-12 | 997 | Active, steady (~14/round) |
| **1e-13** | **369,685** | **Dominant** (~5000/round, no decay) |
| 1e-14 | 416 | **Emerging** (increasing trend) |

**Critical observations:**
1. The 1e-13 scale dominates all others by 370x
2. The improvement rate per round is STABLE — no convergence trend in 71 rounds
3. 1e-14 improvements are INCREASING (0-1/round early, 9-18/round late)
4. Each accepted modification at 1e-13 creates new opportunities at other elements
   via autoconvolution coupling (cascading effect)

**Revision of pattern_012:** The "exponential decay" pattern applies to the REAL C
improvement per round (confirmed: each round contributes less verified C reduction),
but NOT to the improvement COUNT. The landscape has essentially infinite fine-scale
structure at 1e-13.

**Implication:** The float64 precision floor for CD has NOT been reached. With
sufficient time and mandatory FFT resync, many more rounds could be run. However,
the real C improvement per round is ~3-5e-13 (limited by drift), so the practical
benefit diminishes even as improvements continue.
