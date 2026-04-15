---
type: idea
id: idea_012
name: "PGL(2,7) / PSL(2,7) Orbit Clique Search"
lifecycle: active
confidence: 0.6
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: null
supported_by: []
contradicted_by: []
related_ideas: [idea_001, idea_002, idea_003]
cluster: cluster_001
tags: [algebraic, group-theory, PGL, PSL, orbit-clique, unexplored]
---

# PGL(2,7) / PSL(2,7) Orbit Clique Search

## What It Is

Use the projective linear groups PGL(2,7) or PSL(2,7) as alternative group actions to partition S_8. These groups have different structures than AGL(1,8):

- **PGL(2,7)**: 336 elements → 120 orbits of 336 perms each
- **PSL(2,7)**: 168 elements → 240 orbits of 168 perms each (PSL(2,7) ≅ GL(3,2))

The different orbit sizes and group structure may yield larger maximum cliques than the AGL(1,8) orbit graph.

## Why It Matters for M(8,5)

Smith & Montemanni achieved 616 using AGL(1,8). The LP upper bound is 926. The 310-codeword gap suggests AGL(1,8) is not near-optimal. Different group actions may close this gap.

## How It Would Work

1. Generate PGL(2,7) or PSL(2,7) group elements as permutations of {0,...,7}
2. Partition S_8 into orbits under the group action
3. Build compatibility graph between orbits
4. Run max-clique search on the orbit graph (120 or 240 vertices)

## Evidence

- **Not yet tried** in any generation 1 solution
- Research findings (research_1) confirm this is an unexplored direction
- PGL(2,7) is sharply 2-transitive like AGL(1,8) — should give similar orbit properties
- The smaller number of orbits (120 vs 720) means a faster clique search

## Current Status

**Unexplored** — no solutions have implemented this. This is the single most promising direction for beating 616.

## Key Implementation Challenge

Generating the explicit PGL(2,7) or PSL(2,7) elements as permutations of {0,...,7} requires computing Möbius transformations over GF(7)∪{∞}. The abstract group structure is known but the embedding into S_8 must be derived.

## Expected Performance

Unknown. If PGL(2,7) yields a larger clique than AGL(1,8), could beat 616. The orbit size (336 vs 56) means each orbit contributes more codewords — even a 9-orbit PGL clique would give 9×336 = 3024 codewords (exceeds upper bound, so some orbits must be incompatible). The actual maximum is unknown.

## Cluster Note

This idea should be in a new cluster "Alternative Group Actions" (cluster_004, not yet created). Temporarily assigned to cluster_001 for backward compatibility.
