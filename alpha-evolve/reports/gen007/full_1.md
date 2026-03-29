# gen007_full_1 Debrief Report

## Solution Scores

| File | Fitness | Valid | Notes |
|------|---------|-------|-------|
| sol01.py | 1.5028628724712894 | 1 | LP at N=2000, no improvement (upsampling fails) |
| sol02.py | 1.5028628724712894 | 1 | LP at N=30k (1 tight constraint), no improvement |
| sol03.py | 1.5028628724712894 | 1 | LP at N=30k (138 constraints + bounded delta), no improvement |
| sol04.py | **1.5028628712540075** | 1 | Extended coordinate descent, 257 improvements |

**Baseline: C = 1.5028628724712894**
**Best achieved: C = 1.5028628712540075 — improvement of 1.217e-9**

---

## 1. What Did I Try?

### LP at N=2000 with upsampling (sol01.py)
Implemented the exact LP formulation from the brief. At N=2000, the downsampled function has C=1.721 (much worse than N=30k = 1.502 due to resolution). LP found t=-5.5e-5 and improved the N=2000 C from 1.721 to 1.710 (alpha=0.003). When the direction was upsampled to N=30k and applied, all step sizes worsened C. This confirms resolution sensitivity.

### LP directly at N=30k (sol02.py, sol03.py)
Implemented vectorized A_ub construction (O(n_tight) loop, no Python loop over N). Built (1, 30000) matrix in 0.001s — no OOM like gen6. LP solved in 0.16-8.2s depending on constraint count. LP consistently found t < 0 (descent direction exists), but ALL line search steps worsened C.

**Root cause: flat autoconvolution plateau.** The 30k array has ~6500 points within 1e-7 * max of the autoconvolution maximum. LP with ≤ 138 tight constraints controls only those constraints — the other ~6360 near-maximum points then become the new maximum after the perturbation. To properly constrain the problem, you'd need to include all ~6500 constraints, requiring a (6500, 30000) constraint matrix = 1.5GB — the same scaling failure as gen6.

### Extended coordinate descent (sol04.py)
Continued gen6's coordinate descent. Used np.roll(f_pad, idx) for the O(N) incremental update. Found 257 improvements in round 1, 0 in round 2 (converged). **Improvement: 1.217e-9.**

---

## 2. What Information Did I Lack?

- **Flat plateau scale at N=30k.** Needed to know that the autoconvolution has ~6500 near-maximum points at eps=1e-7. This makes LP at N=30k intractable without including all of them.
- **Gen6 coordinate descent delta set.** Gen6 used "1e-9 to 1e-2 absolute + 0.01% to 10% relative". I only used absolute [1e-9 to 5e-4]. Using relative deltas might have found more improvements.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- **idea_020**: "LP-guided refinement should be tractable with K < 100 tight constraints." This is wrong for the 30k array because the plateau has ~6500 near-maximum points. LP with fewer constraints controls some of them but other plateau points become the new maximum.
- **State of Affairs gen 6**: Says "LP at reduced resolution (N=2000) with upsampled descent direction" is high-priority. We now know the upsampled direction doesn't work — the LP is resolution-sensitive.

---

## 4. Was the State of Affairs Accurate?

Mostly accurate. Missing: the flat plateau scale (6500 near-max points at eps=1e-7). This is critical context for understanding why LP approaches keep failing. Should add to idea_020 or a new fact.

---

## 5. What Would I Do Differently?

1. **Start with LP plateau analysis.** Before implementing LP, check how many near-max points exist at various epsilons. This immediately reveals whether LP is tractable.
2. **Focus on coordinate descent first.** It's proven to work and still finding improvements. LP is theoretically appealing but has fundamental issues at this resolution.
3. **Use relative deltas in coordinate descent.** Proportional steps (e.g. ±1% of f[idx]) can find improvements that absolute deltas miss.

---

## 6. Specific Experiments to Run

1. **Coordinate descent with proportional deltas**: Add relative deltas [0.001*f[idx] to 0.5*f[idx]]. Expected: 100-500 more improvements.

2. **LP at intermediate resolution**: Try N=5000 or N=10000. Count tight constraints at eps=1e-7 there — if fewer than 500, LP might be tractable AND the direction might transfer better to N=30k.

3. **Triplet perturbation**: Try d1+d2+d3=0 moves. Pairs (gen6) found 1 improvement; triplets untested.

4. **AlphaEvolve 1319-element array**: Coordinate descent starting from this different basin.

5. **Flat plateau exploitation**: Sample multiple perturbations that keep C within 1e-9 of current best; use these to escape the coordinate-wise optimum basin.

---

## 7. What Surprised Me?

1. **LP at N=30k is now fast.** With vectorized construction, (138, 30000) matrix takes <0.01s and LP solves in 8 seconds. The gen6 bottleneck (Python loop over N) is completely eliminated. But LP still fails because of the plateau, not construction cost.

2. **The flat plateau is huge.** 6500 points within 1e-7 * max = 2.5e-12 of the autoconvolution maximum. This suggests the function is in a very broad valley, not a sharp optimum.

3. **Coordinate descent still works.** After 14373 improvements in gen6, we found 257 more. The function hasn't yet reached the coordinate-wise optimum.

4. **The LP approach is correct in theory.** At N=2000 it improved C by 0.011 (0.6%). The problem is purely about the flat plateau at N=30k.

---

## 8. Helper Tools Feedback

- **compute_c_f64**: Excellent — matched validate.py exactly, no issues.
- **interpolation.py**: Didn't use directly (used np.interp instead for simplicity).
- **Wished I had**: A function `autoconv_tight_count(f, eps_factors)` that computes the number of near-maximum autoconvolution points at various epsilon values. This is the key diagnostic for LP feasibility.
- **Wished I had**: A helper that computes `np.roll(f_padded, idx)` efficiently for many idx values (batched cross-correlation via FFT). This is the bottleneck for coordinate descent speed.
