# Manifest Reasoning — Generation 2

## Situation Assessment

Gen 1 was a breakthrough: Singer q=97 construction jumped the score from 66 (greedy baseline) to 99 (Singer + perturbation). Three independent agents confirmed the 99-element ceiling for Singer q=97 perturbation. The gap to target (100) is just 1 element, but the 99→100 barrier held through ~280s of combined perturbation search across 3 solutions.

**Score trajectory**: 66 → 99 (+33). Rapidly improving, but we are now at a critical barrier.

**Diversity**: All top-3 solutions are Singer q=97 + perturbation variants (same cluster, same approach). Low diversity at the top. Search-based methods are confirmed dead ends (ceiling 68).

**Key untested ideas**: Singer q=101 truncation (idea_008, highest priority), SA from algebraic seed (idea_010), Ruzsa/Bose-Chowla constructions (unexplored).

## Agent Mix Rationale

### Track A — Directed exploitation (3 agents)

**exploit_1 (opus, 1800s)**: Singer q=101 cyclic shift search. This is THE critical experiment — the single most likely path to hitting target=100. The math is clear: 102 elements in Z_{10303}, truncate to {0..10000}, best shift should retain ~99-101 elements. Assigned to opus because correctness of GF(101³) arithmetic is paramount — a subtle bug here wastes the entire session. Timeout set to 1800s because gen 1 explore_1 (which did similar GF arithmetic) hit the 1200s timeout; the multi-polynomial search in Phase 3 needs extra time.

**exploit_2 (sonnet, 1500s)**: Blocker analysis + SA from 99-seed. Two complementary approaches: (1) characterize exactly why the 99-element set can't accept a 100th element (fast, informational), then (2) use SA with temporary worsening to escape the local optimum. This directly tests idea_010. Sonnet is sufficient — the analysis is algorithmic, not requiring deep mathematical insight. Timeout 1500s because SA needs runtime to explore.

**experimentator_1 (opus, 900s)**: Build shared helpers (find_singer_set, greedy_sidon, build_diff_counts). Four agents independently reimplemented these in gen 1, wasting ~30 turns and producing 2 buggy solutions. Opus to ensure correct, well-tested implementations. Timeout 900s — helpers are well-specified, this is a focused coding task.

### Track B — Radical exploration (2 agents, mandatory)

**explore_1 (sonnet, 1500s)**: Non-Singer algebraic construction from scratch. Assigned Ruzsa and Bose-Chowla directions — both are mathematically sound Sidon set constructions that have never been tried in our system. Even if they score lower than Singer initially, they may have different extension properties that enable different paths to 100+. Explicitly forbidden from using Singer sets or existing solutions.

**research_1 (sonnet, 700s)**: Survey non-Singer constructions, published computational records, and specialized search techniques for Sidon sets. Gen 1 research was excellent (identified Singer as the breakthrough approach). Gen 2 research needs to look beyond Singer — are there published 100+ element Sidon sets in {0..10000}? Are there hybrid construction techniques? Timeout 700s based on gen 1 research completing in 698s.

## What I Deliberately Did NOT Do

1. **No full agent**: Gen 1 full_1 scored 66 (no improvement). Full agents are best for gen 1 cold starts. Gen 2 benefits more from targeted exploit and focused exploration.

2. **No genetic crossover**: All top solutions are Singer q=97 variants — crossing two nearly-identical solutions won't produce novelty. Genetic crossover becomes valuable when we have solutions from different clusters (e.g., if explore_1 finds a Ruzsa-based solution, gen 3 could cross it with a Singer-based one).

3. **No SA-from-greedy agent**: Confirmed ceiling of 68. Would waste a slot.

4. **No second explore**: Budget discipline. One Track B explore + one research is the minimum. Adding a second explore would push to 6 agents; the marginal value is lower than the exploit agents' potential.

## Risks and Contingencies

1. **exploit_1 fails to implement GF(101³) correctly**: The biggest risk. GF(101³) arithmetic is tricky — wrong irreducible polynomial or wrong primitive element selection breaks everything. Mitigation: opus model, reference implementation in best.py, explicit verification steps in brief.

2. **Singer q=101 best shift gives only 99**: Possible. If so, the multi-polynomial search (Phase 3) is the backup. If that also gives 99, we know Singer q=101 truncation is not the answer and must pivot to hybrid approaches or larger constructions in gen 3.

3. **Experimentator helpers have bugs**: Would propagate to all future agents. Mitigation: extensive verification tests specified in the brief, opus model for correctness.

4. **explore_1's alternative construction scores much lower**: Expected. A Ruzsa-97 set has 97 elements vs Singer's 98. The value is in the different structure, not the raw score.

## Timeout Calibration

Based on gen 1 timing:
- All 3 work sessions hit the 1200s default timeout (explore_1: 1200.1s, explore_2: 1200.1s, full_1: 1200.1s)
- Research completed in 698s
- Wrap-up sessions: 92-228s

For gen 2:
- exploit_1: 1800s (GF arithmetic + 10303 shifts + multi-polynomial = needs more time)
- exploit_2: 1500s (blocker analysis is fast, but SA needs extended runtime)
- experimentator_1: 900s (focused coding task, well-specified)
- explore_1: 1500s (implementing a new algebraic construction from scratch)
- research_1: 700s (slightly more than gen 1's 698s, research scope is focused)
