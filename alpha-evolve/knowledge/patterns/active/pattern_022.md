---
type: pattern
id: pattern_022
name: "Top-K screening enables 50x speedup for coordinate descent at N=30k"
lifecycle: active
confidence: 0.8
first_seen: generation_10
last_updated: generation_10
evidence: [gen010_exploit_1_sol01, gen010_explore_2_sol01]
related_ideas: [idea_019]
tags: [coordinate-descent, screening, speedup, top-K, engineering, fast-check]
---

Instead of computing full O(M_fft) max of autoconvolution for each trial delta
(the bottleneck at N=30k), only check the top K autoconvolution positions. Two
independent implementations confirm the approach:

**exploit_1 (Top-K=30 screening):**
- Check only K=30 highest autoconvolution positions per trial
- If screening max already ≥ best_C, reject immediately (no false negatives guaranteed)
- If screening suggests improvement, do full incremental update to verify
- Speedup: ~50x (6-12s/round vs ~450s/round naive)
- Enabled 71 rounds in a single session (previously 1-2 rounds)

**explore_2 (fast_check with high-positions):**
- Precompute W≈6760 positions where autoconv is within 1e-7 of max
- For k-element moves, compute predicted new autoconv at these positions only: O(W×k)
- 200k triplet trials at 3666 trials/s — 100% correctly classified as non-improving
- Ultra-fine CD with fast_check pre-filter + exact verify for candidates

**Key property:** Both methods guarantee no false negatives. A rejection at the
screening stage means the move truly cannot improve C. Only potential improvements
need expensive exact verification.

**Implication for gen 11:** All CD implementations should use screening. The choice
of K (30 vs 6760) trades speed vs false-positive rate. K=30 is faster but may
have more false positives requiring verification.
