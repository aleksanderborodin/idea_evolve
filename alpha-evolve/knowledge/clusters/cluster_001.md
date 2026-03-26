---
type: cluster
id: cluster_001
name: "Optimization algorithms and techniques"
member_ideas: [idea_001, idea_005, idea_007, idea_008, idea_009, idea_010, idea_011, idea_015]
best_score: 1.5090
best_solution: gen003_explore_2_sol01
status: active
last_updated: generation_3
---

This cluster groups all ideas related to HOW the optimization is performed:
which optimizer (Adam, Lion, L-BFGS), what objective modification (smooth-max),
what reparameterization (softplus), and what search strategy (multi-seed restart,
DCT perturbation).

**Gen 3 update:**
- idea_010 (L-BFGS) DEBUNKED: zero effect in all gen 3 tests. Confidence 0.1.
- idea_015 (DCT perturbation) added: 10 perturbation configs all return to same 1.509 basin. Shows basin depth but not useful for escaping.
- Best score marginally improved: 1.5091 -> 1.5090 via arcsine init (explore_2/sol01).
- Ultra-low temperature polish confirmed useless (0.000025 improvement).

**The cluster is approaching exhaustion for our gradient pipeline.** All tested
optimization variations converge to the ~1.509 basin. The only path to C < 1.505
within this cluster would be a fundamentally different optimizer (LP-guided, etc.).

**Unexplored within this cluster:**
- Warm-start smooth-max from published 1.5032 solution (idea_014, cluster_003)
- Lion warmup + coarse-to-fine (still untested)
- Coordinate descent on best solution
