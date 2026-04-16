# Observations — Explore Agent gen001_explore_2

## Approaches Tried

### 1. Basic Greedy Cancellation (sol01.py)
- **Approach**: Remove X.-X inverse pairs left-to-right in a single pass
- **Result**: fitness=46312, compression_ratio=0.9158, improved_count=98/101
- **Key insight**: Single-pass greedy cancellation already achieves ~8.4% compression

### 2. Iterative Bidirectional Cancellation (sol02.py)
- **Approach**: Iterate left-to-right + right-to-left cancellation until fixed point
- **Result**: Same as sol01 (46312)
- **Finding**: Iterative cancellation doesn't improve over single-pass for most paths

### 3. Midpoint Repair (sol03.py)
- **Approach**: Split path at midpoint, try random bridges from midpoint to solved
- **Result**: Same as sol01 (46312)
- **Finding**: Random midpoint bridges don't find shorter paths than cancellation

### 4. N-gram Pattern Compression (sol04.py) — FAILED
- **Approach**: Learn common X.Y.-X patterns and replace with shorter equivalents
- **Result**: fitness=50474 (WORSE than sample_submission 50572)
- **Key insight**: X.Y.-X is NOT equal to Y in Megaminx Cayley graph. The heuristic was mathematically invalid.

### 5. Beam Search + Cancellation (sol05.py)
- **Approach**: Beam search for shallow puzzles + local shortening for all
- **Result**: Same as sol01 (46312)
- **Finding**: Beam search doesn't find shorter paths than cancellation for these depths

## Key Findings

1. **Cancellation is the winning approach**: X.-X inverse pair removal achieves ~8.4% compression on sample_submission paths. This is the free lunch.

2. **Random walks have local structure**: The compression comes from the fact that random walks frequently backtrack, creating X.-X pairs.

3. **Cancellations chain**: Removing one pair can create new cancellations. Iterative cancellation handles this.

4. **Structural patterns beyond X.-X don't help**: Attempts to find commutator-like patterns (X.Y.-X ≈ Y) fail because Megaminx isn't commutative.

5. **Beam search doesn't help at these depths**: For ids 1-1000, the beam search found paths similar in length to the sample_submission (which makes sense since sample_submission IS the inverse of the scramble).

## Bucket Analysis (sol01 best result)

| Bucket | Count | Fitness | Avg/Puzzle | Observation |
|--------|-------|---------|------------|-------------|
| special (id=0) | 1 | 72 | 72 | 72-move outlier |
| short (1-25) | 2 | 30 | 15 | Very compressed |
| medium (26-100) | 8 | 474 | 59.25 | Good compression |
| hard (101-500) | 40 | 11102 | 277.55 | Moderate compression |
| very_hard (501-1000) | 50 | 34634 | 692.68 | Dominates score; hard to compress further |

## Unexplored Directions

1. **Macro-move precomputation**: Precompute short sequences (3-8 moves) with clean semantics and use them as high-level moves. This could provide more aggressive compression than local search.

2. **Pattern databases**: Precompute exact distances for subsets of the state space (e.g., corners only). Use as heuristic for A*.

3. **Meet-in-the-middle**: Split the problem at midpoint depth and meet in the middle. Could halve the depth requirement.

4. **Commutator analysis**: Find group-theoretic identities specific to Megaminx's Cayley graph structure.

5. **Learned predictors**: Train a neural network to predict distance from solved state. Use in beam search. This is the approach Kaggle top competitors used.

## What Would Have Changed the Outcome

- If Megaminx had commutator-like identities (A.B.A^{-1}.B^{-1} = identity), we could compress more aggressively
- If the state space had more structure exploitable by local search, we'd see better results
- The ~8.4% compression is likely near the theoretical limit for pure cancellation approaches