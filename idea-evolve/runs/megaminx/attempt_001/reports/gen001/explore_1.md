# Debrief Report — Explore Agent gen001_explore_1

## 1. What did you try?

### Approach 1: Naive MITM BFS
- Ran bidirectional BFS from initial state and solved state simultaneously
- Tried depth limits 5-8 per side (combined 10-16)
- Added beam pruning to limit states per level
- **Result**: Did not find paths shorter than compressed sample. MITM grows as O(24^depth) which became intractable quickly.

### Approach 2: Beam Search with cayleypy
- Used `cayleypy_beam_solver` with beam_width 1000-4000 and max_steps 150-300
- Multi-restart approach with different parameters
- **Result**: Beam search did not beat compressed sample. Either returned None (not solved within budget) or returned longer paths than compressed sample.

### Approach 3: Move Cancellation Compression (WINNER)
- Key insight: sample_submission paths are exact inverses of random walks
- Random walks have internal cancellations (X.-X patterns)
- Iteratively remove adjacent inverse pairs
- **Result**: 46312 vs 50572 baseline (8.4% improvement). This is the best approach.

## 2. What information did you lack?

- **No visibility into beam_search internals**: I couldn't see why beam search was failing to find shorter paths. Was it returning None? Returning longer paths? Without logging inside the solution, it's hard to diagnose.
- **No pattern database**: A precomputed distance database for corner-only configurations could serve as an admissible heuristic for IDA*.
- **No understanding of cancellation patterns**: I don't know if there are systematic longer-range cancellations in the random walks that could be exploited.

## 3. What given facts might be wrong or outdated?

The initial_ideas.md mentions:
- "meet_in_the_middle" is active with confidence medium
- "predictor_training" is active

Both are listed as promising approaches, but:
- MITM is intractable without strong pruning for depth > 10 on Megaminx due to branching factor 24
- Predictor training is off-limits for this generation per the directive

The "cayleypy_beam_solver" helper works, but unguided beam search isn't strong enough to beat compression.

## 4. Was the State of Affairs accurate?

Yes. The state_of_affairs.md correctly noted "everything is open" for generation 1. The initial ideas and facts provided good context.

## 5. What would you do differently with more or different context?

1. **Focus on compression improvements**: The 8.4% from compression is the ceiling without smarter search. Try to find non-adjacent cancellations.

2. **Implement IDA* with corner-only pattern database**: This could find truly optimal paths for depth < 20 and would be a real improvement over compression.

3. **Try Kociemba-style two-phase**: Reduce to a subgroup first, then solve within subgroup. This could dramatically reduce branching factor.

4. **Understand why beam search fails**: Add instrumentation to see what beam search returns vs what compression produces.

## 6. Specific experiments to run

1. **Compression ceiling**: How much of the sample_submission path is cancellable? Run compression on all 1001 puzzles and see max/average compression per depth bucket.

2. **IDA* with pattern database**: Precompute exact distances for corner configurations (20 corners, orientations). Use as h-value in IDA*.

3. **Long-range cancellation search**: Find cancellation patterns that span > 2 moves (e.g., X.Y.-X.-Y).

4. **Beam search vs depth study**: For a set of depth-N puzzles, vary beam_width and max_steps to find the minimum beam needed to solve each depth.

## 7. What surprised you?

- **Compression was the main win**: I expected MITM or beam search to find genuinely shorter paths, but compression alone outperformed all search approaches.
- **Beam search was ineffective**: Even with beam_width=4000 and max_steps=300, beam search couldn't find shorter paths than compression for medium puzzles.
- **MITM explosion**: Even with depth 6 per side, the state space was millions of states. Depth 8 would be billions.

## 8. Helper tools feedback

- `helpers.core` functions worked correctly
- `cayleypy_beam_solver` exists and runs but isn't strong enough without a predictor
- No bugs or misleading docstrings found

## 9. Time budget

- Had enough time to explore multiple approaches
- Would have liked more time to:
  - Implement IDA* with pattern database
  - Add instrumentation to understand beam search failures
  - Try more aggressive compression patterns