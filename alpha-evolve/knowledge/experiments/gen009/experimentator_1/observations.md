# Observations — gen009 experimentator_1

## Key discovery: Window-based batch prediction

For N=30000, the window-based approach (evaluate only at tight indices ±300 positions)
is ~46x faster than sequential incremental_update. Machine precision for |delta| < 1e-3.

**Why FFT batching fails at scale:** numpy's rfft on a (100, 60000) matrix is memory-bandwidth
limited — the 48MB matrix saturates RAM throughput (490ms for rfft+irfft pair). The window
approach uses a (100, 4, 401) intermediate array = 1.3MB that fits in CPU L2 cache.

## Tight indices at N=30000

The current best solution (C = 1.5028628684790137) has only 1 index at epsilon_rel=1e-5
that qualifies as "tight". This means the autoconvolution has a single sharp peak.
The window of ±300 around this covers 601 positions out of M=60000.

This is consistent with the gen008 observation that quadruplet improvements are very small
(delta_C = -4e-10) — the function is extremely well-optimized with a single binding constraint.

## Speedup degrades at small N

At N=1000: only 3x speedup. The fixed overhead of building window_idx, np.unique, etc.
dominates when both window and sequential are fast. Helper is most valuable at N ≥ 5000.

## Error at N=1000 is 8.7e-12, not machine precision

At small N, there are more autoconvolution peaks and the window may occasionally miss one
that shifts into the top position. Still excellent accuracy (8.7e-12 << 1e-8 threshold).

## Production helper deployed

`output/helpers/batch_trial_evaluator.py` — ready for deployment to `problem/helpers/`.
Contains `batch_predict_c` (window-based, fast, recommended) and documents the FFT variant
for reference.

## Recommendation for agents

The filtering workflow enabled by this helper:
1. Sample K=1000 candidates (triplets or quadruplets) in Python
2. Call batch_predict_c → get 1000 predicted C values in ~130ms
3. Keep top 5% (50 candidates)
4. Verify exactly with incremental_update
5. Accept improvements

This replaces the Python loop at ~112 trials/s with ~7500 predictions/s + exact verification.
Net: 10-50x more trials per wall-clock second.
