# Experimentator 1 — Gen 6 Debrief

## What did I try?

### 1. Created `compute_c_f64` helper
Reimplemented validate.py's FFT-based autoconvolution in a standalone function using numpy float64. The implementation is a near-verbatim copy of validate.py's `validate()` function, returning only the C value (no validity checks beyond input validation).

**Result:** Exact match with validate.py — 0.00e+00 difference on best.py (C=1.502862898255827). Float32 compute_c differs by 9.86e-07.

### 2. Updated `sensitivity.py` with float64 mode
Added `use_float64=True` parameter that switches from JAX autodiff to numpy float64 central finite differences via compute_c_f64. Backward compatible — default behavior unchanged.

**Result:** Confirmed pattern_008. Top-20 most sensitive elements have only 20% overlap between float32 and float64 on a 200-element subset of best.py. The gradient magnitudes are similar but rankings are completely shuffled by float32 noise.

### 3. Updated `README.md`
Complete index of all 5 helpers with precision notes, when-to-use guidance, and import examples.

## What information did I lack?

Nothing — the brief was precise and well-scoped. All necessary files were listed.

## What given facts might be wrong or outdated?

Pattern_008 is confirmed correct and should be promoted to `confirmed` lifecycle.

## Was the State of Affairs accurate?

Yes, for the scope of this task.

## What would I do differently with more or different context?

The float64 sensitivity_map is O(N * compute_c_f64_cost). For 30000-element arrays, computing the full gradient takes ~30000 FFTs. A batched approach (perturb multiple elements simultaneously using linearity properties) could speed this up, but would require careful analysis of whether the C functional allows such shortcuts. Worth investigating as a future experimentator task.

## Specific experiments to run

1. **Benchmark compute_c_f64 speed vs compute_c on various array sizes.** For coordinate descent with 30000 elements, knowing the per-call cost matters for time budgeting.
2. **Test whether float64 sensitivity rankings are stable across delta values (1e-7, 1e-8, 1e-9).** If rankings change with delta, the finite-difference approach needs more care.
3. **Investigate batch gradient computation.** Can we compute dC/df[i] for all i faster than N separate perturbations? The FFT structure might allow it.

## What surprised me?

The float32 vs float64 gradient magnitude ranges are nearly identical ([-0.5577, 0.0730] vs [-0.5577, 0.0730]). The *values* are close but the *rankings* are completely different. This means float32 isn't adding large errors to any single gradient — it's adding tiny errors (~1e-6) that are enough to reshuffle which elements are at the top of a nearly-flat ranking. This is more insidious than a large systematic bias.

## Helper tools feedback

- Used `helpers/core.py` (compute_c) as reference and for float32 comparison. Correct and useful.
- The new `compute_c_f64` and updated `sensitivity.py` are the primary outputs.
- **Suggestion:** A targeted sensitivity function that computes gradients for only selected indices (not all N) would be much more practical for large arrays. Could be a future helper.

## Deliverables

| File | Status |
|------|--------|
| `output/helpers/compute_c_f64.py` | Done, validated |
| `output/helpers/sensitivity.py` | Done, validated |
| `output/helpers/README.md` | Done |
| `output/experiment_results.md` | Done |
