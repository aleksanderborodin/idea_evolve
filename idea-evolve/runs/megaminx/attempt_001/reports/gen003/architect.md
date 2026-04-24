# Architect Report — Generation 3

## Data Anomalies

1. **idea_008 has 0 trials after 2 generations.** This is the single most anomalous fact in the system. The primary path to the target (trained MLP predictor) has never been executed, despite being identified as the top priority by the evaluator, system critic, and consistency reviewer in gen 2. The pipeline was confirmed functional by research_1 — the only blocker was execution friction (state encoding error in exploit_1).

2. **Compression ceiling is remarkably precise.** Six different explore_2 solutions with different rule sets and application strategies all landed on 44114 ± 4. The ceiling is real and stable. No amount of additional compression work will meaningfully improve it.

3. **experimentator_1 in gen 2 produced literally nothing.** Zero files, zero output. The agent was given no specific mandate. This was a complete waste of a GPU-equipped agent slot.

4. **Score deceleration.** Gen 1 improved by 4260 (8.4%). Gen 2 improved by 2198 (4.7%). If this trend continues, gen 3 would improve by ~1200 points to ~42914 — which is still nowhere near 15000. Compression-based improvement is asymptotically approaching a floor.

## Confidence

**Medium.** The strategic center is clear and unanimous: run the trained predictor experiment. Every analysis layer agrees. But confidence is not high because:

1. No agent has successfully navigated cayleypy's state encoding for the predictor pipeline. The single attempt (exploit_1 gen 2) failed.
2. We don't know if a depth-20-trained predictor will generalize to depth-500+ puzzles. If it doesn't, the primary path is blocked.
3. If the predictor doesn't work, we're relying on Track B explores to find something entirely new — which is inherently uncertain.

## What Didn't Fit

1. **No genetic agent.** The population lacks the diversity for meaningful crossover. I would add one in gen 4 if the predictor experiment produces solutions with a genuinely different structure from compression.

2. **No dedicated agent to fix documentation inconsistencies.** The description.md "CPU-only" claim, the PROXY_SIZE=100 typo, and the string-replacement warning are all real issues. But they're lower priority than the predictor experiment. Agents can work around documentation issues; they can't work around an untested primary hypothesis.

3. **No agent studying the scramble structure.** The fact that scramble_depth == initial_state_id is a massive structural prior. But I couldn't fit a dedicated agent for this. explore_1 may pick it up as one of its radical directions.

## Strategic Risks

1. **If exploit_1 fails to run the predictor pipeline**, gen 3 may end with no progress on the primary path. Mitigated by having experimentator_1 also building the helper infrastructure. But if the cayleypy API is fundamentally broken for predictor-guided search, both agents fail.

2. **If the predictor runs but doesn't beat 44114**, the system needs to pivot. The Track B agents (explore_1, research_1) provide insurance, but they might not find anything actionable in one generation.

3. **Five agents is a large generation.** Total wall-clock with groups could be 30-60 minutes of agent work plus analysis. If the predictor is a dead end, that's a lot of compute on a failed hypothesis.

4. **The gap between 44114 and 15000 is massive (29k points).** Even a successful predictor experiment is unlikely to close this gap in one generation. We need to think about whether the current approach (beam search + compression) can ever reach 15000, or whether a fundamentally different paradigm is needed.

## Open Questions for the System Critic

1. **Should we reconsider the target of 15000?** Kaggle top-3 is ~8050 (full-set), which would be ~805 proxy. Our current 44114 proxy is very far from that. Is the target achievable with beam search + predictor, or do we need to explore reinforcement learning, GNN-based approaches, or other paradigms?

2. **Is the experimentator role correctly scoped?** Two generations in a row, the experimentator has been underutilized (gen 1: no experimentator, gen 2: no output). Should the architect always give the experimentator a specific, concrete task? Should it default to building helpers?

3. **Knowledge update lag.** gen 2 agents read a stale gen 1 state_of_affairs that listed hamming as "untested." By the time the gen 2 evaluator updated it, agents had already wasted turns on debunked approaches. Should the system support mid-generation knowledge updates?
