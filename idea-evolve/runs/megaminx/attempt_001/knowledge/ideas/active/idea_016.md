---
type: idea
id: idea_016
name: Path-intermediate states as deep training data
lifecycle: active
confidence: 0.6
first_seen: gen_004
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: []
contradicted_by: []
related_ideas: [idea_010, idea_008, idea_014]
cluster: search_algorithms
tags: [training_data, deep_training, path_intermediates, compressed_paths]
---

# Path-Intermediate States as Deep Training Data

## Summary

Instead of training on BFS data (depth 0-6 only, idea_010) or random walks (depth 0-49),
extract intermediate states from the compressed solution paths as training data. Each
compressed path spans depth 0 to ~100-888, providing states at EVERY intermediate depth
with approximate distance labels (remaining path length to solved). This gives training
data coverage across the FULL depth range of the proxy puzzles, including the critical
hard (depth 101-300) and very_hard (depth 501-1000) buckets.

## Confidence Note

Confidence reduced from 0.7 to 0.6 by consistency reviewer gen004. This idea has NOT been
implemented in any solution. gen003 explore_2 tried a similar approach with the raw integer
MLP and reported loss ~6000 (useless), but that failure is attributable to the wrong
architecture, not the data. With correct architecture (MlpModel one-hot or embedding MLP),
results should improve dramatically. However, the approximate nature of the distance labels
(compressed paths ≠ optimal paths) introduces an unknown amount of noise. Until tested with
correct architecture, confidence should remain moderate.

## How It Works

1. For each of the 101 proxy puzzles, take the compressed path (from idea_009 compression)
2. Walk the path forward, recording the state at each step
3. Distance label = `compressed_path_length - current_step` (remaining moves to solved)
4. Each path of length L produces L training samples at depths 1 through L
5. Total: ~44,000 training samples covering depths 1-888

## gen003 Failure Context

gen003 explore_2 tried training on path intermediate states with the raw integer MLP.
Loss was ~6000 (useless). This failure is now understood as a consequence of the wrong
model architecture (raw integer encoding for categorical permutation data, see pattern_006).
The data itself is sound — the architecture couldn't learn from it. This experiment MUST be
re-run with MlpModel (idea_014) or embedding (idea_011) before drawing conclusions about
the data's viability.

## Advantages Over Existing Training Data Sources

- **BFS data (idea_010):** Only covers depths 0-6. Predictor trained on this predicts every
  deep state as ~4 (exploit_1 confirmed). Useless for hard/very_hard puzzles.
- **Random walks:** Covers depths 0-49 (at width=50k). Noisy labels (random walks overestimate
  distance). Still doesn't reach hard/very_hard depth range.
- **Path intermediates:** Covers depths 1-888 (full range). Labels are approximate (compressed
  paths are not optimal) but correlate well with true distance. Each sample is on the actual
  solution trajectory.

## Why Labels Are Approximate

Compressed paths are NOT optimal — they're shortened by algebraic compression but may still be
far from optimal. A compressed path of length 100 may have an optimal path of length 30. The
distance labels are therefore UPPER BOUNDS on true distance. However, for predictor training,
having approximately-correct rankings across the full depth range is far more valuable than
exact labels at only depth 0-6.

## Risk

The approximate labels may introduce bias — the predictor learns compressed-path distance,
not true optimal distance. For beam search guidance, this may still be sufficient as long
as the predictor correctly ranks states by approximate distance. Testing with correct
architecture is needed.
