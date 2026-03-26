---
type: cluster
id: cluster_002
name: "Problem representation and initialization"
member_ideas: [idea_002, idea_003, idea_004, idea_006, idea_012, idea_013]
best_score: 1.5090
best_solution: gen003_explore_2_sol01
status: active
last_updated: generation_3
---

This cluster groups ideas related to WHAT is optimized: discretization resolution,
starting function shape, multi-scale strategy, analytical/mathematical insights,
asymmetry, and initialization family.

**Gen 3 update:**
- idea_004 (coarse-to-fine) promoted to ESTABLISHED. Continues to power all best results.
- idea_013 (arcsine init) added: dominates other init families at coarse scale, marginal improvement (1.5090 vs 1.5091).
- Coarse-scale SA FAILED: explore_1 tried N=30, N=40, N=80 SA, all worse than simple coarse-to-fine (1.5148-1.5169 vs 1.5090-1.5091).
- 3-stage pipeline (N=80->200->600) does NOT improve over 2-stage (N=80->600).
- Step function init is a dead end (1.519-1.522).

**Cluster is near-exhausted for finding new basins.** All init families converge
to the same ~1.509 attractor. The AlphaEvolve solution (1.5032, cluster_003)
has fundamentally different structure (sparse, multi-peaked) that suggests our
representation approach may be limited.

**Remaining opportunities:**
- Properly calibrated coarse-SA (20-40% acceptance, cold inner optimizer) — previous
  attempts had 96-100% acceptance due to metro_T miscalibration.
- Arcsine + Gaussian composite init (untested).
