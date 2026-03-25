---
type: idea
id: idea_012
name: "Asymmetry exploitation"
lifecycle: established
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_2_sol09, gen001_explore_1_sol05, gen001_full_1_sol03]
contradicted_by: []
related_ideas: [idea_003, idea_006]
cluster: cluster_002
tags: [asymmetry, symmetry-breaking, mathematical]
---

The optimal function for this problem is strongly asymmetric. Symmetric functions
satisfy C >= 2 (proven via Cauchy-Schwarz), so any competitive solution must
break symmetry.

**Evidence:**
- explore_2 discovered and proved that C >= 2 for all symmetric functions on
  [-1/4, 1/4]. This is a hard mathematical barrier.
- The baseline's flat+noise initialization breaks symmetry via noise — this is
  why it converges to C ~ 1.518 rather than C >= 2.
- Gaussian initialization (centered, symmetric) gave C = 1.5207 (worse), confirming
  that symmetric starts are suboptimal.
- Hann window (symmetric): C = 3.0.

**Implication:** Initializations should be deliberately asymmetric or at minimum
include sufficient noise to break symmetry quickly. Symmetric initializations
waste optimization steps breaking symmetry before making real progress.
However, explore_2 noted that the symmetric box init (baseline) breaks symmetry
efficiently via the gradient — the steepest descent direction is along asymmetry.
