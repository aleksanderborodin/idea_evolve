# Architect Report — Generation 4

## Data Anomalies

- **Total score monoculture persists.** All competitive solutions are still Singer q=101 with score 102. The population has zero diversity at the frontier. The 69-element Fibonacci solution is the only non-trivial non-Singer result, but it's 33 elements behind.

- **Three consecutive research failures.** No literature search has ever completed successfully. Gen 1 research found Singer (a breakthrough), but gen 2 and gen 3 research both terminated before writing findings. This is the longest-standing data gap. The gen 4 research brief enforces incremental output, but the pattern of failure is concerning.

- **Stale fact files still present.** fact_002 (wrong upper bound) and fact_004 (wrong scoring rules) remain in `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/`. The consistency reviewer flagged them in gen 3 but they were not deleted. All gen 4 briefs include warnings, but agents that independently browse `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/` could still be misled.

- **Missing timing data for gen 2-3 work agents.** The timing.json only has gen001 research_1 (698s) and gen003 evaluator/critic/reviewer times. No timing for gen 2-3 work agents (explore, exploit). This makes timeout calibration approximate.

- **Helpers deployment confirmed.** Unlike the uncertainty flagged in gen 3 reports, `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/` now contains: core.py, singer.py, search.py, optimal_shift.py. Gen 4 agents can use these.

## Confidence: Medium-High

Higher than gen 3 because:
- The ILP direction now has a correct formulation specified (from system recommendations).
- Track B directions (Ruzsa, Bose-Chowla, min-blocking greedy) are genuinely orthogonal.
- Research brief is restructured for incremental output.
- Experimentator addresses two quick-closure questions.

Lower confidence on:
- Whether ILP is computationally feasible at N=10000 (memory/time).
- Whether any Track B approach reaches 80+.

## What Didn't Fit

- **Paley difference set exploration.** Paley sets exist for v = q ≡ 1 (mod 4) prime. For q near 10001, this could give alternative algebraic constructions. Deferred to explore_2's discretion.

- **Prime power Singer sets.** GF(q³) for q = p^k (not prime) gives intermediate v values. Could allow better truncation alignment. Unexplored, low priority.

- **Exhaustive Fibonacci parameter search (100K+ pairs).** Could push the 69 ceiling to 70-71 but not competitive. Not worth agent time.

- **Dedicated fact file cleanup agent.** The stale facts need manual deletion. Briefs include warnings as mitigation.

## Strategic Risks

1. **ILP memory explosion at N=10000.** The difference-indicator formulation creates O(N²) auxiliary variables. For N=10000, that's ~50M variables. CP-SAT may run out of memory before finding any feasible solution. If this happens, the ILP direction may need a decomposition approach (solve sub-problems, combine) or a commercial solver.

2. **Bose-Chowla turns out to be equivalent to Singer.** For prime p, the Bose-Chowla construction S = {i*p + (g^i mod p)} produces a perfect difference set in Z_{p²+p+1}. This is algebraically the same family as Singer. The explore_2 agent might waste time rediscovering this.

3. **Min-blocking greedy is equivalent to standard greedy.** If the blocking score doesn't differentiate candidates meaningfully (e.g., all candidates have similar blocking scores), the algorithm degenerates to standard greedy (ceiling 66-69). The approach may not have real potential.

4. **Research agent finds that 102 IS the published best.** This would mean our pipeline has already matched the state of the art and the remaining gap to 109 is an open mathematical problem. The implication: further optimization may require mathematical breakthroughs beyond what evolutionary search can achieve.

## Open Questions for the System Critic

1. Should cluster_003 (Hybrid Approaches, marked exhausted) be formally retired and archived? It still appears in the knowledge dump and may confuse agents.
2. If ILP proves infeasible at N=10000, what is the next best computational approach? Is there a decomposition strategy that could work?
3. The 109 target — is this achievable computationally, or is it a theoretical bound that may require novel mathematics? After 3 generations of exhaustive Singer exploration, 7 more elements feels more like a research problem than an optimization problem.
4. Should we allocate an entire generation to pure research (3-4 research agents with different search strategies) if gen 4's research agent also fails?
