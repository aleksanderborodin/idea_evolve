---
type: idea
id: idea_009
name: "Erdos-Turan Construction"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_full_1_sol01, gen002_explore_1_sol01, gen002_explore_1_sol02, gen002_explore_1_sol03, gen002_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_006]
cluster: cluster_001
tags: [algebraic, erdos-turan, baseline-explanation, confirmed-alternative]
---

The Erdos-Turan (1941) construction: for prime p, define S_ET(p) = {2pk + (k² mod p) : k = 1, ..., p-1}.
This gives p-1 elements that form a Sidon set. The spacing of 2p prevents carry violations,
making it provably valid for all primes.

**Generation 2 evidence**: explore_1 (Track B, non-Singer) implemented ET(71) and confirmed:
- ET(71) base: 70 elements in {143, ..., 9941}. Valid, zero violations.
- ET(71) + greedy extension: 74 elements.
- ET(71) + greedy + 1-opt: 75 elements. This is a robust local optimum — all random restarts converge to 75.

**Important correction**: The Ruzsa construction {a*p + a²%p} and Bose-Chowla {i*p + g^i%p}
do NOT work for large primes due to carry violations. p=97: 312 violations (Ruzsa), 248 violations
(Bose-Chowla). The Erdos-Turan formula with 2p spacing is the correct version. This was confirmed
by explore_1 after the brief incorrectly suggested Ruzsa/Bose-Chowla as options.

**Ceiling**: ET-based approaches max at ~75 elements (vs Singer's 102). The construction is
mathematically sound but fundamentally less powerful than Singer difference sets.
