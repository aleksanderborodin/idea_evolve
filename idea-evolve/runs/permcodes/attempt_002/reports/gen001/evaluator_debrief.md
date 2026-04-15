# Evaluator Report — gen001

## Completed

- **12 solutions evaluated**: 10 valid, 2 invalid (GA crash, ILNS bug)
- **Best score: 616** (AGL orbit clique, confirmed by 7/7 valid algebraic solutions)
- **Worst valid: 262** (direct greedy on full 40320-perm space)
- **14 ideas created** (idea_001–idea_014): AGL orbit clique established, ILNS/v stochastic approaches documented, PGL/PSL/VNS/SA marked unexplored
- **4 patterns created**: AGL clique uniquely optimal, 616-code orbit-closed, stochastic caps at ~293, greedy needs orbit structure
- **3 preliminary clusters**: Algebraic (616), Stochastic (293), Helper Techniques
- **coverage_matrix.md, solution_idea_map.md, generation_snapshot.md, state_of_affairs.md, agent_gaps.md, evaluator_report.md** — all written

## Incomplete

- **No clusters/ directory files written** (cluster definitions not yet in knowledge/clusters/)
- **No ideas moved to knowledge/ideas/** (all ideas still in output/new_ideas/)
- **No patterns moved to knowledge/patterns/** (all patterns still in output/new_patterns/)
- **No experiment consolidation** — no experiments directory existed to consolidate
- **PGL(2,7) compatible-permutation count never run** — critical empirical data point missing
- **PGL(2,7) elements not derived** — top priority experiment still unexecuted

## Strategic Shift

**YES**: AGL(1,8) construction is at its limit. Beating 616 requires PGL(2,7) or PSL(2,7) orbit construction — a qualitatively different group action.

## Priority for Next Generation

1. **PGL(2,7) orbit clique search** (idea_012) — only path to beating 616
2. **Run compatible-permutation count on 616-code** — confirm orbit-closure empirically
3. **Fix GA crossover** (orbit-level crossover, not union+prune)
