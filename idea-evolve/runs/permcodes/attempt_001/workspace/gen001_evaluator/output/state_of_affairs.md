---
generation: 1
best_score: 262
trajectory: stagnant
last_updated_gen: 1
---

# State of Affairs — Generation 1

## Current Standing

The first evolutionary generation has failed to produce any new solutions. All three solution agents (explore_1/ILS, explore_2/alternative groups, full_1/AGL construction) failed to submit outputs. The best score remains the gen000 greedy baseline at **262** — far below the Smith-Montemanni lower bound of **616**.

The knowledge base now contains 7 ideas and 2 clusters created by the evaluator from the architect's report and literature. These ideas are theoretically grounded but lack empirical validation from this generation.

## What Works

1. **AGL(1,8) construction (idea_002):** The algebraic approach using affine general linear group orbits on GF(8) is the gold standard. Literature and architect analysis confirm it achieves **616+** codewords. The `helpers.agl18.max_clique_code()` function implements this. **Status: Unvalidated this generation — no agent confirmed it works.**

2. **Greedy heuristic (idea_001):** Works but plateaus at 262. Confirmed by gen000 baseline. Not competitive.

3. **fast_compatible_mask helper (idea_005):** Provides 23× speedup over brute force. Should be used by all iterative search methods. **Status: Unvalidated by agent output.**

4. **Partial orbit mixing (idea_007):** Architect's novel insight — orbits need not be used in full. This is the most promising unexplored direction.

## Coverage Map

| Approach | Times Tried | Best Score | Status |
|----------|-------------|------------|--------|
| Greedy nearest-neighbor | 1 | 262 | Established (insufficient) |
| AGL(1,8) construction | 0 | 616 (expected) | Active, unvalidated |
| ILS perturbation | 0 | — | Active, unvalidated |
| Alternative groups | 0 | — | Active, unvalidated |
| Tabu search | 0 | — | Active, unvalidated |
| Partial orbit mixing | 0 | — | Active, unvalidated |

**Coverage gap:** 0 trials for all algebraically-grounded approaches. This generation produced ideas but no empirical validation.

## Dead Ends

1. **Pure greedy search:** Confirmed dead at 262. The search space has deep local optima unreachable by local perturbations alone. Do not invest further in greedy-only approaches without hybridization.

2. **Gen 1 pipeline failure:** All solution agents failed. This is an operational failure, not a scientific result. Must be diagnosed before gen 2.

## Open Questions

1. **Will AGL(1,8) actually produce 616+?** The helper exists but no agent confirmed it works. This is the most urgent question.

2. **Can ILS escape the 616 local maximum?** If we start from an AGL(1,8) code, can controlled destructions find compatible permutations outside the 11-orbit clique?

3. **What other groups (AΓL, PGL, PSL) produce viable orbits?** The Frobenius automorphism on GF(8) gives AΓL(1,8). Other groups might yield different orbit structures.

4. **Can partial orbit mixing exceed 616?** Mixing full orbits from one group with partial orbits from another may access code space regions inaccessible to pure clique search.

5. **Why did gen 1 agents fail?** Pipeline diagnostics needed before gen 2.

## Strategic Recommendation

Gen 2 must prioritize:
1. **Confirm AGL(1,8) helper works** — full_1 should produce a 616+ code to establish baseline
2. **Validate fast_compatible_mask** — ensure iterative search infrastructure is working
3. **Try ILS from AGL baseline** — if 616 is achievable, can we beat it?
4. **Research agent must produce output** — group theory findings need to be captured

The gap from 262 to 616 is enormous. We need to establish that 616 is reachable, then explore the 616–926 space.
