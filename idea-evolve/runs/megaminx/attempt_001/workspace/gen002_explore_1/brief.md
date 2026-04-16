## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/full_1/sol01.py` -> fitness = 46312
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/explore_1/sol04.py` -> fitness = 46312

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/solution_idea_map.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen001/explore_1.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen001/research_1.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/feedback/experiment_suggestions/gen001.md`
- `problems/megaminx/description.md`

## Directive
This is a Track B radical exploration. You must NOT use `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py`, anything in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/`, or refine `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/full_1/sol01.py`. You must NOT do predictor-guided beam search, unguided beam search, or incremental compression tuning. Start from scratch.

Direction: implement a genuinely different search family based on IDA* or another admissible / near-admissible depth-first strategy using a hand-built heuristic or lightweight pattern database for a restricted subproblem.

Goals:
- Test whether a search family outside beam search can outperform the compression floor on at least some proxy buckets.
- Prefer a corner-only, subset-based, or bucket-specialized heuristic if full-state optimal search is too expensive.
- If the global method cannot cover all 101 rows, design a hybrid that uses your new search only where it is strong and guaranteed-valid fallback elsewhere.

What to avoid:
- No starting from prior solution code.
- No reusing the gen001 beam parameter recipes.
- No X.-X-only solution with cosmetic differences.

Success is not defined only by beating 46312. A clear, working non-beam search result with honest bucket limits is valuable if it reveals a new basin of attraction.
