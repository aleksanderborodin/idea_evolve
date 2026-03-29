---
type: pattern
id: pattern_014
name: "Higher-order perturbations unlock lower-order improvement directions"
lifecycle: active
confidence: 0.75
first_seen: generation_8
last_updated: generation_8
evidence: [gen008_explore_1_sol01, gen008_exploit_1_sol01]
related_ideas: [idea_022, idea_021, idea_019]
tags: [interleaving, unlocking, multi-element, perturbation, landscape]
---

When a solution is optimal with respect to k-element perturbations, applying
(k+1)-element perturbations reshapes the autoconvolution landscape and creates
new k-element improvement directions. This "unlocking" effect has been observed
at two transitions:

**Transition 1: Coordinate descent → Triplets (gen 7-8)**
- Gen 7 exploit_1: coordinate descent converged (16 improvements in round 6)
- Gen 7 explore_1: 160 triplet improvements on the coord-descent-optimal array
- Gen 8 exploit_1: 2008 NEW coord descent improvements on the triplet-modified
  array — triplets unlocked single-element directions

**Transition 2: Triplets → Quadruplets (gen 8)**
- Gen 7 explore_1: second triplet pass found 0 improvements in 20k trials
- Gen 8 explore_1: 8015 quadruplet improvements on the triplet-exhausted array
- Gen 8 explore_1: triplet follow-up found 2523 improvements after quadruplets —
  quadruplets unlocked new triplet directions

**Implication:** The correct protocol is iterative interleaving:
coord descent → triplets → quadruplets → (possibly quintuples) → back to
coord descent → ... repeating until ALL methods find 0 in the same cycle.
Each layer unlocks the one below it.

**Quantitative pattern:** The improvement count per cycle appears to grow with
perturbation order (116 coord → 160 triplet → 8015 quadruplet), but the
absolute C improvement per cycle remains O(1e-10). The landscape is extremely
flat but has rich higher-dimensional structure.
