---
type: idea
id: idea_020
name: "LP-based refinement of existing solutions"
lifecycle: debunked
confidence: 0.05
first_seen: generation_5
last_updated: generation_9
last_confirmed_gen: 5
supported_by: []
contradicted_by: [gen006_full_1_sol01, gen007_full_1_sol01, gen007_full_1_sol02, gen007_full_1_sol03, gen009_explore_2_sol01, gen009_explore_2_sol02]
related_ideas: [idea_016, idea_018, idea_019]
cluster: cluster_003
tags: [LP, linear-programming, refinement, constraint-based, debunked]
---

Implement LP-based descent directions for refining existing solutions. The formulation
linearizes the autoconvolution: minimize max(f★f + 2·f★δf) subject to near-tight constraints.

**DEBUNKED — Gen 9 provides definitive closure.**

**Gen 9 evidence (explore_2) — DEFINITIVE:**
- N=5000 near-optimal (C≈1.517) has **2400-2800 tight constraints** at epsilon_rel=1e-5
  (24-28% of autoconv points). This is comparable to N=30k near-optimal (~30.5%).
- Few-constraint LP (13-59 constraints) at N=5000: improvement of -5.85e-12
  (floating point noise, not genuine improvement).
- The plateau structure is **resolution-independent** near optimality. The same
  percentage of autoconv points are near-maximal regardless of N.

**Previous evidence (gen 6-8):**
- N=30k: OOM building constraint matrix (gen 6), 6500 near-max plateau points
  defeat few-constraint LP (gen 7, 3 attempts), downsampling destroys structure (gen 8).

**Why LP fails fundamentally:**
The autoconvolution plateau contains thousands of near-maximal points at any resolution
near optimality. LP with few constraints (the only tractable number) cannot control the
unselected plateau points, which become the new maximum. Full LP is infeasible due to
matrix size (~N² elements). This is not an engineering limitation — it is a mathematical
property of the problem near optimal solutions.

**Recommendation: ARCHIVE.** This idea has been thoroughly tested across 5 generations
(gen 5-9), at multiple resolutions (N=2000, N=5000, N=30000), with multiple constraint
counts (1, 13, 59, 138). All results negative. No remaining path to viability.
Confidence lowered to 0.05.
