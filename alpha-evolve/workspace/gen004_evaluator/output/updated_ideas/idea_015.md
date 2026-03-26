---
type: idea
id: idea_015
name: "DCT-domain perturbation for basin escape"
lifecycle: debunked
confidence: 0.1
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_exploit_1_sol02, gen004_exploit_1_sol02]
related_ideas: [idea_007, idea_008]
cluster: cluster_001
tags: [perturbation, DCT, basin-escape, frequency-domain, debunked]
---

Perturb the raw parameters in DCT (Discrete Cosine Transform) space to explore
neighboring basins while preserving the overall solution structure.

**DEBUNKED after gen 3-4 evidence.**

**Gen 3 evidence:**
- exploit_1/sol02: 10 perturbation configs with n_modes in {10,15,20,25} and
  scale in {0.05-0.18}. ALL 10 seeds converged back to C = 1.5091.

**Gen 4 evidence (indirect):**
- exploit_1/sol02: Aggressive random perturbation (sigma=0.1 in raw_params space)
  of the 1.5032 solution: C = 1.524. Large perturbations destroy the solution
  and land in inferior basins rather than escaping to better ones.

**Conclusion:** Perturbation-based basin escape is fundamentally ineffective for
this problem, regardless of perturbation domain (DCT, raw_params, f-space). The
basins reached by our methods are local minima that can only be escaped by
qualitatively different optimization methods (LP-based, coordinate descent, etc.),
not by perturbation + re-optimization.
