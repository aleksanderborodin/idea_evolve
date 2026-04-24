## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py` -> fitness = 100000.00, invalid (`is_valid: 0`; compile failed because `fast-conv` harness files were missing). Treat this as a seed/reference only, not a usable best.
Second best: none yet.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_009.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.score`

## Directive
Build an AVX-512 popcount kernel from scratch. Do not copy the AVX2 BLIS packing structure except as a correctness reference. The target direction is a direct no-KC-tile loop specialized by `k_bytes` values 2, 4, and 7, using `_mm512_popcnt_epi8()` over 64 columns at a time.

Focus on a compact row-blocked micro-kernel, preferably 4x64 first for register safety, with an optional 8x64 variant only after the 4x64 version is correct. Use a `switch(k / 8)` to dispatch to hand-unrolled code paths. Preserve correctness, zero `C`, handle tails for `m` and `n`, and run evaluation immediately after each candidate. If a fully optimized version is too risky, submit the fastest valid AVX-512 popcount implementation you can produce.

Off-limits for this brief: VNNI/dpbusd reformulation, multi-threading, and tile-size-only tuning of the baseline.
