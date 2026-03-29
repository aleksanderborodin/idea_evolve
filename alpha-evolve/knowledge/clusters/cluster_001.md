---
type: cluster
id: cluster_001
name: "Optimization algorithms and techniques"
member_ideas: [idea_001, idea_005, idea_007, idea_008, idea_009, idea_010, idea_011, idea_015, idea_017, idea_019, idea_021, idea_022, idea_023, idea_024]
best_score: 1.5028628677925082
best_solution: gen011_explore_1_sol01
status: active
last_updated: generation_11
---

This cluster groups all ideas related to HOW the optimization is performed:
which optimizer, what objective modification, what reparameterization, and what
search strategy.

**Gen 11 update:**

**Active members (3):**
- idea_019 (coordinate descent) — ESTABLISHED 0.95. Primary productive technique.
- idea_007 (smooth-max) — ESTABLISHED 0.95. Essential for GD from random init only.
- idea_024 (non-IP multi-element moves) — **NEW, ESTABLISHED 0.85.** Two-phase protocol
  with CD achieves 15x amplification (pattern_025). Produced gen 11's NEW OVERALL BEST.

**Archived members (7):** idea_001 (GD/JAX), idea_005 (regularization), idea_008
(multi-seed), idea_009 (softplus), idea_011 (Lion), idea_021 (triplets), idea_022
(quadruplets).

**Debunked members (4):** idea_010 (L-BFGS), idea_015 (DCT perturbation), idea_017
(projected gradient), idea_023 (minimax LP).

**Key development (gen 11):** Non-integral-preserving multi-element moves (idea_024)
break the monotonic-CD-only paradigm. The amplification effect suggests CD alone was
trapped in shallow basins — the pair moves provide "basin hopping" that CD cannot do alone.
This is the first genuinely new productive technique since ultra-fine CD was established
in gen 5.

**Best score updated: 1.5028628677925082** (gen011_explore_1_sol01).

**Engineering advances (gen 11):**
- Focused delta grid (1e-14 to 1e-11) confirmed 1.83x faster than broad (pattern_026)
- Sub-round FFT resync needed at 500-mod intervals (pattern_027)
- topk_screened_cd shared helper built by experimentator_1
