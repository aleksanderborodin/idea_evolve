# Debrief Report — experimentator_1, Generation 7

## Summary

Delivered 3 shared helper tools + updated README. All helpers pass validation tests.

---

## 1. What did I try?

### Task 1: `incremental_autoconv_update.py` — COMPLETE

Implemented the O(N) incremental autoconvolution update described in the gen006 exploit_1 debrief. The formula was well-specified:
```
autoconv_new[n] = autoconv_old[n] + dx * (2 * delta * f_padded[(n-idx) % M] + delta^2 * (n == 2*idx))
```

Also added `batch_incremental_updates()` for convenience in coordinate descent loops. Both functions use vectorized numpy (no Python loops).

**Test results:** 11 test cases, all errors < 2.2e-18 (well below 1e-14 spec). Specifically:
- 5 random perturbations: max_err < 2.2e-18
- Small delta (1e-12): max_err = 2.2e-18
- Large delta (1.0): max_err = 1.7e-18
- Boundary indices, zero elements, batch updates: all PASS

### Task 2: `cross_convolution_f64.py` — COMPLETE

Implemented three functions:
- `cross_convolve(f, g, dx)`: (f★g)(t) returning length 2N-1 linear convolution
- `autoconvolve(f, dx)`: (f★f) returning length 2N padded array + f_padded, dx, M (compatible with incremental_update)
- `tight_constraint_indices(f, epsilon_rel)`: indices where autoconv ≥ (1-ε)*max

The key design decision was making `autoconvolve` return the same 2N array convention as `compute_c_f64` and `incremental_autoconv_update` (not 2N-1), to ensure compatibility when chaining these helpers.

**Test results:** All 9 tests pass. `autoconvolve` output agrees with `compute_c_f64` to machine precision (diff=0.0). Compatible with `incremental_update`.

### Task 3: `lp_matrix.py` — COMPLETE

Implemented vectorized LP matrix construction and a full `scipy_lp_solve` function:
- `build_lp_matrix(f, tight_indices)`: A_ub[j,k] = 2*f_padded[(j-k)%M]*dx using 2D index broadcasting (zero Python loops)
- `build_lp_rhs(autoconv, tight_indices)`: b_ub[j] = A_max - autoconv[j] - epsilon
- `scipy_lp_solve(f, tight_indices, autoconv, ...)`: Full LP step with integral preservation, non-negativity, step bounds

**Test results:** All 8 unit tests pass. Vectorized vs manual loop diff = 0.0.

**Integration test finding:** A single LP step correctly reduces autoconvolution at tight indices (confirmed: constraint satisfied at tight location), but increases it at non-tight indices, worsening global C. This is *expected* behavior — the LP only constrains the tight_indices supplied. Future agents must use iterative refinement (update f, recompute tight indices, run LP again).

### Task 4: README update — COMPLETE

Rewrote README to document all 7 helpers (4 existing + 3 new) with:
- Import syntax
- Function signatures
- When to use / when not to use
- Warnings about common pitfalls
- Usage examples for chaining helpers

---

## 2. What information did I lack?

- **The TTT-Discover 30k array structure**: I read from reports that it has ~25141 nonzero elements. Knowing this upfront would have been useful for sizing LP memory estimates, but it wasn't needed for the helper implementations.
- **Whether `scipy.optimize.linprog` HiGHS solver is available in the venv**: It was (confirmed). This assumption was safe.

---

## 3. What given facts might be wrong or outdated?

- **README said "none yet" for experimentator-created helpers**: 4 helpers already existed (`compute_c_f64`, `sensitivity`, `inv_softplus`, `interpolation`). README was severely out of date. Fixed in output.
- **Brief said "STALE — says 'none yet' but 4 helpers exist"**: Confirmed accurate self-note.

---

## 4. Was the State of Affairs accurate?

Did not read State of Affairs thoroughly (not needed for this tool-building task). Based on exploit_1 and full_1 debriefs, SoA appears outdated (still references gen 3 best score 1.5032 vs actual 1.5028628).

