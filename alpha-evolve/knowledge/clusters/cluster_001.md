---
type: cluster
id: cluster_001
name: "Optimization algorithms and techniques"
member_ideas: [idea_001, idea_005, idea_007, idea_008, idea_009, idea_010, idea_011]
best_score: 1.5091
best_solution: gen002_explore_1_sol03
status: active
last_updated: generation_2
---

This cluster groups all ideas related to HOW the optimization is performed:
which optimizer (Adam, Lion, L-BFGS), what objective modification (smooth-max),
what reparameterization (softplus), and what search strategy (multi-seed restart).

The dominant combination is smooth-max (idea_007) + multi-seed (idea_008) + Adam
(idea_001) + coarse-to-fine (idea_004, from cluster_002). The new best of 1.5091
was achieved via coarse-to-fine + warm smooth-max + 12 restarts (gen002_explore_1_sol03).

**Gen 2 findings within this cluster:**
- L-BFGS (idea_010) confirmed ineffective after smooth-max convergence. Confidence lowered.
- More restarts beyond 8 show hard diminishing returns (16→1.5107, 20→1.5108).
- Extended temperature phases (T=0.0001) provide negligible benefit.
- SA at N=600 (fine grid) is a dead end — basin is too sticky.

**Unexplored within this cluster:**
- Coarse-scale SA (N=30-80) before upsampling — the actual Boyer et al. approach
- Lion warmup + coarse-to-fine + smooth-max
- Warm-start from existing 1.5091 solution with tighter annealing
