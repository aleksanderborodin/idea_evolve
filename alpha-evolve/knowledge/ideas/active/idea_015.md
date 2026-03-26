---
type: idea
id: idea_015
name: "DCT-domain perturbation for basin escape"
lifecycle: active
confidence: 0.2
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_exploit_1_sol02]
related_ideas: [idea_007, idea_008]
cluster: cluster_001
tags: [perturbation, DCT, basin-escape, frequency-domain]
---

Perturb the raw parameters in DCT (Discrete Cosine Transform) space to explore
neighboring basins while preserving the overall solution structure. Work in
raw-param space (pre-softplus) to avoid non-negativity issues.

**Gen 3 evidence: NEGATIVE.**
- exploit_1/sol02: 10 perturbation configs with n_modes in {10,15,20,25} and
  scale in {0.05-0.18}. ALL 10 seeds converged back to C = 1.5091 (variation
  only 0.000028). A perturbation raising C from 1.509 to 1.83 still converges
  back to the same basin floor.

**Technical notes:**
- Perturbing in f-space (not raw-param space) causes NaN: clipped near-zero
  regions create near-zero integrals leading to division by zero in smooth_c.
- The raw-param space perturbation is numerically clean but ineffective.

**Conclusion:** The ~1.509 basin is remarkably deep. DCT perturbation at any
tested scale cannot escape it. The basin's attractor radius extends to at least
18% perturbation magnitude. This strongly suggests qualitatively different
methods (not just perturbation-based) are needed to find better basins.
