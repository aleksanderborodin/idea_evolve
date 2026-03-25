---
type: cluster
id: cluster_002
name: "Problem representation and initialization"
member_ideas: [idea_002, idea_003, idea_004, idea_006, idea_012]
best_score: 1.5091
best_solution: gen002_explore_1_sol03
status: active
last_updated: generation_2
---

This cluster groups ideas related to WHAT is optimized: the discretization
resolution (idea_002), the starting function shape (idea_003), the multi-scale
strategy (idea_004), analytical/mathematical insights (idea_006), and the
critical asymmetry requirement (idea_012).

**Gen 2 breakthrough:** idea_004 (coarse-to-fine) combined with smooth-max
(idea_007 from cluster_001) achieved C=1.5091 — new overall best. The warm
fine stage (T=0.05 restart after upsampling) was the critical missing ingredient
that gen 1 lacked.

idea_012 (asymmetry) is the strongest member — a mathematical fact that
constrains the search space. idea_002 (higher N) remains disputed. idea_004
is now active (promoted from disputed).

**Unexplored within this cluster:**
- Arcsine distribution initialization (from research findings)
- Fourier-basis parameterization + smooth-max (Fourier alone was 1.5294)
- Non-Gaussian coarse inits (comb, step, arcsine) with coarse-to-fine
- AlphaEvolve's 600-interval array as warm-start initialization
