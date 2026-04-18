# Coverage Matrix — Gen 002

## Top Idea Combinations Tried

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_001 alone | 5 | 46312 | 46312 | gen_001 |
| idea_001 + idea_003 (unguided) | 3 | 46312 | 46312 | gen_002 |
| idea_001 + idea_009 | 6 | 44114 | 44117 | gen_002 |
| idea_001 + idea_006 (hamming) | 2 | 46312 | 46312 | gen_002 |
| idea_001 + idea_004 + idea_003 | 1 | 46312 | 46312 | gen_001 |
| idea_002 (debunked) | 1 | 50474 | 50474 | gen_001 |

## Individual Idea Coverage

| Idea | Central Uses | Peripheral Uses | Best Score | Status |
|------|-------------|----------------|------------|--------|
| idea_001 (basic cancellation) | 16 | 1 | 46312 | established |
| idea_002 (X.Y.-X heuristic) | 1 | 0 | 50474 | debunked |
| idea_003 (predictor-guided beam) | 0 | 3 | 46312 | active (pipeline confirmed, untrained) |
| idea_004 (MITM) | 0 | 1 | 46312 | active (limited depth) |
| idea_005 (identity discovery) | 0 | 6 | 44114 | established |
| idea_006 (hamming predictor) | 0 | 2 | 46312 | DEBUNKED |
| idea_007 (corner PDB) | 1 | 0 | 46312 | active (invalid assumptions) |
| idea_008 (trained MLP predictor) | 0 | 0 | — | active (never tested) |
| idea_009 (empirical algebraic compression) | 6 | 0 | 44114 | active |

## Score Progression

| Solution | Score | compression_ratio | dominant_technique |
|----------|-------|-------------------|-------------------|
| gen002_explore_2_sol01 | 44114 | 0.8723 | Empirical algebraic identities |
| gen002_explore_2_sol07 | 44114 | 0.8723 | Span-6 pattern extension |
| gen002_explore_2_sol08 | 44114 | 0.8723 | Bucket-aware compression |
| gen002_explore_2_sol02 | 44118 | 0.8724 | Systematic commutator enumeration |
| gen002_explore_2_sol03 | 44118 | 0.8724 | Combined systematic + empirical |
| gen002_explore_2_sol05 | 44118 | 0.8724 | Systematic rules, move-list |
| gen001_explore_1_sol01 | 46312 | 0.9158 | MITM + cancellation |
| gen001_explore_1_sol05 | 46312 | 0.9158 | Beam search + cancellation |
| gen002_exploit_1_sol02 | 46312 | 0.9158 | Hamming-guided beam |
| gen002_explore_1_sol03 | 46312 | 0.9158 | Enhanced compression + beam |
| gen002_explore_1_sol04 | 46312 | 0.9158 | Enhanced compression + timed beam |

**Sample submission baseline:** 50572 (compression_ratio=1.0)
**Target:** 15000 (compression_ratio≈0.30)
**Kaggle top-3 equivalent:** ~8050 (compression_ratio≈0.16)
**gen_002 best:** 44114 (compression_ratio=0.8723)

## Unexplored Regions (High Priority for Gen 3)

- **idea_008 (trained MLP predictor)**: Never tested end-to-end. CRITICAL.
- **idea_003 + idea_008 combinations**: Predictor-guided beam with trained model
- **Beam search after identity compression**: Use empirical identities to get a good
  starting path, then beam search to improve further
- **Combination approach**: Identity compression for baseline, then trained-predictor
  beam search for hard/very_hard buckets
