## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py` -> fitness = 100000.00, invalid (`is_valid: 0`; compile failed because `fast-conv` harness files were missing). Treat this as a seed/reference only, not a usable best.
Second best: none yet.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_007.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.score`

## Directive
Produce the first dependable end-to-end valid solution for this attempt. Use the seed baseline only as a functional reference for layout and edge handling, then write a self-contained candidate that compiles without relying on external source inclusion beyond the evaluator harness.

The preferred path is a conservative AVX-512 upgrade of the baseline: remove unnecessary KC tiling for tiny `k_bytes`, use 64-column vector loads where straightforward, keep row blocking simple, and preserve robust tails. Do not chase an exotic formulation at the expense of validity. Your success criterion is a valid `.score` sidecar with real timings, even if the score is only moderately better than the historical 770 us baseline.

Off-limits for this brief: VNNI research prototypes and aggressive streaming-store experiments before a valid baseline exists.
