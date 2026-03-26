---
type: idea
id: idea_013
name: "Arcsine initialization for coarse-to-fine"
lifecycle: active
confidence: 0.55
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_012]
cluster: cluster_002
tags: [initialization, arcsine, coarse-to-fine, asymmetric]
---

Initialize with an arcsine-weighted profile (U-shaped, concentrated at interval
endpoints) on a biased subinterval, then optimize via coarse-to-fine + warm
smooth-max. The arcsine shape f(x) ~ 1/sqrt(x*(0.5-x)) naturally produces
mass concentration at domain boundaries, which is intrinsically asymmetric
when placed on a biased subinterval.

**Gen 3 evidence:**
- explore_2/sol01 (arcsine on [-0.05, 0.22], positive tilt, 6 seeds): C = **1.5090** — marginal improvement over 1.5091 baseline.
- explore_2/sol03 (arcsine, 3-stage N=80->200->600, 12 seeds): C = 1.5091.
- explore_2/sol04 (25-seed funnel: 12 arcsine + 8 Gaussian + 5 comb): C = 1.5092. All top-5 coarse seeds were arcsine-initialized.
- explore_2/sol02 (arcsine subinterval sweep, 10 configs): C = 1.5102.

**Key findings:**
- Arcsine dominates Gaussian, comb, and step inits in head-to-head competition at coarse scale (all top-5 of 25 diverse seeds were arcsine).
- Subinterval placement matters: biased toward one half of domain works best ([-0.05, 0.22] or [-0.22, 0.05]).
- Step function init is a dead end (1.519-1.522 range).
- Comb init is mediocre (worse than arcsine and Gaussian).

**However:** The improvement over Gaussian init is marginal (1.5090 vs 1.5091),
suggesting all init families converge to the same ~1.509 attractor basin. The
arcsine advantage may be in more reliably finding this basin, not finding a
better one.
