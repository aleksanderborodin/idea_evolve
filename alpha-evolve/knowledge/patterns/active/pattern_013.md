---
type: pattern
id: pattern_013
name: "LP refinement fails due to flat autoconvolution plateau at N=30k"
lifecycle: active
confidence: 0.8
first_seen: generation_7
last_updated: generation_7
evidence: [gen007_full_1_sol01, gen007_full_1_sol02, gen007_full_1_sol03, gen006_full_1_sol01]
related_ideas: [idea_020, idea_016, idea_018]
tags: [LP, plateau, autoconvolution, constraint-matrix, scaling]
---

The TTT-Discover 30k array has ~6500 autoconvolution points within 1e-7 * max of the
maximum (gap between 1st and 2nd ≈ 7e-21). This flat plateau fundamentally defeats
LP-based refinement approaches:

1. **Few-constraint LP** (≤138 tight constraints) controls only the included constraints.
   Other plateau points become the new maximum after perturbation, worsening global C.
   (gen 7 full_1, sol02 and sol03)

2. **Full-constraint LP** (all ~6500 near-max points) requires a (6500, 30000) constraint
   matrix = 1.5GB. Same scaling failure as gen 6. (gen 6 full_1)

3. **Downsampled LP** (N=2000): Works locally (reduces C at tight indices by 0.6%) but
   the upsampled direction doesn't transfer to N=30k. The downsampled function has
   C=1.721 (much worse) with fundamentally different structure. (gen 7 full_1, sol01)

**The engineering fix for LP at N=30k was achieved** — vectorized construction now builds
(138, 30000) matrix in <0.01s and LP solves in 8 seconds. The bottleneck is no longer
engineering but the flat plateau structure itself.

**Implication:** LP refinement of the current best may require:
- Iterative LP with tight-index re-identification after each step
- Column generation starting with few variables
- An intermediate resolution (N=5000-10000) where the plateau is smaller
