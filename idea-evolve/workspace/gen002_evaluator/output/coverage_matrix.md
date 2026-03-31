# Coverage Matrix — Updated Generation 2

**Scale note:** Capped to top 30 most-used ideas. Sparse format (only rows with actual data).

## Single-Idea Performance

| Idea | Times Central | Best Score (µs) | Avg Score (µs) | Last Tried |
|------|-------------|-----------------|-----------------|------------|
| idea_001 (AVX-512 popcount) | 28 | 147.26 | 277.30 | gen_2 |
| idea_004 (deferred widening) | 27 | 147.26 | 271.64 | gen_2 |
| idea_014 (row-streaming) | 8 | 147.26 | 177.39 | gen_2 |
| idea_007 (vectorized pack_B) | 15 | 148.18 | 274.56 | gen_2 |
| idea_010 (memset skip) | 14 | 147.26 | 231.76 | gen_2 |
| idea_011 (vpternlogd) | 10 | 147.26 | 259.39 | gen_2 |
| idea_013 (no-pack direct B) | 8 | 182.31 | 248.86 | gen_2 |
| idea_006 (streaming stores) | 6 | 167.23 | 249.65 | gen_2 |
| idea_005 (NC tuning) | 5 | 148.18 | 392.26 | gen_2 |
| idea_012 (stack buffers) | 8 | 148.18 | 291.91 | gen_2 |
| idea_002 (k-loop unroll) | 4 | 171.04 | 337.75 | gen_2 |
| idea_009 (8-row kernel) | 3 | 207.32 | 377.73 | gen_2 |
| idea_019 (adaptive NC) | 2 | 223.17 | 248.64 | gen_2 |
| idea_017 (B micro-pack) | 2 | 177.02 | 189.42 | gen_2 |
| idea_015 (size-adaptive NT) | 0 | — | — | never |
| idea_016 (8-row int8 kernel) | 0 | — | — | never |
| idea_018 (vpshufb LUT) | 0 | — | — | never |

## Key Idea Combinations (Central ideas)

| Idea Combination | Times Tried | Best Score (µs) | Avg Score (µs) | Last Tried |
|-----------------|-------------|-----------------|-----------------|------------|
| idea_001 + idea_004 + idea_007 + idea_010 (BLIS full stack) | 8 | 148.18 | 194.61 | gen_2 |
| idea_001 + idea_004 + idea_014 (row-streaming) | 8 | 147.26 | 177.39 | gen_2 |
| idea_001 + idea_004 + idea_013 (no-pack) | 6 | 182.31 | 246.54 | gen_2 |
| idea_001 + idea_004 + idea_006 (streaming stores) | 5 | 167.23 | 260.95 | gen_2 |
| idea_001 + idea_009 (8-row, any accum) | 3 | 207.32 | 377.73 | gen_2 |
| idea_014 + idea_017 (row-stream + B micro-pack) | 2 | 177.02 | 189.42 | gen_2 |
| idea_014 + idea_006 (row-stream + NT stores) | 1 | 195.22 | 195.22 | gen_2 |

## Unexplored High-Priority Combinations

| Combination | Rationale | Expected Impact |
|------------|-----------|-----------------|
| idea_014 + idea_015 (row-stream + size-adaptive NT) | Row-streaming has sequential writes → NT stores compatible | Potentially 2-3x on geomean |
| idea_016 + idea_015 (8-row int8 + NT stores) | Best kernel + best stores | Potentially 3-5x on geomean |
| idea_001 + idea_004(int8) + idea_016 + idea_015 | Full new stack | Target ~30-50 µs |
| idea_014 + idea_019 (row-stream + adaptive NC) | Optimize medium separately | ~20% medium improvement |
| idea_009 + idea_004(int8) (8-row + int8 accum) | Resolves register pressure failure | Untested, high confidence |
| idea_018 (vpshufb LUT, standalone) | Alternative compute path | Unknown — needs evaluation |

## Coverage Gaps

1. **No solution combines NT stores with sequential write pattern correctly.** BLIS jc-outer conflicts with NT; row-streaming ic-outer is compatible but NT stores haven't been applied to the best row-streaming solution.
2. **8-row int8 kernel never tested empirically.** Theoretical analysis is strong (research + experimentator), but no agent built it.
3. **vpshufb LUT kernel never tested.** Completely unexplored alternative compute path.
4. **No solution uses both int8 accum AND row-streaming for large with B micro-packing.** The best row-streaming solution (sol01) doesn't micro-pack B; the micro-pack variant (sol06) doesn't achieve the same performance.
