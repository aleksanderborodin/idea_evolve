# Observations — gen008 explore_2

## Summary

Two diagnostic experiments as directed. No solution file produced (LP improvements at N=5000
were -1e-8 at C=1.679, far from frontier). Key findings below.

---

## Experiment A: LP Plateau Analysis at Intermediate Resolution

### Critical discovery: downsampling destroys structure

The brief assumed `interpolate_sparse(f_30k, N_target)` would produce near-optimal solutions
at intermediate N. It doesn't. Downsampling from N=30k to N=5000-10000 gives:

| N     | C after interpolation | tight@1e-4 | tight@1e-5 | tight@1e-6 | tight@1e-7 |
|-------|----------------------|------------|------------|------------|------------|
| 5000  | 7.289                | 1          | 1          | 1          | 1          |
| 8000  | 3.058                | 1          | 1          | 1          | 1          |
| 10000 | 4.094                | 1          | 1          | 1          | 1          |
| 30000 | 1.5029               | 18325      | 16185      | 14055      | 6711       |

**With C=3-7, tight constraints (1 each) are for the wrong reasons** — the function is not
near-optimal, just has a single autoconvolution peak. LP at these bad points finds t=0
(trivially satisfying epsilon=1e-9) but the actual delta makes C worse when applied.

### Coord descent to reach near-optimal at N=5000

To answer the actual question, we need to optimize at N=5000. Using O(N) incremental updates:

**Fast coord descent trajectory at N=5000 (step=0.01):**

| C         | tight@1e-4 | tight@1e-5 | tight@1e-6 | time | note |
|-----------|-----------|-----------|-----------|------|------|
| 7.289     | 1         | 1         | 1         | 0s   | downsampled start |
| 1.733     | 3         | 1         | 1         | 15s  | |
| 1.712     | 10        | 2         | 1         | 30s  | |
| 1.702     | 10        | 2         | 1         | 45s  | |
| 1.697     | 6         | 3         | 1         | 60s  | |
| 1.691     | 11        | 1         | 1         | 75s  | |
| 1.685     | 9         | 2         | 2         | 90s  | |
| 1.681     | 7         | 1         | 1         | 105s | |
| **1.679** | **6**     | **1**     | **1**     | 120s | converged |

The optimization converged at C=1.679 (local minimum for step sizes 0.01 → 1e-6). This
is far from the C=1.503 frontier. Starting from a downsampled N=30k solution is poor for
N=5000 optimization — the structure is incompatible.

### LP feasibility at C=1.679 (N=5000)

With tight@1e-5 = 1 (single tight constraint), LP solved successfully:
- LP status: optimal (t=0)
- Line search improvement: C = 1.67913360987 → **1.67913359944** (Δ = -1.04e-8)
- This confirms LP is *mechanically* feasible at N=5000

But this is irrelevant for the frontier — C=1.679 is 0.177 above the frontier (C=1.503).

### Interpretation

**The plateau question cannot be answered by downsampling + short optimization.** To know
tight constraint counts at C~1.503 for N=5000, we need:
1. Start from scratch with gradient methods (Adam + smooth-max) at N=5000
2. Or run coord descent for hours (the downsampled starting point is too far from optimal)

**Prediction from trajectory:** At C=1.679, tight@1e-4 stays ≤ 11. Even if it grows
proportionally as C→1.503, scaling from N=30k (18325/60000 = 30.5% of autoconv points)
to N=5000 would predict ~3000 tight@1e-4 at N=5000 near-optimal. That's still too many
for LP (target <500 from the brief).

However, this scaling is pessimistic — the N=5000 solution structure may be fundamentally
different from N=30k. At C=1.679, tight@1e-4 = 3-11 (0.03-0.11% of 10000 autoconv points),
vs N=30k's 30.5%. The plateau density appears strongly resolution-dependent.

**Bottom line:** LP at intermediate N is **not blocked by the plateau count** (at least
not at C=1.679). But getting to C~1.503 at N=5000 requires more optimization work than
available here.

---

## Experiment B: FFT Padding Validation

**CONCLUSIVE RESULT: All padding sizes give identical C to within 1e-15.**

| Padding config             | C value                | diff from 2N reference |
|---------------------------|------------------------|------------------------|
| 2N (standard, validate.py)| 1.50286286889246       | reference              |
| 2N-1 (tight)              | 1.50286286889245       | ~1e-15 (identical)     |
| next_pow2 (≥ 2N)          | 1.50286286889246       | identical              |
| 4N                        | 1.50286286889246       | identical              |

**The -1e-8 to -1e-9 improvements from coord descent and triplet perturbation are REAL,
not FFT artifacts.** The system critic's flag (raised gen 5, unresolved until now) is
hereby definitively closed. Padding size has no effect on C computation.

**Reason it doesn't matter:** The N=30k solution has support mainly on a small portion
of the domain. The autoconvolution maximum (at index 25379 out of 60000) is well within
the linear convolution range regardless of padding size. FFT aliasing does not affect the
max_conv computation for this problem.

---

## What We Didn't Do

- LP at N=5000 starting from a near-optimal solution (needed gradient-based init first)
- LP upsample direction (N=5000 solution is C=1.679, not competitive)
- Analysis at N=8000, N=10000 (same issues as N=5000; skipped given time constraint)
