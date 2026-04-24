## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py` -> fitness = 100000.00, invalid (`is_valid: 0`; compile failed because `fast-conv` harness files were missing). Treat this as a seed/reference only, not a usable best.
Second best: none yet.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/gemm/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/gemm/attempt_002/population/gen000/baseline/sol01.py`

## Directive
Explore a non-popcount formulation centered on AVX-512 VNNI or byte-level dot products. The goal is to test whether the packed binary/ternary multiply can be transformed into signed or unsigned int8 vectors cheaply enough that `_mm512_dpbusd_epi32` or related byte dot-product machinery beats popcount for the tiny `k_bytes` cases.

Start from the data layout in the description, not from the current baseline implementation. You may use small lookup tables, byte expansion, sign masks, or precomputed per-byte contributions if they keep memory traffic controlled. Prioritize producing at least one valid candidate and one clear diagnostic report about whether VNNI is promising. Run `compile_and_test` before full evaluation if possible, then evaluate any valid solution immediately.

Off-limits for this brief: the direct `_mm512_popcnt_epi8` 4x64/8x64 design assigned to `explore_1`, BLIS tile retuning, and copying the AVX2 LUT popcount kernel.
