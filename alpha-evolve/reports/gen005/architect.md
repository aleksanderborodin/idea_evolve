# Architect Report — Generation 5

## Data Anomalies

1. **Helpers exist but README says "none yet."** Three experimentator-created helpers (`inv_softplus_safe`, `sensitivity_map`, `interpolate_sparse`) are deployed in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` but the README still says "*(none yet)*". The system recommendations (Priority 4) call for creating these helpers. Either they were created outside the experimentator workflow, or the README update was missed. Either way, they're functional — I verified the code.

2. **State of Affairs is stale (gen 3).** The SoA still says "Priority 1: Warm-start smooth-max Adam from the 1.5032 array" — a strategy that gen 4 definitively closed. The System Critic flagged this as Priority 1 for gen 5. The Consistency Reviewer should run before gen 5 agents see the SoA. However, all gen 5 briefs explicitly state pattern_007 and the dead-end status, so agents won't be misled.

3. **Score improvement is entirely retrieval-driven.** Four generations in, no agent has ever improved a published solution through optimization. Every score improvement below 1.509 came from downloading an existing array. Gen 5's exploit agents are the first real test of whether agent optimization can contribute.

4. **Population summary shows duplicate research_1 entries.** `gen003/research_1/sol01.py` appears 3 times in `all_scores.json` with the same score (1.5032). Minor data quality issue.

## Confidence: Medium-High

The gen 5 plan is well-informed by 4 generations of evidence. Each agent has a clear, non-overlapping directive. The two exploit approaches (projected gradient, coordinate descent) are the most-recommended experiments in the entire system — if they can't improve the TTT-Discover array, that's a definitively valuable negative result.

Confidence is not "High" because:
- We have no timing data for JAX at N=30000. Both exploit agents depend on this being feasible.
- Projected gradient descent on non-convex objectives with projection constraints can be unstable (oscillation at the boundary). The brief mitigates this with very conservative LR, but it's untested.

## What Didn't Fit

- **Warm-start Cell 47 (N=600) with gradient pipeline.** This is Experiment 4 from the suggestions — use the intermediate N=600 array as a warm-start for smooth-max Adam. Worth testing but requires research_1 to extract it first. Deferred to gen 6 if research_1 succeeds.
- **CMA-ES in DCT subspace.** Mentioned in cluster_001 as unexplored. Interesting but lower priority than projected gradient and coordinate descent.
- **LP reimplementation.** Both AlphaEvolve and TTT-Discover used LP-based methods. We could try to implement a simplified LP solver. Very complex, deferred.

## Strategic Risks

1. **Both exploit agents may produce the same null result.** If the TTT-Discover 30k array is at a strict local minimum in every optimization sense (not just smooth-max Adam), both exploit agents fail and we learn nothing beyond "retrieval is the only path." This is possible but the risk is acceptable — the negative result is still valuable.

2. **N=30000 may be computationally infeasible for agent optimization.** JAX JIT compilation at N=30000 may take 30-60s. Combined with slow step times, agents may spend most of their budget on setup. Mitigation: timing benchmarks are mandatory in both briefs.

3. **SA explore may distract from the real frontier.** The SA experiment targets beating 1.5090 (gradient-descent floor), while the exploit agents target 1.5029 (actual best). SA success wouldn't change the leaderboard. But it would demonstrate that coarse-search can find different basins — important for the optimization strategy.

## Open Questions for the System Critic

1. **Should we cap solution array size?** The TTT-Discover array has 30000 elements. If agents start creating 100k-element solutions, evaluation time grows and the population becomes unwieldy. Is there a resolution beyond which returns are negligible?

2. **Are the deployed helpers validated?** `inv_softplus.py`, `sensitivity.py`, and `interpolation.py` exist but weren't created through the experimentator workflow (README says "none yet"). Were they tested? Should the Evaluator verify them?

3. **When should we declare the retrieval strategy exhausted?** We've retrieved AlphaEvolve (1.5032) and TTT-Discover (1.5029). The intermediate arrays are lower priority. At what point do we stop looking for published arrays and commit fully to agent-driven optimization?
