## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/full_1/sol01.py` -> fitness = 46312
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/explore_1/sol04.py` -> fitness = 46312

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/feedback/system_recommendations.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/feedback/experiment_suggestions/gen001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/feedback/consistency_reviews/gen001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen001/research_1.md`
- `problems/megaminx/description.md`
- `problems/megaminx/helpers/README.md`

## Directive
Run one narrow experiment: answer the falsifiable question "Does the zero-cost hamming predictor beat the 46312 compression floor on the 101-puzzle proxy?"

Methodology requirements:
- Build the smallest possible direct test using `Puzzles.megaminx()` and `Predictor(graph, 'hamming')`.
- Evaluate on the full proxy set, not a toy subset.
- Record total fitness, runtime, and per-depth-bucket results.
- If the existing helper layer blocks predictor injection, either bypass it directly in the experiment or package a minimal shared helper that exposes predictor-guided beam search.

Shared-helper option:
- If you confirm a clean reusable interface is useful, package it as `output/helpers/predictor_beam.py` with a minimal function that future solution agents can import. Keep it focused; do not build a framework.

Deliverables:
- A concise experimental report with yes/no answer, exact score, and whether the hamming predictor is strong enough to justify more exploit work.

Off-limits:
- Do not broaden into training a large model.
- Do not pursue algebraic compression or MITM.
- Do not spend time on Kaggle notebook archaeology; this is a controlled measurement task.
