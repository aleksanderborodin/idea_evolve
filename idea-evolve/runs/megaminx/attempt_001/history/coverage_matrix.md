# Coverage Matrix — Gen 004

*Scale rule: cap to top 30 most-used ideas. Sparse format — only rows with actual scores.*

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_001 (X.-X cancellation) alone | 18 | 46312 | 46312 | gen_001 |
| idea_001 + idea_004 (manual MITM attempt) | 3 | 46312 | 46312 | gen_001 |
| idea_005 + idea_009 (336 rules) | 1 | 44114 | 44114 | gen_002 |
| idea_005 + idea_009 (432 rules) | 1 | 44118 | 44118 | gen_002 |
| idea_005 + idea_009 (combined rules) | 1 | 44118 | 44118 | gen_002 |
| idea_005 + idea_009 (systematic rules) | 2 | 44114 | 44116 | gen_002 |
| idea_009 + idea_008 (compression + raw-integer predictor) | 1 | 44094 | 44094 | gen_003 |
| idea_009 + idea_008 + idea_011 + idea_012 (combined recipe, embedding MLP, RW depth 50) | 1 | 44111 | 44111 | gen_004 |

## Ideas Never Used as Central

| Idea | Status | Reason |
|------|--------|--------|
| idea_010 (BFS training data, sole source) | NEVER | Empirically useless for deep states (gen004 BFS-only test) |
| idea_013 (combined recipe as described) | TESTED but incomplete | 44111 — recipe works mechanically but training data depth bottleneck |
| idea_014 (MlpModel one-hot) | NEVER | Identified gen004, never tried in solution |
| idea_015 (non-backtracking beam) | NEVER | Identified gen004, never tried in solution |
| idea_016 (path-intermediate training) | NEVER | Identified gen004, TOP PRIORITY for gen005 |
| idea_003 (predictor beam concept) | peripheral only | Used in gen003–004 as peripheral to idea_008 |
| idea_004 (manual MITM) | 3× | Only fallback to compression, superseded by idea_012 |
| idea_011 (embedding MLP) | 1× (exploit_1) | Tied with idea_008 — same result: marginal |
| idea_012 (built-in MITM) | 1× (exploit_1) | Combined with recipe but benefit not isolable |

## Coverage Gaps (Unexplored Combinations)

1. **idea_016 + idea_014 + large beam width** — the updated recipe. Never tested.
2. **idea_015 + large beam width** — non-backtracking at beam_width=65536. Never tested.
3. **idea_016 + idea_015** — deep training data + non-backtracking (no MITM).
4. **Long random walks (depth 200–500) + idea_014** — alternative deep training data.
5. **idea_009 + idea_016 + idea_014 + idea_012 + beam_width=65536** — full recipe v2.

## Score Distribution by Approach

| Approach | Solutions | Score Range | Notes |
|----------|-----------|-------------|-------|
| Compression only (≤ idea_009) | 17+ | 44114–46312 | Ceiling at 44114, confirmed |
| Compression + shallow predictor | 2 | 44094–44111 | Marginal: 3–20 moves saved |
| Any search without predictor | 10+ | 46312 | Unguided search = no benefit |
| Deep training data approaches | 0 | — | Untested (idea_016) |
