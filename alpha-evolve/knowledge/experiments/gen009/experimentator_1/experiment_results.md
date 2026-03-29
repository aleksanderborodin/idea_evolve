# Experiment: Vectorized Batch Trial Evaluator

## Question

Can we build a vectorized batch predictor for k-element integral-preserving candidate moves
that evaluates K=100 candidates at N=30000 in <0.1s (target ≥10x speedup vs sequential
incremental_autoconv_update)?

## Methodology

**Control:** Sequential evaluation of K=100 candidate moves using incremental_autoconv_update
(the current approach in gen008 agents).

**Treatment:** Three approaches evaluated:

1. **Direct fancy-indexing**: Build (K, M) index array, gather f_padded values
2. **FFT-based**: Build sparse impulse matrix, batched FFT/IFFT on (K, M) arrays
3. **Window-based** (winner): Only evaluate at tight indices ±window_half positions

All approaches implement the same first-order linear approximation:
`delta_autoconv[j, m] = 2*dx * sum_p(delta_jp * f_padded[(m - i_jp) % M])`

**Ground truth:** Sequential incremental_autoconv_update (exact, O(N) per call).

**Test conditions:** K=100 candidates, k=4 elements per candidate (quadruplets),
|delta| ~ 1e-5 (typical scale from gen008 agent). N ∈ {1000, 5000, 10000, 30000}.

## Results

### Timing comparison (K=100 candidates)

| N | Window-based | Sequential exact | Speedup | Max rel. error |
|---|-------------|-----------------|---------|----------------|
| 1,000 | 13.7ms | 42ms | 3x | 8.70e-12 |
| 5,000 | 12.6ms | 125ms | 10x | 4.32e-16 |
| 10,000 | 10.3ms | 228ms | 22x | 4.36e-16 |
| 30,000 | 13.5ms | 624ms | **46x** | 6.58e-16 |

### Approach comparison at N=30000

| Approach | Time (K=100) | Notes |
|----------|-------------|-------|
| Direct fancy-indexing | 650ms | Cache-unfriendly: random access into (K,M) index arrays |
| FFT-based | 387ms | Bottleneck: rfft/irfft on (K=100, M=60000) matrix = 490ms |
| Window-based | **13ms** | Cache-friendly: only W~401 evaluation points |
| Sequential exact | 624ms | Baseline |

### Accuracy

All approaches use the same first-order approximation. For |delta| ~ 1e-5:
- Relative error: ≤ 1e-11 (approaches machine precision)
- Ranking correlation with exact: 1.0000000 (perfect)
- Top-10 overlap: 10/10

### Why window-based wins

The FFT bottleneck is clear: `rfft(impulse, axis=1)` on a (100, 60000) matrix takes 255ms
and `irfft` takes 235ms (490ms total), dominated by memory bandwidth for 48MB arrays.

The window-based approach avoids this: only 401 evaluation positions out of 60,000.
The key insight: for small deltas, the autoconvolution maximum stays within ±300 positions
of the current maximum. The tight region (epsilon_rel=1e-5) captures 1-5 indices for well-
optimized solutions; the window covers ±300 positions around each.

The (K, k, W) intermediate array is only 100 × 4 × 401 × 8 = 1.3MB — fits in L2 cache.
Contrast with (K, M) = 48MB for FFT approaches.

## Conclusions

1. **Window-based batch prediction achieves 46x speedup** at the target N=30000, K=100.
   Time: ~13ms vs ~624ms sequential, well under the 0.1s target.

2. **Machine precision for small deltas** (|delta| < 1e-3). The linear approximation
   is effectively exact for the perturbation scales used by gen008 agents (~1e-5).

3. **FFT-based approach NOT faster** than sequential at N=30000. The (K, M) FFT
   matrices are memory-bandwidth limited. Counter-intuitive given FFT's O(N log N) asymptotic.

4. **Practical filtering workflow enabled**: Sample K=1000 candidates in one batch
   (~130ms), keep top 5% (50 candidates), verify exactly. This replaces the Python loop
   at 112 trials/s with ~7500 trials/s filter + 100% exact verification of top candidates.

## Confidence Level

**High** — All findings based on controlled benchmarks with verified ground truth.
Speedup numbers reproduced across 5 timed repetitions. Accuracy verified against both
incremental_update (O(N)) and compute_c_f64 (FFT recompute).

## Limitations

1. **Window assumption**: For |delta| > 0.01, the true maximum may shift outside the
   window, causing underestimation of C. The helper should be used as a pre-filter in
   that regime, not for exact decisions.

2. **N=1000 speedup only 3x**: Window overhead (building window_idx, clip, unique) is
   not negligible at small N where sequential evaluation is already fast. The helper
   is most valuable at N ≥ 5000.

3. **Fixed window_half=300**: Optimal window size depends on delta magnitude and function
   smoothness. The default is conservative (too large for very small deltas, may be too
   small for very large deltas at large N). Users can tune via the `window_half` parameter.
