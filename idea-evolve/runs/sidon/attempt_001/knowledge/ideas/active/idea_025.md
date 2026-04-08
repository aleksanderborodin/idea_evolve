---
id: idea_025
type: idea
name: "Ruzsa-Lindström Construction as SA Seed"
lifecycle: active
confidence: 0.2
first_seen: generation_6
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_001
supported_by: []
contradicted_by: []
related_ideas: [idea_004, idea_006, idea_010, idea_022]
tags: [algebraic, ruzsa, construction, seed, untested]
---

Ruzsa-Lindström construction: for prime p, use primitive root g mod p and define
S = {x*p + g^x mod p : x in {0,...,p-1}}. This produces a p-element Sidon set in
{0,...,p²-1}. For N=10000: p=97 gives 97 elements in {0,...,9408}, p=101 gives ~99
elements in {0,...,10200} (filter to ≤10000).

**Rationale:** This is algebraically distinct from Singer (projective plane) and
Bose-Chowla (affine plane). The gen 5 finding that optimal small-N sets share almost
no elements with Singer suggests that starting from a structurally different seed
might reach different basins of attraction under local search.

**Source:** Research_1 gen 6 (from training data). Not yet implemented or tested.
May correspond to "rl" type in Rokicki-Dogon database.

**Expected outcome:** p=97 gives ~97 elements (below Singer 102 and Bose-Chowla 105).
The value is not in the raw set size but in potentially reaching different local optima
under SA/LNS. If the swap landscape from Ruzsa seeds differs from Bose-Chowla seeds,
this could enable finding 106+ element sets.

**Priority:** Low — the raw construction score is below current best. Only worth testing
if combined with SA/perturbation to explore the non-algebraic solution space.
