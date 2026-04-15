---
generation: 1
best_score: 616
trajectory: climbing
last_updated_gen: 1
---

# State of Affairs — Generation 1 (Rewritten)

## Current Standing

**Best score: 616** codewords for M(8,5), achieved by 7 solutions using the AGL(1,8) orbit clique construction (11 orbits × 56 perms = 616). This matches the Smith & Montemanni (2012) lower bound exactly. Stochastic approaches (ILNS) cap at 290-293 — less than half the gap between the greedy baseline (262) and the algebraic optimum (616). 1 generation completed. Trajectory: **climbing** (262 → 616 in one jump, then plateau).

## What Works

- **AGL(1,8) orbit clique (idea_001, established, 0.95 confidence)**: 6/6 attempts reach 616. Greedy is optimal on this graph. The `agl18_orbits()`, `agl18_compat_graph()`, `agl18_max_clique_code()` helper pipeline is correct and fast (~4s).
- **Multi-seed verification (idea_011, established)**: 500 orderings × all 720 starting vertices all produce exactly 11 orbits. Confirms 616 is the AGL orbit clique maximum.
- **Bucket compatibility pruning (idea_008, established, 0.95)**: 23x speedup over naive pairwise checking. Enables ILNS and individual extension at scale.
- **Individual extension confirms maximality (idea_003)**: 2 attempts found 0 compatible non-orbit permutations. The 616-code is orbit-closed within AGL.
- **Stochastic caps at ~293 (idea_006, established, 0.85)**: ILNS adds ~30 codewords over pure greedy but cannot approach 616 without algebraic structure.

## Current Frontier

The AGL(1,8) construction is exhausted. All reasonable AGL-based approaches converge to 616. The 310-codeword gap to the LP upper bound (926) requires a qualitatively different approach. Priority directions for gen 2:

1. **PGL(2,7) orbit clique search (idea_012, active, 0.6)**: 120 orbits of 336 each vs AGL's 720 orbits of 56. Unexplored. Research identified it; no agent implemented it. If PGL yields >11 orbits, we beat 616.
2. **Compatible-permutation count for 616-code**: The critical empirical question — do any permutations outside the 11 AGL orbits extend the 616-code? Not yet answered. This 5-second experiment determines whether SA/VNS are viable or PGL is mandatory.
3. **Cross-group PGL × AGL clique**: Mixed orbit search could yield larger cliques than either group alone. The 120-vertex PGL graph combined with the 720-vertex AGL graph may contain cross-group cliques exceeding both standalone maxima.
4. **PSL(2,7) exploration**: 240 orbits of 168 each — another completely unexplored group action.

## Coverage Map

| Region | Trials | Best | Status |
|--------|--------|------|--------|
| AGL(1,8) orbit clique alone | 6 | 616 | Exhausted — 11-orbit maximum confirmed |
| Direct greedy on full 40320 space | 1 | 262 | Baseline |
| ILNS + bucket compat | 3 | 293 | Explored, limited — cannot approach 616 without structure |
| Individual permutation extension of AGL code | 2 | 616 (0 extensions) | Confirms orbit-closure |
| Perturbation search on AGL graph | 1 | 616 | No improvement |
| GA crossover | 1 | 0 (INVALID) | Broken operator |
| PGL/PSL orbit clique | 0 | — | **Unexplored — highest priority** |
| Cross-group (PGL × AGL) | 0 | — | Unexplored |
| VNS / Simulated Annealing | 0 | — | Unexplored |

## Dead Ends

1. **Extending AGL 616-code with individual permutations**: Dead end. The code is orbit-closed — 0 compatible non-orbit permutations exist.
2. **Perturbation/ILNS on full 40320-vertex space**: Caps at ~293. Structure-free search cannot replicate the orbit decomposition's lossless search space reduction. The 70-bucket structure is necessary but not sufficient for the search.
3. **GA crossover (union+prune)**: Broken operator. Crossover of two compatible codes loses too many codewords due to pairwise incompatibility. Would need orbit-level crossover to work.

## Open Questions

1. **What is the maximum clique size in the PGL(2,7) orbit graph?** If >11 orbits, we beat 616. This is the single most important question.
2. **How many permutations are compatible with the 616-code but outside the 11 AGL orbits?** Never measured. If count > 0, SA/VNS are viable paths forward. If count = 0, PGL is the only path.
3. **Can cross-group PGL × AGL cliques exceed both groups' standalone maxima?** Unexplored mixed construction combining 120 PGL orbit reps with 720 AGL orbit reps.
4. **Are there larger cliques in PSL(2,7) orbits (240 orbits of 168 each)?** Also unexplored.
5. **LP upper bound of 926 — is it tight?** The gap is 53% of the upper bound. If we find a construction beating 616, we should verify whether it approaches 926 or whether the LP bound is loose.
6. **Is the GA crossover operator fixable?** Orbit-level crossover might work; current union+prune is destructive.

## Strategic Assessment

Gen 1 established that AGL(1,8) is at its limit (616) and structure-free search (ILNS) is fundamentally limited (~293). The 310-codeword gap to 926 is not a marginal improvement situation — it requires algebraic innovation. PGL(2,7) is the most promising unexplored direction. The research-to-execution pipeline must close: research_1 identified PGL but no agent implemented it. This is the primary lesson of gen 1.

**For gen 2:** The architect must assign PGL(2,7) as a required, named task — not optional context. The compatible-permutation count should be run by an experimentator as a trivial 5-second baseline measurement. VNS and SA are secondary experiments.
