## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py` -> fitness = 100000.00, invalid (`is_valid: 0`; compile failed because `fast-conv` harness files were missing). Treat this as a seed/reference only, not a usable best.
Second best: none yet.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_007.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_009.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.score`

## Directive
This is the cold-start research mission. Find approaches the system has never tried and turn them into concrete implementation guidance for generation 2. Read the active ideas and facts, then prioritize adjacent techniques for bit-serial GEMM, binary neural network inference, ternary weights, Tiger Lake AVX-512, VPOPCNT/BITALG, VNNI, and memory-store behavior for huge output matrices.

Expected deliverables: a concise report with at least five actionable kernel designs, their expected bottlenecks, which benchmark size they target, and which active ideas they support or contradict. Include one section diagnosing the current invalid baseline/evaluation anomaly from `sol01.score`, because the first generation may otherwise confuse "no valid implementation" with algorithmic failure.

Off-limits for this brief: spending the whole session tuning the existing AVX2 baseline or writing multiple full candidate implementations. If you test a tiny prototype, evaluate it immediately and report exactly what it showed.
