---
type: pattern
id: pattern_020
name: "Ultra-fine CD may subsume multi-element perturbation improvements"
lifecycle: active
confidence: 0.5
first_seen: generation_9
last_updated: generation_9
evidence: [gen009_exploit_1_sol01]
related_ideas: [idea_019, idea_021, idea_022]
tags: [coordinate-descent, ultra-fine, triplet, quadruplet, subsumption]
---

After ultra-fine coordinate descent (deltas down to 1e-10 to 1e-11), both triplet
AND quadruplet perturbations find zero improvements. This contrasts with the gen 7-8
pattern where multi-element moves found improvements after standard-delta CD.

**Gen 9 evidence (exploit_1):**
- After 6527 ultra-fine CD improvements: 0 triplet improvements in ~33k trials,
  0 quadruplet improvements in ~11k trials
- Previously (gen 7-8), triplets found 160-2523 improvements and quadruplets 8015
  improvements after standard-delta CD

**Contrast with gen 9 explore_1:**
- Starting from the gen 8 best (which only had standard-delta CD), triplets found
  150 improvements
- This confirms that the starting conditions matter: standard-delta CD leaves room
  for multi-element moves, ultra-fine CD does not

**Possible interpretations:**
1. Ultra-fine single-element moves capture the same landscape features as multi-element
   moves, just with smaller individual steps
2. The multi-element gradient (computed at single argmax) is structurally inadequate
   after ultra-fine CD creates a flatter plateau (13 positions within 1e-12)
3. Both effects are present — ultra-fine CD both captures and disrupts the multi-element
   improvement landscape

**Implication for interleaving protocol (pattern_014):**
The interleaving effect may be bidirectional: multi-element moves unlock CD, AND
ultra-fine CD "consumes" multi-element improvements. The optimal protocol may be to
run standard CD → triplets → quadruplets → THEN ultra-fine CD as a final polish,
rather than ultra-fine CD first.
