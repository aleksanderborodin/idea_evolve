# Observations — full_1, Generation 7

## Summary

LP-based refinement proof-of-concept and extended coordinate descent on TTT-Discover 30k array.

**Best result: C = 1.5028628712540075 (sol04.py) — improvement of 1.217e-9 over gen6 best**

## Approaches Tried

### sol01.py — LP at N=2000, upsample to N=30k
- Downsampled 30k array to N=2000 (C went from 1.502 → 1.721 at lower resolution)
- LP at N=2000: SUCCEEDED (t = -5.5e-5, improved N=2000 C from 1.721 → 1.710 with alpha=0.003)
- Upsampled LP direction to 30k: ALL step sizes worsened C (even alpha=1e-6 gave 1.503+)
- **Conclusion**: LP is resolution-sensitive. N=2000 direction doesn't transfer to N=30k.

### sol02.py — LP directly at N=30k, 1 tight constraint
- Used vectorized numpy construction (NOT Python loop over N) — built (1, 30000) in 0.001s
- LP solved in 0.16s, t = -5.0e-5 (descent direction found!)
- But line search: ALL alphas (1e-6 to 1.0) made C worse
- Root cause: delta_f max=244 — LP pushes mass to extreme values, other autoconv peaks form
- **Conclusion**: 1 tight constraint is insufficient — LP direction is unbounded

### sol03.py — LP at N=30k with bounded delta_f, multiple epsilon values
- Added per-element upper bound on delta_f (0.0001×max_f, 0.001×max_f, etc.)
- With max_delta=9.11e-05: t=-2.99e-6, direction is bounded (||d||=0.22)
- Line search still failed: alpha=1e-3 gives C=1.502901 (worse)
- Tried 138 tight constraints (eps=1e-8): t=-1.57e-5, direction still worsens things
- **Key finding**: autoconv plateau at N=30k has ~6500 near-maximum points (eps=1e-7)
  This means any LP with < 6500 constraints lets other points become the new maximum
- Building (6500, 30000) constraint matrix = 1.5GB — essentially the gen6 OOM failure

### sol04.py — Extended coordinate descent
- Resumed coordinate descent from gen6 best (C=1.502862872471)
- Used O(N) incremental autoconv update via np.roll (same as gen6 exploit_1)
- Delta candidates: absolute [1e-9 to 5e-4] at 18 values, both signs
- Round 1: 257 improvements, C → 1.502862871254, took 130s
- Round 2: 0 improvements (converged)
- **Result: C = 1.502862871254, improvement = 1.217e-9 ✓**

## Key Findings

### LP plateau problem
The autoconvolution of the 30k array has an extremely flat region near the max:
- eps=0: 1 point exactly at max
- eps=1e-8: 138 near-max points
- eps=1e-7: **6541 near-max points**
- eps=1e-6: 14052 near-max points

This means LP can only work if we include all ~6500 tight constraints, requiring a (6500 × 30000) matrix = 1.5GB. That's the same scaling failure as gen6.

### LP proof-of-concept at N=2000 succeeded
The LP approach IS mathematically valid: at N=2000, it improved C from 1.721 to 1.710 (improvement of 0.011 = 0.6%). This proves the formulation works. The issue is only in translating between resolutions.

### Coordinate descent still improving
After gen6's 14373 improvements, we found 257 more. The solution is approaching but has NOT reached the coordinate-wise optimum. Diminishing returns: 1800/round → 257/round.

## Performance Numbers
- LP solve at N=30k, 1 constraint: 0.16s
- LP solve at N=30k, 138 constraints: 8.17s
- Constraint matrix construction (138, 30000): trivial (< 0.01s)
- Coordinate descent round (25144 elements, 18 deltas × 2 signs): ~130s

## Directions for Next Agents

1. **More coordinate descent with proportional deltas**: Use relative deltas (1% to 100% of f[idx]) in addition to absolute. Gen6 found they work well.

2. **Triplet perturbation**: d1+d2+d3=0 with 3 elements. Pairs found almost nothing (1 improvement). Triplets are untested.

3. **Different starting point**: AlphaEvolve 1319-element array (C≈1.5053) — coordinate descent on different basin.

4. **LP at intermediate resolution N=5000-10000**: The N=2000 plateau might have fewer tight constraints. Test if the LP direction transfers better from N=5000 than N=2000.

5. **Exploit the flat plateau differently**: The autoconvolution plateau being so flat means many function variations give essentially the same C. This suggests a large flat region of near-optimal solutions — maybe some are more improvable than the current one.
