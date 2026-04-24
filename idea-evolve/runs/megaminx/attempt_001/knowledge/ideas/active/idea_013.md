---
type: idea
id: idea_013
name: Combined recipe — BFS training + embedding MLP + MITM beam search
lifecycle: active
confidence: 0.35
first_seen: gen_003
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen003_research_1, gen004_exploit_1_sol01]
contradicted_by: [gen004_exploit_1_sol01]
related_ideas: [idea_010, idea_011, idea_012, idea_008, idea_009, idea_016, idea_014, idea_015]
cluster: search_algorithms
tags: [combined_recipe, BFS, embedding, MITM, beam_search, end_to_end, tested]
---

# Combined Recipe — BFS Training + Embedding MLP + MITM Beam Search

## Summary

**TESTED END-TO-END (gen004 exploit_1):** The combined recipe (BFS MITM + embedding MLP
trained on random walks + beam search + compression fallback) achieved **44111** — WORSE
than gen003's 44094. The recipe works mechanically but produces marginal-to-negligible
improvement due to two critical limitations: (1) training data depth is too shallow for
deep puzzles, (2) beam width too small (4096 vs competitive 65536+).

The original recipe as specified is insufficient. This idea serves as a BASELINE for
the improved recipe (see Open Items below).

## Gen004 Test Results

**exploit_1/sol01:**
- Pipeline: compression (336 rules) → BFS depth 6 (MITM) → embedding MLP (random walks,
  depth 50, 2.3M samples, 15 epochs) → beam search (beam_width=4096, max_steps=60)
- Score: **44111** (compression alone = 44114, best prior = 44094 gen003)
- Only 2/101 puzzles improved by beam search; 3 total moves saved
- Regression vs gen003 best by 17 moves
- Training loss: 2.83 (embedding MLP on random walks depth 50)

**Key failure mode:** Predictor trained on depth ≤50 data predicts deep states incorrectly.
Very_hard puzzles (depth 501–1000) get no benefit from beam search guidance.

## What Was Confirmed Working

- The end-to-end pipeline (BFS → train → beam search → fallback) executes without errors.
- Embedding MLP trains on random walks in ~44s (faster than estimated 60–120s).
- MITM backstop via `bfs_result_for_mitm` integrates correctly.
- Compression fallback guarantees no regression below 44114 (worst case).

## What Failed

- Score improvement: only 3 moves over 101 puzzles (-0.007%).
- BFS-only training data produces useless predictor for deep states (see idea_010 update).
- Random walk depth 50 insufficient for hard/very_hard buckets.
- Beam width 4096 is 16× too small for competitive results (pattern_009).

## Revised Estimate

- **Conservative:** ~44000–44114 (as tested)
- **With deep training data (idea_016) + beam_width=65536:** ~38000–43000 (hypothetical)
- **Kaggle top-3 approach (optimistic):** ~8050 (requires full recipe from CayleyPy paper)

## The Successor Recipe

The recipe must be updated with three changes before it can make meaningful progress:

1. **Training data depth** — use path-intermediate states (idea_016) for depths 1–888,
   supplemented by BFS data for depths 0–5.
2. **Beam width** — use beam_width=65536 with batch_size=2048 (pattern_009: log-linear scaling).
3. **Model** — use CayleyPy's built-in MlpModel with one-hot encoding (idea_014), proven
   architecture from the library's own team.

The MITM backstop remains valuable (idea_012). Non-backtracking (idea_015) may replace
MITM if the two are mutually exclusive and non-backtracking provides more benefit.

## Priority

Now that the basic recipe has been tested, the priority shifts to idea_016 (deep training data).
Without deep training data, no combination of model architecture or beam width will help
very_hard puzzles (74.8% of score).
