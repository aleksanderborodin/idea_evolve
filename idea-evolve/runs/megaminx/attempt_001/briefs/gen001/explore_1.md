## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py` -> fitness = 50572
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol01.py` -> fitness = 101000000

## Read first
- `problems/megaminx/description.md`
- `problems/megaminx/initial_ideas.md`
- `problems/megaminx/initial_facts.md`
- `problems/megaminx/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/score_progression.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/summary.md`

## Directive
This is a Track B radical exploration. You must NOT use `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py`, `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py`, any file under `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/`, or the plain sample-submission-echo approach as your starting point. Start from scratch.

Direction: build a solver around meet-in-the-middle or depth-bounded bidirectional search ideas for the shallow-to-medium proxy rows. The goal is to discover whether an explicit two-frontier construction can beat the sample baseline on ids where unguided direct search is still tractable.

Requirements:
- Do not simply wrap `load_sample_submission_paths()` and call it the main method. A fallback is allowed only as a safety net for unsolved rows.
- Focus on puzzles where a genuine search win is plausible: special, short, and medium buckets first.
- If you use the sample path at all, use it only after your own search attempt fails or returns a longer path.
- Explicitly measure whether your approach improves `improved_count` and `compression_ratio` while keeping `is_valid = 1`.

Off-limits:
- No predictor training.
- No beam-search-first design; that is assigned elsewhere this generation.
- No incremental tweaks to the existing sample-submission baseline.

Deliverable: one or more valid solutions that test whether MITM-style search can produce shorter paths than the free baseline on the tractable part of the proxy.
