---
type: idea
id: idea_007
name: "Graduated smooth-max (log-sum-exp temperature annealing)"
lifecycle: established
confidence: 0.9
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol02, gen002_exploit_1_sol01]
contradicted_by: []
related_ideas: [idea_001, idea_005, idea_004]
cluster: cluster_001
tags: [smooth-max, log-sum-exp, temperature, annealing, gradient]
---

Replace jnp.max in the objective with a log-sum-exp soft maximum, annealing
the temperature from warm (T=0.05) to cold (T=0.0003) over training.

**Rationale:** The true max operator has a one-hot gradient — only the single
argmax element receives gradient signal. This starves all other function values
of learning signal and traps the optimizer. Log-sum-exp spreads gradient across
all near-max elements, enabling escape from the C ~ 1.5185 basin.

**Evidence:**
- Gen 1: full_1/sol03 (T=0.05->0.0003, 8 restarts, N=600): C = 1.5108.
- Gen 2: explore_1/sol03 (coarse-to-fine + smooth-max, warm fine): C = 1.5091 — NEW BEST.
- Gen 2: explore_1/sol02 (same approach, 8 restarts): C = 1.5093.
- Gen 2: exploit_1/sol01 (16 restarts, extended to T=0.0001): C = 1.5107.
- No solution has broken below 1.5155 without smooth-max.
- Extended schedules (T=0.0001 6th phase) provide negligible benefit — optimization
  converges by T=0.0003.

**Temperature schedule matters:** Too warm (T > 0.1) approximates poorly.
Too cold too fast loses the gradient-spreading benefit. The 5-phase schedule
[0.05, 0.01, 0.003, 0.001, 0.0003] remains the proven baseline.

This is the single most impactful idea across both generations. Confidence
raised to 0.9 based on gen 2 confirmation across multiple agents and
combinations.
