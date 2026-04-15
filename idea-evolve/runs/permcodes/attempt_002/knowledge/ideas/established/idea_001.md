---
type: idea
id: idea_001
name: "AGL(1,8) Orbit Clique Search"
lifecycle: established
confidence: 0.95
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_full_1_sol01, gen001_full_1_sol02, gen001_full_1_sol03]
contradicted_by: []
related_ideas: [idea_002, idea_003, idea_011]
cluster: cluster_001
tags: [algebraic, group-theory, AGL, orbit-clique, M(8,5)]
---

# AGL(1,8) Orbit Clique Search

## What It Is

Partition the symmetric group S_8 into the 720 cosets (orbits) of the affine linear group AGL(1,8) acting on 8 points. Each orbit contains exactly 56 permutations. Build a compatibility graph between orbits (an orbit pair is compatible if all 56×56 = 3136 pairwise Hamming distances ≥ 5). Find the maximum clique in this 720-vertex graph. Each orbit in the clique contributes 56 codewords, yielding a code of size 11×56 = 616.

## How It Works

1. Generate all 720 AGL(1,8) orbits via left group action on S_8
2. Build a 720×720 compatibility graph (degree = 138 for d=5)
3. Run greedy max-clique search from multiple starting vertices
4. Map selected orbits back to their 56 constituent permutations each

## Evidence

- **6/6 solutions** using AGL orbit clique achieve exactly 616 codewords
- Multi-seed search (500 orderings) confirms 11 orbits is the unique maximum
- All 720 starting vertices produce the same 11-orbit clique (extremely regular structure)
- The result matches Smith & Montemanni (2012) lower bound exactly

## Current Performance

Best score: **616**. This matches the known lower bound for M(8,5). The gap to the LP upper bound of 926 is 310 codewords (53% of the upper bound).

## Key Finding: Orbit Maximality

The 616-code appears to be "orbit-maximal": no permutation outside the 11 selected AGL orbits is compatible with all 616 codewords. This was confirmed by two independent extension attempts (explore_1/sol02 and full_1/sol02), both finding zero compatible non-orbit permutations.

## When It Helps

This is currently the only approach that achieves the known optimum. Any solution attempting to beat 616 must either (a) find a larger orbit clique under a different group action, or (b) find individual permutations that extend beyond what any single group orbit provides.

## Limitations

- Only searches the AGL(1,8) orbit structure; may miss cliques in other group actions
- The orbit clique of 616 is closed under AGL compatibility — no direct extension possible
- The 616-to-926 gap suggests significant improvement requires fundamentally different construction
