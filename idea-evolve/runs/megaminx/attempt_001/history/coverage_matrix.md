# Coverage Matrix — Gen 001

## Top Idea Combinations Tried

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_001 alone | 7 | 46312 | 46312 | gen_001 |
| idea_001 + idea_003 | 2 | 46312 | 46312 | gen_001 |
| idea_001 + idea_004 | 1 | 46312 | 46312 | gen_001 |
| idea_002 (failed) | 1 | 50474 | 50474 | gen_001 |

## Individual Idea Coverage

| Idea | Times Used Central | Times Used Peripheral | Best Score | Status |
|------|-------------------|----------------------|------------|--------|
| idea_001 (basic cancellation) | 11 | 1 | 46312 | established |
| idea_002 (X.Y.-X heuristic) | 1 | 0 | 50474 | debunked |
| idea_003 (predictor-guided beam) | 0 | 2 | 46312 | active (unguided tested) |
| idea_004 (MITM) | 0 | 1 | 46312 | active |
| idea_005 (identity discovery) | 0 | 0 | — | active (not tried) |
| idea_006 (hamming predictor) | 0 | 0 | — | active (not tried) |
| idea_007 (corner pattern DB) | 0 | 0 | — | active (not tried) |

## Unexplored Regions (High Priority for Gen 2)

- **idea_003 + idea_004 combinations**: MITM with predictor guidance
- **idea_006 alone**: Zero-cost hamming predictor experiment
- **idea_005**: No systematic identity discovery attempted
- **idea_007**: No pattern database work
- **Cross-bucket search strategies**: Different algorithms for different depth ranges

## Score Progression

| Solution | Score | compression_ratio | improved_count | dominant_technique |
|----------|-------|-------------------|-----------------|-------------------|
| gen001_full_1_sol01 | 46312 | 0.9158 | 98 | depth-aware beam + cancellation |
| gen001_explore_1_sol01 | 46312 | 0.9158 | 98 | MITM + cancellation |
| gen001_explore_2_sol01 | 46312 | 0.9158 | 98 | greedy cancellation |
| gen001_explore_2_sol02 | 46312 | 0.9158 | 98 | iterative bidirectional cancellation |
| gen001_explore_2_sol03 | 46312 | 0.9158 | 98 | midpoint repair |
| gen001_explore_2_sol04 | 50474 | 0.9981 | — | X.Y.-X heuristic (FAILED) |
| gen001_explore_2_sol05 | 46312 | 0.9158 | 98 | beam search + local shortening |

**Sample submission baseline:** 50572 (compression_ratio=1.0)
**Target:** 15000 (compression_ratio≈0.30)
**Kaggle top-3 equivalent:** ~8050 (compression_ratio≈0.16)