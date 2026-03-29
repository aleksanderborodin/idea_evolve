# gen006_full_1 Debrief Report

## Solution Scores

| File | Fitness | Valid | Notes |
|------|---------|-------|-------|
| sol01.py | **1.502862898255827** | 1 | TTT-Discover 30k array, unchanged — LP refinement did not complete |

**Baseline going in:** C = 1.502862898255827 (TTT-Discover 30k array)
**Best achieved:** C = 1.502862898255827 — **no improvement.**

---

## 1. What Did I Try?

### Approach: Linearized LP-based constraint relaxation

Implemented a full LP refinement pipeline:
- Float64 autoconvolution computation matching validate.py
- Near-tight constraint identification at multiple epsilon thresholds
- Linearized LP formulation: minimize max(f★f + 2·f★δ) over tight indices j, subject to non-negativity and integral preservation
- Sparse matrix construction using scipy.optimize.linprog with HiGHS solver
- Iterative refinement loop with multiple step sizes

**Result:** The LP constraint matrix construction phase consumed ~7GB RAM and >19 minutes before being killed. The LP itself never ran.

**Root cause:** Building `A_ub[j, k] = 2 * f[j - active_k] * dx` required iterating over (n_tight × n_active) pairs in a Python loop. At N=30000 with ~2000 active variables and ~100+ tight constraints, this was prohibitively slow.

---

## 2. What Information Did I Lack?

- **Practical LP scaling at N=30k.** The theoretical formulation is sound, but I underestimated the constraint matrix construction cost. Needed to know upfront that vectorized/batched FFT construction is essential.
- **Exact number of tight constraints at relevant epsilons.** The tightness analysis code ran but the output was buffered and lost when the process was killed. Knowing this upfront would have informed the LP size.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- idea_020 says "this is a very tractable LP" for K < 100 constraints. This is true for the LP solve itself, but ignores the matrix construction cost at N=30k. The idea should note that constraint matrix construction dominates, not the LP solve.

---

## 4. Was the State of Affairs Accurate?

The State of Affairs is outdated (gen 3). It doesn't reflect gen 4-5 findings that all gradient methods fail on the 30k array. The LP recommendation from gen 5 reports is accurate and well-motivated — the implementation just hit engineering bottlenecks.

---

## 5. What Would I Do Differently?

1. **Work at reduced resolution (N=1000-3000).** Downsample the 30k array, run LP there, upsample the descent direction, apply to full array. The LP descent direction is smooth and doesn't need 30k resolution.

2. **Use batched FFT for constraint matrix.** Compute f★e_k for all active k simultaneously using a single batched FFT operation, then extract tight-index rows. This would make construction O(K · N log N) instead of O(K · N_active · N).

3. **Start with the smallest possible LP.** Use epsilon=1e-5 to get perhaps 1-3 truly tight constraints. With 3 constraints and 500 variables, the LP would build and solve in seconds.

4. **Use column generation.** Start with a few promising variables, solve the restricted LP, use reduced costs to identify which variables to add. Avoids computing all 2000+ columns upfront.

---

## 6. Specific Experiments to Run

1. **Reduced-resolution LP (HIGHEST PRIORITY):** Downsample TTT-Discover 30k → N=2000. Run LP refinement there. Upsample delta to N=30k via interpolation. Apply. This should complete in minutes, not hours.

2. **Batched FFT constraint matrix:** Implement `A_ub[:, k] = (f ★ e_k)[tight_indices]` via batched FFT. Each column is one FFT of length 2N. 2000 columns × 60k FFT = ~10 seconds with numpy.

3. **Minimal LP with 1-3 constraints:** Use epsilon=1e-6 to get the very tightest constraints only. Build tiny LP. Even if improvement is tiny, it proves the approach works.

4. **Coordinate descent on LP direction:** Instead of full LP, compute the gradient of the linearized objective (which is just the cross-convolution evaluated at the peak) and do steepest descent in that direction. This avoids the LP entirely and may work for small improvements.

---

## 7. What Surprised Me?

1. **Memory consumption.** The sparse matrix construction used 7GB despite using scipy.sparse.csr_matrix. The issue is that the Python loop creates many temporary arrays before they're assembled into the sparse matrix.

2. **The approach is fundamentally sound.** The linearization is correct, the LP formulation is valid, and HiGHS can handle the LP size. Only the implementation's matrix construction was the bottleneck — a pure engineering problem, not a mathematical one.

---

## 8. Helper Tools Feedback

- **Did NOT use** any helpers — went directly to a custom float64 implementation matching validate.py.
- **Wished I had:** A `compute_c_f64` helper that returns both C and the full autoconvolution array (not just the scalar C). The existing `helpers/compute_c_f64.py` may do this but I wrote my own to be safe.
- **Wished I had:** A helper that computes the cross-convolution f★g via FFT in float64. This is the core building block for LP constraint matrices and would save significant implementation time.
- **Wished I had:** A helper that identifies near-tight constraints (indices where autoconv is within epsilon of the max). This analysis is needed by any LP or constraint-based approach.
