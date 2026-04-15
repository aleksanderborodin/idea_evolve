# Architect Report — Generation 1

## Confidence Level: HIGH

Rationale: Generation 1 is a cold start with clear, well-understood moves. The AGL(1,8) construction is deterministic and fully implemented in helpers. All four agents have concrete, orthogonal tasks. The main uncertainty is whether ILS or alternative groups can beat 616, not whether we can reach 616.

## Data Anomalies

**Baseline score of 262 is expected but revealing.** The greedy baseline with 20 random restarts achieves only 262 out of a possible 616+. This confirms that greedy is far from optimal and motivates algebraic approaches. No anomalies — this is consistent with known results.

**Score progression only has gen000.** No previous architect reasoning, no cluster files, no fact files, no consistency reviews, no system recommendations, no experiment suggestions, no interventions. This is exactly expected for a cold start.

**Baseline evaluation time: 22 seconds.** This is notable. The greedy algorithm with 20 restarts over 40320 permutations takes 22s. This suggests that naive iteration over all permutations is expensive. Future agents should use `fast_compatible_mask` from helpers/compat.py which is 23x faster.

## Confidence per Decision

**full_1 assignment:** HIGH confidence. `agl18_max_clique_code()` is a validated, documented function. Expected output: 616. Risk: near zero.

**explore_1 (ILS):** MEDIUM confidence. The approach is sound and the tools are in place (fast_compatible_mask). Whether ILS can actually escape the AGL(1,8) local maximum is unknown. There's a real possibility the 616-code is tight under ILS (all destructions reconstruct to 616). Either outcome is informative.

**explore_2 (alternative groups):** MEDIUM-LOW confidence. AΓL(1,8) is mathematically well-defined but implementing the Frobenius automorphism in GF(8) is subtle. The brief provides the squaring map explicitly. The direct clique search on 40320 vertices is computationally ambitious — beam search with 40K candidates is feasible but might be slow. The coset construction approach is the riskiest (least defined).

**research_1:** HIGH confidence. Research agents produce text, not code. The main risk is factual errors about group orders or construction details, which can be verified in generation 2.

## What Didn't Fit

**Tabu search for max clique:** A dedicated tabu search on the full permutation compatibility graph G(8,5) (40320 vertices) would be a serious tool for pushing above 616. I didn't assign it because: (1) the fast_compatible_mask helper makes neighborhood evaluation feasible, but I didn't want to overload explore_1's brief, and (2) I'd rather see ILS results first before prescribing specific SA/TS parameters. Generation 2 should have a dedicated tabu search agent if ILS shows signs of life.

**Integer programming / column generation:** The problem can be formulated as maximum weight independent set (or max clique) in an LP. Column generation could potentially prove optimality or find bounds. This requires specialized IP solver setup. Deprioritized for gen 1 — too much infrastructure to set up without knowing if simpler methods already work.

**Full enumeration of degree-8 transitive groups:** GAP/Magma could enumerate all transitive subgroups of S₈ and their orbit structures. This would systematically find the best algebraic group rather than guessing. Not feasible without a CAS, but research_1 should enumerate the candidates theoretically.

## Strategic Risks

**Risk: 616 is locally maximum under all reasonable perturbations.** If both ILS (explore_1) and alternative groups (explore_2) return codes ≤ 616, generation 2 faces a real challenge. We'd need to try more aggressive search: larger destructions, longer SA runs, or fundamentally different construction approaches. The research agent's findings would be critical for planning generation 2 in this scenario.

**Risk: The 22s evaluation time will slow iterative agents.** Each call to evaluate.py takes ~22s for the baseline solution. Agents running ILS iterations will want to call evaluate.py on each improved solution, not inside the optimization loop. They should track scores internally and only call evaluate.py at the end for final solutions. The brief addresses this, but agents might get confused.

**Risk: AΓL(1,8) clique size might also be 11 (= 616).** If AΓL orbits are also "hard" with a 11-orbit max clique, we'd get 11×168 = 1848? No — wait. 11 orbits × 168 = 1848, but the code size must be ≤ 926. Let me reconsider: for AΓL(1,8), an orbit has 168 elements, but not all of them need to be pairwise compatible. The compatibility graph on 240 orbits (not individual permutations) determines the clique. A k-orbit clique in AΓL gives k×168 permutations, but only if each orbit is entirely compatible. Actually the clique might only be 3-4 orbits (giving 504-672 codewords). The math here is uncertain — this is exactly why explore_2 should try it empirically.

## Open Questions for the System Critic

1. **Is the 616-code the unique maximum AGL(1,8) code, or are there multiple non-isomorphic 11-orbit cliques?** If multiple, we might try ILS between them to explore the space between.

2. **What is the computational complexity of max-clique on G(8,5)?** The graph has 40320 vertices. Exact solvers (branch-and-bound) are likely infeasible, but good heuristics (tabu search, simulated annealing) may find solutions in minutes. This depends on the graph's density and structure.

3. **Should we invest in a connection to a max-clique solver?** If we could call an external clique solver (e.g., compiled C++ code like MaxClique or Cliquer), we might get much better solutions. Worth exploring as an experimentator task in generation 2.

4. **Does the problem's algebraic structure allow partial orbits to be mixed?** AGL(1,8) codes use complete orbits (56 permutations each). Could we take 10 full orbits + partial permutations from an 11th orbit to exceed 616? Or must codes be closed under group action to be valid? (Answer: no — validity just requires pairwise distance ≥ 5, not group closure. Partial orbits are fully allowed. This opens the door for ILS.)
