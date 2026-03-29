---
type: pattern
id: pattern_024
name: "CD improves C through integral adjustment, not integral-preserving peak reduction"
lifecycle: active
confidence: 0.7
first_seen: generation_10
last_updated: generation_10
evidence: [gen010_explore_1_sol01, gen010_explore_2_sol01]
related_ideas: [idea_019, idea_021, idea_022, idea_023]
tags: [coordinate-descent, mechanism, integral, minimax, optimization-theory]
---

Coordinate descent (non-integral-preserving) and multi-element perturbation
(integral-preserving) improve C = max_ac / integral² through fundamentally
different mechanisms:

- **CD:** Changes individual f[i] values, which changes both max_ac and integral.
  The improvement comes primarily from adjusting the integral:mass ratio, not
  from reducing max_ac while keeping integral fixed.

- **Multi-element (triplets/quadruplets/minimax):** Constrained to d1+...+dk=0,
  so integral is fixed. Must reduce max_ac directly.

**Gen 10 evidence:**
- explore_1 implemented full minimax LP (68k trials, K=28 plateau positions):
  0 improvements. The solution is minimax-optimal for integral-preserving moves.
- explore_1 then ran CD (non-integral-preserving): 1281 improvements, -5.70e-11.
- explore_2: 200k triplet + 50k quadruplet trials: 0 improvements. Then 8003
  CD improvements, -1.06e-10.

**Interpretation:** The autoconvolution plateau has K=28 near-max positions. With
this many constraints, no integral-preserving direction can reduce the max across
all of them (the origin is in the convex hull of gradient vectors). CD escapes
this limitation by being free to change the integral.

**Open question:** Would non-integral-preserving multi-element moves (allowing
d1+...+dk ≠ 0) find improvements beyond what single-element CD finds? This is
untested and represents the last unexplored multi-element avenue.
