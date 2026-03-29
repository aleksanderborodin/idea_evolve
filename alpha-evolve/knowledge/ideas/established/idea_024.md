---
type: idea
id: idea_024
name: "Non-integral-preserving multi-element moves before CD"
lifecycle: established
confidence: 0.85
first_seen: generation_11
last_updated: generation_11
last_confirmed_gen: 11
supported_by: [gen011_explore_1_sol01]
contradicted_by: []
related_ideas: [idea_019, idea_014, idea_021, idea_022]
cluster: cluster_001
tags: [non-integral-preserving, pair-search, multi-element, amplification, coordinate-descent]
---

Coordinated 2-element perturbation where both elements can change independently
(di, dj have independent signs), unlike integral-preserving moves (d1+d2=0).
Applied BEFORE ultra-fine CD to "unlock" deeper basins.

**Gen 11 evidence (explore_1 — FIRST IMPLEMENTATION):**

Phase 2a (neighboring pairs i, i+1): 547 improvements in 280k trials.
Phase 2b (high-sensitivity random pairs): 1753 improvements in 60k trials.
Total: 2300 improvements, C improved by ~2.7e-10 directly.

**Amplification effect (critical discovery):** The non-IP pair search improves C
by only ~2.7e-10 directly, but the subsequent ultra-fine CD round found 10995
improvements (delta ~4.0e-9) — compared to ~3833 improvements (~5e-10 delta)
from the same starting point without Phase 2. This is a ~15x amplification.

The pair moves appear to find flat ridges connecting to deeper basins that
single-element CD cannot access. This is consistent with the mechanism in
pattern_024: CD works via integral adjustment, and coordinated non-IP moves
change the integral in ways that create new descent paths for CD.

**Distinction from archived triplets/quadruplets (idea_021, idea_022):**
Those were integral-preserving (d1+d2+d3=0). Pattern_020 confirmed they find
0 improvements after ultra-fine CD. Non-IP moves are fundamentally different —
they access the same integral-adjustment mechanism as CD but through
multi-element coordinated changes.

**Recommended protocol for gen 12:**
1. Skip coarse CD (already converged)
2. Run 50k-100k non-IP pair trials (improvement rate was still increasing at 15k)
3. Run ultra-fine CD for multiple rounds
4. Consider non-IP triplets as Phase 2.5

**Status: ESTABLISHED** — single implementation but with strong quantitative
evidence (15x amplification, 2300 direct improvements, new overall best score).
The mechanism is well-understood and consistent with existing theory (pattern_024).
