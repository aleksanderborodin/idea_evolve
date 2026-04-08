---
type: idea
id: idea_009
name: "Erdos-Turan Construction"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen001_full_1_sol01, gen002_explore_1_sol01, gen002_explore_1_sol02, gen002_explore_1_sol03, gen002_explore_1_sol04, gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_006, idea_011]
cluster: cluster_001
tags: [algebraic, erdos-turan, baseline-explanation, confirmed-alternative]
---

The Erdos-Turan (1941) construction: for prime p, define S_ET(p) = {2pk + (k^2 mod p) : k = 1, ..., p-1}.
This gives p-1 elements that form a Sidon set. The spacing of 2p prevents carry violations,
making it provably valid for all primes.

**Generation 2 evidence**: explore_1 (Track B, non-Singer) implemented ET(71) and confirmed:
- ET(71) base: 70 elements in {143, ..., 9941}. Valid, zero violations.
- ET(71) + greedy extension: 74 elements.
- ET(71) + greedy + 1-opt: 75 elements. This is a robust local optimum — all random restarts converge to 75.

**Generation 6 evidence**: explore_1 confirmed 75 ceiling with 2-opt, LNS (k=2-15), and 30+ randomized restarts. Hard structural ceiling (pattern_015).

**Ceiling**: ET-based approaches max at ~75 elements (vs algebraic best 105). The construction is
mathematically sound but fundamentally less powerful than Singer/Bose-Chowla.

**Gen 6 consistency fix**: last_confirmed_gen updated to 6 (was stuck at 2). Added gen 6 evidence to supported_by.
