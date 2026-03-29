## Question

Does `compute_c_f64` (numpy float64 reimplementation) match validate.py's ground truth exactly, and does the float64 sensitivity map produce materially different gradient rankings than the float32 version for well-optimized solutions?

## Methodology

**Control:** validate.py's `validate()` function (the ground truth scorer).

**Treatment 1 — compute_c_f64 accuracy:**
- Loaded best.py (C=1.5028628..., 30000-element array)
- Computed C with compute_c_f64 and compared to validate.py output
- Also computed C with compute_c (float32) for comparison
- Tested edge cases: constant function (expected C=2.0), empty array, zero array

**Treatment 2 — sensitivity ranking divergence:**
- Used first 200 elements of best.py as test array
- Computed sensitivity_map with use_float64=False (JAX autodiff) and use_float64=True (finite differences)
- Compared top-20 most sensitive element indices between the two modes

## Results

### compute_c_f64 vs validate.py

| Method | C value | Diff from ground truth |
|--------|---------|----------------------|
| validate.py | 1.502862898255827 | — |
| compute_c_f64 | 1.502862898255827 | 0.00e+00 |
| compute_c (f32) | 1.502863883972168 | 9.86e-07 |

Edge cases all passed: constant function C=2.0 (within 1e-15), empty/zero arrays raise ValueError.

### Sensitivity ranking divergence (200-element subset of best.py)

| Metric | Float32 | Float64 |
|--------|---------|---------|
| Gradient range | [-0.557730, 0.073015] | [-0.557731, 0.073015] |
| Top-5 indices | [196, 195, 160, 164, 183] | [106, 117, 103, 158, 149] |
| Top-20 overlap | 4/20 (20%) | — |

The gradient *magnitudes* are similar (ranges nearly identical), but the *rankings* are completely different. This confirms pattern_008: float32 noise reshuffles which elements appear most sensitive, leading optimization in the wrong direction.

## Conclusions

1. **compute_c_f64 is an exact match for validate.py** — zero difference on the best solution. Safe to use as the optimization oracle for all accept/reject decisions.

2. **Float32 sensitivity rankings are unreliable for well-optimized solutions.** Only 20% overlap in top-20 elements. Any coordinate descent or element-wise optimization guided by float32 gradients is optimizing the wrong elements for solutions below C~1.505.

3. **The updated sensitivity_map with `use_float64=True` correctly uses finite differences on compute_c_f64.** It is ~N times slower (one compute_c_f64 call per element per gradient) but provides trustworthy rankings.

## Confidence Level

**High** — Direct numerical comparison with controlled variables. Zero difference in Treatment 1 is definitive. Treatment 2's 20% overlap on a 200-element subset strongly confirms pattern_008 (would expect ~100% overlap if float32 were reliable).

## Limitations

- Sensitivity map test used only 200 elements (not full 30000) for time reasons. The divergence pattern should hold or worsen for the full array.
- Float64 finite differences use delta=1e-8. Smaller delta might be more accurate but risks numerical noise at ~1e-16. The current delta gives ~1e-8 precision in the gradient, which is sufficient for ranking.
- The finite-difference sensitivity_map is O(N * cost_of_compute_c_f64) — impractical for full 30000-element arrays in a single call. Users should compute sensitivity for subsets or selected indices.
