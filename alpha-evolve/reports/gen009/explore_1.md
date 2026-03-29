# Debrief Report — gen009_explore_1

## Solutions

| File | Fitness (C) | Valid | Method |
|------|-------------|-------|--------|
| sol01.py | **1.5028628683413456** | Yes | Quintuplet + triplet follow-up |

**Baseline (gen008_explore_1):** C = 1.5028628684790137
**Improvement:** delta_C = -1.38e-10
**Method:** Quintuplet perturbation (2 improvements at float64 noise floor) + triplet follow-up (150 improvements)

---

## 1. What did I try?

### Quintuplet perturbation (d1+d2+d3+d4+d5=0) — 50k trials

Implemented gradient-guided 5-element integral-preserving perturbations:
- Gradient at argmax n*: g[m] = 2*dx*f_padded[(n*-idx_m)%M]
- Project onto sum-zero hyperplane: g_proj = g - mean(g) (4 free variables)
- 9 step sizes log-spaced from 1e-1 to 1e-6 (largest valid step chosen)
- 3 strategies rotated: S0 (5 random nonzero), S1 (2 large+2 small+1 rand), S3 (3 nonzero+2 rand)
- Exact O(N) incremental updates with revert on rejection

**Result: 2 improvements, delta_C = -4.4e-16 (1 ULP of float64)**

This is the float64 precision floor, not genuine optimization. Quintuplets do not provide
meaningful improvement over quadruplets on this solution.

### Quadruplet follow-up — 20k trials

After quintuplets, quadruplet pass to test unlocking hypothesis.
**Result: 0 improvements**

### Triplet follow-up — 20k trials

**Result: 150 improvements, delta_C = -1.38e-10**

Triplets found significant residual improvements even after quintuplets and quadruplets
found nothing. Total time: 7 min.

---

## 2. What information did I lack?

- Whether the quintuplet gradient computation is numerically stable at this precision:
  g values are ~3e-5 in magnitude, so g_proj values are ~2.4e-5, and at alpha=1e-6
  deltas are ~2.4e-11. This may be below the noise floor of the incremental update.
- Whether the 2 quintuplet "improvements" are genuine or floating-point artifacts.
  Computing |delta_C| = 4.4e-16 = 1 ULP suggests they are rounding artifacts.
- How many triplet trials are needed to fully exhaust the triplet landscape.

---

## 3. What given facts might be wrong or outdated?

- The brief's prediction "quintuples should find O(10k+) improvements with total
  delta ~1e-11 to 1e-10" was incorrect. Quintuples found only 2 improvements at
  the noise floor. The dimensional analysis is wrong at this precision.
- The unlocking hypothesis (higher k unlocks lower k) was partially confirmed in
  gen8 (quads unlock triplets), but NOT confirmed here (quintuples do not unlock quads).

---

## 4. Was the State of Affairs accurate?

Partially. The State of Affairs correctly identified quintuplets as untested and
worth trying. The result provides a definitive answer: the perturbation hierarchy
does not continue to be useful beyond k=4 at this precision level.

---

## 5. What would I do differently?

1. **Run more triplet trials instead**: 500k triplet trials (~20 min) would likely
   find hundreds more improvements. Triplets are the most effective perturbation
   at this precision.

2. **Gradient-guided index selection**: Instead of random selection, choose indices
   that maximize the projected gradient norm:
   - For each candidate set of k indices, compute ||g_proj||^2 = k*var(g)
   - Select the set with highest variance in g values
   - This focuses search on directions with maximum available descent

3. **Momentum strategy**: After each accepted move, immediately retry the same
   indices with the next smaller step size. Often the same direction has
   remaining improvement potential.

4. **Vectorized batch**: Sample K=100+ index sets simultaneously, evaluate all
   with numpy broadcasting, pick the best. Should achieve 1000+ t/s.

---

## 6. Specific experiments to run

### Experiment A: Extended triplet search (recommended)
- Run 500k triplet trials on current best solution
- At 424 t/s = ~20 min
- Expected: 300-1000 more improvements (assuming rate doesn't plateau)
- Stopping criterion: fewer than 10 improvements in last 50k trials

### Experiment B: Vectorized k-plet
- Implement batch evaluation: 100 candidate index sets, vectorized gradient projection
- Use numpy broadcast: shape (K, k) index arrays, gradient matrices
- First-order screening: reject where first-order delta_C > 0 (can be vectorized)
- Target: 1000+ t/s for triplets

### Experiment C: Optimal k-plet index selection
- For each trial, sample M=50 candidate index sets
- Compute ||g_proj||^2 for each (cheap: k scalar lookups + variance)
- Pick top-1 (highest projected gradient norm)
- This concentrates computation on the most promising directions

---

## 7. What surprised me?

1. **Quintuplets at float64 noise floor**: The 2 improvements found are ~1 ULP each.
   The perturbation hierarchy broke down much earlier than expected — at k=5 we're
   already in numerical noise. The mathematical prediction of "4 free variables = more
   expressivity" doesn't translate to real improvements when the solution is this refined.

2. **Triplets still improving after gen8**: Finding 150 triplet improvements in gen9
   (after gen8's 2523) shows the triplet landscape is not fully exhausted. If we ran
   1M triplet trials, we might still find improvements at this precision.

3. **No quadruplet improvements in follow-up**: Gen8 found 8015 quadruplet improvements.
   Gen9 quadruplet follow-up (after quintuplets) found 0. This confirms the solution
   is at a quadruplet local minimum, and the tiny quintuplet adjustments did not
   unlock new quadruplet directions.

4. **Rate at different k**: Triplets run at 424 t/s vs 165 t/s for quintuplets. The
   O(kN) cost per accepted trial dominates, so triplets are ~3x faster. More efficient
   to run many triplet trials than few quintuplet trials.

---

## 8. Helper tools feedback

- **helpers/incremental_autoconv_update.py**: Correct and essential. batch_incremental_updates
  made the implementation clean. The O(N) update is the key enabling technology.
- **helpers/compute_c_f64.py**: Used for final verification. The autoconv-based tracking
  (max(autoconv)/integral^2) agreed with compute_c_f64 to 15 significant digits.
- **Missing**: A vectorized k-plet trial function. Something like:
  `batch_k_plet_screen(f_padded, autoconv, n_star, index_sets, dx, M)` that takes
  K candidate index sets and returns which ones have non-trivial gradient projections
  and non-negativity-safe step sizes. This would enable 10-50x speedup.

---

## 9. Time budget

Total time: 420.9s (~7 min) for 90k total trials (50k quintuplet + 20k quadruplet + 20k triplet).

Had more time (2 hours): would run 500k triplet trials (estimated 300-1000 improvements,
delta_C ~1e-9) and implement vectorized batch k-plet for 10x throughput.

The session had sufficient time for the planned experiment. The result is clear:
quintuplets do not help, but triplets have residual potential.
