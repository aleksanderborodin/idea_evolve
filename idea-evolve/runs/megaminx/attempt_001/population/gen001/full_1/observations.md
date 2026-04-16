# Observations — gen001 full_1

## Approach: depth-aware beam search + move cancellation

### What worked
- **Move cancellation** (removing X.-X inverse pairs from sample_submission paths): free improvement from 50572 → ~46000. Applied universally as fallback.
- **Per-bucket beam params**: scaling beam width and max_steps by depth bucket improved shallow/medium puzzles.
- **Sample_submission fallback**: guaranteed validity — is_valid=1 maintained throughout.

### What didn't work
- **Hard bucket saturation**: beam=2048/200 is the ceiling for hard puzzles. Trying beam=3072 or more steps didn't improve the hard bucket further.
- **Very_hard beam attempts**: even aggressive beam params (beam=512, steps=200) couldn't crack any very_hard puzzle. Unguided search is insufficient for depth 500+.
- **Multiple restarts**: didn't try due to time constraints, but beam search is deterministic per initial state so restarts may not help.

### Score breakdown (best working eval: fitness=46312)
| Bucket | Count | Fitness | Solved |
|--------|-------|---------|--------|
| special | 1 | 72 | 1 |
| short | 2 | 30 | 2 |
| medium | 8 | 474 | 8 |
| hard | 40 | 11102 | 40 |
| very_hard | 50 | 34634 | 50 |

**Leverage point**: very_hard bucket (76.7% of score) — requires a fundamentally different approach.

### Key insight
The unguided beam search ceiling is ~46000 proxy fitness. To reach target 15000 requires a learned predictor. Top Kaggle solutions used custom-trained ML models on random-walk data. This is the clear next step.

### Experiments to request
1. Train a distance predictor: generate (state, distance) pairs via random walks, train MLP to predict distance, use in beam search heuristic
2. Investigate whether the 50 very_hard puzzles (depth 500-1000) have any structure exploitable by partial-search or macro-move approaches
3. Try meet-in-the-middle for hard bucket puzzles (depth 101-500) — halving the depth requirement may enable solutions