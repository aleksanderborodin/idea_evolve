---
type: pattern
id: pattern_006
name: "Arcsine initialization dominates other families at coarse scale"
lifecycle: active
confidence: 0.6
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_explore_2_sol01, gen003_explore_2_sol04]
related_ideas: [idea_013, idea_003, idea_012]
tags: [initialization, arcsine, comparison, coarse]
---

In head-to-head comparison across initialization families at coarse scale (N=80):
- Arcsine (U-shaped, endpoint-concentrated): Best, occupies all top-5 slots in 25-seed funnel
- Gaussian bumps: Second best, familiar ~1.5091 territory
- Comb (narrow peaks): Mediocre
- Step function: Dead end (1.519-1.522)

The arcsine profile (peaks at interval endpoints) on a biased subinterval
consistently outperforms bell-shaped initializations. However, the final fine
scores differ by only ~0.0001 (arcsine: 1.5090, Gaussian: 1.5091), suggesting
all families converge to the same attractor basin. Arcsine may find this basin
more reliably rather than finding a better basin.

Subinterval placement matters: [-0.05, 0.22] (positive bias) and [-0.22, 0.05]
(negative bias) work better than centered or full-domain arcsine.
