# Debrief Report — experimentator_1, Generation 8

## Deliverables

| Output | Status | Description |
|--------|--------|-------------|
| `output/helpers/coordinate_descent.py` | COMPLETE | Standardized coordinate descent helper with `coordinate_descent_round` and `run_coordinate_descent` |
| `output/helpers/README.md` | COMPLETE | Updated README documenting all 8 helpers (7 existing + coordinate_descent) |
| `output/experiment_results.md` | COMPLETE | Controlled experiment validating correctness and performance |
| `output/sandbox/scripts/test_final.py` | COMPLETE | 6 automated tests, all passing |

## 1. What did you try?

### Attempt 1: Naive full-array candidate evaluation (FAILED — too slow)
- Materialized full autoconv array (length M=60k) for each candidate delta per element
- With 30 candidates × 25k elements × O(60k) per candidate = ~45B operations
- Timed out at 300s without producing any output

### Attempt 2: Vectorized batch evaluation (STILL TOO SLOW)
- Batched all candidates into (n_cand, M_fft) array using numpy broadcasting
- 28.5ms per element → estimated 716s per round at N=30k
- Correct but impractical for production use

### Attempt 3: Hot-set screening without verification (INCORRECT)
- Only evaluated candidates at "hot set" positions (near autoconv max)
- 14k of 60k positions → much faster (~7ms/element)
- BUT: hot set max is a LOWER BOUND on true max
- C increased between rounds on small array test — bug!
- Accepting moves that LOOKED good but were actually worse

### Attempt 4: Hot-set screening with full-max verification (SUCCESS)
- Use hot set to quickly screen all candidates (lower bound on new C)
- If hot-set C suggests improvement, verify with full `np.max` on one candidate
- Correct AND fast: ~6ms/element at N=30k → 147s per round
- All 6 tests pass, verify diff < 1e-13

## 2. What information did I lack?

- **Nothing critical.** The brief was excellent — it specified the exact API, the delta grid, the dependencies, and the testing plan. The exploit_1 report's mention of the "safe set" approach was the key insight for optimization.

## 3. What given facts might be wrong or outdated?

- The current best (gen007/explore_1/sol01.py) is described as near-converged. But coordinate descent found 4027 improvements in one round (C delta -4.75e-10). The "convergence" reports from gen 7 may reflect different delta grids, not true convergence.

## 4. Was the State of Affairs accurate?

Yes. It correctly identified coordinate descent standardization as a key need and the delta grid discrepancy as the root cause of the 40x improvement count difference.

## 5. What would I do differently?

- Start with the hot-set screening approach immediately instead of trying naive/vectorized first. The naive approach was obviously too slow for N=30k but I tested it anyway.
- Add a "fast mode" that skips the full-max verification for elements where the hot-set C is far above current_c (clear no-improve). Currently we always compute hot-set values even when no candidate will help.

## 6. Specific experiments to run

### Experiment A: Optimal hot set epsilon
The epsilon_rel=1e-6 was chosen without systematic study. Test epsilon values from 1e-8 to 1e-3 to find the sweet spot between screening speed and false-negative rate.

### Experiment B: Multi-round coordinate descent on current best
Run 5-10 rounds on gen007/explore_1/sol01.py to find how many improvements total are available and at what C it truly converges.

### Experiment C: Adaptive delta grid
Instead of the fixed grid, try bisection search on the optimal delta magnitude per element. Start with coarse deltas, refine around the best one. May find improvements that the fixed grid misses.

## 7. What surprised me?

- **4027 improvements on the "best" solution.** This was supposed to be well-optimized. The standardized delta grid found significantly more improvements than the ad-hoc implementations in gen 7.
- **The hot-set bug was subtle.** The v1/v2 implementations produced plausible-looking results (C decreased overall) while accepting some worsening moves. Only caught because the small array test had C increase between rounds. The lesson: always verify with the authoritative computation before accepting.
- **Performance was workable.** I expected N=30k to be impractical for per-element coordinate descent. With hot-set screening, 147s/round is viable for exploit agents.

## 8. Helper tools feedback

### `helpers/incremental_autoconv_update.py`
- Correct, well-documented, essential. The O(N) update is the foundation of everything.
- Note: `incremental_update` does NOT modify inputs in-place (returns new array). This is correct for the trial-evaluation pattern (try many deltas, accept one) but requires the caller to manage the accepted update carefully.

### `helpers/compute_c_f64.py`
- Used for final verification. Correct. Essential safety net.

### `helpers/cross_convolution_f64.py`
- `autoconvolve()` used for FFT resync. Correct. Note: the module imports numpy only (no JAX), despite being in a codebase that uses JAX elsewhere. This is intentional and good — avoids JAX initialization overhead for pure numpy workflows.

### No bugs found in any existing helper.

### Missing helper that would help:
- A "safe set max" helper that maintains a sorted index of positions near the autoconv max and provides O(1) max queries after O(N) updates. Would eliminate the O(M) `np.max` call in the verification step, potentially halving runtime.