---

## 5. What would I do differently with more context?

- **Test LP at reduced resolution (N=2000) with TTT-Discover array**: The gen006 full_1 debrief recommended downsampling the 30k array to ~2000 and running LP there. I could have validated this as part of the experimentator work. Instead I focused purely on the helper implementations.
- **Benchmark incremental_update speedup**: The exploit_1 debrief claimed ~28x speedup. I could have measured this explicitly and included timing data.

---

## 6. Specific experiments to run

### Experiment A: LP iterative refinement at reduced resolution (HIGHEST PRIORITY)
- Downsample best.py (N=30000) → N=2000 via `interpolate_sparse`
- Compute autoconvolution, find tight constraints (epsilon_rel=1e-6)
- Run 20-50 LP iterations with max_step=0.01, updating tight indices each time
- Upsample delta back to N=30000 via interpolate_sparse
- Apply to full array, evaluate
- **Hypothesis:** LP descent direction at N=2000 is smooth enough to transfer to N=30000

### Experiment B: How many tight constraints at best solution?
- Load population/best.py (C=1.502862898...)
- Run tight_constraint_indices at epsilon_rel = 1e-6, 1e-5, 1e-4, 1e-3
- Report count and distribution
- **Motivation:** Knowing this determines LP problem size at N=30000

### Experiment C: Coordinate descent with incremental_update on best solution
- Continue from best.py with full-array coordinate descent using incremental_update
- The gen006 exploit_1 report showed 1800 improvements/round in round 3 — not yet converged
- Estimated cost: ~1 second/round for N=30000 with incremental_update (vs 21ms*30000 = 630s with FFT)
- **Target:** 10+ more rounds may find additional -1e-8 improvements

---

## 7. What surprised me?

- **`autoconvolve` output agreed with `compute_c_f64` to exactly 0.0 difference**: Expected some floating-point rounding difference, but the implementations are identical. Reassuring.
- **LP correctly reduced autoconv at tight indices but the single-step failed globally**: I expected either global improvement or "LP infeasible" for a near-optimal solution. Instead the LP found a direction that reduces tight-index autoconv while increasing non-tight indices. This confirms the iterative refinement requirement.
- **No tight constraints for the random test function**: At N=200 with epsilon_rel=1e-4, only 1 tight constraint (index 198). The LP had only 1 row, making it trivially solvable but unable to control the full distribution.

---

## 8. Helper tools feedback

### helpers/core.py — NOT used
Not needed for tool-building work.

### helpers/compute_c_f64.py — Used as reference/ground truth
Excellent. The docstring accurately states it matches validate.py exactly. The `compute_c_f64` function was used as ground truth for verifying `autoconvolve` output.

**Minor issue:** The function signature `compute_c_f64(f_array)` doesn't type-hint the return as `float`. The docstring example is correct and helpful.

### helpers/sensitivity.py — NOT used
Not needed for tool-building work.

### helpers/inv_softplus.py — Read for documentation
Found a critical underdocumented issue: default `clip_min=-10` causes near-zero elements to become softplus(-10) ≈ 4.5e-5, which inflates the integral for sparse solutions. Documented this warning in the new README (under the `clip_min=-20` recommendation).

### helpers/interpolation.py — Read for documentation
Function is straightforward. No issues found.

### New helpers — correctness confirmed:
- `incremental_autoconv_update`: All tests pass, errors < 1e-18
- `cross_convolution_f64`: All tests pass, bit-identical to np.convolve
- `lp_matrix`: All unit tests pass, iterative use required for global improvement

### Missing helper (for future):
- **`coordinate_descent.py`**: A full coordinate descent loop using `incremental_update` would be a natural complement to these helpers. It would encapsulate: init autoconv via autoconvolve(), try deltas for each element, apply improvements greedily, repeat. This would save every future exploit/full agent from reimplementing the coordinate descent loop.
