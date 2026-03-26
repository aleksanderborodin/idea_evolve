---
type: cluster
id: cluster_001
name: "Optimization algorithms and techniques"
member_ideas: [idea_001, idea_005, idea_007, idea_008, idea_009, idea_010, idea_011, idea_015, idea_017]
best_score: 1.5090
best_solution: gen003_explore_2_sol01
status: active
last_updated: generation_4
---

This cluster groups all ideas related to HOW the optimization is performed:
which optimizer (Adam, Lion, L-BFGS), what objective modification (smooth-max),
what reparameterization (softplus), and what search strategy (multi-seed restart,
DCT perturbation, projected gradient).

**Gen 4 update:**
- idea_015 (DCT perturbation) DEBUNKED: combined with gen 3 evidence, perturbation-
  based basin escape is confirmed ineffective for this problem.
- idea_009 (softplus) now has known LIMITATIONS for warm-start optimization of
  sparse published solutions (dead zones at near-zero elements).
- idea_017 (projected gradient descent) ADDED: optimize f directly with non-negativity
  projection. Proposed by exploit_1 to address softplus limitations. Not yet tested.
- Best score unchanged at 1.5090 (gradient-descent floor).

**Status: approaching exhaustion for gradient descent from random init.** All tested
optimization variations converge to the ~1.509 basin. The only remaining opportunity
within this cluster is idea_017 (projected gradient on published solutions).

**Unexplored:**
- idea_017: projected gradient descent on f directly (no softplus)
- Coordinate descent on best solution
- CMA-ES on DCT subspace
