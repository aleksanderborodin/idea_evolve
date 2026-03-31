## Current Population Status
No solutions evaluated yet. Baseline reference: V14opt ~770 µs (geomean). Target: 477 µs.

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_008.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/V14opt.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/baseline.cpp`

## Directive

**Primary direction: AVX-512 micro-kernel with hardware popcount + fully unrolled k-loop.**

The baseline uses AVX2 (256-bit) with a 6-instruction LUT-based popcount. Your job is to build
an AVX-512 implementation that exploits:

1. **`_mm512_popcnt_epi8()`** (AVX512_BITALG) — replace the LUT popcount with a single instruction.
2. **64-byte wide operations** — process 64 columns of B per micro-kernel iteration instead of 32.
3. **Fully unrolled k-loop** — k_bytes is only 2, 4, or 7. Create specialized code paths for each.
   The loop overhead is significant when k is this small.
4. **int16 accumulation** — the diff per byte is at most ±8, and with k_bytes ≤ 7 the accumulated
   sum is at most ±56. Accumulate in int16 and widen to int32 only at the store step. This doubles
   throughput in the accumulation path.

Keep the BLIS 5-loop tiling structure from the baseline but adapt tile sizes for AVX-512:
- NC should be larger (512 or 1024) since we process 64 columns per µkernel call
- MC can stay at 64 or go to 128
- KC is irrelevant (k_bytes always ≤ 7, fits trivially)

Study the baseline `optimize.py` carefully — it shows the exact Python wrapper format. Your
`entrypoint()` must return a C++ string defining `void gemmCandidate(...)`.

**Off-limits:** Do NOT explore VNNI-based reformulations (that's explore_2's direction). Focus
purely on the popcount + wide-register approach.

Read the detail_file after each evaluation to understand per-size performance breakdown.
