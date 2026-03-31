## Current Population Status
No solutions evaluated yet. Baseline reference: V14opt ~770 µs (geomean). Target: 477 µs.

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_007.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/V14opt.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/final.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/gemm/baseline.cpp`
- `/home/sasha/Desktop/project_alpha/fast-conv/candidate_template.cpp`

## Directive

**Build a complete, well-engineered AVX-512 solution combining the most promising ideas.**

Your goal is to produce the best single solution by carefully integrating multiple optimizations:

1. **Start from the BLIS structure** in `optimize.py` but upgrade everything to AVX-512:
   - Replace AVX2 popcount LUT with `_mm512_popcnt_epi8()` (single instruction)
   - Widen micro-kernel from 4×32 (AVX2) to 4×64 (AVX-512)
   - Use 512-bit loads/stores throughout

2. **Re-tune tile sizes** for Tiger Lake:
   - NC: increase to 512+ (we process 64 cols per µkernel, so NC should be a multiple of 64)
   - MC: keep at 64 or try 128 (A is tiny, fits in L1 regardless)
   - KC: eliminate — k_bytes ≤ 7 always, no need to tile over k

3. **Unroll the k-loop**: Dispatch to specialized functions for k_bytes=2, 4, 7 with fully
   unrolled inner loops.

4. **SIMD packing**: Replace scalar pack_A and pack_B loops with SIMD copies where possible.

5. **Streaming stores** for large m: when m > 4096, use `_mm512_stream_si512` on output.

6. **int16 accumulation**: accumulate popcount diffs in int16, widen to int32 only at store.

Be methodical: get a correct AVX-512 version first (use `compile_and_test` from helpers.core
for quick correctness checks), then optimize one thing at a time. After each change, run
`python3 evaluate.py output/solNN.py` and check the detail_file for per-size breakdown.

Focus on getting ALL sizes fast, not just one. The geometric mean penalizes solutions that
are fast on one size but slow on another. The small benchmark (k=2, m=1024) is often limited
by loop overhead; the large benchmark (k=7, m=65536) is limited by memory bandwidth and cache.

Read `fast-conv/gemm/V14opt.cpp` and `fast-conv/gemm/final.cpp` to understand the existing
BLIS implementations and their packing strategies.
