# Solution-Idea Map — Gen 001

## Solution gen001_explore_1_sol01 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (basic X.-X cancellation)
- **Peripheral:** idea_004 (MITM for special bucket — attempted but didn't improve)
- **Novel elements:** None beyond basic cancellation

## Solution gen001_explore_1_sol02 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (basic X.-X cancellation)
- **Peripheral:** None
- **Novel elements:** None — identical to sol01

## Solution gen001_explore_1_sol03 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (basic X.-X cancellation)
- **Peripheral:** None
- **Novel elements:** None — identical to sol01

## Solution gen001_explore_1_sol04 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (basic X.-X cancellation)
- **Peripheral:** None
- **Novel elements:** None — identical to sol01

## Solution gen001_explore_1_sol05 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (basic X.-X cancellation)
- **Peripheral:** None
- **Novel elements:** None — identical to sol01

## Solution gen001_explore_2_sol01 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (greedy left-to-right cancellation)
- **Peripheral:** None
- **Novel elements:** None

## Solution gen001_explore_2_sol02 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (iterative bidirectional cancellation)
- **Peripheral:** None
- **Novel elements:** Confirmed iterative cancellation yields no improvement over greedy

## Solution gen001_explore_2_sol03 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (midpoint repair with random bridges)
- **Peripheral:** None
- **Novel elements:** Confirmed midpoint repair yields no improvement

## Solution gen001_explore_2_sol04 (score: 50474, compression_ratio: 0.9981)
- **Central:** idea_002 (X.Y.-X commutator heuristic)
- **Peripheral:** idea_001 (fallback to cancellation)
- **Novel elements:** idea_002 — X.Y.-X heuristic FAILED. This solution is invalid (worse than baseline). Compression ratio 0.9981 shows it barely compressed. Debunked idea_002.

## Solution gen001_explore_2_sol05 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (beam search + local shortening)
- **Peripheral:** idea_003 (beam search — used but didn't beat cancellation)
- **Novel elements:** Confirmed unguided beam search adds nothing over cancellation

## Solution gen001_full_1_sol01 (score: 46312, compression_ratio: 0.9158)
- **Central:** idea_001 (move cancellation as baseline)
- **Peripheral:** idea_003 (depth-aware beam search per bucket — didn't beat compression)
- **Novel elements:** Depth-aware beam params by bucket (short: beam=512/steps=50, medium: 1024/120, hard: 2048/200, very_hard: 512/200). Confirmed beam search ceiling.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total solutions | 11 |
| Unique approaches | 4 |
| Best score | 46312 |
| Worst valid score | 46312 |
| Failed solutions | 1 (explore_2_sol04, invalid) |
| Solutions using idea_001 | 11 |
| Solutions using idea_003 (beam) | 2 |
| Solutions using idea_004 (MITM) | 1 |
| Solutions using idea_002 | 1 (debunked) |