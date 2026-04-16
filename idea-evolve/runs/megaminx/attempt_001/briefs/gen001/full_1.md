## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py` -> fitness = 50572
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol01.py` -> fitness = 101000000

## Read first
- `problems/megaminx/description.md`
- `problems/megaminx/initial_ideas.md`
- `problems/megaminx/initial_facts.md`
- `problems/megaminx/examples/baseline_cayleypy.py`
- `problems/megaminx/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/score_progression.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/summary.md`

## Directive
Build the strongest practical generation-1 end-to-end baseline: a budget-aware beam-search solver with a guaranteed-valid sample-submission fallback.

Overall strategy:
- Use `helpers.core.cayleypy_beam_solver(...)` as the main search engine.
- Allocate search budget by puzzle depth bucket rather than uniformly.
- Always preserve validity by falling back to `load_sample_submission_paths()` whenever search fails, returns nothing, or returns a longer path.

Specific goals:
- Beat the 50572 proxy baseline while keeping `is_valid = 1`.
- Improve `compression_ratio` below 1.0 and push `improved_count` upward.
- Prioritize genuine gains in short and medium buckets first; do not waste the whole budget trying to crack the deepest rows with unguided search.

Implementation guidance:
- Start from the `baseline_cayleypy.py` example, but make it complete and safe for all rows.
- Use the fact that depth equals `initial_state_id` to choose beam width and max steps.
- Keep the code simple enough that later exploit agents can refine it.

Deliverable: one solid baseline solution that should become the reference point for generation 2 exploitation if it beats the floor.
