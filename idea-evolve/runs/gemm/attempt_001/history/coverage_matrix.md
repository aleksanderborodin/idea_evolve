# Coverage Matrix — Updated Generation 3

**Scale note:** Capped to top 30 most-used ideas. Sparse format (only rows with actual data).

## Single-Idea Performance

| Idea | Times Central | Best Score (µs) | Avg Score (µs) | Last Tried |
|------|-------------|-----------------|-----------------|------------|
| idea_001 (AVX-512 popcount) | 41 | 141.0 | 272.05 | gen_3 |
| idea_004 (deferred widening) | 39 | 141.0 | 265.42 | gen_3 |
| idea_014 (row-streaming) | 17 | 141.0 | 179.81 | gen_3 |
| idea_007 (vectorized pack_B) | 15 | 148.18 | 274.56 | gen_2 |
| idea_011 (vpternlogd) | 12 | 141.0 | 254.21 | gen_3 |
| idea_010 (memset skip) | 14 | 141.0 | 227.88 | gen_3 |
| idea_013 (no-pack direct B) | 8 | 182.31 | 248.86 | gen_2 |
| idea_006 (streaming stores) | 10 | 141.0 | 258.36 | gen_3 |
| idea_018 (vpshufb LUT) | 5 | 341.78 | 397.62 | gen_3 |
| idea_005 (NC tuning) | 5 | 148.18 | 392.26 | gen_2 |
| idea_012 (stack buffers) | 9 | 141.0 | 283.76 | gen_3 |
| idea_002 (k-loop unroll) | 4 | 171.04 | 337.75 | gen_2 |
| idea_009 (8-row kernel) | 4 | 168.35 | 341.26 | gen_3 |
| idea_016 (8-row int8 kernel) | 1 | 168.35 | 168.35 | gen_3 |
| idea_022 (4-row B-amort) | 3 | 204.52 | 321.99 | gen_3 |
| idea_019 (adaptive NC) | 2 | 223.17 | 248.64 | gen_2 |
| idea_017 (B micro-pack) | 2 | 177.02 | 189.42 | gen_2 |
| idea_015 (size-adaptive NT) | 1 | 141.0 | 141.0 | gen_3 |
| idea_020 (multi-threading) | 0 | — | — | never |
| idea_021 (SSE 128-bit NT) | 0 | — | — | never |

## Key Idea Combinations (Central ideas)

| Idea Combination | Times Tried | Best Score (µs) | Avg Score (µs) | Last Tried |
|-----------------|-------------|-----------------|-----------------|------------|
| idea_001 + idea_004 + idea_014 (row-streaming) | 17 | 141.0 | 179.81 | gen_3 |
| idea_001 + idea_004 + idea_007 + idea_010 (BLIS full stack) | 8 | 148.18 | 194.61 | gen_2 |
| idea_001 + idea_004 + idea_013 (no-pack BLIS) | 6 | 182.31 | 246.54 | gen_2 |
| idea_001 + idea_018 (vpshufb LUT) | 5 | 341.78 | 397.62 | gen_3 |
| idea_014 + idea_015 (row-stream + NT check) | 1 | 141.0 | 141.0 | gen_3 |
| idea_014 + idea_016 (row-stream + 8-row int8) | 1 | 168.35 | 168.35 | gen_3 |
| idea_014 + idea_006 (row-stream + NT stores) | 3 | 184.84 | ~260 | gen_3 |
| idea_014 + idea_022 (row-stream + 4-row) | 1 | 204.52 | 204.52 | gen_3 |
| idea_018 + idea_022 (vpshufb + 4-row) | 2 | 341.78 | 380.73 | gen_3 |
| idea_001 + idea_009 (8-row, any accum) | 4 | 168.35 | 341.26 | gen_3 |

## Unexplored High-Priority Combinations

| Combination | Rationale | Expected Impact |
|------------|-----------|-----------------|
| idea_014 + idea_021 (row-stream + SSE 128-bit NT) | 16-byte alignment satisfied; sequential writes compatible | Large: 3841→~1350 µs. Geomean: ~105 µs |
| idea_014 + idea_022 + idea_004(int8) (row-stream + 4-row ternlogd) | 4-row gives 1.55-1.67x on med/large with ternlogd kernel | Geomean: ~80-95 µs |
| idea_014 + idea_020 (row-stream + multi-threading) | 2 cores for bandwidth doubling on large | Large: ~2100-2950 µs. Geomean: ~105-130 µs |
| idea_014 + idea_022 + idea_021 (4-row + SSE NT) | Combine B sharing + NT stores for large | Geomean: ~60-80 µs (if both work) |
| idea_014 + idea_020 + idea_021 (threading + SSE NT) | Maximum bandwidth utilization | Geomean: ~50-70 µs (theoretical) |

## Coverage Gaps

1. **SSE 128-bit NT stores (idea_021) completely untested with size-adaptive approach.** Exploit_1/sol03 tested 128-bit unconditionally (152 µs) but not size-adaptive. Highest priority.
2. **4-row ternlogd+popcnt kernel (idea_022) untested.** Only tested with vpshufb compute. Applying to the winning kernel is the #1 priority.
3. **Multi-threading (idea_020) completely unexplored.** No solution has ever used pthreads. Cgroup verification needed first.
4. **Column-blocked output with multi-row kernel** never tested. Could solve C write scatter (pattern_010).
