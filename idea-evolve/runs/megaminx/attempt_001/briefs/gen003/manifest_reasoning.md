# Manifest Reasoning — Generation 3

## Situation Assessment

**Score trajectory:** 50572 → 46312 → 44114. We're improving but the pace is decelerating. Gen 1 gained 4260 (8.4%). Gen 2 gained 2198 (4.7%). The target is 15000 — we need 29114 more points of improvement. At the current rate, we'd need ~15 more generations of compression gains that likely don't exist.

**Compression is exhausted.** Six explore_2 solutions in gen 2 converged to 44114 ± 4 using algebraic identity compression. Eight different variations of the same approach all landed on the same number. This is a ceiling, not a temporary plateau.

**The trained MLP predictor (idea_008) has zero trials after 2 generations.** This is the single most critical fact. Every analysis layer — evaluator, system critic, consistency reviewer, all agent reports — agrees this is the primary path to the target. research_1 confirmed the pipeline works (`random_walks` → train MLP → `Predictor` → `beam_search(predictor=...)`). But no agent has executed it end-to-end. exploit_1 tried and hit a state-encoding error, then fell back to hamming (which scored the same as baseline).

**Coverage map shows massive unexplored territory.** idea_008 has 0 central uses. Compression + beam search has 0 trials. The only well-covered region is compression (idea_001 + idea_009, 6 solutions, all at 44114).

## Why This Mix of Agent Types

### exploit_1 (opus, 3600s) — THE critical experiment
This agent runs the trained MLP predictor end-to-end. I gave it the longest timeout (3600s) because:
- Training data generation takes time (50k walks of depth 20)
- MLP training needs 10+ epochs
- Beam search on 101 proxy puzzles at width 4096 is compute-intensive
- exploit_1 in gen 2 took 1831s and didn't complete the predictor experiment

I chose opus because this experiment requires precise API integration — the state encoding error that blocked gen 2 needs careful handling. A reasoning-heavy model is more likely to get it right.

The directive explicitly instructs to start from compressed paths then beam-search (REC-7), combining the best of both approaches.

### experimentator_1 (opus, 2700s) — Helper infrastructure
The system critic's REC-2 calls for a `trained_predictor_beam_search` helper. Every agent that tries the predictor route must rediscover cayleypy integration details. This is pure friction. The experimentator builds the helper, validates it, and (if time permits) produces a scored solution using it.

I chose opus because helper code needs to be correct — it will be used by all future agents.

### explore_1 (sonnet, 2700s) — Track B radical exploration
Track B agent pursuing a genuinely different approach (layered solving, A* with landmarks, scramble structure exploitation, or multi-phase compression). The coverage map shows zero attempts at any non-beam, non-compression approach. This agent is explicitly forbidden from using compression or predictor-guided beam search.

### research_1 (sonnet, 1800s) — Track B deep research
gen002 research_1 confirmed the pipeline but couldn't access actual Kaggle solution code. This gen's research agent should try harder to study what the top-scoring competitors actually did — their model architectures, training data, beam parameters. Also investigate cayleypy source code for undocumented features and alternative search algorithms.

### explore_2 (sonnet, 2700s) — Compression + beam combination
REC-7 from the system critic. Nobody has tried starting beam search from compressed paths. This is a straightforward but untested idea. If the trained predictor works, starting from compressed paths should amplify the effect. If the predictor doesn't work, even unguided beam from compressed paths might find something.

## Parallel Group Structure

**Group 1: [exploit_1, experimentator_1, explore_1]** (3 agents, at concurrency budget of 3)
- exploit_1 runs the critical experiment
- experimentator_1 builds the helper in parallel
- explore_1 pursues radical exploration independently
- These three don't depend on each other

**Group 2: [research_1, explore_2]** (2 agents, within budget)
- research_1 findings from Group 2 could inform explore_2 if the light evaluator picks up something
- But explore_2 has a concrete directive already — it doesn't depend on research_1

The Light Evaluator runs between Group 1 and Group 2, so explore_2 and research_1 will see any new ideas/patterns extracted from the first group's output.

## Timeout Rationale

| Agent | Timeout | Reasoning |
|-------|---------|-----------|
| exploit_1 | 3600s | gen002 exploit_1 took 1831s and didn't complete the predictor. The full pipeline (walks + train + beam) needs significantly more time. 3600s provides room for 2-3 attempts. |
| experimentator_1 | 2700s | Helper building + validation. gen002 experimentator took 1831s and produced nothing — this one has a concrete mandate. |
| explore_1 | 2700s | New approaches may need iteration. gen002 explore agents took 968-3187s. |
| research_1 | 1800s | gen002 research_1 took 1312s. Similar scope this generation. |
| explore_2 | 2700s | Combined approach needs time for both compression and beam search phases. |

## What I Deliberately Chose NOT to Do

1. **No genetic agent.** The population lacks genuine solution diversity — 19 of 23 solutions are explore-type, and 6 of the top 10 are identical at 44114. Crossing two compression solutions won't produce a breakthrough. Genetic agents are valuable when we have solutions from genuinely different approaches.

2. **No second exploit agent.** One exploit with a clear mandate is better than two diluted ones. The critical experiment is singular — run the trained predictor.

3. **No more compression tuning.** explore_2's 8 variations in gen 2 all converged to 44114 ± 4. The compression ceiling is established.

4. **No full agent.** The exploit_1 directive essentially gives it a full-scope mandate (build the entire pipeline end-to-end). A separate full agent would duplicate this effort.

## Risks

1. **exploit_1 may hit the same state-encoding error again.** Mitigated by the detailed directive with specific pitfalls documented. But if cayleypy's internal state handling is genuinely opaque, even opus might struggle.

2. **The trained predictor might not beat 44114.** This is actually valuable information (it tells us the current approach is wrong), but it means we need a fundamentally different strategy. The Track B explore and research agents are insurance against this.

3. **experimentator_1 may produce nothing again.** Mitigated by a very specific mandate (build one helper, not "run experiments"). But if cayleypy's API is too complex to wrap cleanly, the helper may not be deployable.

4. **Total of 5 agents is at the high end.** Each costs compute. But given the urgency of the trained-predictor experiment, I consider this justified.

5. **Track B explores may return weak scores.** Expected and acceptable. Their value is in opening new directions, not immediate score improvement.
