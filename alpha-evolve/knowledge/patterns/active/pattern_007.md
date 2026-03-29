---
type: pattern
id: pattern_007
name: "Published solutions are local minima for smooth-max Adam"
lifecycle: active
confidence: 0.85
first_seen: generation_4
last_updated: generation_4
evidence: [gen004_exploit_1_sol01, gen004_exploit_1_sol02, gen004_exploit_2_sol01]
related_ideas: [idea_014, idea_007, idea_009, idea_017]
tags: [warm-start, local-minimum, smooth-max, basin, convergence]
---

Published solutions (AlphaEvolve 1319-element at C=1.5032) are already at the floor
of their basin for smooth-max Adam optimization via softplus reparameterization.
Three independent attempts in gen 4 confirm this:

1. **Conservative warm-start** (exploit_1/sol01): 4 seeds, small perturbation
   (sigma=0.01), tight temperature T=0.005→0.0001. Score moved by 3.8e-9 —
   pure floating-point noise. No improvement.

2. **Aggressive warm-start** (exploit_1/sol02): 2 seeds, large perturbation
   (sigma=0.1), high starting T=0.05. Score: 1.5242 — destroyed the solution
   and landed in an inferior basin.

3. **Upsample to N=2000** (exploit_2/sol01): Cubic spline to N=2000, then
   smooth-max Adam. Score: 1.5159 — cubic interpolation destroyed the sparse
   structure, optimizer couldn't recover.

**Critical finding from exploit_1:** Even 100 steps at T=0.005 worsens C from
1.503 to 1.519. The smooth-max approximation error at any useful temperature is
large enough to push the optimizer away from the true minimum. Temperature
annealing starting from T≥0.005 is fundamentally misguided for well-optimized
solutions — the optimizer first walks uphill, then converges back to where it
started (or worse).

**Implication:** Breaking below C=1.503 requires either:
- A fundamentally different optimization approach (projected gradient, coordinate
  descent, LP-based methods — not smooth-max Adam)
- Higher-resolution published arrays (TTT-Discover 30k at C=1.5029) as starting
  points with gentler optimization
