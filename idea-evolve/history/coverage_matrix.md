# Coverage Matrix — Generation 1

## Key Idea Combinations Explored

| Idea Combination | Times Tried | Best Score (µs) | Avg Score (µs) | Last Tried |
|---|---|---|---|---|
| idea_001 (AVX-512 popcount) alone | 2 | 602.29 | 628.52 | gen_1 |
| idea_001 + idea_004 (deferred widen) | 12 | 148.18 | 354.32 | gen_1 |
| idea_001 + idea_004 + idea_007 (vec pack_B) | 4 | 148.18 | 200.78 | gen_1 |
| idea_001 + idea_004 + idea_010 (skip memset) | 6 | 148.18 | 175.34 | gen_1 |
| idea_001 + idea_004 + idea_007 + idea_010 | 4 | 148.18 | 169.38 | gen_1 |
| idea_001 + idea_004 + idea_011 (vpternlogd) | 8 | 148.18 | 302.04 | gen_1 |
| idea_001 + idea_009 (8x64 kernel) | 1 | 493.42 | 493.42 | gen_1 |
| idea_001 + idea_006 (streaming stores) | 3 | 167.23 | 483.60 | gen_1 |
| idea_001 + idea_002 (template unroll) | 2 | 171.04 | 306.74 | gen_1 |
| idea_001 + idea_012 (stack buffers) | 1 | 148.18 | 148.18 | gen_1 |

## Unexplored Combinations (High Priority)

| Combination | Rationale |
|---|---|
| idea_001 + idea_013 (no-packing direct kernel) | Eliminate pack_B overhead entirely |
| idea_009 (8x64) + idea_004 (int8 accum) | Register-light 8-row kernel |
| idea_001 + idea_005 (NC tuning) systematic | Only NC=256 and NC=512 tested |
| idea_010 + idea_006 (memset skip + streaming) + optimized NC | Full memory optimization stack |
| idea_011 (vpternlogd) isolation test | Quantify standalone impact |

## Notes
- idea_003 (VNNI) debunked — do not explore further
- idea_008 (skip KC) is universal — present in all solutions, not tracked as a combination
- All 14 solutions are valid (is_valid=1), no correctness failures
